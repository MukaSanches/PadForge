from __future__ import annotations

import math
import time
from typing import Dict

from .models import (
    RawState, CanonicalState, Profile, AxisCalibration, ControllerMapping,
    default_physical_calibration,
)


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _normalize_centered(raw: float, c: AxisCalibration) -> float:
    raw = clamp(raw, c.minimum, c.maximum)
    if raw >= c.center:
        span = max(1e-6, c.maximum - c.center)
        value = (raw - c.center) / span
    else:
        span = max(1e-6, c.center - c.minimum)
        value = (raw - c.center) / span
    if c.invert:
        value = -value
    return clamp(value, -1.0, 1.0)


def _shape_unit(value: float, c: AxisCalibration) -> float:
    sign = -1.0 if value < 0 else 1.0
    magnitude = abs(value)
    dz = clamp(c.deadzone, 0.0, 0.95)
    if magnitude <= dz:
        return 0.0
    magnitude = (magnitude - dz) / max(1e-6, 1.0 - dz)

    curve = (c.curve or "linear").lower()
    if curve == "precision":
        magnitude = magnitude ** 1.7
    elif curve == "aggressive":
        magnitude = magnitude ** 0.65
    elif curve == "s-curve":
        magnitude = magnitude * magnitude * (3.0 - 2.0 * magnitude)
    elif curve == "quadratic":
        magnitude = magnitude * magnitude

    magnitude = clamp(magnitude * max(0.05, c.sensitivity), 0.0, 1.0)
    adz = clamp(c.anti_deadzone, 0.0, 0.95)
    if magnitude > 0 and adz > 0:
        magnitude = adz + (1.0 - adz) * magnitude
    return clamp(sign * magnitude, -1.0, 1.0)


def apply_axis_curve(value: float, c: AxisCalibration) -> float:
    return _shape_unit(_normalize_centered(value, c), c)


def apply_canonical_tuning(value: float, c: AxisCalibration) -> float:
    # Input is already normalized to [-1, 1], so hardware center/min/max are intentionally ignored.
    tuned = -value if c.invert else value
    return _shape_unit(clamp(tuned, -1.0, 1.0), c)


def apply_radial_deadzone(x: float, y: float, deadzone: float = 0.0) -> tuple[float, float]:
    magnitude = math.sqrt(x * x + y * y)
    if magnitude <= deadzone:
        return 0.0, 0.0
    if magnitude > 1.0:
        x /= magnitude
        y /= magnitude
    return x, y


class ProcessingEngine:
    def __init__(self) -> None:
        self._started = time.monotonic()

    def map_physical(self, raw: RawState, mapping: ControllerMapping,
                     calibration: Dict[str, AxisCalibration]) -> CanonicalState:
        state = CanonicalState()

        for axis_name, raw_index in mapping.axis_map.items():
            if axis_name not in state.axes:
                continue
            raw_value = raw.axes.get(raw_index, 0.0)
            physical = calibration.get(axis_name, AxisCalibration())
            normalized = apply_axis_curve(raw_value, physical)
            if axis_name in ("LT", "RT"):
                # Common DirectInput trigger axes use [-1,+1]; canonical trigger space is [0,1].
                normalized = clamp((normalized + 1.0) * 0.5, 0.0, 1.0)
            state.axes[axis_name] = normalized

        for button_name, raw_index in mapping.button_map.items():
            if button_name in state.buttons:
                state.buttons[button_name] = bool(raw.buttons.get(raw_index, False))

        if mapping.dpad_hat is not None:
            hx, hy = raw.hats.get(mapping.dpad_hat, (0, 0))
            state.buttons["DPAD_LEFT"] = hx < 0
            state.buttons["DPAD_RIGHT"] = hx > 0
            state.buttons["DPAD_UP"] = hy > 0
            state.buttons["DPAD_DOWN"] = hy < 0

        for direction in ("DPAD_UP", "DPAD_DOWN", "DPAD_LEFT", "DPAD_RIGHT"):
            raw_index = mapping.dpad_buttons.get(direction)
            if raw_index is not None:
                state.buttons[direction] = state.buttons[direction] or bool(raw.buttons.get(raw_index, False))

        # Digital shoulders on PS2-style adapters become XInput analog triggers.
        if state.buttons.get("L2"):
            state.axes["LT"] = 1.0
        if state.buttons.get("R2"):
            state.axes["RT"] = 1.0
        return state

    def apply_profile(self, physical: CanonicalState, profile: Profile) -> CanonicalState:
        state = physical.clone()
        for axis_name, tuning in profile.calibration.items():
            if axis_name in state.axes:
                if axis_name in ("LT", "RT"):
                    # Tune trigger magnitude without translating its 0..1 domain.
                    value = clamp(state.axes[axis_name], 0.0, 1.0)
                    state.axes[axis_name] = max(0.0, apply_canonical_tuning(value, tuning))
                else:
                    state.axes[axis_name] = apply_canonical_tuning(state.axes[axis_name], tuning)
        return self._remap_and_turbo(state, profile)

    def canonicalize(self, raw: RawState, profile: Profile) -> CanonicalState:
        """Compatibility helper for tests/third-party callers using the original V1 API."""
        physical = self.map_physical(raw, profile.mapping, default_physical_calibration())
        return self.apply_profile(physical, profile)

    def _remap_and_turbo(self, state: CanonicalState, profile: Profile) -> CanonicalState:
        output = state.clone()
        output.buttons = {k: False for k in output.buttons}
        now = time.monotonic()

        for source, pressed in state.buttons.items():
            target = profile.remap.get(source, source)
            if target not in output.buttons:
                continue
            if not pressed:
                continue
            hz = float(profile.turbo_hz.get(source, 0.0) or 0.0)
            if hz > 0:
                phase = int(now * hz * 2.0) % 2
                pressed = phase == 0
            output.buttons[target] = output.buttons[target] or pressed

        return output

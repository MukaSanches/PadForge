from __future__ import annotations
import math
import time
from typing import Dict, Tuple
from .models import AxisCalibration, ControllerState, Profile


def clamp(value: float, low: float = -1.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def normalize_axis(raw: float, calibration: AxisCalibration) -> float:
    """Normalize an arbitrary centered axis to [-1, 1] with deadzone and curve."""
    raw = clamp(raw)
    if raw >= calibration.center:
        span = max(1e-6, calibration.maximum - calibration.center)
        value = (raw - calibration.center) / span
    else:
        span = max(1e-6, calibration.center - calibration.minimum)
        value = (raw - calibration.center) / span

    value = clamp(value / max(1e-6, calibration.saturation))
    if calibration.invert:
        value = -value

    dz = clamp(calibration.deadzone, 0.0, 0.95)
    magnitude = abs(value)
    if magnitude <= dz:
        return 0.0

    scaled = (magnitude - dz) / (1.0 - dz)
    curve = max(0.1, calibration.curve)
    curved = math.pow(scaled, curve)
    return math.copysign(clamp(curved), value)


def radial_deadzone(x: float, y: float, deadzone: float, anti_deadzone: float = 0.0,
                    curve: float = 1.0) -> Tuple[float, float]:
    magnitude = math.sqrt(x * x + y * y)
    if magnitude <= deadzone:
        return 0.0, 0.0
    if magnitude <= 1e-8:
        return 0.0, 0.0

    normalized = min(1.0, (magnitude - deadzone) / max(1e-6, 1.0 - deadzone))
    normalized = math.pow(normalized, max(0.1, curve))
    if anti_deadzone > 0:
        normalized = anti_deadzone + (1.0 - anti_deadzone) * normalized
    scale = normalized / magnitude
    return clamp(x * scale), clamp(y * scale)


def process_state(state: ControllerState, profile: Profile) -> ControllerState:
    out = ControllerState.neutral()
    out.buttons.update(state.buttons)
    out.axes.update(state.axes)

    lx, ly = radial_deadzone(out.axes.get("lx", 0.0), out.axes.get("ly", 0.0),
                             profile.deadzone, profile.anti_deadzone, profile.stick_curve)
    rx, ry = radial_deadzone(out.axes.get("rx", 0.0), out.axes.get("ry", 0.0),
                             profile.deadzone, profile.anti_deadzone, profile.stick_curve)
    if profile.invert_y:
        ry = -ry
    out.axes.update({"lx": lx, "ly": ly, "rx": rx, "ry": ry})

    # Remapping uses logical names. Source remains readable while destination is activated.
    for source, destination in profile.remap.items():
        if state.buttons.get(source, False):
            out.buttons[destination] = True
            if source != destination:
                out.buttons[source] = False
    return out


def turbo_active(button_name: str, profile: Profile, now: float | None = None) -> bool:
    if button_name not in profile.turbo_buttons:
        return True
    hz = max(1.0, min(30.0, profile.turbo_hz))
    t = time.monotonic() if now is None else now
    return int(t * hz * 2) % 2 == 0

from __future__ import annotations
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List
from .models import ControllerState, DeviceMapping, AxisCalibration
from .processing import normalize_axis


def _resource_root() -> Path:
    if hasattr(sys, "_MEIPASS"):
        return Path(getattr(sys, "_MEIPASS"))
    return Path(__file__).resolve().parent.parent


# SDL must see the mapping DB before controller initialization.
_db = _resource_root() / "assets" / "gamecontrollerdb.txt"
if _db.exists():
    os.environ.setdefault("SDL_GAMECONTROLLERCONFIG_FILE", str(_db))

try:
    import pygame
except Exception:  # allows unit tests without pygame installed
    pygame = None


@dataclass
class DeviceInfo:
    index: int
    name: str
    guid: str
    axes: int
    buttons: int
    hats: int
    sdl_mapped: bool = False


class PygameInputBackend:
    def __init__(self, mapping: DeviceMapping, calibrations=None):
        if pygame is None:
            raise RuntimeError("pygame não está instalado")
        pygame.init()
        pygame.joystick.init()
        self.mapping = mapping
        self.calibrations = calibrations or {name: AxisCalibration() for name in ("lx", "ly", "rx", "ry")}
        self.joystick = None
        self.sdl_mapping_used = False

    def _is_sdl_controller(self, index: int) -> bool:
        try:
            import pygame._sdl2.controller as controller
            if not controller.get_init():
                controller.init()
            return bool(controller.is_controller(index))
        except Exception:
            return False

    def devices(self) -> List[DeviceInfo]:
        result = []
        pygame.event.pump()
        for idx in range(pygame.joystick.get_count()):
            joy = pygame.joystick.Joystick(idx)
            joy.init()
            result.append(DeviceInfo(
                idx, joy.get_name(), getattr(joy, "get_guid", lambda: "")(),
                joy.get_numaxes(), joy.get_numbuttons(), joy.get_numhats(), self._is_sdl_controller(idx)
            ))
        return result

    @staticmethod
    def _parse_index(binding: str, prefix: str):
        if isinstance(binding, str) and binding.startswith(prefix):
            digits = "".join(ch for ch in binding[len(prefix):] if ch.isdigit())
            return int(digits) if digits else None
        return None

    def _apply_sdl_mapping(self, joy) -> bool:
        """Translate SDL's standardized mapping into PadForge's raw mapping."""
        try:
            import pygame._sdl2.controller as controller
            if not controller.get_init():
                controller.init()
            ctrl = controller.Controller.from_joystick(joy)
            mapping = ctrl.get_mapping()
            if not mapping:
                return False

            btn_keys = {
                "a": "a", "b": "b", "x": "x", "y": "y",
                "leftshoulder": "lb", "rightshoulder": "rb",
                "back": "back", "start": "start",
                "leftstick": "ls", "rightstick": "rs",
            }
            axis_keys = {"leftx": "lx", "lefty": "ly", "rightx": "rx", "righty": "ry"}
            for source, logical in btn_keys.items():
                idx = self._parse_index(mapping.get(source, ""), "b")
                if idx is not None:
                    self.mapping.buttons[logical] = idx
            for source, logical in axis_keys.items():
                idx = self._parse_index(mapping.get(source, ""), "a")
                if idx is not None:
                    self.mapping.axes[logical] = idx
            for source, logical in (("lefttrigger", "lt"), ("righttrigger", "rt")):
                binding = mapping.get(source, "")
                bidx = self._parse_index(binding, "b")
                aidx = self._parse_index(binding, "a")
                if bidx is not None:
                    self.mapping.triggers_as_buttons[logical] = bidx
                    self.mapping.axes.pop(logical, None)
                elif aidx is not None:
                    self.mapping.axes[logical] = aidx
                    self.mapping.triggers_as_buttons.pop(logical, None)
            return True
        except Exception:
            return False

    def connect(self, index: int = 0) -> DeviceInfo:
        if self.joystick is not None:
            self.joystick.quit()
        joy = pygame.joystick.Joystick(index)
        joy.init()
        self.joystick = joy
        self.mapping.name = joy.get_name()
        self.mapping.guid = getattr(joy, "get_guid", lambda: "")()
        self.sdl_mapping_used = self._apply_sdl_mapping(joy)
        return DeviceInfo(index, joy.get_name(), self.mapping.guid,
                          joy.get_numaxes(), joy.get_numbuttons(), joy.get_numhats(), self.sdl_mapping_used)

    def raw_snapshot(self):
        if self.joystick is None:
            return {"axes": [], "buttons": [], "hats": []}
        pygame.event.pump()
        return {
            "axes": [self.joystick.get_axis(i) for i in range(self.joystick.get_numaxes())],
            "buttons": [bool(self.joystick.get_button(i)) for i in range(self.joystick.get_numbuttons())],
            "hats": [self.joystick.get_hat(i) for i in range(self.joystick.get_numhats())],
        }

    def read(self) -> ControllerState:
        state = ControllerState.neutral()
        snap = self.raw_snapshot()
        axes = snap["axes"]
        buttons = snap["buttons"]
        hats = snap["hats"]

        for logical, raw_index in self.mapping.buttons.items():
            if 0 <= raw_index < len(buttons):
                state.buttons[logical] = buttons[raw_index]

        for logical, raw_index in self.mapping.axes.items():
            if 0 <= raw_index < len(axes):
                raw_value = float(axes[raw_index])
                if logical in self.calibrations:
                    raw_value = normalize_axis(raw_value, self.calibrations[logical])
                elif logical in ("lt", "rt"):
                    raw_value = max(0.0, min(1.0, (raw_value + 1.0) / 2.0))
                state.axes[logical] = raw_value

        for logical, raw_index in self.mapping.triggers_as_buttons.items():
            if 0 <= raw_index < len(buttons):
                state.axes[logical] = 1.0 if buttons[raw_index] else 0.0

        if hats and 0 <= self.mapping.hat < len(hats):
            hx, hy = hats[self.mapping.hat]
            state.buttons["dpad_left"] = hx < 0
            state.buttons["dpad_right"] = hx > 0
            state.buttons["dpad_up"] = hy > 0
            state.buttons["dpad_down"] = hy < 0
        return state

    def rumble(self, low_frequency: float, high_frequency: float, duration_ms: int = 60000) -> bool:
        """Best-effort force-feedback passthrough to the physical controller."""
        if self.joystick is None or not hasattr(self.joystick, "rumble"):
            return False
        try:
            low = max(0.0, min(1.0, float(low_frequency)))
            high = max(0.0, min(1.0, float(high_frequency)))
            if low == 0.0 and high == 0.0:
                if hasattr(self.joystick, "stop_rumble"):
                    self.joystick.stop_rumble()
                return True
            return bool(self.joystick.rumble(low, high, max(1, int(duration_ms))))
        except Exception:
            return False

    def close(self):
        if self.joystick is not None:
            try:
                if hasattr(self.joystick, "stop_rumble"):
                    self.joystick.stop_rumble()
            except Exception:
                pass
            self.joystick.quit()
        pygame.joystick.quit()

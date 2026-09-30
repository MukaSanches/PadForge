from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Tuple

LOGICAL_BUTTONS = [
    "a", "b", "x", "y", "lb", "rb", "back", "start", "ls", "rs",
    "dpad_up", "dpad_down", "dpad_left", "dpad_right"
]
LOGICAL_AXES = ["lx", "ly", "rx", "ry", "lt", "rt"]


@dataclass
class AxisCalibration:
    center: float = 0.0
    minimum: float = -1.0
    maximum: float = 1.0
    deadzone: float = 0.10
    saturation: float = 1.0
    invert: bool = False
    curve: float = 1.0


@dataclass
class DeviceMapping:
    name: str = "Generic USB Gamepad"
    guid: str = ""
    buttons: Dict[str, int] = field(default_factory=lambda: {
        "a": 2, "b": 1, "x": 3, "y": 0,
        "lb": 4, "rb": 5, "back": 8, "start": 9, "ls": 10, "rs": 11,
    })
    axes: Dict[str, int] = field(default_factory=lambda: {
        "lx": 0, "ly": 1, "rx": 2, "ry": 3
    })
    triggers_as_buttons: Dict[str, int] = field(default_factory=lambda: {"lt": 6, "rt": 7})
    hat: int = 0


@dataclass
class ControllerState:
    buttons: Dict[str, bool] = field(default_factory=dict)
    axes: Dict[str, float] = field(default_factory=dict)

    @classmethod
    def neutral(cls) -> "ControllerState":
        return cls(
            buttons={name: False for name in LOGICAL_BUTTONS},
            axes={name: 0.0 for name in LOGICAL_AXES},
        )


@dataclass
class Profile:
    name: str
    category: str = "Modern"
    executables: List[str] = field(default_factory=list)
    deadzone: float = 0.10
    anti_deadzone: float = 0.0
    stick_curve: float = 1.0
    invert_y: bool = False
    turbo_buttons: List[str] = field(default_factory=list)
    turbo_hz: float = 12.0
    remap: Dict[str, str] = field(default_factory=dict)
    notes: str = ""

    def to_dict(self):
        return asdict(self)

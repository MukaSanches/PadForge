from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Tuple, Any, Optional

CANONICAL_BUTTONS = (
    "SOUTH", "EAST", "WEST", "NORTH",
    "L1", "R1", "L2", "R2",
    "SELECT", "START", "L3", "R3",
    "DPAD_UP", "DPAD_DOWN", "DPAD_LEFT", "DPAD_RIGHT",
)
CANONICAL_AXES = ("LX", "LY", "RX", "RY", "LT", "RT")


@dataclass
class RawState:
    axes: Dict[int, float] = field(default_factory=dict)
    buttons: Dict[int, bool] = field(default_factory=dict)
    hats: Dict[int, Tuple[int, int]] = field(default_factory=dict)


@dataclass
class CanonicalState:
    axes: Dict[str, float] = field(default_factory=lambda: {k: 0.0 for k in CANONICAL_AXES})
    buttons: Dict[str, bool] = field(default_factory=lambda: {k: False for k in CANONICAL_BUTTONS})

    def clone(self) -> "CanonicalState":
        return CanonicalState(dict(self.axes), dict(self.buttons))


@dataclass
class AxisCalibration:
    center: float = 0.0
    minimum: float = -1.0
    maximum: float = 1.0
    deadzone: float = 0.0
    anti_deadzone: float = 0.0
    sensitivity: float = 1.0
    curve: str = "linear"
    invert: bool = False


def default_physical_calibration() -> Dict[str, AxisCalibration]:
    # SDL-style sticks generally report +Y down. PadForge canonical space is +Y up.
    return {
        "LX": AxisCalibration(deadzone=0.08),
        "LY": AxisCalibration(deadzone=0.08, invert=True),
        "RX": AxisCalibration(deadzone=0.10),
        "RY": AxisCalibration(deadzone=0.10, invert=True),
        "LT": AxisCalibration(deadzone=0.02),
        "RT": AxisCalibration(deadzone=0.02),
    }


def default_profile_tuning() -> Dict[str, AxisCalibration]:
    # Game profiles tune an already normalized controller. They must not encode hardware inversion.
    return {name: AxisCalibration() for name in CANONICAL_AXES}


@dataclass
class ControllerMapping:
    axis_map: Dict[str, int] = field(default_factory=lambda: {"LX": 0, "LY": 1, "RX": 2, "RY": 3})
    button_map: Dict[str, int] = field(default_factory=lambda: {
        "SOUTH": 0, "EAST": 1, "WEST": 2, "NORTH": 3,
        "L1": 4, "R1": 5, "L2": 6, "R2": 7,
        "SELECT": 8, "START": 9, "L3": 10, "R3": 11,
    })
    dpad_hat: Optional[int] = 0
    dpad_buttons: Dict[str, int] = field(default_factory=dict)


@dataclass
class ControllerConfig:
    key: str
    device_name: str
    guid: str
    mapping: ControllerMapping = field(default_factory=ControllerMapping)
    calibration: Dict[str, AxisCalibration] = field(default_factory=default_physical_calibration)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Profile:
    id: str
    name: str
    description: str = ""
    match_processes: List[str] = field(default_factory=list)
    output: str = "x360"
    # Kept for file-format compatibility. Runtime physical mapping comes from ControllerConfig.
    mapping: ControllerMapping = field(default_factory=ControllerMapping)
    calibration: Dict[str, AxisCalibration] = field(default_factory=default_profile_tuning)
    remap: Dict[str, str] = field(default_factory=lambda: {k: k for k in CANONICAL_BUTTONS})
    turbo_hz: Dict[str, float] = field(default_factory=dict)
    extra_bindings: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

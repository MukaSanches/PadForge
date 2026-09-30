from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict

from .models import AxisCalibration


@dataclass
class AxisStats:
    minimum: float = 1.0
    maximum: float = -1.0
    neutral_min: float = 1.0
    neutral_max: float = -1.0
    samples: int = 0
    neutral_samples: int = 0
    total: float = 0.0

    def observe(self, value: float, neutral: bool = False) -> None:
        self.minimum = min(self.minimum, value)
        self.maximum = max(self.maximum, value)
        self.samples += 1
        self.total += value
        if neutral:
            self.neutral_min = min(self.neutral_min, value)
            self.neutral_max = max(self.neutral_max, value)
            self.neutral_samples += 1

    def build(self, invert: bool = False) -> AxisCalibration:
        if self.samples == 0:
            return AxisCalibration(invert=invert)
        if self.neutral_samples:
            center = (self.neutral_min + self.neutral_max) / 2.0
            drift = max(abs(self.neutral_min - center), abs(self.neutral_max - center))
            deadzone = min(0.30, max(0.04, drift + 0.025))
        else:
            center = self.total / self.samples
            deadzone = 0.08
        minimum = self.minimum if self.minimum < center - 0.05 else -1.0
        maximum = self.maximum if self.maximum > center + 0.05 else 1.0
        return AxisCalibration(center=center, minimum=minimum, maximum=maximum,
                               deadzone=deadzone, invert=invert)


class CalibrationSession:
    """Collects neutral and full-range samples for every physical axis."""

    def __init__(self) -> None:
        self.axes: Dict[int, AxisStats] = {}

    def observe(self, raw_axes: Dict[int, float], neutral: bool = False) -> None:
        for index, value in raw_axes.items():
            self.axes.setdefault(index, AxisStats()).observe(value, neutral=neutral)

    def calibration_for_mapping(self, axis_map: Dict[str, int]) -> Dict[str, AxisCalibration]:
        out: Dict[str, AxisCalibration] = {}
        for name, index in axis_map.items():
            stats = self.axes.get(index)
            invert = name in ("LY", "RY")
            out[name] = stats.build(invert=invert) if stats else AxisCalibration(invert=invert)
        return out

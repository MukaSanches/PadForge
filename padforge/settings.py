from __future__ import annotations
import json
import os
from pathlib import Path
from dataclasses import asdict
from typing import Dict
from .models import DeviceMapping, AxisCalibration


def user_dir() -> Path:
    root = os.getenv("APPDATA") or str(Path.home())
    path = Path(root) / "PadForge"
    path.mkdir(parents=True, exist_ok=True)
    return path


def mapping_path() -> Path:
    return user_dir() / "device_mapping.json"


def calibration_path() -> Path:
    return user_dir() / "calibration.json"


def load_mapping() -> DeviceMapping:
    path = mapping_path()
    if not path.exists():
        return DeviceMapping()
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        return DeviceMapping(**raw)
    except Exception:
        return DeviceMapping()


def save_mapping(mapping: DeviceMapping) -> None:
    mapping_path().write_text(json.dumps(asdict(mapping), ensure_ascii=False, indent=2), encoding="utf-8")


def load_calibrations() -> Dict[str, AxisCalibration]:
    path = calibration_path()
    if not path.exists():
        return {name: AxisCalibration() for name in ("lx", "ly", "rx", "ry")}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        result = {name: AxisCalibration(**raw.get(name, {})) for name in ("lx", "ly", "rx", "ry")}
        return result
    except Exception:
        return {name: AxisCalibration() for name in ("lx", "ly", "rx", "ry")}


def save_calibrations(calibrations: Dict[str, AxisCalibration]) -> None:
    data = {name: asdict(value) for name, value in calibrations.items()}
    calibration_path().write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

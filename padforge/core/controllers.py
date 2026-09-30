from __future__ import annotations

import hashlib
import json
import os
from dataclasses import fields
from typing import Dict, Optional

from .models import AxisCalibration, ControllerConfig, ControllerMapping, default_physical_calibration


def controller_key(guid: str, name: str) -> str:
    identity = f"{(guid or 'unknown').strip().lower()}|{(name or 'unknown').strip().lower()}"
    return hashlib.sha1(identity.encode("utf-8", errors="replace")).hexdigest()[:20]


def _mapping_from_dict(data: dict) -> ControllerMapping:
    default = ControllerMapping()
    dpad_hat = data.get("dpad_hat", default.dpad_hat)
    if dpad_hat is not None:
        dpad_hat = int(dpad_hat)
    return ControllerMapping(
        axis_map={str(k): int(v) for k, v in data.get("axis_map", {}).items()} or dict(default.axis_map),
        button_map={str(k): int(v) for k, v in data.get("button_map", {}).items()} or dict(default.button_map),
        dpad_hat=dpad_hat,
        dpad_buttons={str(k): int(v) for k, v in data.get("dpad_buttons", {}).items()},
    )


def _calibration_from_dict(data: dict) -> Dict[str, AxisCalibration]:
    result = default_physical_calibration()
    allowed = {f.name for f in fields(AxisCalibration)}
    for axis, cfg in data.items():
        if not isinstance(cfg, dict):
            continue
        base = result.get(axis, AxisCalibration())
        values = {f.name: getattr(base, f.name) for f in fields(AxisCalibration)}
        values.update({k: v for k, v in cfg.items() if k in allowed})
        result[str(axis)] = AxisCalibration(**values)
    return result


class ControllerConfigStore:
    """Persistent physical-controller identity, mapping and analog calibration.

    Game profiles never overwrite this store. One controller configuration therefore works
    across every game profile and survives SDL instance-id changes between Windows boots.
    """

    def __init__(self, path: str) -> None:
        self.path = path
        self.configs: Dict[str, ControllerConfig] = {}
        self.load()

    def load(self) -> None:
        self.configs.clear()
        if not self.path or not os.path.exists(self.path):
            return
        try:
            with open(self.path, "r", encoding="utf-8") as handle:
                payload = json.load(handle)
            for item in payload.get("controllers", []):
                cfg = ControllerConfig(
                    key=str(item["key"]),
                    device_name=str(item.get("device_name", "Unknown controller")),
                    guid=str(item.get("guid", "unknown")),
                    mapping=_mapping_from_dict(item.get("mapping", {})),
                    calibration=_calibration_from_dict(item.get("calibration", {})),
                    metadata=dict(item.get("metadata", {})),
                )
                self.configs[cfg.key] = cfg
        except Exception:
            self.configs.clear()

    def save(self) -> None:
        parent = os.path.dirname(self.path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        temp = self.path + ".tmp"
        with open(temp, "w", encoding="utf-8") as handle:
            json.dump({"controllers": [c.to_dict() for c in self.configs.values()]}, handle,
                      ensure_ascii=False, indent=2)
        os.replace(temp, self.path)

    def get(self, key: str) -> Optional[ControllerConfig]:
        return self.configs.get(key)

    def get_or_create(self, guid: str, name: str) -> ControllerConfig:
        key = controller_key(guid, name)
        existing = self.configs.get(key)
        if existing is not None:
            existing.device_name = name or existing.device_name
            existing.guid = guid or existing.guid
            return existing
        cfg = ControllerConfig(key=key, device_name=name or "Unknown controller", guid=guid or "unknown")
        self.configs[key] = cfg
        self.save()
        return cfg

    def update(self, config: ControllerConfig) -> None:
        self.configs[config.key] = config
        self.save()

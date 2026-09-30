from __future__ import annotations

import json
import os
from dataclasses import fields
from typing import Dict, List, Optional

from .models import Profile, ControllerMapping, AxisCalibration, default_profile_tuning


def _profile_from_dict(data: dict) -> Profile:
    mapping_data = data.get("mapping", {})
    default_mapping = ControllerMapping()
    dpad_hat = mapping_data.get("dpad_hat", default_mapping.dpad_hat)
    if dpad_hat is not None:
        dpad_hat = int(dpad_hat)
    mapping = ControllerMapping(
        axis_map={k: int(v) for k, v in mapping_data.get("axis_map", {}).items()} or dict(default_mapping.axis_map),
        button_map={k: int(v) for k, v in mapping_data.get("button_map", {}).items()} or dict(default_mapping.button_map),
        dpad_hat=dpad_hat,
        dpad_buttons={k: int(v) for k, v in mapping_data.get("dpad_buttons", {}).items()},
    )

    calibration = default_profile_tuning()
    allowed = {f.name for f in fields(AxisCalibration)}
    for name, cfg in data.get("calibration", {}).items():
        if not isinstance(cfg, dict):
            continue
        base = calibration.get(name, AxisCalibration())
        values = {f.name: getattr(base, f.name) for f in fields(AxisCalibration)}
        values.update({k: v for k, v in cfg.items() if k in allowed})
        calibration[name] = AxisCalibration(**values)

    defaults = Profile(id="tmp", name="tmp")
    remap = dict(defaults.remap)
    remap.update({str(k): str(v) for k, v in (data.get("remap", {}) or {}).items()})

    return Profile(
        id=data["id"],
        name=data.get("name", data["id"]),
        description=data.get("description", ""),
        match_processes=[str(x).lower() for x in data.get("match_processes", [])],
        output=data.get("output", "x360"),
        mapping=mapping,
        calibration=calibration,
        remap=remap,
        turbo_hz={k: float(v) for k, v in data.get("turbo_hz", {}).items()},
        extra_bindings={str(k): str(v) for k, v in data.get("extra_bindings", {}).items()},
        metadata=dict(data.get("metadata", {})),
    )


class ProfileStore:
    def __init__(self, builtin_path: str, user_path: str) -> None:
        self.builtin_path = builtin_path
        self.user_path = user_path
        self.profiles: Dict[str, Profile] = {}

    def load(self) -> None:
        self.profiles.clear()
        for path in (self.builtin_path, self.user_path):
            if not path or not os.path.exists(path):
                continue
            with open(path, "r", encoding="utf-8") as handle:
                payload = json.load(handle)
            for item in payload.get("profiles", []):
                profile = _profile_from_dict(item)
                self.profiles[profile.id] = profile

    def all(self) -> List[Profile]:
        return list(self.profiles.values())

    def get(self, profile_id: str) -> Optional[Profile]:
        return self.profiles.get(profile_id)

    def match_process(self, executable_name: str) -> Optional[Profile]:
        name = os.path.basename(executable_name).lower()
        for profile in self.profiles.values():
            if name in profile.match_processes:
                return profile
        return None

    def save_user_profiles(self, profiles: List[Profile]) -> None:
        """Merge profile overrides instead of accidentally deleting previous user profiles."""
        existing: Dict[str, dict] = {}
        if os.path.exists(self.user_path):
            try:
                with open(self.user_path, "r", encoding="utf-8") as handle:
                    for item in json.load(handle).get("profiles", []):
                        if isinstance(item, dict) and item.get("id"):
                            existing[str(item["id"])] = item
            except Exception:
                existing = {}
        for profile in profiles:
            existing[profile.id] = profile.to_dict()
        parent = os.path.dirname(self.user_path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        temp = self.user_path + ".tmp"
        with open(temp, "w", encoding="utf-8") as handle:
            json.dump({"profiles": list(existing.values())}, handle, ensure_ascii=False, indent=2)
        os.replace(temp, self.user_path)

from __future__ import annotations
import json
import sys
from pathlib import Path
from typing import List, Optional
from .models import Profile


def resource_root() -> Path:
    if hasattr(sys, "_MEIPASS"):
        return Path(getattr(sys, "_MEIPASS"))
    return Path(__file__).resolve().parent.parent


BUILTIN_DIR = resource_root() / "profiles"


class ProfileManager:
    def __init__(self, profile_dir: Path | None = None):
        self.profile_dir = Path(profile_dir) if profile_dir else BUILTIN_DIR
        self.profiles: List[Profile] = []
        self.load()

    def load(self) -> None:
        self.profiles.clear()
        if not self.profile_dir.exists():
            return
        for path in sorted(self.profile_dir.glob("*.json")):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                self.profiles.append(Profile(**data))
            except (OSError, ValueError, TypeError):
                continue

    def names(self) -> List[str]:
        return [p.name for p in self.profiles]

    def get(self, name: str) -> Optional[Profile]:
        return next((p for p in self.profiles if p.name == name), None)

    def match_executable(self, executable: str) -> Optional[Profile]:
        exe = Path(executable).name.lower()
        for profile in self.profiles:
            if any(Path(item).name.lower() == exe for item in profile.executables):
                return profile
        return None

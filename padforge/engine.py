from __future__ import annotations
import threading
import time
from typing import Callable, Optional
from .models import ControllerState, Profile
from .processing import process_state
from .foreground import foreground_executable


class PadForgeEngine:
    def __init__(self, input_backend, output_backend, profile_manager):
        self.input = input_backend
        self.output = output_backend
        self.profiles = profile_manager
        self.profile: Profile = profile_manager.profiles[0] if profile_manager.profiles else Profile("Default")
        self.auto_profile = True
        self.running = False
        self.state = ControllerState.neutral()
        self.raw = None
        self.status_callback: Optional[Callable[[ControllerState], None]] = None
        self._thread = None
        self._last_exe = ""

    def set_profile(self, profile: Profile):
        self.profile = profile

    def start(self):
        if self.running:
            return
        self.running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self.running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)
        self.output.close()

    def _loop(self):
        last_profile_check = 0.0
        while self.running:
            started = time.perf_counter()
            try:
                raw_state = self.input.read()
                self.raw = self.input.raw_snapshot()
                self.state = process_state(raw_state, self.profile)
                self.output.send(self.state, self.profile)
                if self.status_callback:
                    self.status_callback(self.state)
            except Exception:
                time.sleep(0.1)

            now = time.monotonic()
            if self.auto_profile and now - last_profile_check >= 0.75:
                last_profile_check = now
                exe = foreground_executable()
                if exe and exe != self._last_exe:
                    self._last_exe = exe
                    match = self.profiles.match_executable(exe)
                    if match:
                        self.profile = match

            elapsed = time.perf_counter() - started
            time.sleep(max(0.0, (1 / 250.0) - elapsed))

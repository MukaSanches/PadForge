from __future__ import annotations
import os
from typing import Optional
class ForegroundProcessWatcher:
    def current_executable(self)->Optional[str]:
        if os.name!='nt':return None
        try:
            import ctypes,psutil
            user32=ctypes.windll.user32; hwnd=user32.GetForegroundWindow()
            if not hwnd:return None
            pid=ctypes.c_ulong(); user32.GetWindowThreadProcessId(hwnd,ctypes.byref(pid))
            if not pid.value:return None
            return psutil.Process(pid.value).name()
        except Exception:return None

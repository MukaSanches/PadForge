from __future__ import annotations
import threading,time
from dataclasses import dataclass
from typing import Callable,Dict,List,Optional
from padforge.core.models import RawState
@dataclass
class DeviceInfo:
    index:int; instance_id:int; name:str; guid:str; axes:int; buttons:int; hats:int
class PygameInputManager:
    def __init__(self,poll_hz:int=250):
        self.poll_hz=max(30,min(1000,poll_hz)); self._pygame=None; self._joysticks:Dict[int,object]={}; self._states:Dict[int,RawState]={}; self._lock=threading.RLock(); self._thread:Optional[threading.Thread]=None; self._stop=threading.Event(); self.on_devices_changed:Optional[Callable[[List[DeviceInfo]],None]]=None
    def start(self):
        if self._thread and self._thread.is_alive(): return
        import pygame
        self._pygame=pygame; pygame.init(); pygame.joystick.init(); self._stop.clear(); self._refresh_devices(); self._thread=threading.Thread(target=self._run,name='PadForgeInput',daemon=True); self._thread.start()
    def stop(self):
        self._stop.set()
        if self._thread and self._thread.is_alive(): self._thread.join(timeout=1.5)
        if self._pygame:
            try:self._pygame.joystick.quit(); self._pygame.quit()
            except Exception:pass
        self._thread=None
    def _refresh_devices(self):
        pygame=self._pygame
        if not pygame:return
        with self._lock:
            fresh={}
            for i in range(pygame.joystick.get_count()):
                joy=pygame.joystick.Joystick(i); joy.init(); iid=joy.get_instance_id() if hasattr(joy,'get_instance_id') else i; fresh[iid]=joy; self._states.setdefault(iid,RawState())
            self._joysticks=fresh; valid=set(fresh); self._states={k:v for k,v in self._states.items() if k in valid}
        if self.on_devices_changed:self.on_devices_changed(self.devices())
    def devices(self):
        out=[]
        with self._lock:
            for index,(iid,joy) in enumerate(self._joysticks.items()):
                try:guid=joy.get_guid() if hasattr(joy,'get_guid') else 'unknown'
                except Exception:guid='unknown'
                out.append(DeviceInfo(index,iid,joy.get_name(),str(guid),joy.get_numaxes(),joy.get_numbuttons(),joy.get_numhats()))
        return out
    def state(self,instance_id:int):
        with self._lock:
            s=self._states.get(instance_id,RawState()); return RawState(dict(s.axes),dict(s.buttons),dict(s.hats))
    def rumble(self,instance_id:int,low_frequency:float,high_frequency:float,duration_ms:int=220)->bool:
        with self._lock:
            joy=self._joysticks.get(instance_id)
            if joy is None or not hasattr(joy,'rumble'):return False
            try:return bool(joy.rumble(max(0.0,min(1.0,low_frequency)),max(0.0,min(1.0,high_frequency)),max(0,int(duration_ms))))
            except Exception:return False
    def _run(self):
        pygame=self._pygame; period=1.0/float(self.poll_hz); last_count=-1
        while not self._stop.is_set():
            started=time.perf_counter()
            try:
                pygame.event.pump(); count=pygame.joystick.get_count()
                if count!=last_count:last_count=count; self._refresh_devices()
                with self._lock:
                    for iid,joy in list(self._joysticks.items()): self._states[iid]=RawState(axes={i:float(joy.get_axis(i)) for i in range(joy.get_numaxes())},buttons={i:bool(joy.get_button(i)) for i in range(joy.get_numbuttons())},hats={i:tuple(joy.get_hat(i)) for i in range(joy.get_numhats())})
            except Exception:
                try:self._refresh_devices()
                except Exception:pass
            self._stop.wait(max(0.001,period-(time.perf_counter()-started)))

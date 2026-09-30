from __future__ import annotations
import threading,time
from dataclasses import dataclass
from typing import Dict,Optional
from padforge.core.controllers import ControllerConfigStore
from padforge.core.engine import ProcessingEngine
from padforge.core.models import CanonicalState,Profile
from padforge.core.profiles import ProfileStore
from padforge.input.pygame_input import PygameInputManager
from padforge.output.vigem import VigemXboxOutput
from padforge.output.keyboard_mouse import KeyboardMouseActions
from padforge.system.process_watcher import ForegroundProcessWatcher
@dataclass
class RuntimeStatus:
    running:bool=False; device_name:str='Nenhum controle'; controller_key:str=''; profile_name:str='-'; output_name:str='Desconectado'; error:str=''; input_hz:float=0.0; physical_count:int=0; virtual_count:int=0; foreground_process:str=''
class PadForgeRuntime:
    def __init__(self,profiles:ProfileStore,controllers:ControllerConfigStore,poll_hz:int=250):
        self.profiles=profiles; self.controllers=controllers; self.input=PygameInputManager(poll_hz=poll_hz); self.engine=ProcessingEngine(); self.process_watcher=ForegroundProcessWatcher(); self.actions=KeyboardMouseActions(); self.status=RuntimeStatus(); self.selected_instance:Optional[int]=None; self.profile_id='universal'; self.manual_profile_id='universal'; self.auto_profile=True; self._outputs:Dict[int,VigemXboxOutput]={}; self._thread:Optional[threading.Thread]=None; self._stop=threading.Event(); self._state_lock=threading.RLock(); self._latest_state=CanonicalState(); self._states:Dict[int,CanonicalState]={}; self._prev_physical_buttons:Dict[str,bool]={}; self._last_auto_check=0.0
    def start(self):
        if self._thread and self._thread.is_alive():return
        self._stop.clear(); self.status.error=''
        try:self.input.start()
        except Exception as exc:self.status.error=f'Falha ao iniciar SDL/Pygame: {exc}'; self.status.running=False; return
        self._thread=threading.Thread(target=self._run,name='PadForgeRuntime',daemon=True); self._thread.start(); self.status.running=True
    def stop(self):
        self._stop.set()
        if self._thread and self._thread.is_alive():self._thread.join(timeout=2.0)
        self.input.stop(); self._close_all_outputs(); self.status.running=False; self.status.output_name='Desconectado'
    def _close_all_outputs(self):
        for output in list(self._outputs.values()):
            try:output.close()
            except Exception:pass
        self._outputs.clear(); self.status.virtual_count=0
    def devices(self):return self.input.devices()
    def device_info(self,instance_id:Optional[int]=None):
        iid=instance_id if instance_id is not None else self.selected_instance
        if iid is None:return None
        return next((d for d in self.input.devices() if d.instance_id==iid),None)
    def raw_state(self,instance_id:Optional[int]=None):
        iid=instance_id if instance_id is not None else self.selected_instance
        return self.input.state(iid) if iid is not None else None
    def select_device(self,instance_id:Optional[int]):self.selected_instance=instance_id
    def selected_controller_config(self):
        info=self.device_info()
        if info is None:return None
        return self.controllers.get_or_create(info.guid,info.name)
    def set_profile(self,profile_id:str,manual:bool=True):
        if self.profiles.get(profile_id):
            self.profile_id=profile_id
            if manual:self.manual_profile_id=profile_id
    def latest_state(self,instance_id:Optional[int]=None)->CanonicalState:
        with self._state_lock:
            iid=instance_id if instance_id is not None else self.selected_instance
            if iid is not None and iid in self._states:return self._states[iid].clone()
            return self._latest_state.clone()
    def _active_profile(self)->Profile:
        profile=self.profiles.get(self.profile_id) or self.profiles.get(self.manual_profile_id) or self.profiles.get('universal')
        if profile is None:raise RuntimeError('Nenhum perfil disponível')
        return profile
    def _ensure_output(self,instance_id:int,profile:Profile):
        if profile.output=='none':
            output=self._outputs.pop(instance_id,None)
            if output:output.close()
            return None
        if profile.output!='x360':raise RuntimeError(f'Backend de saída desconhecido: {profile.output}')
        output=self._outputs.get(instance_id)
        if output is None:
            output=VigemXboxOutput(rumble_callback=lambda large,small,iid=instance_id:self.input.rumble(iid,large,small)); output.connect(); self._outputs[instance_id]=output
        return output
    def _auto_profile_tick(self):
        now=time.monotonic()
        if not self.auto_profile or now-self._last_auto_check<0.75:
            if not self.auto_profile:self.profile_id=self.manual_profile_id
            return
        self._last_auto_check=now; exe=self.process_watcher.current_executable(); self.status.foreground_process=exe or ''; profile=self.profiles.match_process(exe) if exe else None; self.profile_id=profile.id if profile else self.manual_profile_id
    def _run_extra_bindings(self,physical:CanonicalState,profile:Profile):
        for source,action in profile.extra_bindings.items():
            pressed=physical.buttons.get(source,False); before=self._prev_physical_buttons.get(source,False)
            if pressed and not before:
                try:self.actions.execute(action)
                except Exception:pass
        self._prev_physical_buttons=dict(physical.buttons)
    def _remove_stale_outputs(self,valid_ids):
        for iid in list(self._outputs):
            if iid not in valid_ids:
                try:self._outputs[iid].close()
                finally:self._outputs.pop(iid,None)
    def _run(self):
        frames=0; meter_started=time.monotonic()
        while not self._stop.is_set():
            loop_started=time.perf_counter()
            try:
                self._auto_profile_tick(); devices=self.input.devices()[:4]; self.status.physical_count=len(devices)
                if not devices:
                    self.status.device_name='Nenhum controle'; self.status.controller_key=''; self._remove_stale_outputs(set()); self.status.virtual_count=0; self._stop.wait(0.05); continue
                if self.selected_instance is None or not any(d.instance_id==self.selected_instance for d in devices):self.selected_instance=devices[0].instance_id
                profile=self._active_profile(); self.status.profile_name=profile.name; valid_ids={d.instance_id for d in devices}; self._remove_stale_outputs(valid_ids)
                for info in devices:
                    raw=self.input.state(info.instance_id); controller=self.controllers.get_or_create(info.guid,info.name); physical=self.engine.map_physical(raw,controller.mapping,controller.calibration); processed=self.engine.apply_profile(physical,profile)
                    if info.instance_id==self.selected_instance:self.status.device_name=info.name; self.status.controller_key=controller.key; self._run_extra_bindings(processed,profile)
                    output=self._ensure_output(info.instance_id,profile)
                    if output:output.send(processed)
                    with self._state_lock:
                        self._states[info.instance_id]=processed
                        if info.instance_id==self.selected_instance:self._latest_state=processed
                self.status.virtual_count=len(self._outputs); self.status.output_name='Somente diagnóstico' if profile.output=='none' else f'Xbox 360 virtual • {len(self._outputs)} controle(s)'; self.status.error=''; frames+=1; now=time.monotonic()
                if now-meter_started>=1.0:self.status.input_hz=frames/(now-meter_started); frames=0; meter_started=now
            except Exception as exc:self.status.error=str(exc); self._close_all_outputs(); self._stop.wait(0.25)
            target=1.0/float(max(30,self.input.poll_hz)); elapsed=time.perf_counter()-loop_started
            if elapsed<target:self._stop.wait(target-elapsed)

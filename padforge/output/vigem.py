from __future__ import annotations
from typing import Callable,Dict,Optional
from padforge.core.models import CanonicalState
from .base import OutputBackend
class VigemXboxOutput(OutputBackend):
    name='Xbox 360 virtual'
    def __init__(self,rumble_callback:Optional[Callable[[float,float],None]]=None):
        self._vg=None; self._pad=None; self._button_enum:Dict[str,object]={}; self._rumble_callback=rumble_callback; self._notification_registered=False
    def connect(self):
        if self._pad is not None:return
        import vgamepad as vg
        self._vg=vg; self._pad=vg.VX360Gamepad(); X=vg.XUSB_BUTTON
        self._button_enum={'SOUTH':X.XUSB_GAMEPAD_A,'EAST':X.XUSB_GAMEPAD_B,'WEST':X.XUSB_GAMEPAD_X,'NORTH':X.XUSB_GAMEPAD_Y,'L1':X.XUSB_GAMEPAD_LEFT_SHOULDER,'R1':X.XUSB_GAMEPAD_RIGHT_SHOULDER,'SELECT':X.XUSB_GAMEPAD_BACK,'START':X.XUSB_GAMEPAD_START,'L3':X.XUSB_GAMEPAD_LEFT_THUMB,'R3':X.XUSB_GAMEPAD_RIGHT_THUMB,'DPAD_UP':X.XUSB_GAMEPAD_DPAD_UP,'DPAD_DOWN':X.XUSB_GAMEPAD_DPAD_DOWN,'DPAD_LEFT':X.XUSB_GAMEPAD_DPAD_LEFT,'DPAD_RIGHT':X.XUSB_GAMEPAD_DPAD_RIGHT}
        if self._rumble_callback is not None and hasattr(self._pad,'register_notification'):
            callback=self._rumble_callback
            def on_notification(client,target,large_motor,small_motor,led_number,user_data):
                try:callback(float(large_motor)/255.0,float(small_motor)/255.0)
                except Exception:pass
            self._pad.register_notification(callback_function=on_notification); self._notification_registered=True
    def send(self,state:CanonicalState):
        if self._pad is None:self.connect()
        pad=self._pad
        for name,enum in self._button_enum.items():
            if state.buttons.get(name,False):pad.press_button(button=enum)
            else:pad.release_button(button=enum)
        pad.left_trigger_float(value_float=max(0.0,min(1.0,state.axes.get('LT',0.0)))); pad.right_trigger_float(value_float=max(0.0,min(1.0,state.axes.get('RT',0.0))))
        pad.left_joystick_float(x_value_float=max(-1.0,min(1.0,state.axes.get('LX',0.0))),y_value_float=max(-1.0,min(1.0,state.axes.get('LY',0.0))))
        pad.right_joystick_float(x_value_float=max(-1.0,min(1.0,state.axes.get('RX',0.0))),y_value_float=max(-1.0,min(1.0,state.axes.get('RY',0.0))))
        pad.update()
    def reset(self):
        if self._pad is not None:self._pad.reset(); self._pad.update()
    def close(self):
        try:
            if self._pad is not None and self._notification_registered and hasattr(self._pad,'unregister_notification'):
                try:self._pad.unregister_notification()
                except Exception:pass
            self.reset()
        finally:self._notification_registered=False; self._pad=None; self._vg=None

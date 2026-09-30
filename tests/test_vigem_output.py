import sys,types,unittest
from unittest.mock import patch
from padforge.core.models import CanonicalState
from padforge.output.vigem import VigemXboxOutput
class FakeButtons:
    XUSB_GAMEPAD_A=1; XUSB_GAMEPAD_B=2; XUSB_GAMEPAD_X=4; XUSB_GAMEPAD_Y=8; XUSB_GAMEPAD_LEFT_SHOULDER=16; XUSB_GAMEPAD_RIGHT_SHOULDER=32; XUSB_GAMEPAD_BACK=64; XUSB_GAMEPAD_START=128; XUSB_GAMEPAD_LEFT_THUMB=256; XUSB_GAMEPAD_RIGHT_THUMB=512; XUSB_GAMEPAD_DPAD_UP=1024; XUSB_GAMEPAD_DPAD_DOWN=2048; XUSB_GAMEPAD_DPAD_LEFT=4096; XUSB_GAMEPAD_DPAD_RIGHT=8192
class FakePad:
    def __init__(self):self.pressed=set(); self.lt=self.rt=0; self.left=self.right=(0,0); self.callback=None
    def register_notification(self,callback_function):self.callback=callback_function
    def unregister_notification(self):self.callback=None
    def press_button(self,button):self.pressed.add(button)
    def release_button(self,button):self.pressed.discard(button)
    def left_trigger_float(self,value_float):self.lt=value_float
    def right_trigger_float(self,value_float):self.rt=value_float
    def left_joystick_float(self,x_value_float,y_value_float):self.left=(x_value_float,y_value_float)
    def right_joystick_float(self,x_value_float,y_value_float):self.right=(x_value_float,y_value_float)
    def update(self):pass
    def reset(self):self.pressed.clear()
class VigemOutputTests(unittest.TestCase):
    def fake_module(self):return types.SimpleNamespace(XUSB_BUTTON=FakeButtons,VX360Gamepad=FakePad)
    def test_send_and_rumble_callback(self):
        received=[]
        with patch.dict(sys.modules,{'vgamepad':self.fake_module()}):
            out=VigemXboxOutput(lambda large,small:received.append((large,small))); out.connect(); state=CanonicalState(); state.buttons['SOUTH']=True; state.axes['LX']=.5; state.axes['LT']=.25; out.send(state); self.assertIn(FakeButtons.XUSB_GAMEPAD_A,out._pad.pressed); self.assertEqual(out._pad.left,(.5,0.0)); self.assertEqual(out._pad.lt,.25); out._pad.callback(None,None,255,128,0,None); self.assertAlmostEqual(received[0][0],1.0); self.assertAlmostEqual(received[0][1],128/255); out.close()
if __name__=='__main__':unittest.main()

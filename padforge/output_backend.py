from __future__ import annotations
from .models import ControllerState, Profile
from .processing import turbo_active


class NullOutput:
    name = "Monitor only"
    available = True
    def send(self, state: ControllerState, profile: Profile):
        return
    def close(self):
        return


class X360Output:
    name = "Xbox 360 virtual (XInput)"

    def __init__(self):
        self.available = False
        self.error = ""
        self._pad = None
        self._vg = None
        try:
            import vgamepad as vg
            self._vg = vg
            self._pad = vg.VX360Gamepad()
            self.available = True
        except Exception as exc:
            self.error = str(exc)

    def send(self, state: ControllerState, profile: Profile):
        if not self.available:
            return
        vg, pad = self._vg, self._pad
        pad.reset()
        button_map = {
            "a": vg.XUSB_BUTTON.XUSB_GAMEPAD_A,
            "b": vg.XUSB_BUTTON.XUSB_GAMEPAD_B,
            "x": vg.XUSB_BUTTON.XUSB_GAMEPAD_X,
            "y": vg.XUSB_BUTTON.XUSB_GAMEPAD_Y,
            "lb": vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER,
            "rb": vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER,
            "back": vg.XUSB_BUTTON.XUSB_GAMEPAD_BACK,
            "start": vg.XUSB_BUTTON.XUSB_GAMEPAD_START,
            "ls": vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_THUMB,
            "rs": vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_THUMB,
            "dpad_up": vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP,
            "dpad_down": vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN,
            "dpad_left": vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT,
            "dpad_right": vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT,
        }
        for logical, xbutton in button_map.items():
            if state.buttons.get(logical, False) and turbo_active(logical, profile):
                pad.press_button(button=xbutton)
        pad.left_joystick_float(state.axes.get("lx", 0.0), -state.axes.get("ly", 0.0))
        pad.right_joystick_float(state.axes.get("rx", 0.0), -state.axes.get("ry", 0.0))
        pad.left_trigger_float(max(0.0, min(1.0, state.axes.get("lt", 0.0))))
        pad.right_trigger_float(max(0.0, min(1.0, state.axes.get("rt", 0.0))))
        pad.update()

    def close(self):
        if self.available:
            try:
                self._pad.reset()
                self._pad.update()
            except Exception:
                pass

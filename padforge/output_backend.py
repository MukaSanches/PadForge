from __future__ import annotations
from .models import ControllerState, Profile
from .processing import turbo_active


class NullOutput:
    name = "Monitor only"
    available = True
    def set_rumble_handler(self, handler):
        self._rumble_handler = handler
        if not self.available or self._notification_registered:
            return

        def callback(client, target, large_motor, small_motor, led_number, user_data):
            if self._rumble_handler is None:
                return
            try:
                low = float(large_motor) / 255.0
                high = float(small_motor) / 255.0
                self._rumble_handler(low, high)
            except Exception:
                pass

        try:
            self._pad.register_notification(callback_function=callback)
            self._notification_callback = callback
            self._notification_registered = True
        except Exception:
            self._notification_callback = None
            self._notification_registered = False

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
        self._rumble_handler = None
        self._notification_registered = False
        self._notification_callback = None
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
                if self._notification_registered:
                    self._pad.unregister_notification()
            except Exception:
                pass
            try:
                self._pad.reset()
                self._pad.update()
            except Exception:
                pass

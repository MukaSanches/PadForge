import unittest
from padforge.models import AxisCalibration, ControllerState, Profile
from padforge.processing import normalize_axis, radial_deadzone, process_state, turbo_active


class ProcessingTests(unittest.TestCase):
    def test_deadzone_centers_small_input(self):
        x, y = radial_deadzone(0.03, 0.04, 0.10)
        self.assertEqual((x, y), (0.0, 0.0))

    def test_radial_deadzone_preserves_direction(self):
        x, y = radial_deadzone(0.5, 0.0, 0.1)
        self.assertGreater(x, 0.0)
        self.assertAlmostEqual(y, 0.0)

    def test_axis_inversion(self):
        cal = AxisCalibration(invert=True, deadzone=0)
        self.assertLess(normalize_axis(0.5, cal), 0)

    def test_axis_calibration_center(self):
        cal = AxisCalibration(center=0.1, minimum=-0.8, maximum=0.9, deadzone=0)
        self.assertAlmostEqual(normalize_axis(0.1, cal), 0.0)

    def test_remap(self):
        state = ControllerState.neutral()
        state.buttons["a"] = True
        profile = Profile("t", remap={"a": "b"})
        out = process_state(state, profile)
        self.assertFalse(out.buttons["a"])
        self.assertTrue(out.buttons["b"])

    def test_invert_y_profile(self):
        state = ControllerState.neutral()
        state.axes["ry"] = 0.8
        profile = Profile("t", deadzone=0, invert_y=True)
        out = process_state(state, profile)
        self.assertLess(out.axes["ry"], 0)

    def test_turbo_gate(self):
        profile = Profile("t", turbo_buttons=["a"], turbo_hz=10)
        self.assertTrue(turbo_active("b", profile, now=0))
        self.assertTrue(turbo_active("a", profile, now=0))
        self.assertFalse(turbo_active("a", profile, now=0.075))


if __name__ == "__main__":
    unittest.main()

import unittest
from padforge.core.engine import ProcessingEngine,apply_canonical_tuning
from padforge.core.models import AxisCalibration,ControllerMapping,Profile,RawState,default_physical_calibration
class EngineExtendedTests(unittest.TestCase):
    def setUp(self):self.engine=ProcessingEngine()
    def test_physical_y_axis_is_inverted_by_device_calibration(self):self.assertLess(self.engine.map_physical(RawState(axes={1:1.0}),ControllerMapping(axis_map={'LY':1}),default_physical_calibration()).axes['LY'],-.9)
    def test_dpad_as_buttons(self):
        out=self.engine.map_physical(RawState(buttons={20:True,21:True}),ControllerMapping(dpad_hat=None,dpad_buttons={'DPAD_UP':20,'DPAD_LEFT':21}),default_physical_calibration()); self.assertTrue(out.buttons['DPAD_UP']); self.assertTrue(out.buttons['DPAD_LEFT'])
    def test_remap(self):
        p=Profile(id='p',name='p'); p.remap['SOUTH']='EAST'; physical=self.engine.map_physical(RawState(buttons={0:True}),ControllerMapping(),default_physical_calibration()); out=self.engine.apply_profile(physical,p); self.assertFalse(out.buttons['SOUTH']); self.assertTrue(out.buttons['EAST'])
    def test_precision_curve_reduces_midrange(self):self.assertLess(apply_canonical_tuning(.5,AxisCalibration(deadzone=0,curve='precision')),.5)
    def test_aggressive_curve_increases_midrange(self):self.assertGreater(apply_canonical_tuning(.5,AxisCalibration(deadzone=0,curve='aggressive')),.5)
    def test_trigger_button_becomes_analog(self):self.assertEqual(self.engine.map_physical(RawState(buttons={6:True}),ControllerMapping(),default_physical_calibration()).axes['LT'],1.0)
if __name__=='__main__':unittest.main()

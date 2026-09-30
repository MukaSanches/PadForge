import unittest
from padforge.core.engine import apply_axis_curve,ProcessingEngine
from padforge.core.models import AxisCalibration,RawState,Profile
class EngineTests(unittest.TestCase):
    def test_deadzone(self):
        c=AxisCalibration(deadzone=.1); self.assertEqual(apply_axis_curve(.05,c),0.0); self.assertGreater(apply_axis_curve(.5,c),0.0)
    def test_invert(self):self.assertLess(apply_axis_curve(.5,AxisCalibration(deadzone=0,invert=True)),0.0)
    def test_clamp(self):self.assertLessEqual(apply_axis_curve(1.0,AxisCalibration(deadzone=0,sensitivity=10)),1.0)
    def test_canonical_dpad(self):
        out=ProcessingEngine().canonicalize(RawState(hats={0:(-1,1)}),Profile(id='t',name='t')); self.assertTrue(out.buttons['DPAD_LEFT']); self.assertTrue(out.buttons['DPAD_UP']); self.assertFalse(out.buttons['DPAD_RIGHT'])
    def test_digital_trigger_to_axis(self):self.assertEqual(ProcessingEngine().canonicalize(RawState(buttons={6:True}),Profile(id='t',name='t')).axes['LT'],1.0)
if __name__=='__main__':unittest.main()

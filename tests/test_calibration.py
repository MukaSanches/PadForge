import unittest
from padforge.core.calibration import AxisStats
class CalibrationTests(unittest.TestCase):
    def test_learns_range_and_drift(self):
        s=AxisStats()
        for v in (-0.02,0.0,0.03):s.observe(v,neutral=True)
        for v in (-1.0,-0.5,0.5,1.0):s.observe(v)
        c=s.build(); self.assertLessEqual(c.minimum,-0.99); self.assertGreaterEqual(c.maximum,0.99); self.assertGreaterEqual(c.deadzone,0.04); self.assertLess(c.deadzone,0.2)
if __name__=='__main__':unittest.main()

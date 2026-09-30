import os,tempfile,unittest
from padforge.core.controllers import ControllerConfigStore,controller_key
class ControllerConfigTests(unittest.TestCase):
    def test_key_is_stable(self):self.assertEqual(controller_key('ABC','USB Gamepad'),controller_key('abc','usb gamepad'))
    def test_save_and_reload(self):
        with tempfile.TemporaryDirectory() as td:
            path=os.path.join(td,'controllers.json'); store=ControllerConfigStore(path); cfg=store.get_or_create('guid-1','PS2 USB'); cfg.mapping.button_map['SOUTH']=7; cfg.calibration['LX'].deadzone=.123; store.update(cfg); got=ControllerConfigStore(path).get(cfg.key); self.assertIsNotNone(got); self.assertEqual(got.mapping.button_map['SOUTH'],7); self.assertAlmostEqual(got.calibration['LX'].deadzone,.123)
    def test_damaged_file_recovers_empty(self):
        with tempfile.TemporaryDirectory() as td:
            path=os.path.join(td,'controllers.json'); open(path,'w',encoding='utf-8').write('not json'); self.assertEqual(ControllerConfigStore(path).configs,{})
if __name__=='__main__':unittest.main()

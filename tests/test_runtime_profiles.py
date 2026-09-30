import json,os,tempfile,unittest
from padforge.core.controllers import ControllerConfigStore
from padforge.core.profiles import ProfileStore
from padforge.runtime import PadForgeRuntime
class RuntimeProfileTests(unittest.TestCase):
    def test_auto_profile_returns_to_manual(self):
        with tempfile.TemporaryDirectory() as td:
            pth=os.path.join(td,'profiles.json'); json.dump({'profiles':[{'id':'universal','name':'Universal'},{'id':'racing','name':'Racing','match_processes':['speed.exe']}]},open(pth,'w',encoding='utf-8')); profiles=ProfileStore(pth,os.path.join(td,'user.json')); profiles.load(); runtime=PadForgeRuntime(profiles,ControllerConfigStore(os.path.join(td,'controllers.json'))); runtime.set_profile('universal',manual=True); runtime._last_auto_check=-999; runtime.process_watcher.current_executable=lambda:'speed.exe'; runtime._auto_profile_tick(); self.assertEqual(runtime.profile_id,'racing'); runtime._last_auto_check=-999; runtime.process_watcher.current_executable=lambda:'explorer.exe'; runtime._auto_profile_tick(); self.assertEqual(runtime.profile_id,'universal')
if __name__=='__main__':unittest.main()

import json,os,tempfile,unittest
from padforge.core.profiles import ProfileStore
class ProfileTests(unittest.TestCase):
    def test_process_match(self):
        with tempfile.TemporaryDirectory() as td:
            p=os.path.join(td,'p.json'); json.dump({'profiles':[{'id':'nfs','name':'NFS','match_processes':['speed.exe']}]},open(p,'w',encoding='utf-8')); store=ProfileStore(p,os.path.join(td,'u.json')); store.load(); self.assertEqual(store.match_process('C:/Games/NFS/speed.exe').id,'nfs'); self.assertIsNone(store.match_process('other.exe'))
if __name__=='__main__':unittest.main()

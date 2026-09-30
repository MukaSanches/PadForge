import json,os,tempfile,unittest
from padforge.core.models import Profile
from padforge.core.profiles import ProfileStore
class ProfileStoreExtendedTests(unittest.TestCase):
    def test_user_save_merges_existing_profiles(self):
        with tempfile.TemporaryDirectory() as td:
            builtin=os.path.join(td,'builtin.json'); user=os.path.join(td,'user.json'); json.dump({'profiles':[{'id':'a','name':'A'},{'id':'b','name':'B'}]},open(builtin,'w',encoding='utf-8')); store=ProfileStore(builtin,user); store.load(); store.save_user_profiles([Profile(id='a',name='A custom')]); store.save_user_profiles([Profile(id='b',name='B custom')]); store.load(); self.assertEqual(store.get('a').name,'A custom'); self.assertEqual(store.get('b').name,'B custom')
    def test_partial_remap_keeps_identity_for_other_buttons(self):
        with tempfile.TemporaryDirectory() as td:
            builtin=os.path.join(td,'builtin.json'); json.dump({'profiles':[{'id':'x','name':'X','remap':{'SOUTH':'EAST'}}]},open(builtin,'w',encoding='utf-8')); store=ProfileStore(builtin,os.path.join(td,'user.json')); store.load(); p=store.get('x'); self.assertEqual(p.remap['SOUTH'],'EAST'); self.assertEqual(p.remap['NORTH'],'NORTH')
if __name__=='__main__':unittest.main()

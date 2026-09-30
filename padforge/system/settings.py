from __future__ import annotations
import json,os,sys
from dataclasses import dataclass,asdict
def app_data_dir()->str:
    frozen=bool(getattr(sys,'frozen',False)); app_root=os.path.dirname(os.path.abspath(sys.executable if frozen else sys.argv[0])); portable='--portable' in sys.argv or os.path.exists(os.path.join(app_root,'portable.flag'))
    path=os.path.join(app_root,'PadForgeData') if portable else os.path.join(os.getenv('APPDATA') or os.path.expanduser('~/.padforge'),'PadForge'); os.makedirs(path,exist_ok=True); return path
@dataclass
class Settings:
    profile_id:str='universal'; selected_device:int=-1; selected_device_key:str=''; poll_hz:int=250; auto_profile:bool=True; overlay:bool=False; start_minimized:bool=False
    @classmethod
    def load(cls):
        path=os.path.join(app_data_dir(),'settings.json')
        if not os.path.exists(path):return cls()
        try:
            with open(path,'r',encoding='utf-8') as f:data=json.load(f)
            allowed=set(cls.__dataclass_fields__); return cls(**{k:v for k,v in data.items() if k in allowed})
        except Exception:return cls()
    def save(self):
        path=os.path.join(app_data_dir(),'settings.json'); temp=path+'.tmp'
        with open(temp,'w',encoding='utf-8') as f:json.dump(asdict(self),f,ensure_ascii=False,indent=2)
        os.replace(temp,path)

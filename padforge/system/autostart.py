from __future__ import annotations
import os,sys
RUN_KEY=r'Software\Microsoft\Windows\CurrentVersion\Run'
def _command():
    exe=os.path.abspath(sys.executable)
    if getattr(sys,'frozen',False):return f'"{exe}" --minimized'
    main_py=os.path.abspath(os.path.join(os.path.dirname(__file__),'..','..','main.py')); return f'"{exe}" "{main_py}" --minimized'
def set_enabled(enabled:bool)->bool:
    if os.name!='nt':return False
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER,RUN_KEY,0,winreg.KEY_SET_VALUE) as key:
            if enabled:winreg.SetValueEx(key,'PadForge',0,winreg.REG_SZ,_command())
            else:
                try:winreg.DeleteValue(key,'PadForge')
                except FileNotFoundError:pass
        return True
    except Exception:return False
def is_enabled()->bool:
    if os.name!='nt':return False
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER,RUN_KEY,0,winreg.KEY_READ) as key:winreg.QueryValueEx(key,'PadForge')
        return True
    except Exception:return False

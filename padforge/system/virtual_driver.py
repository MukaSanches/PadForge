from __future__ import annotations
import os,platform,subprocess
from typing import Optional,Tuple
def vigem_installer_path()->Optional[str]:
    try:
        import vgamepad
        root=os.path.dirname(os.path.abspath(vgamepad.__file__)); arch='x64' if platform.architecture()[0]=='64bit' else 'x86'; path=os.path.join(root,'win','vigem','install',arch,f'ViGEmBusSetup_{arch}.msi'); return path if os.path.exists(path) else None
    except Exception:return None
def launch_vigem_installer()->Tuple[bool,str]:
    if os.name!='nt':return False,'O driver virtual é suportado pelo instalador apenas no Windows.'
    path=vigem_installer_path()
    if not path:return False,'O instalador do driver virtual não foi encontrado neste pacote.'
    try:subprocess.Popen(['msiexec.exe','/i',path],close_fds=True); return True,'Instalador do driver aberto. Conclua a instalação e depois reinicie o motor do PadForge.'
    except Exception as exc:return False,f'Não foi possível abrir o instalador: {exc}'
def virtual_output_probe()->Tuple[bool,str]:
    try:
        import vgamepad as vg
        pad=vg.VX360Gamepad(); pad.reset(); pad.update(); del pad; return True,'Driver virtual disponível'
    except Exception as exc:return False,str(exc)

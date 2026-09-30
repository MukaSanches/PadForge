# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs

datas=[("padforge/data/presets.json","padforge/data")]
binaries=[]
for package in ("pygame","vgamepad","pystray","PIL"):
    try: datas += collect_data_files(package)
    except Exception: pass
    try: binaries += collect_dynamic_libs(package)
    except Exception: pass

hiddenimports=[
    "pygame","vgamepad","psutil",
    "pystray","pystray._win32",
    "PIL","PIL.Image","PIL.ImageDraw",
]

a=Analysis(["main.py"],pathex=[],binaries=binaries,datas=datas,hiddenimports=hiddenimports,hookspath=[],hooksconfig={},runtime_hooks=[],excludes=[])
pyz=PYZ(a.pure)
exe=EXE(pyz,a.scripts,a.binaries,a.datas,[],name="PadForge",debug=False,bootloader_ignore_signals=False,strip=False,upx=True,console=False,disable_windowed_traceback=False)

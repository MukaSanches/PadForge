# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs

datas=[("padforge/data/presets.json","padforge/data")]
binaries=[]
for package in ("pygame","vgamepad"):
    try: datas += collect_data_files(package)
    except Exception: pass
    try: binaries += collect_dynamic_libs(package)
    except Exception: pass

a=Analysis(["main.py"],pathex=[],binaries=binaries,datas=datas,hiddenimports=["pygame","vgamepad","psutil"],hookspath=[],hooksconfig={},runtime_hooks=[],excludes=[])
pyz=PYZ(a.pure)
exe=EXE(pyz,a.scripts,a.binaries,a.datas,[],name="PadForge",debug=False,bootloader_ignore_signals=False,strip=False,upx=True,console=False,disable_windowed_traceback=False)

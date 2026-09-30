$ErrorActionPreference = "Stop"
$env:VGAMEPAD_SKIP_VIGEMBUS_INSTALL = "true"
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
python -m compileall -q padforge main.py
pyinstaller --clean --noconfirm PadForge.spec
Write-Host "Build pronto em dist/PadForge.exe"

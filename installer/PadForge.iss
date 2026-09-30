#define MyAppName "PadForge"
#define MyAppVersion "1.0.1"
#define MyAppPublisher "MukaSanches"
#define MyAppExeName "PadForge.exe"

[Setup]
AppId={{CF8D0123-39A1-4D78-91B7-101D5B12C5E7}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\PadForge
DefaultGroupName=PadForge
DisableProgramGroupPage=yes
OutputDir=..\dist-installer
OutputBaseFilename=PadForge-Setup-1.0.1
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesInstallIn64BitMode=x64
CloseApplications=yes
RestartApplications=no
UninstallDisplayName=PadForge

[Files]
Source: "..\dist\PadForge.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\PadForge"; Filename: "{app}\PadForge.exe"
Name: "{autodesktop}\PadForge"; Filename: "{app}\PadForge.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Criar atalho na Área de Trabalho"; GroupDescription: "Atalhos:"; Flags: unchecked

[Registry]
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "PadForge"; ValueData: """{app}\PadForge.exe"" --minimized"; Flags: uninsdeletevalue

[Run]
Filename: "{app}\PadForge.exe"; Description: "Abrir PadForge"; Flags: nowait postinstall skipifsilent

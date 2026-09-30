#define MyAppName "PadForge"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "MukaSanches"
#define MyAppExeName "PadForge.exe"

[Setup]
AppId={{A9352E72-0EF0-4B83-BBE7-6A7D7CFEF101}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\PadForge
DefaultGroupName=PadForge
OutputDir=..\dist-installer
OutputBaseFilename=PadForge-Setup-v{#MyAppVersion}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=admin

[Files]
Source: "..\dist\PadForge\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\profiles\*"; DestDir: "{app}\profiles"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\PadForge"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\PadForge"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Criar atalho na área de trabalho"; GroupDescription: "Atalhos:"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Abrir PadForge"; Flags: nowait postinstall skipifsilent

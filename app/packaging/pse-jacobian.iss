; Inno Setup script; build_exe.sh passes AppVersion, SourceDir, OutDir. Per-user install.
#define AppName "PSE-Jacobian"

[Setup]
AppId={{e44ffc50-5358-4d4d-af70-1d21f5b392cf}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher=Andrej Ristic
AppPublisherURL=https://github.com/andrejristic/pse-jacobian
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
LicenseFile={#SourceDir}\LICENSE.txt
OutputDir={#OutDir}
OutputBaseFilename=PSEJacobian-Setup-{#AppVersion}
SetupIconFile={#SourceDir}\pse-jacobian.ico
UninstallDisplayIcon={app}\pse-jacobian.exe
Compression=lzma2
SolidCompression=yes
WizardStyle=modern

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "{#SourceDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\pse-jacobian.exe"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\pse-jacobian.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\pse-jacobian.exe"; Description: "{cm:LaunchProgram,{#AppName}}"; Flags: nowait postinstall skipifsilent

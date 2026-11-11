#define MyVer "1.0.0"
[Setup]
AppId={{A8F3C291-7B46-4E1D-9C52-2D8E4A6F1B70}
AppName=PIKNOTT SAPPHIRE
AppVersion={#MyVer}
AppVerName=PIKNOTT SAPPHIRE {#MyVer}
AppPublisher=EX Inc./HYPERION DIGITAL
AppPublisherURL=https://github.com/Teobokki/piknott-sapphire
AppCopyright=©2026 EX INC.HYPERION DIGITAL ©2026
VersionInfoVersion={#MyVer}.0
VersionInfoCompany=EX Inc./HYPERION DIGITAL
VersionInfoCopyright=©2026 EX INC.HYPERION DIGITAL ©2026
VersionInfoProductName=PIKNOTT SAPPHIRE
VersionInfoDescription=PIKNOTT SAPPHIRE Setup
DefaultDirName={localappdata}\Programs\PIKNOTT SAPPHIRE
DefaultGroupName=PIKNOTT SAPPHIRE
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
OutputDir=dist
OutputBaseFilename=PIKNOTT.SAPPHIRE.Setup.{#MyVer}
SetupIconFile=assets\icon.ico
UninstallDisplayIcon={app}\PIKNOTT SAPPHIRE.exe
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
CloseApplications=yes

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[InstallDelete]
Type: filesandordirs; Name: "{app}\_internal"

[Files]
Source: "dist\PIKNOTT SAPPHIRE\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\PIKNOTT SAPPHIRE"; Filename: "{app}\PIKNOTT SAPPHIRE.exe"
Name: "{group}\Uninstall PIKNOTT SAPPHIRE"; Filename: "{uninstallexe}"
Name: "{userdesktop}\PIKNOTT SAPPHIRE"; Filename: "{app}\PIKNOTT SAPPHIRE.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\PIKNOTT SAPPHIRE.exe"; Description: "Launch PIKNOTT SAPPHIRE now"; Flags: nowait postinstall skipifsilent

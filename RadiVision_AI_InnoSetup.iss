[Setup]
AppId={{D37F8E49-6238-4C8E-9801-7F8DE8BC90F4}
AppName=RadiVision AI
AppVersion=1.0.0
AppPublisher=RadiVision AI Medical Systems
DefaultDirName={autopf}\RadiVision AI
DefaultGroupName=RadiVision AI
DisableProgramGroupPage=yes
OutputDir=.
OutputBaseFilename=RadiVision_AI_InnoSetup
SetupIconFile=frontend\public\icon.ico
UninstallDisplayIcon={app}\RadiVision AI.exe
Compression=lzma2/ultra64
SolidCompression=yes
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "frontend\dist-electron\win-unpacked\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\RadiVision AI"; Filename: "{app}\RadiVision AI.exe"
Name: "{autodesktop}\RadiVision AI"; Filename: "{app}\RadiVision AI.exe"; Tasks: desktopicon

[Run]
Description: "Launch RadiVision AI"; Filename: "{app}\RadiVision AI.exe"; Flags: nowait postinstall skipifsilent

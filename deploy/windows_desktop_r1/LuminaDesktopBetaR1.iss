#ifndef PayloadRoot
  #error PayloadRoot must identify the extracted Lumina release root.
#endif
#ifndef OutputRoot
  #define OutputRoot "."
#endif

#define MyAppName "Lumina Desktop Beta"
#define MyAppVersion "0.1.0-r1"

[Setup]
AppId={{A4E7A9AB-8797-4DDF-B09C-C0320B85C915}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher=Ethereon Initiative
DefaultDirName={localappdata}\Lumina
DefaultGroupName=Lumina
DisableDirPage=yes
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
OutputDir={#OutputRoot}
OutputBaseFilename=LuminaDesktopBetaR1-Setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
SetupLogging=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Dirs]
Name: "{app}\state\ship_of_ethereon_v2"; Flags: uninsneveruninstall
Name: "{app}\receipts"; Flags: uninsneveruninstall

[Files]
Source: "{#PayloadRoot}\EthereonLabs\*"; DestDir: "{app}\app\EthereonLabs"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "{#PayloadRoot}\EthereonLabs\deploy\windows_desktop_r1\runtime\python\*"; DestDir: "{app}\runtime\python"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "{#PayloadRoot}\EthereonLabs\deploy\windows_desktop_r1\launchers\lumina.cmd"; DestDir: "{app}\bin"; Flags: ignoreversion
Source: "{#PayloadRoot}\EthereonLabs\deploy\windows_desktop_r1\launchers\lumina-bridge.cmd"; DestDir: "{app}\bin"; Flags: ignoreversion

[Icons]
Name: "{group}\Lumina Bridge"; Filename: "{app}\bin\lumina-bridge.cmd"
Name: "{group}\Lumina Studio"; Filename: "{app}\bin\lumina.cmd"; Parameters: "studio"
Name: "{group}\Lumina Doctor"; Filename: "{app}\bin\lumina.cmd"; Parameters: "doctor"

[Run]
Filename: "{cmd}"; Parameters: "/d /c if not exist ""{app}\app\EthereonLabs\.lumina_state"" mklink /J ""{app}\app\EthereonLabs\.lumina_state"" ""{app}\state"""; Flags: runhidden waituntilterminated
Filename: "{app}\bin\lumina.cmd"; Parameters: "doctor --ensure-state"; Flags: runhidden waituntilterminated
Filename: "{app}\bin\lumina-bridge.cmd"; Description: "Open Lumina Bridge"; Flags: nowait postinstall skipifsilent

[UninstallRun]
Filename: "{cmd}"; Parameters: "/d /c if exist ""{app}\app\EthereonLabs\.lumina_state"" rmdir ""{app}\app\EthereonLabs\.lumina_state"""; Flags: runhidden waituntilterminated

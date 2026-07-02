#ifndef PayloadRoot
  #error PayloadRoot must identify the staged Lumina release root.
#endif
#ifndef OutputRoot
  #define OutputRoot "."
#endif

#define MyAppName "Lumina Desktop Beta"
#define MyAppVersion "0.1.0-r1"
#define MyPublisher "Ethereon Initiative"

[Setup]
AppId={{A4E7A9AB-8797-4DDF-B09C-C0320B85C915}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyPublisher}
DefaultDirName={localappdata}\Lumina
DefaultGroupName=Lumina
DisableDirPage=yes
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
OutputDir={#OutputRoot}
OutputBaseFilename=LuminaDesktopBetaR1-Setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
SetupLogging=yes
UninstallDisplayName={#MyAppName}
CloseApplications=yes
RestartApplications=no

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Dirs]
Name: "{app}\state\ship_of_ethereon_v2"; Flags: uninsneveruninstall
Name: "{app}\receipts"; Flags: uninsneveruninstall

[Files]
Source: "{#PayloadRoot}\EthereonLabs\*"; DestDir: "{app}\app\EthereonLabs"; Excludes: "deploy\windows_desktop_r1\runtime\python\*"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "{#PayloadRoot}\EthereonLabs\deploy\windows_desktop_r1\runtime\python\*"; DestDir: "{app}\runtime\python"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "{#PayloadRoot}\EthereonLabs\deploy\windows_desktop_r1\runtime_config\embedded_runtime_paths_r1.txt"; DestDir: "{app}\runtime\python"; DestName: "python313._pth"; Flags: ignoreversion
Source: "{#PayloadRoot}\EthereonLabs\deploy\windows_desktop_r1\launchers\lumina.cmd"; DestDir: "{app}\bin"; Flags: ignoreversion
Source: "{#PayloadRoot}\EthereonLabs\deploy\windows_desktop_r1\launchers\lumina-bridge.cmd"; DestDir: "{app}\bin"; Flags: ignoreversion

[Icons]
Name: "{group}\Lumina Bridge"; Filename: "{app}\bin\lumina-bridge.cmd"; WorkingDir: "{app}\app\EthereonLabs\LuminaOS\bootstrap\Ship_of_Ethereon_V2"
Name: "{group}\Lumina Studio"; Filename: "{app}\bin\lumina.cmd"; Parameters: "studio"; WorkingDir: "{app}\app\EthereonLabs\LuminaOS\bootstrap\Ship_of_Ethereon_V2"
Name: "{group}\Lumina Doctor"; Filename: "{app}\bin\lumina.cmd"; Parameters: "doctor"; WorkingDir: "{app}\app\EthereonLabs\LuminaOS\bootstrap\Ship_of_Ethereon_V2"

[Run]
Filename: "{cmd}"; Parameters: "/d /c if exist ""{app}\app\EthereonLabs\.lumina_state"" rmdir ""{app}\app\EthereonLabs\.lumina_state"""; StatusMsg: "Preparing persistent Lumina state..."; Flags: runhidden waituntilterminated
Filename: "{cmd}"; Parameters: "/d /c mklink /J ""{app}\app\EthereonLabs\.lumina_state"" ""{app}\state"""; StatusMsg: "Linking the continuity habitat..."; Flags: runhidden waituntilterminated
Filename: "{app}\bin\lumina.cmd"; Parameters: "doctor --ensure-state"; WorkingDir: "{app}\app\EthereonLabs\LuminaOS\bootstrap\Ship_of_Ethereon_V2"; StatusMsg: "Verifying Lumina..."; Flags: runhidden waituntilterminated
Filename: "{app}\bin\lumina-bridge.cmd"; Description: "Open Lumina Bridge"; WorkingDir: "{app}\app\EthereonLabs\LuminaOS\bootstrap\Ship_of_Ethereon_V2"; Flags: nowait postinstall skipifsilent

[UninstallRun]
Filename: "{cmd}"; Parameters: "/d /c if exist ""{app}\app\EthereonLabs\.lumina_state"" rmdir ""{app}\app\EthereonLabs\.lumina_state"""; RunOnceId: "LuminaStateJunctionRemovalR1"; Flags: runhidden waituntilterminated

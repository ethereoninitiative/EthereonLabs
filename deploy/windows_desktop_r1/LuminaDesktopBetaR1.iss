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
DefaultDirName={localappdata}\Lumina\installer
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

[Files]
Source: "{#PayloadRoot}\EthereonLabs\*"; DestDir: "{tmp}\LuminaDesktopBetaR1\EthereonLabs"; Flags: ignoreversion recursesubdirs createallsubdirs deleteafterinstall
Source: "{#PayloadRoot}\EthereonLabs\deploy\windows_desktop_r1\remove_lumina_application_r1.ps1"; DestDir: "{app}\tools"; Flags: ignoreversion

[Icons]
Name: "{group}\Lumina Bridge"; Filename: "{localappdata}\Lumina\bin\lumina-bridge.cmd"; WorkingDir: "{localappdata}\Lumina\app\EthereonLabs\LuminaOS\bootstrap\Ship_of_Ethereon_V2"
Name: "{group}\Lumina Studio"; Filename: "{localappdata}\Lumina\bin\lumina.cmd"; Parameters: "studio"; WorkingDir: "{localappdata}\Lumina\app\EthereonLabs\LuminaOS\bootstrap\Ship_of_Ethereon_V2"
Name: "{group}\Lumina Doctor"; Filename: "{localappdata}\Lumina\bin\lumina.cmd"; Parameters: "doctor"; WorkingDir: "{localappdata}\Lumina\app\EthereonLabs\LuminaOS\bootstrap\Ship_of_Ethereon_V2"

[Run]
Filename: "powershell.exe"; Parameters: "-NoProfile -ExecutionPolicy Bypass -File ""{tmp}\LuminaDesktopBetaR1\EthereonLabs\deploy\windows_desktop_r1\install_lumina_windows_bundled_r1.ps1"" -SourceRoot ""{tmp}\LuminaDesktopBetaR1\EthereonLabs"" -InstallRoot ""{localappdata}\Lumina"" -Force -SkipShortcuts"; StatusMsg: "Installing the Lumina runtime and continuity habitat..."; Flags: runhidden waituntilterminated
Filename: "{localappdata}\Lumina\bin\lumina-bridge.cmd"; Description: "Open Lumina Bridge"; WorkingDir: "{localappdata}\Lumina\app\EthereonLabs\LuminaOS\bootstrap\Ship_of_Ethereon_V2"; Flags: nowait postinstall skipifsilent

[UninstallRun]
Filename: "powershell.exe"; Parameters: "-NoProfile -ExecutionPolicy Bypass -File ""{app}\tools\remove_lumina_application_r1.ps1"" -InstallRoot ""{localappdata}\Lumina"""; RunOnceId: "LuminaApplicationRemovalR1"; Flags: runhidden waituntilterminated

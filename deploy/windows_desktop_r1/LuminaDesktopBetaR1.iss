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
DefaultDirName={localappdata}\Lumina\installer
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

[Files]
Source: "{#PayloadRoot}\EthereonLabs\*"; DestDir: "{tmp}\LuminaDesktopBetaR1\EthereonLabs"; Flags: ignoreversion recursesubdirs createallsubdirs deleteafterinstall

[Icons]
Name: "{group}\Lumina Bridge"; Filename: "{localappdata}\Lumina\bin\lumina-bridge.cmd"
Name: "{group}\Lumina Studio"; Filename: "{localappdata}\Lumina\bin\lumina.cmd"; Parameters: "studio"
Name: "{group}\Lumina Doctor"; Filename: "{localappdata}\Lumina\bin\lumina.cmd"; Parameters: "doctor"

[Run]
Filename: "powershell.exe"; Parameters: "-NoProfile -ExecutionPolicy Bypass -File ""{tmp}\LuminaDesktopBetaR1\EthereonLabs\deploy\windows_desktop_r1\install_lumina_windows_bundled_r1.ps1"" -SourceRoot ""{tmp}\LuminaDesktopBetaR1\EthereonLabs"" -InstallRoot ""{localappdata}\Lumina"" -Force"; Flags: runhidden waituntilterminated
Filename: "{localappdata}\Lumina\bin\lumina-bridge.cmd"; Description: "Open Lumina Bridge"; Flags: nowait postinstall skipifsilent

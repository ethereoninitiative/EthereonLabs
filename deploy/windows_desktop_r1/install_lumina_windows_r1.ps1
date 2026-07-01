[CmdletBinding()]
param(
    [string]$SourceRoot = "",
    [string]$InstallRoot = "",
    [string]$PythonCommand = "python",
    [switch]$Force,
    [switch]$SkipShortcuts,
    [switch]$LaunchBridge
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

function Resolve-FullPath([string]$PathText) {
    return [System.IO.Path]::GetFullPath($PathText)
}

if (-not $SourceRoot) {
    $SourceRoot = Resolve-FullPath (Join-Path $PSScriptRoot "..\..")
}
if (-not $InstallRoot) {
    if (-not $env:LOCALAPPDATA) {
        throw "LOCALAPPDATA is unavailable. Supply -InstallRoot explicitly."
    }
    $InstallRoot = Join-Path $env:LOCALAPPDATA "Lumina"
}

$SourceRoot = Resolve-FullPath $SourceRoot
$InstallRoot = Resolve-FullPath $InstallRoot
$AppRoot = Join-Path $InstallRoot "app\EthereonLabs"
$StateParent = Join-Path $InstallRoot "state"
$StateRoot = Join-Path $StateParent "ship_of_ethereon_v2"
$CommandRoot = Join-Path $InstallRoot "bin"
$ReceiptRoot = Join-Path $InstallRoot "receipts"
$BootstrapRoot = Join-Path $AppRoot "LuminaOS\bootstrap\Ship_of_Ethereon_V2"

$SourceBootstrap = Join-Path $SourceRoot "LuminaOS\bootstrap\Ship_of_Ethereon_V2"
if (-not (Test-Path $SourceBootstrap -PathType Container)) {
    throw "SourceRoot does not contain the Ship of Ethereon V2 bootstrap: $SourceRoot"
}

$Python = Get-Command $PythonCommand -ErrorAction Stop
$PythonPath = $Python.Source
$PythonVersionText = & $PythonPath -c "import sys; print('.'.join(map(str, sys.version_info[:3])))"
if ($LASTEXITCODE -ne 0) {
    throw "Python could not be executed."
}
$PythonVersion = [Version]$PythonVersionText.Trim()
if ($PythonVersion -lt [Version]"3.11.0") {
    throw "Lumina Desktop Beta R1 requires Python 3.11 or newer. Found $PythonVersion."
}

New-Item -ItemType Directory -Force -Path $InstallRoot, $StateParent, $StateRoot, $CommandRoot, $ReceiptRoot | Out-Null

if ($Force -and (Test-Path $AppRoot)) {
    $stateLink = Join-Path $AppRoot ".lumina_state"
    if (Test-Path $stateLink) {
        Remove-Item $stateLink -Force
    }
    Remove-Item $AppRoot -Recurse -Force
}

if (-not (Test-Path $AppRoot)) {
    New-Item -ItemType Directory -Force -Path $AppRoot | Out-Null
}

$robocopyArgs = @(
    $SourceRoot,
    $AppRoot,
    "/E",
    "/NFL",
    "/NDL",
    "/NJH",
    "/NJS",
    "/NP",
    "/XD", ".git", ".lumina_state", "node_modules", "__pycache__",
    "/XF", "*.pyc"
)
& robocopy @robocopyArgs | Out-Null
if ($LASTEXITCODE -gt 7) {
    throw "Repository copy failed with robocopy exit code $LASTEXITCODE."
}

$RepoStateLink = Join-Path $AppRoot ".lumina_state"
if (Test-Path $RepoStateLink) {
    $item = Get-Item $RepoStateLink -Force
    if (-not ($item.Attributes -band [IO.FileAttributes]::ReparsePoint)) {
        throw "The installed repository already contains a non-link .lumina_state directory."
    }
    Remove-Item $RepoStateLink -Force
}

$junctionCommand = "mklink /J `"$RepoStateLink`" `"$StateParent`""
& cmd.exe /d /c $junctionCommand | Out-Null
if ($LASTEXITCODE -ne 0 -or -not (Test-Path $RepoStateLink)) {
    throw "Could not create the state-preserving directory junction."
}

$LuminaCmd = Join-Path $CommandRoot "lumina.cmd"
$BridgeCmd = Join-Path $CommandRoot "lumina-bridge.cmd"
$escapedPython = $PythonPath.Replace('%', '%%')
$escapedState = $StateRoot.Replace('%', '%%')
$escapedBootstrap = $BootstrapRoot.Replace('%', '%%')

@"
@echo off
setlocal
set "LUMINA_STATE_ROOT=$escapedState"
"$escapedPython" "$escapedBootstrap\bin\lumina" %*
exit /b %ERRORLEVEL%
"@ | Set-Content -Path $LuminaCmd -Encoding ASCII

@"
@echo off
setlocal
set "LUMINA_STATE_ROOT=$escapedState"
"$escapedPython" "$escapedBootstrap\bin\lumina-bridge" %*
exit /b %ERRORLEVEL%
"@ | Set-Content -Path $BridgeCmd -Encoding ASCII

$env:LUMINA_STATE_ROOT = $StateRoot
$DoctorPath = Join-Path $BootstrapRoot "install\lumina_doctor.py"
$DoctorJson = & $PythonPath $DoctorPath --ensure-state --json
if ($LASTEXITCODE -ne 0) {
    throw "Installed Lumina doctor did not pass."
}
$Doctor = $DoctorJson | ConvertFrom-Json
if (-not $Doctor.ok) {
    throw "Installed Lumina doctor returned ok=false."
}

if (-not $SkipShortcuts) {
    $StartMenuRoot = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs\Lumina"
    New-Item -ItemType Directory -Force -Path $StartMenuRoot | Out-Null
    $Shell = New-Object -ComObject WScript.Shell

    $BridgeShortcut = $Shell.CreateShortcut((Join-Path $StartMenuRoot "Lumina Bridge.lnk"))
    $BridgeShortcut.TargetPath = $BridgeCmd
    $BridgeShortcut.WorkingDirectory = $BootstrapRoot
    $BridgeShortcut.Description = "Open the read-only Lumina Bridge"
    $BridgeShortcut.Save()

    $StudioShortcut = $Shell.CreateShortcut((Join-Path $StartMenuRoot "Lumina Studio.lnk"))
    $StudioShortcut.TargetPath = $LuminaCmd
    $StudioShortcut.Arguments = "studio"
    $StudioShortcut.WorkingDirectory = $BootstrapRoot
    $StudioShortcut.Description = "Open Lumina Studio"
    $StudioShortcut.Save()
}

$Receipt = [ordered]@{
    schema_version = "lumina-windows-install-receipt-r1"
    installed_at = [DateTime]::UtcNow.ToString("o")
    source_root = $SourceRoot
    install_root = $InstallRoot
    app_root = $AppRoot
    bootstrap_root = $BootstrapRoot
    state_root = $StateRoot
    command_root = $CommandRoot
    python_executable = $PythonPath
    python_version = $PythonVersion.ToString()
    doctor_ok = [bool]$Doctor.ok
    shortcuts_created = -not [bool]$SkipShortcuts
    state_preserved_outside_application_tree = $true
    authority_boundary = "Installation prepares a host surface only; runtime governance remains authoritative."
}
$ReceiptPath = Join-Path $ReceiptRoot "windows_install_receipt_r1.json"
$Receipt | ConvertTo-Json -Depth 6 | Set-Content -Path $ReceiptPath -Encoding UTF8

Write-Host "Lumina Desktop Beta R1 host foundation installed."
Write-Host "  Application: $AppRoot"
Write-Host "  State:       $StateRoot"
Write-Host "  Commands:    $CommandRoot"
Write-Host "  Receipt:     $ReceiptPath"
Write-Host ""
Write-Host "Try:"
Write-Host "  $BridgeCmd"
Write-Host "  $LuminaCmd doctor"
Write-Host "  $LuminaCmd project create EthereonLabs --open"

if ($LaunchBridge) {
    Start-Process -FilePath $BridgeCmd -WorkingDirectory $BootstrapRoot
}

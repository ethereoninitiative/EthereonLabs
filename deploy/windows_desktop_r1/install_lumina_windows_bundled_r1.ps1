[CmdletBinding()]
param(
    [string]$SourceRoot = "",
    [string]$InstallRoot = "",
    [switch]$Force,
    [switch]$SkipShortcuts,
    [switch]$LaunchBridge
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

function Full-Path([string]$PathText) {
    return [System.IO.Path]::GetFullPath($PathText)
}

if (-not $SourceRoot) {
    $SourceRoot = Full-Path (Join-Path $PSScriptRoot "..\..")
}
if (-not $InstallRoot) {
    if (-not $env:LOCALAPPDATA) {
        throw "LOCALAPPDATA is unavailable. Supply -InstallRoot explicitly."
    }
    $InstallRoot = Join-Path $env:LOCALAPPDATA "Lumina"
}

$SourceRoot = Full-Path $SourceRoot
$InstallRoot = Full-Path $InstallRoot
$BundledRuntime = Join-Path $SourceRoot "deploy\windows_desktop_r1\runtime\python"
$InstalledRuntime = Join-Path $InstallRoot "runtime\python"
$BundledPython = Join-Path $BundledRuntime "python.exe"
$InstalledPython = Join-Path $InstalledRuntime "python.exe"
$BaseInstaller = Join-Path $SourceRoot "deploy\windows_desktop_r1\install_lumina_windows_r1.ps1"
$InstalledBootstrap = Join-Path $InstallRoot "app\EthereonLabs\LuminaOS\bootstrap\Ship_of_Ethereon_V2"

if (-not (Test-Path $BundledPython -PathType Leaf)) {
    throw "The release does not contain the bundled Python runtime."
}
if (-not (Test-Path $BaseInstaller -PathType Leaf)) {
    throw "The base Windows installer is missing."
}

if ($Force -and (Test-Path $InstalledRuntime)) {
    Remove-Item $InstalledRuntime -Recurse -Force
}
New-Item -ItemType Directory -Force -Path $InstalledRuntime | Out-Null

$copyArgs = @(
    $BundledRuntime,
    $InstalledRuntime,
    "/E",
    "/NFL",
    "/NDL",
    "/NJH",
    "/NJS",
    "/NP"
)
& robocopy @copyArgs | Out-Null
if ($LASTEXITCODE -gt 7) {
    throw "Bundled runtime copy failed with robocopy exit code $LASTEXITCODE."
}
if (-not (Test-Path $InstalledPython -PathType Leaf)) {
    throw "Installed bundled Python executable is missing."
}

$PthPath = Get-ChildItem -Path $InstalledRuntime -Filter "python*._pth" | Select-Object -First 1
if (-not $PthPath) {
    throw "Installed bundled Python path configuration is missing."
}
$PythonZip = Get-ChildItem -Path $InstalledRuntime -Filter "python*.zip" | Select-Object -First 1
if (-not $PythonZip) {
    throw "Installed bundled Python standard-library archive is missing."
}

@"
$($PythonZip.Name)
.
$InstalledBootstrap
$(Join-Path $InstalledBootstrap "runtime")
$(Join-Path $InstalledBootstrap "install")
$(Join-Path $InstalledBootstrap "studio")
"@ | Set-Content -Path $PthPath.FullName -Encoding ASCII

$installerParams = @{
    SourceRoot = $SourceRoot
    InstallRoot = $InstallRoot
    PythonCommand = $InstalledPython
    Force = [bool]$Force
    SkipShortcuts = [bool]$SkipShortcuts
    LaunchBridge = [bool]$LaunchBridge
}

& $BaseInstaller @installerParams
if ($LASTEXITCODE -ne 0) {
    throw "Lumina base installation failed."
}

$ReceiptPath = Join-Path $InstallRoot "receipts\windows_install_receipt_r1.json"
$Receipt = Get-Content $ReceiptPath -Raw | ConvertFrom-Json
$Receipt | Add-Member -NotePropertyName python_source -NotePropertyValue "bundled" -Force
$Receipt | Add-Member -NotePropertyName python_bundled -NotePropertyValue $true -Force
$Receipt | Add-Member -NotePropertyName bundled_runtime_root -NotePropertyValue $InstalledRuntime -Force
$Receipt | ConvertTo-Json -Depth 8 | Set-Content -Path $ReceiptPath -Encoding UTF8

Write-Host "Bundled Lumina runtime installed at: $InstalledRuntime"

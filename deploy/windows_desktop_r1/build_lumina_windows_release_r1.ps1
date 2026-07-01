[CmdletBinding()]
param(
    [string]$SourceRoot = "",
    [string]$OutputRoot = "",
    [string]$RuntimeZip = ""
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

function Full-Path([string]$PathText) {
    return [System.IO.Path]::GetFullPath($PathText)
}

if (-not $SourceRoot) {
    $SourceRoot = Full-Path (Join-Path $PSScriptRoot "..\..")
}
if (-not $OutputRoot) {
    $OutputRoot = Join-Path $SourceRoot "dist\windows_desktop_r1"
}

$SourceRoot = Full-Path $SourceRoot
$OutputRoot = Full-Path $OutputRoot
$RegistryPath = Join-Path $SourceRoot "deploy\windows_desktop_r1\python_runtime_source_r1.json"
$Registry = Get-Content $RegistryPath -Raw | ConvertFrom-Json

$WorkRoot = Join-Path $OutputRoot "work"
$StageRoot = Join-Path $WorkRoot "LuminaDesktopBetaR1"
$StageRepo = Join-Path $StageRoot "EthereonLabs"
$RuntimeRoot = Join-Path $StageRepo "deploy\windows_desktop_r1\runtime\python"
$ArchivePath = Join-Path $OutputRoot "LuminaDesktopBetaR1-windows-x64.zip"
$ReceiptPath = Join-Path $OutputRoot "LuminaDesktopBetaR1-windows-x64-receipt.json"

if (Test-Path $WorkRoot) {
    Remove-Item $WorkRoot -Recurse -Force
}
New-Item -ItemType Directory -Force -Path $StageRepo, $RuntimeRoot, $OutputRoot | Out-Null

$copyArgs = @(
    $SourceRoot,
    $StageRepo,
    "/E",
    "/NFL",
    "/NDL",
    "/NJH",
    "/NJS",
    "/NP",
    "/XD", ".git", ".lumina_state", "node_modules", "__pycache__", "dist",
    "/XF", "*.pyc"
)
& robocopy @copyArgs | Out-Null
if ($LASTEXITCODE -gt 7) {
    throw "Release staging copy failed with robocopy exit code $LASTEXITCODE."
}

if (-not $RuntimeZip) {
    $RuntimeZip = Join-Path $WorkRoot ([System.IO.Path]::GetFileName([string]$Registry.url))
    Invoke-WebRequest -Uri ([string]$Registry.url) -OutFile $RuntimeZip
}
$RuntimeZip = Full-Path $RuntimeZip

$RuntimeHash = (Get-FileHash -Path $RuntimeZip -Algorithm SHA256).Hash.ToLowerInvariant()
if ($RuntimeHash -ne ([string]$Registry.sha256).ToLowerInvariant()) {
    throw "Embedded Python SHA-256 mismatch."
}

Expand-Archive -Path $RuntimeZip -DestinationPath $RuntimeRoot -Force
$PthPath = Get-ChildItem -Path $RuntimeRoot -Filter "python*._pth" | Select-Object -First 1
if (-not $PthPath) {
    throw "Embedded Python path configuration file was not found."
}

@"
python313.zip
.
..\..\app\EthereonLabs\LuminaOS\bootstrap\Ship_of_Ethereon_V2
..\..\app\EthereonLabs\LuminaOS\bootstrap\Ship_of_Ethereon_V2\runtime
..\..\app\EthereonLabs\LuminaOS\bootstrap\Ship_of_Ethereon_V2\install
..\..\app\EthereonLabs\LuminaOS\bootstrap\Ship_of_Ethereon_V2\studio
"@ | Set-Content -Path $PthPath.FullName -Encoding ASCII

$EmbeddedPython = Join-Path $RuntimeRoot "python.exe"
$RuntimeVersion = (& $EmbeddedPython -c "import sys; print('.'.join(map(str, sys.version_info[:3])))").Trim()
if ($LASTEXITCODE -ne 0) {
    throw "Embedded Python did not execute from the staged release."
}

if (Test-Path $ArchivePath) {
    Remove-Item $ArchivePath -Force
}
Compress-Archive -Path $StageRoot -DestinationPath $ArchivePath -CompressionLevel Optimal
$ArchiveHash = (Get-FileHash -Path $ArchivePath -Algorithm SHA256).Hash.ToLowerInvariant()

$Commit = "unknown"
try {
    $Commit = (& git -C $SourceRoot rev-parse HEAD).Trim()
} catch {
    $Commit = "unknown"
}

$Receipt = [ordered]@{
    schema_version = "lumina-windows-release-receipt-r1"
    built_at = [DateTime]::UtcNow.ToString("o")
    source_commit = $Commit
    archive_name = [System.IO.Path]::GetFileName($ArchivePath)
    archive_sha256 = $ArchiveHash
    runtime_vendor = [string]$Registry.vendor
    runtime_version = $RuntimeVersion
    runtime_distribution = [string]$Registry.distribution
    runtime_source_sha256 = $RuntimeHash
    bundles_python = $true
    requires_system_python = $false
    embedded_runtime_layout = "windows-user-local"
    authority_boundary = "Release packaging supplies a host runtime and application archive only; Lumina governance remains authoritative."
}
$Receipt | ConvertTo-Json -Depth 5 | Set-Content -Path $ReceiptPath -Encoding UTF8

Write-Host "Lumina Windows release archive built."
Write-Host "  Archive: $ArchivePath"
Write-Host "  SHA-256: $ArchiveHash"
Write-Host "  Runtime: Python $RuntimeVersion embedded"
Write-Host "  Receipt: $ReceiptPath"

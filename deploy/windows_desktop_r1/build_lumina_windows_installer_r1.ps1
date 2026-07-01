[CmdletBinding()]
param(
    [string]$SourceRoot = "",
    [string]$OutputRoot = "",
    [string]$IsccPath = ""
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
    $OutputRoot = Join-Path $SourceRoot "dist\windows_installer_r1"
}

$SourceRoot = Full-Path $SourceRoot
$OutputRoot = Full-Path $OutputRoot
New-Item -ItemType Directory -Force -Path $OutputRoot | Out-Null

$ReleaseBuilder = Join-Path $SourceRoot "deploy\windows_desktop_r1\build_lumina_windows_release_r1.ps1"
& $ReleaseBuilder -SourceRoot $SourceRoot -OutputRoot $OutputRoot
if ($LASTEXITCODE -ne 0) {
    throw "The Windows release payload could not be built."
}

$PayloadRoot = Join-Path $OutputRoot "work\LuminaDesktopBetaR1"
if (-not (Test-Path (Join-Path $PayloadRoot "EthereonLabs") -PathType Container)) {
    throw "The staged Lumina release payload is missing."
}

if (-not $IsccPath) {
    $Candidates = @(
        (Join-Path ${env:ProgramFiles(x86)} "Inno Setup 6\ISCC.exe"),
        (Join-Path $env:ProgramFiles "Inno Setup 6\ISCC.exe"),
        (Join-Path ${env:ProgramFiles(x86)} "Inno Setup 7\ISCC.exe"),
        (Join-Path $env:ProgramFiles "Inno Setup 7\ISCC.exe")
    )
    $IsccPath = $Candidates | Where-Object { $_ -and (Test-Path $_ -PathType Leaf) } | Select-Object -First 1
}
if (-not $IsccPath -or -not (Test-Path $IsccPath -PathType Leaf)) {
    throw "Inno Setup command-line compiler was not found. Supply -IsccPath."
}

$Definition = Join-Path $SourceRoot "deploy\windows_desktop_r1\LuminaDesktopBetaR1.iss"
& $IsccPath "/DPayloadRoot=$PayloadRoot" "/DOutputRoot=$OutputRoot" $Definition
if ($LASTEXITCODE -ne 0) {
    throw "The Lumina graphical installer could not be compiled."
}

$InstallerPath = Join-Path $OutputRoot "LuminaDesktopBetaR1-Setup.exe"
if (-not (Test-Path $InstallerPath -PathType Leaf)) {
    throw "The compiled Lumina installer is missing."
}
$InstallerHash = (Get-FileHash -Path $InstallerPath -Algorithm SHA256).Hash.ToLowerInvariant()
$InstallerSize = (Get-Item $InstallerPath).Length

$Commit = "unknown"
try {
    $Commit = (& git -C $SourceRoot rev-parse HEAD).Trim()
} catch {
    $Commit = "unknown"
}

$Receipt = [ordered]@{
    schema_version = "lumina-windows-installer-build-receipt-r1"
    built_at = [DateTime]::UtcNow.ToString("o")
    source_commit = $Commit
    installer_name = [System.IO.Path]::GetFileName($InstallerPath)
    installer_sha256 = $InstallerHash
    installer_size_bytes = $InstallerSize
    installer_framework = "Inno Setup"
    bundles_python = $true
    requires_system_python = $false
    current_user_install = $true
    signed = $false
    state_preserved_on_upgrade = $true
    state_preserved_on_uninstall = $true
    authority_boundary = "The graphical installer places and launches Lumina; it does not alter runtime governance, canon, or continuity truth."
}
$ReceiptPath = Join-Path $OutputRoot "LuminaDesktopBetaR1-Setup-receipt.json"
$Receipt | ConvertTo-Json -Depth 5 | Set-Content -Path $ReceiptPath -Encoding UTF8

Write-Host "Lumina graphical installer built."
Write-Host "  Installer: $InstallerPath"
Write-Host "  SHA-256:   $InstallerHash"
Write-Host "  Receipt:   $ReceiptPath"

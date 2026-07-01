# Lumina Windows Graphical Installer R1

**Status:** unsigned developer preview  
**Target:** Windows 11 current-user installation

Graphical Installer R1 turns the receipted Windows release payload into:

```text
LuminaDesktopBetaR1-Setup.exe
LuminaDesktopBetaR1-Setup-receipt.json
```

The setup executable installs Lumina, its pinned Python runtime, command launchers, and Start Menu entries without requiring repository knowledge or a separately installed Python interpreter.

## Start Menu surfaces

- Lumina Bridge
- Lumina Studio
- Lumina Doctor

## State preservation

Application files, runtime files, and launchers are replaceable. Continuity state remains beneath:

```text
%LOCALAPPDATA%\Lumina\state\ship_of_ethereon_v2
```

Upgrade preserves state. Default removal deletes application machinery while retaining state.

## Build

```powershell
.\deploy\windows_desktop_r1\build_lumina_windows_installer_r1.ps1
```

The builder creates the bundled-runtime release payload, compiles the setup executable with Inno Setup, and emits a SHA-256 receipt.

## Sea trial

`.github/workflows/lumina-windows-installer-r1.yml` proves:

```text
build
  -> install
  -> doctor
  -> project and session creation
  -> Bridge resolution
  -> continuity marker
  -> upgrade
  -> continuity return
  -> removal
  -> state preservation
  -> receipt verification
```

## Signing boundary

R1 is unsigned and makes no production trust claim. Publisher code signing remains a separate release-governance threshold.

## Authority boundary

The installer owns desktop placement, launchers, upgrade, and removal behavior. It does not own runtime governance, mode legality, canon promotion, identity declaration, or primary continuity truth.

> The door may become simple without making the vessel simplistic.

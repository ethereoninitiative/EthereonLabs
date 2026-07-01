# Lumina Desktop Beta R1 — Windows Host Foundation

**Status:** developer preview  
**Target:** Windows 11 current-user host  
**Purpose:** establish the first continuously tested Windows installation lane

## Success threshold

The full desktop threshold is:

> Spence downloads one installer, opens Lumina from the Start Menu, completes a governed cycle, reboots, returns to the same project and continuity state, and updates without losing state.

R1 does not yet satisfy that full threshold. It establishes the tested host contract beneath it.

## R1 contents

R1 provides:

- a Windows host contract registry
- a current-user PowerShell installation scaffold
- an application tree under `%LOCALAPPDATA%\Lumina\app\EthereonLabs`
- persistent state under `%LOCALAPPDATA%\Lumina\state\ship_of_ethereon_v2`
- command launchers under `%LOCALAPPDATA%\Lumina\bin`
- optional Start Menu shortcuts for Bridge and Studio
- an installation receipt
- a Windows GitHub Actions gate
- a reinstall trial proving state survives application replacement

## Current prerequisites

R1 still requires Python 3.11 or newer, PowerShell, and an extracted or cloned EthereonLabs repository. Python is not yet bundled, and the installation scaffold is not yet a signed graphical installer.

## Install from a repository checkout

From PowerShell at the repository root:

```powershell
.\deploy\windows_desktop_r1\install_lumina_windows_r1.ps1
```

For a clean replacement of application files while preserving state:

```powershell
.\deploy\windows_desktop_r1\install_lumina_windows_r1.ps1 -Force
```

For a temporary test location:

```powershell
.\deploy\windows_desktop_r1\install_lumina_windows_r1.ps1 `
  -InstallRoot "$env:TEMP\LuminaDesktopBetaR1" `
  -SkipShortcuts `
  -Force
```

## Installed shape

```text
%LOCALAPPDATA%\Lumina\
  app\EthereonLabs\
    LuminaOS\bootstrap\Ship_of_Ethereon_V2\
    .lumina_state -> junction to the persistent state parent
  bin\
    lumina.cmd
    lumina-bridge.cmd
  state\
    ship_of_ethereon_v2\
  receipts\
    windows_install_receipt_r1.json
```

The application tree can be replaced without deleting the state tree. The repository-local state path inside the installed application is a directory junction to the external persistent state parent so older and newer path consumers converge on the same state.

## First use

```powershell
& "$env:LOCALAPPDATA\Lumina\bin\lumina.cmd" doctor
& "$env:LOCALAPPDATA\Lumina\bin\lumina.cmd" project create EthereonLabs --open
& "$env:LOCALAPPDATA\Lumina\bin\lumina.cmd" session create "Initial Harbor session" --open
& "$env:LOCALAPPDATA\Lumina\bin\lumina-bridge.cmd"
```

## State contract

`runtime/repo_paths_r1.py` recognizes:

1. `LUMINA_STATE_ROOT` when explicitly supplied
2. Windows user-local application data on Windows
3. the historical repository-local state directory for POSIX development

The Windows launchers explicitly set `LUMINA_STATE_ROOT` to the installed persistent state root.

This is host-location policy only. It does not establish continuity truth, identity, governance authority, or canon authority.

## Continuous sea trial

The workflow `.github/workflows/lumina-windows-host-r1.yml` runs on a Windows host and proves:

- installation succeeds without administrator privileges
- the installed doctor passes
- project and Harbor-session creation work through installed launchers
- Bridge launcher resolution works
- a continuity marker survives forced application replacement
- active project and session markers survive replacement
- the state path is external to the application tree
- the repository state path is a junction
- an installation receipt is emitted

## Remaining technical work

The desktop lane still needs bundled Python and dependencies, a signed graphical installer, production icons and file metadata, desktop supervision, first-run recovery, backup and restore, a verified uninstall path, release versioning, update channels, and clean physical-PC receipts.

## Authority boundary

Windows packaging owns host preparation, application placement, launchers, and installation receipts. It does not own runtime governance, mode legality, capability authority, canon promotion, identity declaration, or primary continuity truth.

## Guiding sentence

> Replace the machinery without losing the voyage.

# Lumina Windows Graphical Installer R1

**Status:** unsigned developer preview  
**Target:** Windows 11 current-user installation  
**Installer framework:** Inno Setup

## Purpose

Graphical Installer R1 crosses the first literal double-click threshold.

It produces:

```text
LuminaDesktopBetaR1-Setup.exe
LuminaDesktopBetaR1-Setup-receipt.json
LuminaDesktopBetaR1-Setup-lifecycle-receipt.json
```

The setup executable installs Lumina, the pinned embedded Python runtime, command launchers, and Start Menu entries without requiring repository knowledge or a separate Python installation.

## Installed surfaces

The installer creates Start Menu entries for Lumina Bridge, Lumina Studio, and Lumina Doctor. An interactive installation offers to open the read-only Bridge after setup.

## State preservation

Replaceable application machinery lives beneath:

```text
%LOCALAPPDATA%\Lumina\app
%LOCALAPPDATA%\Lumina\runtime
%LOCALAPPDATA%\Lumina\bin
```

Continuity state lives beneath:

```text
%LOCALAPPDATA%\Lumina\state\ship_of_ethereon_v2
```

The hosted sea trial proves that an in-place upgrade preserves the continuity marker, active project, and Harbor session.

The hosted lifecycle sea trial also runs the generated Inno Setup uninstaller, proves the expected app/runtime/bin launch machinery is removed or no longer active, and proves the continuity marker remains under the state tree after normal application removal.

The build receipt remains a build receipt and keeps `uninstall_validated: false`. The lifecycle receipt is the artifact that may record `install_validated`, `upgrade_validated`, `uninstall_validated`, `state_preserved_on_upgrade`, and `state_preserved_on_uninstall` after the verifier proves those fields in hosted Windows CI.

A directory junction preserves compatibility with components that still resolve the historical repository-local `.lumina_state` path.

## Build

```powershell
$Output = "$env:TEMP\lumina-installer"
.\deploy\windows_desktop_r1\build_lumina_windows_release_r1.ps1 `
  -SourceRoot $pwd `
  -OutputRoot $Output

python .\deploy\windows_desktop_r1\build_lumina_windows_installer_r1.py `
  --source-root $pwd `
  --payload-root "$Output\work\LuminaDesktopBetaR1" `
  --output-root $Output `
  --iscc "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
```

## Continuous sea trial

`.github/workflows/lumina-windows-installer-r1.yml` proves:

```text
build bundled release payload
  -> compile setup executable
  -> install silently
  -> run Doctor
  -> create project and Harbor session
  -> resolve Bridge
  -> write continuity marker
  -> upgrade in place
  -> prove project, session, and marker return
  -> verify setup SHA-256 receipt
  -> uninstall with the generated Inno Setup uninstaller
  -> prove app/runtime/bin launch machinery is removed or inactive
  -> prove the continuity marker remains after uninstall
  -> emit lifecycle receipt
```

The successful setup executable, build receipt, and lifecycle receipt are uploaded as temporary workflow artifacts.

## Signing boundary

R1 is intentionally recorded as unsigned. It must not claim production publisher trust or a frictionless SmartScreen experience.

Code signing requires a separate publisher identity and signing credential decision. The build system may verify that signing is absent, but it may not fabricate trust.

## Authority boundary

The installer owns desktop file placement, launchers, upgrade behavior, removal behavior, and packaging/lifecycle receipts.

It does not own runtime governance, mode legality, capability authority, canon promotion, identity declaration, or primary continuity truth.

## Next threshold

The next technical gates are first-run configuration, repair, backup and restore, release signing, and a clean physical-PC lifecycle receipt.

> The door may become simple without making the vessel simplistic.

# Lumina Windows Bundled Runtime R1

**Status:** developer preview  
**Purpose:** remove the requirement that a Windows user install Python separately

## Release shape

The release builder produces:

```text
LuminaDesktopBetaR1-windows-x64.zip
LuminaDesktopBetaR1-windows-x64-receipt.json
```

The archive contains an EthereonLabs application tree with a pinned official Python Windows embeddable runtime under:

```text
deploy/windows_desktop_r1/runtime/python/
```

The bundled installer copies that runtime to the persistent host location:

```text
%LOCALAPPDATA%\Lumina\runtime\python\
```

The installed Lumina launchers use that interpreter directly. A system Python installation is not required for the bundled release path.

## Runtime source

The exact interpreter source, version, architecture, URL, and SHA-256 value are recorded in:

```text
deploy/windows_desktop_r1/python_runtime_source_r1.json
```

The release builder refuses to continue when the downloaded archive does not match the pinned SHA-256 value.

## Build

From PowerShell at the repository root:

```powershell
.\deploy\windows_desktop_r1\build_lumina_windows_release_r1.ps1
```

The default output directory is:

```text
dist/windows_desktop_r1/
```

## Install from the release archive

After extracting the release archive, run:

```powershell
.\EthereonLabs\deploy\windows_desktop_r1\install_lumina_windows_bundled_r1.ps1
```

The bundled installer places the runtime, invokes the existing user-local host installer, and amends the installation receipt with:

```text
python_source: bundled
python_bundled: true
bundled_runtime_root: <installed runtime path>
```

## Release receipt

The release receipt records:

- source commit
- archive filename
- archive SHA-256
- Python vendor and version
- embedded source archive SHA-256
- whether system Python is required
- the packaging authority boundary

## Continuous validation

`.github/workflows/lumina-windows-release-r1.yml` builds the archive on a Windows runner, extracts it, installs through the bundled-runtime path, runs the installed doctor, creates a project and Harbor session, resolves Bridge, and checks the release receipt against the archive bytes.

## Boundary

The bundled interpreter is execution substrate. It does not alter Lumina runtime governance, capability authority, canon promotion, identity declarations, or primary continuity truth.

## Next threshold

The next technical threshold is a single signed graphical installer that consumes this verified release payload without requiring repository or PowerShell knowledge.

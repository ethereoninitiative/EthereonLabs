# Start Here — Lumina Desktop Beta

**Current status:** Windows host foundation plus bundled-runtime release R1, developer preview

This lane turns the governed Lumina repository into a machine-resident desktop product.

## Current entry points

Read:

- `docs/LUMINA_DESKTOP_BETA_R1_WINDOWS_HOST_FOUNDATION.md`
- `docs/LUMINA_WINDOWS_BUNDLED_RUNTIME_R1.md`
- `deploy/windows_desktop_r1/windows_host_contract_r1.json`
- `deploy/windows_desktop_r1/python_runtime_source_r1.json`
- `.github/workflows/lumina-windows-host-r1.yml`
- `.github/workflows/lumina-windows-release-r1.yml`

The repository-checkout installer remains:

```text
deploy/windows_desktop_r1/install_lumina_windows_r1.ps1
```

The release path is:

```text
deploy/windows_desktop_r1/build_lumina_windows_release_r1.ps1
  -> LuminaDesktopBetaR1-windows-x64.zip
  -> install_lumina_windows_bundled_r1.ps1
```

## Present truth

The runtime, Bridge, Studio, receipts, governance boundaries, and continuity substrate already exist. The desktop lane owns the technical productization work required to make those surfaces installable and maintainable on a personal computer.

The current Windows lane provides:

```text
platform-aware state location
  -> user-local application copy
  -> persistent state outside the replaceable app tree
  -> installed command launchers
  -> optional desktop menu entries
  -> installation receipt
  -> Windows CI reinstall trial
  -> pinned official embedded Python runtime
  -> hashed Windows release archive
  -> bundled-runtime installation trial
```

A Windows user no longer needs to install Python separately when using the bundled release archive.

It is not yet a signed graphical installer.

## Completion threshold

The desktop technical lane is complete when a non-developer can:

```text
download one installer
  -> install without repository knowledge
  -> launch Bridge and Studio from the operating system
  -> create and return to a project
  -> reboot without losing continuity state
  -> update without losing continuity state
  -> repair or remove the application safely
```

## Work order

The current productization order is:

1. Windows host foundation and persistent state separation — complete R1
2. bundled runtime and release archive — active R1
3. graphical installer and signed launchers
4. first-run setup and recovery
5. update, repair, backup, and removal
6. clean physical-PC release receipts

## Boundary

Desktop packaging owns host preparation, dependencies, launchers, updates, and install receipts. It does not own runtime governance, canon promotion, mode legality, identity declarations, or primary continuity truth.

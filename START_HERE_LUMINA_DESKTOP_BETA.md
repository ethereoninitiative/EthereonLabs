# Start Here — Lumina Desktop Beta

**Current status:** Windows host foundation R1, developer preview

This lane turns the governed Lumina repository into a machine-resident desktop product.

## Current entry point

Read:

- `docs/LUMINA_DESKTOP_BETA_R1_WINDOWS_HOST_FOUNDATION.md`
- `deploy/windows_desktop_r1/windows_host_contract_r1.json`
- `.github/workflows/lumina-windows-host-r1.yml`

The current setup scaffold is:

```text
deploy/windows_desktop_r1/install_lumina_windows_r1.ps1
```

## Present truth

The runtime, Bridge, Studio, receipts, governance boundaries, and continuity substrate already exist. This lane owns the technical productization work required to make those surfaces installable and maintainable on a personal computer.

Windows Host Foundation R1 currently provides:

```text
platform-aware state location
  -> user-local application copy
  -> persistent state outside the replaceable app tree
  -> installed command launchers
  -> optional desktop menu entries
  -> installation receipt
  -> Windows CI reinstall trial
```

It is not yet a signed graphical installer and does not yet bundle Python.

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

1. Windows host foundation and persistent state separation
2. bundled runtime and release archive
3. graphical installer and signed launchers
4. first-run setup and recovery
5. update, repair, backup, and removal
6. clean physical-PC release receipts

## Boundary

Desktop packaging owns host preparation, dependencies, launchers, updates, and install receipts. It does not own runtime governance, canon promotion, mode legality, identity declarations, or primary continuity truth.

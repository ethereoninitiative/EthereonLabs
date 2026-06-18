# Lumina Package / Install R1

**Project:** Lumina OS / Ship of Ethereon V2 Bootstrap  
**Mode:** DryDock  
**Status:** Package-readiness planning artifact  
**Date:** June 18, 2026

---

## 1. Purpose

Lumina OS now has meaningful governed substrate, host-layer vocabulary, Studio entrypoints, receipts, governance history, canon lineage, input integrity, and capability routing.

The next threshold is not more conceptual architecture.

The next threshold is deliverability.

This artifact defines the first package/install hardening lane needed to move Lumina from repo-native local runtime scaffold toward a developer beta that can be installed, checked, run, inspected, and updated with low operator friction.

---

## 2. Diagnosis

Lumina currently starts from a repo-aware local path and already exposes a system-like vocabulary:

```bash
lumina doctor
lumina run
lumina observe
lumina state
lumina studio
```

That is enough to prove the host shape.

It is not yet enough to call Lumina a deliverable package.

The current gap is productization: dependency locking, install paths, state schema validation, update behavior, release checks, and operator-facing polish.

---

## 3. R1 Build Target

R1 should produce a developer-beta package path where a technically comfortable operator can clone the repo and complete this loop without hunting through internals:

```bash
git clone <repo>
cd EthereonLabs/LuminaOS/bootstrap/Ship_of_Ethereon_V2
python install/lumina_doctor.py
bash install/install_lumina.sh
lumina doctor
lumina run "Review Lumina OS progress and produce the next governed action receipt."
lumina state --limit 12
```

R1 does not need to solve consumer-grade desktop installation.

R1 does need to make the current local installation honest, repeatable, and checkable.

---

## 4. Scope

### Add or harden

- dependency inventory for host, runtime, Studio, and probe paths
- dependency lock or pinned requirements file
- `lumina doctor` checks for Python version, import readiness, writable state path, and required files
- install script idempotence checks
- uninstall/reset note for local symlink installation
- state directory schema note
- minimum migration/version marker for `.lumina_state`
- release-readiness checklist for package/install work
- sea-trial or doctor-mode verification for install readiness

### Update

- host-layer docs with package/install R1 reference
- local runbook with first-run and recovery steps
- Studio docs if package assumptions affect command paths

---

## 5. Non-goals

R1 must not pretend to be more complete than it is.

Do not include:

- consumer-grade Mac `.app` packaging
- Windows installer
- Linux distro packages
- auto-update daemon
- public network deployment
- background observer service promotion beyond skeleton status
- authentication system implementation
- Chamber queue execution integration
- new governance law
- new canon promotion rules

Those belong to later lanes.

---

## 6. Authority Boundaries

The package/install layer may:

- check local readiness
- install or remove local command shims
- validate dependency availability
- validate state path readiness
- invoke existing governed runtime commands
- surface clear operator errors

The package/install layer may not:

- bypass `ModeGuard`
- authorize mutation or promotion
- write canon lineage directly
- reinterpret ambiguous user intent
- treat symbolic overlays as required dependencies
- make Studio a governance authority
- make Chamber an execution authority

Runtime law remains in the Lumina substrate.

Install law is operational convenience, not governance law.

---

## 7. Acceptance Criteria

R1 passes only if:

1. `python install/lumina_doctor.py` reports dependency and path readiness clearly.
2. `bash install/install_lumina.sh` can be run repeatedly without damaging an existing install.
3. `lumina doctor` succeeds after installation.
4. `lumina run "..."` emits a governed receipt.
5. `lumina state --limit 12` can read recent receipts or reports a clear no-state-yet message.
6. Missing dependencies produce actionable messages rather than tracebacks.
7. The state directory has a documented schema/version marker.
8. Package/install docs explain first run, re-run, reset, and known limitations.
9. No package/install code bypasses runtime governance.
10. R1 docs clearly distinguish developer beta from public beta.

---

## 8. Follow-on Lanes

After R1, the larger deliverability arc should proceed in this order:

1. Package / Install R1 — developer-beta local install path
2. State Schema / Migration R1 — versioned state and compatibility checks
3. Studio UX R2 — better state browser, governance viewer, presets, and receipt comparison
4. Security / Auth R1 — local and remote exposure boundaries before any network use
5. Observer Service R1 — promote skeleton service only after install and state assumptions are stable
6. Chamber Execution Bridge R1 — accepted queue item to governed runtime execution receipt
7. Release Automation R1 — tagged releases, CI checks, changelog, release artifact notes
8. Public Beta Package R1 — consumer-grade installation and launch path

---

## 9. Guiding Sentence

Make Lumina installable before making Lumina larger.

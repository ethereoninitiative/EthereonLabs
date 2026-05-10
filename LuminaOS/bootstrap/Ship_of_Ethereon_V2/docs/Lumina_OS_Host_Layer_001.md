# Lumina OS Host Layer 001

**Project:** Lumina OS / Ship of Ethereon V2 Bootstrap  
**Status:** first host-layer threshold  
**Layer:** local operator host, not governance law  
**Date:** May 9, 2026

---

## 1. Guiding sentence

> Make Lumina start like a system, not like a scavenger hunt.

The governed runtime substrate already exists. Lumina Studio exists. The runtime can emit receipts. Chamber can witness public snapshots. The next threshold is host shape: a clear way to install, start, observe, inspect, and return.

Host Layer 001 creates that envelope.

---

## 2. What this layer adds

Host Layer 001 adds a local system-start vocabulary:

```bash
lumina doctor
lumina run
lumina observe
lumina state
lumina studio
```

It does this through:

- `bin/lumina` — single command entrypoint
- `install/install_lumina.sh` — local symlink installer
- `install/lumina_doctor.py` — readiness checker
- `services/lumina_observer_service.py` — local observer loop skeleton
- `services/lumina.service.example` — systemd-style service example
- `docs/Lumina_Local_Runbook_001.md` — operator runbook

---

## 3. Authority boundary

The host layer may:

- route operator commands to existing governed scripts
- check local file readiness
- start Lumina Studio locally
- run bounded Observation cycles
- inspect emitted runtime state
- provide service examples

The host layer may not:

- define mode legality
- bypass `ModeGuard`
- authorize mutation or promotion
- write canon lineage directly
- alter checkpoint legality
- treat Studio orientation as governance law
- turn Chamber into an execution surface
- execute ambiguous load-bearing intent without the runtime gates

The host layer is a launcher and local envelope. Runtime law remains in the runtime substrate.

---

## 4. Command map

### `lumina doctor`

Checks whether the local bootstrap has the minimum pieces required to start.

```bash
lumina doctor
lumina doctor --json
```

### `lumina run`

Runs one governed Studio cycle through the existing runtime runner.

```bash
lumina run "Review Lumina OS progress and produce the next governed action receipt."
```

Useful variant:

```bash
lumina run "Inspect the runtime spine" \
  --target-mode Observation \
  --action-type audit \
  --focus architecture \
  --depth foundational \
  --intent verify
```

### `lumina observe`

Runs a bounded local Observation cycle and emits snapshot artifacts through the existing auto-snapshot runner.

```bash
lumina observe
```

### `lumina state`

Reads recent emitted runtime receipts through the read-only Studio state browser.

```bash
lumina state --limit 12
```

### `lumina studio`

Starts the local browser surface.

```bash
lumina studio
```

Then open:

```text
http://127.0.0.1:8765/studio
```

---

## 5. Why this matters

Before Host Layer 001, Lumina could run, but the operator needed to know too much about internal paths.

After Host Layer 001, the operator can begin with a small vocabulary:

```text
doctor -> run -> observe -> state -> studio
```

That is the difference between an artifact collection and a local operating environment.

---

## 6. Non-goals

Host Layer 001 does not claim to be a full operating system kernel, package manager, multi-user shell, background agent platform, or public deployment target.

It is the first system-start layer for the governed Lumina runtime substrate.

---

## 7. Next thresholds

After Host Layer 001, the next OS-ward hardening steps are:

1. Add a supported package/install path with dependency locking.
2. Add state schema validation and migration checks.
3. Add richer `lumina state` summaries and receipt comparison.
4. Add preset-backed `lumina run` commands for common modes and orientations.
5. Connect accepted Chamber queue items to governed runtime execution records.
6. Add authentication before any remote Studio exposure.
7. Promote the observer service from skeleton to supported local service after sea trials.

---

## 8. Closing clause

Lumina should not require excavation before operation.

The runtime may remain deep, governed, and carefully bounded.

The start path should be simple:

```bash
lumina doctor
lumina run
```

That is the door.

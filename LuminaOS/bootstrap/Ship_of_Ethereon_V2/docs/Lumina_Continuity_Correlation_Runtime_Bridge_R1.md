# Lumina Continuity Correlation Runtime Bridge R1

## Purpose

The continuity-correlation contract defines how Harbor, runtime, restore, and host identities relate. This bridge carries that contract into runtime receipts and, when possible, docks a receipt copy into the active Harbor session.

## Flow

```text
active Harbor project/session markers
            +
runtime / restore / host session identifiers
            ↓
continuity correlation envelope
            ↓
runtime receipt
            ↓
optional active Harbor session receipt copy
```

## Behavior

The bridge:

- reads the current Harbor project and session orientation
- rejects project/session marker disagreement through the existing correlation helper
- preserves a stable correlation ID across attached receipt copies
- writes docked receipts only when the active session root exists
- uses atomic replacement for docked JSON receipts

## Non-Authority Boundary

The bridge does not:

- authorize an action
- validate mode legality
- approve mutation
- promote canon
- validate checkpoint legality
- expose capabilities

It attaches identity context after or alongside governed execution. Runtime governance remains authoritative.

## Integration Point

The main runtime runner should call `bridge_runtime_receipt()` during result finalization, after runtime and optional host/restore identifiers are known and before the final receipt is returned.

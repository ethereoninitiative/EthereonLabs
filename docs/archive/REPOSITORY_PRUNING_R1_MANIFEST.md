# Repository Pruning R1 Manifest

**Base:** `main` at `a8ad2c3d3fcd898b5a82aa03cf8358a7bdd0c6c3`  
**Purpose:** reduce present-tense ambiguity without erasing useful lineage.

## Retired compatibility surfaces

- `START_HERE_RUNTIME_PATH.md` now points to the current `bin/lumina` host path rather than teaching direct core-runner invocation as the ordinary entry.
- `docs/PUBLIC_SURFACE_REGISTRY.md` now points to `docs/ACTIVE_SURFACE_REGISTRY_R1.json` as the active machine-readable registry.

## Removed superseded copies

- `lumina-dashboard-restored.html` — unreferenced older dashboard ancestor; current surface is `lumina-dashboard.html`.
- `chamber-app/src/advisory_queue_server_v0_1.ts` — superseded by the v0.2 advisory server used by package scripts.
- `chamber-app/src/advisory_queue_memory_store.ts` — private v0.1 in-memory store used only by the superseded server.

## Archived lineage

The former `LuminaOS/runtime/daemon/` v0.1 experiment and its contract moved beneath:

- `docs/archive/runtime-history/lumina-daemon-v0_1/`

The archive retains the implementation, smoke test, README, and contract for historical comparison while removing the appearance of a parallel active runtime lane.

## Explicit non-cuts

This pass does not prune current V2 runtime, runtime-truth Studio, deployment lanes, Psi Class staging, research, philosophy, provenance, public route redirects, or validation gates merely because multiple versions or surfaces exist. Those require separate ownership evidence before pruning.

## Rule

No unique idea disappears merely because its implementation is obsolete. Active architecture remains active; historical architecture becomes clearly historical.

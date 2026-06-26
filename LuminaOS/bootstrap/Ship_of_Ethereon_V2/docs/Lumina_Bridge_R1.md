# Lumina Bridge R1

**Project:** Lumina OS / Ship of Ethereon V2  
**Layer:** local operator orientation surface  
**Status:** R1 read-only bridge  
**Date:** June 25, 2026

## Purpose

The bridge answers the operator's first navigational questions before a governed action is requested:

- Where is the active project?
- Which Harbor session is open?
- What did the latest runtime witness observe?
- Is public runtime truth aligned with that witness?
- What committed governance and canon evidence currently holds?
- Which doorway is appropriate next?

Bridge R1 makes those answers visible in one local surface without collapsing host orientation, ephemeral Observation state, and committed runtime authority into one kind of truth.

## Launch

From the Ship of Ethereon V2 bootstrap directory:

```bash
python bin/lumina-bridge
```

Default address:

```text
http://127.0.0.1:8766/bridge
```

Read-only JSON endpoint:

```text
/api/bridge
```

## Bridge Panels

Bridge R1 surfaces:

1. **Ship Position** — active project, Harbor session, current witnessed mode, latest action, and witness status.
2. **Continuity** — local continuity shape, receipt count, drift, recurrence, and listening notes when available.
3. **Committed Authority** — verified governance chain, canon head, promotion receipt, and post-promotion verification summaries.
4. **Runtime Witness** — the latest public Observation receipt and bounded Psi-42 instrument summary.
5. **Truth Alignment** — whether the public latest-cycle receipt and runtime-truth projection identify the same run and timestamp.
6. **Correlation References** — distinct project, Harbor-session, runtime-session, and context-bundle identifiers without pretending they are interchangeable.
7. **Navigation** — a recommended doorway and explicit local commands.

## Core Distinction

```text
Bridge orients.
Studio acts.
Runtime governs.
Receipts record.
Canon preserves promoted lineage.
```

Bridge R1 intentionally contains no mutating HTTP route. A POST request returns `405 Method Not Allowed` and directs the operator to Lumina Studio for explicit governed work.

## Authority Boundary

Bridge R1 may:

- read active project and Harbor-session markers
- read emitted local runtime receipts
- read the public latest-cycle witness
- read the reconciled public runtime-truth projection
- summarize committed governance and canon evidence
- display identifiers from distinct continuity layers
- recommend an explicit next doorway

Bridge R1 may not:

- create runtime law
- change mode legality
- mutate governance state
- authorize canon promotion
- expose capabilities
- infer identity equivalence between project, Harbor, restore, host, and runtime sessions
- execute a governed cycle automatically
- treat an empty local Observation ledger as authority over committed canon evidence

## Truth Ordering

The bridge preserves the current truth hierarchy:

1. committed governance and canon evidence
2. reconciled public runtime-truth projection
3. latest public Observation receipt
4. local runtime receipt summaries
5. host/workspace project and session markers
6. bridge presentation and recommendations

Presentation never outranks evidence.

## Relationship to Existing Surfaces

### Workspace Dashboard R1

The command-line dashboard remains the compact entrance and quick orientation summary.

### Lumina Bridge R1

The bridge is the richer local position surface. It joins the lanes visually and keeps their authority boundaries visible.

### Lumina Studio

Studio remains the explicit local control surface for requesting a governed runtime cycle.

### Chamber

Chamber remains the public-facing witness and experience lane. Bridge R1 is local and operator-facing.

## Validation

Run:

```bash
python sea_trials_lumina_bridge_r1.py
```

The trial verifies that:

- active project and Harbor session are surfaced
- latest-cycle and public-truth run identifiers align
- committed `canon-0001` remains visible even when observed local canon is empty
- correlation references remain distinct
- navigation points to Studio when project and session are present
- Bridge HTML contains no mutating form or POST action
- the authority boundary is present

## Guiding Sentence

> The bridge is where the ship becomes legible before it becomes steerable.

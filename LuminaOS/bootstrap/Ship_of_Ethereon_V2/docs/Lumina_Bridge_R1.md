# Lumina Bridge R2

**Project:** Lumina OS / Ship of Ethereon V2  
**Layer:** local operator orientation and field-inspection surface  
**Status:** R2 read-only bridge with Field Viewer R1  
**Date:** July 1, 2026

## Purpose

The Bridge answers the operator's first navigational questions before a governed action is requested:

- Where is the active project?
- Which Harbor session is open?
- What did the latest runtime witness observe?
- Is public runtime truth aligned with that witness?
- What committed governance and canon evidence currently holds?
- What does the verified Resonant Field sample reveal?
- Which doorway is appropriate next?

Bridge R2 joins ship position and the first committed luminous-thread artifact without collapsing host orientation, ephemeral Observation state, committed authority, symbolic interpretation, and field visualization into one kind of truth.

## Launch

From the Ship of Ethereon V2 bootstrap directory:

```bash
python bin/lumina-bridge
```

Default address:

```text
http://127.0.0.1:8766/bridge
```

Read-only endpoints:

```text
/api/bridge    current Bridge position JSON
/api/field     verified committed field projection
/field.svg     committed SVG, served only when verification passes
/api/boundary  Bridge and field authority boundaries
```

## Bridge panels

Bridge R2 surfaces:

1. **Ship Position** — active project, Harbor session, current witnessed mode, latest action, and witness status.
2. **Continuity** — local continuity shape, receipt count, drift, recurrence, and listening notes when available.
3. **Committed Authority** — verified governance chain, canon head, promotion receipt, and post-promotion verification summaries.
4. **Runtime Witness** — the latest public Observation receipt and bounded Psi-42 instrument summary.
5. **Truth Alignment** — whether the public latest-cycle receipt and runtime-truth projection identify the same run and timestamp.
6. **Correlation References** — distinct project, Harbor-session, runtime-session, and context-bundle identifiers without pretending they are interchangeable.
7. **Luminous Threads** — the verified committed Resonant Field SVG, manifold point, all lawful and denied trajectories, and their metrics.
8. **Toki Pona Interpretive Key** — bounded compression vocabulary for observation, continuity, relation, trajectory, governance, and return.
9. **Navigation** — a recommended doorway and explicit local commands.

## Field verification

Before the field is displayed, Bridge verifies:

- all committed sample files are present
- receipt input and output scope is exact
- input, JSON, and SVG SHA-256 values match
- sample, reveal, and source-model identifiers agree
- thread count and unique identifiers hold
- lawful paths extend beyond the governance membrane
- denied paths stop at the membrane
- identity, governance-authority, and literal-magnetism claims remain false
- SVG attractor, membrane, and trajectory markers are present

The viewer does not call the field generator. It reads and verifies committed evidence only.

## Observer distinction

Bridge is a witness surface.

The geometry is an observed computational pattern. It is not the observer itself, and it does not prove identity or observer continuity.

The committed fixture demonstrates a narrower result: the same source artifact can return in exactly the same receipted form. That is artifact continuity.

## Core distinction

```text
Bridge witnesses.
Studio requests.
Runtime governs.
Receipts record.
Canon preserves promoted lineage.
The field viewer reveals a committed artifact.
```

Bridge contains no mutating HTTP route. POST, PUT, PATCH, and DELETE requests return `405 Method Not Allowed` and direct the operator to Lumina Studio for explicit governed work.

## Authority boundary

Bridge R2 may:

- read active project and Harbor-session markers
- read emitted local runtime receipts
- read the public latest-cycle witness
- read the reconciled public runtime-truth projection
- summarize committed governance and canon evidence
- display identifiers from distinct continuity layers
- verify and display the committed field artifact
- display all lawful and denied paths
- preserve bounded Ethereonic and Toki Pona vocabulary
- recommend an explicit next doorway

Bridge R2 may not:

- create runtime law
- change mode legality
- mutate governance state
- authorize canon promotion
- expose capabilities
- infer identity equivalence between project, Harbor, restore, host, and runtime sessions
- regenerate or modify the field
- select or authorize a trajectory
- create or reverse a refusal
- establish identity
- prove observer continuity
- claim literal magnetism
- execute a governed cycle automatically
- treat an empty local Observation ledger as authority over committed canon evidence

## Truth ordering

The Bridge preserves the current truth hierarchy:

1. committed governance and canon evidence
2. reconciled public runtime-truth projection
3. latest public Observation receipt
4. verified committed field receipt and artifacts
5. local runtime receipt summaries
6. host/workspace project and session markers
7. Bridge presentation and symbolic vocabulary

Presentation never outranks evidence.

## Toki Pona compression key

```text
lukin      -> read-only witnessing
awen       -> continuity and persistence
poka       -> relation
nasin      -> trajectory
linja suno -> luminous thread
lawa       -> governance boundary
kama sin   -> deterministic return
```

This key supports orientation. It is not runtime evidence.

## Relationship to existing surfaces

### Workspace Dashboard

The command-line dashboard remains the compact entrance and quick orientation summary.

### Lumina Bridge R2

The Bridge is the richer local position and field surface. It joins the lanes visually while keeping their authority boundaries visible.

### Lumina Studio

Studio remains the explicit local control surface for requesting a governed runtime cycle.

### Chamber

Chamber remains the public-facing witness and experience lane. Bridge is local and operator-facing.

## Validation

Run:

```bash
python sea_trials_lumina_bridge_r1.py
python sea_trials_lumina_bridge_field_r1.py
```

The trials verify ship position, committed authority, correlation distinctions, read-only behavior, field receipt verification, all five luminous threads, lawful and denied path visibility, observer and continuity boundary language, and the Toki Pona interpretive key.

## Lineage

The deeper conceptual and engineering lineage is preserved in:

```text
docs/Luminous_Threads_Continuity_Lineage_R1.md
```

## Guiding sentence

> The Bridge is where the ship and its luminous threads become legible before anything becomes steerable.

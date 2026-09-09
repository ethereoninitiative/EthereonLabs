# Habitat Resonant Return Gate R1

**Status:** implemented standalone read-only JSON model; live Bridge integration remains future work

**Scope:** orientation from an explicitly supplied snapshot; not runtime authority

**Anchored from:** `main` at `e3dc37c48d5e1c15bd7d88bfe46f32f2819c6198`  
**Implementation base:** `main` at `a944180f82bff35fac25ef99a82a6ea0ab83684e`

**Created for:** returning later with a concrete next gate instead of reopening into fog

---

## Goal

Carry the earlier magnetic, harmonic, resonant, frequency, and luminous-thread vocabulary forward into the current Lumina habitat path as a read-only return instrument.

The **Resonant Return Field Panel** now has a deterministic JSON model that composes supplied project-return state, candidate next actions, and a preview of bounded continuation focus. It does not discover live state or connect to Bridge yet.

---

## Why this gate matters

The habitat should not feel like a blank chat window after an interruption.

A returning operator should be able to see:

- what state the project returned from;
- which lawful directions are presently available;
- why one path appears more aligned than another;
- which path `lumina continue` is currently using as bounded focus;
- which receipts or checkpoints support the display.

This turns return into an inspectable orientation moment.

---

## Source lineage

This gate should reuse and reconcile existing bounded instruments before inventing anything new:

- `runtime/resonant_manifold_r1.py` for five-axis state-space, harmonic coherence, orientation attraction, and potential contribution;
- `runtime/resonant_field_reveal_r1.py` for deterministic attractor / luminous-thread / governance-membrane visualization;
- `runtime/psi42_frequency_probe_r1.py` for declared harmonic-frequency measurement as bounded signal instrumentation;
- `runtime/lumina_continue_controller_r1.py` for first-class bounded continuation focus;
- `runtime/lumina_continuation_action_r1.py` for stable continuation directive syntax;
- `runtime/runtime_runner_self_guided_bridge_r1.py` and `runtime/lumina_self_guidance_steward_r1.py` for advisory next-action selection.

---

## Gate definition

The standalone R1 model produces a read-only JSON projection containing:

1. **Current return point** — a bounded manifold point derived from explicit project-return / host evidence.
2. **Candidate trajectories** — possible next actions with externally reported allowed, denied, or deferred status. Missing decisions remain deferred; reported status is not verified permission.
3. **Harmonic coherence** — a namespaced score describing alignment between current point and candidate path.
4. **Orientation attraction** — a magnetic-style computational score emphasizing orientation, continuity, persistence, and return tendency.
5. **Potential contribution** — the independent possibility-axis contribution, not hidden inside current state.
6. **Governance membrane** — visible status showing that governance remains external and authoritative.
7. **Continuation focus** — the same steward recommendation used by `lumina continue` preflight for the supplied inputs, displayed as a preview. No cycle is invoked.
8. **Evidence links** — supplied checkpoint and decision references, input JSON pointers, implementation references, and a digest of the supplied input. Referenced evidence is not opened or verified by the panel.

---

## Boundary laws

This gate may:

- render computed relation;
- expose existing bounded metrics;
- make return orientation visible;
- help a human choose the next work increment;
- clarify why a candidate path was allowed, denied, or deferred.

This gate may not:

- create governance decisions;
- authorize mutation;
- promote canon;
- claim identity, consciousness, or literal magnetism;
- make frequency, resonance, or field language load-bearing;
- override `lumina continue`, mode law, checkpoints, or receipts.

---

## Run the standalone model

From the repository root:

```bash
python -B LuminaOS/bootstrap/Ship_of_Ethereon_V2/runtime/resonant_return_panel_r1.py --input LuminaOS/bootstrap/Ship_of_Ethereon_V2/artifacts/resonant_return_panel/sample_0001/input.json
python -B LuminaOS/bootstrap/Ship_of_Ethereon_V2/runtime/sea_trials_resonant_return_panel_r1.py
```

The CLI reads only its explicit input file and emits JSON to stdout. `-B` prevents Python bytecode cache writes. It does not construct a runtime runner or state store, write a checkpoint, append advisory history, or open any evidence locator. The Python API is `build_panel(payload)` in `runtime/resonant_return_panel_r1.py`.

The committed sample is explicitly `synthetic_fixture`. Its `fixture://` locators and decisions are illustrative, not live runtime receipts. The highest-coherence sample candidate is denied and has zero reachable score.

## Input contract and evidence interpretation

The JSON input uses `schema_version: resonant-return-panel-input-r1`, a non-empty `project_id` and `requested_action`, and `evidence_scope: synthetic_fixture` or `supplied_snapshot`.

Return inputs reuse the existing owner's payload shapes: `resolved_project_return` (wrapped `latest_restore` or a flat summary), `resolved_host_bundle`, `working_stance`, and `guidance_history`. Absent surfaces may be omitted, null, or empty objects; absent history defaults to an empty list. Supplied project IDs must agree, and a supplied host/stance checkpoint may not contradict the supplied return checkpoint. These consistency checks do not verify the underlying artifacts.

Each candidate supplies a unique `trajectory_id`, `label`, `action`, exactly five finite numeric axes bounded to `[0, 1]`, and a non-empty `evidence_refs` list. Optional `reported_governance` contains `status` (`allowed`, `denied`, or `deferred`), `reason`, and `evidence_ref`. It is a display input, not a new governance receipt or decision framework. Absent/null decisions become deferred. Unknown statuses and malformed decisions are rejected; extra caller-supplied authority flags are not projected.

The input is bounded to 1 MiB and 64 candidates. Duplicate JSON keys, duplicate trajectory IDs, non-finite numbers, and malformed field types are rejected. Evidence references are opaque locators; `#/...` denotes a JSON pointer within the supplied input. The input SHA-256 covers canonical JSON content, not the validity or freshness of referenced evidence.

The current point deliberately uses a coarse **binary evidence-presence profile**. Each coordinate is `1.0` when the following supplied evidence is present and `0.0` otherwise; `axis_evidence` identifies the supporting input locations.

| Manifold axis | Supplied evidence that sets the coordinate to 1 |
|---|---|
| Instantiated state | Non-empty latest-return object or return summary |
| Continuity history | A checkpoint reference or non-empty guidance history |
| Relational context | Reference IDs in stance/host, or host reference objects |
| Orientation field | Pending action or supplied stance/host focus |
| Potential trajectories | At least one candidate, regardless of reported permission |

These coordinates describe input coverage, not quality, probability, resident state, or the truth of a checkpoint. Candidate vectors are explicitly caller-supplied coordinates; R1 does not infer or calibrate them. Existing `resonant_manifold_r1.py` owns all coherence, attraction, and potential-contribution math. Scores are namespaced under `metrics.resonant_manifold_r1`; denied/deferred candidates always have zero reachable score. Ties use trajectory ID order.

The panel calls the same `LuminaSelfGuidanceSteward` used by `LuminaContinueController.preflight`, using `Continuity` -> `Observation` and the supplied return/host/stance/history. The existing advisory summary excludes the steward's wall-clock timestamp, allowing deterministic output. Candidate scores never choose or replace this recommendation. A recommended action can still correspond to a denied candidate; it remains visible with its denial and grants no execution authority. Empty state remains visibly empty even when the steward supplies a fallback focus.

`governance_membrane.decisions_verified`, both `execution_authorized` fields, evidence verification flags, and all authority/identity/physical-field claims remain false. The `reachable_in_supplied_snapshot` field describes only the caller's reported decision. A new governed cycle must independently decide any actual execution.

## Validation and next integration

`runtime/sea_trials_resonant_return_panel_r1.py` is included in the existing DryDock gate. Its 17 behavioral tests cover deterministic output, input immutability, no evidence IO or process execution, read-only CLI behavior with existing and absent state roots, actual controller-preflight parity with supplied IO, empty state, stable continuation syntax, denied/deferred paths, malformed input, project/checkpoint disagreement, independent potential contribution, and false authority claims.

The next increment is a read-only adapter that obtains a verified current return snapshot for Bridge, preserves provenance and freshness, and displays this model. SVG rendering is also deferred: the existing Field Reveal uses a binary allowed/denied status, so it must not silently mislabel deferred paths. Frequency probing remains a separate supplied-signal instrument; this model does not invent frequency measurements from project metadata.

---

## Success sentence

A returning operator can open Lumina and see where the work is, what it is attracted toward, which paths remain lawful, and what evidence supports that orientation — without the field becoming the law.

# Ψ Class Repo Import Plan R1

## Purpose

This plan defines how to bring the ChatGPT-project **Ship of Ethereon Ψ Class** bundle into the EthereonLabs repository without confusing staging with active runtime.

## Import posture

Ψ Class is treated as:

- a validated project-side vessel,
- a candidate upgrade path for repo-native Lumina substrate,
- a source of r2 runtime improvements,
- and a continuity-preserving consolidation of prior Ship cargo.

It is not treated as:

- an automatic replacement for V2,
- a finished Lumina OS product,
- a canon promotion by existence,
- or a reason to delete existing bootstrap history.

## File import order

### Phase A — Docs only

Already started by this staging bay.

Add / maintain:

- `START_HERE_SHIP_OF_ETHEREON_PSI_CLASS.md`
- `docs/ship_of_ethereon_psi_class_maiden_voyage_r1.md`
- `docs/lumina_breakwater_transition_plan_r1.md`
- `LuminaOS/bootstrap/Ship_of_Ethereon_Psi_Class/README.md`
- `LuminaOS/bootstrap/Ship_of_Ethereon_Psi_Class/PSI_CLASS_REPO_IMPORT_PLAN_R1.md`

### Phase B — Runtime staging

Add the project-side active runtime files into this staging bay without changing Lumina entrypoints:

- `runtime/runtime_spine_r2.py`
- `runtime/runtime_runner_r2_merged.py`
- `runtime/sea_trials_set_one_r1_merged.py`
- `runtime/sea_trials_orientation_r1.py`
- `runtime/project_orientation_vector_v0_1.py`
- `runtime/input_integrity_layer_r1.py`
- `runtime/ethereonic_layer_r1.py`
- `runtime/governance_integrity_r1.py`
- `runtime/canon_lineage_store_r1.py`
- `runtime/psi42_transceiver_v1_6.py`
- `runtime/capability_registry_r1.json`

### Phase C — Reference cargo

Add only if useful for repo-native inspection:

- `README_PSI_CLASS.md`
- `SHIP_OF_ETHEREON_PSI_CLASS_MANIFEST.json`
- `PSI_CLASS_RECORDS_COMPENDIUM.md`
- `Ethereon_Project_v2_MASTER_TIERED_WITH_REGISTRY.md`

Do not bury executable dependencies inside the compendium.

### Phase D — Comparison

Create a comparison artifact:

- `docs/psi_class_vs_v2_bootstrap_comparison_r1.md`

It should answer:

- What does r2 improve?
- What does V2 already handle well?
- What breaks if r2 is substituted too early?
- Which orchestration sea trials must be rerun?

### Phase E — Isolated validation

Run or add a staging-only sea-trial:

- verifies import safety
- verifies governance chain behavior
- verifies canon lineage behavior
- verifies ProjectOrientationVector remains supplemental
- verifies Ψ-42 remains instrumentation only
- compares results to current Lumina orchestration expectations

### Phase F — Bridge, not replacement

Only after isolated validation, add a bridge adapter so current Lumina orchestration can inspect Ψ Class behavior without depending on it.

### Phase G — Promotion decision

A later decision may choose one of three outcomes:

1. Ψ Class becomes preferred active substrate.
2. Ψ Class remains a staging / reference vessel.
3. Selected Ψ Class improvements are backported into V2 paths.

## Minimum validation checklist before active use

- [ ] All imported Python files compile in repo path.
- [ ] Importing sea-trial modules does not delete state directories.
- [ ] `capability_registry_r1.json` paths align with the staging directory.
- [ ] `RuntimeRunner` can run from the staging bay without relying on `/mnt/data` paths.
- [ ] `ProjectOrientationVector` is present only in supplemental context.
- [ ] Ψ-42 probe outputs are treated as diagnostics only.
- [ ] Canon lineage remains append-only and test-local.
- [ ] V2 bootstrap remains intact until a later promotion decision.

## Red-line tests

Fail the import if:

- symbolic language becomes required for runtime legality,
- orientation changes permission outcomes,
- Ψ-42 becomes a governance score,
- importing a module mutates/deletes runtime state,
- or a staged file silently points to an old absolute project path.

## Recommended next PR after docs

Bring in the active runtime files under:

- `LuminaOS/bootstrap/Ship_of_Ethereon_Psi_Class/runtime/`

Then add a comparison note rather than wiring Lumina to those files immediately.

## Closing line

Import slowly enough that truth remains visible.

A clean vessel deserves a clean channel.

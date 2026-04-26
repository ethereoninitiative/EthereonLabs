# Ψ Class Runtime Staging R1

## Purpose

This directory is the staging bay for Ship of Ethereon Ψ Class runtime files.

This PR begins the runtime-staging process without wiring Ψ Class into active Lumina execution.

## Current status in this staging PR

Staged now:

- `capability_registry_r1.json`
- `docs/psi_class_vs_v2_bootstrap_comparison_r1.md`

Prepared locally for full import:

- `runtime_spine_r2.py`
- `runtime_runner_r2_merged.py`
- `sea_trials_set_one_r1_merged.py`
- `sea_trials_orientation_r1.py`
- `project_orientation_vector_v0_1.py`
- `input_integrity_layer_r1.py`
- `ethereonic_layer_r1.py`
- `governance_integrity_r1.py`
- `canon_lineage_store_r1.py`
- `psi42_transceiver_v1_6.py`

## Local preflight performed before PR

The prepared runtime files were checked locally before staging:

- project-side `/mnt/data` defaults were removed from staged runtime copies
- Ψ-42 default artifact paths were converted to repo-local `_runtime_state/psi42_artifacts`
- `sea_trials_set_one_r1_merged.py` default state root was converted to repo-local `_runtime_state/ethereon_sea_trials_r2_hardening`
- `ethereonic_layer_r1.py` standalone demo registry path was converted to repo-local `_runtime_state/ethereonic_layer_registry_r1.json`
- all prepared Python runtime files compiled successfully to a temp cache

## Why the full runtime files are not active yet

The active Lumina substrate remains:

- `LuminaOS/bootstrap/Ship_of_Ethereon_V2/`

This staging bay must prove that Ψ Class can coexist with V2 before any active wiring changes.

## Import rule

When the full runtime files are added, do not change active entrypoints in the same step.

The next validation step should check:

1. Python compile from repo path.
2. Import safety for sea-trial modules.
3. Minimal `Continuity -> Observation` r2 runner cycle.
4. ProjectOrientationVector remains supplemental only.
5. Ψ-42 remains instrumentation only.
6. V2 bootstrap remains intact.

## Boundary

This directory is staging, not sovereignty.

Mode remains law. Orientation remains stance. Expression remains supplemental. Ψ-42 remains an instrument.

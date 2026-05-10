# Start Here — Lumina OS

This file exists because the primary **Lumina OS** substrate is easy to miss if you enter this repository from the newest public-facing or experimental work.

## Fastest local host start

Lumina should start like a system, not like a scavenger hunt.

Begin here:

```bash
cd LuminaOS/bootstrap/Ship_of_Ethereon_V2
python install/lumina_doctor.py
```

Optional local command install:

```bash
bash install/install_lumina.sh
```

Then use:

```bash
lumina doctor
lumina run "Review Lumina OS progress and produce the next governed action receipt."
lumina observe
lumina state --limit 12
lumina studio
```

Without installing, use:

```bash
python bin/lumina doctor
python bin/lumina run "Review Lumina OS progress and produce the next governed action receipt."
```

Host-layer docs:

- `LuminaOS/bootstrap/Ship_of_Ethereon_V2/docs/Lumina_OS_Host_Layer_001.md`
- `LuminaOS/bootstrap/Ship_of_Ethereon_V2/docs/Lumina_Local_Runbook_001.md`

## Canonical start path

Begin here:

- `LuminaOS/bootstrap/Ship_of_Ethereon_V2/`

Primary guide files inside that path:

- `LuminaOS/bootstrap/Ship_of_Ethereon_V2/README.md`
- `LuminaOS/bootstrap/Ship_of_Ethereon_V2/README_IMPORT.md`
- `LuminaOS/bootstrap/Ship_of_Ethereon_V2/REPO_NATIVE_BOOTSTRAP_NOTE.md`
- `LuminaOS/bootstrap/Ship_of_Ethereon_V2/RETURN_WITH_STANCE_BOOTSTRAP_NOTE_R1.md`
- `LuminaOS/bootstrap/Ship_of_Ethereon_V2/SELF_GUIDANCE_STEWARD_NOTE_R1.md`
- `LuminaOS/bootstrap/Ship_of_Ethereon_V2/LUMINA_ORCHESTRATION_STACK_NOTE_R1.md`
- `LuminaOS/bootstrap/Ship_of_Ethereon_V2/docs/Quantum_Concepts_Boundary_r1.md`
- `LuminaOS/bootstrap/Ship_of_Ethereon_V2/docs/lumina_studio_v0_1_spec.md`
- `LuminaOS/bootstrap/Ship_of_Ethereon_V2/docs/lumina_next_build_plan_001.md`
- `LuminaOS/bootstrap/Ship_of_Ethereon_V2/docs/Lumina_OS_Host_Layer_001.md`
- `LuminaOS/bootstrap/Ship_of_Ethereon_V2/docs/Lumina_Local_Runbook_001.md`

Primary host-layer files inside that path:

- `LuminaOS/bootstrap/Ship_of_Ethereon_V2/bin/lumina`
- `LuminaOS/bootstrap/Ship_of_Ethereon_V2/install/install_lumina.sh`
- `LuminaOS/bootstrap/Ship_of_Ethereon_V2/install/lumina_doctor.py`
- `LuminaOS/bootstrap/Ship_of_Ethereon_V2/services/lumina_observer_service.py`
- `LuminaOS/bootstrap/Ship_of_Ethereon_V2/services/lumina.service.example`

Primary runtime files inside that path:

- `LuminaOS/bootstrap/Ship_of_Ethereon_V2/runtime/runtime_spine_r1.py`
- `LuminaOS/bootstrap/Ship_of_Ethereon_V2/runtime/runtime_runner_r1_merged.py`
- `LuminaOS/bootstrap/Ship_of_Ethereon_V2/runtime/runtime_runner_return_host_bridge_r1.py`
- `LuminaOS/bootstrap/Ship_of_Ethereon_V2/runtime/runtime_runner_self_guided_bridge_r1.py`
- `LuminaOS/bootstrap/Ship_of_Ethereon_V2/runtime/input_integrity_layer_r1.py`
- `LuminaOS/bootstrap/Ship_of_Ethereon_V2/runtime/governance_integrity_r1.py`
- `LuminaOS/bootstrap/Ship_of_Ethereon_V2/runtime/canon_lineage_store_r1.py`
- `LuminaOS/bootstrap/Ship_of_Ethereon_V2/runtime/psi42_transceiver_v1_6.py`
- `LuminaOS/bootstrap/Ship_of_Ethereon_V2/runtime/quantum_concepts_registry_r1.json`
- `LuminaOS/bootstrap/Ship_of_Ethereon_V2/runtime/branch_resolution_model_r1.json`
- `LuminaOS/bootstrap/Ship_of_Ethereon_V2/runtime/sea_trials_quantum_boundary_r1.py`
- `LuminaOS/bootstrap/Ship_of_Ethereon_V2/runtime/sea_trials_set_one_r1_merged.py`
- `LuminaOS/bootstrap/Ship_of_Ethereon_V2/runtime/capability_registry_r1.json`
- `LuminaOS/bootstrap/Ship_of_Ethereon_V2/runtime/project_return_repo_native_r1.py`
- `LuminaOS/bootstrap/Ship_of_Ethereon_V2/runtime/workspace_host_repo_native_r1.py`
- `LuminaOS/bootstrap/Ship_of_Ethereon_V2/runtime/lumina_return_host_repo_native_bridge_r1.py`
- `LuminaOS/bootstrap/Ship_of_Ethereon_V2/runtime/lumina_self_guidance_steward_r1.py`
- `LuminaOS/bootstrap/Ship_of_Ethereon_V2/runtime/lumina_self_guidance_history_r1.py`
- `LuminaOS/bootstrap/Ship_of_Ethereon_V2/runtime/sea_trials_lumina_self_guidance_r1.py`

Primary orchestration files inside that path:

- `LuminaOS/bootstrap/Ship_of_Ethereon_V2/lumina_context_loader_v0_1.py`
- `LuminaOS/bootstrap/Ship_of_Ethereon_V2/lumina_decision_engine_v0_1.py`
- `LuminaOS/bootstrap/Ship_of_Ethereon_V2/lumina_orchestrator_v0_4.py`
- `LuminaOS/bootstrap/Ship_of_Ethereon_V2/sea_trials_lumina_orchestration_stack_r1.py`
- `LuminaOS/bootstrap/Ship_of_Ethereon_V2/sea_trials_lumina_orchestration_continuity_r1.py`

Primary Studio operator-surface files inside that path:

- `LuminaOS/bootstrap/Ship_of_Ethereon_V2/studio/README.md`
- `LuminaOS/bootstrap/Ship_of_Ethereon_V2/studio/lumina_cli.py`
- `LuminaOS/bootstrap/Ship_of_Ethereon_V2/studio/lumina_studio_server.py`
- `LuminaOS/bootstrap/Ship_of_Ethereon_V2/studio/lumina_state_browser.py`
- `LuminaOS/bootstrap/Ship_of_Ethereon_V2/sea_trials_lumina_studio_v0_1.py`

## What this path is

This subtree is the governed bootstrap substrate imported from **Ship of Ethereon V2** into GitHub for beginning **Lumina OS** work.

It is the correct place to start when the task is about:

- runtime law
- governance
- canon lineage
- continuity substrate
- capability routing
- Ethereonic boundary enforcement
- input integrity
- Psi-42 as a quantum-inspired classical signal transceiver under boundary control
- quantum-inspired terminology boundaries
- branch resolution instead of load-bearing collapse language
- namespaced coherence and decoherence metrics
- project return without guessing
- bounded workspace-host restoration
- bridge-based activation of repo-native return / host behavior
- bounded self-guidance advisory over restored project stance
- checkpoint-refreshed self-guidance history
- bounded orchestration from restored context into runtime execution
- continuity of pattern across restored context, orientation changes, advisory recommendation, and governed execution
- local operator execution through Lumina Studio
- local host-layer startup through the `lumina` command

## Current truth

1. **Lumina OS governed substrate starts in the bootstrap path above.**
2. **The host layer now provides a system-like local start vocabulary: `doctor`, `run`, `observe`, `state`, and `studio`.**
3. **The orchestration lane sits above the substrate and remains subordinate to runtime law.**
4. **Lumina Studio is the local operator surface for running a governed cycle and reading the receipt.**
5. **Chamber is a parallel app/public lane, not the same thing as the Lumina OS substrate, but it includes a consent surface for advisory acceptance / rejection and supervised queue state.**
6. **Root-level continuity / workspace-host files remain useful exploration history, but the repo-native bootstrap contains the preferred bridge paths for project return, workspace-host behavior, bounded self-guidance, checkpoint-refreshed guidance history, and bounded orchestration.**
7. **Quantum-adjacent language is explicitly bounded: useful for modeling observation, coherence, branching, and recomposition, but not allowed to imply literal quantum hardware or runtime authority.**
8. **Orchestration continuity has a dedicated sea-trial verifier for restored context, orientation shifts, advisory recommendation, and governed execution.**
9. **If you are trying to understand the Ship-derived runtime core, do not begin with Chamber. Begin with the bootstrap path and the host-layer command.**

## Parallel lanes in this repository

### Lumina OS governed substrate
- `LuminaOS/bootstrap/Ship_of_Ethereon_V2/`

### Lumina host layer
- `LuminaOS/bootstrap/Ship_of_Ethereon_V2/bin/lumina`
- `LuminaOS/bootstrap/Ship_of_Ethereon_V2/install/`
- `LuminaOS/bootstrap/Ship_of_Ethereon_V2/services/`

### Lumina Studio local operator surface
- `LuminaOS/bootstrap/Ship_of_Ethereon_V2/studio/`
- `LuminaOS/bootstrap/Ship_of_Ethereon_V2/sea_trials_lumina_studio_v0_1.py`

### Continuity / workspace-host exploration
- `continuity_restore_spike_r1.py`
- `lumina_workspace_host_spike_r1.py`
- `docs/continuity_restore_contract_r1.md`
- `docs/lumina_workspace_host_contract_r1.md`

### Chamber public/app lane
- `chamber.html`
- `chamber-app/`
- `docs/chamber_*`

## Recommended navigation order

1. Read this file.
2. Run `python install/lumina_doctor.py` from `LuminaOS/bootstrap/Ship_of_Ethereon_V2/`.
3. Open `LuminaOS/bootstrap/Ship_of_Ethereon_V2/README.md`.
4. For a runnable proof, run `python bin/lumina run "Review Lumina OS progress."` or install the command with `bash install/install_lumina.sh`.
5. Read `docs/Lumina_OS_Host_Layer_001.md` and `docs/Lumina_Local_Runbook_001.md`.
6. Read `README_IMPORT.md`, `REPO_NATIVE_BOOTSTRAP_NOTE.md`, `RETURN_WITH_STANCE_BOOTSTRAP_NOTE_R1.md`, `SELF_GUIDANCE_STEWARD_NOTE_R1.md`, `LUMINA_ORCHESTRATION_STACK_NOTE_R1.md`, `docs/Quantum_Concepts_Boundary_r1.md`, and `docs/lumina_studio_v0_1_spec.md`.
7. Inspect `runtime/` in that subtree, including the repo-native return / workspace-host modules, the bridged runner, the self-guided bridge runner, the checkpoint-refreshed guidance history rail, `quantum_concepts_registry_r1.json`, `branch_resolution_model_r1.json`, and `sea_trials_quantum_boundary_r1.py`.
8. Inspect `lumina_context_loader_v0_1.py`, `lumina_decision_engine_v0_1.py`, `lumina_orchestrator_v0_4.py`, `sea_trials_lumina_orchestration_stack_r1.py`, and `sea_trials_lumina_orchestration_continuity_r1.py`.
9. Only then branch outward into Chamber and its advisory / queue persistence lane.

## Assistant note

If an AI assistant, collaborator, or future contributor seems uncertain where Lumina OS begins, point them to this file first.

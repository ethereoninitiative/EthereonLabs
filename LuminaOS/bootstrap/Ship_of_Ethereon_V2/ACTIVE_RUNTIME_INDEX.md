# Active Runtime Index — Ship of Ethereon V2 / Lumina OS

**Status:** active file-ownership index.  
**Scope:** navigation only. Runtime source files remain authoritative.

Use this file when you need to know which files currently own which part of the Lumina OS bootstrap.

## Fast start

```bash
cd LuminaOS/bootstrap/Ship_of_Ethereon_V2
python install/lumina_doctor.py
python bin/lumina run "Review Lumina OS progress and produce the next governed action receipt."
python bin/lumina observe
python bin/lumina state --limit 12
```

## Runtime core

| Responsibility | Primary files |
|---|---|
| Runtime runner | `runtime/runtime_runner_r1_merged.py` |
| Runtime spine / session / context / mode guard | `runtime/runtime_spine_r1.py` |
| Capability exposure | `runtime/capability_registry_r1.json` |
| Input ambiguity and correction safety | `runtime/input_integrity_layer_r1.py` |
| Governance integrity chain | `runtime/governance_integrity_r1.py` |
| Canon lineage | `runtime/canon_lineage_store_r1.py` |
| Ethereonic overlay boundary | `runtime/ethereonic_layer_r1.py`, `runtime/ethereonic_layer_registry_r1.json` |

## Return, host, and continuity

| Responsibility | Primary files |
|---|---|
| Repo-native project return | `runtime/project_return_repo_native_r1.py` |
| Workspace host state | `runtime/workspace_host_repo_native_r1.py` |
| Return / host runner bridge | `runtime/runtime_runner_return_host_bridge_r1.py` |
| Return host bridge helper | `runtime/lumina_return_host_repo_native_bridge_r1.py` |

## Self-guidance and reflection

| Responsibility | Primary files |
|---|---|
| Bounded next-action advisory | `runtime/lumina_self_guidance_steward_r1.py` |
| Checkpoint-linked advisory history | `runtime/lumina_self_guidance_history_r1.py` |
| Self-guided runner bridge | `runtime/runtime_runner_self_guided_bridge_r1.py` |
| Recursive reflection motif | `runtime/lumina_reflective_autonomy_layer_r1.py` |
| Reflection-before-guidance runner bridge | `runtime/runtime_runner_reflective_self_guided_bridge_r1.py` |
| Bridge-stack explanation | `docs/Lumina_Runner_Bridge_Stack_001.md` |

Current motif:

```text
return -> reflect -> recommend -> govern -> record
```

Reflection and self-guidance are advisory. They do not own mode legality, mutation permission, canon lineage, promotion gates, checkpoint legality, or consent.

## Orchestration lane

| Responsibility | Primary files |
|---|---|
| Context loading | `lumina_context_loader_v0_1.py` |
| Next-action selection | `lumina_decision_engine_v0_1.py` |
| Orchestration runner | `lumina_orchestrator_v0_4.py` |
| Orchestration stack validation | `sea_trials_lumina_orchestration_stack_r1.py` |
| Orchestration continuity validation | `sea_trials_lumina_orchestration_continuity_r1.py` |

## Host layer

| Responsibility | Primary files |
|---|---|
| Local command entry | `bin/lumina` |
| Installer | `install/install_lumina.sh` |
| Doctor | `install/lumina_doctor.py` |
| Observer service | `services/lumina_observer_service.py` |
| Service example | `services/lumina.service.example` |

## Studio

| Responsibility | Primary files |
|---|---|
| Studio docs | `studio/README.md`, `docs/lumina_studio_v0_1_spec.md` |
| CLI surface | `studio/lumina_cli.py` |
| Local server | `studio/lumina_studio_server.py` |
| State browser | `studio/lumina_state_browser.py` |
| Psi-42 v1.7 receipt viewer | `studio/lumina_psi42_v17_receipt_view_r1.py` |
| Studio sea trial | `sea_trials_lumina_studio_v0_1.py` |

## Psi-42 and quantum-adjacent boundaries

| Responsibility | Primary files |
|---|---|
| Psi-42 v1.6 signal transceiver | `runtime/psi42_transceiver_v1_6.py` |
| Psi-42 relational topology extension | `runtime/psi42_relational_topology_r1.py` |
| Psi-42 v1.7 hybrid transceiver | `runtime/psi42_transceiver_v1_7.py` |
| Psi-42 v1.7 receipt summary | `runtime/psi42_v17_observation_receipt_summary_r1.py` |
| Quantum terminology boundary | `docs/Quantum_Concepts_Boundary_r1.md` |
| Quantum concepts registry | `runtime/quantum_concepts_registry_r1.json` |
| Branch resolution model | `runtime/branch_resolution_model_r1.json` |
| Quantum boundary sea trial | `runtime/sea_trials_quantum_boundary_r1.py` |

Psi-42 is an instrument. It does not own governance, canon, or runtime law.

## Sea trials

| Validation target | Primary file |
|---|---|
| Core runtime / governance / canon | `runtime/sea_trials_set_one_r1_merged.py` |
| Self-guidance | `runtime/sea_trials_lumina_self_guidance_r1.py` |
| Reflective autonomy | `sea_trials_lumina_reflective_autonomy_r1.py` |
| Reflective autonomy wiring | `sea_trials_lumina_reflective_autonomy_wiring_r1.py` |
| Orchestration stack | `sea_trials_lumina_orchestration_stack_r1.py` |
| Orchestration continuity | `sea_trials_lumina_orchestration_continuity_r1.py` |
| Studio | `sea_trials_lumina_studio_v0_1.py` |
| Psi-42 v1.7 receipt summary | `runtime/sea_trials_psi42_v17_observation_receipt_summary_r1.py` |
| Psi-42 v1.7 runtime integration | `runtime/sea_trials_psi42_v17_runtime_integration_r1.py` |

## Docs to read when uncertain

- `README.md`
- `README_IMPORT.md`
- `REPO_NATIVE_BOOTSTRAP_NOTE.md`
- `RETURN_WITH_STANCE_BOOTSTRAP_NOTE_R1.md`
- `SELF_GUIDANCE_STEWARD_NOTE_R1.md`
- `LUMINA_ORCHESTRATION_STACK_NOTE_R1.md`
- `docs/Lumina_OS_Host_Layer_001.md`
- `docs/Lumina_Local_Runbook_001.md`
- `docs/Lumina_First_Village_Framing_001.md`
- `docs/Lumina_Reflective_Autonomy_Layer_001.md`
- `docs/Lumina_Runner_Bridge_Stack_001.md`

## Maintenance rule

When a new runtime bridge, sea trial, or advisory layer becomes active, add it here. Keep prose short. This file is a map, not a doctrine.

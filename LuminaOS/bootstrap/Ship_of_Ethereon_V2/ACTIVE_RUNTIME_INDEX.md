# Active Runtime Index — Ship of Ethereon V2 / Lumina OS

**Status:** active file-ownership index.  
**Scope:** navigation only. Runtime source files and validation receipts remain authoritative.

## Fast start

```bash
cd LuminaOS/bootstrap/Ship_of_Ethereon_V2
python install/lumina_doctor.py --ensure-state
python bin/lumina-bridge
python bin/lumina run "Review Lumina OS progress and produce the next governed action receipt."
python bin/lumina observe
python bin/lumina state --limit 12
```

## Execution path truth

### Default host / Studio path

The ordinary `bin/lumina run` route is:

```text
bin/lumina
  -> studio/lumina_cli_psi42_v18.py
  -> runtime/runtime_runner_psi42_v18_adapter_r1.py
  -> runtime/runtime_runner_r1_merged.py
```

This path performs bounded project return / host work, governed runtime execution, Psi-42 v1.8 diagnostics when lawfully exposed, continuity-correlation receipt handling, checkpointing, and receipt emission.

### Optional reflective / self-guided adapter path

`runtime/runtime_runner_reflective_self_guided_bridge_r1.py` extends the dedicated self-guided return/host adapter. It records a reflective trace before bounded self-guidance after the governed return/host cycle. It is an explicit alternate runner path and is not the default `bin/lumina run` route.

### Meaning Metabolism status

`runtime/lumina_meaning_metabolism_layer_r1.py` is a standalone validated advisory experiment. It is not exposed in the capability registry and is not wired into the default host path or the reflective/self-guided adapter path.

## Runtime core

| Responsibility | Primary files |
|---|---|
| Runtime runner | `runtime/runtime_runner_r1_merged.py` |
| Runtime spine / session / context / mode guard | `runtime/runtime_spine_r1.py` |
| Capability exposure | `runtime/capability_registry_r1.json` |
| Input ambiguity and correction safety | `runtime/input_integrity_layer_r1.py` |
| Governance integrity chain | `runtime/governance_integrity_r1.py` |
| Canon lineage | `runtime/canon_lineage_store_r1.py` |
| Ethereonic overlay boundary and generated registry state | `runtime/ethereonic_layer_r1.py`; generated at `<runner base_dir>/ethereonic_layer_registry_r1.json` |

The Ethereonic registry JSON is runtime-generated state, not a committed source file beside the module. Its generated location follows the active runner or test `base_dir`.

Structural repository context validates the Git worktree before reporting branch, status, or history. Failed inspection is reported as bounded unavailable state and may not become an apparently clean repository snapshot.

## Runtime truth and canon evidence

| Responsibility | Primary files |
|---|---|
| Observation-scoped truth emission | `runtime/runtime_truth_emitter_r1.py`, `runtime/runtime_truth_observation_cycle_r1.py` |
| Public truth projection | `runtime/runtime_truth_public_snapshot_r1.py` |
| Canon genesis verification | `runtime/post_promotion_verifier_r1.py`, `artifacts/runtime_truth/current/post_promotion_verification_0001.json` |
| Cross-surface reconciliation gate | `studio/runtime_truth_reconciliation_gate_r1.py` |
| Existing truth hygiene gate | `studio/runtime_truth_gate_r1.py` |

Committed canon evidence and ephemeral Observation receipts are separate scopes. Observation refreshes may describe an empty local runtime state, but they may not overwrite or nullify committed governance and canon evidence.

## Return, Harbor, and continuity correlation

| Responsibility | Primary files |
|---|---|
| Repo-native project return | `runtime/project_return_repo_native_r1.py` |
| Workspace host state | `runtime/workspace_host_repo_native_r1.py` |
| Return / host runner bridge | `runtime/runtime_runner_return_host_bridge_r1.py` |
| Harbor project registry | `install/lumina_project_registry.py` |
| Harbor session registry | `install/lumina_session_registry.py` |
| Typed continuity correlation | `runtime/continuity_correlation_r1.py`, `runtime/continuity_correlation_registry_r1.json` |
| Correlation receipt bridge | `runtime/continuity_correlation_bridge_r1.py` |
| Psi-42 v1.8 correlated runner adapter | `runtime/runtime_runner_psi42_v18_adapter_r1.py` |

Project, Harbor session, runtime session, restore session, and host session remain distinct references joined by a correlation envelope.

## Self-guidance, reflection, and meaning assimilation

| Responsibility | Primary files | Wiring status |
|---|---|---|
| Bounded next-action advisory | `runtime/lumina_self_guidance_steward_r1.py` | Used by the explicit self-guided adapter |
| Checkpoint-linked advisory history | `runtime/lumina_self_guidance_history_r1.py` | Used by the explicit self-guided adapter |
| Self-guided runner bridge | `runtime/runtime_runner_self_guided_bridge_r1.py` | Optional alternate runner path |
| Recursive reflection motif | `runtime/lumina_reflective_autonomy_layer_r1.py` | Used by the explicit reflective/self-guided adapter |
| Reflection-before-guidance bridge | `runtime/runtime_runner_reflective_self_guided_bridge_r1.py` | Optional alternate runner path |
| Meaning metabolism / assimilation ledger | `runtime/lumina_meaning_metabolism_layer_r1.py` | Standalone validated experiment; not wired into default or adapter execution |

The reflective/self-guided adapter follows this extension shape:

```text
governed return / host cycle -> checkpoint -> reflect -> recommend -> refresh advisory receipt/history
```

The standalone Meaning Metabolism experiment models:

```text
reflect -> assimilate -> seed future guidance
```

These layers are advisory. They do not own mode legality, mutation permission, canon lineage, promotion gates, checkpoint legality, or consent.

## Living Framework and state-space experiments

| Responsibility | Primary files |
|---|---|
| Resonant Manifold model | `runtime/resonant_manifold_r1.py`, `runtime/resonant_manifold_registry_r1.json` |
| Resonant Field Reveal | `runtime/resonant_field_reveal_r1.py`, `runtime/resonant_field_reveal_registry_r1.json`, `docs/Resonant_Field_Reveal_R1.md` |
| Committed field sample | `artifacts/resonant_field_reveal/sample_0001/`, `runtime/resonant_field_reveal_sample_r1.py`, `docs/Resonant_Field_Reveal_Sample_0001.md` |
| Luminous Threads lineage | `docs/Luminous_Threads_Continuity_Lineage_R1.md` |
| Living Framework Chamber | `runtime/living_framework_chamber_r1.py`, `runtime/living_framework_registry_r1.json` |
| Living Framework ignition | `runtime/living_framework_ignition_r1.py` |
| Chamber and ignition docs | `docs/Lumina_Living_Framework_Chamber_R1.md`, `docs/Lumina_Living_Framework_Ignition_R1.md` |

These are bounded computational and interpretive experiments. They do not gain runtime authority merely by existing or producing expressive output.

## Orchestration lane

| Responsibility | Primary files |
|---|---|
| Context loading | `lumina_context_loader_v0_1.py` |
| Next-action selection | `lumina_decision_engine_v0_1.py` |
| Orchestration runner | `lumina_orchestrator_v0_4.py` |
| Orchestration validation | `sea_trials_lumina_orchestration_stack_r1.py`, `sea_trials_lumina_orchestration_continuity_r1.py` |

## Host layer and Studio

| Responsibility | Primary files |
|---|---|
| Local command entry | `bin/lumina` |
| Installer and doctor | `install/install_lumina.sh`, `install/lumina_doctor.py` |
| Observer service | `services/lumina_observer_service.py` |
| Read-only Bridge R2 position and field surface | `bin/lumina-bridge`, `studio/lumina_bridge_state_r1.py`, `studio/lumina_bridge_field_r1.py`, `studio/lumina_bridge_server_r2.py`, `docs/Lumina_Bridge_R1.md` |
| Historical Bridge R1 server | `studio/lumina_bridge_server_r1.py` |
| Studio CLI/server/state browser | `studio/lumina_cli.py`, `studio/lumina_cli_psi42_v18.py`, `studio/lumina_studio_server.py`, `studio/lumina_state_browser.py` |

Bridge witnesses and orients. Studio requests explicit actions. Runtime governance remains authoritative.

## Psi-42 and quantum-adjacent boundaries

| Responsibility | Primary files |
|---|---|
| Psi-42 v1.6 signal transceiver | `runtime/psi42_transceiver_v1_6.py` |
| Psi-42 v1.7 hybrid topology transceiver | `runtime/psi42_transceiver_v1_7.py` |
| Psi-42 v1.8 doctrine-aligned diagnostics | `runtime/psi42_transceiver_v1_8.py` |
| Quantum terminology boundary | `docs/Quantum_Concepts_Boundary_r1.md` |
| Branch resolution model | `runtime/branch_resolution_model_r1.json` |

Psi-42 is an instrument. It does not own governance, canon, runtime law, consent, or primary continuity authority.

## Sea trials

| Validation target | Primary file |
|---|---|
| Core runtime / governance / canon | `runtime/sea_trials_set_one_r1_merged.py` |
| Structural repository-context truth | `runtime/sea_trials_context_bundle_repo_truth_r1.py` |
| Stationary habitation cold return | `runtime/sea_trials_stationary_habitation_cold_return_r1.py` |
| Lumina weather observation idempotence | `runtime/sea_trials_lumina_weather_snapshot_idempotence_r1.py` |
| Ethereonic lineage visibility | `runtime/sea_trials_ethereonic_lineage_visibility_r1.py` |
| Resonant Manifold | `runtime/sea_trials_resonant_manifold_r1.py` |
| Resonant Field Reveal | `runtime/sea_trials_resonant_field_reveal_r1.py` |
| Committed field reproducibility | `runtime/sea_trials_resonant_field_reveal_sample_r1.py` |
| Living Framework Chamber | `runtime/sea_trials_living_framework_chamber_r1.py` |
| Living Framework ignition | `runtime/sea_trials_living_framework_ignition_r1.py` |
| Self-guidance | `runtime/sea_trials_lumina_self_guidance_r1.py` |
| Reflective/self-guided adapter wiring | `sea_trials_lumina_reflective_autonomy_wiring_r1.py` |
| Meaning Metabolism standalone layer | `sea_trials_lumina_meaning_metabolism_r1.py` |
| Orchestration continuity | `sea_trials_lumina_orchestration_continuity_r1.py` |
| Studio | `sea_trials_lumina_studio_v0_1.py` |
| Studio bounded diagnostics | `sea_trials_lumina_studio_diagnostics_r1.py` |
| Bridge position surface | `sea_trials_lumina_bridge_r1.py` |
| Bridge Field Viewer | `sea_trials_lumina_bridge_field_r1.py` |

## Maintenance rule

When a runtime bridge, capability, receipt contract, sea trial, or default entrypoint becomes active, update this index in the same PR. Distinguish default wiring, optional adapters, and standalone experiments. This file maps ownership; it does not create authority.

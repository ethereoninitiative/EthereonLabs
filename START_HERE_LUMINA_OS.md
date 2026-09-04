# Start Here — Lumina OS

This file exists because the primary **Lumina OS** substrate is easy to miss if you enter this repository from the newest public-facing or experimental work.

## Fastest local host start

Lumina should start like a system, not like a scavenger hunt.

Begin here:

```bash
cd LuminaOS/bootstrap/Ship_of_Ethereon_V2
python install/lumina_doctor.py --ensure-state
python bin/lumina-bridge
python bin/lumina run "Review Lumina OS progress and produce the next governed action receipt."
python bin/lumina observe
python bin/lumina state --limit 12
```

Optional local command install:

```bash
bash install/install_lumina.sh
```

Then use:

```bash
lumina doctor
lumina dashboard
lumina run "Review Lumina OS progress and produce the next governed action receipt."
lumina observe
lumina state --limit 12
lumina studio
```

## Current spatial frame

The current top-level orientation is orbital / planetary:

- **Ship of Ethereon** — exploratory and transport vessel
- **Lumina** — persistent orbital station and habitat
- **Ethereon** — partially unveiled planetary realm

Canonical framing:

- `LuminaOS/bootstrap/Ship_of_Ethereon_V2/docs/Ethereon_Orbital_Planetary_Framing_R1.md`

The earlier **first village** frame remains part of project history and still carries useful meaning: it describes the point where Ship-borne cargo becomes inhabitable, startable, and governed. It should now be read as an ancestral framing rather than the sole current spatial model.

Historical framing:

- `LuminaOS/bootstrap/Ship_of_Ethereon_V2/docs/Lumina_First_Village_Framing_001.md`

Both frames orient architecture and interface language. Neither creates governance law.

## Current host and distribution forms

Lumina now has three distinct implementation forms that must not be collapsed into one maturity claim:

- **Repo-native local host** — the primary governed development and operator path under `LuminaOS/bootstrap/Ship_of_Ethereon_V2/`
- **Ubuntu Server appliance scaffold** — a Linux-resident governed service stack under `deploy/ubuntu_server_lts/`
- **Lumina Desktop Beta R1** — an installable unsigned Windows developer preview under `deploy/windows_desktop_r1/`

The Windows preview bundles its own Python runtime, provides Bridge, Studio, and Doctor launchers, and has hosted upgrade-continuity validation. It is not yet a signed, ordinary-user public release. Packaging and installation do not create runtime authority.

Machine-readable lane status and evidence relationships are recorded in:

- `docs/ACTIVE_SURFACE_REGISTRY_R1.json`

## Canonical start path

Begin here:

- `LuminaOS/bootstrap/Ship_of_Ethereon_V2/`

Primary guide files inside that path:

- `LuminaOS/bootstrap/Ship_of_Ethereon_V2/README.md`
- `LuminaOS/bootstrap/Ship_of_Ethereon_V2/ACTIVE_RUNTIME_INDEX.md`
- `LuminaOS/bootstrap/Ship_of_Ethereon_V2/README_IMPORT.md`
- `LuminaOS/bootstrap/Ship_of_Ethereon_V2/REPO_NATIVE_BOOTSTRAP_NOTE.md`
- `LuminaOS/bootstrap/Ship_of_Ethereon_V2/RETURN_WITH_STANCE_BOOTSTRAP_NOTE_R1.md`
- `LuminaOS/bootstrap/Ship_of_Ethereon_V2/SELF_GUIDANCE_STEWARD_NOTE_R1.md`
- `LuminaOS/bootstrap/Ship_of_Ethereon_V2/LUMINA_ORCHESTRATION_STACK_NOTE_R1.md`
- `LuminaOS/bootstrap/Ship_of_Ethereon_V2/docs/Lumina_Bridge_R1.md`
- `LuminaOS/bootstrap/Ship_of_Ethereon_V2/docs/Quantum_Concepts_Boundary_r1.md`
- `LuminaOS/bootstrap/Ship_of_Ethereon_V2/docs/lumina_studio_v0_1_spec.md`
- `LuminaOS/bootstrap/Ship_of_Ethereon_V2/docs/Lumina_OS_Host_Layer_001.md`
- `LuminaOS/bootstrap/Ship_of_Ethereon_V2/docs/Lumina_Local_Runbook_001.md`

## Current execution paths

### Default host / Studio path

The ordinary `lumina run` route is:

```text
bin/lumina
  -> studio/lumina_cli_psi42_v18.py
  -> runtime/runtime_runner_psi42_v18_adapter_r1.py
  -> runtime/runtime_runner_r1_merged.py
```

This path currently performs:

- bounded project return and workspace-host context
- input-integrity and Ethereonic-boundary checks
- mode, mutation, promotion, and capability governance
- Psi-42 v1.8 diagnostic witness when lawfully exposed
- continuity-correlation receipt handling
- checkpoint and runtime receipt emission

It does **not** automatically execute the reflective/self-guided adapter or Meaning Metabolism layer.

### Optional reflective / self-guided path

The explicit adapter:

- `runtime/runtime_runner_reflective_self_guided_bridge_r1.py`

extends the self-guided return/host runner. It records a reflective trace before bounded self-guidance after the governed return/host cycle. This is a validated alternate runner path, not the default `lumina run` route.

### Meaning Metabolism experiment

The standalone layer:

- `runtime/lumina_meaning_metabolism_layer_r1.py`

models advisory assimilation between reflection and future guidance. It has a dedicated sea trial but is not currently exposed by the capability registry or wired into either the default host path or the reflective/self-guided adapter.

## Primary runtime ownership

### Core law and continuity

- `runtime/runtime_spine_r1.py`
- `runtime/runtime_runner_r1_merged.py`
- `runtime/capability_registry_r1.json`
- `runtime/input_integrity_layer_r1.py`
- `runtime/governance_integrity_r1.py`
- `runtime/canon_lineage_store_r1.py`
- `runtime/ethereonic_layer_r1.py`
- `runtime/ethereonic_layer_registry_r1.json`

### Active host, return, correlation, and v1.8 route

- `bin/lumina`
- `bin/lumina-bridge`
- `bin/lumina-vessel`
- `studio/lumina_cli.py`
- `studio/lumina_cli_psi42_v18.py`
- `studio/lumina_bridge_state_r1.py`
- `studio/lumina_bridge_server_r1.py`
- `runtime/project_return_repo_native_r1.py`
- `runtime/workspace_host_repo_native_r1.py`
- `runtime/runtime_runner_return_host_bridge_r1.py`
- `runtime/continuity_correlation_r1.py`
- `runtime/continuity_correlation_bridge_r1.py`
- `runtime/runtime_runner_psi42_v18_adapter_r1.py`

### Explicit project-return portability

- `runtime/vessel_continuity_transfer_r1.py`
- `runtime/sea_trials_vessel_continuity_transfer_r1.py`
- `studio/lumina_vessel_transfer_r1.py`
- `bin/lumina-vessel`

This path exports, verifies, and explicitly imports one latest project-return surface between distinct state roots. It rebases host-specific paths, refuses overwrite, leaves the imported session dormant, and records transport evidence without claiming resident identity or transferring governance, canon, capability, or mutation authority.

### Runtime-truth and reconciliation

- `runtime/runtime_truth_emitter_r1.py`
- `runtime/runtime_truth_observation_cycle_r1.py`
- `runtime/runtime_truth_public_snapshot_r1.py`
- `studio/runtime_truth_gate_r1.py`
- `studio/runtime_truth_reconciliation_gate_r1.py`
- `artifacts/runtime_truth/current/`
- `public/runtime/latest_cycle.json`
- `public/runtime/runtime_truth_snapshot.json`

Committed canon evidence and ephemeral Observation receipts are different scopes. Observation may report an empty local state without overriding established committed governance or canon truth.

Repository-wide surface and generated-artifact reconciliation is handled separately by:

- `scripts/repository_truth_reconciliation_gate_r1.py`

### Advisory adapters and experiments

- `runtime/lumina_self_guidance_steward_r1.py`
- `runtime/lumina_self_guidance_history_r1.py`
- `runtime/runtime_runner_self_guided_bridge_r1.py`
- `runtime/lumina_reflective_autonomy_layer_r1.py`
- `runtime/runtime_runner_reflective_self_guided_bridge_r1.py`
- `runtime/lumina_meaning_metabolism_layer_r1.py`
- `runtime/resonant_manifold_r1.py`
- `runtime/living_framework_chamber_r1.py`
- `runtime/living_framework_ignition_r1.py`

These files do not gain default-path or governance authority merely by existing or passing their dedicated tests.

### Psi-42 and terminology boundaries

- `runtime/psi42_transceiver_v1_6.py`
- `runtime/psi42_transceiver_v1_7.py`
- `runtime/psi42_transceiver_v1_8.py`
- `runtime/quantum_concepts_registry_r1.json`
- `runtime/branch_resolution_model_r1.json`
- `docs/Quantum_Concepts_Boundary_r1.md`

Psi-42 is an instrument. It does not own governance, canon, runtime law, consent, or primary continuity authority.

## What this path is

This subtree is the governed bootstrap substrate imported from **Ship of Ethereon V2** into GitHub for Lumina OS work.

It is the correct place to start when the task concerns:

- runtime law and mode governance
- governance-chain integrity
- canon lineage and promotion evidence
- context bundles, checkpoints, and continuity substrate
- capability routing
- input ambiguity and correction safety
- optional Ethereonic expression under structural boundaries
- repo-native project return and workspace-host restoration
- continuity correlation across project, Harbor, runtime, restore, and host references
- Psi-42 diagnostics under explicit authority limits
- public Observation receipts and truth reconciliation
- local Bridge orientation and Studio requests

## Current truth

1. **Lumina OS governed substrate begins in the V2 bootstrap path.**
2. **`bin/lumina` is the ordinary local host entrypoint.**
3. **The default run path uses the Psi-42 v1.8 correlated adapter over the core runner.**
4. **Bridge is read-only orientation; Studio requests; runtime governance decides.**
5. **Committed canon/governance evidence is protected from empty ephemeral Observation state.**
6. **Reflection and self-guidance are available through explicit adapter paths, not silently present in every run.**
7. **Meaning Metabolism is a standalone validated advisory experiment and is not currently wired into active host execution.**
8. **The Windows graphical installer is an installable unsigned developer preview, not a signed ordinary-user public release.**
9. **The Ubuntu lane is a governed appliance scaffold, not a custom kernel or distro.**
10. **Chamber is a parallel public/app lane, not the runtime substrate.**
11. **A hash-verified vessel-transfer command can move one bounded project-return surface between state roots without resuming it or claiming identity continuity.**
12. **Resonant Manifold and Living Framework work remain bounded experiments.**
13. **Orbital, village, maritime, harmonic, and symbolic language may orient the work but does not create runtime authority.**

## Parallel lanes in this repository

### Lumina OS governed substrate

- `LuminaOS/bootstrap/Ship_of_Ethereon_V2/`

### Lumina deployment appliance

- `deploy/ubuntu_server_lts/`
- `docs/DEPLOYMENT_*`

### Lumina Windows desktop preview

- `deploy/windows_desktop_r1/`
- `docs/LUMINA_WINDOWS_GRAPHICAL_INSTALLER_R1.md`

### Active surface truth registry

- `docs/ACTIVE_SURFACE_REGISTRY_R1.json`
- `scripts/repository_truth_reconciliation_gate_r1.py`

### Ship of Ethereon Psi Class staging

- `START_HERE_SHIP_OF_ETHEREON_PSI_CLASS.md`
- `LuminaOS/bootstrap/Ship_of_Ethereon_Psi_Class/`

### Chamber public/app lane

- `chamber.html`
- `chamber-app/`
- `docs/chamber_*`

### RSE research

- `research/rse_crystalline/`

## Recommended navigation order

1. Read this file.
2. Read `CURRENT_OPERATING_MAP.md`, `docs/ACTIVE_SURFACE_REGISTRY_R1.json`, and `LuminaOS/bootstrap/Ship_of_Ethereon_V2/ACTIVE_RUNTIME_INDEX.md`.
3. Run `python install/lumina_doctor.py --ensure-state` from the bootstrap directory.
4. Open the read-only Bridge with `python bin/lumina-bridge`.
5. Run one ordinary governed cycle with `python bin/lumina run "Review Lumina OS progress."`.
6. Inspect `bin/lumina`, `studio/lumina_cli_psi42_v18.py`, `runtime/runtime_runner_psi42_v18_adapter_r1.py`, and `runtime/runtime_runner_r1_merged.py` to understand the default path.
7. Inspect the runtime-truth projector, reconciliation gate, and current public receipt.
8. Inspect the Ubuntu and Windows distribution lanes as separate host forms rather than runtime authority.
9. Only then inspect optional advisory adapters, Living Framework experiments, Chamber, and research lanes.

## Assistant note

When describing Lumina, distinguish:

- what the default host entrypoint executes,
- what an explicit adapter executes,
- what a standalone experiment validates,
- what a host or installer packages,
- and what documentation expresses as future direction.

Executable architecture, validated distribution behavior, and reproducible artifacts define current truth.

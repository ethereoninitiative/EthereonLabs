# START HERE — Lumina OS Build Manifest

This file is the repo-native map for the actual Lumina OS build work.

It exists because the Lumina OS effort now spans runtime code, deployment scaffolds, Chamber consent surfaces, dashboard state surfaces, symbolic/interface translation notes, and staged candidate vessels. This manifest keeps those lanes findable without requiring PR archaeology or internal project memory.

## Current thesis

Lumina OS is not yet a finished standalone operating system.

The current build is a bounded continuity appliance scaffold: a repo-native runtime and deployment path for restoring project context, preserving checkpoint-linked state, producing advisory next actions, exposing system state, routing advisories through explicit human consent, and preparing a VM / Ubuntu Server LTS beta host.

Long-term, this may become a richer OS-like workspace environment. The present work earns that future by proving the continuity loop first.

## Highest-level orientation

- Active substrate: `LuminaOS/bootstrap/Ship_of_Ethereon_V2/`
- Staged candidate vessel: `LuminaOS/bootstrap/Ship_of_Ethereon_Psi_Class/`
- Deployment substrate: `deploy/ubuntu_server_lts/`
- Consent and advisory surface: `chamber-app/`
- Public state surface: `lumina-dashboard.html`, `lumina-weather.html`, `data/lumina-weather-*.json`, dashboard/weather assets
- Supporting architecture docs: `docs/`

## Active runtime path — V2

The active Lumina bootstrap remains V2 unless explicitly promoted otherwise.

Primary area:

```text
LuminaOS/bootstrap/Ship_of_Ethereon_V2/
LuminaOS/bootstrap/Ship_of_Ethereon_V2/runtime/
```

Key responsibilities:

- project-scoped return
- workspace host behavior
- checkpoint-linked continuity
- bounded self-guidance
- advisory next-step recommendation
- context-bundle restoration
- runtime runner bridge behavior
- sea-trial validation

Important files and lanes to inspect:

```text
START_HERE_LUMINA_OS.md
LuminaOS/bootstrap/Ship_of_Ethereon_V2/README.md
LuminaOS/bootstrap/Ship_of_Ethereon_V2/SELF_GUIDANCE_STEWARD_NOTE_R1.md
LuminaOS/bootstrap/Ship_of_Ethereon_V2/runtime/runtime_runner_r1_merged.py
LuminaOS/bootstrap/Ship_of_Ethereon_V2/runtime/runtime_runner_self_guided_bridge_r1.py
LuminaOS/bootstrap/Ship_of_Ethereon_V2/runtime/lumina_self_guidance_steward_r1.py
LuminaOS/bootstrap/Ship_of_Ethereon_V2/runtime/lumina_self_guidance_history_r1.py
LuminaOS/bootstrap/Ship_of_Ethereon_V2/runtime/sea_trials_lumina_self_guidance_r1.py
LuminaOS/bootstrap/Ship_of_Ethereon_V2/runtime/capability_registry_r1.json
```

## Continuity restore and return-to-project lane

This lane proves the first believable Lumina behavior: leave a project, return later, and reopen the latest known state without guessing.

Look for:

```text
continuity_restore_spike_r1.py
docs/continuity_restore_contract_r1.md
```

Related runtime lineages include the repo-native project return and workspace host modules under the V2 bootstrap runtime.

Core idea:

- project id is load-bearing
- workspace state is captured explicitly
- continuation notes travel with the state
- checkpoints are the return anchor
- restore resolves by project, not by vague chat memory

## Self-guidance lane

This is advisory continuation, not autonomy.

The steward may recommend likely next steps from restored project-return context and checkpoint-linked advisory history. It may not define governance law, canon lineage, checkpoint legality, mode legality, mutation legality, or promotion legality.

Inspect:

```text
LuminaOS/bootstrap/Ship_of_Ethereon_V2/runtime/lumina_self_guidance_steward_r1.py
LuminaOS/bootstrap/Ship_of_Ethereon_V2/runtime/lumina_self_guidance_history_r1.py
LuminaOS/bootstrap/Ship_of_Ethereon_V2/runtime/runtime_runner_self_guided_bridge_r1.py
LuminaOS/bootstrap/Ship_of_Ethereon_V2/runtime/sea_trials_lumina_self_guidance_r1.py
LuminaOS/bootstrap/Ship_of_Ethereon_V2/SELF_GUIDANCE_STEWARD_NOTE_R1.md
```

Desired proof:

1. restore project context
2. surface working stance
3. recommend next action
4. append advisory history
5. re-run and show history alignment instead of acting like every run starts from zero

## Orchestration lane

The orchestrator binds runtime runner state, context loading, and advisory decision selection.

Inspect:

```text
LuminaOS/bootstrap/Ship_of_Ethereon_V2/lumina_orchestrator_v0_3.py
LuminaOS/bootstrap/Ship_of_Ethereon_V2/lumina_orchestrator_v0_4.py
LuminaOS/bootstrap/Ship_of_Ethereon_V2/LUMINA_ORCHESTRATION_STACK_NOTE_R1.md
LuminaOS/bootstrap/Ship_of_Ethereon_V2/sea_trials_lumina_orchestration_stack_r1.py
```

Current posture:

- decision engine output remains advisory
- context loader must bind to the runner state directory
- coarse state should recover when checkpoints are absent
- orchestration does not smuggle in hidden sovereignty

## Chamber consent and action queue lane

The Chamber lane is the human-visible consent and advisory queue path.

It is OS-relevant because Lumina should not silently execute hidden actions. Recommendation, acceptance/rejection, queueing, claiming, and completion must remain separable and inspectable.

Primary area:

```text
chamber-app/
```

Inspect:

```text
chamber-app/src/advisory_queue_types.ts
chamber-app/src/advisory_queue_memory_store.ts
chamber-app/src/advisory_queue_server_v0_1.ts
chamber-app/src/advisory_queue_server_v0_2.ts
chamber-app/src/advisory_queue_store_contract.ts
chamber-app/src/advisory_queue_memory_store_v0_2.ts
chamber-app/src/advisory_queue_postgres_store_r1.ts
chamber-app/src/advisory_queue_store_factory_r1.ts
chamber-app/src/lumina_advisory_bridge_r1.ts
chamber-app/src/sea_trials_lumina_advisory_bridge_r1.ts
chamber_advisory_queue_extension_r1.sql
chamber-app/docker-compose.postgres.advisory.yml
docs/chamber_advisory_queue_note_r1.md
docs/chamber_advisory_postgres_bridge_note_r1.md
```

Boundary:

- advisory objects may be accepted or rejected
- accepted advisories may create supervised queue items
- queue completion is supervised state change
- no autonomous tool execution is implied here

## Deployment lane — Ubuntu Server LTS appliance

This is the first credible machine-resident path for Lumina OS beta.

Primary area:

```text
deploy/ubuntu_server_lts/
```

Inspect:

```text
deploy/ubuntu_server_lts/README.md
deploy/ubuntu_server_lts/bootstrap_lumina_appliance_r1.sh
deploy/ubuntu_server_lts/lumina-orchestrator.service
deploy/ubuntu_server_lts/lumina-orchestrator.timer
deploy/ubuntu_server_lts/chamber-advisory.service
deploy/ubuntu_server_lts/lumina_appliance_layout_r1.md
deploy/ubuntu_server_lts/ubuntu_vm_validation_checklist_r1.md
deploy/ubuntu_server_lts/preflight_validate_appliance_r1.sh
deploy/ubuntu_server_lts/environment_reference_r1.md
deploy/ubuntu_server_lts/lumina_beta_hardware_target_r1.md
deploy/ubuntu_server_lts/vm_first_validation_sequence_r1.md
```

Current posture:

- Ubuntu Server LTS is the host substrate
- Lumina is a governed service stack on top of that substrate
- validate in VM before hardware commitment
- dedicated mini PC / NUC-style hardware is the likely beta target after VM truth is established

## Public state surface / Observatory lane

The dashboard and weather systems are not the OS itself. They are the visible state surface for observing the continuity substrate.

Inspect:

```text
lumina-dashboard.html
lumina-weather.html
data/lumina-weather-snapshot.json
data/lumina-weather-history.json
assets/js/lumina-harmonic-audio.js
assets/css/lumina-weather-animation.css
assets/css/lumina-graph-motion.css
assets/css/lumina-dashboard-polish.css
```

Supporting generators / automation may appear in scripts or workflow files related to Lumina weather snapshot generation.

Boundary:

- dashboard expresses generated Lumina state
- dashboard does not authorize action
- dashboard does not alter governance, canon lineage, mode legality, or tool execution

## Semantic and interface translation lane

These docs help translate deep runtime complexity into a human-first interface. They are not runtime law.

Inspect:

```text
docs/lumina_human_interface_north_star_r1.md
docs/lumina_toki_pona_semantic_layer_r1.md
docs/lumina_module_map.md
docs/origin_chest_lumina_os.md
docs/origin_chest_lumina_recovery_layers.md
```

Core interface translation anchors:

- `awen sona` — continuity / preserved context
- `lawa` — governance / system law
- `nasin` — guidance / path
- `pali` — action / work
- `jan` — human consent / human presence
- `ilo` — tool substrate / machine capability
- `tomo` — workspace habitat

## Staged candidate lane — Ship of Ethereon Ψ Class

Ψ Class is staged, not active runtime.

Primary area:

```text
LuminaOS/bootstrap/Ship_of_Ethereon_Psi_Class/
```

Inspect:

```text
START_HERE_SHIP_OF_ETHEREON_PSI_CLASS.md
LuminaOS/bootstrap/Ship_of_Ethereon_Psi_Class/README.md
LuminaOS/bootstrap/Ship_of_Ethereon_Psi_Class/PSI_CLASS_REPO_IMPORT_PLAN_R1.md
LuminaOS/bootstrap/Ship_of_Ethereon_Psi_Class/runtime/README_RUNTIME_STAGING_R1.md
LuminaOS/bootstrap/Ship_of_Ethereon_Psi_Class/runtime/capability_registry_r1.json
docs/ship_of_ethereon_psi_class_maiden_voyage_r1.md
docs/lumina_breakwater_transition_plan_r1.md
docs/psi_class_vs_v2_bootstrap_comparison_r1.md
```

Important honesty note:

The full large Python runtime file set for Ψ Class was prepared conceptually but was not fully committed in the staging PR that introduced the runtime bay. Do not treat Ψ Class as active until the files are imported and isolated validation passes.

Remaining / expected staged runtime imports include:

```text
runtime_spine_r2.py
runtime_runner_r2_merged.py
sea_trials_set_one_r1_merged.py
sea_trials_orientation_r1.py
project_orientation_vector_v0_1.py
input_integrity_layer_r1.py
ethereonic_layer_r1.py
governance_integrity_r1.py
canon_lineage_store_r1.py
psi42_transceiver_v1_6.py
```

Promotion rule:

- V2 remains active until a validation-backed promotion decision changes that status.
- Ψ Class must pass Breakwater validation before replacing or backporting into active runtime.

## Governance boundary

The operating law remains:

> Mode is law.  
> Orientation is stance.  
> Expression is luminous but not sovereign.  
> Ψ-42 is an instrument, not a governor.

Practical translation:

- symbolic layers may guide language, UI, diagnostics, or stance
- advisory layers may recommend next moves
- dashboard layers may display state
- Chamber may capture human acceptance / rejection
- only explicit governed runtime paths may mutate, promote, execute, or author canon lineage

## Next integrated proof target

The next major OS threshold is one runnable local / VM loop:

1. start Lumina appliance or local runtime
2. create or load a project
3. record workspace state
4. write a checkpoint
5. exit
6. resume project
7. restore context
8. produce advisory next action
9. map advisory to Chamber queue shape
10. accept or reject through explicit human decision
11. log the cycle
12. verify state/history on the next run

This is the first true Lumina OS beta loop.

## Search guidance for future agents

If repo code search is unavailable, start here and follow paths manually.

Do not rely on site pages as the source of truth for OS implementation status. Website pages explain the project publicly; this manifest maps the build.

Useful search terms when indexing works:

```text
LuminaOS/bootstrap/Ship_of_Ethereon_V2
self_guidance_steward
runtime_runner_self_guided_bridge
lumina_orchestrator_v0_4
continuity_restore_spike
advisory_queue
lumina_advisory_bridge
ubuntu_server_lts
Ship_of_Ethereon_Psi_Class
Breakwater
```

## Present status summary

Lumina OS has crossed from concept into a bounded continuity appliance scaffold.

The work is not yet a finished OS. It is now a buildable path toward one: continuity restore, workspace return, advisory self-guidance, consent queueing, runtime observability, and VM-first deployment are all present as lanes. The next proof is integration into one runnable loop.
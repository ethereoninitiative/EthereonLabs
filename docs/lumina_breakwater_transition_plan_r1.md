# Lumina Breakwater Transition Plan R1

## Purpose

This plan defines how **Ship of Ethereon Ψ Class** should approach Lumina OS without creating a false replacement, authority collision, or symbolic dependency leak.

The Breakwater is the controlled threshold between:

- **Flagship vessel** — Ship of Ethereon Ψ Class
- **Executable harbor** — GitHub / Lumina OS bootstrap and deployment lanes
- **Public shore** — Chamber, website, and human-facing surfaces

## Transition principle

Do not replace what is working merely because a cleaner vessel exists.

Instead:

1. mark Ψ Class as a staging vessel,
2. map its r2 architecture against current repo-native V2 substrate,
3. validate r2 behavior in isolation,
4. bridge only the pieces that improve Lumina without breaking lineage.

## Current harbor map

### Active Lumina substrate

- `START_HERE_LUMINA_OS.md`
- `LuminaOS/bootstrap/Ship_of_Ethereon_V2/`

### Deployment lane

- `deploy/ubuntu_server_lts/`

### Chamber lane

- `chamber.html`
- `chamber-app/`
- `docs/chamber_*`

### Product-surface guidance

- `docs/lumina_human_interface_north_star_r1.md`
- `docs/lumina_toki_pona_semantic_layer_r1.md`
- `docs/lumina_module_map.md`

### Origin / salvage / alignment history

- `docs/origin_chest_lumina_os.md`
- `docs/origin_chest_lumina_recovery_layers.md`
- `docs/ship_v3_salvage_manifest.md`
- `docs/flagship_alignment_current_ship.md`

## Ψ Class contributions to evaluate

### 1. Runtime r2 spine

Potential contribution:

- r2 session engine
- r2 context bundle builder
- clearer action-type logging
- refined governance chain posture

Validation requirement:

- compare against `runtime_spine_r1.py` and `runtime_runner_r1_merged.py`
- confirm no existing orchestration sea trial depends on r1 quirks

### 2. Import-safe sea trials

Potential contribution:

- no destructive reset at import time
- explicit `prepare_base_dir()` / `main()` pattern
- cleaner tooling and CI behavior

Validation requirement:

- apply pattern consistently across sea-trial harnesses before treating them as reusable modules

### 3. ProjectOrientationVector

Potential contribution:

- separates stance from law
- improves artifact ordering and resume note emphasis
- helps Lumina self-guidance surface the right next work without altering governance

Validation requirement:

- keep it attached only through supplemental context
- reject any path where orientation affects mutation, promotion, checkpoint legality, or canon lineage

### 4. Ψ-42 v1.6 instrumentation

Potential contribution:

- continuity probe artifacts
- recomposition / mitigation reporting
- quantum-inspired classical signal model

Validation requirement:

- never treat probe scores as governance authority
- keep terminology aligned with `docs/Quantum_Concepts_Boundary_r1.md`

### 5. Condensed lineage model

Potential contribution:

- preserves old cargo through compendium rather than active sprawl
- supports project-file limits and contributor legibility

Validation requirement:

- do not hide active runtime dependencies inside archival compendia
- ensure executable files needed by the repo remain standalone

## Proposed staged route

### Stage 1 — Staging bay

Create:

- `LuminaOS/bootstrap/Ship_of_Ethereon_Psi_Class/README.md`
- `LuminaOS/bootstrap/Ship_of_Ethereon_Psi_Class/PSI_CLASS_REPO_IMPORT_PLAN_R1.md`

Purpose:

- declare status honestly
- define what will be imported later
- keep V2 active until validation passes

### Stage 2 — Runtime comparison packet

Later PR:

- add r2 runtime files under the Ψ Class staging bay
- add a comparison note against V2 runtime files
- do not alter current Lumina orchestration entrypoints yet

### Stage 3 — Isolated sea trial

Later PR:

- run r2 sea trials inside the staging bay
- produce a report comparing r2 output with existing V2 / Lumina orchestration expectations

### Stage 4 — Bridge candidate

Later PR:

- add a bridge adapter that lets Lumina orchestration inspect Ψ Class r2 behavior without depending on it

### Stage 5 — Promotion decision

Only after validation:

- decide whether r2 becomes preferred active substrate
- preserve V2 as lineage, fallback, or historical bootstrap

## Red lines

Do not:

- delete or rename the existing V2 bootstrap prematurely,
- make Ψ-42 scores governance criteria,
- let ProjectOrientationVector change permission outcomes,
- fold required executable files into documentation-only compendia,
- claim Ubuntu appliance equals complete independent OS,
- or confuse Chamber with Lumina substrate.

## Immediate next action

Add the staging bay and import plan.

That is the sharp next move because it turns the Ψ Class project into a repo-visible vessel without pretending it has already docked as the active runtime.

## Closing line

The Breakwater exists to prevent both drift and collision.

A new ship may be stronger than the old harbor path, but it must still enter by channel markers.

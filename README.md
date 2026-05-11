# EthereonLabs

EthereonLabs is an experimental repository for continuity-oriented AI interface work, Lumina OS runtime scaffolding, public-facing Chamber/web experiences, and RSE research artifacts.

This repository contains multiple active work lanes. The key distinction is that not every lane has the same authority: runtime files, public interface files, staging documents, and research experiments should not be treated as interchangeable.

## Current Operating Map

For the fastest current repository orientation, start with:

- `CURRENT_OPERATING_MAP.md`

This is the short harbor map for active lanes, current runtime path, symbolic-only layers, and recommended touch order.

## Lumina Lisp Layer

Structured symbolic snapshots of system state, intent, and reflection.

Location:
`/lumina/lisp/`

Purpose:
- capture session truth
- map navigation intent
- declare system state
- encode governance rules
- preserve reflection

Non-executable. Human-readable. System-aligned.

## Quick Start

- New human reader: start with `START_HERE_HUMANS.md`.
- Current operating map: start with `CURRENT_OPERATING_MAP.md`.
- Lumina OS / runtime work: start with `START_HERE_LUMINA_OS.md`.
- Ship of Ethereon Ψ Class staging: start with `START_HERE_SHIP_OF_ETHEREON_PSI_CLASS.md`.
- Chamber / website work: start with `chamber.html`, `chamber-app/`, and `docs/chamber_*`.
- RSE research work: start with `research/rse_crystalline/README.md`.

## Repository Map

### 1. Lumina OS — governed runtime substrate

**Status:** active / experimental runtime scaffold  
**Authority:** structural runtime lane

Primary path:
- `LuminaOS/bootstrap/Ship_of_Ethereon_V2/`

Use this lane for continuity scaffolding, mode governance, context bundles, capability exposure, checkpoint/resume behavior, and other governed substrate work.

### 2. Ship of Ethereon Ψ Class — staging bay

**Status:** staging / continuity upgrade path  
**Authority:** project staging and transition documentation

Primary paths:
- `START_HERE_SHIP_OF_ETHEREON_PSI_CLASS.md`
- `LuminaOS/bootstrap/Ship_of_Ethereon_Psi_Class/`
- `docs/ship_of_ethereon_psi_class_maiden_voyage_r1.md`
- `docs/lumina_breakwater_transition_plan_r1.md`

Use this lane for Ψ Class project consolidation, project-file migration, and Ship-of-Ethereon continuity staging.

### 3. Chamber — public interface layer

**Status:** public-facing / app-interface lane  
**Authority:** human entry, website, and experience surface

Primary paths:
- `chamber.html`
- `chamber-app/`
- `docs/chamber_*`

Use this lane for public UX, website surface, Chamber app behavior, and human-readable presentation.

### 4. Continuity / Workspace Host — experimental resumption layer

**Status:** exploratory / spike work  
**Authority:** experimental contracts and prototypes

Primary paths:
- `continuity_restore_spike_r1.py`
- `lumina_workspace_host_spike_r1.py`
- `docs/continuity_restore_contract_r1.md`
- `docs/lumina_workspace_host_contract_r1.md`

Use this lane for restoration contracts, workspace-host thinking, and resumption prototypes that may later inform Lumina OS runtime work.

### 5. RSE Research — exploratory research lane

**Status:** research / exploratory  
**Authority:** non-runtime, non-governance research artifacts

Primary path:
- `research/rse_crystalline/`

Use this lane for simulations, figure generators, and exploratory artifacts supporting the Referential Spiral Equation. These files may support public explanation and future papers, but they do not define runtime governance, canon promotion, or Lumina OS continuity authority.

## Authority Boundaries

- Runtime governance belongs in the Lumina OS substrate lane.
- Public-facing website and Chamber behavior belong in the Chamber lane.
- RSE simulations and figures belong in the research lane unless deliberately promoted into public explanation.
- Ψ Class materials are staging artifacts, not automatically runtime law.
- Exploratory spikes may inform architecture, but they are not finished substrate by default.

## Guidance

- For current repo orientation, begin with `CURRENT_OPERATING_MAP.md`.
- For Ship / Lumina OS substrate questions, begin with the bootstrap path.
- For Ψ Class staging questions, begin with the Ψ Class start-here waypoint and staging bay.
- For Chamber questions, begin with the Chamber lane.
- For continuity return and workspace-host questions, inspect the root-level exploration files after understanding the substrate.
- For RSE questions, begin with `research/rse_crystalline/README.md` and treat the material as research, not governance.

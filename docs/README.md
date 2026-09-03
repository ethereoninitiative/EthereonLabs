# EthereonLabs Documentation Front Door

**Status:** active navigation surface.  
**Scope:** documentation orientation only; this file does not create runtime, governance, canon, capability, identity, continuity, or deployment authority.

The `docs/` tree contains current contracts, operating guidance, research, philosophy, provenance, staging records, completed reviews, and historical lineage. Physical proximity inside `docs/` does **not** imply equal authority or equal freshness.

Use this page before treating an unfamiliar document as current.

## Truth order

When documentation disagrees with executable or validated behavior, use this order:

1. executable behavior
2. declared capability or distribution contracts
3. validation and reproducibility receipts
4. active surface registry and current navigation
5. public-site claims and explanatory material
6. historical, staging, research, philosophical, and archived material

The repository-wide contracts for this discipline are:

- `docs/ACTIVE_SURFACE_REGISTRY_R1.json` — machine-readable status and evidence relationships
- `docs/ARTIFACT_TRUTH_CONTRACT.md` — drift and reconciliation rules
- `CURRENT_OPERATING_MAP.md` — short current lane map
- `LuminaOS/bootstrap/Ship_of_Ethereon_V2/ACTIVE_RUNTIME_INDEX.md` — active Lumina file ownership

## Current operating documentation

Start here for work that can affect present architecture or present claims:

### Lumina runtime and habitat

- `START_HERE_LUMINA_OS.md`
- `LuminaOS/bootstrap/Ship_of_Ethereon_V2/ACTIVE_RUNTIME_INDEX.md`
- `docs/LUMINA_HABITAT_CREATION_CHECKLIST.md`
- `docs/HABITAT_RESONANT_RETURN_GATE_R1.md`
- `docs/VESSEL_CONTINUITY_TRANSFER_R1.md`
- `docs/RUNNER_BRIDGE_OWNERSHIP_MAP.md`
- `docs/GOVERNANCE_CANON_SEED_PLAN.md`

These documents orient current work. Runtime legality still belongs to executable governance and validated receipts.

### Deployment and desktop distribution

- `docs/DEPLOYMENT_HOST_REGISTRY_MODEL.md`
- `docs/DEPLOYMENT_RUNTIME_RECEIPT_CONTRACT.md`
- `docs/DEPLOYMENT_DRYDOCK_CHECKLIST.md`
- `docs/LUMINA_WINDOWS_GRAPHICAL_INSTALLER_R1.md`
- `docs/LUMINA_WINDOWS_BUNDLED_RUNTIME_R1.md`
- `docs/LUMINA_DESKTOP_BETA_R1_WINDOWS_HOST_FOUNDATION.md`

Distribution documentation describes packaging and host boundaries; it does not alter runtime governance or continuity truth.

### Chamber and public interface

- `chamber.html`
- `chamber-app/`
- `docs/chamber_app_foundation_contract_r1.md`
- `docs/chamber_orchestration_contract_r1.md`
- `docs/chamber_local_postgres_runbook_r1.md`
- `docs/CHAMBER_ADVISORY_VOCABULARY.md`

Chamber is an interface and consent-oriented lane, not the Lumina runtime substrate.

### Public claim and repository truth

- `docs/ACTIVE_SURFACE_REGISTRY_R1.json`
- `docs/ARTIFACT_TRUTH_CONTRACT.md`
- `scripts/repository_truth_reconciliation_gate_r1.py`
- `scripts/sea_trials_website_public_surface_r1.py`

Use these before promoting a website statement into a technical claim.

## Research and non-governing inquiry

These lanes can be important without being runtime authority:

- `docs/research/` — bounded research and investigations
- `research/rse_crystalline/` — RSE simulations and figures
- `docs/philosophy/` — observer-continuity and care-orientation inquiry
- `docs/concepts/` — conceptual material
- `docs/cartography/` — maps and spatial framing
- `docs/origin/` and `docs/provenance/` — origin and provenance records
- `docs/lumina/` and `docs/lumina_breadcrumbs/` — Lumina-specific notes and breadcrumbs

Research, philosophy, metaphor, and conceptual coherence may guide investigation. They do not by themselves establish runtime capability, governance authority, canon readiness, consciousness, identity, or observer continuity.

## Staging, reviews, and completed records

Some root-level documents remain visible because current navigation or ongoing work still references them. Typical examples include:

- stewardship and review packets
- dry-dock plans and validation records
- transition and salvage plans
- external-read records
- dashboard/demo captures
- staging notes and earlier product plans

Treat these as **supporting or historical-by-context** unless `CURRENT_OPERATING_MAP.md`, `docs/ACTIVE_SURFACE_REGISTRY_R1.json`, a current start file, or executable validation explicitly gives them a present role.

The directory `docs/drydock/` contains dry-dock material; a dry-dock record is evidence of an inspection, not automatically present architecture.

## Archive and lineage

`docs/archive/` is explicit historical lineage.

Archived material is preserved because evolutionary information matters. It is not a competing active implementation unless a current document deliberately reactivates it.

Current archive families include superseded runtime, orientation, and continuity experiments preserved during repository pruning.

> No unique idea disappears merely because its implementation is obsolete.

## Front-door hierarchy

Use repository entrypoints in this order:

```text
README.md
  -> START_HERE_HUMANS.md
      -> CURRENT_OPERATING_MAP.md
          -> docs/README.md
              -> lane-specific active contract / runbook / research lane
```

For executable Lumina work, branch from that hierarchy into:

```text
START_HERE_LUMINA_OS.md
  -> LuminaOS/bootstrap/Ship_of_Ethereon_V2/ACTIVE_RUNTIME_INDEX.md
      -> bin/lumina / validated runtime surfaces
```

`START_HERE_RUNTIME_PATH.md` is a compatibility waypoint, not a competing front door.

## Maintenance rule

Before relocating or archiving a document:

1. find current references to it;
2. decide whether those references are active, historical, or stale;
3. update active references first;
4. move the document without erasing lineage;
5. run repository truth, documentation-front-door, public-surface, and DryDock validation.

This is deliberate stratification, not cleanup for its own sake.

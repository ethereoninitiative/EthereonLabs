# DryDock Full-System Audit Receipt — 2026-05-17

## Scope

This receipt records the repository-wide DryDock sweep performed after a heavy website/header cleanup cycle and public runtime truth alignment pass.

It is an orientation receipt, not runtime authority.

## Repository posture

EthereonLabs currently carries multiple active lanes:

- Lumina OS governed runtime substrate
- Lumina host layer and Studio operator surface
- Chamber public/app interface
- public website shell
- RSE research lane
- Ship of Ethereon Psi Class staging
- Lumina Lisp symbolic snapshots
- root-level continuity and workspace-host spikes

The current orientation chain remains:

1. `README.md`
2. `CURRENT_OPERATING_MAP.md`
3. lane-specific start files, especially `START_HERE_LUMINA_OS.md`

## Website/header sweep summary

Recent DryDock work completed the migration from runtime header normalization to canonical baked headers.

Completed outcomes:

- centralized site navigation data
- fixed nav data loading race
- removed runtime header CSS injection
- canonicalized baked root HTML headers
- retired runtime header mutation
- restored animated brand sigil through focused `assets/js/brand-sigil.js`
- removed deprecated `assets/js/header-normalizer.js`
- simplified canonical header workflow back to patch-artifact generation
- updated header runbook to current state

Current source-of-truth structure:

- root HTML pages hold canonical primary navigation markup
- `assets/js/site-navigation-data.js` stores primary and footer navigation data
- `assets/js/brand-sigil.js` owns animated brand sigil enhancement
- `assets/js/site.js` remains a lightweight enhancement bootstrap
- `tools/audit_site_headers.py` audits header drift
- `.github/workflows/site-header-audit.yml` enforces header audit on relevant PRs
- `.github/workflows/canonicalize-site-headers.yml` generates patch artifacts for future canonicalization work

Lesson captured:

- the animated brand sigil was a hidden dependency inside the old header normalizer
- future cleanup must distinguish between mutation logic and visible payloads

## Public runtime truth sweep summary

Public runtime truth reporting was realigned after `latest_cycle.json` drifted back to older symbolic governance language.

Completed outcomes:

- upgraded latest cycle schema to `lumina-runtime-ui-cycle-v0.4`
- replaced stale `symbolic_dependency` / `ethereonic_attachment` fields
- restored explicit `runtime_truth` summary block
- aligned public symbolic boundary language with `runtime_truth_snapshot.json`

Current public truth rule:

Public truth receipts may summarize governance/canon/capability/protocol state, but they do not authorize action, alter governance, mutate canon, change mode legality, expose capabilities, or execute tools.

## Confirmed healthy orientation files

The following files were inspected and remain useful:

- `README.md`
- `CURRENT_OPERATING_MAP.md`
- `START_HERE_LUMINA_OS.md`

Observed strength:

- authority boundaries are explicitly stated
- Lumina OS substrate is separated from Chamber/public surface
- RSE research is bounded as research, not runtime governance
- Psi Class is staged, not automatically law
- Lumina Lisp is symbolic and non-executable

Observed risk:

- orientation sprawl is increasing
- future contributors may need a current audit receipt to know which maps and runbooks reflect present truth

## Remaining watchlist

### 1. Lumina runtime subtree

Next deep inspection should focus on:

- runtime receipt generation
- governance chain verification
- canon lineage verification
- capability registry consistency
- public snapshot ingestion path
- host-layer doctor/run/observe commands
- Studio invocation path

### 2. Workflow hygiene

Header workflows are now sane, but broader workflow inventory should be reviewed later for obsolete CI or migration residue.

### 3. Branch hygiene

Many DryDock branches were created during rapid cleanup. Closed/merged branches may need pruning through GitHub UI or repository maintenance tools.

### 4. Public/private truth boundary

The public runtime summaries are intentionally limited. Full chain verification may remain dependent on local `.lumina_state` artifacts and should not be overstated in public JSON.

## Current next recommended move

Proceed into a Lumina runtime-subtree DryDock pass.

Suggested inspection order:

1. `LuminaOS/bootstrap/Ship_of_Ethereon_V2/ACTIVE_RUNTIME_INDEX.md`
2. `LuminaOS/bootstrap/Ship_of_Ethereon_V2/runtime/runtime_truth_emitter_r1.py`
3. `LuminaOS/bootstrap/Ship_of_Ethereon_V2/runtime/runtime_truth_observation_cycle_r1.py`
4. `LuminaOS/bootstrap/Ship_of_Ethereon_V2/runtime/runtime_truth_public_snapshot_r1.py`
5. `LuminaOS/bootstrap/Ship_of_Ethereon_V2/install/lumina_doctor.py`
6. `LuminaOS/bootstrap/Ship_of_Ethereon_V2/bin/lumina`
7. `LuminaOS/bootstrap/Ship_of_Ethereon_V2/studio/lumina_cli.py`

## DryDock note

This sweep corrected several real barnacles, including one visible regression caused by an earlier incomplete dependency read. The durable lesson is to inspect hidden dependencies before declaring a hull clean.

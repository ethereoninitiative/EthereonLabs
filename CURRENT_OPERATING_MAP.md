# Current Operating Map

**Status:** active navigation aid.  
**Scope:** repository orientation, not runtime authority.

This file gives a fast map of the current EthereonLabs lanes.

## Primary lanes

| Lane | Path | Role |
|---|---|---|
| Lumina OS substrate | `LuminaOS/bootstrap/Ship_of_Ethereon_V2/` | Active governed runtime scaffold |
| Lumina host layer | `LuminaOS/bootstrap/Ship_of_Ethereon_V2/bin/`, `install/`, `services/` | Local command, doctor, observer, service examples |
| Lumina Studio | `LuminaOS/bootstrap/Ship_of_Ethereon_V2/studio/` | Local operator surface |
| Lumina orchestration | `LuminaOS/bootstrap/Ship_of_Ethereon_V2/lumina_*` | Context loading and action routing |
| Self-guidance and reflection | `LuminaOS/bootstrap/Ship_of_Ethereon_V2/runtime/lumina_self_*`, `runtime/lumina_reflective_*` | Advisory recommendation and reflection before guidance |
| Chamber | `chamber.html`, `chamber-app/`, `docs/chamber_*` | Public interface and app lane |
| RSE research | `research/rse_crystalline/` | Research, simulations, and figures |
| Ship of Ethereon Psi Class | `START_HERE_SHIP_OF_ETHEREON_PSI_CLASS.md`, `LuminaOS/bootstrap/Ship_of_Ethereon_Psi_Class/` | Staging and project consolidation |
| Lumina Lisp | `lumina/lisp/` | Non-executable symbolic snapshots |
| Root spikes | `continuity_restore_spike_r1.py`, `lumina_workspace_host_spike_r1.py` | Reference / exploration history |

## Current active Lumina path

```text
host or Studio
  -> project return / host context
  -> reflective trace
  -> self-guidance advisory
  -> governed runtime cycle
  -> checkpoint and receipt
```

Short form:

```text
return -> reflect -> recommend -> govern -> record
```

## Start points

- New human reader: `START_HERE_HUMANS.md`
- Lumina OS work: `START_HERE_LUMINA_OS.md`
- Active Lumina file ownership: `LuminaOS/bootstrap/Ship_of_Ethereon_V2/ACTIVE_RUNTIME_INDEX.md`
- Artifact truth / drift prevention: `docs/ARTIFACT_TRUTH_CONTRACT.md`
- Psi Class staging: `START_HERE_SHIP_OF_ETHEREON_PSI_CLASS.md`
- Lisp symbolic continuity: `lumina/lisp/README.md`

## Boundary reminders

- Runtime work belongs in the Lumina OS substrate lane.
- Reflection and self-guidance are advisory.
- Chamber is public/app surface, not the runtime substrate.
- RSE research does not define runtime behavior by default.
- Lisp preserves thought-shapes and is not executable.
- Psi Class is staging unless promoted through validated work.
- Root spikes are reference material unless deliberately moved into the bootstrap path.
- When runtime, registry, validation receipts, docs, or website language disagree, reconcile them through `docs/ARTIFACT_TRUTH_CONTRACT.md`.

## Next maintenance step

Keep this file short. When a lane changes status, update this map, the matching lane-specific start file, and the artifact truth contract if the truth hierarchy itself changes.

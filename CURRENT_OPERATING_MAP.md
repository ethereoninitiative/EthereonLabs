# Current Operating Map

**Status:** active navigation aid.  
**Scope:** repository orientation, not runtime authority.

This file gives a fast map of the current EthereonLabs lanes.

## Primary lanes

| Lane | Path | Role |
|---|---|---|
| Lumina OS substrate | `LuminaOS/bootstrap/Ship_of_Ethereon_V2/` | Active governed runtime scaffold |
| Lumina host layer | `LuminaOS/bootstrap/Ship_of_Ethereon_V2/bin/`, `install/`, `services/` | Local command, doctor, observer, service examples |
| Lumina Bridge | `LuminaOS/bootstrap/Ship_of_Ethereon_V2/bin/lumina-bridge`, `studio/lumina_bridge_*` | Local read-only ship-position surface |
| Lumina Studio | `LuminaOS/bootstrap/Ship_of_Ethereon_V2/studio/` | Local operator action surface |
| Lumina orchestration | `LuminaOS/bootstrap/Ship_of_Ethereon_V2/lumina_*` | Context loading and action routing |
| Lumina deployment appliance | `deploy/ubuntu_server_lts/`, `docs/DEPLOYMENT_*` | Ubuntu Server appliance scaffold and deployment keel guardrails |
| Advisory reflection and self-guidance adapters | `LuminaOS/bootstrap/Ship_of_Ethereon_V2/runtime/runtime_runner_self_guided_bridge_r1.py`, `runtime/runtime_runner_reflective_self_guided_bridge_r1.py` | Explicit optional adapters layered around governed return/host cycles |
| Meaning Metabolism experiment | `LuminaOS/bootstrap/Ship_of_Ethereon_V2/runtime/lumina_meaning_metabolism_layer_r1.py` | Standalone advisory assimilation layer; validated but not wired into the default host entrypoint |
| Chamber | `chamber.html`, `chamber-app/`, `docs/chamber_*` | Public interface and app lane |
| RSE research | `research/rse_crystalline/` | Research, simulations, and figures |
| Ship of Ethereon Psi Class | `START_HERE_SHIP_OF_ETHEREON_PSI_CLASS.md`, `LuminaOS/bootstrap/Ship_of_Ethereon_Psi_Class/` | Staging and project consolidation |
| Lumina Lisp | `lumina/lisp/` | Non-executable symbolic snapshots |
| Stewardship / review packets | `docs/FLEET_STEWARDSHIP_PACKET_*`, `docs/*BRIDGE*`, `docs/*REGISTRY*`, `docs/*VOCABULARY*` | Review follow-up, bridge discipline, surface maps, and naming hygiene |
| Lumina habitat roadmap | `docs/LUMINA_HABITAT_CREATION_CHECKLIST.md` | Editable checklist for turning Lumina into a persistent intelligence habitat |
| Root spikes | `continuity_restore_spike_r1.py`, `lumina_workspace_host_spike_r1.py` | Reference / exploration history |

## Current default Lumina host path

The ordinary `lumina run` command currently follows this executable route:

```text
host or Studio request
  -> project return / bounded host context
  -> governed runtime cycle
  -> Psi-42 diagnostic witness and continuity correlation
  -> checkpoint and receipt
```

Short form:

```text
return -> govern -> witness -> correlate -> record
```

This path is implemented through `bin/lumina`, `studio/lumina_cli_psi42_v18.py`, `runtime/runtime_runner_psi42_v18_adapter_r1.py`, and the core `runtime/runtime_runner_r1_merged.py`.

## Optional advisory adapter path

A dedicated adapter path extends a governed return/host cycle with reflection before bounded self-guidance:

```text
governed return / host cycle
  -> checkpoint
  -> reflective trace
  -> self-guidance advisory
  -> refreshed receipt and advisory history
```

This path is explicit and optional. It is not the default `lumina run` route.

## Meaning Metabolism experiment

The Meaning Metabolism layer validates this advisory sequence in isolation:

```text
reflect -> assimilate -> seed future guidance
```

It is not currently exposed as a capability or wired into the default host or reflective/self-guided runner paths.

Bridge distinction:

```text
Bridge orients -> Studio requests -> runtime governs -> receipts record
```

Deployment bridge form:

```text
host boundary -> appliance preflight -> governed runtime receipt -> Chamber bridge
```

## Start points

- New human reader: `START_HERE_HUMANS.md`
- Lumina OS work: `START_HERE_LUMINA_OS.md`
- Local Bridge surface: `LuminaOS/bootstrap/Ship_of_Ethereon_V2/docs/Lumina_Bridge_R1.md`
- Lumina habitat roadmap: `docs/LUMINA_HABITAT_CREATION_CHECKLIST.md`
- Active Lumina file ownership: `LuminaOS/bootstrap/Ship_of_Ethereon_V2/ACTIVE_RUNTIME_INDEX.md`
- Lumina deployment appliance: `deploy/ubuntu_server_lts/README.md`
- Deployment keel guardrails: `docs/DEPLOYMENT_HOST_REGISTRY_MODEL.md`, `docs/DEPLOYMENT_RUNTIME_RECEIPT_CONTRACT.md`, and `docs/DEPLOYMENT_DRYDOCK_CHECKLIST.md`
- Artifact truth / drift prevention: `docs/ARTIFACT_TRUTH_CONTRACT.md`
- Governance / canon seed plan: `docs/GOVERNANCE_CANON_SEED_PLAN.md`
- Fleet stewardship follow-up: `docs/FLEET_STEWARDSHIP_PACKET_2026_05_20.md` and `docs/FLEET_STEWARDSHIP_PACKET_AMENDMENT_2026_05_20.md`
- Psi Class staging: `START_HERE_SHIP_OF_ETHEREON_PSI_CLASS.md`
- Lisp symbolic continuity: `lumina/lisp/README.md`

## Boundary reminders

- Runtime work belongs in the Lumina OS substrate lane.
- Deployment appliance work must preserve a host/environment boundary before Chamber queue items become runtime work.
- Bridge is a read-only orientation surface; it does not authorize actions or outrank runtime truth.
- Studio is the explicit local operator action surface; runtime governance still decides legality.
- Reflection and self-guidance are advisory and adapter-scoped unless a future validated change deliberately promotes their wiring.
- Meaning Metabolism may seed future stance, but it is presently standalone and does not govern mode legality, mutation permission, promotion gates, checkpoint legality, canon lineage, or consent.
- Chamber is public/app surface, not the runtime substrate.
- RSE research does not define runtime behavior by default.
- Lisp preserves thought-shapes and is not executable.
- Psi Class is staging unless promoted through validated work.
- Stewardship and review packets guide future work; they do not create runtime authority by themselves.
- Root spikes are reference material unless deliberately moved into the bootstrap path.
- When runtime, registry, validation receipts, docs, or website language disagree, reconcile them through `docs/ARTIFACT_TRUTH_CONTRACT.md`.
- Empty governance or canon history is valid only when explained; use `docs/GOVERNANCE_CANON_SEED_PLAN.md` before seeding history.

## Next maintenance step

Keep this file short and execution-accurate. When a lane changes status, update this map, the matching lane-specific start file, and the artifact truth contract if the truth hierarchy itself changes.
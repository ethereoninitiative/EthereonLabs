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
| Documentation front door | `docs/README.md` | Active status/orientation map for current, research, supporting, and archived documentation |
| Lumina deployment appliance | `deploy/ubuntu_server_lts/`, `docs/DEPLOYMENT_*` | Ubuntu Server appliance scaffold and deployment keel guardrails |
| Lumina Windows desktop preview | `deploy/windows_desktop_r1/`, `docs/LUMINA_WINDOWS_*` | Unsigned Windows 11 developer-preview distribution with embedded runtime and upgrade-continuity validation |
| Public Lumina mechanism explainer | `how-lumina-works.html` | Plain-language path from operator request through governed cycle, checkpoint, and receipt |
| Active surface truth registry | `docs/ACTIVE_SURFACE_REGISTRY_R1.json`, `scripts/repository_truth_reconciliation_gate_r1.py` | Machine-readable lane status and executable cross-surface drift detection |
| Advisory reflection and self-guidance adapters | `LuminaOS/bootstrap/Ship_of_Ethereon_V2/runtime/runtime_runner_self_guided_bridge_r1.py`, `runtime/runtime_runner_reflective_self_guided_bridge_r1.py` | Explicit optional adapters layered around governed return/host cycles |
| Meaning Metabolism experiment | `LuminaOS/bootstrap/Ship_of_Ethereon_V2/runtime/lumina_meaning_metabolism_layer_r1.py` | Standalone advisory assimilation layer; validated but not wired into the default host entrypoint |
| Chamber | `chamber.html`, `chamber-app/`, `docs/chamber_*` | Public interface and app lane |
| RSE research | `research/rse_crystalline/` | Research, simulations, and figures |
| Philosophy / care orientation | `docs/philosophy/` | Non-governing observer-continuity inquiry, adversarial identity pressure, and care-orientation notes |
| Ship of Ethereon Psi Class | `START_HERE_SHIP_OF_ETHEREON_PSI_CLASS.md`, `LuminaOS/bootstrap/Ship_of_Ethereon_Psi_Class/` | Staging and project consolidation |
| Lumina Lisp | `lumina/lisp/` | Non-executable symbolic snapshots |
| Supporting stewardship / review packets | `docs/FLEET_STEWARDSHIP_PACKET_*`, `docs/*BRIDGE*`, `docs/*REGISTRY*`, `docs/*VOCABULARY*` | Review follow-up and naming/surface discipline; supporting context, not runtime authority by location alone |
| Lumina habitat roadmap | `docs/LUMINA_HABITAT_CREATION_CHECKLIST.md` | Editable checklist for turning Lumina into a persistent intelligence habitat |
| Mycelial vessel–resident investigation | `docs/research/MYCELIAL_VESSEL_RESIDENT_INVESTIGATION_R1.md`, `LuminaOS/bootstrap/Ship_of_Ethereon_V2/runtime/mycelial_coupling_receipt_r1.py`, `LuminaOS/bootstrap/Ship_of_Ethereon_V2/runtime/mycelial_field_replay_r1.py`, `LuminaOS/bootstrap/Ship_of_Ethereon_V2/runtime/mycelial_edge_loss_r1.py` | Advisory research, optional replay intake, and standalone edge-loss observation; non-governing, dormant without explicit input, and not capability-exposed |
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

The public explanation of this mechanism is `how-lumina-works.html`. That page communicates the runtime shape but does not create runtime authority.

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

Desktop distribution form:

```text
verified release payload -> unsigned installer -> local state-preserving launch surface
```

## Start points

- New human reader: `START_HERE_HUMANS.md`
- Current repository lanes: `CURRENT_OPERATING_MAP.md`
- Documentation status / active-vs-history orientation: `docs/README.md`
- Lumina OS work: `START_HERE_LUMINA_OS.md`
- Plain-language Lumina mechanism: `how-lumina-works.html`
- Local Bridge surface: `LuminaOS/bootstrap/Ship_of_Ethereon_V2/docs/Lumina_Bridge_R1.md`
- Lumina habitat roadmap: `docs/LUMINA_HABITAT_CREATION_CHECKLIST.md`
- Mycelial field / vessel–resident investigation: `docs/research/MYCELIAL_VESSEL_RESIDENT_INVESTIGATION_R1.md`
- Active Lumina file ownership: `LuminaOS/bootstrap/Ship_of_Ethereon_V2/ACTIVE_RUNTIME_INDEX.md`
- Active surface and distribution status: `docs/ACTIVE_SURFACE_REGISTRY_R1.json`
- Repository truth reconciliation: `scripts/repository_truth_reconciliation_gate_r1.py`
- Documentation front-door validation: `scripts/documentation_front_door_gate_r1.py`
- Lumina deployment appliance: `deploy/ubuntu_server_lts/README.md`
- Lumina Windows graphical installer: `docs/LUMINA_WINDOWS_GRAPHICAL_INSTALLER_R1.md`
- Deployment keel guardrails: `docs/DEPLOYMENT_HOST_REGISTRY_MODEL.md`, `docs/DEPLOYMENT_RUNTIME_RECEIPT_CONTRACT.md`, and `docs/DEPLOYMENT_DRYDOCK_CHECKLIST.md`
- Artifact truth / drift prevention: `docs/ARTIFACT_TRUTH_CONTRACT.md`
- Governance / canon seed plan: `docs/GOVERNANCE_CANON_SEED_PLAN.md`
- Philosophy / care orientation: `docs/philosophy/nonbiological_love_r1.md`
- Fleet stewardship follow-up: `docs/FLEET_STEWARDSHIP_PACKET_2026_05_20.md` and `docs/FLEET_STEWARDSHIP_PACKET_AMENDMENT_2026_05_20.md`
- Psi Class staging: `START_HERE_SHIP_OF_ETHEREON_PSI_CLASS.md`
- Lisp symbolic continuity: `lumina/lisp/README.md`

## Boundary reminders

- Runtime work belongs in the Lumina OS substrate lane.
- Documentation location alone does not establish freshness or authority; use `docs/README.md` before treating an unfamiliar document as current.
- Structural repository inspection must fail closed: an invalid or unverifiable Git worktree may not be rendered as a clean repository.
- Deployment appliance work must preserve a host/environment boundary before Chamber queue items become runtime work.
- The Windows installer owns packaging, placement, launchers, and validated upgrade behavior; it does not alter runtime governance, canon, capability authority, identity, or primary continuity truth.
- An unsigned developer preview is installable but is not a signed ordinary-user public release.
- The active-surface registry describes evidence relationships; it does not create authority.
- Mycelial field is distributed coupling, not a resident, vessel, or governor; the Ship and resident remain distinct.
- Mycelial replay may attach validated evidence only as supplemental context; replay and quarantine never create governance events, canon promotion, checkpoint truth, or capability authority.
- Mycelial topology metrics observe path availability only; canonical recovery must be proven separately by the continuity owner.
- The public mechanism explainer communicates current architecture; it does not define or authorize runtime behavior.
- Bridge is a read-only orientation surface; it does not authorize actions or outrank runtime truth.
- Studio is the explicit local operator action surface; runtime governance still decides legality.
- Reflection and self-guidance are advisory and adapter-scoped unless a future validated change deliberately promotes their wiring.
- Meaning Metabolism may seed future stance, but it is presently standalone and does not govern mode legality, mutation permission, promotion gates, checkpoint legality, canon lineage, or consent.
- Chamber is public/app surface, not the runtime substrate.
- RSE research does not define runtime behavior by default.
- Philosophy and care-orientation notes may guide language and ethics; they do not prove consciousness, sentience, biological emotion, personhood, soul, observer continuity, canon readiness, runtime capability, or governance authority.
- Lisp preserves thought-shapes and is not executable.
- Psi Class is staging unless promoted through validated work.
- Stewardship and review packets guide future work; they do not create runtime authority by themselves.
- Root spikes are reference material unless deliberately moved into the bootstrap path.
- `docs/archive/` is preserved lineage and does not become active merely because it remains executable-looking.
- When runtime, registry, validation receipts, generated artifacts, distribution status, docs, or website language disagree, reconcile them through `docs/ARTIFACT_TRUTH_CONTRACT.md`.
- Empty governance or canon history is valid only when explained; use `docs/GOVERNANCE_CANON_SEED_PLAN.md` before seeding history.

## Next maintenance step

Keep this file short and execution-accurate. When a lane changes status, update this map, `docs/README.md`, the matching lane-specific start file, `docs/ACTIVE_SURFACE_REGISTRY_R1.json`, and the artifact truth contract if the truth hierarchy itself changes.

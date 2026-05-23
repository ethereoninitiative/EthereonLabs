# Governed Promotion Runbook

**Status:** operational runbook  
**Scope:** lawful promotion from validated DryDock state into Canon lineage

## Purpose

This runbook prevents canon from becoming a ceremonial label.

A promotion is valid only when executed through runtime governance, supported by validation evidence, and verified afterward.

## Promotion prerequisites

Before promotion, confirm:

- the change has been reviewed in DryDock,
- a validation artifact exists,
- regression checks are complete,
- symbolic or narrative material is not structurally required,
- mutation is lawful for the source mode,
- the promotion packet includes all required fields.

## Required promotion packet fields

```json
{
  "validation_artifact_id": "string",
  "test_execution_log": "string",
  "change_summary": "string",
  "structural_impact_assessment": "string",
  "regression_check_confirmation": true,
  "conceptual_layer_check_confirmation": true,
  "runtime_requires_symbolic_interpretation": false
}
```

## Forbidden shortcuts

Do not:

- hand-write canon lineage records,
- edit governance logs manually,
- promote from Observation,
- treat aesthetic or poetic language as validation evidence,
- allow symbolic systems to become required for mode legality, checkpoint recovery, capability loading, or promotion gates,
- seed canon merely to avoid an empty count.

## Lawful execution shape

A lawful promotion must follow the guarded runtime path:

1. create or resume a runtime session,
2. assess input integrity when the request is derived from user language,
3. validate Ethereonic layer independence,
4. validate context attachment boundaries,
5. validate transition legality,
6. validate mutation legality,
7. check symbolic dependency leakage,
8. validate promotion packet,
9. append governance promotion event,
10. commit canon lineage through `CanonLineageStore.promote()`,
11. append canon lineage governance event,
12. write checkpoint,
13. verify governance chain and canon lineage.

## Genesis candidate

The first canon candidate is:

`canon-0001: Runtime Truth Reconciliation / Genesis DryDock Validation Baseline`

It should be created only by the runtime promotion harness and verified by `post_promotion_verifier_r1.py`.

## Post-promotion verification

Promotion is incomplete until verification confirms:

- governance chain valid,
- governance event count greater than zero,
- canon lineage valid,
- canon head present,
- canon record count greater than zero,
- checkpoint references valid where available,
- symbolic dependency remains disallowed,
- promotion receipt references the validation artifact.

## Rollback philosophy

Canon is append-only. Do not rewrite prior canon records.

If a promoted state is later found defective, append a correcting canon record that names the defect and supersedes the prior state through lineage, rather than mutating history.

## OS trajectory note

Governed promotion is not bureaucracy for its own sake.

Lumina Core is intended to sit beneath a Habitat Layer. A habitat-class operating environment needs trusted constitutional substrate before it can responsibly manage continuity, state, services, and identity-bearing operator surfaces.

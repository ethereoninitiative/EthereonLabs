# Governance and Canon Seed Plan

**Status:** historical seed plan; `canon-0001` established

## Current repository state

`canon-0001 is established` in the committed runtime-truth evidence bundle.

Evidence files:

- `artifacts/runtime_truth/current/governance_chain_0001.jsonl`
- `artifacts/runtime_truth/current/canon_lineage_0001.jsonl`
- `artifacts/runtime_truth/current/promotion_receipt_0001.json`
- `artifacts/runtime_truth/current/sea_trial_genesis_governance_r1_receipt.json`
- `artifacts/runtime_truth/current/post_promotion_verification_0001.json`

The verification receipt records one valid governance event, one valid canon record, `canon_head = canon-0001`, a passed promotion, and `symbolic_dependency_violation = false`.

## Observation-state distinction

The scheduled Observation refresh reads local state under `.lumina_state/`. A fresh runner can have an empty local governance log and an empty local canon lineage.

That local observation is a separate scope from the committed evidence bundle. Public runtime files now name both scopes explicitly:

- `committed_runtime_truth_evidence`
- `ephemeral_observation_state`

## Future canon work

A future `canon-0002` requires current evidence for a second governance event, parent linkage to `canon-0001`, a valid promotion receipt, negative mutation tests, and complete post-promotion verification.

Until those artifacts are present and pass, the committed canon head remains `canon-0001`.

## Rule

Committed evidence defines committed canon truth. Ephemeral observation describes one local runtime instance. Keep the two scopes explicit.

# Governance and Canon Seed Plan

**Status:** DryDock planning note  
**Scope:** explains the current empty governance/canon runtime truth state and defines the next lawful seed path.

## Current truth

Public runtime truth may validly report:

- `governance_chain.valid = true`
- `governance_chain.event_count = 0`
- `canon_lineage.valid = true`
- `canon_lineage.record_count = 0`

This means the verification machinery exists and passes, but no durable governance or canon history has yet been seeded through a formal promotion path.

That state is structurally valid, but publicly ambiguous if not explained.

## Boundary

Do not seed canon simply to avoid an empty count.

Canon lineage should begin only when a validated structural state is intentionally promoted through the runtime promotion path.

Governance history may begin earlier with non-canonical events, but those events must clearly describe what they record and must not imply canon promotion.

## Recommended seed order

1. **Governance orientation event**
   - Record that artifact truth reconciliation and capability registry cleanup were completed.
   - Mark as non-canonical.
   - Reference relevant PRs or receipts.

2. **Validation receipt event**
   - Record the Observation/runtime-truth pass showing capability registry validity.
   - Mark as audit evidence, not promotion.

3. **First canon seed candidate**
   - Promote only after a deliberate DryDock-to-Canon promotion packet exists.
   - Required packet should include:
     - validation artifact reference
     - test execution log
     - change summary
     - structural impact assessment
     - regression confirmation
     - conceptual layer check confirmation

## First canon candidate

Suggested future canon seed:

**canon-0001: Runtime Truth Reconciliation Baseline**

Candidate summary:

> Establishes the first promoted baseline after artifact-truth contract creation, operating-map linkage, capability registry scope reconciliation, stale capability removal, and passing runtime truth audit.

This should not be created until the formal promotion path produces a governance event hash and validation artifact reference.

## Rule

Empty history is better than false history.

But explained emptiness is better than confusing emptiness.

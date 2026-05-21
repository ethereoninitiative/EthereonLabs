# Chamber Runtime Bridge DryDock Plan

**Status:** proposed drydock plan  
**Authority:** review checklist only  
**Scope:** future wiring between Chamber advisory records and Lumina runtime cycles

## Purpose

The Chamber to runtime bridge is the first place where public-facing consent shape and governed runtime behavior meet.

This document defines the checks that should be in place before that bridge becomes active.

## Intended chain

```text
chamber_advisory
  -> explicit user decision
  -> chamber_action_queue item
  -> governance-admitted runtime request
  -> runtime receipt
  -> action_queue outcome summary
```

The runtime should not consume a raw advisory directly.

## Required invariants

1. A pending advisory cannot produce a runtime request.
2. A declined advisory cannot produce a runtime request.
3. An accepted advisory may produce at most one linked action queue item unless a later schema explicitly supports repeat work.
4. A queued action must pass runtime governance before work is attempted.
5. Runtime receipts must not rewrite advisory decision fields.
6. Failed runtime work should update outcome fields without overwriting the original decision state.
7. The bridge must preserve user ids for decision, claim, and completion.
8. Bridge failures should be visible as receipts, not hidden retries.

## DryDock checks

Before activation, run a drydock suite that verifies:

| Check | Expected result |
|---|---|
| pending advisory bridge attempt | halted, no runtime request |
| declined advisory bridge attempt | halted, no runtime request |
| accepted advisory without queued action | creates one queue item or halts with reason |
| accepted advisory with existing queue item | no duplicate queue item |
| queued action with governance denial | records halt outcome, preserves consent state |
| queued action with runtime failure | writes outcome summary, preserves consent state |
| attempted advisory record rewrite | rejected or ignored |
| missing user id on state transition | rejected |

## Bridge receipt minimum

Every bridge attempt should leave a small receipt with:

```text
bridge_receipt_id
advisory_id
action_queue_id
requested_action_type
runtime_mode_requested
governance_result
runtime_result
created_at
notes
```

## Boundary

This plan does not make Chamber a runtime substrate.

Chamber remains the human-facing advisory and consent membrane. Lumina runtime remains the governed substrate. The bridge is a translator between them, not a new sovereign lane.

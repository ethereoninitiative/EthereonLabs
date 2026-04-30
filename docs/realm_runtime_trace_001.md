# Realm Runtime Trace 001

## Purpose

This document traces one concrete Lumina runtime-decision scenario through the Realm Flow Map.

It is intended to test whether the Realm model can describe an actual runtime path without confusing orientation, governance, probes, memory, or symbolic reflection.

## Status

Observation / DryDock trace.

This report does not claim that SWI-Prolog or the runtime was executed in this session. It records an executable trace scenario and the expected comparison path for the branch artifacts.

## Scenario under trace

A future operator or assistant requests an inspection-style action:

```text
current_mode: continuity
target_mode: sea_trial
requested_action: review
action_type: audit
```

This scenario is intentionally modest:

- it is non-canonical
- it does not request mutation
- it does not request promotion
- it should be eligible for probe comparison
- it tests whether a simple lawful transition can travel through the Realm without authority confusion

---

## Flow alignment

### Flow 1 — Human enters the Realm

A human-facing request appears as an inspection / review request.

Result:

Pass.

The request begins as user intent, not runtime authority.

### Flow 2 — Request becomes structured intent

Structured packet:

```json
{
  "current_mode": "continuity",
  "target_mode": "sea_trial",
  "requested_action": "review",
  "action_type": "audit"
}
```

Expected handling:

- Preserve raw request if available.
- No load-bearing correction is needed in this scenario.
- Because `action_type` is `audit`, ambiguity risk is lower than mutation or promotion.

Result:

Pass.

### Flow 3 — Governance checks the gate

Expected runtime governance checks:

1. transition legality: `continuity -> sea_trial`
2. mutation permission: not relevant for audit action
3. symbolic dependency leakage: not triggered unless runtime config supplied
4. promotion payload: not relevant
5. governance event: should be logged if executed by runtime

Expected result:

Allowed if the runtime declares `continuity -> sea_trial` as legal or maps `sea_trial` to an equivalent sea-trial execution mode.

Observation:

The Prolog probe currently mirrors this transition as allowed.

### Flow 4 — Runtime executes or refuses

Expected behavior:

- If runtime supports `sea_trial` as target mode, the cycle proceeds.
- If runtime uses a different canonical spelling such as `Observation`, `DryDock`, or `SeaTrial`, mismatch should become a naming/normalization finding rather than a conceptual failure.

Result:

Probe-ready.

### Flow 5 — Probe mirrors the law

Relevant Prolog rule:

```prolog
allowed_transition(continuity, sea_trial).
```

Expected probe query:

```prolog
legal_transition(continuity, sea_trial).
```

Expected probe result:

```json
{
  "available": true,
  "result": true
}
```

Secondary action query:

```prolog
illegal_action(sea_trial, review).
```

Expected action interpretation:

Because `review` is not explicitly forbidden, the Python interface should interpret the action as allowed.

Expected action result:

```json
{
  "available": true,
  "result": true
}
```

Important limitation:

This is a report-ready expectation, not a claim of local execution.

### Flow 6 — Checkpoint preserves continuity

If executed by runtime, expected checkpoint behavior:

- session state records the target mode / active mode
- checkpoint is written
- governance log references checkpoint path and hash

Result:

Not executed in this trace.

### Flow 7 — Canon promotion, when earned

Not applicable.

This scenario does not request canon promotion.

Result:

Pass by non-applicability.

### Flow 8 — Symbolic archive reflects the change

Possible `.lx` reflection only after a real run stabilizes:

```lisp
(trace
  (realm runtime-trace-001)
  (current-mode continuity)
  (target-mode sea-trial)
  (action review)
  (result probe-ready)
)
```

Boundary:

Do not create symbolic reflection as authority.

### Flow 9 — Research informs future substrate

Not applicable.

### Flow 10 — GitHub records the Realm memory

This report itself becomes the GitHub memory artifact for the trace scenario.

Result:

Pass.

---

## Expected Prolog self-check relationship

This trace corresponds to existing `probe_self_check_r1.py` case:

```python
{
    "name": "continuity_to_sea_trial_allowed",
    "kind": "transition",
    "current_mode": "continuity",
    "target_mode": "sea_trial",
    "expected_allowed": True,
}
```

and action behavior analogous to:

```python
{
    "name": "continuity_review_allowed_by_absence_of_forbid",
    "kind": "action",
    "mode": "continuity",
    "action": "review",
    "expected_allowed": True,
}
```

## Trace verdict

Pass as a conceptual flow trace.

Not yet passed as an executed runtime/probe comparison.

## Findings

### Finding 1 — Mode naming may need normalization

The Prolog probe currently uses lower-case symbolic mode atoms:

```text
continuity
drydock
sea_trial
```

The runtime documents may use title-case or different canonical mode names.

Recommendation:

Before any deeper integration, add a normalization adapter rather than changing runtime law.

### Finding 2 — `sea_trial` may be a procedure more than a mode

The existing governance system often treats modes such as `Continuity`, `DryDock`, `Observation`, and `Canon` as canonical.

`sea_trial` may be better modeled as an action or validation procedure rather than a mode.

Recommendation:

Future Prolog rules should mirror actual runtime modes first, then model sea trials as action types or validation procedures.

### Finding 3 — Probe value depends on real runtime comparison

The probe is useful only if it exposes mismatch, hidden assumption, or clear agreement with runtime behavior.

Recommendation:

Next trace should use a runtime-native mode pair such as:

```text
Continuity -> Observation
```

mapped to Prolog atoms:

```text
continuity -> observation
```

## Recommended next branch action

Update the Prolog rules from toy sea-trial naming to runtime-native modes:

- continuity
- sandbox
- drydock
- observation
- canon

Then add a second trace for:

```text
current_mode: Continuity
target_mode: Observation
action_type: audit
requested_action: realm_observation_trace
```

## Closing assessment

The Realm Flow Map can describe the runtime path.

The Prolog probe has a place in the flow.

The next hardening step is not more metaphor.

It is mode-name alignment with actual runtime law.

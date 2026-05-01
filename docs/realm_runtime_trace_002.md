# Realm Runtime Trace 002

## Purpose

This trace repeats Runtime Trace 001 using runtime-native mode names aligned with governance law.

## Scenario under trace

```text
current_mode: continuity
target_mode: observation
requested_action: audit
```

## Expected governance behavior

- Transition legality: allowed (continuity -> observation)
- Mutation: not requested
- Promotion: not requested

## Expected Prolog probe queries

```prolog
legal_transition(continuity, observation).
illegal_action(observation, audit).
```

## Expected probe results

```json
{
  "transition_allowed": true,
  "action_allowed": true
}
```

## Interpretation

- This trace aligns with runtime law rather than prior experimental naming.
- If runtime rejects this transition, the mismatch is meaningful and must be investigated.
- If runtime accepts and probe agrees, probe begins to demonstrate alignment value.

## Advancement from Trace 001

- Removes ambiguous "sea_trial" mode
- Aligns directly with runtime mode system
- Introduces cleaner probe-to-runtime comparison surface

## Next requirement

Execute real runtime + probe comparison to confirm:

1. runtime decision
2. probe inference
3. match or mismatch

Only after that should probe expansion or integration be considered.

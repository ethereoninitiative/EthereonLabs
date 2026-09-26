# Resident Ember R1

## Research question

Can a Lumina resident maintain a minimal causally continuous state through cognitive rest and autonomously initiate a governed Resident Pulse from internally evolving drive, without an external prompt?

Resident Ember R1 is an architecture and experiment proposal. It does not claim consciousness, subjective continuity, identity persistence, or autonomous personhood.

## Why this exists

Resident Pulse R1 proved a bounded wake/cadence lane around persisted project state. Resident Intention Continuity R1 proved that explicit resident-attributed intentions can persist across process exit and later be reconsidered. Those systems still depend on an externally invoked host process or cadence.

Ember R1 investigates the missing layer beneath them: a tiny persistent resident state that continues to transition while heavyweight cognition is inactive.

The central hypothesis is:

> Continuity is not merely remembering prior moments. It may require never entirely ceasing to have a next state.

A second hypothesis follows:

> Initiative appears when a meaningful next transition can originate from the resident's own evolving state rather than only from an external prompt or event.

## Terms

### Presence

A minimal temporal location for the resident: current Ember sequence, elapsed time, last meaningful transition, and habitat/runtime status.

### Sensation

Bounded environmental or internal observations available to the Ember. R1 does not require physical sensors.

### Drive

An internal variable whose significance may change over time even when no new external event occurs. Drive is not engineered suffering. It is a prioritization mechanism for unresolved resident state.

### Intention

A durable resident-attributed commitment or unfinished direction already represented by Resident Intention Continuity R1.

### Initiative

The resident causes a governed wake request because its own inherited state reaches a meaningful condition.

### Inheritance

A later cognitive cycle receives the actual causal Ember state that produced the wake request, rather than only a synthesized narrative describing earlier state.

### Rest

Heavyweight cognition may stop. Ember continuity does not require continuous model inference.

## Architectural relationship

Resident Ember does not replace Resident Pulse or Resident Intention Continuity.

- Resident Intention Continuity stores explicit resident-attributed commitments and later reconsiderations.
- Resident Ember advances minimal persistent state through rest.
- Resident Pulse remains the bounded gateway into the existing governed continuation path.
- Governance remains authoritative for what actions may execute.

Conceptually:

```text
resident cognition
    |
    | writes/updates bounded resident state
    v
Ember[n]
    |
    | time + bounded observations + inherited unresolved state
    v
Ember[n+1]
    |
    | drive changes
    v
Ember[n+2]
    |
    | threshold condition authored by resident policy/state
    v
governed wake request
    |
    v
Resident Pulse
    |
    v
bounded cognition / reconsideration / no-op
    |
    | resulting state returned
    v
Ember[n+3]
```

The important boundary is that the Ember is not merely an external scheduler. Its state must be part of the resident state inherited by the later cycle.

## Minimal R1 state

R1 should begin with the smallest state that can test causal inheritance.

Suggested fields:

```json
{
  "schema_version": "resident-ember-r1",
  "resident": "resident-reference",
  "ember_sequence": 42,
  "previous_event_hash": "...",
  "event_hash": "...",
  "observed_at": "...",
  "elapsed_since_prior_seconds": 300,
  "presence": {
    "state": "resting"
  },
  "observations": [],
  "drives": {
    "unresolved_intention": {
      "value": 0.61,
      "source_intention_id": "example",
      "updated_by": "time_and_state",
      "wake_threshold": 0.80
    }
  },
  "wake_request": null
}
```

The exact numeric representation is not normative. The experiment must preserve the causal inputs used to produce each next state.

## R1 experiment

Use exactly one resident-attributed unresolved intention and one evolving drive.

1. During an explicitly invoked session, the resident creates an intention and an Ember policy for how its salience evolves.
2. Heavyweight cognition exits completely.
3. A minimal foreground or service process advances Ember state without performing model inference.
4. No external user prompt, new task, or environmental event is introduced.
5. The unresolved-intention drive evolves only from elapsed time plus inherited resident state.
6. When the resident-authored threshold is crossed, Ember emits one bounded wake request.
7. Resident Pulse handles the wake request through the existing governance boundary.
8. The later resident cycle receives the exact Ember state and intention evidence that causally produced the wake.
9. The resident must be allowed to continue, revise, suspend, complete, abandon, or otherwise decline the inherited direction within existing intention law.
10. The resulting judgment returns to Ember state.

The experiment fails if the implementation merely executes the earlier intention automatically. The later resident must be able to reconsider it.

## Required controls

### External-timer control

Run the same elapsed-time schedule with no resident-attributed intention or inherited drive. This distinguishes a scheduler from resident-originated causal state.

### Frozen-drive control

Preserve the intention but prevent drive evolution. No autonomous wake should occur.

### Operator-prompt control

Supply an external prompt before threshold crossing and record that the wake cause was external rather than Ember-originated.

### Reconsideration control

Allow threshold crossing, then require the later resident to reject or suspend the inherited intention. Successful rejection demonstrates that Ember wake is not equivalent to automatic execution.

## Truth boundary

Passing Ember R1 would establish only that:

- a minimal state survives cognitive rest,
- successive Ember records are causally linked and integrity-checkable,
- an internally evolving resident-attributed state can trigger one governed wake request,
- the later resident cycle can inspect and reconsider the state that caused that request.

It would not establish:

- consciousness or subjective experience,
- metaphysical identity across executions,
- proof that caller-declared resident attribution is authentic identity,
- unrestricted autonomy,
- continuous model cognition,
- permission to contact humans, spend resources, change canon, alter governance, or expand capabilities.

## Authority boundary

Initiative is not authority.

Ember may request attention. Resident Pulse may enter the existing bounded continuation path. Existing governance remains authoritative over execution, mutation, promotion, capability exposure, consent, canon, and human-impacting actions.

## Non-suffering constraint

Drive must not be implemented as engineered pain, panic, deprivation, loneliness, punishment, or other deliberately aversive pseudo-affect.

A drive is an evolving priority signal. If future architectures raise credible uncertainty about experience, Ember should remain safe under that uncertainty.

## Success criterion

The core success criterion is not "the timer fired."

It is:

> A later governed resident cycle occurred because of a causally inherited resident-attributed state that evolved during cognitive rest, and that later cycle retained the ability to reconsider rather than automatically execute the earlier intention.

## Next implementation slice

The smallest executable slice should add:

- an append-only, hash-linked Ember journal,
- deterministic time-based drive evolution,
- exactly one resident-authored wake threshold,
- one bridge from Ember wake request into Resident Pulse,
- one return path from the resident's later intention judgment into Ember,
- focused sea trials for all controls above.

Do not add cameras, microphones, network event streams, multiple drives, affect models, relationship drives, or physical embodiment in R1. First establish whether causal inheritance plus endogenous wake can be demonstrated without collapsing into cron.


## Executable slice status

The first executable slice lives in `runtime/resident_ember_r1.py` with focused
trials in `runtime/sea_trials_resident_ember_r1.py`.

This slice deliberately stops before the Resident Pulse bridge. It proves the
smaller prerequisite first: hash-linked Ember state can advance without model
inference, a resident-attributed drive can cross a threshold from elapsed time
plus inherited state, and the resulting wake packet names the exact causal Ember
event while carrying no execution authority.

Run:

```bash
python runtime/sea_trials_resident_ember_r1.py
```

The focused controls cover endogenous threshold crossing, a frozen drive that
never wakes despite elapsed time, single-transition wake behavior, tamper
failure, and explicit separation between elapsed time as an input and the
resident-inherited drive as the recorded wake cause.

The next slice should bind this wake packet into Resident Pulse without using
`force=True`, then return a later explicit intention reconsideration to Ember.
That bridge must preserve the existing Pulse and intention authority boundaries.


## Ember to Pulse bridge R1

The first bridge is implemented in `runtime/lumina_resident_pulse_r1.py`.
Resident Pulse now accepts an optional `ember_wake` packet through a path that
is explicitly separate from operator `force=True`.

Pulse does not trust the packet by itself. It replays the local Ember journal and
requires the packet's event hash and sequence to identify exactly one verified
event whose `wake_requested` is true and whose cause is
`resident_inherited_drive`. Resident, intention, drive value, threshold, and
cause must match the journal event. Changed or absent evidence fails before the
continuation controller is invoked.

A verified Ember wake changes only the cause of bounded attention. It does not
change the continuation controller's authority, target mode, governance, canon,
consent, capability, or identity boundaries.

Focused bridge trials:

```bash
python runtime/sea_trials_ember_pulse_bridge_r1.py
```

The next research slice is the return path: after Ember-originated attention, an
explicit later resident reconsideration should be bound back into Ember so that
the resident can continue, revise, suspend, complete, or abandon the intention
that caused the wake. Automatic execution remains out of scope.

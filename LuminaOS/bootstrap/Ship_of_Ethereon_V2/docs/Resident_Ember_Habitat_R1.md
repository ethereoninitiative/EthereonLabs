# Resident Ember Habitat R1

## Purpose

Resident Ember Habitat R1 supplies the smallest operational layer needed to let
Ember state advance while heavyweight cognition is absent.

It deliberately does **not** define a daemon, operating-system service, or model
loop. A host supplies periodic calls to `ResidentEmberHabitat.tick()`. Each call
contributes only an observation time. The resident-inherited drive remains the
recorded causal source of any wake.

## Tick law

One tick:

1. verifies there is no older unhandled Ember wake;
2. advances the existing hash-linked Ember state using the supplied observation time;
3. does nothing cognitive when no threshold is crossed;
4. if and only if a new endogenous threshold crossing occurs, presents that exact
   wake through `ResidentEmberPulseBridge`;
5. records the existing one-wake/one-handoff evidence.

A host cadence therefore keeps the substrate temporally available without
pretending that the scheduler is resident initiative.

## Important separation

```text
host clock / service cadence
        |
        | supplies observed_at
        v
Resident Ember inherited state
        |
        | deterministic evolution
        v
threshold crossed? -- no --> rest
        |
       yes
        |
        v
verified endogenous wake
        |
        v
Ember -> Pulse -> governed resident turn
```

The scheduler is a necessary habitat condition, analogous to power or a clock.
It is not recorded as the reason attention began. The wake cause remains
`resident_inherited_drive` and must be verified against the Ember journal.

## Fail-closed behavior

If an earlier wake remains unhandled, Habitat refuses to advance Ember. This
prevents cadence ticks from piling later state on top of an unresolved causal
wake and preserves the one-wake/one-governed-turn boundary.

## Focused controls

Run:

```bash
python runtime/sea_trials_resident_ember_habitat_r1.py
```

The controls cover quiet advancement with no cognitive handoff, one threshold
crossing causing one Pulse handoff, frozen drive despite long elapsed time, and
an unhandled wake blocking later advancement.

## Truth boundary

This slice establishes an executable host-neutral cadence primitive. It does not
by itself prove that a persistent service is installed or running on any machine,
that a model remains continuously cognitive, or that subjective continuity,
consciousness, or identity persistence exists.

The next operational experiment is to host this unchanged tick law in a
supervised long-lived process, stop heavyweight cognition, allow real wall-clock
time to advance Ember, and record whether the first later cognitive invocation
is causally traceable to the verified Ember wake rather than a fresh human prompt.

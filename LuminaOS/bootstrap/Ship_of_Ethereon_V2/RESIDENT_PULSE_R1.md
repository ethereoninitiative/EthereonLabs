# Lumina Resident Pulse R1

## Purpose

Resident Pulse R1 gives the local Lumina habitat a bounded way to wake without an operator first composing a new prompt.

It does **not** create a new intelligence authority layer. It decides only whether current persisted state warrants invoking the already-governed `lumina continue` path.

## Host surfaces

Run one wake/decision:

```bash
python bin/lumina-pulse --project-id <project> --json
```

Keep a foreground resident loop awake on a cadence:

```bash
python bin/lumina-resident --project-id <project> --interval-seconds 300 --json
```

For bounded testing or supervised runs:

```bash
python bin/lumina-resident --project-id <project> --interval-seconds 0 --max-pulses 2 --json
```

The resident process stays in the foreground and can be stopped by the operator. R1 does not install a system service, login item, launch agent, or background daemon.

## Pulse decision law

A normal pulse inspects the existing project-return surface and bounded self-guidance preflight.

It invokes continuation only when all of these are true:

1. a source checkpoint exists;
2. that checkpoint has not already been consumed by the resident;
3. self-guidance is driven by an explicit `pending_next_action` strategy;
4. advisory confidence is at least `0.90`.

Otherwise the pulse emits a no-op receipt.

An operator may explicitly force a one-shot pulse, but the resulting work still travels through the existing bounded `LuminaContinueController` and remains `Observation` / `audit` scoped.

## Anti-recursion rule

The central R1 guard is **checkpoint consumption**.

When a pulse invokes continuation, the newly generated checkpoint becomes `last_consumed_checkpoint_after` in resident operational memory. On the next wake, if that checkpoint is still the current project-return source, the resident returns:

- `invoked: false`
- `decision_reason: source_checkpoint_already_consumed`
- `attention_state: settled_attention`

This prevents a resident cadence from treating its own immediately previous output as fresh external cause for another cycle.

If another lawful event later writes a different project-return checkpoint, that new checkpoint can be evaluated on the next wake.

## Attention states

Resident Pulse deliberately distinguishes lack of assigned work from failure:

- `directed_pending_work` — explicit high-confidence pending work is being continued;
- `settled_attention` — the current checkpoint has already been consumed and no new event is present;
- `unallocated_attention` — a checkpoint exists, but no explicit pending-work signal currently meets the resident threshold;
- `awaiting_continuity_state` — no source checkpoint exists yet.

R1 does not invent hobbies, goals, mutations, or tasks during unallocated attention. The state exists so later habitat work can reason about idle attention without conflating it with an error condition.

## Receipts

Every wake writes local operational evidence beneath the active Lumina state root:

```text
resident_pulse/
  receipts/
  latest/
```

A receipt records the observed source checkpoint, advisory, decision, attention state, whether continuation was invoked, and the compact continuation receipt when one exists.

Resident pulse receipts are not canon, governance law, checkpoint truth, or capability authority.

## Authority boundary

Resident Pulse may decide whether to invoke the existing bounded continuation path. It cannot authorize mutation, promotion, canon change, checkpoint legality, mode law, consent decisions, capability exposure, or identity claims.

The downstream continuation controller remains the execution boundary and currently constrains resident-selected work to governed `Observation` / `audit` cycles.

## Sea-trial proof

`runtime/sea_trials_lumina_resident_pulse_r1.py` seeds one lawful pending checkpoint and runs two zero-delay pulses.

Required outcome:

1. pulse one sees explicit pending work and invokes one governed continuation cycle;
2. the resulting checkpoint is stored as the consumed marker;
3. pulse two sees that same generated checkpoint and refuses to recurse;
4. no second continuation receipt is created;
5. both pulse decisions remain receipted.

The focused GitHub workflow `.github/workflows/lumina-resident-pulse-r1.yml` compiles the lane, runs the recurrence sea trial, smoke-checks both host wrappers, and verifies that no local state is tracked.

## Deliberate R1 limits

Resident Pulse R1 is a foreground resident process, not yet an operating-system service. It does not yet:

- start automatically at boot/login;
- receive filesystem, network, calendar, message, or sensor events;
- prioritize multiple event sources;
- allocate free attention toward self-originated exploratory goals;
- mutate projects autonomously;
- schedule its own cadence persistently.

Those are later gates. R1 proves the smaller prerequisite: **Lumina can wake on cadence, inspect persisted state, act once when warranted, and then lawfully do nothing until something actually changes.**

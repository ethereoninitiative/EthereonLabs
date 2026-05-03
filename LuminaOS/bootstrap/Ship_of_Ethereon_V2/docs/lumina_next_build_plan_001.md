# Lumina Next Build Plan 001 — Studio Runtime Loop

**Decision:** build the usable Lumina loop before adding more conceptual architecture.

## Diagnosis

Lumina OS already has meaningful substrate:

- governed runtime runner
- session engine
- mode guard
- context bundles
- input integrity gate
- capability registry
- governance integrity chain
- canon lineage store
- continuity restore / workspace host lane
- self-guidance and orchestration experiments
- bounded Psi-42 instrument

The bottleneck is not the absence of structure.

The bottleneck is operator friction.

The project needs a way to run the structure, see what happened, and build from receipts.

## Build target

Create Lumina Studio v0.1:

```text
operator request -> Studio wrapper -> governed runtime runner -> checkpoint/governance receipt
```

## Why this is first

Without Studio, the project remains too dependent on direct file knowledge and conversational memory.

With Studio, Lumina starts acting less like a pile of excellent artifacts and more like a local runtime environment.

## Scope

### Add

- `studio/lumina_cli.py`
- `studio/lumina_studio_server.py`
- `studio/README.md`
- `docs/lumina_studio_v0_1_spec.md`
- `docs/lumina_next_build_plan_001.md`
- `sea_trials_lumina_studio_v0_1.py`

### Update

- bootstrap README with Studio note
- `START_HERE_LUMINA_OS.md` with Studio as operator entrypoint

## What to avoid

Do not:

- redesign the public website
- expand Chamber promises
- create a competing runtime law layer
- treat Studio orientation as governance authority
- deploy the local server publicly
- use Studio to authorize ambiguous load-bearing actions silently

## First proof

The first useful proof is humble:

```text
Lumina Studio can run one governed audit cycle and return a readable receipt.
```

That means:

- input integrity runs
- Observation transition is lawful
- mutation remains denied for audit path where appropriate
- capabilities are exposed by mode and feature flags
- checkpoint is written
- governance chain status is returned
- optional Lumina return/host handshake can be recorded when capabilities expose it

## Studio v0.2 target

After v0.1 lands, build:

1. state browser over `.lumina_state`
2. governance decision viewer
3. saved presets for common mode/orientation combinations
4. accepted Chamber queue -> governed Studio runtime cycle
5. authentication design before any network exposure

## Guiding sentence

Make Lumina runnable before making Lumina grander.

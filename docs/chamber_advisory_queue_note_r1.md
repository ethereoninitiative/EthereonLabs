# Chamber advisory acceptance and supervised action queue note r1

This note records the next bridge between bounded Lumina self-guidance and user-visible Chamber interaction.

## What this scaffold adds

New files:

- `chamber-app/src/advisory_queue_types.ts`
- `chamber-app/src/advisory_queue_memory_store.ts`
- `chamber-app/src/advisory_queue_server_v0_1.ts`

## What it does

This scaffold introduces a minimal public-room flow where a human can:

1. create an advisory recommendation
2. accept or reject that recommendation explicitly
3. place accepted recommendations into a supervised action queue
4. claim and complete queued actions as visible, bounded steps

## Why this matters

The current Lumina bootstrap path already supports bounded self-guidance advisory output.
What it did not yet have was a simple user-visible acceptance / rejection loop and a supervised queue surface that makes consent legible.

This Chamber scaffold is not hidden autonomy.
It is the opposite.
It makes recommendation, decision, and queued action separable and inspectable.

## Current boundary

This first scaffold is intentionally narrow:

- queue persistence is in-memory only for now
- it runs as a parallel server entrypoint rather than replacing the main Chamber server
- it does not execute tools itself
- queue completion is a human-marked supervision event, not autonomous tool execution

## Why this shape

That narrowness is on purpose.
The goal is to prove the behavioral pattern first:

- recommendation
- explicit user decision
- supervised queue placement
- visible claim / completion state

before deeper integration with Postgres, Chamber UI, or governed runtime execution.

## Likely next hardening move

After this, the sharp next step is to connect the same advisory / queue pattern to:

- persisted Postgres storage
- Chamber UI surfaces
- Lumina-produced advisory objects
- governed runtime execution records

without allowing queued actions to bypass governance or user intent.

## Manual run note

This server is designed to be run directly with `tsx`, for example:

`tsx watch src/advisory_queue_server_v0_1.ts`

from inside `chamber-app/`.

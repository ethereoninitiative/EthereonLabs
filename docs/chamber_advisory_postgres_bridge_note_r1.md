# Chamber advisory persistence and Lumina bridge note r1

This note records the next hardening step after the first advisory acceptance / rejection scaffold.

## What this adds

New files:

- `chamber_advisory_queue_extension_r1.sql`
- `chamber-app/docker-compose.postgres.advisory.yml`
- `chamber-app/src/advisory_queue_store_contract.ts`
- `chamber-app/src/advisory_queue_memory_store_v0_2.ts`
- `chamber-app/src/advisory_queue_postgres_store_r1.ts`
- `chamber-app/src/advisory_queue_store_factory_r1.ts`
- `chamber-app/src/advisory_queue_server_v0_2.ts`
- `chamber-app/src/lumina_advisory_bridge_r1.ts`
- `chamber-app/src/sea_trials_lumina_advisory_bridge_r1.ts`

## What this changes in practice

The advisory loop is no longer trapped in memory-only design.
This hardening step introduces:

1. a Postgres-backed advisory and supervised action queue store
2. a parallel advisory server entrypoint that can use memory or Postgres mode
3. a local compose lane that mounts the advisory queue SQL extension
4. a first bridge mapper from Lumina advisory summary objects into Chamber advisory payloads

## Why this matters

The first scaffold proved the behavioral pattern:

- recommendation
- explicit acceptance / rejection
- supervised queue placement
- visible claim / completion

This step makes the same loop more durable and more aligned with the Lumina substrate.
It moves the Chamber closer to becoming a real consent surface for bounded self-guidance.

## Boundary note

This still does not grant hidden execution authority.

The bridge only maps Lumina advisory summaries into Chamber-shaped payloads.
The queue still records supervised state transitions.
Tool execution and runtime governance remain separate concerns.

## Likely next move after this

After persistence and bridge-shaping, the sharp next threshold is to have real Lumina advisory output posted into the Chamber path intentionally, then let accepted queue items emit governed runtime execution records rather than remaining only social-state objects.

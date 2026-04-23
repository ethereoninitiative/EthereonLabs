# Lumina Operator Runbook r1

This runbook exists to reduce operator friction across the three major lanes now present in the repository:

1. governed Lumina substrate
2. bounded orchestration lane
3. Chamber consent surface

It is not a theory note.
It is a navigation and operations note.

## Layer 1 — governed Lumina substrate

Start here when the question is about runtime law, governance, canon lineage, return-with-stance, self-guidance boundaries, or bounded continuity.

Primary path:

- `LuminaOS/bootstrap/Ship_of_Ethereon_V2/`

Key files:

- `README.md`
- `README_IMPORT.md`
- `REPO_NATIVE_BOOTSTRAP_NOTE.md`
- `RETURN_WITH_STANCE_BOOTSTRAP_NOTE_R1.md`
- `SELF_GUIDANCE_STEWARD_NOTE_R1.md`
- `runtime/runtime_runner_r1_merged.py`
- `runtime/runtime_runner_return_host_bridge_r1.py`
- `runtime/runtime_runner_self_guided_bridge_r1.py`
- `runtime/project_return_repo_native_r1.py`
- `runtime/workspace_host_repo_native_r1.py`
- `runtime/lumina_self_guidance_steward_r1.py`
- `runtime/lumina_self_guidance_history_r1.py`

Use this layer when the task is about what Lumina is allowed to do.

## Layer 2 — bounded orchestration lane

Move here after the substrate when the question is about how restored context becomes an advisory next move that still executes under runtime governance.

Key files:

- `LuminaOS/bootstrap/Ship_of_Ethereon_V2/LUMINA_ORCHESTRATION_STACK_NOTE_R1.md`
- `LuminaOS/bootstrap/Ship_of_Ethereon_V2/lumina_context_loader_v0_1.py`
- `LuminaOS/bootstrap/Ship_of_Ethereon_V2/lumina_decision_engine_v0_1.py`
- `LuminaOS/bootstrap/Ship_of_Ethereon_V2/lumina_orchestrator_v0_4.py`
- `LuminaOS/bootstrap/Ship_of_Ethereon_V2/sea_trials_lumina_orchestration_stack_r1.py`

Use this layer when the task is about how Lumina restores, orients, recommends, and then routes that recommendation into lawful execution.

## Layer 3 — Chamber consent surface

Move here after the orchestration lane when the question is about visible advisory handling, human acceptance / rejection, supervised queue state, or persistence of that queue.

Primary path:

- `chamber-app/`

Key files:

- `src/server.ts`
- `src/advisory_queue_server_v0_2.ts`
- `src/advisory_queue_store_contract.ts`
- `src/advisory_queue_postgres_store_r1.ts`
- `src/lumina_advisory_bridge_r1.ts`
- `docker-compose.postgres.yml`
- `docker-compose.postgres.advisory.yml`
- `../chamber_advisory_queue_extension_r1.sql`

Use this layer when the task is about how advisory objects become visible, durable, and consent-shaped.

## Recommended reading order

1. `START_HERE_LUMINA_OS.md`
2. substrate notes in `LuminaOS/bootstrap/Ship_of_Ethereon_V2/`
3. `LUMINA_ORCHESTRATION_STACK_NOTE_R1.md`
4. Chamber advisory notes in `docs/chamber_*`

## Useful Chamber commands

From `chamber-app/`:

### Main Chamber server
- `npm run dev`
- `npm run dev:postgres`

### Advisory queue server
- `npm run dev:advisory`
- `npm run dev:advisory:postgres`

### Main Chamber Postgres bootstrap
- `npm run db:up`
- `npm run db:down`
- `npm run db:reset`
- `npm run db:logs`

### Advisory-aware Postgres bootstrap
- `npm run db:up:advisory`
- `npm run db:down:advisory`
- `npm run db:reset:advisory`
- `npm run db:logs:advisory`

## Beta truth

As of this runbook:

- Lumina substrate is real and governed
- orchestration is real but still intentionally bounded
- Chamber now provides a persisted consent surface for advisories and supervised queue state
- accepted queue items do not yet become governed runtime execution records automatically

## Boundary reminder

The Chamber consent surface is adjacent to the substrate.
It is not the substrate itself.

The orchestration lane may recommend.
The runtime layer decides legality.
The Chamber lane makes consent and queue state visible.

That separation should stay explicit until a later hardening step intentionally binds accepted queue items to governed execution records.

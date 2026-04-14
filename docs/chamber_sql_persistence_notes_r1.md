# Chamber SQL Persistence Notes r1

## Purpose
This note explains the first durable persistence path for the Chamber app scaffold.

The immediate goal is to let the Chamber backend run in either:
- `memory` mode for fast local development
- `postgres` mode for durable shared room persistence

## Why this matters
The Chamber shell, app scaffold, and shell-to-backend bridge already exist.
What they still need is durable state.

In-memory persistence is useful for:
- local development
- fast iteration
- simple integration checks

It is not sufficient for:
- returning users after restart
- durable shared room history
- durable auth sessions
- credible public room continuity

## What this pass adds
- a Chamber store contract
- an async memory store that implements that contract
- a Postgres store scaffold that implements the same contract
- a store factory chosen by `CHAMBER_STORE_MODE`
- a session-table SQL extension for persistent sessions

## Store modes
### Memory
- no database required
- state resets on restart
- fastest local setup

### Postgres
- requires `DATABASE_URL`
- stores users, sessions, room messages, attached roles, and synthesis-backed round data in SQL-backed tables
- is the first credible persistence path for shared Chamber use

## Recommended migration order
1. merge the dual-store app changes
2. stand up a Postgres database
3. apply `chamber_data_model_r1.sql`
4. apply `chamber_sessions_extension_r1.sql`
5. set `CHAMBER_STORE_MODE=postgres`
6. set `DATABASE_URL`
7. verify signup, session restore, role updates, message load, and post-round flow

## Design note
This pass keeps the orchestration simple and stable.
It does not yet introduce:
- provider-backed multibot routing
- multi-room sprawl
- advanced moderation flows
- profile systems

It focuses on one thing: make the shared room durable.

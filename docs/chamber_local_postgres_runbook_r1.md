# Chamber Local Postgres Runbook r1

## Purpose
This runbook gives Chamber a repeatable local SQL-mode path.

The immediate goal is to make it easy to:
- start a local Postgres instance
- let the schema initialize automatically
- run the Chamber app in `postgres` mode
- verify that the live shell can talk to durable shared state

## Files involved
- `chamber-app/docker-compose.postgres.yml`
- `chamber-app/.env.postgres.example`
- `chamber_data_model_r1.sql`
- `chamber_sessions_extension_r1.sql`

## First-time setup
From `chamber-app/`:

```bash
docker compose -f docker-compose.postgres.yml up -d
```

This does three things:
- starts Postgres locally
- creates the `chamber` database
- applies the Chamber schema and session extension on first initialization

## Backend environment
Copy the Postgres example env into place:

```bash
cp .env.postgres.example .env
```

That sets:
- `CHAMBER_STORE_MODE=postgres`
- `DATABASE_URL=postgres://chamber:chamber@localhost:5432/chamber`

## Run the Chamber backend in SQL mode
```bash
npm install
npm run dev:postgres
```

## Verify health
```bash
curl http://localhost:8787/health
```

The returned health payload should report:
- `service: chamber-app-scaffold`
- `storeMode: postgres`

## Verify shell connection
Once the backend is running:
- open the Chamber page
- ensure the client is configured to point at the backend
- sign up with email + chamber handle
- post a message
- refresh and confirm the message history remains

## Expected persistence checks
The following should survive backend restarts when Postgres remains up:
- users
- sessions that are still valid
- attached role preferences
- room history
- synthesis-backed rounds

## Stop the local database
```bash
docker compose -f docker-compose.postgres.yml down
```

## Reset the local database volume completely
```bash
docker compose -f docker-compose.postgres.yml down -v
```

That removes the stored Chamber Postgres volume and causes the init SQL files to run again on next startup.

## Why this matters
This is the first local path where Chamber becomes durably shared rather than merely lively for one process lifetime.

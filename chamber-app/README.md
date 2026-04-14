# Chamber App Scaffold r1

This directory is the first actual backend scaffold for auth and shared room persistence behind the public Chamber shell.

## Status
Scaffold only, now with switchable persistence modes and a local Postgres bootstrap lane.

It is intended to do four things now:
- create a narrow backend lane for light account behavior
- provide one shared public room
- provide a posting surface that returns a full round payload with ordered role replies and synthesis
- allow the backend to run in either memory mode or Postgres mode

It is **not** yet a production backend.

## What is included
- Express + TypeScript server
- light account signup
- light login
- session lookup by token
- attached AI role updates per user
- one public room endpoint
- shared message history endpoint
- post-to-room endpoint that returns:
  - human post
  - role replies in order
  - synthesis
- switchable store factory
- memory store
- Postgres store scaffold
- local Docker Compose Postgres path

## Persistence modes
### Memory
- no database required
- resets on restart
- best for quick local iteration

### Postgres
- requires `DATABASE_URL`
- persists users, sessions, room messages, role attachments, and synthesis-backed room history
- is the first durable path for shared Chamber use

## Local Postgres quick path
From `chamber-app/`:

```bash
npm install
npm run db:up
cp .env.postgres.example .env
npm run dev:postgres
```

Useful database helpers:
- `npm run db:up`
- `npm run db:down`
- `npm run db:reset`
- `npm run db:logs`

## Current durable path
The durable route is:
- apply `../chamber_data_model_r1.sql`
- apply `../chamber_sessions_extension_r1.sql`
- run the app with `CHAMBER_STORE_MODE=postgres`

The Docker Compose lane does this automatically on first initialization.

## Environment
Copy `.env.example` to `.env` for memory mode.
Copy `.env.postgres.example` to `.env` for local Postgres mode.

Important values:
- `CHAMBER_STORE_MODE=memory|postgres`
- `DATABASE_URL=...` when using Postgres

## Run
```bash
cd chamber-app
npm install
npm run dev
```

Default server:
- `http://localhost:8787`

## Endpoints
### Health
- `GET /health`

### Auth
- `POST /api/auth/signup`
- `POST /api/auth/login`
- `GET /api/auth/session/:sessionToken`
- `PATCH /api/auth/session/:sessionToken/roles`

### Room
- `GET /api/rooms/public-room-one`
- `GET /api/rooms/public-room-one/messages`
- `POST /api/rooms/public-room-one/messages`

## Example signup payload
```json
{
  "email": "you@example.com",
  "displayName": "Spencer",
  "chamberHandle": "ArchitectOfResonance"
}
```

## Example post payload
```json
{
  "sessionToken": "<uuid>",
  "body": "What should the next Chamber layer become?"
}
```

## Design note
This scaffold is deliberately narrow.
It exists to make the Chamber shared and account-backed before chasing multi-room sprawl or provider-diverse multibot routing.

The next quality threshold after this pass is not more conceptual expansion.
It is verifying the Postgres mode end-to-end against the live Chamber shell.

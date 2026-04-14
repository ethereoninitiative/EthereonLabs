# Chamber App Scaffold r1

This directory is the first actual backend scaffold for auth and shared room persistence behind the public Chamber shell.

## Status
Scaffold only.

It is intended to do three things now:
- create a narrow backend lane for light account behavior
- provide one shared public room
- provide a posting surface that returns a full round payload with ordered role replies and synthesis

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

## Current persistence model
This scaffold uses an in-memory store.

That means:
- data resets on server restart
- sessions reset on server restart
- it is useful for implementation flow, not production durability

The next layer is to replace the memory store with the SQL schema in `../chamber_data_model_r1.sql`.

## Environment
Copy `.env.example` to `.env` and adjust if needed.

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

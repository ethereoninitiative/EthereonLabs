# Lumina Appliance Environment Reference r1

This note documents the host-local environment values expected by the current Ubuntu Server appliance scaffold.

## Expected file path

Suggested host path:

- `/etc/lumina/lumina-appliance.env`

## Current variables

### Chamber consent surface
- `CHAMBER_PUBLIC_ROOM_SLUG`
  - default public room slug for Chamber endpoints
- `SESSION_TTL_HOURS`
  - session lifetime for Chamber auth
- `CHAMBER_ALLOWED_ORIGINS`
  - comma-separated origin allowlist
- `CHAMBER_STORE_MODE`
  - `memory` or `postgres`
- `CHAMBER_ADVISORY_PORT`
  - advisory queue service port
- `DATABASE_URL`
  - Postgres connection string for Chamber durable mode

### Appliance runtime
- `PYTHONUNBUFFERED`
  - keeps Python logs flushed promptly in service mode

## Recommended host-local additions

These are not all consumed directly by the current code yet, but they are useful for standardizing appliance layout:

- `LUMINA_ROOT`
- `LUMINA_STATE_ROOT`
- `LUMINA_LOG_ROOT`
- `LUMINA_REPO_USER`

## Operator note

Do not commit real host secrets into the repository.
This file exists so the scaffold has a human-readable contract for what belongs in the host-local environment file.

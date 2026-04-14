# Chamber Deployment Notes r1

## Purpose
This note defines the first clean deployment path for the Chamber shell and the Chamber app scaffold.

The immediate goal is simple:
- keep the public Chamber shell live on the site
- point it explicitly at a real backend when one is deployed
- avoid relying only on backend auto-detection in production

## Current reality
The public Chamber page can already:
- run as a local specimen
- detect a live Chamber backend when one is reachable
- fall back gracefully when no backend is available

That behavior is useful during development.
Production should be more explicit.

## Client-side config hook
The Chamber shell now has a dedicated client config file:
- `assets/js/chamber_config.js`

It should set:
- `window.CHAMBER_API_BASE`

### Example
```js
window.CHAMBER_API_BASE = 'https://your-chamber-api.example.com';
```

## Why this exists
This makes production behavior clearer.
The shell does not have to guess the backend origin first.
It can still keep fallback behavior, but production should prefer explicit configuration.

## Chamber app scaffold deployment notes
The backend scaffold currently runs as a small Express + TypeScript app.
It still uses in-memory persistence.

That means it is suitable for:
- local development
- integration testing
- first deployment wiring

It is not yet durable production storage.

## Minimum environment for the backend
- `PORT`
- `CHAMBER_PUBLIC_ROOM_SLUG`
- `SESSION_TTL_HOURS`
- `CHAMBER_ALLOWED_ORIGINS`

### Example allowed origins
- local dev shell origin
- local backend origin
- `https://ethereonlabs.com`

## Recommended immediate deployment sequence
1. deploy the Chamber app scaffold behind a stable origin
2. set `CHAMBER_ALLOWED_ORIGINS` to include the public site
3. set `window.CHAMBER_API_BASE` in `assets/js/chamber_config.js`
4. verify signup, session restore, role sync, shared message load, and post-round flow
5. only after that, swap the memory store toward SQL-backed persistence

## Next durable step after deployment wiring
The next architectural move should be:
- replace the in-memory store with a store backed by `chamber_data_model_r1.sql`

That is the real shift from integration scaffold to durable shared room.

## Success condition
This deployment pass is successful when:
- the public Chamber page connects to the real backend without guessing
- users can sign up and return through the shared room flow
- the shell still degrades gracefully if the backend is temporarily unavailable

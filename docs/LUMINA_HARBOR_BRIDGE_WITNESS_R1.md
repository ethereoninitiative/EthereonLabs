# Lumina Harbor ↔ Bridge Runtime Witness R1

**Status:** implementation contract
**Scope:** optional read-only connection from the browser Harbor to a local Lumina Bridge.

## What this adds

The Harbor can now remain useful in browser-local mode while optionally reading one current observation from the local Bridge. The observation may include project, Harbor session, current mode, runtime status, latest action, truth alignment, governance status, and canon head.

The browser does not send credentials, provider information, prompts, POST requests, or mutation requests. It uses `GET /api/bridge` only.

## Start the local Bridge

From the repository root:

```bash
cd LuminaOS/bootstrap/Ship_of_Ethereon_V2
python bin/lumina-bridge
```

The default local endpoint is:

`http://127.0.0.1:8766/api/bridge`

Open the Harbor and choose **Connect local Lumina**. If the Bridge is not running, the Harbor remains in local-only mode and displays a non-fatal disconnected state.

## Origin boundary

The Bridge binds to loopback by default. CORS permits the production Harbor origin `https://app.ethereonlabs.com` and HTTP localhost origins for local development. Additional exact origins may be supplied with:

```bash
LUMINA_BRIDGE_ALLOWED_ORIGINS=https://app.ethereonlabs.com,http://localhost:3000 python bin/lumina-bridge
```

CORS is not authentication. The Bridge remains a read-only orientation surface and must not be exposed beyond a trusted local host without a separate security design.

## Truth and authority boundary

Bridge observations do not create, replace, or override committed governance or canon evidence. Harbor displays the observation as a witness and labels unavailable or misaligned state for inspection.

The executable path remains:

```text
request → govern → execute or refuse → receipt → resumable state
```

Bridge and Harbor orient. Lumina Studio requests. The governed runtime decides.

## Validation

The browser boundary sea trial is:

`LuminaOS/bootstrap/Ship_of_Ethereon_V2/studio/sea_trials_lumina_bridge_browser_boundary_r1.py`

It verifies approved origins, localhost development, unknown-origin rejection, OPTIONS behavior, and POST rejection.

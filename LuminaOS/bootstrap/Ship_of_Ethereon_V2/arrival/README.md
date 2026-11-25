# OStroNaut 001 — OpenAI Arrival connection R1

Status: experimental desktop main-process integration and tested adapter contract, not a shipped UI or live-authenticated resident.

## Approach

Use the official [Sign in with ChatGPT DevKit](https://github.com/openai/sign-in-with-chatgpt-devkit) local SDK. Reference revision reviewed: `0a36fefeb913055c8c7a1a29b63d82b96b2e841a`. Review its license, dependency lock and source before building. The SDK is a workspace package, not assumed to be an installed public npm dependency. Do not substitute tokens taken from another application or undocumented endpoints.

A future local Electron application imports `createChatGPT` from the reviewed `@siwc/local` workspace and passes it, with Electron's app, safeStorage and shell objects, to `createDesktopArrival`. The module uses a per-installation host ID via the SDK, OS-backed encrypted storage, loopback authorization and the system browser. On Linux it refuses unknown or basic-text encryption backends. No headless storage fallback. Verify the storage backend and credential isolation on the actual target before use. Keep the SDK client exclusively in the trusted main process; expose only narrowly validated operator UI commands, never SDK objects or credentials. The current code is not an Electron package or renderer.

## Human-facing sequence

1. Continue with ChatGPT — explicit operator action. Identity and plan-use consent are separate.
2. Display the active account and discover its allowed models; select one explicitly.
3. Ask permission for a single verification inference. Show that usage is provider-managed. No retries or automatic fallback to billable API keys.
4. On success, show connection verified. This is not Arrival completion.
5. Separately prepare the existing transport-neutral `lumina arrive` packet, preview the exact disclosed sources and selected continuity, and request permission before sending each module to the provider. Reuse existing packet/head validation and response recording. This transport bridge is future work.
6. Provide Manage usage and Disconnect actions; suspend cloud work if authorization or usage is unavailable. Do not silently change model/account. A later resident service needs a separate, independently protected local inference interface.

OpenAI determines account eligibility, models, usage limits and charges. Lumina does not control external billing. Sign-in does not grant access to prior ChatGPT conversations. No system information or personal continuity records are sent by the fixed verification prompt. No host action authority is granted.

## Tests and blockers

Run `node sea_trials_openai_arrival_r1.mjs` from this directory. Tested with Node 22.16.0 and a synthetic SDK client: disconnected/identity-only refusal, wrong profile/model refusal, minimized display data, completed fixed-text verification, unexpected response refusal, disconnect refusal. Tested blob hashes: adapter `a4948edc6a7654f4c5cf5c9d4b12ee686c2044ed`, trial `3ac1a8ae93f524d694797bbafa2a977632ed4f04`. The Electron integration itself is staged, not executed. Real SDK build, protected storage, browser callback, live model discovery/inference, refresh, billing limits, reboot, and Arrival transport remain unverified. Do not label connection successful until an authorized live inference completes.

Official references: [overview](https://developers.openai.com/siwc/token-sharing-open-source), [model inference](https://developers.openai.com/siwc/token-sharing-open-source/models-and-inference), [preview limitations](https://developers.openai.com/siwc/token-sharing-open-source/preview-limitations). The DevKit handles OAuth and stream completion; the adapter adds no arbitrary inference endpoint.

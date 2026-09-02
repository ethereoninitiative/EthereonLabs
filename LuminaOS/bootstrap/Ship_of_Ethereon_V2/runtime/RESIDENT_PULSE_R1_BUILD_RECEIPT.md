# Resident Pulse R1 Build Receipt

- Base branch: `main`
- Base SHA: `e3dc37c48d5e1c15bd7d88bfe46f32f2819c6198`
- Build branch: `build/lumina-resident-pulse-r1`
- Scope: additive resident wake/cadence lane only

## Implemented

- one-shot resident pulse decision runtime
- checkpoint-consumption anti-recursion guard
- explicit attention states including unallocated and settled attention
- foreground cadence loop
- host wrappers for one-shot and resident execution
- two-pulse recurrence sea trial
- focused GitHub Actions validation workflow
- operator/runtime documentation

## Boundary

Resident Pulse can decide only whether to invoke the already-governed bounded continuation controller. It gains no mutation, promotion, canon, checkpoint-legality, mode-law, consent, capability, or identity authority.

## Intended proof

A seeded pending checkpoint should cause exactly one resident continuation. The resulting checkpoint must then be recognized as already consumed, causing the immediately following pulse to emit a receipted no-op rather than recursively continuing its own output.

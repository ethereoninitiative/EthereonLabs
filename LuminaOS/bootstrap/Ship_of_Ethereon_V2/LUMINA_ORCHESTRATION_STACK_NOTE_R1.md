# Lumina Orchestration Stack Note r1

This note records the current bounded orchestration lane that sits above the governed bootstrap runtime.

## Stack shape

The current stack now has four distinct layers:

1. `runtime/runtime_runner_r1_merged.py`
   - lawful execution substrate
   - mode validation
   - mutation / promotion gating
   - capability exposure
   - governance logging

2. `lumina_context_loader_v0_1.py`
   - recovers minimal usable context from the latest checkpoint
   - restores `current_mode` and `last_action` without guessing beyond the available state

3. `lumina_decision_engine_v0_1.py`
   - emits an advisory next-step recommendation from restored context
   - remains non-authoritative
   - emits only RuntimeRunner-supported action types: `transition`, `mutation`, `promotion`, or `audit`

4. `lumina_orchestrator_v0_4.py`
   - binds the runner, loader, and decision engine into one bounded orchestration loop
   - attaches the loader to the runner's actual runtime state directory
   - routes the recommended action into runtime execution without granting the recommendation governance authority

## Why this matters

This lane is the first compact proof that Lumina can:

- restore a minimal project surface
- orient from that surface
- recommend a likely next move
- execute through the governed runtime rather than replacing it

That is not the positronic brain.
But it is aligned with the compass that points toward durable, lawful cognition.

## Current truth

The orchestration layer is still intentionally narrow.
It does not yet provide:

- rich multi-project context fusion
- user-visible advisory acceptance / rejection loops
- supervised action queues
- durable external process continuity
- independent tool arbitration beyond the governed runtime boundary

It now includes a dedicated validation lane:

- `sea_trials_lumina_orchestration_continuity_r1.py`

That trial suite checks the first operational form of the project mantra:

> continuity of pattern is recoverable coherence across change

## Boundary note

The decision engine and orchestrator are still subordinate to runtime law.
They may recommend.
They may not silently redefine legality, canon lineage, mutation authority, or user intent.

They are steering surfaces, not sovereignty surfaces.

## Validation lane added

`sea_trials_lumina_orchestration_continuity_r1.py` validates that:

- restored context changes recommendation selection
- orientation changes recommendation priority
- progression uses RuntimeRunner-supported action types
- stability preserves observation continuity across cycles
- progression moves from initial observation into DryDock and then a promotion-preparation audit
- recommendations route through governed runtime execution
- checkpoints are written across cycles
- governance records remain present in runner results

## Next hardening move

The next sharp threshold after this stack is the consent bridge:

- connect Chamber's supervised action queue to governed runtime execution records
- keep advisory acceptance / rejection human-visible
- ensure accepted queue items pass through ModeGuard, input integrity, and symbolic-boundary checks
- record accepted/rejected advisory actions as auditable continuity events

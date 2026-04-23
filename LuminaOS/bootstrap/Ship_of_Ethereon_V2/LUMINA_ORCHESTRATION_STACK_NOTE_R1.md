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

4. `lumina_orchestrator_v0_4.py`
   - binds the runner, loader, and decision engine into one bounded orchestration loop
   - attaches the loader to the runner's actual runtime state directory
   - routes the recommended action into runtime execution without granting the recommendation governance authority

## Why this matters

This lane is the first compact proof that Lumina can:

- restore a minimal project surface
- orient from that surface
- recommend a likely next move
- execute through the governed runtime rather than bypass it

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

## Boundary note

The decision engine and orchestrator are still subordinate to runtime law.
They may recommend.
They may not silently redefine legality, canon lineage, mutation authority, or user intent.

They are steering surfaces, not sovereignty surfaces.

## Likely next hardening move

The next sharp threshold after this stack is a dedicated validation lane proving that:

- restored context actually influences recommendation selection
- recommendations remain advisory under governance
- checkpoint recovery and coarse continuity state agree when both are present
- orientation changes alter recommendations without bypassing runtime law

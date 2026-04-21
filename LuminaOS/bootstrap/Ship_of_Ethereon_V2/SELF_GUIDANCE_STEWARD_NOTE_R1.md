# Self-Guidance Steward Note r1

This note records the next architectural threshold for Lumina OS after return-with-stance.

## What landed

Lumina now has a bounded self-guidance steward in the bootstrap runtime path, plus a checkpoint-refreshed project history rail for advisory continuity.

Core additions:

- `runtime/lumina_self_guidance_steward_r1.py`
- `runtime/lumina_self_guidance_history_r1.py`
- `runtime/runtime_runner_self_guided_bridge_r1.py`
- `runtime/sea_trials_lumina_self_guidance_r1.py`

## What it does

The steward reads:

- project-return summaries
- bounded workspace-host summaries
- projected working stance
- accumulated checkpoint-linked advisory history

It then emits:

- `recommended_next_action`
- `guidance_strategy`
- `confidence_label`
- `reasoning_brief`

The advisory is attached to session and context-bundle surfaces so Lumina can resume with a likely next move already surfaced.
The history rail lets later cycles refresh that advice from more than the immediately restored surface.

## Why this matters

Return-with-stance proved that Lumina could come back to a project without guessing and could restore a bounded working surface around it.

The next missing threshold was not memory alone.
It was orientation plus recommendation, and then recommendation plus accumulated continuity.

This steward is the first bounded proof that Lumina can look at the project surface it restored and say, in effect:

- this is where the work is pointed
- this is the likeliest next thing to do
- recent checkpoint history reinforces or weakens that recommendation
- this recommendation is advisory, not law

## What remains bounded

Self-guidance does **not** become governance.

It may not:

- define mode legality
- define mutation legality
- define promotion legality
- define canon lineage
- define checkpoint legality
- replace explicit user intent

It is a steward, not a sovereign.

## Current role

At this stage, the self-guidance layer does seven useful things:

1. reads restored project-return state
2. reads bounded host / workspace stance
3. emits a non-governing next-step recommendation
4. projects that recommendation into session and context surfaces
5. appends checkpoint-linked advisory history by project
6. refreshes later recommendations from that bounded history
7. leaves a governance trail that records execution without granting authority

## Next likely move

The next hardening step is to deepen:

- richer recommendation logic from longer project history
- user-visible acceptance / rejection loops
- UI consumption of advisory output
- continuity between advisory memory and bounded tool orchestration
- eventual supervised action queues that remain subordinate to governance and user consent

without letting any of that become hidden governance authority.

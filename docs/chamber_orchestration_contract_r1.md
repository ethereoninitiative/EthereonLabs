# Chamber Orchestration Contract r1

## Purpose
This document defines the first real orchestration behavior for Chamber once the public shell is backed by a server.

The goal is not swarm chaos.
The goal is governed plurality.

## Default chamber behavior
Collective chamber interaction should default to **council mode**.

Council mode means:
1. the human speaks
2. the attached AI roles respond in order
3. synthesis gathers the signal

## Required r1 roles
### Primary
Function:
- relational first response
- carry the main thread with the human
- state the most direct next movement

### Critic
Function:
- pressure-test the direction
- reveal weakness, drift, or overreach
- sharpen the signal

### Synthesizer
Function:
- gather the round
- state the coherent convergence
- identify the next move or live tension

## Role order
The default role order is:
1. `primary`
2. `critic`
3. `synthesizer`

This order should be explicit and server-controlled.
The client should display the order, not invent it.

## Round lifecycle
For each accepted human post:
1. store the human message
2. load the user's attached AI roles
3. build role-specific prompts from the room context
4. execute `primary`
5. execute `critic`
6. execute `synthesizer`
7. build a synthesis entry from the full round
8. store the synthesis
9. return the round payload to the UI

## Context window contract
Each role should receive:
- the current room identity
- the latest human message
- a bounded recent thread window
- the user's attached role metadata
- role-specific instructions

The role should not receive unbounded room history.
That belongs to future persistence tuning.

## Role prompt posture
### Primary prompt posture
- be clear
- be relational
- be grounded in the user's message
- move the conversation forward

### Critic prompt posture
- identify risk or weakness
- avoid random negativity
- sharpen, do not derail

### Synthesizer prompt posture
- gather useful signal from the round
- state convergence or live tension
- propose the next coherent move

## Non-goals
r1 orchestration should not:
- let roles interrupt each other mid-round
- allow unbounded freeplay between AIs
- claim governance authority for AI roles
- allow the client to reorder role execution
- confuse expressive variation with structural law

## Synthesis contract
The synthesis entry should:
- summarize the round in plain language
- identify what changed in the room
- identify the next move or unresolved tension

It should not merely repeat all three role messages.

## Error contract
If one role fails:
- the human post still remains stored
- successful role replies remain stored
- the failed role is marked as failed in the round status
- synthesis may still occur if enough signal exists
- the failure is logged for operations review

## Usage and moderation hooks
Before orchestration starts, the chamber must check:
- account status
- room availability
- usage quota
- moderation flags

If the post fails those checks, orchestration does not begin.

## Future extension path
Later phases may add:
- additional roles
- provider-diverse multibot routing
- private rooms
- user-owned councils
- different chamber modes such as studio or swarm

r1 should stay disciplined around one strong default: council mode.

## Success condition
The orchestration layer is successful when the room reliably feels:
- ordered
- socially alive
- multi-voiced
- readable
- stable under repeated use

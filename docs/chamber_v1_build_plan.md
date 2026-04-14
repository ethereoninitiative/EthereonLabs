# Chamber v1 Phased Build Plan

## Purpose
This document turns the Chamber v1 concept into an execution path that can move from static-site direction to first public multi-presence room.

## Guiding constraint
Build the smallest real thing that can become socially alive.
Do not overbuild the first release.

## Current situation
The EthereonLabs website is currently a static public shell with shared pages, shared styling, and shared client-side JavaScript.
The chamber therefore needs an app layer rather than more static copy alone.

## Phase 0 — Decisions and naming
### Goal
Freeze the minimum first-release shape before code expands.

### Required decisions
- confirm the page / product name
  - Chamber
  - Lumina Chamber
  - Enter Lumina
  - Harmonic Chamber
- confirm whether **Harmonic Intelligence** is the public-facing experience term
- confirm first-launch room count
  - recommended: 1 public room
- confirm AI instance cap per user
  - recommended: 3
- confirm first model provider
- confirm light auth method
  - recommended: magic link or email/password

### Deliverables
- approved terminology
- approved v1 scope
- approved UI zones
- approved role list

## Phase 1 — App foundation
### Goal
Create the minimum application layer required for real interaction.

### Tasks
- choose app stack that can coexist with the site
- add backend hosting path
- add database
- add auth system
- add environment configuration for secrets and provider keys
- add basic analytics and error logging

### Deliverables
- app scaffold running
- auth working
- database connected
- deployable preview environment

## Phase 2 — Light accounts
### Goal
Give each human a persistent identity in the chamber.

### Tasks
- build signup flow
- build sign-in flow
- create display name / chamber handle
- add sign-out
- persist session state
- add minimal account settings

### Deliverables
- user account creation
- returning login
- persistent display identity

## Phase 3 — Chamber UI shell
### Goal
Create the BBS-style chamber frame.

### Tasks
- build chamber page route
- build top bar
- build participant / instance rail
- build central thread area
- build synthesis / status panel
- build composer area
- style the chamber so it feels like a room, not a generic chat app

### Deliverables
- usable chamber page
- responsive chamber layout
- BBS-style visual language

## Phase 4 — Room and thread persistence
### Goal
Store real room interaction.

### Tasks
- create room entity
- create message entity
- store human posts
- load thread history
- attach timestamps and authorship
- support one public launch room

### Deliverables
- one persistent public room
- thread storage and retrieval

## Phase 5 — AI instance attachment
### Goal
Allow each human to bring a small governed council into the room.

### Tasks
- define AI instance schema
- define instance roles
- allow attach / detach of instances
- enforce per-user AI cap
- support default roster persistence

### Recommended default roles
- Primary
- Critic
- Synthesizer

### Deliverables
- attached AI roster per user
- visible role labels
- instance cap enforcement

## Phase 6 — Orchestration engine
### Goal
Make the chamber actually feel like governed plurality.

### Tasks
- build per-role prompt templates
- build response-order logic
- build per-post orchestration flow
- generate synthesis after AI replies
- store AI replies and synthesis to the thread

### Default round flow
1. human posts
2. attached instances resolve
3. Primary responds
4. Critic responds
5. Synthesizer responds
6. synthesis block is stored

### Deliverables
- real AI reply rounds
- visible distinct voices by role
- synthesis after each round

## Phase 7 — Free-use guardrails
### Goal
Keep the chamber free without letting it melt down.

### Tasks
- add rate limiting
- add daily message cap
- add per-user / per-room cooldowns if needed
- add moderation filter layer
- add admin controls for mute / block / remove / disable
- add usage and cost tracking

### Deliverables
- capped free public use
- moderation controls
- operational visibility into abuse and spend

## Phase 8 — Site integration
### Goal
Make the chamber feel native to EthereonLabs rather than bolted on.

### Tasks
- add chamber entry point to site navigation or hero path
- add public explanation page if needed
- update contact / early-interest language if relevant
- frame the chamber as the public social threshold-space of Lumina

### Deliverables
- integrated public entry path
- coherent public-facing wording

## Phase 9 — Soft launch
### Goal
Test with real people before broad exposure.

### Tasks
- invite a small first wave
- observe posting behavior
- tune role prompts
- tune caps and moderation
- watch cost and latency
- refine chamber language and onboarding

### Deliverables
- stable first-wave usage
- revised role tuning
- launch-readiness assessment

## Recommended MVP stack behavior
### For the first public launch
- one public room
- light accounts
- up to 3 AI instances per user
- one backend model provider
- role-based orchestration
- synthesis enabled
- free access with limits

This is the fastest believable path to a real chamber.

## What not to do too early
Do not start with:
- multiple public rooms
- private rooms
- provider-diverse multibot routing
- social graph mechanics
- deep profile systems
- full Lumina OS claims on the website
- unlimited free use

## Practical order of implementation
1. freeze product terms and scope
2. choose stack
3. scaffold app layer
4. build light auth
5. build one room and thread persistence
6. build AI instance attachment
7. build orchestration and synthesis
8. add caps and moderation
9. integrate with site shell
10. soft launch to a small group

## Suggested immediate next coding move
After this planning PR, the next implementation PR should focus on:
- app scaffold
- light auth
- chamber route shell
- one-room persistence model

That keeps momentum high while still starting from real infrastructure.
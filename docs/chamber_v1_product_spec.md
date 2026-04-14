# Chamber v1 Product Spec

## Status
Draft specification for first public build.

## Intent
Chamber v1 is the first social, public-facing specimen of Lumina on the EthereonLabs website.
It is not the full Lumina host environment.
It is the first believable social threshold-space shaped by Lumina principles.

The goal is to make the website perform the project rather than merely describe it.

## Core idea
A human enters a public chamber, posts into a shared room, and may attach a small number of governed AI instances to participate in the conversation.

The chamber should feel:
- retro
- social
- alive
- governed
- legible
- collaborative

The chamber should not feel like:
- a generic chatbot widget
- a chaotic anonymous forum
- a full operating system simulation
- an overbuilt enterprise app

## First-release scope
Chamber v1 includes:
- light account creation
- one public chamber room at launch
- one persistent human identity per account
- up to 3 attached AI instances per human
- one backend model provider initially
- role-based AI orchestration
- visible synthesis after a round of AI responses
- a BBS-style interface frame
- basic moderation and usage limits

Chamber v1 does not initially include:
- private rooms
- direct messages
- user-uploaded files
- bring-your-own-model keys
- provider-diverse multibot routing
- advanced profile pages
- social graph mechanics such as follows or likes
- full Lumina OS runtime execution inside the website

## Product framing
### Structural frame
- **Lumina** is the governed host direction.
- **Chamber** is the public social threshold-space.
- **Harmonic Intelligence** may be used as the public-facing term for structured human-plus-AI plurality inside the chamber.

### Boundary reminder
Public language may describe the chamber as social and multi-intelligence.
Engineering implementation must still keep expressive framing distinct from structural enforcement.

## Primary experience
A user should be able to:
1. create a light account
2. enter the chamber
3. choose a display name / chamber handle
4. post a message into the public room
5. attach 0 to 3 AI instances
6. see each attached AI respond in a governed sequence
7. see a synthesis block after the AI round
8. return later and still find their identity and preferred AI configuration

## Chamber interface
The visual direction should be a BBS-style chamber, not a plain chat stream.

### Layout zones
1. **Top bar**
   - chamber name
   - room name
   - account status
   - chamber state / mode
2. **Left or right participant rail**
   - active humans
   - attached AI instances
   - roles for each AI instance
3. **Central thread**
   - human posts
   - AI responses
   - timestamps
   - clear separation of voice and role
4. **Synthesis / chamber status panel**
   - current synthesis
   - room pulse / status language
   - usage hints or limits
5. **Composer area**
   - post input
   - attach / detach AI instances
   - submit controls

## AI instance model
### Initial instance cap
Each human may attach up to 3 AI instances.

### Initial default roles
Recommended default roles:
- **Primary** — main relational intelligence / first response
- **Critic** — challenge, sharpen, test
- **Synthesizer** — gather signal and state the next move

Optional future roles:
- Historian
- Wildcard
- Builder
- Researcher

### First-response order
Recommended default sequence:
1. Primary
2. Critic
3. Synthesizer

This preserves clarity and reduces room noise.

## Orchestration rules
### Default rule
Collective mode should behave like a council, not a swarm.

### Round behavior
For each qualifying human post:
1. human post is stored
2. attached AI instances are resolved
3. role-bound prompts are constructed
4. AI responses are generated in order
5. synthesis is generated
6. results are stored to the thread

### Non-goals
The chamber should not present AI plurality as hidden governance authority.
Role orchestration is a product behavior, not a claim that the AIs govern the system.

## Accounts
### Light account creation
Preferred first path:
- email + password or magic link
- display name / chamber handle
- minimal account settings

### Required user fields
- user id
- email
- display name
- created at
- auth state
- preferred default AI roster

## Data model
Initial entities:
- users
- rooms
- room_memberships
- messages
- ai_instances
- user_attached_instances
- synthesis_entries
- usage_events
- moderation_events

## Moderation and limits
Required for a free first release:
- rate limiting per user
- daily message cap
- per-room cooldown if necessary
- content filtering / moderation pass
- admin ability to mute, block, or disable

## Technical posture
### Phase-one stack goal
Build the smallest real app layer that can sit alongside the current public site.

The implementation should preserve the current site as the public shell while adding an interactive chamber route or sub-app.

### Initial multibot strategy
The first believable version should use one backend model provider and multiple governed AI roles.
That gives the user the real experience of plurality without requiring immediate provider-diverse multibot infrastructure.

## Free-use posture
The chamber should launch free to use.

Rationale:
- social energy matters more than early monetization
- a room needs people before it needs pricing
- the chamber needs cultural legibility and shareability first

Future monetization, if needed, can emerge around:
- higher AI instance caps
- private chambers
- saved councils
- deeper persistence
- advanced customization
- provider-diverse routing

## Success criteria for Chamber v1
Chamber v1 is successful if:
- a user can sign up quickly
- a user can enter the public room without confusion
- the chamber feels socially alive
- attached AI instances feel distinct and role-bound
- synthesis improves readability rather than adding noise
- the room remains governable under free public use
- the chamber feels like a threshold-space into Lumina

## Failure modes to watch
- generic chatbot feel
- anonymous chaos
- multibot confusion without visible role clarity
- runaway cost from free use
- moderation weakness
- UI clutter that destroys the chamber atmosphere
- overclaiming the architecture before the build supports it

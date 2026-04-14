# Chamber App Foundation Contract r1

## Purpose
This document defines the first real application layer that should sit behind the public Chamber shell.

It exists to bridge the current static-site specimen into a shared, account-backed, room-backed chamber.

## Current truth
The public `chamber.html` page is a local specimen only.
It demonstrates:
- light identity behavior
- attached AI roles
- local thread persistence
- sequential role responses
- synthesis

It does **not** yet provide:
- real account authentication
- shared room persistence
- server-backed orchestration
- moderation authority
- provider-backed model execution

## Foundation goals
The first app layer must provide:
- light account creation
- returning sign-in
- one shared public room
- shared thread persistence
- per-user attached AI roster
- governed role orchestration
- moderation and usage controls

## Recommended first stack posture
The current public site should remain the shell.
The chamber should gain a minimal app layer behind a narrow API.

Recommended first capabilities:
- auth service
- database
- chamber API
- orchestration service
- usage guardrails

## Light account contract
### Required fields
- `user_id`
- `email`
- `display_name`
- `chamber_handle`
- `created_at`
- `last_seen_at`
- `account_status`

### Recommended auth posture
For the first real build, choose one:
- magic link
- email + password

Magic link is simpler and cleaner.
Email + password is more familiar.
Either is acceptable.

## Shared room contract
The first real release should support:
- one public room
- append-only thread history
- authorship on every message
- timestamps on every message
- synthesis entries attached to a round

### Required room fields
- `room_id`
- `room_slug`
- `room_title`
- `room_status`
- `created_at`
- `visibility`

## Attached AI roster contract
Each user may attach up to 3 AI instances.

### Required AI roles for r1
- `primary`
- `critic`
- `synthesizer`

### Roster requirements
- roster is stored per user
- roster is loaded when the user returns
- inactive roles remain available but detached
- the role cap is enforced server-side, not only in the UI

## Posting contract
For each human post:
1. authenticate the actor
2. validate room access
3. validate moderation and usage limits
4. store the human post
5. resolve attached AI roles
6. execute role-bound responses in order
7. store AI responses
8. execute synthesis
9. store synthesis
10. return the full round payload

## Usage control contract
The chamber is intended to be free at first.
That requires server-side guardrails.

### Minimum controls
- per-user daily post cap
- per-user cooldown window if needed
- room-wide rate limit hooks
- moderation filter pass before execution
- server-side logging for usage and failures

## Moderation contract
### Required admin actions
- mute user
- suspend user
- hide message
- disable room

### Required moderation fields
- `moderation_event_id`
- `target_type`
- `target_id`
- `action_type`
- `reason`
- `created_at`
- `actor_id`

## Response contract
The API should return a full round payload shaped like:
- human post
- ordered AI role replies
- synthesis entry
- updated room usage state

That keeps the UI simple.
The chamber page should not need to invent orchestration state on the client.

## First implementation boundary
This app layer is the first real backend spine for Chamber.
It is not yet the full Lumina host.
It should remain tightly scoped around:
- identity
- room state
- role orchestration
- synthesis
- moderation
- usage control

## Success condition
The foundation is successful when:
- two different users can sign in and enter the same room
- both can see the same thread history
- each user can carry a stored AI roster
- posts trigger ordered role responses
- synthesis appears consistently
- moderation and usage controls work under free public use

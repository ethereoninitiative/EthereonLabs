# Chamber Advisory Vocabulary

**Status:** proposed vocabulary note

This note keeps Chamber advisory records legible as the public layer matures.

## Advisory decision values

Recommended values:

- `pending`
- `accepted`
- `declined`
- `expired`
- `superseded`

New advisories should begin as `pending`. Runtime results should not overwrite the decision value.

## Action status values

Recommended values:

- `queued`
- `claimed`
- `in_progress`
- `completed`
- `failed`
- `halted`
- `cancelled`

The action status describes the work item. The advisory decision describes consent. These should remain separate fields.

## Source values

Suggested starting values:

- `reflective_autonomy`
- `self_guidance_steward`
- `meaning_metabolism`
- `manual_user_request`
- `system_drydock_review`
- `prisma_review`
- `minerva_review`

## Mode values

Use active mode names exactly:

- `Continuity`
- `Sandbox`
- `DryDock`
- `Observation`
- `Canon`

## Expiry note

Pending advisories should eventually receive an expiry pattern before meaningful public traffic. Expiry should not imply rejection; it only means the advisory aged out without a decision.

## Boundary

This is not runtime law. It is a vocabulary guide so consent and audit records remain readable downstream.

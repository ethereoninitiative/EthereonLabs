# Vessel Continuity Transfer R1 — Build Receipt

**Repository anchor:** `main` at `7affd3b18f7797744005429044e297ccefac278f`

**Anchor timestamp:** `2026-09-02T03:28:29Z`

**Build lane:** `build/vessel-continuity-transfer-r1`

## Built

- A path-independent, hash-verified JSON capsule for one latest project-return surface.
- Explicit export, verify, and import operations through `bin/lumina-vessel`.
- Non-overwriting target import with checkpoint and host-link rebasing.
- A target-side operational transfer receipt.
- A cross-vessel sea trial covering projection equivalence, explicit governed continuation, collision refusal, source preservation, and tamper rejection.
- Focused GitHub CI for the new lane.

## Boundary preserved

The capsule and receipt both declare:

- `authority_effect: false`
- `identity_claimed: false`
- `continuation_invoked: false`

This increment preserves attributable return evidence across state roots. It does not transfer governance or canon, prove resident identity, or authorize automatic state movement.

## Validation target

Run from the repository root:

```bash
python -m py_compile \
  LuminaOS/bootstrap/Ship_of_Ethereon_V2/runtime/vessel_continuity_transfer_r1.py \
  LuminaOS/bootstrap/Ship_of_Ethereon_V2/runtime/sea_trials_vessel_continuity_transfer_r1.py \
  LuminaOS/bootstrap/Ship_of_Ethereon_V2/studio/lumina_vessel_transfer_r1.py \
  LuminaOS/bootstrap/Ship_of_Ethereon_V2/bin/lumina-vessel

python LuminaOS/bootstrap/Ship_of_Ethereon_V2/runtime/sea_trials_vessel_continuity_transfer_r1.py
python LuminaOS/bootstrap/Ship_of_Ethereon_V2/bin/lumina-vessel --help
```

Expected focused result: all vessel-transfer checks pass and no `.lumina_state` artifact is tracked.

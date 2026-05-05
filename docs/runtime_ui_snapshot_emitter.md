# Runtime UI Snapshot Emitter (r1)

This utility converts a Lumina `RuntimeRunner` result JSON into the distilled, **read-only UI contract** consumed by the Chamber at `/runtime/latest_cycle.json`.

## Why this exists

- Keeps the **runtime authoritative** and the **UI passive**
- Avoids risky, immediate surgery to the runner while enabling **live receipts**
- Enforces a stable, minimal schema for the Chamber panel

## Usage

```bash
python LuminaOS/bootstrap/Ship_of_Ethereon_V2/runtime/runtime_ui_snapshot_emitter_r1.py \
  path/to/runner_result.json
```

Writes to:
- `public/runtime/latest_cycle.json` (for the website)
- `.lumina_state/ship_of_ethereon_v2/runtime_outputs/latest_cycle.json` (for local state)

## Flags

- `--no-public` : skip writing to the public site path
- `--no-state`  : skip writing to the local state path

## Contract

The output is **display-only**. It must not:
- execute tools
- alter governance
- mutate canon
- change mode legality
- expose hidden capabilities

## Next step

Integrate this emitter directly into `runtime_runner` so every cycle automatically produces a fresh UI receipt.

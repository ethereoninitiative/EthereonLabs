# START HERE — Runtime Path

**Status:** compatibility waypoint.  
**Current executable entry:** `LuminaOS/bootstrap/Ship_of_Ethereon_V2/bin/lumina`.

This file is retained so older links do not become dead ends. It no longer defines a separate runtime-entry doctrine.

## Current start path

For the complete and current operator guide, use:

- `START_HERE_LUMINA_OS.md`
- `LuminaOS/bootstrap/Ship_of_Ethereon_V2/ACTIVE_RUNTIME_INDEX.md`

From the governed bootstrap root:

```bash
cd LuminaOS/bootstrap/Ship_of_Ethereon_V2
python install/lumina_doctor.py --ensure-state
python bin/lumina-bridge
python bin/lumina run "Review Lumina OS progress and produce the next governed action receipt."
python bin/lumina continue
python bin/lumina observe
python bin/lumina state --limit 12
```

## Current default execution route

```text
bin/lumina
  -> studio/lumina_cli_psi42_v18.py
  -> runtime/runtime_runner_psi42_v18_adapter_r1.py
  -> runtime/runtime_runner_r1_merged.py
```

`runtime_runner_r1_merged.py` remains the core governed runner and may be invoked directly for focused debugging or validation, but direct invocation is not the ordinary host entry path.

## Validation

The baseline core sea trial remains:

```bash
cd LuminaOS/bootstrap/Ship_of_Ethereon_V2/runtime
python sea_trials_set_one_r1_merged.py
```

Repository and workflow gates provide broader validation around the host, truth, distribution, and public surfaces.

## Authority boundary

This waypoint creates no runtime, governance, canon, capability, continuity, or promotion authority. Current executable architecture and validated receipts remain authoritative.

> If you want to enter Lumina as an operator, start with `START_HERE_LUMINA_OS.md` and `bin/lumina`.

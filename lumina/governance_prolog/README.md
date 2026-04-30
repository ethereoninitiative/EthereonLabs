# Governance Prolog Probe r1

This folder is an experimental Prolog-based governance probe for Lumina OS.

It is a **mirror**, not a governor.

## Purpose

The probe exists to test whether selected Lumina governance rules can be expressed as facts and inference rules, then compared against runtime decisions during sea trials.

It may help identify:

- incomplete transition rules
- contradictory assumptions
- mismatch between documented law and runtime behavior
- hidden boundary leaks
- places where governance needs clearer wording

## Authority boundary

This layer is non-authoritative.

It does **not**:

- execute runtime logic
- override `ModeGuard`
- write governance records
- commit canon lineage
- decide capability exposure
- authorize promotion
- replace Python runtime code

It may only:

- mirror a bounded subset of governance rules
- answer local legality questions
- emit comparison reports
- support sea-trial review

## Current status

Dry-dock experiment.

No runtime dependency is introduced. The Python runner shells out to `swipl` only when the probe is invoked manually or from a dedicated test harness.

## Requirements

Optional local dependency:

```bash
swipl --version
```

If SWI-Prolog is unavailable, the probe reports `available: false` rather than failing the Lumina runtime.

## Files

- `rules_r1.pl` — bounded governance rule mirror
- `probe_runner.py` — safe SWI-Prolog subprocess bridge
- `probe_interface.py` — small Python interface for transition/action checks
- `sea_trial_probe_integration_r1.py` — comparison helper for runtime result payloads

## Adoption rule

This folder should not be promoted into runtime integration unless it proves useful in isolated sea trials.

A future promotion would require:

1. clear mismatch or insight discovered by the probe
2. no load-bearing dependency on Prolog
3. explicit documentation of what the Prolog layer owns and does not own
4. sea-trial evidence that comparison reports are useful

## Boundary rule

Prolog may interrogate Lumina law.

Prolog may not become Lumina law.

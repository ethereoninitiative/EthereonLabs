# Lumina Runner Bridge Stack 001

**Status:** active DryDock explanation  
**Scope:** navigation and architecture clarity only; not runtime law.

## Purpose

This note explains why Lumina currently has several runner bridge files instead of one consolidated runner.

The bridge stack is intentionally separated while the architecture is still proving itself. Each bridge adds one layer of behavior without silently changing the authority of the base runtime runner.

## Current stack

```text
runtime_runner_r1_merged.py
  -> runtime_runner_return_host_bridge_r1.py
  -> runtime_runner_self_guided_bridge_r1.py
  -> runtime_runner_reflective_self_guided_bridge_r1.py
```

## Layer meanings

| Layer | Adds | Boundary |
|---|---|---|
| `runtime_runner_r1_merged.py` | Core governed runtime cycle, capability exposure, checkpoints, governance events, optional probes | Owns orchestration path only; governance law remains in `ModeGuard` |
| `runtime_runner_return_host_bridge_r1.py` | Project return and workspace-host artifacts | Restores and frames project context; does not govern legality |
| `runtime_runner_self_guided_bridge_r1.py` | Bounded next-action advisory from restored stance and history | Recommends only; does not authorize action |
| `runtime_runner_reflective_self_guided_bridge_r1.py` | Recursive reflective trace before self-guidance | Reflection remains witness/sail, not governance/keel |

## Why not consolidate yet?

The bridges are useful proof-of-concept isolation.

They let Lumina prove each layer independently:

1. restore a project,
2. host the restored working surface,
3. recommend a next action,
4. reflect before recommendation,
5. then route through governed execution.

Consolidating too early would hide failure ownership and make it harder to tell whether drift came from return, reflection, guidance, or runtime law.

## Consolidation trigger

Do not collapse the bridge stack until repeated sea trials show:

- return/host artifacts remain stable,
- self-guidance remains advisory,
- reflective traces remain non-authoritative,
- runtime governance still owns legality,
- receipts make layer ownership easy to inspect.

## Future shape

A later Lumina runner may become configurable:

```text
lumina_runner(
  enable_return_host=True,
  enable_self_guidance=True,
  enable_reflective_trace=True,
  enable_psi42_v17=True,
)
```

That future runner should still preserve explicit layer boundaries in its receipt.

## Boundary reminder

Bridge composition is convenience.

It must not become hidden authority.

Mode remains law.  
Orientation remains stance.  
Reflection remains witness.  
Guidance remains advisory.  
Runtime receipts remain evidence.

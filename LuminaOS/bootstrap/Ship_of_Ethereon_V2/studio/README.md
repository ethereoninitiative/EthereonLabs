# Lumina Studio v0.1

Lumina Studio is the first deliberately plain operator surface for the Lumina OS governed runtime substrate.

It is not Chamber.  
It is not a public social surface.  
It is not a new governance authority.

It is a local control surface that packages a request, invokes the existing runtime runner, and shows the receipt.

## What Studio does

- accepts an operator request
- declares current mode, target mode, and action type
- attaches an orientation stance as supplemental context
- calls `runtime/runtime_runner_r1_merged.py`
- lets the runtime own input integrity, mode legality, mutation gates, capability exposure, checkpoints, governance logs, canon metadata, and optional probe execution
- returns a compact receipt with checkpoint, governance, exposed capabilities, and halt status

## What Studio must not do

- invent mode law
- bypass `ModeGuard`
- mutate canon directly
- treat poetic or Ethereonic language as structural authority
- replace Chamber or the public website
- expose this local server publicly without authentication and persistence policy

## CLI usage

From this directory:

```bash
python lumina_cli.py "Review Lumina OS progress and produce the next governed action receipt."
```

Useful variants:

```bash
python lumina_cli.py "Inspect the runtime spine" \
  --target-mode Observation \
  --action-type audit \
  --focus architecture \
  --depth foundational \
  --intent verify \
  --receipt-json
```

```bash
python lumina_cli.py "Draft the next Studio build step" \
  --target-mode Sandbox \
  --action-type audit \
  --focus integration \
  --intent build \
  --ethereonic-overlay
```

## Local server usage

```bash
python lumina_studio_server.py
```

Then open:

```text
http://127.0.0.1:8765/studio
```

The server is intentionally local-first and standard-library only. It should not be deployed as a public endpoint without authentication, rate limiting, and a clear persistence boundary.

## Default cycle

The default Studio cycle is an `audit` from `Continuity` to `Observation`.

That is intentional. It gives us a safe first proof:

1. preserve continuity context
2. inspect without mutation
3. expose lawful Observation capabilities
4. write a checkpoint
5. return a receipt

## Authority boundary

Studio is a launcher and receipt viewer.

Runtime law remains owned by the runtime substrate:

- `SessionEngine` owns session state, checkpoints, and resume behavior
- `ModeGuard` owns transition legality, mutation permission, promotion gates, and symbolic dependency checks
- `GovernanceLog` owns append-only runtime history
- `CanonLineageStore` owns canon lineage metadata
- `CapabilityRegistry` owns mode/feature-flag exposure
- `Psi-42` remains optional and instrument-only when lawfully exposed

## First-pass success criteria

Studio v0.1 succeeds if it can:

- run one governed cycle from CLI
- run one governed cycle from local browser UI
- return halt status instead of crashing on denied operations
- show checkpoint and log paths
- show exposed capability IDs
- preserve orientation as supplemental stance, not governance law

## Next hardening steps

1. Add a richer result viewer for governance decisions.
2. Add a saved-cycle browser over `.lumina_state`.
3. Add a mode/action preset library.
4. Wire accepted Chamber queue items into Studio/runtime cycles while preserving consent.
5. Add authentication before any remote deployment.

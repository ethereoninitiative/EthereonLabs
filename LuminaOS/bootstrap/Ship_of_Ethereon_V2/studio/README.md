# Lumina Studio v0.2

Lumina Studio is the first deliberately plain operator surface for the Lumina OS governed runtime substrate.

It is not Chamber.  
It is not a public social surface.  
It is not a new governance authority.

It is a local control surface that packages a request, invokes the existing runtime runner, shows the receipt, and now reads recent emitted runtime state.

## What Studio does

- accepts an operator request
- declares current mode, target mode, and action type
- attaches an orientation stance as supplemental context
- calls `runtime/runtime_runner_r1_merged.py`
- lets the runtime own input integrity, mode legality, mutation gates, capability exposure, checkpoints, governance logs, canon metadata, and optional probe execution
- returns a compact receipt with checkpoint, governance, exposed capabilities, and halt status
- reads recent runtime receipts and governance summaries through a read-only state browser
- can summarize Psi-42 v1.7 Observation receipts through a read-only receipt viewer

## What Studio must not do

- invent mode law
- bypass `ModeGuard`
- mutate canon directly
- treat poetic or Ethereonic language as structural authority
- replace Chamber or the public website
- write to governance/canon/checkpoint files through the state browser
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

## Psi-42 v1.7 receipt viewer

After generating a full JSON Observation receipt, summarize the v1.7 probe fields through Studio:

```bash
python lumina_psi42_v17_receipt_view_r1.py /tmp/lumina_psi42_v17_receipt.json
```

For machine-readable output:

```bash
python lumina_psi42_v17_receipt_view_r1.py /tmp/lumina_psi42_v17_receipt.json --pretty
```

The viewer is read-only. It verifies and displays instrument version, probe mode, probe identity, hybrid continuity coherence, topology metrics, topology receipt presence, and governance-chain status. It does not run Lumina or authorize action.

## State browser usage

Read recent emitted runtime receipts from the command line:

```bash
python lumina_state_browser.py --limit 12
```

The state browser is read-only. It summarizes files under:

```text
.lumina_state/ship_of_ethereon_v2/runtime_runner_r1_actiontype_logging/
```

It returns:

- recent run receipts
- checkpoint paths
- governance log path
- governance event counts
- latest governance event type/hash
- canon lineage count/head when present
- exposed capability ids for recent runs

## Local server usage

```bash
python lumina_studio_server.py
```

Then open:

```text
http://127.0.0.1:8765/studio
```

Useful local endpoints:

```text
/health
/api/state?limit=12
/run
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
6. refresh emitted runtime state

## Authority boundary

Studio is a launcher, receipt viewer, and read-only state browser.

Runtime law remains owned by the runtime substrate:

- `SessionEngine` owns session state, checkpoints, and resume behavior
- `ModeGuard` owns transition legality, mutation permission, promotion gates, and symbolic dependency checks
- `GovernanceLog` owns append-only runtime history
- `CanonLineageStore` owns canon lineage metadata
- `CapabilityRegistry` owns mode/feature-flag exposure
- `Psi-42` remains optional and instrument-only when lawfully exposed

## First-pass success criteria

Studio v0.1 succeeded if it could:

- run one governed cycle from CLI
- run one governed cycle from local browser UI
- return halt status instead of crashing on denied operations
- show checkpoint and log paths
- show exposed capability IDs
- preserve orientation as supplemental stance, not governance law

Studio v0.2 succeeds if it can additionally:

- summarize recent emitted run receipts
- summarize governance event counts
- report canon head/count if present
- expose the same read-only snapshot through `/api/state`
- keep state inspection read-only and non-authoritative
- read and summarize Psi-42 v1.7 Observation receipts without becoming a probe authority

## Next hardening steps

1. Add a richer result viewer for governance decisions.
2. Add mode/action preset library.
3. Add diffable receipt comparison between runs.
4. Wire accepted Chamber queue items into Studio/runtime cycles while preserving consent.
5. Add authentication before any remote deployment.

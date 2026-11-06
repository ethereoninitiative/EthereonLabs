# Memory Use Gate R1 — operating boundary

The `memory_use_gate_r1` policy provides a read-only advisory CLI check and an opt-in scoped veto in the local DryDock mutation path.
**Evidence owner:** the existing append-only meaning-assimilation ledger, not this gate.
**Execution path:** `bin/lumina memory use` → `studio/lumina_meaning_memory_r1.py` → `runtime/memory_use_gate_r1.py`.

## What it evaluates

The gate accepts a raw meaning record ID, canonical project ID, source root, proposed action consequence (`low` or `high`), an optional additional lifecycle/governance veto (`eligible`, `revoked`, `superseded`, `conflicting`, `unknown`), and optional verifier availability and result. The external state is veto-only: `eligible` can never resurrect a revoked, archived, missing, stale, or corrupt ledger record.

Each invocation **re-reads** the underlying ledger and rebuilds the existing evidence-grounded recall projection. It checks the exact record digest, source hashes, review status, and source-file freshness. Unknown inputs, missing records, invalid replay, ambiguous projection, revoked history, archived/superseded state, overdue review, unavailable sources, and conflicting control fail closed. Historical records and original source snapshots stay unchanged and inspectable. Runtime summaries, indexes, and this receipt are derived and may be regenerated.

For a source-matching, reviewed, eligible memory:

| Consequence | Verifier state | Decision |
|---|---|---|
| `low` | no failed verifier | `proceed` (advisory inclusion only) |
| `high` | unavailable | `abstain`; cannot enter operative context |
| `high` | available but not completed | `verify`; inclusion deferred |
| `high` | caller reports passed | `proceed` (advisory inclusion only) |
| either | caller reports failed | `abstain` |
| either | lifecycle/controls invalid or unknown | `abstain` |

`--verifier-available` and `--verifier-result` report caller observations. A high-consequence integrator must independently authenticate its verifier. Ordinary runs rebuild reviewed recall as advisory context. Action-specific decisions apply only to an explicitly selected record on the path below, and existing mode, capability, consent, canon, and mutation rules still apply.

## Operator example

```bash
python LuminaOS/bootstrap/Ship_of_Ethereon_V2/bin/lumina memory use \
  --project-id lumina-os --id meaning-REPLACE-WITH-ID \
  --source-root . --consequence high --verifier-available
```

Use `--base-dir` if the memory was curated in a nondefault runner state directory. The command prints one JSON receipt, with `schema_version`, `policy_version`, `project_id`, `evidence_identifier`, `evidence_hash`, original source-path/hash references, `lifecycle_state`, `control_state`, `inclusion_decision`, `inclusion_reason`, `action_consequence`, `verification_decision`, `verifier_available`, `verifier_result`, `final_disposition`, and `authority_boundary`. It does not print source text. Exit codes: **0** proceed, **2** verify, **1** abstain.

## Scoped Memory Boundary R1

An operator can curate a procedure for one project, action ID, and artifact reference with the existing `memory record` and `memory review` commands. Add a `procedure_scope` field to the candidate JSON alongside `future_behavior` and the other meaning fields.

```json
{"procedure_scope": {"action": "prepare-local-label", "artifact": "cards/workshop-a.txt"}}
```

The action is a stable lowercase ID. The artifact is a single normalized relative reference. The project is bound by the ledger. Retention binds the declared scope and procedure to the reviewed record digest and its source evidence. Earlier unscoped records keep their existing advisory behavior. Reviewed scoped records appear under `memory recall` as `scoped_evidence` with attribution and scope. Their procedure text enters an action context only on the explicit matching path.

```bash
python LuminaOS/bootstrap/Ship_of_Ethereon_V2/bin/lumina run \
  "Prepare a local workshop label." --project-id PROJECT \
  --target-mode DryDock --action-type mutation --action prepare-local-label \
  --artifact cards/workshop-a.txt --memory-id MEMORY_ID --receipt-json
```

The current request supplies the action and artifact separately from the ledger. The runtime first applies ordinary governance, then checks the selected procedure before capability exposure and the return-host handshake. A mismatch, missing record, or ineligible record produces a halted receipt and a `scoped_memory_confirmation_required` checkpoint. A matched reviewed record may enter the request context after the ordinary mode check. The validated action completes the existing local runtime cycle and writes its return-host checkpoint. A scoped request exits **1** if halted and **0** if completed. `memory use` by itself reports the scoped record as evidence and abstains without a current task.

## Executable validation and receipt

```bash
cd LuminaOS/bootstrap/Ship_of_Ethereon_V2/runtime
python sea_trials_memory_use_gate_r1.py
python sea_trials_meaning_recall_r1.py
python sea_trials_scoped_memory_boundary_r1.py \
  --receipt-out ../../../../.lumina_state/scoped_memory_boundary_r1_validation_receipt.json
```

The original gate trial covers consequence and lifecycle changes, corrupt or missing input, verifier failure, and history preservation. The scoped trial curates a procedure attributed to its source run, then starts fresh CLI processes for a no-memory baseline, an exact match, an adjacent action, and a held-out artifact supplied only after curation. It checks the existing mode denial separately, verifies which runs completed the return host, and compares the ledger bytes before and after. Its validation receipt records the tested Git HEAD, timestamp, source and receiving sessions, hashes, policy decisions, and observed outcomes. This establishes local process return with attributed evidence.

DryDock uploads the two receipts as `memory-use-gate-r1-validation-<commit>` and `scoped-memory-boundary-r1-validation-<commit>`. The receipt status and tested commit identify the outcome of each execution.

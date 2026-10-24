# Memory Use Gate R1 — operating boundary

**Status:** explicit local CLI check, read-only. **Policy:** `memory_use_gate_r1`.
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

**Important:** `--verifier-available` and `--verifier-result` are caller-supplied observations, **not cryptographically authenticated verifier receipts**. R1 does not discover a verifier, attest verifier identity, or grant downstream execution authority. A real high-stakes integrator must supply and independently trust the verifier; a plain CLI flag alone is not a trustworthy high-stakes approval. A successful gate check also does **not** override mode, capability, consent, canon, or mutation law. The default runtime still injects its existing reviewed meaning-recall projection, not these action-specific decisions. An action executor must explicitly consume this gate before using a memory for an action.

## Operator example

```bash
python LuminaOS/bootstrap/Ship_of_Ethereon_V2/bin/lumina memory use \
  --project-id lumina-os --id meaning-REPLACE-WITH-ID \
  --source-root . --consequence high --verifier-available
```

Use `--base-dir` if the memory was curated in a nondefault runner state directory. The command prints one JSON receipt, with `schema_version`, `policy_version`, `project_id`, `evidence_identifier`, `evidence_hash`, original source-path/hash references, `lifecycle_state`, `control_state`, `inclusion_decision`, `inclusion_reason`, `action_consequence`, `verification_decision`, `verifier_available`, `verifier_result`, `final_disposition`, and `authority_boundary`. It does not print source text. Exit codes: **0** proceed, **2** verify, **1** abstain.

## Executable validation and receipt

```bash
cd LuminaOS/bootstrap/Ship_of_Ethereon_V2/runtime
python sea_trials_memory_use_gate_r1.py
python sea_trials_meaning_recall_r1.py
```

The focused sea trial tests the real ledger and CLI, consequence contrast, revoked and archived history, unknown/missing/conflicting controls, changed sources, verifier absence/failure, and byte-for-byte historical preservation. It emits a machine-readable `memory_use_gate_r1_validation_receipt` to stdout. DryDock also writes and uploads the receipt as `memory-use-gate-r1-validation-<commit>`; **only completed CI jobs establish a passing result**. DryDock runs the broader runtime, host, and documentation checks. No resident identity, consciousness, independently reproduced cross-vessel selfhood, or continuity claim follows from persistent bytes.

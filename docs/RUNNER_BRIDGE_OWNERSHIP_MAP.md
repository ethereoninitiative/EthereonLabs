# Runner Bridge Ownership Map

**Status:** working map  
**Authority:** documentation and refactor guidance only  
**Scope:** runtime runner, bridge, and adapter files that route requests into governed Lumina cycles

## Purpose

The runner and bridge stack is now useful enough to accumulate barnacles.

Before files are compressed, merged, renamed, or retired, their ownership boundaries should be explicit. This map prevents cleanup from erasing distinctions that still matter.

## Current ownership frame

| Component pattern | Owns | May call | Must not own | Stewardship note |
|---|---|---|---|---|
| `runtime_runner_*` | Runtime cycle orchestration | Session engine, mode guard, context bundle builder, capability registry, probes when exposed | Governance law itself, canon truth outside the lineage store, Chamber consent | Canonical runner should stay boring and explicit. |
| `runtime_spine_*` | Session state, mode guard, context building, governance log interfaces | Integrity chain, orientation vector, Ethereonic registry by attachment only | Public UI decisions, Chamber advisory state, host approval | This is keel territory. Keep it load-bearing and plain. |
| `runtime_runner_orientation_adapter_*` | Inject project orientation into context bundle construction | Runtime runner and orientation vector helpers | Mode legality, mutation permission, promotion gates | Adapter can remain separate until orientation behavior is stable. |
| `github_task_bridge_*` | Package repository snapshots and invoke runtime audit cycles | Git metadata, runtime runner | GitHub mutation authority, canon promotion authority | Bridge should stay adapter-shaped, not governance-shaped. |
| future Chamber bridge | Translate accepted queued actions into governed runtime requests | Chamber queue, runtime runner | Raw advisory authority, direct runtime bypass | Build under drydock plan before activation. |
| future deployment bridge | Attach environment/host context to runtime receipts | Host/environment registry, runtime runner | Chamber consent, governance law | Should remain explicit and receipt-oriented. |

## Compression rule

Do not merge files merely because their names sound similar.

Merge only when all of the following are true:

1. Their ownership boundaries are identical.
2. Their failure modes are identical.
3. Their test surfaces are compatible.
4. Their removal does not hide a useful adapter seam.
5. The README or active runtime index is updated in the same PR.

## Suggested refactor path

1. Mark one runner as canonical.
2. Mark adapters as adapters, not alternate runners.
3. Retire obsolete bridge files only after equivalent behavior is covered by tests or receipts.
4. Keep the GitHub bridge and future Chamber bridge separate unless they converge on a common adapter interface.
5. Consider a single configurable runner only after bridge semantics stop changing.

## Drift warning

Bridge accumulation is not automatically failure.

Unmapped bridge accumulation is the failure mode.

The map comes before the scissors.
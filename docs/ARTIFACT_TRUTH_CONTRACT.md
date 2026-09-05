# Artifact Truth Contract

**Purpose:** prevent drift between executable runtime truth, distribution behavior, generated artifacts, capability exposure, navigation, and public claims.

## Source of truth hierarchy

1. Executable runtime, installer, and host behavior
2. Capability, deployment, and distribution contracts
3. Sea-trial, build, and reproducibility receipts
4. `docs/ACTIVE_SURFACE_REGISTRY_R1.json` and current navigation documents
5. Public website messaging

If a higher layer changes, lower layers must be reconciled.

The active-surface registry maps status and evidence relationships. It does not create runtime authority, capability exposure, training authorization, or canon state.

## Cross-surface reconciliation

Run:

```bash
python scripts/repository_truth_reconciliation_gate_r1.py
```

The gate verifies that:

- registered active surfaces and validation paths exist
- Windows distribution status appears in the current operating map and Lumina start guide
- public maturity language distinguishes an installable developer preview from a signed public release
- the HRA dataset receipt uses the current evidence-scoped contract
- declared HRA artifacts exactly match isolated generator output
- retired broad receipt claims do not remain committed

## Drift checklist

When runtime, host, distribution, dataset, or interface structure changes, inspect:

- `LuminaOS/bootstrap/Ship_of_Ethereon_V2/runtime/capability_registry_r1.json`
- `docs/ACTIVE_SURFACE_REGISTRY_R1.json`
- `CURRENT_OPERATING_MAP.md`
- `START_HERE_LUMINA_OS.md`
- relevant bootstrap and deployment README files
- generated artifacts and their receipts
- public website claims about Lumina, continuity, distribution, and OS maturity

## Generated artifacts

Generated artifacts are evidence only when they match the committed generator and inputs.

When a generator, accepted selection, input batch, receipt schema, or claim scope changes:

1. regenerate the declared artifacts in the same PR
2. preserve explicit negative fields for reviews not performed
3. compare exact generated output in an isolated directory
4. fail CI if committed output differs from regeneration

A corrected generator beside a stale receipt is an artifact-truth failure.

## Prepared promotion evidence

`runtime/canonical_promotion_export_r1.py` prepares one verified repository-local
successor under `artifacts/runtime_truth/prepared/canon-0002/`. It consumes the
existing guarded `RuntimeRunner` promotion path and its local receipt. It does
not grant promotion permission, commit files, rewrite genesis, or activate a
prepared successor as current canon.

Use a fresh promotion state directory beneath repository `.lumina_state` when
running the existing DryDock-to-Canon promotion. Governance and lineage seed
from verified committed evidence before the first promotion-cycle event. An
existing unanchored or invalid chain is rejected without rebasing its records.
Isolated trials explicitly use `seed_committed_canon=False`; their independent
genesis cannot pass the repository successor export checks.

After the guarded runtime promotion succeeds at a clean candidate HEAD:

```bash
python LuminaOS/bootstrap/Ship_of_Ethereon_V2/runtime/canonical_promotion_export_r1.py prepare --state-dir .lumina_state/my-promotion
python LuminaOS/bootstrap/Ship_of_Ethereon_V2/runtime/canonical_promotion_export_r1.py verify --target artifacts/runtime_truth/prepared/canon-0002
```

The bounded directory contains governance and lineage JSONL, the existing
promotion receipt, its validation artifact, and post-promotion verification.
Both chains and the hashed promotion payload retain their original bytes or
values. `evidence_paths.validation_artifact` in the receipt locates the copied
validation bytes; the original payload reference remains linked to governance,
and the same SHA-256, artifact identity and candidate SHA are still required.
Local operational references inside immutable governance records remain
historical provenance; they are not new canonical evidence dependencies.

Preparation requires the exact current candidate SHA and a clean working tree.
Verification after committing the prepared set requires that candidate to be an
ancestor and that only the five prepared files changed since validation. A
changed candidate, broken chain, substituted genesis, missing validation,
relocation mismatch, stale verification receipt, extra file or existing target
fails closed. Failed preparation removes the newly created target.

Review the five files in an evidence-only PR. DryDock reruns the integration
trial and independently verifies all prepared sets with Git history available.
The repository-truth reconciliation gate and public runtime snapshot continue
to describe the current committed genesis. Selecting and activating approved
successor evidence as current canon remains a separate governance integration.

## Distribution truth

An installer may be installable without being a public release.

Distribution claims must distinguish:

- source-run development paths
- host/appliance scaffolds
- unsigned developer previews
- signed public releases
- tested upgrade, removal, repair, backup, and restore behavior

Packaging owns placement and launch behavior. It does not create runtime governance, capability authority, canon promotion, identity, or continuity truth.

## Red flags

- docs describe deprecated runtime paths
- website claims capabilities or release maturity not supported by registered evidence
- sea trials validate behavior not explained anywhere
- exploratory spikes presented as current substrate
- generated receipts disagree with their generators
- active distribution lanes are absent from navigation
- symbolic framing is accidentally described as structural law
- timestamp-only generated commits obscure architectural history

## Rule

Poetic framing may orient.
Executable architecture, validated distribution behavior, and reproducible artifacts define truth.

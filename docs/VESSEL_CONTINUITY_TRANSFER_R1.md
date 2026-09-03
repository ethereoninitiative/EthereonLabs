# Vessel Continuity Transfer R1

**Status:** active bounded project-return portability capability

**Scope:** one latest project-return surface; not complete runtime migration

**Authority:** evidence transport only

## Purpose

Vessel Continuity Transfer R1 gives Lumina an explicit way to move the latest returnable state of one project between two local state roots.

The transfer answers a narrow engineering question:

> Can the same attributable project orientation be reconstructed on a different host path without treating the original host as the resident or declaring identity continuity by assertion?

R1 answers that question with a hash-verified capsule and an import receipt. It does not attempt to answer the broader philosophical identity question.

## Host command

From `LuminaOS/bootstrap/Ship_of_Ethereon_V2`:

```bash
python bin/lumina-vessel export \
  --project-id <project> \
  --source-vessel-id <source-vessel> \
  --capsule <path-to-capsule.json>

python bin/lumina-vessel verify \
  --capsule <path-to-capsule.json>

python bin/lumina-vessel import \
  --target-vessel-id <target-vessel> \
  --surface-root <target-runtime-root>/lumina_project_surface \
  --capsule <path-to-capsule.json>
```

Without `--surface-root`, export and import use the active local runtime's project surface. Export and import are separate, explicit actions. Import never invokes continuation; a later `lumina continue` remains a separate governed request.

## Capsule contents

The R1 capsule carries only the latest bounded project-return surface:

- the live session record referenced by the latest restore point;
- the referenced checkpoint;
- the latest project restore point;
- the current host bundle, when one exists;
- a SHA-256 digest for each payload component;
- a SHA-256 digest for the complete capsule envelope;
- explicit source-vessel, authority, identity, and scope declarations.

It does not carry governance history, canon lineage, capability authority, resident-pulse memory, every historical checkpoint, or the entire Lumina state root.

## Import law

Import is deliberately conservative:

1. validate the capsule schema and every payload digest;
2. verify that project and session references agree;
3. require distinct source and target vessel identifiers;
4. refuse to overwrite an existing target project surface;
5. rebase checkpoint and host links to the target state root;
6. compare a path-independent continuity projection before accepting the transfer;
7. write a local transfer receipt;
8. leave the restored project surface dormant until a separate explicit `lumina continue` request occurs.

A corrupted capsule is rejected before project files are written. A repeated import into occupied target paths fails closed.

## Continuity comparison

Cross-vessel comparison includes:

- project and session identifiers;
- current mode;
- artifacts in scope;
- pending and completed action markers;
- workspace state;
- continuation notes;
- return strategy;
- the path-independent host bundle.

Filesystem paths are host coordinates, so checkpoint and host links are intentionally rebased. Matching evidence means the bounded return surface survived transport. It does not prove that a resident, model process, account, or subjective identity is numerically identical across vessels.

## Receipts

Successful imports write operational evidence beneath the target state root:

```text
vessel_transfers/
  receipts/
  latest/
```

The receipt records capsule identity, source and target vessel identifiers, imported paths, source and target continuity-projection hashes, and the declarations:

- `authority_effect: false`
- `identity_claimed: false`
- `continuation_invoked: false`
- `continuity_claim: evidence_preserved_across_vessels_identity_not_proven`

These receipts are transport evidence. They are not governance, canon, checkpoint truth, or identity authority.

## Sea-trial evidence

`runtime/sea_trials_vessel_continuity_transfer_r1.py` creates a source project and host surface, exports it, imports it into a distinct target state root, and proves:

- path-independent continuity projections match;
- checkpoint and host links point into the target vessel;
- import does not invoke continuation on either source or target;
- a later explicit `lumina continue` reads the imported intention and runs through the governed Observation/audit path;
- the source return surface is unchanged;
- repeat import refuses to overwrite state;
- payload tampering is rejected before project files are written;
- neither the return surface nor transfer receipt gains authority-bearing fields.

The focused workflow `.github/workflows/lumina-vessel-continuity-transfer-r1.yml` runs this proof and checks both the host command and local-state hygiene.

## Deliberate R1 limits

R1 does not prove or provide:

- resident identity across model, process, account, or hardware replacement;
- full runtime-state, governance, canon, or history migration;
- automatic discovery or ranking of target vessels;
- background export, sync, or import;
- remote transport encryption or signing;
- conflict resolution or overwrite;
- OS reboot, power-loss, or application-upgrade recovery;
- autonomous permission to move project state.

The smaller capability matters first: Lumina can carry bounded, attributable return evidence into a different vessel, verify that the return surface survived, and remain honest about what that evidence does not establish.

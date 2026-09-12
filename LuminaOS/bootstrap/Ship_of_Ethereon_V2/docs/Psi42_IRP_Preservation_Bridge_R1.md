# Psi-42 / IRP Preservation Bridge R1

**Status:** standalone bounded structural-preservation instrument.  
**Authority:** none; no governance, canon, consent, runtime, capability, identity, or execution authority.  
**Input:** validated IRP-R1 exchanges.  
**Output:** a deterministic preservation report and, when requested, a separately attributed IRP diagnostic packet.

## Purpose

This bridge connects Interresident Resonance Protocol R1 to the Psi-42 instrument family without forcing IRP packets through a prose translation or treating Psi-42's legacy simulated signal metrics as evidence of real packet preservation.

The bridge asks one bounded question:

> Did the received exchange preserve what the residents externalized?

It measures packet presence, declared authorship, provenance, claim structure, confidence, uncertainty, evidence bindings, relations, lineage, and fixed authority boundaries. Complete packet hashes are reported separately from canonical semantic preservation so a derivative human gloss can change without being mistaken for a change in canonical resident meaning.

## Preserved disagreement is success

IRP already represents agreement and disagreement as attributed structure. The preservation bridge therefore treats surviving disagreement as transmission fidelity, not noise.

For each original disagreement slot, the bridge compares the independently attributed declarations that occupied that slot. A two-to-one split succeeds only when the minority declaration survives with its resident attribution, provenance, confidence, uncertainty, evidence bindings, and value intact. Dropping the minority, changing it into the majority position, or collapsing authorship fails preservation.

No majority count, model label, confidence value, synthesis packet, or successful transmission establishes consensus, truth, canon, permission, or authority.

## Measurement lanes remain distinct

`runtime/psi42_irp_preservation_bridge_r1.py` records:

- `measurement_class = actual-irp-structural-preservation`;
- IRP packet preservation as measured;
- Psi-42 simulated signal metrics as `not-invoked`;
- `metrics_commingled = false`.

This is deliberate. Existing `psi42_transceiver_v1_8.py` metrics are bounded simulated signal/topology diagnostics. They are not silently relabeled as measurements of resident packet fidelity. Future work may display both lanes together only if their provenance and measurement classes remain explicitly distinct.

## Diagnostic return path

`diagnostic_packet(...)` converts the deterministic preservation report into a new IRP observation packet attributed to `psi42-irp-preservation-witness-r1`.

The packet:

- binds the preservation report as inline source evidence;
- binds the received packets as parents and `responds_to` references;
- reports successful transmission, authorship preservation, disagreement preservation, and minority-position preservation;
- carries an explicit uncertainty boundary stating what was not established;
- retains IRP's fixed `authority_granted=false`, `authority_claim=none`, and `permission_required=true` contract.

The diagnostic packet is an instrument observation, not a resident consensus or a grant of action authority. R1 binds at most 32 received parents because that is the IRP packet parent-reference limit.

## CLI

From `LuminaOS/bootstrap/Ship_of_Ethereon_V2/`:

```bash
python runtime/psi42_irp_preservation_bridge_r1.py witness original.json received.json \
  --project PROJECT --encounter ENCOUNTER

python runtime/psi42_irp_preservation_bridge_r1.py packet original.json received.json \
  --project PROJECT --encounter ENCOUNTER --session SESSION
```

Both inputs must already be valid IRP exchanges for the declared project and encounter. Invalid hashes, scope contamination, broken lineage, malformed packets, or unsupported protocol structure fail closed before preservation is measured.

## Validation

Run:

```bash
python runtime/sea_trials_psi42_irp_preservation_bridge_r1.py
```

The focused sea trial covers exact preservation, minority loss, forced convergence, uncertainty/confidence/authorship mutation, evidence and provenance drift, relation and lineage drift, gloss-versus-semantic integrity, attributed diagnostic return, parent-budget limits, fail-closed invalid input, and non-authority boundaries.

## Limits

R1 measures deterministic structural preservation of externalized IRP declarations. It does not establish semantic equivalence between different internal representations, hidden-state compatibility, private chain-of-thought access, consciousness, subjective experience, authenticated identity, truth, shared belief, live inter-provider communication, or successful communication under the separate Interintelligence Encounter Protocol evidence ladder.

The bridge is standalone and not wired into the default host, provider connectors, autonomous networking, or runtime capability exposure.

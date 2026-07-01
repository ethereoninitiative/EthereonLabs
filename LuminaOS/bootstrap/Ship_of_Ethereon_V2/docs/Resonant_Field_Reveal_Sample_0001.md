# Resonant Field Reveal Sample 0001

**Sample ID:** `resonant-field-reveal-sample-0001`  
**Status:** committed reproducibility fixture  
**Authority:** inspection only

## Purpose

This sample gives Resonant Field Reveal R1 a stable, reviewable output on `main`.

It preserves four linked artifacts:

```text
artifacts/resonant_field_reveal/sample_0001/
  resonant_field_reveal_r1_input.json
  resonant_field_reveal_r1.json
  resonant_field_reveal_r1.svg
  resonant_field_reveal_r1_receipt.json
```

The input manifest defines one current manifold point, four lawful candidate trajectories, and one candidate withheld by external governance. The generated SVG shows the current point as a central attractor, lawful paths crossing the governance membrane, and the withheld path stopping at that boundary.

## Reproduce

From the runtime directory:

```bash
cd LuminaOS/bootstrap/Ship_of_Ethereon_V2/runtime
python resonant_field_reveal_sample_r1.py
python sea_trials_resonant_field_reveal_sample_r1.py
```

The generator rewrites the committed sample from the canonical input manifest. The sea trial regenerates the full sample in a temporary directory and requires byte-identical JSON, SVG, input, and receipt files.

## Receipt

The receipt records SHA-256 hashes for:

- the canonical input manifest
- the reveal JSON
- the reveal SVG

No timestamp or machine-specific path is included, so identical inputs and code produce identical committed bytes.

## Boundary

This fixture is not:

- runtime truth
- identity proof
- canon evidence
- governance authority
- a claim of literal magnetism

It is a deterministic inspection artifact demonstrating how computed relation, orientation, possibility, and external refusal can be made visible.

# HRA Training Dataset Conversion Plan v0.1

**Adapter:** Harmonic Reflection Adapter v0.1  
**Source selection:** `accepted_candidate_selection_v0_1.json`  
**Accepted records:** 40  
**Status:** Conversion plan only  
**Dataset file created:** No  
**Training-ready:** No  

## Purpose

This plan defines how the 40 accepted candidates should later be converted into `hra_training_dataset_v0_1.jsonl`.

It does not create that dataset file.

It does not authorize LoRA / QLoRA training.

---

## Source of Truth

The conversion source is:

```text
accepted_candidate_selection_v0_1.json
```

Only records listed under `accepted_records` may be converted for v0.1.

Reserve, needs-rewrite, rejected, or retired records must not be copied into the dataset file.

---

## Conversion Output

Future output file:

```text
hra_training_dataset_v0_1.jsonl
```

Each line should contain one complete JSON object matching the HRA training example schema.

Minimum required fields per JSONL record:

```text
record_id
record_type
messages
tags
curation_notes
safety_boundary
quality_status
source_selection_ref
```

---

## Quality Status

All converted records must use:

```json
"quality_status": "accepted"
```

---

## Required Safety Boundary

Each converted record must preserve or derive safety fields:

```json
{
  "contains_private_reasoning": false,
  "claims_memory_authority": false,
  "claims_governance_authority": false,
  "claims_canon_authority": false,
  "creates_symbolic_dependency": false,
  "includes_sensitive_personal_material": false
}
```

If any accepted candidate cannot support these fields, stop conversion and return it to `needs_rewrite`.

---

## Conversion Rules

1. Pull candidate content only from the original batch candidate files.
2. Include only records listed as accepted in `accepted_candidate_selection_v0_1.json`.
3. Preserve prompt/response content exactly unless a separate rewrite review exists.
4. Do not include hidden chain-of-thought.
5. Do not add new examples during conversion.
6. Do not infer private or personal context.
7. Do not convert reserve records unless a later selection review promotes them.
8. Do not convert needs-rewrite records until rewritten and re-reviewed.
9. Keep each JSONL line compact and valid.
10. Run schema conformance review after conversion.

---

## Duplicate / Overfitting Check

Before writing the dataset file, inspect the accepted set for:

- repeated response openings
- repeated phrasing around `self guide`
- too many repo / PR examples
- too many internal Lumina / Ethereon examples
- too many humor-based returns
- too many correction-only examples
- too little positive reflection practice

If duplication risk is high, revise the accepted selection before conversion.

---

## Required Companion Artifacts

Before or alongside dataset creation, add:

- `training_dataset_card_update_v0_1.md`
- `jsonl_schema_conformance_note_v0_1.md`
- optionally, `accepted_candidate_conversion_receipt_v0_1.json`

---

## Dataset Creation Does Not Authorize Training

Creating `hra_training_dataset_v0_1.jsonl` would only create a dataset artifact.

Training remains blocked until:

- base model selection exists
- model license / use constraints are documented
- clean baseline eval exists
- training config exists
- training run plan exists
- post-training eval plan exists
- failure review process exists

---

## Closing Standard

Convert only what has been selected.

Train only what has been tested.

Receipts before reverence.

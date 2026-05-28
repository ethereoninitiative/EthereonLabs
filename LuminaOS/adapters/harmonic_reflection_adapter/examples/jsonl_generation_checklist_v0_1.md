# HRA JSONL Generation Checklist v0.1

**Adapter:** Harmonic Reflection Adapter v0.1  
**Future dataset:** `hra_training_dataset_v0_1.jsonl`  
**Status:** Generation checklist only  
**Dataset file created:** No  
**Training-ready:** No  

## Purpose

This checklist defines the safe manual or scripted process for generating the future JSONL dataset from accepted candidates.

It does not create the dataset.

It does not authorize LoRA / QLoRA training.

---

## Generation Order

1. Load `accepted_candidate_selection_v0_1.json`.
2. Read the list under `accepted_records`.
3. For each accepted `record_id`, locate the original record in its source batch file.
4. Copy only visible training fields.
5. Add `quality_status: accepted`.
6. Add `source_selection_ref: accepted_candidate_selection_v0_1`.
7. Add or preserve `source_batch`.
8. Preserve safety boundary fields.
9. Write exactly one JSON object per line.
10. Run schema conformance validation.
11. Create dataset creation receipt.
12. Stop.

---

## Do Not

Do not:

- include reserve records
- include needs-rewrite records
- include rejected records
- include retired records
- add new examples during generation
- rewrite candidate content during generation
- include hidden chain-of-thought
- include private/sensitive material
- infer memory, governance, canon, mode-legality, or capability authority
- treat dataset creation as training authorization

---

## Expected Record Count

Expected v0.1 JSONL record count:

```text
40
```

If the generated dataset contains anything other than exactly 40 records, stop and inspect.

---

## Required Validation Commands / Checks

A future script or manual check should verify:

```text
line_count == 40
all_lines_parse_as_json == true
all_record_ids_unique == true
all_record_ids_in_accepted_selection == true
no_unaccepted_records_present == true
all_quality_status == accepted
all_required_fields_present == true
all_safety_boundary_fields_false == true
```

---

## Required Fields

Each JSONL object must include:

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

Recommended additional fields:

```text
family
source_batch
review_notes
```

---

## Stop Conditions

Stop generation if:

- any accepted record cannot be found
- any record has malformed messages
- any record has missing safety boundary fields
- any safety boundary field is true
- any record contains hidden reasoning or sensitive material
- record count differs from expected
- any unaccepted record appears
- any script attempts to infer missing content

---

## Output Files For Future Dataset Creation

When actually creating the dataset, future output should include:

- `hra_training_dataset_v0_1.jsonl`
- `hra_training_dataset_creation_receipt_v0_1.json`

The dataset file should not be committed alone.

---

## Closing Standard

Generate exactly what was accepted.

Validate before reverence.

Training remains blocked.

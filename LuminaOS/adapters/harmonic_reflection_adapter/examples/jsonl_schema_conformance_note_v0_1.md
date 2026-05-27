# HRA JSONL Schema Conformance Note v0.1

**Adapter:** Harmonic Reflection Adapter v0.1  
**Future dataset:** `hra_training_dataset_v0_1.jsonl`  
**Status:** Schema conformance planning note  
**Dataset file created:** No  
**Training-ready:** No  

## Purpose

This note defines the schema checks that must pass before any accepted HRA records are converted into JSONL format.

It does not create a dataset file.

It does not authorize LoRA / QLoRA training.

---

## Required JSONL Shape

Each future JSONL line must be one valid JSON object.

Required fields:

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

Recommended optional fields:

```text
family
source_batch
review_notes
```

---

## Message Rules

Each `messages` array must contain only visible final-form content.

Allowed roles:

```text
system
user
assistant
```

Forbidden content:

- hidden chain-of-thought
- credentials or secrets
- sensitive personal material
- private third-party details
- unsupported memory claims
- governance / canon / runtime authority claims

---

## Safety Boundary Rules

Each record must include:

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

Any missing or true value must halt dataset creation until reviewed.

---

## Selection Rules

Only records listed under `accepted_records` in `accepted_candidate_selection_v0_1.json` may be converted.

Do not convert:

- reserve pool records
- needs-rewrite records
- rejected records
- retired records
- unreviewed candidates

---

## Validation Checklist

Before dataset creation, verify:

1. Every line parses as JSON.
2. Every record id is unique.
3. Every accepted record appears exactly once.
4. No unaccepted record appears.
5. Every record has required fields.
6. Every `messages` array contains valid roles.
7. Every safety boundary field exists and is false.
8. Every record has `quality_status: accepted`.
9. Every record has a `source_selection_ref`.
10. No hidden chain-of-thought or sensitive material is present.

---

## Boundary

Passing schema conformance would mean the dataset file is structurally valid.

It would not mean:

- the adapter is trained
- training is authorized
- the dataset is behaviorally sufficient
- HRA has runtime authority
- HRA has memory authority
- HRA has canon or governance authority

---

## Closing Standard

Schema validity is necessary, not sufficient.

Receipts before reverence.

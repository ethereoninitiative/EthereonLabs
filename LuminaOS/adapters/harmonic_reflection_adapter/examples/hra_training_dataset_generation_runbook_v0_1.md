# HRA Training Dataset Generation Runbook v0.1

**Adapter:** Harmonic Reflection Adapter v0.1  
**Generator:** `build_hra_training_dataset_v0_1.py`  
**Expected dataset output:** `hra_training_dataset_v0_1.jsonl`  
**Expected receipt output:** `hra_training_dataset_creation_receipt_v0_1.json`  
**Training-ready:** No  

## Purpose

This runbook explains how to generate the first HRA JSONL dataset artifact from the accepted candidate selection.

The generator converts only the 40 records listed in `accepted_candidate_selection_v0_1.json`.

It does not authorize LoRA / QLoRA training.

---

## Command

From the repository root:

```bash
python LuminaOS/adapters/harmonic_reflection_adapter/examples/build_hra_training_dataset_v0_1.py
```

Expected outputs:

```text
LuminaOS/adapters/harmonic_reflection_adapter/examples/hra_training_dataset_v0_1.jsonl
LuminaOS/adapters/harmonic_reflection_adapter/examples/hra_training_dataset_creation_receipt_v0_1.json
```

---

## Required Inputs

The script expects these files to exist beside it:

- `accepted_candidate_selection_v0_1.json`
- `training_candidates_batch_001_seed_v0_1.json`
- `training_candidates_batch_002_seed_v0_1.json`
- `training_candidates_batch_003_seed_v0_1.json`
- `training_candidates_batch_004_seed_v0_1.json`
- `training_candidates_batch_005_seed_v0_1.json`

---

## Built-In Checks

The generator verifies:

- exactly 40 accepted records
- every accepted record is found in source batches
- output order matches accepted selection order
- every record id is unique
- required fields exist
- message roles are valid
- safety boundary fields exist and are false
- JSONL reparses after writing
- receipt says training is not authorized

---

## Stop Conditions

Stop and repair if the generator reports:

- missing accepted record
- duplicate accepted record id
- invalid message role
- empty message content
- missing safety boundary field
- true safety boundary field
- record count other than 40
- JSONL parse failure

---

## Boundary

Running the generator creates a dataset artifact and receipt only.

It does not:

- authorize LoRA / QLoRA training
- select a base model
- create a training config
- create a training run plan
- create a post-training eval plan
- create runtime, canon, governance, memory, mode-legality, or capability authority

---

## Next Gate After Generation

After the dataset and receipt exist, the next safe gate is:

1. review generated JSONL and receipt
2. update dataset card with actual dataset file presence
3. create or run clean open-base-model baseline eval
4. only then consider training configuration planning

Receipts before reverence.

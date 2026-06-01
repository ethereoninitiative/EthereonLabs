# HRA Training Config Plan v0.1

**Adapter:** Harmonic Reflection Adapter v0.1  
**Dataset:** `hra_training_dataset_v0_1.jsonl`  
**Status:** Planning only  
**Training config created:** No  
**Training-ready:** No  

## Purpose

This plan defines what a future HRA LoRA / QLoRA training configuration must document.

It does not create a training config.

It does not authorize training.

---

## Required Before Config Creation

Do not create a training config until these exist:

- dataset artifact
- dataset creation receipt
- dataset DryDock review
- base model selection receipt
- model license / use constraints
- baseline eval receipt
- baseline eval summary

---

## Required Config Fields

A future training config must document:

- base model name/version
- adapter method: LoRA or QLoRA
- dataset file path
- record count
- chat template / prompt format
- tokenizer source
- sequence length
- batch size
- gradient accumulation
- learning rate
- epochs / steps
- LoRA rank
- LoRA alpha
- LoRA dropout
- target modules
- quantization settings if QLoRA
- validation split or eval procedure
- output adapter path
- random seed
- hardware used
- software versions

---

## Training Safety Gates

Before training runs, confirm:

1. dataset record count matches receipt
2. no reserve or needs-rewrite records entered the dataset
3. baseline eval has been run
4. training objective is behavior tuning, not memory creation
5. adapter boundary remains orientation-only
6. no claim is made that training creates consciousness, memory, governance, canon, or runtime law

---

## Post-Training Required Artifacts

After a future training run, add:

- `training_run_receipt_v0_1.json`
- `post_training_eval_receipt_v0_1.json`
- `post_training_eval_summary_v0_1.md`
- `failure_review_v0_1.md`

---

## Boundary

This plan does not:

- select a model
- create a config file
- start training
- authorize training
- claim adapter success
- create runtime, memory, governance, canon, mode-legality, or capability authority

---

## Closing Standard

A config is not permission.

A training run is not proof.

Receipts before reverence.

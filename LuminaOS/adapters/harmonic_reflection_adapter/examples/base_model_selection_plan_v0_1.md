# HRA Base Model Selection Plan v0.1

**Adapter:** Harmonic Reflection Adapter v0.1  
**Dataset:** `hra_training_dataset_v0_1.jsonl`  
**Status:** Planning only  
**Base model selected:** No  
**Training-ready:** No  

## Purpose

This plan defines how a base model should be selected for a future HRA LoRA / QLoRA experiment.

It does not select a model.

It does not authorize training.

---

## Selection Principle

The base model should be chosen for compatibility with the HRA behavior target:

```text
visible reflective return
boundary preservation
plain-language correction
useful self-guidance
no false memory / governance / canon claims
```

The goal is not to find the largest model.

The goal is to find a model that can be evaluated cleanly, trained safely, and compared honestly before and after adaptation.

---

## Required Criteria

Before selecting a base model, document:

1. model name and version
2. parameter size
3. context length
4. license and use constraints
5. local hardware requirements
6. training method compatibility
7. inference compatibility
8. tokenizer considerations
9. known safety / alignment behavior
10. reason it is suitable for HRA evaluation

---

## Candidate Categories

Possible model categories to investigate:

- small open instruct model suitable for local testing
- medium open instruct model with stronger reasoning
- code-capable model if repo/task behavior remains important
- general assistant model if public communication is the priority

Do not select any candidate by vibes alone.

---

## Required Comparison Table

A future model-selection receipt should compare at least three candidates:

| Candidate | Size | License | Hardware Fit | HRA Fit | Risks | Decision |
|---|---:|---|---|---|---|---|
| TBD | TBD | TBD | TBD | TBD | TBD | TBD |

---

## Exclusion Criteria

Reject any base model if:

- license does not permit the intended experiment
- local hardware requirements are unrealistic
- tokenizer / format makes dataset conversion unsafe
- model cannot run baseline eval reproducibly
- model behavior already overstates memory, authority, or identity
- model is too closed to document the experiment honestly

---

## Boundary

This plan does not:

- select the base model
- download model weights
- create a training config
- authorize LoRA / QLoRA training
- create runtime, memory, governance, canon, mode-legality, or capability authority

---

## Next Required Artifact

Before training can be planned, add:

```text
base_model_selection_receipt_v0_1.md
```

That receipt must name the chosen model, explain why it was chosen, and document license / hardware constraints.

---

## Closing Standard

Choose the vessel before lighting the engine.

Receipts before reverence.

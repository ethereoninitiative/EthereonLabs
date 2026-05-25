# HRA Eval Tool

This directory contains the first executable scaffold for Harmonic Reflection Adapter evaluation.

## Included

- `hra_eval_runner_v0_1.py`

## What it does

The runner builds structured evaluation receipts from visible model responses and manual/human scores.

It can:

- load `eval_prompts_v0_1.json`
- load a response map keyed by prompt id
- aggregate rubric scores
- collect fail flags
- emit a receipt JSON

## What it does not do

It does not:

- call a model
- train a LoRA / QLoRA adapter
- score responses automatically
- authorize governance, canon, memory, mode legality, or capability exposure
- store hidden chain-of-thought

## Example

From the repository root:

```bash
python LuminaOS/adapters/harmonic_reflection_adapter/tools/hra_eval_runner_v0_1.py \
  --model-id base-model-placeholder \
  --responses LuminaOS/adapters/harmonic_reflection_adapter/examples/sample_eval_responses_v0_1.json \
  --out /tmp/hra_eval_receipt_v0_1.json \
  --reviewer-notes "Sample fixture only"
```

## Boundary

Receipts are evaluation evidence only.

They do not become governance law.  
They do not promote canon.  
They do not prove memory.  
They do not make the adapter sovereign.

Receipts before reverence.

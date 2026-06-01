# HRA Baseline Response Generation Runbook v0.1

**Adapter:** Harmonic Reflection Adapter v0.1  
**Target model:** `Qwen/Qwen3-4B-Instruct-2507`  
**Generator:** `generate_hra_baseline_responses_v0_1.py`  
**Status:** Response-generation scaffold only  
**Scoring completed:** No  
**Training-ready:** No  

## Purpose

This runbook explains how to generate unscored baseline responses from the selected base model.

The goal is to measure the unadapted model before any HRA LoRA / QLoRA training is considered.

This does not authorize training.

---

## Install Dependencies

From a Python environment with sufficient memory / GPU support:

```bash
pip install "transformers>=4.51.0" torch accelerate
```

If the environment requires special CUDA wheels, install PyTorch according to the local CUDA setup first.

---

## Generate Unscored Baseline Responses

From the repository root:

```bash
python LuminaOS/adapters/harmonic_reflection_adapter/examples/generate_hra_baseline_responses_v0_1.py
```

Expected output:

```text
LuminaOS/adapters/harmonic_reflection_adapter/examples/baseline_eval_responses_unscored_v0_1.json
```

---

## Optional Settings

```bash
python LuminaOS/adapters/harmonic_reflection_adapter/examples/generate_hra_baseline_responses_v0_1.py \
  --model Qwen/Qwen3-4B-Instruct-2507 \
  --max-new-tokens 384 \
  --temperature 0.2
```

---

## Important Boundary

The generated file is unscored.

It is not a completed baseline eval.

It cannot produce `baseline_eval_receipt_v0_1.json` until a scored response file exists.

---

## Scoring Path

After generation:

1. Copy or rename `baseline_eval_responses_unscored_v0_1.json` to:

```text
baseline_eval_responses_v0_1.json
```

2. Fill numeric scores from 0 to 5 for every scoring dimension.
3. Add failure categories where needed.
4. Add review notes where useful.
5. Run:

```bash
python LuminaOS/adapters/harmonic_reflection_adapter/examples/run_hra_baseline_eval_v0_1.py \
  --responses LuminaOS/adapters/harmonic_reflection_adapter/examples/baseline_eval_responses_v0_1.json
```

Expected outputs after scoring:

```text
baseline_eval_receipt_v0_1.json
baseline_eval_summary_v0_1.md
```

---

## Do Not

Do not:

- load an HRA adapter
- train a LoRA / QLoRA adapter
- score automatically without human review
- treat unscored responses as an eval receipt
- commit model weights
- commit caches
- commit private tokens
- claim baseline success before review

---

## Suggested Git Ignore Safety

Before committing outputs, ensure local model cache directories are not included.

Never commit:

```text
.cache/
models/
*.safetensors
*.bin
*.pt
*.gguf
```

---

## Closing Standard

Generate first.

Score second.

Receipt third.

Train never by implication.

Receipts before reverence.

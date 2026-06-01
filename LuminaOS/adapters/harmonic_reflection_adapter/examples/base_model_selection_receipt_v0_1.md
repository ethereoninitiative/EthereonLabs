# HRA Base Model Selection Receipt v0.1

**Adapter:** Harmonic Reflection Adapter v0.1  
**Dataset:** `hra_training_dataset_v0_1.jsonl`  
**Receipt status:** Baseline target selected  
**Selected for baseline eval:** Yes  
**Selected for training:** No  
**Training-ready:** No  

## Purpose

This receipt selects a first baseline-evaluation target model for HRA.

It does not authorize LoRA / QLoRA training.

It does not create a training config.

It does not claim HRA effectiveness.

---

## Selected Baseline Target

```text
Qwen/Qwen3-4B-Instruct-2507
```

Selection status:

```text
baseline evaluation target only
```

This model is selected as the first baseline target because it is small enough for practical local / modest-cloud evaluation, has an Apache-2.0 license on its public model card, supports standard Hugging Face / vLLM / SGLang workflows, has a strong instruction-following profile, and is explicitly described as non-thinking mode that does not emit `<think></think>` blocks.

That last point is useful for HRA because the adapter target is visible reflective behavior, not hidden chain-of-thought imitation.

---

## Evidence Snapshot

Evidence checked from public model cards / primary model pages on 2026-05-31.

| Candidate | Size | License | Notes | Decision |
|---|---:|---|---|---|
| `Qwen/Qwen3-4B-Instruct-2507` | 4.0B | Apache-2.0 | Strong practical fit; non-thinking mode; large context; supported by Transformers/vLLM/SGLang. | selected for baseline |
| `Qwen/Qwen2.5-7B-Instruct` | 7.61B | Apache-2.0 | Strong fallback; mature; larger than necessary for first pass. | reserve |
| `mistralai/Mistral-7B-Instruct-v0.3` | 7B | Apache-2.0 | Mature and permissive; good alternate; tokenizer/tooling differences need care. | reserve |
| `meta-llama/Llama-3.2-3B-Instruct` | 3B | Llama 3.2 Community License | Small and useful, but custom/gated license makes it less clean as first baseline. | not first target |

---

## Why Qwen3-4B-Instruct-2507 First

HRA v0.1 needs a model that can be tested without turning the experiment into infrastructure mud.

`Qwen/Qwen3-4B-Instruct-2507` is a strong first target because:

1. 4B parameter size is more practical than 7B+ for early iteration.
2. Apache-2.0 license is cleaner for experimental adaptation planning than custom gated licenses.
3. The model card states it is non-thinking mode and does not generate `<think></think>` blocks.
4. HRA wants visible reflective stance, not hidden reasoning traces.
5. Transformers / vLLM / SGLang support makes baseline eval easier to reproduce.
6. The model’s instruction-following and writing strengths align with HRA response-style evaluation.

---

## What This Does Not Mean

This selection does not mean:

- Qwen3-4B is the final HRA model
- training is authorized
- QLoRA should begin
- HRA is proven
- adapter behavior is safe
- the dataset is sufficient for final use
- any model now has memory, governance, canon, runtime, mode-legality, or capability authority

---

## Required Before Training

Still required:

1. baseline eval run against `Qwen/Qwen3-4B-Instruct-2507`
2. baseline eval receipt
3. baseline eval summary
4. training config proposal
5. training config DryDock review
6. explicit training authorization receipt
7. post-training eval plan

---

## Initial Baseline Command Sketch

A future eval runner may load:

```text
model: Qwen/Qwen3-4B-Instruct-2507
dataset: hra_training_dataset_v0_1.jsonl
eval prompts: baseline_eval_prompt_set_v0_1.json
```

Suggested inference posture for baseline:

```text
temperature: 0.2-0.7 range, documented per run
max_new_tokens: enough for full answers without encouraging ramble
fixed seed where framework supports it
no adapter loaded
```

---

## Boundary

This receipt does not:

- download model weights
- run inference
- run baseline evaluation
- create training config
- authorize LoRA / QLoRA training
- create runtime, memory, governance, canon, mode-legality, or capability authority

---

## Closing Standard

A vessel has been chosen for first measurement.

The engine remains cold.

Receipts before reverence.

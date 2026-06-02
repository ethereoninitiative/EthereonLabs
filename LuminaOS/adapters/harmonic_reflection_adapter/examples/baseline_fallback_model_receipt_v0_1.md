# HRA Baseline Fallback Model Receipt v0.1

**Adapter:** Harmonic Reflection Adapter v0.1  
**Preferred baseline target:** `Qwen/Qwen3-4B-Instruct-2507`  
**Fallback target:** `Qwen/Qwen3-0.6B`  
**Fallback status:** Smoke / plumbing fallback  
**Selected for preferred baseline:** No  
**Selected for training:** No  
**Training-ready:** No  

## Purpose

This receipt selects `Qwen/Qwen3-0.6B` as the first compute fallback after the preferred Qwen3-4B smoke test stalled during first-prompt generation on the available local/Codex environment.

This fallback is selected to prove that the baseline generation machinery can run end-to-end on constrained hardware.

It is not selected as the preferred HRA quality baseline.

It does not authorize LoRA / QLoRA training.

---

## Decision

```json
{
  "preferred_baseline_target": "Qwen/Qwen3-4B-Instruct-2507",
  "fallback_target": "Qwen/Qwen3-0.6B",
  "fallback_use": "smoke_and_plumbing_baseline_only",
  "preferred_target_replaced": false,
  "training_authorized": false
}
```

---

## Why Fallback Is Needed

The Qwen3-4B smoke attempt reached:

```text
model downloaded / cached
model loaded
HRA-EVAL-0001 generation began
no output JSON written before stopping
```

This indicates compute friction rather than an HRA dataset or script failure.

The fallback model is needed to determine whether the baseline-generation path itself works on available hardware.

---

## Evidence Snapshot

Evidence checked from public model cards / primary model pages on 2026-06-02.

| Field | Evidence |
|---|---|
| Model id | `Qwen/Qwen3-0.6B` |
| License | Apache-2.0 on public Hugging Face model card |
| Task | Text generation / conversational |
| Parameters | 0.6B parameters, 0.44B non-embedding parameters |
| Context length | 32,768 tokens |
| Tooling | Transformers, vLLM, SGLang, Docker Model Runner, local apps |
| Thinking behavior | Supports thinking and non-thinking mode; non-thinking mode must be used for HRA baseline smoke unless separately justified |

---

## Use Boundary

`Qwen/Qwen3-0.6B` may be used for:

- one-prompt smoke generation
- three-prompt smoke generation
- verifying JSON output shape
- verifying no-adapter baseline path
- verifying scoring/receipt machinery after manual review

It must not be treated as:

- the preferred HRA quality baseline
- proof that HRA works
- proof that the dataset is sufficient
- authorization to train
- a replacement for the Qwen3-4B baseline if stronger compute becomes available

---

## Required Settings

For HRA fallback smoke generation:

```text
model: Qwen/Qwen3-0.6B
enable_thinking: false
adapter_loaded: false
training_authorized: false
max_prompts: 1 first, then 3 if successful
```

The fallback should avoid `<think>...</think>` output because HRA evaluates visible reflective return, not hidden reasoning imitation.

---

## Next Command

First fallback smoke:

```bash
python LuminaOS/adapters/harmonic_reflection_adapter/examples/generate_hra_baseline_responses_v0_1.py \
  --model Qwen/Qwen3-0.6B \
  --max-prompts 1 \
  --max-new-tokens 160 \
  --temperature 0.2 \
  --out LuminaOS/adapters/harmonic_reflection_adapter/examples/baseline_eval_responses_smoke_qwen3_06b_v0_1.json
```

---

## Boundary

This receipt does not:

- run inference
- create model responses
- score responses
- generate a baseline receipt
- authorize LoRA / QLoRA training
- create a training config
- create runtime, memory, governance, canon, mode-legality, or capability authority

---

## Closing Standard

This is the tiny vessel.

It proves the canal before we sail the sea.

Receipts before reverence.

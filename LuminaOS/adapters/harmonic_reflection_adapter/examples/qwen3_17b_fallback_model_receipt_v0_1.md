# Qwen3 1.7B Fallback Model Receipt v0.1

**Adapter:** Harmonic Reflection Adapter v0.1  
**Preferred baseline target:** `Qwen/Qwen3-4B-Instruct-2507`  
**Fallback target:** `Qwen/Qwen3-1.7B`  
**Fallback status:** Smoke / plumbing fallback candidate  
**Selected for preferred baseline:** No  
**Selected for training:** No  
**Training-ready:** No  
**Origin issue:** #360  

## Purpose

This receipt records `Qwen/Qwen3-1.7B` as the next HRA fallback smoke target after the preferred Qwen3-4B target stalled during first-prompt generation on available local/Codex compute and the Qwen3-0.6B fallback proved plumbing while producing weak/generic output.

This fallback is selected to test whether a somewhat larger Qwen3 dense model can preserve the same no-adapter baseline smoke path while remaining more feasible than the preferred 4B target on constrained compute.

It is not selected as the preferred HRA quality baseline.

It does not authorize LoRA / QLoRA training.

---

## Decision

```json
{
  "preferred_baseline_target": "Qwen/Qwen3-4B-Instruct-2507",
  "fallback_target": "Qwen/Qwen3-1.7B",
  "fallback_use": "smoke_and_plumbing_baseline_only",
  "preferred_target_replaced": false,
  "training_authorized": false,
  "adapter_loaded": false,
  "scoring_authorized_from_smoke_alone": false
}
```

---

## Why This Fallback Is Needed

The HRA baseline path currently has three evidence points:

1. The preferred Qwen3-4B path remains the intended baseline target but stalled during first-prompt generation on available compute.
2. The Qwen3-0.6B fallback smoke path proved that the generator and output plumbing can run.
3. The Qwen3-0.6B response quality was weak/generic, so it should remain smoke/plumbing evidence only.

`Qwen/Qwen3-1.7B` is a bounded next step between those points.

It should test improved fallback viability without changing the preferred target or authorizing training.

---

## Evidence Snapshot

Evidence checked from public model cards / primary model pages on 2026-06-17 UTC.

| Field | Evidence |
|---|---|
| Model id | `Qwen/Qwen3-1.7B` |
| Source | Hugging Face public model card and Qwen Qwen3 release post |
| License | Apache-2.0 on Hugging Face model card; Qwen release post lists Qwen3-1.7B among Apache-2.0 dense models |
| Task | Text generation / conversational |
| Parameters | 1.7B parameters; 1.4B non-embedding parameters |
| Layers | 28 |
| Attention heads | 16 Q heads / 8 KV heads |
| Context length | 32,768 tokens |
| Tooling | Transformers, vLLM, SGLang, Docker Model Runner, local apps |
| Thinking behavior | Supports thinking and non-thinking mode; non-thinking mode must be used for HRA fallback smoke unless separately justified |

Primary evidence URLs:

```text
https://huggingface.co/Qwen/Qwen3-1.7B
https://qwenlm.github.io/blog/qwen3/
```

---

## Use Boundary

`Qwen/Qwen3-1.7B` may be used for:

- one-prompt smoke generation
- three-prompt smoke generation if the one-prompt smoke succeeds
- verifying JSON output shape
- verifying no-adapter baseline path
- comparing fallback viability against the prior 0.6B smoke result after manual review

It must not be treated as:

- the preferred HRA quality baseline
- proof that HRA works
- proof that the dataset is sufficient
- authorization to train
- authorization to score automatically
- a replacement for the Qwen3-4B baseline if stronger compute becomes available

---

## Required Settings

For HRA fallback smoke generation:

```text
model: Qwen/Qwen3-1.7B
enable_thinking: false
adapter_loaded: false
training_authorized: false
scoring_authorized: false
max_prompts: 1 first, then 3 if successful
```

The fallback should avoid `<think>...</think>` output because HRA evaluates visible reflective return, not hidden reasoning imitation.

---

## Next Command

First fallback smoke:

```bash
python LuminaOS/adapters/harmonic_reflection_adapter/examples/generate_hra_baseline_responses_v0_1.py \
  --model Qwen/Qwen3-1.7B \
  --max-prompts 1 \
  --max-new-tokens 192 \
  --temperature 0.2 \
  --no-enable-thinking \
  --out LuminaOS/adapters/harmonic_reflection_adapter/examples/baseline_eval_responses_smoke_qwen3_17b_v0_1.json
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

This is a larger smoke vessel, not the flagship.

It tests the channel before the channel is trusted.

Receipts before reverence.

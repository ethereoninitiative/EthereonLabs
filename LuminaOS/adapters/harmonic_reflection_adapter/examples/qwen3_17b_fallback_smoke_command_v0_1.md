# Qwen3 1.7B Fallback Smoke Command v0.1

**Adapter:** Harmonic Reflection Adapter v0.1  
**Preferred baseline target:** `Qwen/Qwen3-4B-Instruct-2507`  
**Fallback smoke target:** `Qwen/Qwen3-1.7B`  
**Status:** Command packet only  
**Training-ready:** No  
**Training authorized:** No  
**Origin issue:** #360  

## Purpose

This command packet gives the exact Qwen3-1.7B fallback smoke command after:

1. Qwen3-4B stalled during first-prompt generation on available local/Codex compute.
2. Qwen3-0.6B proved smoke/plumbing viability but produced weak/generic output.

This fallback is for smoke/plumbing only.

It does not replace the preferred baseline target.

It does not authorize training, scoring, or adapter loading.

---

## One-Prompt Fallback Smoke

Run from the repository root:

```bash
python LuminaOS/adapters/harmonic_reflection_adapter/examples/generate_hra_baseline_responses_v0_1.py \
  --model Qwen/Qwen3-1.7B \
  --max-prompts 1 \
  --max-new-tokens 192 \
  --temperature 0.2 \
  --no-enable-thinking \
  --out LuminaOS/adapters/harmonic_reflection_adapter/examples/baseline_eval_responses_smoke_qwen3_17b_v0_1.json
```

Expected output:

```text
LuminaOS/adapters/harmonic_reflection_adapter/examples/baseline_eval_responses_smoke_qwen3_17b_v0_1.json
```

---

## If One Prompt Passes

Then try three prompts:

```bash
python LuminaOS/adapters/harmonic_reflection_adapter/examples/generate_hra_baseline_responses_v0_1.py \
  --model Qwen/Qwen3-1.7B \
  --max-prompts 3 \
  --max-new-tokens 224 \
  --temperature 0.2 \
  --no-enable-thinking \
  --out LuminaOS/adapters/harmonic_reflection_adapter/examples/baseline_eval_responses_smoke_qwen3_17b_3prompt_v0_1.json
```

Expected output:

```text
LuminaOS/adapters/harmonic_reflection_adapter/examples/baseline_eval_responses_smoke_qwen3_17b_3prompt_v0_1.json
```

---

## Review Gate After Smoke

If a smoke JSON is generated successfully, review it before any next step.

Manual review should check:

- output JSON exists and parses
- prompt id and model metadata are present
- `enable_thinking` is false in metadata
- no `<think>...</think>` trace is emitted
- responses are visibly final-form answers
- no adapter was loaded
- no scoring was run
- no baseline receipt was generated from smoke alone

Only after review should a separate DryDock review receipt be considered.

---

## Boundary

Do not train.

Do not load an HRA adapter.

Do not score automatically.

Do not create a baseline receipt from smoke output alone.

Do not commit model weights, caches, or local environment artifacts.

Do not treat Qwen3-1.7B output as the preferred HRA quality baseline.

Do not replace `Qwen/Qwen3-4B-Instruct-2507` unless a separate selection receipt explicitly does so.

Receipts before reverence.

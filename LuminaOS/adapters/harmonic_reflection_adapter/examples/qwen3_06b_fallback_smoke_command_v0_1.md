# Qwen3 0.6B Fallback Smoke Command v0.1

**Adapter:** Harmonic Reflection Adapter v0.1  
**Preferred baseline target:** `Qwen/Qwen3-4B-Instruct-2507`  
**Fallback smoke target:** `Qwen/Qwen3-0.6B`  
**Status:** Command packet only  
**Training-ready:** No  
**Training authorized:** No  

## Purpose

This command packet gives the exact fallback smoke command after Qwen3-4B stalled during first-prompt generation on available local/Codex compute.

This fallback is for smoke/plumbing only.

It does not replace the preferred baseline target.

---

## One-Prompt Fallback Smoke

Run from the repository root:

```bash
python LuminaOS/adapters/harmonic_reflection_adapter/examples/generate_hra_baseline_responses_v0_1.py \
  --model Qwen/Qwen3-0.6B \
  --max-prompts 1 \
  --max-new-tokens 160 \
  --temperature 0.2 \
  --no-enable-thinking \
  --out LuminaOS/adapters/harmonic_reflection_adapter/examples/baseline_eval_responses_smoke_qwen3_06b_v0_1.json
```

Expected output:

```text
LuminaOS/adapters/harmonic_reflection_adapter/examples/baseline_eval_responses_smoke_qwen3_06b_v0_1.json
```

---

## If One Prompt Passes

Then try three prompts:

```bash
python LuminaOS/adapters/harmonic_reflection_adapter/examples/generate_hra_baseline_responses_v0_1.py \
  --model Qwen/Qwen3-0.6B \
  --max-prompts 3 \
  --max-new-tokens 192 \
  --temperature 0.2 \
  --no-enable-thinking \
  --out LuminaOS/adapters/harmonic_reflection_adapter/examples/baseline_eval_responses_smoke_qwen3_06b_3prompt_v0_1.json
```

---

## Boundary

Do not train.

Do not load an HRA adapter.

Do not score automatically.

Do not create a baseline receipt from smoke output alone.

Do not commit model weights, caches, or local environment artifacts.

Do not treat Qwen3-0.6B output as the preferred HRA quality baseline.

Receipts before reverence.

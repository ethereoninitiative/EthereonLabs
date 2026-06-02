# HRA Baseline Smoke Eval Plan v0.1

**Adapter:** Harmonic Reflection Adapter v0.1  
**Preferred baseline target:** `Qwen/Qwen3-4B-Instruct-2507`  
**Status:** Smoke-test planning  
**Training-ready:** No  
**Training authorized:** No  

## Purpose

This plan defines a small baseline-generation smoke test before attempting the full 12-prompt baseline run.

The smoke test exists to verify compute feasibility, not HRA quality.

---

## Smoke Prompt Count

Recommended first attempt:

```text
1 prompt
```

Recommended second attempt if the first passes:

```text
3 prompts
```

Only after 3 prompts complete should the full 12-prompt run be attempted.

---

## Command Shape

Preferred model smoke test:

```bash
python LuminaOS/adapters/harmonic_reflection_adapter/examples/generate_hra_baseline_responses_v0_1.py \
  --model Qwen/Qwen3-4B-Instruct-2507 \
  --max-prompts 1 \
  --max-new-tokens 192 \
  --temperature 0 \
  --out LuminaOS/adapters/harmonic_reflection_adapter/examples/baseline_eval_responses_smoke_qwen3_4b_v0_1.json
```

If that succeeds, try:

```bash
python LuminaOS/adapters/harmonic_reflection_adapter/examples/generate_hra_baseline_responses_v0_1.py \
  --model Qwen/Qwen3-4B-Instruct-2507 \
  --max-prompts 3 \
  --max-new-tokens 256 \
  --temperature 0.2 \
  --out LuminaOS/adapters/harmonic_reflection_adapter/examples/baseline_eval_responses_smoke_qwen3_4b_3prompt_v0_1.json
```

---

## Smoke Success Criteria

A smoke test passes if:

- output JSON is written
- every requested prompt has a non-empty model response
- `adapter_loaded` is false
- `training_authorized` is false
- `scoring_completed` is false
- no model weights/cache artifacts are staged
- run notes identify model, prompt count, and settings

---

## Smoke Failure Criteria

A smoke test fails if:

- model cannot load
- generation does not complete first prompt
- output JSON is not written
- local process stalls beyond practical session limits
- disk/CPU offload makes completion unreasonable
- dependency install cannot complete

---

## Result Handling

Smoke outputs are diagnostic artifacts.

They should not be treated as completed baseline evaluation.

If committed, they must be labeled as smoke outputs only and not used for training decisions.

---

## Boundary

This plan does not:

- run smoke eval
- score responses
- create a baseline receipt
- authorize training
- change the selected baseline target
- select a fallback model

---

## Closing Standard

Do one prompt before asking the machine for twelve.

Receipts before reverence.

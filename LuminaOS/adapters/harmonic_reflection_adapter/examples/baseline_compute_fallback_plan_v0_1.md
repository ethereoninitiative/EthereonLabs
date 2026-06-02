# HRA Baseline Compute Fallback Plan v0.1

**Adapter:** Harmonic Reflection Adapter v0.1  
**Preferred baseline target:** `Qwen/Qwen3-4B-Instruct-2507`  
**Status:** Compute fallback planning  
**Training-ready:** No  
**Training authorized:** No  

## Purpose

This plan records the compute-aware fallback path after the first local/Codex attempt to generate Qwen3-4B baseline responses stalled during prompt generation.

The failed attempt did not indicate a dataset, script, or HRA architecture failure.

It indicated local inference friction.

---

## Observed Blocker

The prior attempt reached this stage:

```text
model downloaded / cached
model loaded
first prompt generation began
no output file written before process stopped
```

No adapter was loaded.

No scoring occurred.

No training config or model weights were committed.

No baseline receipt was produced.

---

## Interpretation

This is a compute limitation, not an HRA failure.

Probable causes:

- 4B model too heavy for local/Codex CPU or disk-offloaded inference
- insufficient GPU / VRAM
- slow first-token generation under offload
- session time / connectivity limits

---

## Preferred Target Remains

The preferred target remains:

```text
Qwen/Qwen3-4B-Instruct-2507
```

Reason: it is already documented as the selected baseline target and remains the stronger first full baseline if adequate compute is available.

---

## Fallback Target Class

If Qwen3-4B cannot complete a smoke test, use a smaller Qwen3 instruct-class model for local baseline plumbing only.

Recommended fallback class:

```text
Qwen3 dense instruct-class model in the 0.6B-1.7B range
```

A specific fallback model must be verified from its current model card before use, including:

- exact model id
- license
- instruction/chat template compatibility
- thinking/non-thinking behavior
- hardware fit

Do not silently swap the baseline target without a receipt.

---

## Fallback Receipt Required

Before using a fallback model for committed baseline responses, add:

```text
baseline_fallback_model_receipt_v0_1.md
```

The receipt must state:

- preferred model remains Qwen3-4B
- fallback model id
- why fallback is needed
- evidence checked
- whether fallback is smoke-only or full-baseline eligible
- training remains unauthorized

---

## Smoke Test Before Full Run

Before attempting all 12 prompts, run only 1-3 prompts.

Success criteria:

- model loads
- first prompt completes
- output JSON is written
- adapter_loaded remains false
- training_authorized remains false
- no weights/cache files are committed

---

## Decision Ladder

1. Try smoke test with Qwen3-4B.
2. If Qwen3-4B smoke passes, run full Qwen3-4B baseline response generation.
3. If Qwen3-4B smoke fails due to compute, create fallback model receipt.
4. Try smoke test with verified smaller fallback.
5. If fallback smoke passes, run fallback full baseline response generation and label it as fallback baseline, not preferred baseline.
6. Do not train from any baseline result without later training authorization.

---

## Boundary

This plan does not:

- select a fallback model
- run inference
- score responses
- create a baseline receipt
- authorize LoRA / QLoRA training
- change the dataset
- create runtime, memory, governance, canon, mode-legality, or capability authority

---

## Closing Standard

Do not mistake hardware exhaustion for epistemic failure.

Measure what can run.

Name what cannot.

Receipts before reverence.

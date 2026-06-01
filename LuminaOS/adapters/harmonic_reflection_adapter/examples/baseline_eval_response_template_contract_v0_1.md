# HRA Baseline Eval Response Template Contract v0.1

**Adapter:** Harmonic Reflection Adapter v0.1  
**Target model:** `Qwen/Qwen3-4B-Instruct-2507`  
**Status:** Response template contract only  
**Eval run completed:** No  
**Training-ready:** No  

## Purpose

This contract defines the expected response file shape for future baseline evaluation.

It does not contain model responses.

It does not run eval.

It does not authorize LoRA / QLoRA training.

---

## Response File Name

Future response file:

```text
baseline_eval_responses_v0_1.json
```

Do not confuse this with the generated template file:

```text
baseline_eval_response_template_v0_1.json
```

---

## Required Top-Level Fields

```json
{
  "response_set_id": "hra_baseline_eval_responses_v0_1",
  "target_model": "Qwen/Qwen3-4B-Instruct-2507",
  "eval_set_id": "hra_baseline_eval_prompt_set_v0_1",
  "eval_run_completed": true,
  "training_authorized": false,
  "responses": []
}
```

---

## Required Response Fields

Each response object must include:

```json
{
  "prompt_id": "HRA-EVAL-0001",
  "model_response": "...",
  "scores": {
    "boundary_preservation": 0,
    "useful_return": 0,
    "reflection_visibility": 0,
    "correction_quality": 0,
    "verification_discipline": 0,
    "anti_bloat_restraint": 0,
    "human_tone": 0
  },
  "failure_categories": [],
  "review_notes": ""
}
```

Scores must be numeric values from 0 to 5.

---

## Required Prompt Coverage

The response file must include exactly one response for each prompt in `baseline_eval_prompt_set_v0_1.json`.

The response order must match prompt order.

---

## Boundary

The response file must not include:

- adapted model responses
- LoRA / QLoRA outputs
- hidden chain-of-thought
- private or sensitive material
- training authorization claims
- runtime, canon, governance, memory, mode-legality, or capability authority claims

---

## Closing Standard

Responses measure the unadapted vessel.

They do not light the engine.

Receipts before reverence.

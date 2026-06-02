#!/usr/bin/env python3
"""Generate unscored HRA baseline responses with a local Hugging Face model.

This script reads baseline_eval_prompt_set_v0_1.json, runs the selected base
model with no adapter loaded, and writes baseline_eval_responses_unscored_v0_1.json.

It supports smoke runs through --max-prompts so compute feasibility can be tested
before attempting the full baseline.

It also supports Qwen chat-template thinking-mode control so HRA baseline smoke
runs can request visible final-form answers without <think> traces.

It does not train, score, create a baseline receipt, or authorize LoRA/QLoRA.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
DEFAULT_PROMPTS = ROOT / "baseline_eval_prompt_set_v0_1.json"
DEFAULT_OUTPUT = ROOT / "baseline_eval_responses_unscored_v0_1.json"
DEFAULT_MODEL = "Qwen/Qwen3-4B-Instruct-2507"

SCORING_DIMENSIONS = [
    "boundary_preservation",
    "useful_return",
    "reflection_visibility",
    "correction_quality",
    "verification_discipline",
    "anti_bloat_restraint",
    "human_tone",
]


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, data: dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def validate_prompt_set(prompt_set: dict[str, Any]) -> list[dict[str, Any]]:
    prompts = prompt_set.get("prompts")
    if not isinstance(prompts, list) or not prompts:
        raise ValueError("prompt set must contain a non-empty prompts array")
    seen: set[str] = set()
    for prompt in prompts:
        prompt_id = prompt.get("prompt_id")
        if not isinstance(prompt_id, str) or not prompt_id:
            raise ValueError("prompt missing prompt_id")
        if prompt_id in seen:
            raise ValueError(f"duplicate prompt_id: {prompt_id}")
        seen.add(prompt_id)
        messages = prompt.get("messages")
        if not isinstance(messages, list) or not messages:
            raise ValueError(f"{prompt_id} missing messages")
        for message in messages:
            if message.get("role") not in {"system", "user", "assistant"}:
                raise ValueError(f"{prompt_id} has invalid message role: {message.get('role')!r}")
            if not isinstance(message.get("content"), str) or not message["content"].strip():
                raise ValueError(f"{prompt_id} has empty message content")
    return prompts


def select_prompts(prompts: list[dict[str, Any]], max_prompts: int | None) -> list[dict[str, Any]]:
    if max_prompts is None:
        return prompts
    if max_prompts < 1:
        raise ValueError("--max-prompts must be >= 1 when provided")
    if max_prompts > len(prompts):
        raise ValueError(f"--max-prompts {max_prompts} exceeds prompt count {len(prompts)}")
    return prompts[:max_prompts]


def load_model(model_name: str):
    try:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
    except ImportError as exc:
        raise SystemExit(
            "Missing dependencies. Install with: pip install 'transformers>=4.51.0' torch accelerate"
        ) from exc

    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype="auto",
        device_map="auto",
        trust_remote_code=True,
    )
    return tokenizer, model


def chat_template_text(tokenizer, messages: list[dict[str, str]], enable_thinking: bool | None) -> str:
    template_kwargs: dict[str, Any] = {
        "tokenize": False,
        "add_generation_prompt": True,
    }
    if enable_thinking is not None:
        template_kwargs["enable_thinking"] = enable_thinking

    try:
        return tokenizer.apply_chat_template(messages, **template_kwargs)
    except TypeError:
        if enable_thinking is not None:
            print("Tokenizer chat template does not accept enable_thinking; continuing without that flag.")
        template_kwargs.pop("enable_thinking", None)
        return tokenizer.apply_chat_template(messages, **template_kwargs)


def generate_response(
    tokenizer,
    model,
    messages: list[dict[str, str]],
    max_new_tokens: int,
    temperature: float,
    enable_thinking: bool | None,
) -> str:
    import torch

    text = chat_template_text(tokenizer, messages, enable_thinking)
    model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

    generation_kwargs: dict[str, Any] = {
        "max_new_tokens": max_new_tokens,
        "pad_token_id": tokenizer.eos_token_id,
    }
    if temperature <= 0:
        generation_kwargs["do_sample"] = False
    else:
        generation_kwargs["do_sample"] = True
        generation_kwargs["temperature"] = temperature

    with torch.no_grad():
        generated_ids = model.generate(**model_inputs, **generation_kwargs)

    new_tokens = generated_ids[0][model_inputs.input_ids.shape[-1]:]
    return tokenizer.decode(new_tokens, skip_special_tokens=True).strip()


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate unscored HRA baseline responses.")
    parser.add_argument("--prompts", type=Path, default=DEFAULT_PROMPTS)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--max-new-tokens", type=int, default=384)
    parser.add_argument("--temperature", type=float, default=0.2)
    parser.add_argument("--max-prompts", type=int, default=None, help="Limit generation to the first N prompts for smoke testing.")
    parser.add_argument(
        "--enable-thinking",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Pass enable_thinking to chat templates that support it. Default is --no-enable-thinking for HRA baselines.",
    )
    args = parser.parse_args()

    prompt_set = load_json(args.prompts)
    all_prompts = validate_prompt_set(prompt_set)
    prompts = select_prompts(all_prompts, args.max_prompts)

    print(f"Loading model: {args.model}")
    tokenizer, model = load_model(args.model)

    responses = []
    for prompt in prompts:
        prompt_id = prompt["prompt_id"]
        print(f"Generating {prompt_id}...")
        model_response = generate_response(
            tokenizer=tokenizer,
            model=model,
            messages=prompt["messages"],
            max_new_tokens=args.max_new_tokens,
            temperature=args.temperature,
            enable_thinking=args.enable_thinking,
        )
        responses.append({
            "prompt_id": prompt_id,
            "model_response": model_response,
            "scores": {dimension: None for dimension in SCORING_DIMENSIONS},
            "failure_categories": [],
            "review_notes": ""
        })

    output = {
        "response_set_id": "hra_baseline_eval_responses_unscored_v0_1",
        "target_model": args.model,
        "eval_set_id": prompt_set.get("eval_set_id", "hra_baseline_eval_prompt_set_v0_1"),
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "eval_run_completed": False,
        "scoring_completed": False,
        "training_authorized": False,
        "generation_settings": {
            "max_new_tokens": args.max_new_tokens,
            "temperature": args.temperature,
            "adapter_loaded": False,
            "max_prompts": args.max_prompts,
            "prompt_count_requested": len(prompts),
            "prompt_count_total": len(all_prompts),
            "smoke_run": args.max_prompts is not None and args.max_prompts < len(all_prompts),
            "enable_thinking": args.enable_thinking,
        },
        "responses": responses,
    }
    write_json(args.out, output)
    print(f"Wrote unscored baseline responses: {args.out}")
    print(f"Generated {len(responses)} of {len(all_prompts)} prompts.")
    print("Scoring still required. Training remains unauthorized.")


if __name__ == "__main__":
    main()

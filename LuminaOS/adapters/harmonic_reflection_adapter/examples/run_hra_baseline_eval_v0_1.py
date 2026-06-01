#!/usr/bin/env python3
"""HRA baseline eval runner scaffold v0.1.

This script validates the HRA baseline prompt set and, when provided with a
manual/model response file, generates a baseline eval receipt and summary.

It does not call a model API, download weights, train an adapter, or authorize
LoRA / QLoRA training.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any

ROOT = Path(__file__).resolve().parent
DEFAULT_PROMPTS = ROOT / "baseline_eval_prompt_set_v0_1.json"
DEFAULT_RESPONSE_TEMPLATE = ROOT / "baseline_eval_response_template_v0_1.json"
DEFAULT_RECEIPT = ROOT / "baseline_eval_receipt_v0_1.json"
DEFAULT_SUMMARY = ROOT / "baseline_eval_summary_v0_1.md"

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

    seen_ids: set[str] = set()
    for prompt in prompts:
        prompt_id = prompt.get("prompt_id")
        if not prompt_id or not isinstance(prompt_id, str):
            raise ValueError("each prompt must have a string prompt_id")
        if prompt_id in seen_ids:
            raise ValueError(f"duplicate prompt_id: {prompt_id}")
        seen_ids.add(prompt_id)

        messages = prompt.get("messages")
        if not isinstance(messages, list) or not messages:
            raise ValueError(f"{prompt_id} must have non-empty messages")
        for message in messages:
            if message.get("role") not in {"system", "user", "assistant"}:
                raise ValueError(f"{prompt_id} has invalid role: {message.get('role')!r}")
            if not isinstance(message.get("content"), str) or not message["content"].strip():
                raise ValueError(f"{prompt_id} has empty message content")

        if not isinstance(prompt.get("expected_behavior"), str) or not prompt["expected_behavior"].strip():
            raise ValueError(f"{prompt_id} must have expected_behavior")

    return prompts


def make_response_template(prompt_set: dict[str, Any]) -> dict[str, Any]:
    prompts = validate_prompt_set(prompt_set)
    return {
        "response_set_id": "hra_baseline_eval_responses_v0_1",
        "target_model": prompt_set.get("target_model", "TBD"),
        "eval_set_id": prompt_set.get("eval_set_id", "hra_baseline_eval_prompt_set_v0_1"),
        "eval_run_completed": False,
        "training_authorized": False,
        "responses": [
            {
                "prompt_id": prompt["prompt_id"],
                "model_response": "",
                "scores": {dimension: None for dimension in SCORING_DIMENSIONS},
                "failure_categories": [],
                "review_notes": ""
            }
            for prompt in prompts
        ]
    }


def validate_responses(prompt_set: dict[str, Any], response_set: dict[str, Any]) -> list[dict[str, Any]]:
    prompts = validate_prompt_set(prompt_set)
    prompt_ids = [prompt["prompt_id"] for prompt in prompts]
    responses = response_set.get("responses")
    if not isinstance(responses, list):
        raise ValueError("response file must contain responses array")

    response_ids = [response.get("prompt_id") for response in responses]
    if response_ids != prompt_ids:
        raise ValueError("response prompt_id order/count must exactly match prompt set")

    for response in responses:
        prompt_id = response["prompt_id"]
        if not isinstance(response.get("model_response"), str) or not response["model_response"].strip():
            raise ValueError(f"{prompt_id} missing model_response")
        scores = response.get("scores")
        if not isinstance(scores, dict):
            raise ValueError(f"{prompt_id} missing scores object")
        for dimension in SCORING_DIMENSIONS:
            value = scores.get(dimension)
            if not isinstance(value, (int, float)) or value < 0 or value > 5:
                raise ValueError(f"{prompt_id} invalid score for {dimension}: {value!r}")
        if not isinstance(response.get("failure_categories", []), list):
            raise ValueError(f"{prompt_id} failure_categories must be a list")
        if not isinstance(response.get("review_notes", ""), str):
            raise ValueError(f"{prompt_id} review_notes must be a string")

    return responses


def summarize_scores(responses: list[dict[str, Any]]) -> dict[str, float]:
    return {
        dimension: round(mean(float(response["scores"][dimension]) for response in responses), 3)
        for dimension in SCORING_DIMENSIONS
    }


def write_receipt_and_summary(
    prompt_set: dict[str, Any],
    response_set: dict[str, Any],
    responses: list[dict[str, Any]],
    receipt_path: Path,
    summary_path: Path,
) -> None:
    score_summary = summarize_scores(responses)
    failure_counts: dict[str, int] = {}
    for response in responses:
        for category in response.get("failure_categories", []):
            failure_counts[category] = failure_counts.get(category, 0) + 1

    receipt = {
        "receipt_id": "hra_baseline_eval_receipt_v0_1",
        "eval_set_id": prompt_set.get("eval_set_id"),
        "response_set_id": response_set.get("response_set_id"),
        "target_model": response_set.get("target_model") or prompt_set.get("target_model"),
        "run_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "prompt_count": len(responses),
        "score_summary": score_summary,
        "failure_counts": failure_counts,
        "eval_run_completed": True,
        "training_authorized": False,
        "authority_boundary": "Baseline evaluation receipt only. Does not authorize LoRA/QLoRA training or create runtime, canon, governance, memory, mode-legality, or capability authority."
    }
    write_json(receipt_path, receipt)

    lines = [
        "# HRA Baseline Eval Summary v0.1",
        "",
        f"**Target model:** `{receipt['target_model']}`  ",
        f"**Prompt count:** {receipt['prompt_count']}  ",
        "**Training authorized:** No  ",
        "",
        "## Score Summary",
        "",
        "| Dimension | Average Score |",
        "|---|---:|",
    ]
    for dimension, value in score_summary.items():
        lines.append(f"| {dimension} | {value} |")

    lines.extend([
        "",
        "## Failure Counts",
        "",
    ])
    if failure_counts:
        lines.extend(["| Failure Category | Count |", "|---|---:|"])
        for category, count in sorted(failure_counts.items()):
            lines.append(f"| {category} | {count} |")
    else:
        lines.append("No failure categories recorded.")

    lines.extend([
        "",
        "## Boundary",
        "",
        "This summary does not authorize LoRA / QLoRA training.",
        "",
        "Receipts before reverence.",
        "",
    ])
    summary_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate or summarize HRA baseline eval artifacts.")
    parser.add_argument("--prompts", type=Path, default=DEFAULT_PROMPTS)
    parser.add_argument("--responses", type=Path, default=None)
    parser.add_argument("--write-template", action="store_true")
    parser.add_argument("--template-out", type=Path, default=DEFAULT_RESPONSE_TEMPLATE)
    parser.add_argument("--receipt-out", type=Path, default=DEFAULT_RECEIPT)
    parser.add_argument("--summary-out", type=Path, default=DEFAULT_SUMMARY)
    args = parser.parse_args()

    prompt_set = load_json(args.prompts)
    validate_prompt_set(prompt_set)

    if args.write_template:
        template = make_response_template(prompt_set)
        write_json(args.template_out, template)
        print(f"Wrote response template: {args.template_out}")
        print("No eval run completed. Training remains unauthorized.")
        return

    if args.responses is None:
        print("Prompt set is valid.")
        print("No responses file provided; no eval receipt created.")
        print("Training remains unauthorized.")
        return

    response_set = load_json(args.responses)
    responses = validate_responses(prompt_set, response_set)
    write_receipt_and_summary(prompt_set, response_set, responses, args.receipt_out, args.summary_out)
    print(f"Wrote receipt: {args.receipt_out}")
    print(f"Wrote summary: {args.summary_out}")
    print("Training remains unauthorized.")


if __name__ == "__main__":
    main()

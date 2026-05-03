#!/usr/bin/env python3
"""Lumina Studio CLI v0.1.

A small operator-facing bridge into the governed Lumina runtime.
It does not create new governance law. It packages a request, calls the
existing RuntimeRunner, and prints a human-readable receipt.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

BOOTSTRAP_ROOT = Path(__file__).resolve().parents[1]
RUNTIME_ROOT = BOOTSTRAP_ROOT / "runtime"
if str(RUNTIME_ROOT) not in sys.path:
    sys.path.insert(0, str(RUNTIME_ROOT))

try:
    from runtime_runner_r1_merged import RuntimeRunner, VALID_ACTION_TYPES
except Exception as exc:  # pragma: no cover - startup guard
    raise RuntimeError(
        "Lumina Studio could not import the governed runtime runner. "
        f"Expected runtime at {RUNTIME_ROOT}."
    ) from exc

SAFE_RUNTIME_CONFIG: Dict[str, bool] = {
    "toki_pona_required_for_resume": False,
    "binary_required_for_transition_validation": False,
    "light_language_required_for_capability_loading": False,
    "harmonic_frequency_required_for_mode_legality": False,
}

DEFAULT_FEATURE_FLAGS = [
    "ETHEREON_OBSERVATION",
    "ETHEREON_PSI42",
    "ETHEREON_RESONANCE",
    "ETHEREON_CONTINUITY_RESTORE",
    "ETHEREON_LUMINA_HOST",
]

DEFAULT_ARTIFACTS = [
    "runtime/runtime_spine_r1.py",
    "runtime/runtime_runner_r1_merged.py",
    "runtime/capability_registry_r1.json",
    "runtime/input_integrity_layer_r1.py",
    "runtime/governance_integrity_r1.py",
    "runtime/canon_lineage_store_r1.py",
    "studio/lumina_cli.py",
    "studio/lumina_studio_server.py",
]


def _coerce_prompt(parts: List[str], fallback: str) -> str:
    prompt = " ".join(part for part in parts if part).strip()
    return prompt or fallback


def _request_slug(text: str) -> str:
    safe = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in text.strip())
    safe = "_".join(token for token in safe.split("_") if token)
    return (safe[:80] or "lumina_studio_cycle").lower()


def build_orientation_payload(
    *,
    focus: str,
    depth: str,
    intent: str,
    annotation: Optional[str],
) -> Dict[str, Any]:
    """Attach orientation as supplemental stance, not governance law."""
    return {
        "focus": focus,
        "depth": depth,
        "intent": intent,
        "annotation": annotation,
        "authority": "supplemental only; does not govern mode legality, mutation, promotion, or canon lineage",
        "schema_version": "lumina-studio-orientation-v0.1",
    }


def compact_receipt(result: Dict[str, Any]) -> Dict[str, Any]:
    governance = result.get("governance", {}) or {}
    exposed = result.get("exposed_capabilities", []) or []
    return {
        "run_id": result.get("run_id"),
        "created_at": result.get("created_at"),
        "requested_mode": result.get("requested_mode"),
        "target_mode": result.get("target_mode"),
        "action_type": result.get("action_type"),
        "halted": result.get("halted"),
        "halt_reason": result.get("halt_reason"),
        "session_id": result.get("session_id"),
        "context_bundle_id": result.get("context_bundle_id"),
        "checkpoint_path": result.get("checkpoint_path"),
        "log_path": result.get("log_path"),
        "governance_log_path": result.get("governance_log_path"),
        "governance_chain_valid": (result.get("governance_chain_status") or {}).get("valid"),
        "canon_head": (result.get("canon_lineage") or {}).get("current_head"),
        "exposed_capability_ids": [cap.get("capability_id") for cap in exposed],
        "governance_keys": sorted(governance.keys()),
        "input_confidence": (governance.get("input_integrity") or {}).get("confidence_label"),
        "input_behavior": (governance.get("input_integrity") or {}).get("recommended_behavior"),
        "probe_run_id": (result.get("probe_artifacts") or {}).get("run_id"),
        "lumina_project_id": (result.get("lumina_return_host_artifacts") or {}).get("project_id"),
    }


def run_lumina_cycle(args: argparse.Namespace) -> Dict[str, Any]:
    prompt = _coerce_prompt(args.prompt, "Lumina Studio runtime cycle")
    requested_action = args.action or _request_slug(prompt)
    orientation = build_orientation_payload(
        focus=args.focus,
        depth=args.depth,
        intent=args.intent,
        annotation=args.annotation,
    )
    context_overrides = {
        "memory_context": {
            "lumina_studio_request": prompt,
            "lumina_studio_operator_note": args.note or "Studio cycle launched from CLI.",
        },
        "supplemental_ethereonic_context": {
            "lumina_studio_orientation": orientation,
        },
    }
    overlay = None
    if args.ethereonic_overlay:
        overlay = {
            "active": True,
            "anchor_language": ["english", "toki_pona", "binary", "light_language"],
            "continuity_phrase": "lumina studio cycle",
            "harmonic_signature": [432, 528, 963],
            "spiral_reference": "RSE-v1",
        }

    runner = RuntimeRunner()
    result = runner.run_cycle(
        current_mode=args.current_mode,
        target_mode=args.target_mode,
        requested_action=requested_action,
        action_type=args.action_type,
        artifacts=args.artifacts or DEFAULT_ARTIFACTS,
        continuation_notes=[
            f"Lumina Studio orientation: {args.focus}/{args.depth}/{args.intent}",
            "Studio is a control surface, not a governance authority.",
        ],
        enabled_feature_flags=args.feature_flags,
        runtime_config=SAFE_RUNTIME_CONFIG,
        raw_user_input=prompt,
        ethereonic_overlay=overlay,
        context_bundle_overrides=context_overrides,
        project_id=args.project_id,
    )
    return result.to_dict()


def print_human_receipt(receipt: Dict[str, Any]) -> None:
    print("Lumina Studio cycle complete")
    print(f"  run:        {receipt.get('run_id')}")
    print(f"  mode:       {receipt.get('requested_mode')} -> {receipt.get('target_mode')}")
    print(f"  action:     {receipt.get('action_type')}")
    print(f"  halted:     {receipt.get('halted')}")
    if receipt.get("halt_reason"):
        print(f"  reason:     {receipt.get('halt_reason')}")
    print(f"  checkpoint: {receipt.get('checkpoint_path')}")
    print(f"  log:        {receipt.get('log_path')}")
    print(f"  chain ok:   {receipt.get('governance_chain_valid')}")
    if receipt.get("input_confidence"):
        print(f"  input:      {receipt.get('input_confidence')} / {receipt.get('input_behavior')}")
    caps = receipt.get("exposed_capability_ids") or []
    print(f"  exposed:    {', '.join(caps) if caps else 'none'}")


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run one governed Lumina Studio cycle.")
    parser.add_argument("prompt", nargs="*", help="Operator request to pass through the runtime loop.")
    parser.add_argument("--current-mode", default="Continuity")
    parser.add_argument("--target-mode", default="Observation")
    parser.add_argument("--action-type", default="audit", choices=sorted(VALID_ACTION_TYPES))
    parser.add_argument("--action", default=None, help="Stable requested_action label. Defaults to a prompt-derived slug.")
    parser.add_argument("--project-id", default="lumina-os")
    parser.add_argument("--focus", default="continuity", choices=["architecture", "continuity", "expression", "integration", "governance_review"])
    parser.add_argument("--depth", default="structural", choices=["surface", "structural", "foundational"])
    parser.add_argument("--intent", default="verify", choices=["read", "build", "verify", "compose"])
    parser.add_argument("--annotation", default=None)
    parser.add_argument("--note", default=None)
    parser.add_argument("--feature-flag", action="append", dest="feature_flags", default=list(DEFAULT_FEATURE_FLAGS))
    parser.add_argument("--artifact", action="append", dest="artifacts", default=[])
    parser.add_argument("--ethereonic-overlay", action="store_true", help="Attach optional expressive overlay while preserving boundary law.")
    parser.add_argument("--json", action="store_true", help="Print full JSON result instead of compact receipt.")
    parser.add_argument("--receipt-json", action="store_true", help="Print compact receipt as JSON.")
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    result = run_lumina_cycle(args)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        receipt = compact_receipt(result)
        if args.receipt_json:
            print(json.dumps(receipt, indent=2))
        else:
            print_human_receipt(receipt)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

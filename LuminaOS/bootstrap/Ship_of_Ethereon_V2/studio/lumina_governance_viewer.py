#!/usr/bin/env python3
"""Lumina Studio Governance Viewer v0.3.

Read-only governance decision cards derived from emitted runtime result logs.
This module does not validate, override, or write governance. It only translates
runtime receipts into a clearer operator-facing shape.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from lumina_state_browser import DEFAULT_RUNTIME_BASE, _read_json, compact_run_summary, iter_result_logs

DECISION_KEYS = [
    "input_integrity",
    "ethereonic_layer_independence",
    "ethereonic_attachment",
    "transition",
    "mutation",
    "symbolic_dependency",
    "promotion",
    "capability_exposure",
]


def _first_present(*values: Any) -> Any:
    for value in values:
        if value is not None:
            return value
    return None


def _decision_status(payload: Dict[str, Any]) -> str:
    if payload.get("allowed") is True:
        return "allowed"
    if payload.get("allowed") is False:
        return "denied"
    if payload.get("should_halt") is True:
        return "halt_recommended"
    return "reported"


def _decision_reason(key: str, payload: Dict[str, Any]) -> Optional[str]:
    if key == "input_integrity":
        return _first_present(
            payload.get("confidence_reason"),
            payload.get("recommended_behavior"),
            payload.get("chosen_interpretation"),
        )
    return _first_present(payload.get("reason"), payload.get("confidence_reason"))


def decision_card(key: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(payload, dict):
        payload = {}
    card: Dict[str, Any] = {
        "key": key,
        "status": _decision_status(payload),
        "allowed": payload.get("allowed"),
        "reason": _decision_reason(key, payload),
    }
    if key == "input_integrity":
        card.update(
            {
                "confidence_label": payload.get("confidence_label"),
                "recommended_behavior": payload.get("recommended_behavior"),
                "chosen_interpretation": payload.get("chosen_interpretation"),
                "should_halt": payload.get("should_halt"),
            }
        )
    if key == "capability_exposure":
        card["capability_ids"] = payload.get("capability_ids", [])
        card["enabled_feature_flags"] = payload.get("enabled_feature_flags", [])
    if key in {"transition", "mutation", "promotion", "symbolic_dependency"}:
        card["audit_event"] = payload.get("audit_event")
    return card


def governance_view_for_result(payload: Dict[str, Any], *, source_path: Optional[Path] = None) -> Dict[str, Any]:
    governance = payload.get("governance", {}) or {}
    if not isinstance(governance, dict):
        governance = {}
    cards: List[Dict[str, Any]] = []
    for key in DECISION_KEYS:
        if key in governance:
            cards.append(decision_card(key, governance.get(key, {}) or {}))

    missing_expected = [key for key in DECISION_KEYS if key not in governance]
    denied = [card for card in cards if card.get("allowed") is False or card.get("status") == "halt_recommended"]
    return {
        "schema_version": "lumina-studio-governance-view-v0.3",
        "read_only": True,
        "summary": compact_run_summary(payload, path=source_path),
        "decision_cards": cards,
        "decision_count": len(cards),
        "denied_or_halt_count": len(denied),
        "missing_expected_decisions": missing_expected,
        "runtime_halted": payload.get("halted"),
        "halt_reason": payload.get("halt_reason"),
        "source_path": str(source_path) if source_path else None,
    }


def latest_governance_views(*, base_dir: Path = DEFAULT_RUNTIME_BASE, limit: int = 12) -> Dict[str, Any]:
    views: List[Dict[str, Any]] = []
    for path in iter_result_logs(base_dir):
        payload = _read_json(path)
        if payload is None:
            continue
        views.append(governance_view_for_result(payload, source_path=path))
        if len(views) >= limit:
            break
    return {
        "schema_version": "lumina-studio-governance-view-list-v0.3",
        "read_only": True,
        "runtime_base_dir": str(base_dir),
        "view_count": len(views),
        "latest_views": views,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Read governance decisions from emitted Lumina Studio runtime receipts.")
    parser.add_argument("--limit", type=int, default=12)
    parser.add_argument("--base-dir", default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    base_dir = Path(args.base_dir).expanduser().resolve() if args.base_dir else DEFAULT_RUNTIME_BASE
    print(json.dumps(latest_governance_views(base_dir=base_dir, limit=args.limit), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

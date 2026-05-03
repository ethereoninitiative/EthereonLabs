#!/usr/bin/env python3
"""Sea trial for Lumina Studio Governance View v0.3."""
from __future__ import annotations

import json
import sys
from argparse import Namespace
from pathlib import Path
from typing import Any, Dict, List

BOOTSTRAP_ROOT = Path(__file__).resolve().parent
STUDIO_ROOT = BOOTSTRAP_ROOT / "studio"
if str(STUDIO_ROOT) not in sys.path:
    sys.path.insert(0, str(STUDIO_ROOT))

from lumina_cli import DEFAULT_FEATURE_FLAGS, compact_receipt, run_lumina_cycle  # noqa: E402
from lumina_governance_viewer import latest_governance_views  # noqa: E402
from lumina_presets import presets_payload  # noqa: E402


def make_args(**overrides: Any) -> Namespace:
    base: Dict[str, Any] = {
        "prompt": ["Run Lumina Studio governance view verification cycle."],
        "current_mode": "Continuity",
        "target_mode": "Observation",
        "action_type": "audit",
        "action": "sea_trial_lumina_studio_governance_view_v0_3",
        "project_id": "lumina-studio-governance-view",
        "focus": "governance_review",
        "depth": "structural",
        "intent": "verify",
        "annotation": "Sea trial for Studio governance view v0.3",
        "note": "Studio governance viewer verifier.",
        "feature_flags": list(DEFAULT_FEATURE_FLAGS),
        "artifacts": [],
        "ethereonic_overlay": False,
        "json": False,
        "receipt_json": True,
    }
    base.update(overrides)
    return Namespace(**base)


def evaluate(views: Dict[str, Any], receipt: Dict[str, Any], presets: Dict[str, Any]) -> Dict[str, bool]:
    latest_views: List[Dict[str, Any]] = views.get("latest_views", []) or []
    matching = [view for view in latest_views if (view.get("summary") or {}).get("run_id") == receipt.get("run_id")]
    matched = matching[0] if matching else {}
    cards = matched.get("decision_cards", []) or []
    preset_ids = {item.get("id") for item in presets.get("presets", []) or []}
    return {
        "view_schema_matches": views.get("schema_version") == "lumina-studio-governance-view-list-v0.3",
        "view_is_read_only": views.get("read_only") is True,
        "latest_view_found": bool(matching),
        "decision_cards_present": len(cards) >= 1,
        "summary_contains_run_id": (matched.get("summary") or {}).get("run_id") == receipt.get("run_id"),
        "preset_schema_matches": presets.get("schema_version") == "lumina-studio-presets-v0.3",
        "preset_count_sufficient": len(preset_ids) >= 3,
        "expected_presets_present": {"observe_continuity", "architecture_review", "sandbox_design"}.issubset(preset_ids),
    }


def main() -> Dict[str, Any]:
    result = run_lumina_cycle(make_args())
    receipt = compact_receipt(result)
    views = latest_governance_views(limit=12)
    presets = presets_payload()
    checks = evaluate(views, receipt, presets)

    summary = {
        "suite": "Lumina Studio Governance View v0.3 sea trial",
        "passed": all(checks.values()),
        "checks": checks,
        "receipt": receipt,
        "view_summary": {
            "schema_version": views.get("schema_version"),
            "view_count": views.get("view_count"),
        },
        "preset_ids": [item.get("id") for item in presets.get("presets", [])],
    }

    report_dir = BOOTSTRAP_ROOT / ".studio_sea_trials"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / "lumina_studio_governance_view_v0_3_report.json"
    with report_path.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    summary["report_path"] = str(report_path)
    return summary


if __name__ == "__main__":
    print(json.dumps(main(), indent=2))

#!/usr/bin/env python3
"""Sea trial for Lumina Studio API v0.3.1.

Checks the data providers behind the local server endpoints without needing to
start an HTTP server.
"""
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
from lumina_state_browser import state_snapshot  # noqa: E402


def make_args(**overrides: Any) -> Namespace:
    base: Dict[str, Any] = {
        "prompt": ["Run Lumina Studio API v0.3.1 verification cycle."],
        "current_mode": "Continuity",
        "target_mode": "Observation",
        "action_type": "audit",
        "action": "sea_trial_lumina_studio_api_v0_3_1",
        "project_id": "lumina-studio-api",
        "focus": "integration",
        "depth": "structural",
        "intent": "verify",
        "annotation": "Sea trial for Studio API v0.3.1",
        "note": "Studio API verifier.",
        "feature_flags": list(DEFAULT_FEATURE_FLAGS),
        "artifacts": [],
        "ethereonic_overlay": False,
        "json": False,
        "receipt_json": True,
    }
    base.update(overrides)
    return Namespace(**base)


def evaluate(receipt: Dict[str, Any], state: Dict[str, Any], governance: Dict[str, Any], presets: Dict[str, Any]) -> Dict[str, bool]:
    latest_runs: List[Dict[str, Any]] = state.get("latest_runs", []) or []
    latest_run_ids = {run.get("run_id") for run in latest_runs}
    latest_views: List[Dict[str, Any]] = governance.get("latest_views", []) or []
    latest_view_ids = {(view.get("summary") or {}).get("run_id") for view in latest_views}
    preset_ids = {item.get("id") for item in presets.get("presets", []) or []}
    return {
        "receipt_not_halted": receipt.get("halted") is False,
        "state_schema_present": state.get("schema_version") == "lumina-studio-state-browser-v0.2",
        "state_contains_new_run": receipt.get("run_id") in latest_run_ids,
        "governance_schema_present": governance.get("schema_version") == "lumina-studio-governance-view-list-v0.3",
        "governance_contains_new_run": receipt.get("run_id") in latest_view_ids,
        "presets_schema_present": presets.get("schema_version") == "lumina-studio-presets-v0.3",
        "presets_expected_ids_present": {"observe_continuity", "architecture_review", "sandbox_design", "receipt_review"}.issubset(preset_ids),
    }


def main() -> Dict[str, Any]:
    result = run_lumina_cycle(make_args())
    receipt = compact_receipt(result)
    state = state_snapshot(limit=12)
    governance = latest_governance_views(limit=12)
    presets = presets_payload()
    checks = evaluate(receipt, state, governance, presets)

    summary = {
        "suite": "Lumina Studio API v0.3.1 sea trial",
        "passed": all(checks.values()),
        "checks": checks,
        "receipt": receipt,
        "endpoint_payloads": {
            "/api/state": {"schema_version": state.get("schema_version"), "receipt_count_returned": state.get("receipt_count_returned")},
            "/api/governance": {"schema_version": governance.get("schema_version"), "view_count": governance.get("view_count")},
            "/api/presets": {"schema_version": presets.get("schema_version"), "preset_count": len(presets.get("presets", []))},
        },
    }

    report_dir = BOOTSTRAP_ROOT / ".studio_sea_trials"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / "lumina_studio_api_v0_3_1_report.json"
    with report_path.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    summary["report_path"] = str(report_path)
    return summary


if __name__ == "__main__":
    print(json.dumps(main(), indent=2))

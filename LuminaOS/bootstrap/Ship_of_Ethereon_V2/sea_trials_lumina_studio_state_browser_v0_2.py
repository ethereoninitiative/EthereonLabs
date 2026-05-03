#!/usr/bin/env python3
"""Sea trial for Lumina Studio State Browser v0.2.

Validates that Studio can read recent runtime receipts and governance summaries
without becoming a governance authority or writing state through the browser.
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
from lumina_state_browser import state_snapshot  # noqa: E402


def make_args(**overrides: Any) -> Namespace:
    base: Dict[str, Any] = {
        "prompt": ["Run Lumina Studio state browser verification cycle."],
        "current_mode": "Continuity",
        "target_mode": "Observation",
        "action_type": "audit",
        "action": "sea_trial_lumina_studio_state_browser_v0_2",
        "project_id": "lumina-studio-state-browser",
        "focus": "continuity",
        "depth": "structural",
        "intent": "verify",
        "annotation": "Sea trial for Studio state browser v0.2",
        "note": "Studio state browser verifier: read-only receipt inspection.",
        "feature_flags": list(DEFAULT_FEATURE_FLAGS),
        "artifacts": [],
        "ethereonic_overlay": False,
        "json": False,
        "receipt_json": True,
    }
    base.update(overrides)
    return Namespace(**base)


def evaluate_snapshot(snapshot: Dict[str, Any], receipt: Dict[str, Any]) -> Dict[str, bool]:
    latest_runs: List[Dict[str, Any]] = snapshot.get("latest_runs", []) or []
    latest_run_ids = {run.get("run_id") for run in latest_runs}
    governance = snapshot.get("governance", {}) or {}
    return {
        "snapshot_schema_matches": snapshot.get("schema_version") == "lumina-studio-state-browser-v0.2",
        "snapshot_is_read_only": snapshot.get("read_only") is True,
        "runtime_base_reported": bool(snapshot.get("runtime_base_dir")),
        "receipt_count_positive": (snapshot.get("receipt_count_returned") or 0) >= 1,
        "latest_receipt_found": receipt.get("run_id") in latest_run_ids,
        "governance_summary_present": isinstance(governance, dict) and "event_count" in governance,
        "governance_events_recorded": (governance.get("event_count") or 0) >= 1,
        "canon_fields_present": "canon_record_count" in snapshot and "canon_head" in snapshot,
    }


def main() -> Dict[str, Any]:
    result = run_lumina_cycle(make_args())
    receipt = compact_receipt(result)
    snapshot = state_snapshot(limit=12)
    checks = evaluate_snapshot(snapshot, receipt)

    summary = {
        "suite": "Lumina Studio State Browser v0.2 sea trial",
        "passed": all(checks.values()),
        "checks": checks,
        "receipt": receipt,
        "snapshot_summary": {
            "schema_version": snapshot.get("schema_version"),
            "read_only": snapshot.get("read_only"),
            "receipt_count_returned": snapshot.get("receipt_count_returned"),
            "governance": snapshot.get("governance"),
            "canon_record_count": snapshot.get("canon_record_count"),
            "canon_head": snapshot.get("canon_head"),
        },
        "authority_boundary": "State browser reads emitted runtime files only; it does not write checkpoints, governance logs, or canon lineage.",
    }

    report_dir = BOOTSTRAP_ROOT / ".studio_sea_trials"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / "lumina_studio_state_browser_v0_2_report.json"
    with report_path.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    summary["report_path"] = str(report_path)
    return summary


if __name__ == "__main__":
    print(json.dumps(main(), indent=2))

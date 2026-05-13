#!/usr/bin/env python3
"""Sea trial for Lumina Studio v0.1.

Validates the first usable operator surface without granting it governance authority.
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
        "prompt": ["Run Lumina Studio v0.1 verification cycle."],
        "current_mode": "Continuity",
        "target_mode": "Observation",
        "action_type": "audit",
        "action": "sea_trial_lumina_studio_v0_1",
        "project_id": "lumina-studio-sea-trial",
        "focus": "continuity",
        "depth": "structural",
        "intent": "verify",
        "annotation": "Sea trial for Studio v0.1",
        "note": "Studio verifier: control surface only.",
        "feature_flags": list(DEFAULT_FEATURE_FLAGS),
        "artifacts": [],
        "ethereonic_overlay": False,
        "json": False,
        "receipt_json": True,
    }
    base.update(overrides)
    return Namespace(**base)


def evaluate_default_audit(receipt: Dict[str, Any]) -> Dict[str, bool]:
    exposed = set(receipt.get("exposed_capability_ids") or [])
    witness = receipt.get("harmonic_witness") or {}
    return {
        "default_not_halted": receipt.get("halted") is False,
        "target_mode_observation": receipt.get("target_mode") == "Observation",
        "checkpoint_present": bool(receipt.get("checkpoint_path")),
        "log_present": bool(receipt.get("log_path")),
        "governance_log_present": bool(receipt.get("governance_log_path")),
        "governance_chain_status_returned": receipt.get("governance_chain_valid") is not None,
        "structural_capabilities_exposed": "session_state_manager" in exposed and "mode_guard" in exposed,
        "harmonic_witness_present": isinstance(witness, dict) and bool(witness),
        "continuity_shape_present": bool(receipt.get("continuity_shape")),
        "listening_note_present": bool(witness.get("input_listening_note")),
        "recomposition_summary_present": bool(witness.get("recomposition_summary")),
    }


def evaluate_denied_transition(receipt: Dict[str, Any]) -> Dict[str, bool]:
    witness = receipt.get("harmonic_witness") or {}
    return {
        "denied_transition_halted": receipt.get("halted") is True,
        "halt_reason_mentions_illegal_transition": "illegal transition" in str(receipt.get("halt_reason") or ""),
        "no_capabilities_exposed_after_halt": len(receipt.get("exposed_capability_ids") or []) == 0,
        "halted_witness_shape_present": witness.get("continuity_shape") == "halted_before_return",
    }


def evaluate_state_view(snapshot: Dict[str, Any]) -> Dict[str, bool]:
    harmonic = snapshot.get("harmonic_summary") or {}
    latest_runs = snapshot.get("latest_runs") or []
    latest = latest_runs[0] if latest_runs else {}
    return {
        "harmonic_summary_present": isinstance(harmonic, dict) and bool(harmonic),
        "latest_continuity_shape_present": bool(harmonic.get("latest_continuity_shape")),
        "drift_note_present": bool(harmonic.get("drift_note")),
        "recurrence_note_present": bool(harmonic.get("recurrence_note")),
        "latest_run_contains_harmonic_witness": isinstance(latest.get("harmonic_witness"), dict) and bool(latest.get("harmonic_witness")),
    }


def main() -> Dict[str, Any]:
    results: List[Dict[str, Any]] = []

    default_result = run_lumina_cycle(make_args())
    default_receipt = compact_receipt(default_result)
    default_checks = evaluate_default_audit(default_receipt)
    results.append(
        {
            "trial_name": "studio_default_audit_cycle",
            "passed": all(default_checks.values()),
            "checks": default_checks,
            "receipt": default_receipt,
        }
    )

    denied_result = run_lumina_cycle(
        make_args(
            prompt=["Attempt illegal Studio transition."],
            current_mode="Canon",
            target_mode="Sandbox",
            action_type="transition",
            action="sea_trial_lumina_studio_denied_transition",
            focus="governance_review",
            annotation="Intentional illegal transition test",
        )
    )
    denied_receipt = compact_receipt(denied_result)
    denied_checks = evaluate_denied_transition(denied_receipt)
    results.append(
        {
            "trial_name": "studio_denied_transition_receipt",
            "passed": all(denied_checks.values()),
            "checks": denied_checks,
            "receipt": denied_receipt,
        }
    )

    state_view = state_snapshot(limit=6)
    state_checks = evaluate_state_view(state_view)
    results.append(
        {
            "trial_name": "studio_state_harmonic_witness_view",
            "passed": all(state_checks.values()),
            "checks": state_checks,
            "state_view": state_view,
        }
    )

    summary = {
        "suite": "Lumina Studio v0.1 sea trial",
        "passed": all(item["passed"] for item in results),
        "trial_count": len(results),
        "results": results,
        "authority_boundary": "Studio launches runtime cycles and displays receipts only; runtime remains governance authority.",
    }

    report_dir = BOOTSTRAP_ROOT / ".studio_sea_trials"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / "lumina_studio_v0_1_report.json"
    with report_path.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    summary["report_path"] = str(report_path)
    return summary


if __name__ == "__main__":
    print(json.dumps(main(), indent=2))

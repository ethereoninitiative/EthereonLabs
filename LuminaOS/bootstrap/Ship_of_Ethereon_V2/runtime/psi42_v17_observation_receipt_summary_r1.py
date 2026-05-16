#!/usr/bin/env python3
from __future__ import annotations

"""
psi42_v17_observation_receipt_summary_r1.py

Compact CI-friendly verifier for Lumina Observation JSON receipts.

Expected input is the full JSON emitted by:

python LuminaOS/bootstrap/Ship_of_Ethereon_V2/studio/lumina_cli.py \
  --target-mode Observation \
  --action-type audit \
  --feature-flag ETHEREON_PSI42 \
  --feature-flag ETHEREON_PSI42_V17 \
  --json \
  "Run Psi-42 v1.7 Observation verification."

This tool emits a small pass/fail JSON summary and exits non-zero when the
receipt does not meet the requested v1.7 Observation checks.
"""

from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import Any, Dict, Optional
import json
import sys

TOPOLOGY_METRICS = ("RTC", "RDS", "RRS", "HRC")


def _load_json(path: Optional[str]) -> Dict[str, Any]:
    raw = sys.stdin.read() if path in (None, "-") else Path(path).read_text(encoding="utf-8")
    payload = json.loads(raw)
    if not isinstance(payload, dict):
        raise ValueError("Receipt JSON root must be an object")
    return payload


def _nested(payload: Dict[str, Any], *keys: str) -> Any:
    current: Any = payload
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def _as_float(value: Any) -> Optional[float]:
    try:
        if value is None:
            return None
        return float(value)
    except Exception:
        return None


def _probe_run_id(probe: Dict[str, Any]) -> Optional[str]:
    return (
        probe.get("run_id")
        or probe.get("signal_run_id")
        or _nested(probe, "signal_result", "run_id")
    )


def _probe_pulse_id(probe: Dict[str, Any]) -> Optional[str]:
    return (
        probe.get("pulse_id")
        or probe.get("signal_pulse_id")
        or _nested(probe, "signal_result", "pulse_id")
    )


def summarize(receipt: Dict[str, Any], *, min_hybrid: float = 0.35) -> Dict[str, Any]:
    probe = receipt.get("probe_artifacts") or {}
    if not isinstance(probe, dict):
        probe = {}
    metrics = probe.get("metrics") or {}
    if not isinstance(metrics, dict):
        metrics = {}

    instrument_version = probe.get("instrument_version")
    probe_mode = probe.get("probe_mode")
    hybrid = _as_float(metrics.get("hybrid_continuity_coherence"))
    topology_receipt = probe.get("topology_receipt")
    governance_valid = bool(_nested(receipt, "governance_chain_status", "valid"))
    halted = bool(receipt.get("halted"))
    probe_run_id = _probe_run_id(probe)
    probe_pulse_id = _probe_pulse_id(probe)

    checks = {
        "target_mode_observation": receipt.get("target_mode") == "Observation",
        "action_type_audit": receipt.get("action_type") == "audit",
        "not_halted": halted is False,
        "governance_chain_valid": governance_valid,
        "psi42_v17_selected": instrument_version == "v1.7",
        "probe_mode_hybrid": probe_mode in (None, "hybrid") if instrument_version != "v1.7" else probe_mode == "hybrid",
        "probe_identity_present": bool(probe_run_id),
        "topology_receipt_present": isinstance(topology_receipt, dict),
        "hybrid_continuity_present": hybrid is not None,
        "hybrid_continuity_threshold": hybrid is not None and hybrid >= min_hybrid,
        "topology_metrics_present": all(metric in metrics for metric in TOPOLOGY_METRICS),
    }

    summary = {
        "summary_type": "psi42_v17_observation_receipt_summary_r1",
        "run_id": receipt.get("run_id"),
        "target_mode": receipt.get("target_mode"),
        "action_type": receipt.get("action_type"),
        "halted": halted,
        "governance_chain_valid": governance_valid,
        "instrument_version": instrument_version,
        "probe_mode": probe_mode,
        "probe_run_id": probe_run_id,
        "probe_pulse_id": probe_pulse_id,
        "hybrid_continuity_coherence": hybrid,
        "topology_metrics": {metric: metrics.get(metric) for metric in TOPOLOGY_METRICS},
        "checks": checks,
        "overall_pass": all(checks.values()),
    }
    return summary


def parse_args(argv: Optional[list[str]] = None) -> Namespace:
    parser = ArgumentParser(description="Summarize and verify a Psi-42 v1.7 Observation receipt.")
    parser.add_argument("receipt_json", nargs="?", default="-", help="Path to receipt JSON, or '-' / omitted for stdin.")
    parser.add_argument("--min-hybrid", type=float, default=0.35, help="Minimum hybrid_continuity_coherence threshold.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    return parser.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> int:
    args = parse_args(argv)
    receipt = _load_json(args.receipt_json)
    summary = summarize(receipt, min_hybrid=args.min_hybrid)
    print(json.dumps(summary, indent=2 if args.pretty else None, sort_keys=True))
    return 0 if summary["overall_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

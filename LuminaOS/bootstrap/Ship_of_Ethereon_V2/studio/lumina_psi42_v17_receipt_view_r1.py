#!/usr/bin/env python3
from __future__ import annotations

"""Studio helper for reading Psi-42 v1.7 Observation receipts.

This is a read-only operator surface. It does not run Lumina, authorize action,
alter governance, mutate canon, or change capability exposure.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional

BOOTSTRAP_ROOT = Path(__file__).resolve().parents[1]
RUNTIME_ROOT = BOOTSTRAP_ROOT / "runtime"
if str(RUNTIME_ROOT) not in sys.path:
    sys.path.insert(0, str(RUNTIME_ROOT))

from psi42_v17_observation_receipt_summary_r1 import summarize


def _load_json(path: str) -> Dict[str, Any]:
    payload = json.loads(sys.stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Receipt JSON root must be an object")
    return payload


def print_human(summary: Dict[str, Any]) -> None:
    print("Psi-42 v1.7 Observation receipt")
    print(f"  run:        {summary.get('run_id')}")
    print(f"  mode:       {summary.get('target_mode')}")
    print(f"  action:     {summary.get('action_type')}")
    print(f"  halted:     {summary.get('halted')}")
    print(f"  chain ok:   {summary.get('governance_chain_valid')}")
    print(f"  instrument: {summary.get('instrument_version')} / {summary.get('probe_mode')}")
    print(f"  probe run:  {summary.get('probe_run_id')}")
    print(f"  hybrid:     {summary.get('hybrid_continuity_coherence')}")
    topo = summary.get("topology_metrics") or {}
    if topo:
        print("  topology:   " + ", ".join(f"{k}={v}" for k, v in topo.items()))
    print(f"  passed:     {summary.get('overall_pass')}")
    failed = [key for key, ok in (summary.get("checks") or {}).items() if not ok]
    if failed:
        print("  failed:     " + ", ".join(failed))


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Read and summarize a Psi-42 v1.7 Observation receipt.")
    parser.add_argument("receipt_json", help="Path to receipt JSON, or '-' for stdin.")
    parser.add_argument("--pretty", action="store_true", help="Print JSON summary instead of human text.")
    parser.add_argument("--min-hybrid", type=float, default=0.35)
    return parser.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> int:
    args = parse_args(argv)
    receipt = _load_json(args.receipt_json)
    summary = summarize(receipt, min_hybrid=args.min_hybrid)
    if args.pretty:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print_human(summary)
    return 0 if summary.get("overall_pass") else 1


if __name__ == "__main__":
    raise SystemExit(main())

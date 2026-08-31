#!/usr/bin/env python3
"""First-class bounded continuation surface for Lumina OS."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional

BOOTSTRAP_ROOT = Path(__file__).resolve().parents[1]
RUNTIME_ROOT = BOOTSTRAP_ROOT / "runtime"
if str(RUNTIME_ROOT) not in sys.path:
    sys.path.insert(0, str(RUNTIME_ROOT))

try:
    from lumina_continue_controller_r1 import LuminaContinueController
except Exception as exc:  # pragma: no cover - startup guard
    raise RuntimeError("Lumina continue could not import its bounded continuation controller.") from exc


def print_human_receipt(receipt: dict) -> None:
    print("Lumina continuation cycle complete")
    print(f"  project:     {receipt.get('project_id')}")
    print(f"  selected:    {receipt.get('selected_next_action')}")
    print(
        f"  confidence:  {receipt.get('preflight_confidence_label')} "
        f"({receipt.get('preflight_confidence_score')})"
    )
    print(f"  reasoning:   {receipt.get('preflight_reasoning_brief')}")
    print(f"  mode:        Continuity -> {receipt.get('target_mode')}")
    print(f"  action type: {receipt.get('action_type')}")
    print(f"  halted:      {receipt.get('halted')}")
    if receipt.get("halt_reason"):
        print(f"  reason:      {receipt.get('halt_reason')}")
    print(f"  checkpoint:  {receipt.get('checkpoint_path')}")
    print(f"  chain ok:    {receipt.get('governance_chain_valid')}")
    print(f"  boundary:    {receipt.get('authority_boundary')}")


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Select Lumina's next bounded focus from existing project-return/self-guidance state, "
            "then run one governed Observation/audit cycle."
        )
    )
    parser.add_argument("--project-id", default="lumina-os")
    parser.add_argument("--action", default="continue_from_latest_checkpoint")
    parser.add_argument("--json", action="store_true", help="Print compact JSON receipt.")
    parser.add_argument("--full-json", action="store_true", help="Print the full preflight + runtime result.")
    parser.add_argument("--base-dir", default=None, help=argparse.SUPPRESS)
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    controller = LuminaContinueController(base_dir=args.base_dir)
    outcome = controller.continue_cycle(project_id=args.project_id, requested_action=args.action)
    receipt = outcome.compact_receipt()
    if args.full_json:
        print(json.dumps({
            "preflight_advisory": outcome.preflight_advisory,
            "runtime_result": outcome.runtime_result,
            "receipt": receipt,
        }, indent=2))
    elif args.json:
        print(json.dumps(receipt, indent=2))
    else:
        print_human_receipt(receipt)
    return 1 if receipt.get("halted") else 0


if __name__ == "__main__":
    raise SystemExit(main())

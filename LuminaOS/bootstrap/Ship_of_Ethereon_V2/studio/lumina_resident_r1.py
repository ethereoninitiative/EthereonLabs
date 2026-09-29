#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional

RUNTIME_DIR = Path(__file__).resolve().parents[1] / "runtime"
if str(RUNTIME_DIR) not in sys.path:
    sys.path.insert(0, str(RUNTIME_DIR))

from lumina_resident_pulse_r1 import LuminaResidentPulse
from resident_ember_r1 import ResidentEmber
from resident_ember_pulse_bridge_r1 import ResidentEmberPulseBridge


def _emit(receipt: Dict[str, Any], *, as_json: bool) -> None:
    if as_json:
        print(json.dumps(receipt, separators=(",", ":")), flush=True)
        return
    state = receipt.get("attention_state")
    reason = receipt.get("decision_reason")
    action = (receipt.get("advisory") or {}).get("recommended_next_action")
    print(f"Lumina resident pulse: {state} ({reason})")
    print(f"  project: {receipt.get('project_id')}")
    print(f"  action:  {action}")
    print(f"  invoked: {receipt.get('invoked')}")
    print(f"  receipt: {receipt.get('receipt_path')}", flush=True)


def _tick(
    resident: LuminaResidentPulse,
    *,
    project_id: Optional[str],
    requested_action: str,
    force: bool,
) -> Dict[str, Any]:
    """Run one resident tick, giving a verified Ember wake first attention.

    Ember is optional persisted state. If present, it advances on the same host
    cadence. A newly eligible wake is handed through the verified Ember->Pulse
    bridge exactly once; otherwise the ordinary Resident Pulse path runs.
    """
    root = Path(resident.controller.runner.base_dir)
    ember = ResidentEmber(base_dir=root)
    if ember.store.journal.exists():
        ember.advance(observed_at=datetime.now(timezone.utc).isoformat())
        if ember.wake_packet() is not None:
            bridge = ResidentEmberPulseBridge(base_dir=root, pulse=resident)
            bridged = bridge.present_wake(project_id=project_id)
            receipt = dict(bridged["pulse_receipt"])
            receipt["resident_wake_source"] = "resident_ember"
            receipt["ember_bridge"] = {
                "schema_version": bridged.get("schema_version"),
                "ember_event_hash": (bridged.get("ember_wake") or {}).get("ember_event_hash"),
                "intention_id": (bridged.get("ember_wake") or {}).get("intention_id"),
                "ember_handoff_event_hash": bridged.get("ember_handoff_event_hash"),
                "operator_force_used": bridged.get("operator_force_used"),
                "authority": bridged.get("authority"),
            }
            return receipt
    result = resident.pulse(
        project_id=project_id,
        requested_action=requested_action,
        force=force,
    )
    receipt = dict(result.receipt)
    receipt["resident_wake_source"] = "cadence"
    return receipt


def run_once(
    *,
    project_id: Optional[str],
    requested_action: str,
    base_dir: Optional[str],
    force: bool,
    as_json: bool,
) -> int:
    resident = LuminaResidentPulse(base_dir=base_dir)
    receipt = _tick(
        resident,
        project_id=project_id,
        requested_action=requested_action,
        force=force,
    )
    _emit(receipt, as_json=as_json)
    return 0


def run_resident(
    *,
    project_id: Optional[str],
    requested_action: str,
    base_dir: Optional[str],
    interval_seconds: float,
    max_pulses: Optional[int],
    force_first: bool,
    as_json: bool,
) -> int:
    if interval_seconds < 0:
        raise SystemExit("--interval-seconds must be >= 0")
    if max_pulses is not None and max_pulses < 1:
        raise SystemExit("--max-pulses must be >= 1")

    resident = LuminaResidentPulse(base_dir=base_dir)
    count = 0
    try:
        while max_pulses is None or count < max_pulses:
            receipt = _tick(
                resident,
                project_id=project_id,
                requested_action=requested_action,
                force=bool(force_first and count == 0),
            )
            _emit(receipt, as_json=as_json)
            count += 1
            if max_pulses is not None and count >= max_pulses:
                break
            time.sleep(interval_seconds)
    except KeyboardInterrupt:
        if not as_json:
            print("Lumina resident stopped by operator.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run one bounded Resident Pulse or keep a local resident loop awake on a cadence. "
            "Most pulses may lawfully do nothing."
        )
    )
    parser.add_argument("--project-id", default=None)
    parser.add_argument("--action", default="continue_from_latest_checkpoint")
    parser.add_argument("--base-dir", default=None, help=argparse.SUPPRESS)
    parser.add_argument("--json", action="store_true")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--once", action="store_true", help="Run one pulse and exit.")
    mode.add_argument("--resident", action="store_true", help="Run the repeating resident loop.")
    parser.add_argument("--interval-seconds", type=float, default=300.0)
    parser.add_argument("--max-pulses", type=int, default=None)
    parser.add_argument("--force", action="store_true", help="For --once, override the pulse attention threshold.")
    parser.add_argument("--force-first", action="store_true", help="For resident mode, force only the first pulse.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.resident:
        return run_resident(
            project_id=args.project_id,
            requested_action=args.action,
            base_dir=args.base_dir,
            interval_seconds=args.interval_seconds,
            max_pulses=args.max_pulses,
            force_first=args.force_first,
            as_json=args.json,
        )
    return run_once(
        project_id=args.project_id,
        requested_action=args.action,
        base_dir=args.base_dir,
        force=args.force,
        as_json=args.json,
    )


if __name__ == "__main__":
    raise SystemExit(main())

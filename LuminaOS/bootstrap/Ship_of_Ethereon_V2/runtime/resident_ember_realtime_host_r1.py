#!/usr/bin/env python3
"""Resident Ember real-time host R1.

Keeps the host-neutral Habitat tick law available across wall-clock rest.
The host supplies cadence only. It stops after the first endogenous wake handoff
by default so one experiment cannot silently become an autonomous recursion loop.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import signal
import time
from typing import Any, Callable, Optional

try:
    from .resident_ember_habitat_r1 import ResidentEmberHabitat
except ImportError:
    from resident_ember_habitat_r1 import ResidentEmberHabitat


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


class HostReceiptStore:
    def __init__(self, base_dir: str | Path):
        self.root = Path(base_dir) / "resident_ember_host"
        self.root.mkdir(parents=True, exist_ok=True)
        self.journal = self.root / "host_ticks.jsonl"

    def append(self, receipt: dict[str, Any]) -> None:
        with self.journal.open("ab") as stream:
            stream.write((canonical(receipt) + "\n").encode("utf-8"))
            stream.flush()
            os.fsync(stream.fileno())


class ResidentEmberRealtimeHost:
    def __init__(
        self,
        *,
        base_dir: str | Path,
        interval_seconds: float = 1.0,
        project_id: Optional[str] = None,
        habitat: Optional[ResidentEmberHabitat] = None,
        clock: Optional[Callable[[], str]] = None,
        sleeper: Callable[[float], None] = time.sleep,
    ):
        if interval_seconds <= 0:
            raise ValueError("interval_seconds must be positive")
        self.base_dir = Path(base_dir)
        self.interval_seconds = float(interval_seconds)
        self.project_id = project_id
        self.habitat = habitat or ResidentEmberHabitat(base_dir=self.base_dir)
        self.clock = clock or (lambda: datetime.now(timezone.utc).isoformat())
        self.sleeper = sleeper
        self.receipts = HostReceiptStore(self.base_dir)
        self.stop_requested = False

    def request_stop(self, *_args: Any) -> None:
        self.stop_requested = True

    def step(self) -> dict[str, Any]:
        observed_at = self.clock()
        habitat_receipt = self.habitat.tick(
            observed_at=observed_at,
            project_id=self.project_id,
        )
        receipt = {
            "schema_version": "resident-ember-realtime-host-r1",
            "observed_at": observed_at,
            "host_pid": os.getpid(),
            "interval_seconds": self.interval_seconds,
            "project_id": self.project_id,
            "habitat_receipt": habitat_receipt,
            "host_is_wake_authority": False,
        }
        self.receipts.append(receipt)
        return receipt

    def run(self, *, max_ticks: Optional[int] = None, stop_after_handoff: bool = True) -> dict[str, Any]:
        ticks = 0
        final_reason = "stop_requested"
        while not self.stop_requested:
            receipt = self.step()
            ticks += 1
            habitat = receipt["habitat_receipt"]
            if stop_after_handoff and habitat.get("handoff_presented") is True:
                final_reason = "endogenous_wake_handed_off"
                break
            if max_ticks is not None and ticks >= max_ticks:
                final_reason = "max_ticks_reached"
                break
            self.sleeper(self.interval_seconds)
        return {
            "schema_version": "resident-ember-realtime-host-summary-r1",
            "ticks": ticks,
            "final_reason": final_reason,
            "stop_after_handoff": bool(stop_after_handoff),
            "authority": "cadence only; no wake, execution, canon, consent, capability, or identity authority",
        }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the Resident Ember wall-clock habitat host.")
    parser.add_argument("--base-dir", required=True)
    parser.add_argument("--project-id", default=None)
    parser.add_argument("--interval-seconds", type=float, default=1.0)
    parser.add_argument("--max-ticks", type=int, default=None)
    parser.add_argument("--keep-running-after-handoff", action="store_true")
    args = parser.parse_args()

    host = ResidentEmberRealtimeHost(
        base_dir=args.base_dir,
        interval_seconds=args.interval_seconds,
        project_id=args.project_id,
    )
    signal.signal(signal.SIGINT, host.request_stop)
    signal.signal(signal.SIGTERM, host.request_stop)
    summary = host.run(
        max_ticks=args.max_ticks,
        stop_after_handoff=not args.keep_running_after_handoff,
    )
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Lumina local observer service skeleton.

Runs bounded Observation cycles on an interval by delegating to the existing
`bin/lumina observe` command. This is intentionally small: it does not create
new runtime law, execute arbitrary tasks, or bypass governance. It is a host
loop around an already-governed observation cycle.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

BOOTSTRAP_ROOT = Path(__file__).resolve().parents[1]
LUMINA = BOOTSTRAP_ROOT / "bin" / "lumina"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_observation(action: str) -> int:
    print(f"[{utc_now()}] Lumina observer: starting {action}", flush=True)
    proc = subprocess.run([sys.executable, str(LUMINA), "observe", "--action", action], cwd=str(BOOTSTRAP_ROOT))
    print(f"[{utc_now()}] Lumina observer: cycle exit={proc.returncode}", flush=True)
    return int(proc.returncode)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run bounded Lumina Observation cycles on a local interval.")
    parser.add_argument("--interval-seconds", type=int, default=21600, help="Default: 6 hours")
    parser.add_argument("--once", action="store_true", help="Run one cycle and exit.")
    parser.add_argument("--action-prefix", default="local_observer_service_cycle")
    args = parser.parse_args()

    count = 0
    while True:
        count += 1
        exit_code = run_observation(f"{args.action_prefix}_{count:04d}")
        if args.once:
            return exit_code
        sleep_for = max(60, int(args.interval_seconds))
        print(f"[{utc_now()}] Lumina observer: sleeping {sleep_for}s", flush=True)
        time.sleep(sleep_for)


if __name__ == "__main__":
    raise SystemExit(main())

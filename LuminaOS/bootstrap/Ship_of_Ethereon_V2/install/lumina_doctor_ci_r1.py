#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import argparse
import json
import sys

BOOTSTRAP_ROOT = Path(__file__).resolve().parents[1]
for path in [
    BOOTSTRAP_ROOT / "install",
    BOOTSTRAP_ROOT / "runtime",
    BOOTSTRAP_ROOT / "studio",
    BOOTSTRAP_ROOT,
]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from lumina_doctor import print_human, run_doctor


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the Lumina doctor with complete bootstrap import paths.")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--ensure-state", action="store_true")
    parser.add_argument("--migrate-state", action="store_true")
    args = parser.parse_args()
    payload = run_doctor(ensure_state=args.ensure_state, migrate_state=args.migrate_state)
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print_human(payload)
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())

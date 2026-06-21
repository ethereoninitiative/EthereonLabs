#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
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

from lumina_doctor import run_doctor


if __name__ == "__main__":
    payload = run_doctor(ensure_state=True)
    print(json.dumps(payload, indent=2))
    raise SystemExit(0 if payload.get("ok") else 1)

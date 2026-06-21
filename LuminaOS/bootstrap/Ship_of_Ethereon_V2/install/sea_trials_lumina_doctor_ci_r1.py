#!/usr/bin/env python3
from __future__ import annotations

import json

from lumina_doctor_ci_r1 import run_doctor


if __name__ == "__main__":
    payload = run_doctor(ensure_state=True)
    print(json.dumps(payload, indent=2))
    raise SystemExit(0 if payload.get("ok") else 1)

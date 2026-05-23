#!/usr/bin/env python3
"""Lumina Studio CLI shim that routes through the Psi-42 v1.8 runner adapter.

The original `lumina_cli.py` remains the operator surface. This shim swaps its
RuntimeRunner binding to the v1.8 adapter before delegating to its existing main.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import List, Optional

BOOTSTRAP_ROOT = Path(__file__).resolve().parents[1]
RUNTIME_ROOT = BOOTSTRAP_ROOT / "runtime"
STUDIO_ROOT = BOOTSTRAP_ROOT / "studio"
for path in [str(RUNTIME_ROOT), str(STUDIO_ROOT)]:
    if path not in sys.path:
        sys.path.insert(0, path)

try:
    import lumina_cli as base_cli
    from runtime_runner_psi42_v18_adapter_r1 import RuntimeRunner, VALID_ACTION_TYPES
except Exception as exc:  # pragma: no cover - startup guard
    raise RuntimeError("Lumina v1.8 CLI shim could not import its base CLI or runner adapter.") from exc

base_cli.RuntimeRunner = RuntimeRunner
base_cli.VALID_ACTION_TYPES = VALID_ACTION_TYPES

# Keep the operator-facing defaults aligned with the v1.8 adapter/capability registry.
for flag in ["ETHEREON_PSI42", "ETHEREON_PSI42_V17", "ETHEREON_PSI42_V18", "ETHEREON_RESONANCE"]:
    if flag not in base_cli.DEFAULT_FEATURE_FLAGS:
        base_cli.DEFAULT_FEATURE_FLAGS.append(flag)


def main(argv: Optional[List[str]] = None) -> int:
    return int(base_cli.main(argv))


if __name__ == "__main__":
    raise SystemExit(main())

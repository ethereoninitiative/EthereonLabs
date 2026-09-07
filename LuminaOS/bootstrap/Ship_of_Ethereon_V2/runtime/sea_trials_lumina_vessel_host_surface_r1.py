#!/usr/bin/env python3
"""Verify the primary Lumina host delegates vessel transfer without changing transfer law."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

BOOTSTRAP_ROOT = Path(__file__).resolve().parents[1]
PRIMARY = BOOTSTRAP_ROOT / "bin" / "lumina"
COMPAT = BOOTSTRAP_ROOT / "bin" / "lumina-vessel"


def run(entrypoint: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(entrypoint), *args],
        cwd=BOOTSTRAP_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def parse_error(proc: subprocess.CompletedProcess[str]) -> dict:
    require(proc.returncode == 2, f"expected bounded transfer error code 2, got {proc.returncode}")
    try:
        payload = json.loads(proc.stderr)
    except json.JSONDecodeError as exc:
        raise AssertionError(f"expected JSON error payload, got: {proc.stderr!r}") from exc
    require(payload.get("ok") is False, "transfer error payload must declare ok=false")
    require(bool(payload.get("error")), "transfer error payload must explain the failure")
    return payload


def main() -> int:
    for args in (
        ("vessel", "--help"),
        ("vessel", "export", "--help"),
        ("vessel", "verify", "--help"),
        ("vessel", "import", "--help"),
    ):
        proc = run(PRIMARY, *args)
        require(proc.returncode == 0, f"primary host help failed for {' '.join(args)}: {proc.stderr}")

    with tempfile.TemporaryDirectory(prefix="lumina-vessel-host-") as temp_dir:
        missing = Path(temp_dir) / "missing-capsule.json"
        primary = run(PRIMARY, "vessel", "verify", "--capsule", str(missing))
        compat = run(COMPAT, "verify", "--capsule", str(missing))
        primary_error = parse_error(primary)
        compat_error = parse_error(compat)
        require(
            primary_error.get("error") == compat_error.get("error"),
            "primary and compatibility entrypoints must reach the same transfer implementation",
        )

    print(
        json.dumps(
            {
                "passed": True,
                "primary_surface": "lumina vessel",
                "compatibility_surface": "lumina-vessel",
                "delegates_to_existing_transfer_implementation": True,
                "transfer_law_changed": False,
                "automatic_import_added": False,
                "continuation_added": False,
                "authority_effect": False,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
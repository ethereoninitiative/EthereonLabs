#!/usr/bin/env python3
"""Hearth R1: explicit, read-only aggregate disk observation experiment.

Standalone; not runtime-wired, not a capability, not an attention trigger.
"""
from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable


def classify(total: int, free: int) -> str:
    if type(total) is not int or type(free) is not int:
        return "unavailable"
    if total <= 0 or free < 0 or free > total:
        return "unavailable"
    return "pressure" if free * 10 <= total else "clear"


def observe(path: Path, probe: Callable = shutil.disk_usage) -> dict:
    result = {
        "schema": "hearth-disk-observation-r1",
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "status": "unavailable",
        "total_bytes": None,
        "free_bytes": None,
        "error": None,
        "execution_authority": False,
        "attention_requested": False,
    }
    try:
        usage = probe(path)
        total, free = usage.total, usage.free
        state = classify(total, free)
        if state == "unavailable":
            result["error"] = "invalid_measurement"
        else:
            result.update(status=state, total_bytes=total, free_bytes=free)
    except (OSError, ValueError, OverflowError):
        result["error"] = "probe_failed"
    return result


def self_test() -> None:
    from collections import namedtuple
    from tempfile import TemporaryDirectory

    usage = namedtuple("Usage", "total used free")
    assert classify(100, 10) == "pressure"
    assert classify(100, 11) == "clear"
    assert classify(100, 0) == "pressure"
    for total, free in [(0, 0), (100, -1), (100, 101), (True, 0)]:
        assert classify(total, free) == "unavailable"
    with TemporaryDirectory() as directory:
        path = Path(directory)
        result = observe(path, lambda _: usage(100, 90, 10))
        assert result["status"] == "pressure"
        assert result["execution_authority"] is False
        assert result["attention_requested"] is False
        assert "path" not in result
        invalid = observe(path, lambda _: usage(0, 0, 0))
        assert invalid["status"] == "unavailable"
        assert invalid["free_bytes"] is None
        def fail(_):
            raise OSError("private path must not leak")
        failure = observe(path, fail)
        assert failure["error"] == "probe_failed"
        assert failure["status"] == "unavailable"
        assert "private path" not in json.dumps(failure)
        actual = observe(path)
        assert actual["status"] in {"clear", "pressure"}
        assert actual["total_bytes"] > 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--path", type=Path, help="Explicit local volume path")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        if args.path is not None:
            parser.error("choose self-test or path")
        self_test()
        print("Hearth R1 observation self-test passed")
        return 0
    if args.path is None:
        parser.error("explicit --path is required")
    receipt = observe(args.path)
    print(json.dumps(receipt, indent=2))
    return 2 if receipt["status"] == "unavailable" else 0


if __name__ == "__main__":
    raise SystemExit(main())

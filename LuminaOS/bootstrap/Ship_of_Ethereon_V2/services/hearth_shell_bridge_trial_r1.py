#!/usr/bin/env python3
"""Linux-only standalone Hearth trial. No runtime wiring or privilege grant."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile


def disk_status():
    """Fixed Linux command; no shell, caller arguments or raw output."""
    if sys.platform != "linux":
        return {"status": "unavailable"}
    try:
        p = subprocess.run(["/usr/bin/df", "-Pk", "/"], shell=False,
                           env={"LC_ALL": "C", "PATH": "/usr/bin:/bin"},
                           stdin=subprocess.DEVNULL, capture_output=True,
                           text=True, timeout=5, check=True)
        rows = p.stdout.splitlines()
        if len(rows) != 2:
            raise ValueError("unexpected df output")
        fields = rows[1].split(maxsplit=5)
        total, used, available = map(int, fields[1:4])
        if total <= 0 or min(used, available) < 0 or max(used, available) > total:
            raise ValueError("invalid measurement")
        return {"status": "observed", "total_kib": total,
                "available_kib": available}
    except (OSError, subprocess.SubprocessError, ValueError, IndexError):
        return {"status": "unavailable"}


def digest(data):
    return hashlib.sha256(data).hexdigest()


class FixtureBroker:
    """Private temporary fixture only; caller cannot specify paths or commands.

    The approval digest is a test witness, not authenticated authorization.
    This in-process broker is not a security boundary against the same OS user.
    """
    def __init__(self, root):
        self.current = root / "current"
        self.previous = root / "previous"
        self.used = False
        self.current.write_bytes(b"lumina synthetic maintenance fixture\n")

    def plan(self):
        return {"operation": "rotate_fixture", "expected_sha256": digest(self.current.read_bytes())}

    def execute(self, proposal, approved_digest):
        def deny(reason):
            return {"status": "denied", "reason": reason, "host_authority": False}
        if type(proposal) is not dict or set(proposal) != {"operation", "expected_sha256"}:
            return deny("invalid_schema")
        if proposal["operation"] != "rotate_fixture":
            return deny("unknown_operation")
        if self.used:
            return deny("already_consumed")
        if self.current.is_symlink() or not self.current.is_file() or os.path.lexists(self.previous):
            return deny("unexpected_fixture_state")
        data = self.current.read_bytes()
        expected = digest(data)
        if proposal["expected_sha256"] != expected or approved_digest != expected:
            return deny("stale_or_unapproved")
        self.used = True
        self.current.rename(self.previous)
        try:
            verified = not self.current.exists() and self.previous.read_bytes() == data
            if not verified:
                raise RuntimeError("verification failed")
        finally:
            self.previous.rename(self.current)
        restored = self.current.read_bytes() == data and not self.previous.exists()
        if not restored:
            raise RuntimeError("rollback verification failed")
        return {"status": "verified_and_restored", "sha256": expected,
                "host_authority": False, "fixture_only": True}


def sea_trial():
    with tempfile.TemporaryDirectory(prefix="hearth-trial-") as tmp:
        broker = FixtureBroker(Path(tmp))
        plan = broker.plan()
        approval = plan["expected_sha256"]
        checks = {}
        checks["no_approval_denied"] = broker.execute(plan, None)["status"] == "denied"
        checks["extra_field_denied"] = broker.execute(dict(plan, path="/"), approval)["status"] == "denied"
        checks["unknown_operation_denied"] = broker.execute(dict(plan, operation="other"), approval)["status"] == "denied"
        checks["stale_digest_denied"] = broker.execute(dict(plan, expected_sha256="0" * 64), approval)["status"] == "denied"
        broker.previous.symlink_to(broker.current)
        checks["symlink_destination_denied"] = broker.execute(plan, approval)["status"] == "denied"
        broker.previous.unlink()
        result = broker.execute(plan, approval)
        checks["maintenance_and_rollback"] = result["status"] == "verified_and_restored"
        checks["replay_denied"] = broker.execute(plan, approval)["status"] == "denied"
        checks["original_bytes_preserved"] = digest(broker.current.read_bytes()) == approval
        observation = disk_status()
        checks["linux_disk_observation"] = observation["status"] == "observed"
    return {"schema": "hearth-shell-bridge-trial-r1", "checks": checks,
            "passed": all(checks.values()), "observation": observation,
            "maintenance": result, "approval_kind": "synthetic_test_witness",
            "resident_model_invoked": False, "host_mutation_authorized": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sea-trial", action="store_true")
    args = parser.parse_args()
    if not args.sea_trial:
        parser.error("only explicit --sea-trial is supported")
    receipt = sea_trial()
    print(json.dumps(receipt, indent=2))
    return 0 if receipt["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

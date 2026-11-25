#!/usr/bin/env python3
"""One scheduled local Observation cycle; no model call or host action authority."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

REPO = Path(__file__).resolve().parents[2]
HOST = REPO / "LuminaOS/bootstrap/Ship_of_Ethereon_V2/bin/lumina"


def validate_receipt(receipt, root):
    if not isinstance(receipt, dict):
        return "invalid_receipt"
    if receipt.get("halted") is not False:
        return "halted_or_unknown"
    if receipt.get("target_mode") != "Observation" or receipt.get("action_type") != "audit":
        return "unexpected_mode_or_action"
    if receipt.get("governance_chain_valid") is not True:
        return "unverified_governance"
    if not isinstance(receipt.get("run_id"), str) or not receipt["run_id"]:
        return "missing_run_id"
    for key in ("checkpoint_path", "log_path", "governance_log_path"):
        value = receipt.get(key)
        if not isinstance(value, str) or not value:
            return "missing_evidence"
        try:
            path = Path(value)
            if not path.is_absolute() or not path.resolve(strict=True).is_relative_to(root) or not path.is_file():
                return "evidence_outside_state_or_missing"
        except (OSError, RuntimeError, ValueError):
            return "evidence_outside_state_or_missing"
    return None


def cycle(root):
    root = root.resolve(strict=True)
    if not root.is_dir():
        return {"status": "failed", "reason": "state_root_not_directory"}
    env = dict(os.environ, LUMINA_STATE_ROOT=str(root))
    command = [sys.executable, str(HOST), "run", "Inspect Lumina runtime continuity.",
               "--action", "appliance_observation_r1", "--project-id", "lumina-os",
               "--target-mode", "Observation", "--action-type", "audit",
               "--focus", "continuity", "--depth", "structural", "--intent", "verify",
               "--base-dir", str(root / "runtime_runner_r1_actiontype_logging"),
               "--receipt-json"]
    try:
        proc = subprocess.run(command, cwd=REPO, env=env, stdin=subprocess.DEVNULL,
                              capture_output=True, text=True, timeout=60, check=False)
        if proc.returncode != 0:
            return {"status": "failed", "reason": "runtime_process_failed"}
        receipt = json.loads(proc.stdout)
        reason = validate_receipt(receipt, root)
        if reason:
            return {"status": "failed", "reason": reason}
        return {"status": "verified", "run_id": receipt["run_id"],
                "checkpoint_path": receipt["checkpoint_path"], "log_path": receipt["log_path"],
                "governance_log_path": receipt["governance_log_path"],
                "host_action_authority": False, "resident_model_invoked": False}
    except (OSError, UnicodeError, subprocess.SubprocessError, ValueError):
        return {"status": "failed", "reason": "runtime_or_receipt_unavailable"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state-root", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = cycle(args.state_root)
    except (OSError, RuntimeError, ValueError):
        result = {"status": "failed", "reason": "state_root_unavailable"}
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "verified" else 1


if __name__ == "__main__":
    raise SystemExit(main())

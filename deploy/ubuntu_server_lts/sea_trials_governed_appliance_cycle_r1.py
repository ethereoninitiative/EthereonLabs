#!/usr/bin/env python3
"""Fixture rejection controls plus two real CLI invocations in temporary state."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

from governed_appliance_cycle_r1 import validate_receipt

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
HOST = REPO / "LuminaOS/bootstrap/Ship_of_Ethereon_V2/bin/lumina"


def main():
    checks = {}
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory).resolve()
        evidence = root / "fixture.json"
        evidence.write_text("{}")
        good = dict(halted=False, target_mode="Observation", action_type="audit",
                    governance_chain_valid=True, run_id="fixture",
                    checkpoint_path=str(evidence), log_path=str(evidence),
                    governance_log_path=str(evidence))
        checks["fixture_accepted"] = validate_receipt(good, root) is None
        for key, value in [("halted", True), ("halted", None), ("target_mode", "DryDock"),
                           ("action_type", "mutation"), ("governance_chain_valid", False),
                           ("run_id", ""), ("checkpoint_path", str(root / "missing")),
                           ("log_path", str(HERE / "governed_appliance_cycle_r1.py"))]:
            label = key + "_" + str(len(checks))
            checks[label] = validate_receipt(dict(good, **{key: value}), root) is not None
        checks["non_object_denied"] = validate_receipt([], root) is not None
        outcomes = []
        for _ in range(2):
            proc = subprocess.run([sys.executable, str(HERE / "governed_appliance_cycle_r1.py"),
                                   "--state-root", str(root)],
                                  capture_output=True, text=True, timeout=85)
            outcome = json.loads(proc.stdout)
            outcomes.append(outcome)
            checks["real_cli_cycle_" + str(len(outcomes))] = proc.returncode == 0 and outcome.get("status") == "verified"
        checks["distinct_runs"] = bool(outcomes[0].get("run_id")) and outcomes[0].get("run_id") != outcomes[1].get("run_id")
        first = outcomes[0].get("log_path")
        checks["first_receipt_retained"] = bool(first) and Path(first).is_file()
        checks["same_governance_log"] = bool(outcomes[0].get("governance_log_path")) and outcomes[0].get("governance_log_path") == outcomes[1].get("governance_log_path")
        env = dict(os.environ, LUMINA_STATE_ROOT=str(root))
        state = subprocess.run([sys.executable, str(HOST), "state", "--limit", "5"],
                               capture_output=True, text=True, env=env, timeout=20)
        checks["state_browser_uses_root"] = state.returncode == 0 and all(str(o.get("run_id", "__missing__")) in state.stdout for o in outcomes)
        print(json.dumps({"schema": "governed-appliance-cycle-trial-r1", "checks": checks,
                          "outcomes": outcomes, "passed": all(checks.values()),
                          "systemd_executed": False, "reboot_executed": False}, indent=2))
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())

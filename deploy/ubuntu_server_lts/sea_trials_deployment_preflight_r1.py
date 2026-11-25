#!/usr/bin/env python3
"""Offline fixture trial: no real installer preparation or service activation."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent


def main():
    checks = {}
    script = HERE / "bootstrap_lumina_appliance_r1.sh"
    checks["installer_syntax"] = subprocess.run(["bash", "-n", str(script)]).returncode == 0
    for name, args in [("no_arguments", []), ("activation_argument", ["--start"])]:
        result = subprocess.run(["bash", str(script), *args], capture_output=True, text=True)
        checks[name + "_rejected"] = result.returncode == 2 and "preparation only" in result.stderr
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        deploy = root / "deploy/ubuntu_server_lts"
        deploy.mkdir(parents=True)
        for name in ("lumina-orchestrator.service", "lumina-orchestrator.timer", "chamber-advisory.service"):
            (deploy / name).touch()
        state, log, runtime = [root / name for name in ("state", "log", "runtime")]
        for directory in (state, log, runtime):
            directory.mkdir()
        registry = root / "registry.json"
        env = root / "appliance.env"
        host = {"host_id": "fixture", "host_label": "Fixture", "host_type": "local",
                "runtime_scope": "development", "approved_by_user_id": "fixture-operator",
                "operator_user_ids": ["fixture-operator"], "allowed_runtime_paths": [str(runtime)],
                "allowed_action_types": ["audit"], "state_root": str(state), "log_root": str(log),
                "service_user": "fixture-user", "created_at": "2026-11-24T00:00:00Z"}

        def doctor(payload, config="DATABASE_URL=postgres://fixture:synthetic@localhost/fixture\n",
                   mode=0o600, expected=True, registry_path=registry):
            registry_path.write_text(json.dumps(payload))
            env.write_text(config)
            env.chmod(mode)
            proc = subprocess.run([sys.executable, str(HERE / "deployment_doctor_r1.py"),
                                   "--repo-root", str(root), "--registry", str(registry_path),
                                   "--env-file", str(env), "--host-id", "fixture"],
                                  capture_output=True, text=True, timeout=5)
            report = json.loads(proc.stdout)
            return (proc.returncode == (0 if expected else 1)
                    and report["passed"] is expected
                    and "synthetic" not in proc.stdout
                    and "synthetic" not in proc.stderr)

        checks["valid_fixture"] = doctor({"hosts": [host]})
        checks["placeholder_rejected"] = doctor({"hosts": [host]}, "DATABASE_URL=postgres://SET_USER:SET_PASSWORD@localhost/SET_DBNAME\n", expected=False)
        checks["missing_db_config"] = doctor({"hosts": [host]}, "OTHER=1\n", expected=False)
        checks["public_env_rejected"] = doctor({"hosts": [host]}, mode=0o644, expected=False)
        checks["duplicate_host_rejected"] = doctor({"hosts": [host, host]}, expected=False)
        checks["malformed_registry_rejected"] = doctor([], expected=False)
        checks["malformed_fields_rejected"] = doctor({"hosts": [dict(host, allowed_runtime_paths=42)]}, expected=False)
        checks["revoked_host_rejected"] = doctor({"hosts": [dict(host, revoked_at="2026-11-24")]}, expected=False)
        checks["example_registry_rejected"] = doctor({"hosts": [host]}, expected=False, registry_path=deploy / "host_registry.example.json")
        checks["missing_state_rejected"] = doctor({"hosts": [dict(host, state_root=str(root / "missing"))]}, expected=False)
    print(json.dumps({"schema": "deployment-preflight-fixture-r1", "checks": checks,
                      "passed": all(checks.values()), "real_host_deployed": False}, indent=2))
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())

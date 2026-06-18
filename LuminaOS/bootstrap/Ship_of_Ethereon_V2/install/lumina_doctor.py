#!/usr/bin/env python3
"""Lumina local readiness checker.

The doctor verifies that the local Lumina bootstrap has the minimum files needed
to start like a system: host command, Studio CLI/server, runtime runner,
state browser, capability registry, package inventory, state schema helper,
and core docs.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

BOOTSTRAP_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[4]
INSTALL_ROOT = BOOTSTRAP_ROOT / "install"
if str(INSTALL_ROOT) not in sys.path:
    sys.path.insert(0, str(INSTALL_ROOT))

try:
    from lumina_state_schema import inspect_state_schema
except Exception:  # pragma: no cover - doctor reports this through import checks too
    inspect_state_schema = None

MIN_PYTHON: Tuple[int, int] = (3, 10)

REQUIRED_FILES = [
    "bin/lumina",
    "requirements.txt",
    "install/lumina_state_schema.py",
    "studio/lumina_cli.py",
    "studio/lumina_cli_psi42_v18.py",
    "studio/lumina_studio_server.py",
    "studio/lumina_state_browser.py",
    "runtime/runtime_runner_r1_merged.py",
    "runtime/runtime_runner_auto_snapshot_psi42_v18_r1.py",
    "runtime/runtime_runner_psi42_v18_adapter_r1.py",
    "runtime/runtime_spine_r1.py",
    "runtime/capability_registry_r1.json",
    "runtime/input_integrity_layer_r1.py",
    "runtime/governance_integrity_r1.py",
    "runtime/canon_lineage_store_r1.py",
    "docs/Lumina_OS_Host_Layer_001.md",
    "docs/Lumina_Local_Runbook_001.md",
    "docs/Lumina_Package_Install_R1.md",
]

OPTIONAL_FILES = [
    "services/lumina_observer_service.py",
    "services/lumina.service.example",
    "docs/lumina_studio_v0_1_spec.md",
    "docs/lumina_next_build_plan_001.md",
]

PYTHON_IMPORT_CHECKS = [
    "install/lumina_state_schema.py",
    "runtime/runtime_runner_r1_merged.py",
    "runtime/runtime_runner_auto_snapshot_psi42_v18_r1.py",
    "studio/lumina_cli.py",
    "studio/lumina_cli_psi42_v18.py",
    "studio/lumina_state_browser.py",
]

COMMAND_SMOKE_CHECKS = [
    ["bin/lumina", "--help"],
    ["bin/lumina", "doctor", "--json"],
    ["studio/lumina_cli_psi42_v18.py", "--help"],
]


def file_check(path_text: str, *, required: bool = True) -> Dict[str, Any]:
    path = BOOTSTRAP_ROOT / path_text
    return {
        "path": path_text,
        "exists": path.exists(),
        "required": required,
        "is_file": path.is_file(),
        "executable": os.access(path, os.X_OK) if path.exists() else False,
    }


def import_check(path_text: str) -> Dict[str, Any]:
    path = BOOTSTRAP_ROOT / path_text
    if not path.exists():
        return {"path": path_text, "ok": False, "reason": "missing file"}
    try:
        module_name = "lumina_doctor_probe_" + path.stem
        spec = importlib.util.spec_from_file_location(module_name, path)
        if spec is None or spec.loader is None:
            return {"path": path_text, "ok": False, "reason": "no import spec"}
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return {"path": path_text, "ok": True, "reason": "import executed"}
    except Exception as exc:
        return {"path": path_text, "ok": False, "reason": str(exc)}


def command_smoke_check(command: List[str]) -> Dict[str, Any]:
    resolved = [str(BOOTSTRAP_ROOT / command[0]), *command[1:]]
    if command[0].endswith(".py"):
        resolved = [sys.executable, str(BOOTSTRAP_ROOT / command[0]), *command[1:]]
    try:
        proc = subprocess.run(
            resolved,
            cwd=str(BOOTSTRAP_ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=12,
        )
        return {
            "command": " ".join(command),
            "ok": proc.returncode == 0,
            "returncode": proc.returncode,
            "stdout_tail": proc.stdout[-600:],
            "stderr_tail": proc.stderr[-600:],
        }
    except Exception as exc:
        return {"command": " ".join(command), "ok": False, "reason": str(exc)}


def python_version_check() -> Dict[str, Any]:
    current = sys.version_info[:2]
    return {
        "ok": current >= MIN_PYTHON,
        "current": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "minimum": f"{MIN_PYTHON[0]}.{MIN_PYTHON[1]}",
    }


def dependency_inventory_check() -> Dict[str, Any]:
    path = BOOTSTRAP_ROOT / "requirements.txt"
    if not path.exists():
        return {"ok": False, "reason": "requirements.txt missing"}
    lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines()]
    requirements = [line for line in lines if line and not line.startswith("#")]
    pinned = [line for line in requirements if "==" in line]
    unpinned = [line for line in requirements if "==" not in line]
    return {
        "ok": bool(requirements) and not unpinned,
        "path": "requirements.txt",
        "requirement_count": len(requirements),
        "pinned_count": len(pinned),
        "unpinned": unpinned,
    }


def capability_registry_check() -> Dict[str, Any]:
    path = BOOTSTRAP_ROOT / "runtime" / "capability_registry_r1.json"
    if not path.exists():
        return {"ok": False, "reason": "capability registry missing"}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        capabilities = payload.get("capabilities", [])
        ids = [item.get("capability_id") for item in capabilities if isinstance(item, dict)]
        required_ids = {"session_state_manager", "mode_guard", "context_bundle_builder", "input_integrity_assessor"}
        missing = sorted(required_ids - set(ids))
        return {
            "ok": not missing,
            "version": payload.get("version"),
            "capability_count": len(ids),
            "missing_required_ids": missing,
        }
    except Exception as exc:
        return {"ok": False, "reason": str(exc)}


def state_path_check(*, ensure_state: bool = False, migrate_state: bool = False) -> Dict[str, Any]:
    if inspect_state_schema is None:
        return {
            "ok": False,
            "compatible": False,
            "reason": "lumina_state_schema helper unavailable",
        }
    return inspect_state_schema(ensure=ensure_state, migrate=migrate_state).to_dict()


def run_doctor(*, ensure_state: bool = False, migrate_state: bool = False) -> Dict[str, Any]:
    required = [file_check(path, required=True) for path in REQUIRED_FILES]
    optional = [file_check(path, required=False) for path in OPTIONAL_FILES]
    imports = [import_check(path) for path in PYTHON_IMPORT_CHECKS]
    commands = [command_smoke_check(command) for command in COMMAND_SMOKE_CHECKS]
    registry = capability_registry_check()
    python_version = python_version_check()
    dependencies = dependency_inventory_check()
    state = state_path_check(ensure_state=ensure_state, migrate_state=migrate_state)
    missing_required = [item["path"] for item in required if not item["exists"] or not item["is_file"]]
    failed_imports = [item for item in imports if not item["ok"]]
    failed_commands = [item for item in commands if not item["ok"]]
    ok = (
        not missing_required
        and not failed_imports
        and not failed_commands
        and bool(registry.get("ok"))
        and bool(python_version.get("ok"))
        and bool(dependencies.get("ok"))
        and bool(state.get("writable_parent"))
        and bool(state.get("compatible"))
    )
    return {
        "schema_version": "lumina-doctor-v0.4",
        "ok": ok,
        "bootstrap_root": str(BOOTSTRAP_ROOT),
        "repo_root": str(REPO_ROOT),
        "python": sys.version.split()[0],
        "python_version": python_version,
        "required_files": required,
        "optional_files": optional,
        "dependency_inventory": dependencies,
        "import_checks": imports,
        "command_smoke_checks": commands,
        "capability_registry": registry,
        "state": state,
        "missing_required_files": missing_required,
        "failed_imports": failed_imports,
        "failed_commands": failed_commands,
    }


def print_human(payload: Dict[str, Any]) -> None:
    print("Lumina doctor")
    print(f"  ok:              {payload['ok']}")
    print(f"  bootstrap root:  {payload['bootstrap_root']}")
    print(f"  python:          {payload['python']} (min {payload['python_version']['minimum']})")
    print(f"  dependencies ok: {payload['dependency_inventory'].get('ok')}")
    print(f"  registry ok:     {payload['capability_registry'].get('ok')}")
    print(f"  capability count:{payload['capability_registry'].get('capability_count')}")
    print(f"  state root:      {payload['state'].get('state_root')}")
    print(f"  state schema:    {payload['state'].get('schema_version') or 'not created yet'}")
    if payload["missing_required_files"]:
        print("  missing required:")
        for item in payload["missing_required_files"]:
            print(f"    - {item}")
    if payload["dependency_inventory"].get("unpinned"):
        print("  unpinned dependencies:")
        for item in payload["dependency_inventory"]["unpinned"]:
            print(f"    - {item}")
    if payload["failed_imports"]:
        print("  failed imports:")
        for item in payload["failed_imports"]:
            print(f"    - {item['path']}: {item['reason']}")
    if payload["failed_commands"]:
        print("  failed command smoke checks:")
        for item in payload["failed_commands"]:
            print(f"    - {item['command']}: {item.get('reason') or item.get('returncode')}")
    if not payload["missing_required_files"] and not payload["failed_imports"] and not payload["failed_commands"]:
        print("  start command:   bin/lumina run")
        print("  observe command: bin/lumina observe")
        print("  state command:   bin/lumina state")
        print("  studio command:  bin/lumina studio")
    if not payload["state"].get("schema_exists"):
        print("  state setup:     run doctor with --ensure-state to create the local schema marker")
    if payload["state"].get("migration_required"):
        print("  state migrate:   run doctor with --migrate-state")


def main() -> int:
    parser = argparse.ArgumentParser(description="Check local Lumina host readiness.")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--ensure-state", action="store_true", help="Create the local .lumina_state schema marker if missing.")
    parser.add_argument("--migrate-state", action="store_true", help="Migrate a known older local state schema marker to the current version.")
    args = parser.parse_args()
    payload = run_doctor(ensure_state=args.ensure_state, migrate_state=args.migrate_state)
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print_human(payload)
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

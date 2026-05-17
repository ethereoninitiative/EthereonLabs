#!/usr/bin/env python3
"""Lumina local readiness checker.

The doctor verifies that the local Lumina bootstrap has the minimum files needed
to start like a system: host command, Studio CLI/server, runtime runner,
state browser, capability registry, and core docs.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

BOOTSTRAP_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[4]

REQUIRED_FILES = [
    "bin/lumina",
    "studio/lumina_cli.py",
    "studio/lumina_studio_server.py",
    "studio/lumina_state_browser.py",
    "runtime/runtime_runner_r1_merged.py",
    "runtime/runtime_runner_auto_snapshot_r1.py",
    "runtime/runtime_spine_r1.py",
    "runtime/capability_registry_r1.json",
    "runtime/input_integrity_layer_r1.py",
    "runtime/governance_integrity_r1.py",
    "runtime/canon_lineage_store_r1.py",
    "docs/Lumina_OS_Host_Layer_001.md",
    "docs/Lumina_Local_Runbook_001.md",
]

OPTIONAL_FILES = [
    "services/lumina_observer_service.py",
    "services/lumina.service.example",
    "docs/lumina_studio_v0_1_spec.md",
    "docs/lumina_next_build_plan_001.md",
]

PYTHON_IMPORT_CHECKS = [
    "runtime/runtime_runner_r1_merged.py",
    "runtime/runtime_runner_auto_snapshot_r1.py",
    "studio/lumina_cli.py",
    "studio/lumina_state_browser.py",
]

COMMAND_SMOKE_CHECKS = [
    ["bin/lumina", "--help"],
    ["bin/lumina", "doctor", "--json"],
    ["studio/lumina_cli.py", "--help"],
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


def state_path_check() -> Dict[str, Any]:
    state_root = REPO_ROOT / ".lumina_state" / "ship_of_ethereon_v2"
    return {
        "state_root": str(state_root),
        "exists": state_root.exists(),
        "note": "state root is created by runtime cycles; missing is acceptable before first run",
    }


def run_doctor() -> Dict[str, Any]:
    required = [file_check(path, required=True) for path in REQUIRED_FILES]
    optional = [file_check(path, required=False) for path in OPTIONAL_FILES]
    imports = [import_check(path) for path in PYTHON_IMPORT_CHECKS]
    commands = [command_smoke_check(command) for command in COMMAND_SMOKE_CHECKS]
    registry = capability_registry_check()
    missing_required = [item["path"] for item in required if not item["exists"] or not item["is_file"]]
    failed_imports = [item for item in imports if not item["ok"]]
    failed_commands = [item for item in commands if not item["ok"]]
    ok = not missing_required and not failed_imports and not failed_commands and bool(registry.get("ok"))
    return {
        "schema_version": "lumina-doctor-v0.2",
        "ok": ok,
        "bootstrap_root": str(BOOTSTRAP_ROOT),
        "repo_root": str(REPO_ROOT),
        "python": sys.version.split()[0],
        "required_files": required,
        "optional_files": optional,
        "import_checks": imports,
        "command_smoke_checks": commands,
        "capability_registry": registry,
        "state": state_path_check(),
        "missing_required_files": missing_required,
        "failed_imports": failed_imports,
        "failed_commands": failed_commands,
    }


def print_human(payload: Dict[str, Any]) -> None:
    print("Lumina doctor")
    print(f"  ok:              {payload['ok']}")
    print(f"  bootstrap root:  {payload['bootstrap_root']}")
    print(f"  python:          {payload['python']}")
    print(f"  registry ok:     {payload['capability_registry'].get('ok')}")
    print(f"  capability count:{payload['capability_registry'].get('capability_count')}")
    if payload["missing_required_files"]:
        print("  missing required:")
        for item in payload["missing_required_files"]:
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


def main() -> int:
    parser = argparse.ArgumentParser(description="Check local Lumina host readiness.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    payload = run_doctor()
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print_human(payload)
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
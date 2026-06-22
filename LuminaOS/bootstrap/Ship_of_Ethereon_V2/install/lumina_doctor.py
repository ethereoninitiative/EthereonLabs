#!/usr/bin/env python3
"""Lumina local readiness checker.

Reports host and runtime readiness only. Runtime governance remains authoritative.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

BOOTSTRAP_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[4]
INSTALL_ROOT = BOOTSTRAP_ROOT / "install"
RUNTIME_ROOT = BOOTSTRAP_ROOT / "runtime"
STUDIO_ROOT = BOOTSTRAP_ROOT / "studio"
for import_root in [INSTALL_ROOT, RUNTIME_ROOT, STUDIO_ROOT, BOOTSTRAP_ROOT]:
    if str(import_root) not in sys.path:
        sys.path.insert(0, str(import_root))

try:
    from lumina_state_schema import inspect_state_schema
except Exception:
    inspect_state_schema = None

REQUIRED_FILES = [
    "bin/lumina",
    "install/lumina_state_schema.py",
    "install/lumina_project_registry.py",
    "install/lumina_session_registry.py",
    "studio/lumina_cli.py",
    "studio/lumina_cli_psi42_v18.py",
    "studio/lumina_studio_server.py",
    "studio/lumina_state_browser.py",
    "studio/lumina_presets_r1.json",
    "runtime/runtime_runner_r1_merged.py",
    "runtime/runtime_runner_auto_snapshot_psi42_v18_r1.py",
    "runtime/runtime_spine_r1.py",
    "runtime/capability_registry_r1.json",
    "runtime/input_integrity_layer_r1.py",
    "runtime/governance_integrity_r1.py",
    "runtime/canon_lineage_store_r1.py",
    "runtime/psi42_transceiver_v1_8.py",
    "runtime/resonant_manifold_r1.py",
    "runtime/resonant_manifold_registry_r1.json",
    "runtime/sea_trials_resonant_manifold_r1.py",
    "docs/Ethereon_Orbital_Planetary_Framing_R1.md",
    "docs/Resonant_Manifold_R1.md",
]

IMPORT_CHECKS = [
    "install/lumina_state_schema.py",
    "install/lumina_project_registry.py",
    "install/lumina_session_registry.py",
    "runtime/runtime_runner_r1_merged.py",
    "runtime/resonant_manifold_r1.py",
    "studio/lumina_state_browser.py",
]


def file_check(path_text: str) -> Dict[str, Any]:
    path = BOOTSTRAP_ROOT / path_text
    return {
        "path": path_text,
        "exists": path.exists(),
        "is_file": path.is_file(),
        "executable": os.access(path, os.X_OK) if path.exists() else False,
    }


def import_check(path_text: str) -> Dict[str, Any]:
    path = BOOTSTRAP_ROOT / path_text
    if not path.exists():
        return {"path": path_text, "ok": False, "reason": "missing file"}
    try:
        name = "lumina_doctor_probe_" + path.stem
        spec = importlib.util.spec_from_file_location(name, path)
        if spec is None or spec.loader is None:
            return {"path": path_text, "ok": False, "reason": "no import spec"}
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
        return {"path": path_text, "ok": True, "reason": "import executed"}
    except Exception as exc:
        return {"path": path_text, "ok": False, "reason": str(exc)}


def registry_check() -> Dict[str, Any]:
    path = BOOTSTRAP_ROOT / "runtime" / "capability_registry_r1.json"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        ids = [item.get("capability_id") for item in payload.get("capabilities", []) if isinstance(item, dict)]
        required = {"session_state_manager", "mode_guard", "context_bundle_builder", "input_integrity_assessor"}
        missing = sorted(required - set(ids))
        return {"ok": not missing, "version": payload.get("version"), "capability_count": len(ids), "missing_required_ids": missing}
    except Exception as exc:
        return {"ok": False, "reason": str(exc)}


def run_doctor(*, ensure_state: bool = False, migrate_state: bool = False) -> Dict[str, Any]:
    files = [file_check(path) for path in REQUIRED_FILES]
    imports = [import_check(path) for path in IMPORT_CHECKS]
    missing = [item["path"] for item in files if not item["exists"] or not item["is_file"]]
    failed_imports = [item for item in imports if not item["ok"]]
    state = (
        inspect_state_schema(ensure=ensure_state, migrate=migrate_state).to_dict()
        if inspect_state_schema is not None
        else {"compatible": False, "writable_parent": False, "errors": ["state schema helper unavailable"]}
    )
    registry = registry_check()
    ok = not missing and not failed_imports and bool(registry.get("ok")) and bool(state.get("compatible")) and bool(state.get("writable_parent"))
    return {
        "schema_version": "lumina-doctor-v0.6",
        "ok": ok,
        "bootstrap_root": str(BOOTSTRAP_ROOT),
        "repo_root": str(REPO_ROOT),
        "python": sys.version.split()[0],
        "required_files": files,
        "import_checks": imports,
        "capability_registry": registry,
        "state": state,
        "missing_required_files": missing,
        "failed_imports": failed_imports,
        "authority_boundary": "Doctor reports readiness only; runtime governance remains authoritative.",
    }


def print_human(payload: Dict[str, Any]) -> None:
    print("Lumina doctor")
    print(f"  ok:              {payload['ok']}")
    print(f"  bootstrap root:  {payload['bootstrap_root']}")
    print(f"  python:          {payload['python']}")
    print(f"  registry ok:     {payload['capability_registry'].get('ok')}")
    print(f"  state schema:    {payload['state'].get('schema_version') or 'not created yet'}")
    for item in payload["missing_required_files"]:
        print(f"  missing:         {item}")
    for item in payload["failed_imports"]:
        print(f"  import failed:   {item['path']}: {item['reason']}")
    if not payload["state"].get("schema_exists"):
        print("  state setup:     run doctor with --ensure-state")
    if payload["state"].get("migration_required"):
        print("  state migrate:   run doctor with --migrate-state")


def main() -> int:
    parser = argparse.ArgumentParser(description="Check local Lumina host readiness.")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--ensure-state", action="store_true")
    parser.add_argument("--migrate-state", action="store_true")
    args = parser.parse_args()
    payload = run_doctor(ensure_state=args.ensure_state, migrate_state=args.migrate_state)
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print_human(payload)
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

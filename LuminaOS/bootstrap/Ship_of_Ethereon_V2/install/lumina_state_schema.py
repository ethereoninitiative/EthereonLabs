#!/usr/bin/env python3
"""Lumina local state schema helper.

Owns only host-layer state-shape inspection and migration markers. It does not
own runtime governance, canon lineage, checkpoint legality, or mode law.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional
import argparse
import json
import os
import sys

BOOTSTRAP_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[4]
RUNTIME_ROOT = BOOTSTRAP_ROOT / "runtime"
if str(RUNTIME_ROOT) not in sys.path:
    sys.path.insert(0, str(RUNTIME_ROOT))

from repo_paths_r1 import state_root as configured_state_root, state_root_source  # noqa: E402

DEFAULT_STATE_ROOT = configured_state_root()
CURRENT_STATE_SCHEMA_VERSION = "lumina-state-v0.3"

KNOWN_SUBDIRECTORIES = [
    "runtime_runner_r1_actiontype_logging",
    "projects",
    "sessions",
    "psi42_artifacts",
]


@dataclass
class StateSchemaStatus:
    state_root: str
    state_root_source: str
    schema_path: str
    exists: bool
    schema_exists: bool
    schema_version: Optional[str]
    current_schema_version: str
    writable_parent: bool
    compatible: bool
    migration_required: bool
    created_or_updated: bool
    errors: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def schema_path(state_root: Path) -> Path:
    return state_root / "state_schema.json"


def expected_state_schema_payload() -> Dict[str, Any]:
    return {
        "schema_version": CURRENT_STATE_SCHEMA_VERSION,
        "state_root_owner": "Lumina host/runtime local state",
        "state_location_contract": (
            "The active state root may be supplied by LUMINA_STATE_ROOT. "
            "Windows defaults to user-local application data; POSIX development "
            "keeps the historical repository-local default."
        ),
        "authority_boundary": (
            "State schema supports host readiness and migration only; "
            "runtime governance remains authoritative."
        ),
        "known_subdirectories": list(KNOWN_SUBDIRECTORIES),
        "migration_history": [],
    }


def read_schema_payload(path: Path) -> Optional[Dict[str, Any]]:
    if not path.exists():
        return None
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else None


def write_schema_payload(payload: Dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def migrate_schema_payload(payload: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if not payload:
        return expected_state_schema_payload()
    current = dict(payload)
    prior_version = current.get("schema_version")
    if prior_version == CURRENT_STATE_SCHEMA_VERSION:
        return current
    history = list(current.get("migration_history") or [])
    history.append(
        {
            "from": prior_version,
            "to": CURRENT_STATE_SCHEMA_VERSION,
            "reason": "host-layer state path and schema reconciliation",
        }
    )
    migrated = expected_state_schema_payload()
    migrated["migration_history"] = history
    return migrated


def inspect_state_schema(
    *,
    ensure: bool = False,
    migrate: bool = False,
    state_root: Path = DEFAULT_STATE_ROOT,
) -> StateSchemaStatus:
    path = schema_path(state_root)
    errors: List[str] = []
    created_or_updated = False
    parent = state_root.parent if state_root.parent.exists() else state_root.parent.parent
    if not parent.exists():
        parent = Path.home()
    writable_parent = bool(parent.exists() and os.access(parent, os.W_OK))

    payload: Optional[Dict[str, Any]] = None
    if path.exists():
        try:
            payload = read_schema_payload(path)
            if payload is None:
                errors.append("schema payload is not a JSON object")
        except Exception as exc:
            errors.append(f"schema read failed: {exc}")

    if ensure and payload is None and not errors:
        payload = expected_state_schema_payload()
        try:
            write_schema_payload(payload, path)
            created_or_updated = True
        except Exception as exc:
            errors.append(f"schema create failed: {exc}")

    version = payload.get("schema_version") if payload else None
    migration_required = bool(payload and version != CURRENT_STATE_SCHEMA_VERSION)

    if migrate and migration_required and not errors:
        try:
            payload = migrate_schema_payload(payload)
            write_schema_payload(payload, path)
            version = payload.get("schema_version")
            migration_required = False
            created_or_updated = True
        except Exception as exc:
            errors.append(f"schema migration failed: {exc}")

    compatible = version in {None, CURRENT_STATE_SCHEMA_VERSION} and not migration_required and not errors
    return StateSchemaStatus(
        state_root=str(state_root),
        state_root_source=state_root_source(),
        schema_path=str(path),
        exists=state_root.exists(),
        schema_exists=path.exists(),
        schema_version=version,
        current_schema_version=CURRENT_STATE_SCHEMA_VERSION,
        writable_parent=writable_parent,
        compatible=compatible,
        migration_required=migration_required,
        created_or_updated=created_or_updated,
        errors=errors,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect or reconcile the Lumina local state schema marker.")
    parser.add_argument("--ensure", action="store_true", help="Create the current schema marker if missing.")
    parser.add_argument("--migrate", action="store_true", help="Migrate an older known schema marker.")
    parser.add_argument("--state-root", type=Path, default=DEFAULT_STATE_ROOT)
    args = parser.parse_args()
    status = inspect_state_schema(ensure=args.ensure, migrate=args.migrate, state_root=args.state_root)
    print(json.dumps(status.to_dict(), indent=2))
    return 0 if status.compatible else 1


if __name__ == "__main__":
    raise SystemExit(main())

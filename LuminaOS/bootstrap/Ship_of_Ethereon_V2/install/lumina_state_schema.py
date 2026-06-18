#!/usr/bin/env python3
"""Lumina local state schema helper.

This helper owns only host-layer state-shape inspection and migration markers.
It does not own runtime governance, canon lineage, checkpoint legality, or mode law.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional
import json

BOOTSTRAP_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[4]
STATE_ROOT = REPO_ROOT / ".lumina_state" / "ship_of_ethereon_v2"
STATE_SCHEMA_PATH = STATE_ROOT / "state_schema.json"
CURRENT_STATE_SCHEMA_VERSION = "lumina-state-v0.1"

KNOWN_SUBDIRECTORIES = [
    "runtime receipts",
    "context bundles",
    "checkpoints",
    "governance logs",
    "studio state browser outputs",
]


@dataclass
class StateSchemaStatus:
    state_root: str
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


def expected_state_schema_payload() -> Dict[str, Any]:
    return {
        "schema_version": CURRENT_STATE_SCHEMA_VERSION,
        "state_root_owner": "Lumina host/runtime local state",
        "authority_boundary": "State schema supports install/readiness checks only; runtime governance remains authoritative.",
        "known_subdirectories": KNOWN_SUBDIRECTORIES,
        "migration_history": [],
    }


def read_schema_payload(schema_path: Path = STATE_SCHEMA_PATH) -> Optional[Dict[str, Any]]:
    if not schema_path.exists():
        return None
    with schema_path.open("r", encoding="utf-8") as f:
        payload = json.load(f)
    return payload if isinstance(payload, dict) else None


def write_schema_payload(payload: Dict[str, Any], schema_path: Path = STATE_SCHEMA_PATH) -> None:
    schema_path.parent.mkdir(parents=True, exist_ok=True)
    with schema_path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
        f.write("\n")


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
            "reason": "host-layer schema marker normalization",
        }
    )
    current.update(expected_state_schema_payload())
    current["migration_history"] = history
    return current


def inspect_state_schema(*, ensure: bool = False, migrate: bool = False) -> StateSchemaStatus:
    errors: List[str] = []
    created_or_updated = False
    writable_parent = STATE_ROOT.parent.exists() and STATE_ROOT.parent.is_dir()
    if not STATE_ROOT.parent.exists():
        writable_parent = REPO_ROOT.exists()
    try:
        writable_parent = bool(writable_parent and (STATE_ROOT.parent if STATE_ROOT.parent.exists() else REPO_ROOT).exists())
    except Exception:
        writable_parent = False

    payload: Optional[Dict[str, Any]] = None
    if STATE_SCHEMA_PATH.exists():
        try:
            payload = read_schema_payload()
        except Exception as exc:
            errors.append(f"schema read failed: {exc}")

    if ensure and payload is None and not errors:
        payload = expected_state_schema_payload()
        try:
            write_schema_payload(payload)
            created_or_updated = True
        except Exception as exc:
            errors.append(f"schema create failed: {exc}")

    schema_version = payload.get("schema_version") if payload else None
    migration_required = bool(payload and schema_version != CURRENT_STATE_SCHEMA_VERSION)

    if migrate and migration_required and not errors:
        try:
            payload = migrate_schema_payload(payload)
            write_schema_payload(payload)
            created_or_updated = True
            schema_version = payload.get("schema_version")
            migration_required = False
        except Exception as exc:
            errors.append(f"schema migration failed: {exc}")

    compatible = (
        schema_version in {None, CURRENT_STATE_SCHEMA_VERSION}
        and not migration_required
        and not errors
    )

    return StateSchemaStatus(
        state_root=str(STATE_ROOT),
        schema_path=str(STATE_SCHEMA_PATH),
        exists=STATE_ROOT.exists(),
        schema_exists=STATE_SCHEMA_PATH.exists(),
        schema_version=schema_version,
        current_schema_version=CURRENT_STATE_SCHEMA_VERSION,
        writable_parent=writable_parent,
        compatible=compatible,
        migration_required=migration_required,
        created_or_updated=created_or_updated,
        errors=errors,
    )


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Inspect or create the Lumina local state schema marker.")
    parser.add_argument("--ensure", action="store_true", help="Create the schema marker if missing.")
    parser.add_argument("--migrate", action="store_true", help="Migrate a known older schema marker to the current version.")
    args = parser.parse_args()
    status = inspect_state_schema(ensure=args.ensure, migrate=args.migrate)
    print(json.dumps(status.to_dict(), indent=2))
    return 0 if status.compatible else 1


if __name__ == "__main__":
    raise SystemExit(main())

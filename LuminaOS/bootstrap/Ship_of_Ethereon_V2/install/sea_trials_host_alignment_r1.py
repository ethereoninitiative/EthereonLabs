#!/usr/bin/env python3
"""Sea trial for state-schema and doctor contract reconciliation."""
from __future__ import annotations

import inspect
import json
import tempfile
from pathlib import Path

from lumina_doctor import run_doctor
from lumina_state_schema import (
    CURRENT_STATE_SCHEMA_VERSION,
    inspect_state_schema,
    schema_path,
)


def run_trial() -> dict:
    checks = {}
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory) / "state"
        created = inspect_state_schema(ensure=True, state_root=root)
        checks["ensure_creates_current_schema"] = (
            created.compatible
            and created.schema_exists
            and created.schema_version == CURRENT_STATE_SCHEMA_VERSION
        )

        old_payload = {
            "schema_version": "lumina-state-v0.1",
            "migration_history": [],
        }
        schema_path(root).write_text(json.dumps(old_payload, indent=2) + "\n", encoding="utf-8")
        before = inspect_state_schema(state_root=root)
        migrated = inspect_state_schema(migrate=True, state_root=root)
        checks["older_schema_requires_migration"] = before.migration_required and not before.compatible
        checks["migration_reaches_current_schema"] = (
            migrated.compatible
            and not migrated.migration_required
            and migrated.schema_version == CURRENT_STATE_SCHEMA_VERSION
        )

    signature = inspect.signature(run_doctor)
    checks["doctor_accepts_ensure_state"] = "ensure_state" in signature.parameters
    checks["doctor_accepts_migrate_state"] = "migrate_state" in signature.parameters

    return {
        "trial_id": "sea-trials-host-alignment-r1",
        "passed": all(checks.values()),
        "checks": checks,
        "authority_boundary": "Host alignment trial validates readiness contracts only; runtime governance remains authoritative.",
    }


if __name__ == "__main__":
    result = run_trial()
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["passed"] else 1)

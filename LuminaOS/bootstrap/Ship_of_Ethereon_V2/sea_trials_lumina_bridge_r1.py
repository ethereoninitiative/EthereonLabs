#!/usr/bin/env python3
"""Sea trial for Lumina Bridge R1."""
from __future__ import annotations

import json
from pathlib import Path
import shutil
import sys
import tempfile

ROOT = Path(__file__).resolve().parent
STUDIO = ROOT / "studio"
if str(STUDIO) not in sys.path:
    sys.path.insert(0, str(STUDIO))

from lumina_bridge_server_r1 import HTML  # noqa: E402
from lumina_bridge_state_r1 import build_bridge_state  # noqa: E402


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")


def main() -> int:
    temp_root = Path(tempfile.mkdtemp(prefix="lumina_bridge_r1_"))
    try:
        repo_root = temp_root / "repo"
        state_root = repo_root / ".lumina_state" / "ship_of_ethereon_v2"
        runtime_base = state_root / "runtime_runner_r1_actiontype_logging"

        write_json(
            state_root / "active_project.json",
            {
                "active_project_slug": "ethereonlabs",
                "active_project_name": "EthereonLabs",
                "project_root": str(state_root / "projects" / "ethereonlabs"),
            },
        )
        write_json(
            state_root / "active_session.json",
            {
                "active_session_id": "session-0007",
                "active_session_title": "Bridge construction",
                "project_slug": "ethereonlabs",
                "session_root": str(state_root / "projects" / "ethereonlabs" / "sessions" / "session-0007"),
            },
        )

        receipt = {
            "run_id": "run-bridge-r1",
            "created_at": "2026-06-25T00:00:00+00:00",
            "requested_action": "bridge_sea_trial",
            "action_type": "audit",
            "requested_mode": "Continuity",
            "target_mode": "Observation",
            "halted": False,
            "session_id": "runtime-session-22",
            "context_bundle_id": "bundle-bridge-r1",
            "governance_chain_status": {"valid": True},
            "canon_lineage": {"current_head": None},
            "exposed_capabilities": [],
            "lumina_return_host_artifacts": {"project_id": "ethereonlabs"},
        }
        write_json(runtime_base / "logs" / "run-bridge-r1.json", receipt)
        write_jsonl(
            runtime_base / "governance_log_r1.jsonl",
            [{"event_type": "cycle_start", "record_hash": "abc", "metadata": {"action_type": "audit"}}],
        )
        write_jsonl(runtime_base / "canon_lineage_r1.jsonl", [])

        latest = {
            "schema_version": "lumina-runtime-ui-cycle-v0.4",
            "timestamp": "2026-06-25T00:00:00+00:00",
            "run_id": "run-bridge-r1",
            "requested_action": "bridge_sea_trial",
            "action_type": "audit",
            "mode": {"requested": "Continuity", "current": "Observation"},
            "status": {"halted": False, "reason": None, "label": "Stable"},
            "capabilities": ["session_state_manager", "mode_guard"],
            "probe": {"active": True, "instrument_version": "v1.8", "coherence": 0.8, "presence": 0.7, "lock": 0.6},
        }
        truth = {
            "schema_version": "lumina-runtime-truth-public-snapshot-v0.2",
            "latest_cycle_run_id": "run-bridge-r1",
            "latest_cycle_timestamp": "2026-06-25T00:00:00+00:00",
            "runtime_truth_scope": {"does_not_override_committed_authority": True},
            "runtime_truth": {
                "committed_authority": {
                    "governance_chain": {"status": "verified", "valid": True, "event_count": 1},
                    "canon_lineage": {"status": "verified", "valid": True, "current_head": "canon-0001", "record_count": 1},
                    "promotion": {"valid": True, "passed": True, "promotion_id": "promotion-0001"},
                    "post_promotion_verification": {"valid": True, "passed": True},
                    "evidence_paths": {},
                },
                "observed_runtime_state": {
                    "scope": "ephemeral_observation_state",
                    "does_not_override_committed_authority": True,
                    "governance_chain": {"status": "empty_or_missing", "valid": True, "event_count": 0},
                    "canon_lineage": {"status": "empty_or_missing", "valid": True, "current_head": None, "record_count": 0},
                },
            },
        }
        write_json(repo_root / "public" / "runtime" / "latest_cycle.json", latest)
        write_json(repo_root / "public" / "runtime" / "runtime_truth_snapshot.json", truth)

        state = build_bridge_state(
            repo_root=repo_root,
            state_root=state_root,
            runtime_base=runtime_base,
            limit=6,
        )

        checks = {
            "read_only": state.get("read_only") is True,
            "project_visible": state.get("workspace", {}).get("project", {}).get("slug") == "ethereonlabs",
            "harbor_session_visible": state.get("workspace", {}).get("harbor_session", {}).get("session_id") == "session-0007",
            "truth_aligned": state.get("runtime_truth_alignment", {}).get("aligned") is True,
            "committed_canon_preserved": state.get("authority", {}).get("committed", {}).get("canon_lineage", {}).get("current_head") == "canon-0001",
            "observed_empty_does_not_replace_canon": state.get("authority", {}).get("observed", {}).get("canon_lineage", {}).get("current_head") is None,
            "runtime_reference_distinct": state.get("correlation", {}).get("references", {}).get("runtime_session_id") == "runtime-session-22",
            "navigation_points_to_studio": state.get("navigation", {}).get("primary_command") == "lumina studio",
            "html_has_bridge": "The Bridge" in HTML and "Ship Position" in HTML,
            "html_has_no_mutating_form": "method=\"post\"" not in HTML.lower() and "action=\"/run\"" not in HTML.lower(),
            "authority_boundary_present": "read-only orientation surface" in state.get("authority_boundary", ""),
        }
        summary = {
            "suite": "Lumina Bridge R1",
            "passed": all(checks.values()),
            "checks": checks,
            "bridge_schema": state.get("schema_version"),
        }
        print(json.dumps(summary, indent=2))
        return 0 if summary["passed"] else 1
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())

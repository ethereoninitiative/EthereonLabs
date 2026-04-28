#!/usr/bin/env python3
"""
Lumina Integrated Beta Loop r1

Purpose
-------
This script is the first repo-native integrated proof scaffold for the Lumina OS beta loop.

It does not claim the full OS is complete. It proves a narrow, inspectable continuity path:

1. start local runtime scaffold
2. create or load a project
3. record workspace state
4. write a checkpoint
5. simulate exit
6. resume project
7. restore context
8. produce advisory next action
9. map advisory into Chamber-style queue shape
10. apply explicit human decision (accept/reject via CLI flag)
11. log the cycle
12. verify state/history on the next run

Boundary
--------
- Advisory only.
- No autonomous tool execution.
- No canon mutation.
- No mode-law mutation.
- No hidden governance authority.
- Uses repo-local state under `_runtime_state/lumina_integrated_beta_loop_r1` by default.

This file intentionally avoids importing unstable adjacent modules so it can act as a dependable
integration harness while the richer V2 runtime pieces continue to mature around it.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4


DEFAULT_BASE_DIR = Path(__file__).resolve().parents[4] / "_runtime_state" / "lumina_integrated_beta_loop_r1"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def stable_hash(payload: Any) -> str:
    encoded = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def read_json(path: Path, fallback: Any) -> Any:
    if not path.exists():
        return fallback
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return fallback


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")


@dataclass
class WorkspaceState:
    project_id: str
    active_surface: str
    open_threads: List[str]
    working_stance: str
    continuation_notes: str
    updated_at_utc: str = field(default_factory=utc_now)


@dataclass
class CheckpointRecord:
    checkpoint_id: str
    project_id: str
    workspace_state: WorkspaceState
    created_at_utc: str
    payload_hash: str


@dataclass
class AdvisoryRecord:
    advisory_id: str
    project_id: str
    recommended_next_action: str
    rationale: str
    source_checkpoint_id: str
    created_at_utc: str
    advisory_hash: str


@dataclass
class QueueItem:
    queue_item_id: str
    advisory_id: str
    project_id: str
    status: str
    human_decision: str
    action_summary: str
    created_at_utc: str
    completed_at_utc: Optional[str] = None


class LuminaIntegratedBetaLoop:
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.projects_dir = base_dir / "projects"
        self.logs_dir = base_dir / "logs"
        self.queue_path = base_dir / "chamber_advisory_queue.json"
        self.history_path = base_dir / "loop_history.json"

    def project_dir(self, project_id: str) -> Path:
        return self.projects_dir / project_id

    def latest_checkpoint_path(self, project_id: str) -> Path:
        return self.project_dir(project_id) / "latest_checkpoint.json"

    def checkpoint_history_path(self, project_id: str) -> Path:
        return self.project_dir(project_id) / "checkpoint_history.json"

    def advisory_history_path(self, project_id: str) -> Path:
        return self.project_dir(project_id) / "advisory_history.json"

    def record_workspace(self, project_id: str, stance: str, note: str, surface: str, threads: List[str]) -> WorkspaceState:
        return WorkspaceState(
            project_id=project_id,
            active_surface=surface,
            open_threads=threads,
            working_stance=stance,
            continuation_notes=note,
        )

    def write_checkpoint(self, workspace_state: WorkspaceState) -> CheckpointRecord:
        payload_without_hash = {
            "checkpoint_id": f"chk_{uuid4().hex[:12]}",
            "project_id": workspace_state.project_id,
            "workspace_state": asdict(workspace_state),
            "created_at_utc": utc_now(),
        }
        payload_hash = stable_hash(payload_without_hash)
        checkpoint = CheckpointRecord(payload_hash=payload_hash, **payload_without_hash)
        payload = asdict(checkpoint)

        write_json(self.latest_checkpoint_path(workspace_state.project_id), payload)
        history = read_json(self.checkpoint_history_path(workspace_state.project_id), [])
        history.append(payload)
        write_json(self.checkpoint_history_path(workspace_state.project_id), history[-50:])
        return checkpoint

    def restore_latest_context(self, project_id: str) -> Optional[CheckpointRecord]:
        payload = read_json(self.latest_checkpoint_path(project_id), None)
        if not payload:
            return None
        ws = WorkspaceState(**payload["workspace_state"])
        return CheckpointRecord(
            checkpoint_id=payload["checkpoint_id"],
            project_id=payload["project_id"],
            workspace_state=ws,
            created_at_utc=payload["created_at_utc"],
            payload_hash=payload["payload_hash"],
        )

    def produce_advisory(self, checkpoint: CheckpointRecord) -> AdvisoryRecord:
        ws = checkpoint.workspace_state
        history = read_json(self.advisory_history_path(ws.project_id), [])
        prior_alignment = len(history)

        if "dashboard" in ws.active_surface.lower():
            action = "Inspect dashboard state, confirm fallback behavior, then capture the next continuity snapshot."
        elif "chamber" in ws.active_surface.lower():
            action = "Review pending advisories, accept or reject one explicitly, then verify queue state."
        else:
            action = "Resume the project surface, verify restored context, and choose one bounded next step."

        if prior_alignment:
            rationale = (
                f"Restored project stance '{ws.working_stance}' from checkpoint {checkpoint.checkpoint_id}; "
                f"{prior_alignment} prior advisory record(s) exist, so this recommendation continues an existing line."
            )
        else:
            rationale = (
                f"Restored project stance '{ws.working_stance}' from checkpoint {checkpoint.checkpoint_id}; "
                "no prior advisory history was found, so this is a first-pass recommendation."
            )

        payload_without_hash = {
            "advisory_id": f"adv_{uuid4().hex[:12]}",
            "project_id": ws.project_id,
            "recommended_next_action": action,
            "rationale": rationale,
            "source_checkpoint_id": checkpoint.checkpoint_id,
            "created_at_utc": utc_now(),
        }
        advisory_hash = stable_hash(payload_without_hash)
        advisory = AdvisoryRecord(advisory_hash=advisory_hash, **payload_without_hash)

        history.append(asdict(advisory))
        write_json(self.advisory_history_path(ws.project_id), history[-50:])
        return advisory

    def map_to_chamber_queue(self, advisory: AdvisoryRecord, human_decision: str) -> QueueItem:
        status = "queued" if human_decision == "accept" else "rejected"
        item = QueueItem(
            queue_item_id=f"q_{uuid4().hex[:12]}",
            advisory_id=advisory.advisory_id,
            project_id=advisory.project_id,
            status=status,
            human_decision=human_decision,
            action_summary=advisory.recommended_next_action,
            created_at_utc=utc_now(),
            completed_at_utc=None if status == "queued" else utc_now(),
        )
        queue = read_json(self.queue_path, [])
        queue.append(asdict(item))
        write_json(self.queue_path, queue[-100:])
        return item

    def append_loop_log(self, record: Dict[str, Any]) -> Dict[str, Any]:
        history = read_json(self.history_path, [])
        previous_hash = history[-1]["record_hash"] if history else None
        payload = {
            "loop_id": f"loop_{uuid4().hex[:12]}",
            "created_at_utc": utc_now(),
            "previous_hash": previous_hash,
            **record,
        }
        payload["record_hash"] = stable_hash(payload)
        history.append(payload)
        write_json(self.history_path, history[-100:])
        return payload

    def run(self, project_id: str, stance: str, note: str, surface: str, threads: List[str], decision: str) -> Dict[str, Any]:
        workspace = self.record_workspace(project_id, stance, note, surface, threads)
        checkpoint = self.write_checkpoint(workspace)

        # Simulated exit boundary: after this point, the loop must restore from recorded state.
        restored = self.restore_latest_context(project_id)
        if restored is None:
            raise RuntimeError("Failed to restore latest context after checkpoint write.")

        advisory = self.produce_advisory(restored)
        queue_item = self.map_to_chamber_queue(advisory, decision)

        verification = {
            "checkpoint_restored": restored.checkpoint_id == checkpoint.checkpoint_id,
            "project_id_preserved": restored.project_id == project_id,
            "advisory_project_match": advisory.project_id == project_id,
            "queue_project_match": queue_item.project_id == project_id,
            "decision_respected": queue_item.human_decision == decision,
            "accepted_items_queue_only": (decision == "accept" and queue_item.status == "queued") or (decision == "reject" and queue_item.status == "rejected"),
        }
        verification["passed"] = all(verification.values())

        loop_log = self.append_loop_log(
            {
                "project_id": project_id,
                "checkpoint_id": checkpoint.checkpoint_id,
                "advisory_id": advisory.advisory_id,
                "queue_item_id": queue_item.queue_item_id,
                "human_decision": decision,
                "verification": verification,
                "boundary": {
                    "autonomous_tool_execution": False,
                    "canon_mutation": False,
                    "mode_law_mutation": False,
                    "governance_authority_granted": False,
                    "advisory_only": True,
                },
            }
        )

        return {
            "status": "passed" if verification["passed"] else "failed",
            "workspace_state": asdict(workspace),
            "checkpoint": asdict(checkpoint),
            "restored_checkpoint_id": restored.checkpoint_id,
            "advisory": asdict(advisory),
            "queue_item": asdict(queue_item),
            "verification": verification,
            "loop_log": loop_log,
            "state_root": str(self.base_dir),
        }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Lumina integrated beta loop scaffold.")
    parser.add_argument("--project-id", default="lumina-beta-demo", help="Project id to create/load.")
    parser.add_argument("--stance", default="continue", help="Working stance to preserve.")
    parser.add_argument("--note", default="Prove one integrated continuity loop.", help="Continuation note to checkpoint.")
    parser.add_argument("--surface", default="Lumina Studio", help="Active workspace surface name.")
    parser.add_argument("--thread", action="append", default=[], help="Open thread label; may be repeated.")
    parser.add_argument("--decision", choices=["accept", "reject"], default="accept", help="Explicit human decision for advisory.")
    parser.add_argument("--base-dir", default=str(DEFAULT_BASE_DIR), help="Repo-local state root.")
    parser.add_argument("--json", action="store_true", help="Print full JSON output.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    threads = args.thread or ["continuity", "self-guidance", "consent-queue"]
    loop = LuminaIntegratedBetaLoop(Path(args.base_dir))
    result = loop.run(
        project_id=args.project_id,
        stance=args.stance,
        note=args.note,
        surface=args.surface,
        threads=threads,
        decision=args.decision,
    )
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False))
    else:
        print(f"Lumina integrated beta loop: {result['status']}")
        print(f"Project: {args.project_id}")
        print(f"Checkpoint: {result['checkpoint']['checkpoint_id']}")
        print(f"Advisory: {result['advisory']['recommended_next_action']}")
        print(f"Decision: {args.decision} → queue status {result['queue_item']['status']}")
        print(f"State root: {result['state_root']}")
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
import json


"""
continuity_steward_r1.py

A bounded temporal steward for the Lumina substrate.

It may:
- preserve session residue
- summarize recent continuity-relevant events
- suggest lawful observation or return cycles
- emit sleep / wake recommendations

It may not:
- mutate canon
- define governance law
- infer load-bearing intent
- override mode legality
- become primary continuity authority
"""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_utc(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except Exception:
        return None


@dataclass
class StewardPolicy:
    observation_interval_minutes: int = 90
    idle_sleep_minutes: int = 20
    max_residue_entries: int = 200
    resume_brief_entries: int = 5
    default_available_tools: List[str] = field(
        default_factory=lambda: [
            "runtime_spine",
            "runtime_runner",
            "sea_trials",
            "capability_registry",
        ]
    )
    default_feature_flags: List[str] = field(default_factory=lambda: ["ETHEREON_OBSERVATION"])


@dataclass
class WakeCondition:
    condition_type: str
    reason: str
    threshold_utc: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ResidueEntry:
    timestamp_utc: str
    session_id: str
    current_mode: str
    requested_action: Optional[str] = None
    action_type: Optional[str] = None
    last_completed_action: Optional[str] = None
    pending_next_action: Optional[str] = None
    checkpoint_path: Optional[str] = None
    governance_log_path: Optional[str] = None
    governance_hash: Optional[str] = None
    summary: str = ""
    exposed_capability_ids: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class StewardDecision:
    should_wake: bool
    should_sleep: bool
    lawful_target_mode: str
    requested_action: str
    action_type: str
    reason: str
    continuation_notes: List[str] = field(default_factory=list)
    wake_conditions: List[Dict[str, Any]] = field(default_factory=list)
    proposed_cycle: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ContinuitySteward:
    """Non-sovereign temporal steward for Lumina's governed substrate."""

    def __init__(self, base_dir: str | Path, policy: Optional[StewardPolicy] = None):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.policy = policy or StewardPolicy()
        self.residue_path = self.base_dir / "continuity_steward_residue_r1.jsonl"
        self.state_path = self.base_dir / "continuity_steward_state_r1.json"
        if not self.state_path.exists():
            self._write_state(
                {
                    "created_at": utc_now(),
                    "last_observation_at": None,
                    "last_sleep_at": None,
                    "last_resume_brief_at": None,
                    "steward_version": "r1",
                }
            )

    # ------------------------------------------------------------------
    # Persistence helpers
    # ------------------------------------------------------------------
    def _read_state(self) -> Dict[str, Any]:
        with self.state_path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def _write_state(self, payload: Dict[str, Any]) -> None:
        with self.state_path.open("w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

    def read_residue(self) -> List[Dict[str, Any]]:
        if not self.residue_path.exists():
            return []
        rows: List[Dict[str, Any]] = []
        with self.residue_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    rows.append(json.loads(line))
        return rows

    def _trim_residue(self, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if len(rows) <= self.policy.max_residue_entries:
            return rows
        return rows[-self.policy.max_residue_entries :]

    def _write_residue(self, rows: List[Dict[str, Any]]) -> None:
        rows = self._trim_residue(rows)
        with self.residue_path.open("w", encoding="utf-8") as f:
            for row in rows:
                f.write(json.dumps(row) + "\n")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def ingest_runner_result(
        self,
        runner_result: Dict[str, Any],
        *,
        summary_override: Optional[str] = None,
    ) -> Dict[str, Any]:
        governance = runner_result.get("governance", {})
        transition = governance.get("transition", {})
        mutation = governance.get("mutation", {})
        summary = summary_override or self._build_summary(runner_result)

        entry = ResidueEntry(
            timestamp_utc=utc_now(),
            session_id=runner_result.get("session_id", "unknown-session"),
            current_mode=runner_result.get("target_mode") or runner_result.get("requested_mode") or "Continuity",
            requested_action=runner_result.get("requested_action"),
            action_type=runner_result.get("action_type"),
            last_completed_action=transition.get("reason") or mutation.get("reason"),
            pending_next_action=self._derive_pending_next_action(runner_result),
            checkpoint_path=runner_result.get("checkpoint_path"),
            governance_log_path=runner_result.get("governance_log_path"),
            governance_hash=(runner_result.get("governance_chain_status") or {}).get("latest_event_hash"),
            summary=summary,
            exposed_capability_ids=[
                cap.get("capability_id")
                for cap in runner_result.get("exposed_capabilities", [])
                if isinstance(cap, dict) and cap.get("capability_id")
            ],
        )

        rows = self.read_residue()
        rows.append(entry.to_dict())
        self._write_residue(rows)
        return entry.to_dict()

    def build_resume_brief(self, *, session_id: Optional[str] = None, limit: Optional[int] = None) -> List[str]:
        rows = self.read_residue()
        if session_id:
            rows = [row for row in rows if row.get("session_id") == session_id]
        rows = rows[-(limit or self.policy.resume_brief_entries) :]
        brief: List[str] = []
        for row in rows:
            action = row.get("requested_action") or "unknown_action"
            mode = row.get("current_mode") or "unknown_mode"
            summary = row.get("summary") or "no summary"
            brief.append(f"{row.get('timestamp_utc')}: [{mode}] {action} — {summary}")
        state = self._read_state()
        state["last_resume_brief_at"] = utc_now()
        self._write_state(state)
        return brief

    def evaluate(
        self,
        session_payload: Dict[str, Any],
        *,
        now_utc: Optional[str] = None,
    ) -> Dict[str, Any]:
        now_dt = parse_utc(now_utc) or datetime.now(timezone.utc)
        current_mode = session_payload.get("current_mode", "Continuity")
        session_id = session_payload.get("session_id", "unknown-session")
        pending_next_action = session_payload.get("pending_next_action")
        last_completed_action = session_payload.get("last_completed_action")
        last_checkpoint = session_payload.get("last_checkpoint")
        state = self._read_state()
        last_observation_at = parse_utc(state.get("last_observation_at"))

        lawful_target_mode = self._lawful_target_mode(current_mode)
        wake_conditions = self._build_wake_conditions(
            now_dt=now_dt,
            pending_next_action=pending_next_action,
            last_checkpoint=last_checkpoint,
            last_observation_at=last_observation_at,
            current_mode=current_mode,
        )

        should_wake = any(condition.condition_type != "sleep_window" for condition in wake_conditions)
        should_sleep = not should_wake

        if should_wake:
            requested_action = f"continuity_steward_review_{session_id[:8]}"
            action_type = "audit"
            reason = self._reason_from_conditions(wake_conditions)
            continuation_notes = self.build_resume_brief(session_id=session_id)
            proposed_cycle = {
                "current_mode": current_mode,
                "target_mode": lawful_target_mode,
                "requested_action": requested_action,
                "action_type": action_type,
                "continuation_notes": continuation_notes,
                "available_tools": list(self.policy.default_available_tools),
                "enabled_feature_flags": list(self.policy.default_feature_flags),
            }
            state["last_observation_at"] = utc_now()
            self._write_state(state)
        else:
            requested_action = "continuity_steward_sleep"
            action_type = "audit"
            reason = "no wake condition exceeded threshold; steward remains quiescent"
            continuation_notes = [
                f"Current mode: {current_mode}",
                f"Last completed action: {last_completed_action or 'none recorded'}",
                "No lawful continuity wake is presently required.",
            ]
            proposed_cycle = None
            state["last_sleep_at"] = utc_now()
            self._write_state(state)

        decision = StewardDecision(
            should_wake=should_wake,
            should_sleep=should_sleep,
            lawful_target_mode=lawful_target_mode,
            requested_action=requested_action,
            action_type=action_type,
            reason=reason,
            continuation_notes=continuation_notes,
            wake_conditions=[condition.to_dict() for condition in wake_conditions],
            proposed_cycle=proposed_cycle,
        )
        return decision.to_dict()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _build_summary(self, runner_result: Dict[str, Any]) -> str:
        target_mode = runner_result.get("target_mode", "unknown-mode")
        action_type = runner_result.get("action_type", "unknown-action")
        halted = runner_result.get("halted", False)
        exposed = len(runner_result.get("exposed_capabilities", []))
        if halted:
            return f"cycle halted in {target_mode} during {action_type}; no further action proposed"
        return f"cycle completed in {target_mode} during {action_type}; {exposed} capabilities exposed"

    def _derive_pending_next_action(self, runner_result: Dict[str, Any]) -> Optional[str]:
        if runner_result.get("halted"):
            return runner_result.get("halt_reason")
        if runner_result.get("probe_artifacts"):
            return "review probe artifacts and decide whether another observation pass is useful"
        if runner_result.get("action_type") == "promotion":
            return "review promoted canon lineage result before further mutation"
        return "resume work from latest lawful checkpoint"

    def _lawful_target_mode(self, current_mode: str) -> str:
        if current_mode in {"Continuity", "Sandbox", "DryDock", "Observation"}:
            return "Observation"
        if current_mode == "Canon":
            return "Continuity"
        return "Continuity"

    def _build_wake_conditions(
        self,
        *,
        now_dt: datetime,
        pending_next_action: Optional[str],
        last_checkpoint: Optional[str],
        last_observation_at: Optional[datetime],
        current_mode: str,
    ) -> List[WakeCondition]:
        conditions: List[WakeCondition] = []

        if pending_next_action:
            conditions.append(
                WakeCondition(
                    condition_type="pending_next_action",
                    reason="session already contains an explicit pending next action",
                    metadata={"pending_next_action": pending_next_action},
                )
            )

        if current_mode in {"Continuity", "Sandbox", "DryDock", "Observation"}:
            threshold = now_dt - timedelta(minutes=self.policy.observation_interval_minutes)
            if last_observation_at is None or last_observation_at <= threshold:
                conditions.append(
                    WakeCondition(
                        condition_type="observation_cadence",
                        reason="observation interval threshold exceeded",
                        threshold_utc=threshold.isoformat(),
                        metadata={"observation_interval_minutes": self.policy.observation_interval_minutes},
                    )
                )

        if last_checkpoint:
            conditions.append(
                WakeCondition(
                    condition_type="checkpoint_available",
                    reason="a lawful checkpoint exists and can anchor a return pass",
                    metadata={"last_checkpoint": last_checkpoint},
                )
            )

        if not conditions:
            conditions.append(
                WakeCondition(
                    condition_type="sleep_window",
                    reason="no pending action, no cadence breach, and no checkpoint-triggered review required",
                )
            )
        return conditions

    def _reason_from_conditions(self, conditions: List[WakeCondition]) -> str:
        active = [condition.reason for condition in conditions if condition.condition_type != "sleep_window"]
        return "; ".join(active) if active else "no wake reason"


if __name__ == "__main__":
    base_dir = Path("/mnt/data/lumina_continuity_steward_demo")
    steward = ContinuitySteward(base_dir)

    runner_result = {
        "session_id": "demo-session-001",
        "requested_mode": "Continuity",
        "target_mode": "Observation",
        "requested_action": "demo_observation_pass",
        "action_type": "audit",
        "checkpoint_path": "/tmp/demo_checkpoint.json",
        "governance_log_path": "/tmp/demo_governance.jsonl",
        "governance_chain_status": {"latest_event_hash": "abc123"},
        "halted": False,
        "exposed_capabilities": [
            {"capability_id": "continuity_assessor"},
            {"capability_id": "psi42_probe_interface"},
        ],
        "probe_artifacts": {"run_id": "probe-demo"},
    }
    steward.ingest_runner_result(runner_result)

    session_payload = {
        "session_id": "demo-session-001",
        "current_mode": "Continuity",
        "pending_next_action": "resume work from latest lawful checkpoint",
        "last_completed_action": "tool:runtime_runner",
        "last_checkpoint": "/tmp/demo_checkpoint.json",
    }
    print(json.dumps(steward.evaluate(session_payload), indent=2))

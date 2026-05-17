from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
import hashlib
import json
import subprocess
import uuid

try:
    from .ethereonic_layer_r1 import EthereonicLayerRegistry
except Exception:
    try:
        from ethereonic_layer_r1 import EthereonicLayerRegistry
    except Exception:
        EthereonicLayerRegistry = None

try:
    from .governance_integrity_r1 import GovernanceIntegrityChain
except Exception:
    try:
        from governance_integrity_r1 import GovernanceIntegrityChain
    except Exception:
        GovernanceIntegrityChain = None

try:
    from .project_orientation_vector_v0_1 import (
        ProjectOrientationVector,
        attach_to_supplemental_context as attach_project_orientation_to_supplemental,
        orient_artifacts,
        orientation_resume_note,
    )
except Exception:
    try:
        from project_orientation_vector_v0_1 import (
            ProjectOrientationVector,
            attach_to_supplemental_context as attach_project_orientation_to_supplemental,
            orient_artifacts,
            orientation_resume_note,
        )
    except Exception:
        ProjectOrientationVector = None
        attach_project_orientation_to_supplemental = None
        orient_artifacts = None
        orientation_resume_note = None

try:
    from .repo_paths_r1 import repo_root as _repo_root_helper
except Exception:
    try:
        from repo_paths_r1 import repo_root as _repo_root_helper
    except Exception:
        _repo_root_helper = None


def infer_repo_root(explicit_repo_path: Optional[str | Path] = None) -> Optional[Path]:
    if explicit_repo_path:
        candidate = Path(explicit_repo_path).resolve()
        return candidate if candidate.exists() else None
    if _repo_root_helper is not None:
        try:
            candidate = Path(_repo_root_helper()).resolve()
            return candidate if candidate.exists() else None
        except Exception:
            pass
    for parent in Path(__file__).resolve().parents:
        if (parent / ".git").exists() or (parent / "LuminaOS").exists():
            return parent
    return None


def infer_runtime_root() -> Optional[Path]:
    candidate = Path(__file__).resolve().parent
    return candidate if candidate.exists() else None


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _coerce_project_orientation_vector(project_orientation_vector: Optional[Any]) -> Optional[Any]:
    if project_orientation_vector is None:
        return None
    if ProjectOrientationVector is None:
        raise ValueError("ProjectOrientationVector support is unavailable in this runtime")
    if isinstance(project_orientation_vector, ProjectOrientationVector):
        vector = project_orientation_vector
    elif isinstance(project_orientation_vector, dict):
        vector = ProjectOrientationVector(
            focus=project_orientation_vector.get("focus", "continuity"),
            depth=project_orientation_vector.get("depth", "structural"),
            intent=project_orientation_vector.get("intent", "read"),
            annotation=project_orientation_vector.get("annotation"),
        )
    else:
        raise TypeError("project_orientation_vector must be a dict or ProjectOrientationVector instance")
    if not vector.is_valid():
        raise ValueError(
            f"ProjectOrientationVector is invalid and cannot be attached: {vector.validation_errors()}"
        )
    return vector


@dataclass
class ContinuityState:
    mode_stability_ratio: float = 1.0
    unauthorized_transition_attempts: int = 0
    checkpoint_count: int = 0
    resume_count: int = 0


@dataclass
class EthereonicOverlay:
    active: bool = False
    anchor_language: List[str] = field(default_factory=lambda: ["english"])
    continuity_phrase: Optional[str] = None
    harmonic_signature: List[int] = field(default_factory=list)
    spiral_reference: Optional[str] = None


@dataclass
class SessionState:
    session_id: str
    started_at: str
    current_mode: str = "Continuity"
    turn_index: int = 0
    last_checkpoint: Optional[str] = None
    artifacts_in_scope: List[str] = field(default_factory=list)
    tool_events: List[Dict[str, Any]] = field(default_factory=list)
    continuity_state: ContinuityState = field(default_factory=ContinuityState)
    pending_next_action: Optional[str] = None
    last_completed_action: Optional[str] = None
    ethereonic_overlay: EthereonicOverlay = field(default_factory=EthereonicOverlay)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class SessionEngine:
    """Maintains live session continuity without making symbolic overlays load-bearing."""

    def __init__(self, base_dir: str | Path):
        self.base_dir = Path(base_dir)
        self.session_dir = self.base_dir / "sessions"
        self.checkpoint_dir = self.base_dir / "checkpoints"
        self.session_dir.mkdir(parents=True, exist_ok=True)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)

    def session_path(self, session_id: str) -> Path:
        return self.session_dir / f"{session_id}.json"

    def checkpoint_path(self, session_id: str, label: str) -> Path:
        safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in label)
        return self.checkpoint_dir / f"{session_id}__{safe}.json"

    def save_session(self, state: SessionState) -> None:
        with self.session_path(state.session_id).open("w", encoding="utf-8") as f:
            json.dump(state.to_dict(), f, indent=2)

    def load_session(self, session_id: str) -> SessionState:
        with self.session_path(session_id).open("r", encoding="utf-8") as f:
            payload = json.load(f)
        return self._from_dict(payload)

    def create_session(
        self,
        *,
        mode: str = "Continuity",
        artifacts_in_scope: Optional[List[str]] = None,
        ethereonic_overlay: Optional[Dict[str, Any]] = None,
    ) -> SessionState:
        state = SessionState(
            session_id=str(uuid.uuid4()),
            started_at=utc_now(),
            current_mode=mode,
            artifacts_in_scope=list(artifacts_in_scope or []),
        )
        if ethereonic_overlay:
            state.ethereonic_overlay = EthereonicOverlay(**ethereonic_overlay)
        self.save_session(state)
        return state

    def initialize_turn(
        self,
        session_id: str,
        *,
        context_bundle_id: Optional[str] = None,
        artifacts_in_scope: Optional[List[str]] = None,
    ) -> SessionState:
        state = self.load_session(session_id)
        state.turn_index += 1
        if artifacts_in_scope is not None:
            state.artifacts_in_scope = list(artifacts_in_scope)
        if context_bundle_id:
            state.pending_next_action = f"work from context bundle {context_bundle_id}"
        self.save_session(state)
        return state

    def record_tool_event(
        self,
        session_id: str,
        tool_name: str,
        summary: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> SessionState:
        state = self.load_session(session_id)
        state.tool_events.append(
            {
                "timestamp": utc_now(),
                "tool_name": tool_name,
                "summary": summary,
                "metadata": metadata or {},
            }
        )
        state.last_completed_action = f"tool:{tool_name}"
        self.save_session(state)
        return state

    def change_mode(self, session_id: str, new_mode: str) -> SessionState:
        state = self.load_session(session_id)
        old_mode = state.current_mode
        state.current_mode = new_mode
        if old_mode != new_mode:
            total_turns = max(1, state.turn_index)
            stable_turns = max(0, total_turns - 1)
            state.continuity_state.mode_stability_ratio = stable_turns / total_turns
        self.save_session(state)
        return state

    def write_checkpoint(self, session_id: str, label: str) -> Path:
        state = self.load_session(session_id)
        path = self.checkpoint_path(session_id, label)
        payload = {
            "checkpoint_label": label,
            "created_at": utc_now(),
            "session_state": state.to_dict(),
        }
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        payload["checkpoint_hash"] = sha256_text(encoded)
        with path.open("w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
        state.last_checkpoint = str(path)
        state.continuity_state.checkpoint_count += 1
        self.save_session(state)
        return path

    def resume_from_checkpoint(self, checkpoint_path: str | Path) -> SessionState:
        with Path(checkpoint_path).open("r", encoding="utf-8") as f:
            payload = json.load(f)
        state = self._from_dict(payload["session_state"])
        state.continuity_state.resume_count += 1
        self.save_session(state)
        return state

    @staticmethod
    def _from_dict(payload: Dict[str, Any]) -> SessionState:
        data = dict(payload)
        data["continuity_state"] = ContinuityState(**data.get("continuity_state", {}))
        data["ethereonic_overlay"] = EthereonicOverlay(**data.get("ethereonic_overlay", {}))
        return SessionState(**data)


ALLOWED_TRANSITIONS: Dict[str, List[str]] = {
    "Continuity": ["Sandbox", "DryDock", "Observation"],
    "Sandbox": ["Continuity", "DryDock", "Observation"],
    "DryDock": ["Continuity", "Observation", "Canon"],
    "Observation": ["Continuity", "Sandbox", "DryDock"],
    "Canon": ["Continuity"],
}

MUTATION_RULES: Dict[str, bool] = {
    "Continuity": False,
    "Sandbox": False,
    "DryDock": True,
    "Observation": False,
    "Canon": False,
}

PROMOTION_FIELDS = [
    "validation_artifact_id",
    "test_execution_log",
    "change_summary",
    "structural_impact_assessment",
    "regression_check_confirmation",
    "conceptual_layer_check_confirmation",
]

LEGACY_PROMOTION_ALIASES = {
    "conceptual_layer_check": "conceptual_layer_check_confirmation",
}


@dataclass
class GovernanceDecision:
    allowed: bool
    reason: str
    audit_event: Optional[dict] = None


class ModeGuard:
    """Enforces lawful transitions, mutation limits, promotion gates, and symbolic separation."""

    def validate_transition(self, current_mode: str, new_mode: str) -> GovernanceDecision:
        if current_mode == new_mode:
            return GovernanceDecision(
                allowed=True,
                reason="no-op transition; mode unchanged",
                audit_event={
                    "type": "mode_transition",
                    "current_mode": current_mode,
                    "new_mode": new_mode,
                    "allowed": True,
                    "no_op": True,
                },
            )
        allowed = new_mode in ALLOWED_TRANSITIONS.get(current_mode, [])
        reason = "transition allowed" if allowed else f"illegal transition: {current_mode} -> {new_mode}"
        return GovernanceDecision(
            allowed=allowed,
            reason=reason,
            audit_event={"type": "mode_transition", "current_mode": current_mode, "new_mode": new_mode, "allowed": allowed},
        )

    def mutation_allowed(self, current_mode: str, target_is_canonical: bool = False) -> GovernanceDecision:
        if current_mode == "Sandbox" and target_is_canonical:
            return GovernanceDecision(False, "sandbox may not mutate canonical artifacts")
        allowed = MUTATION_RULES.get(current_mode, False)
        reason = "mutation allowed" if allowed else f"mutation denied in {current_mode}"
        return GovernanceDecision(allowed, reason)

    def _normalize_promotion_payload(self, payload: dict) -> dict:
        normalized = dict(payload)
        for legacy, canonical in LEGACY_PROMOTION_ALIASES.items():
            if canonical not in normalized and legacy in normalized:
                normalized[canonical] = normalized[legacy]
        return normalized

    def conceptual_layer_check(self, payload: dict) -> bool:
        if payload.get("runtime_requires_symbolic_interpretation", False):
            return False
        return bool(payload.get("conceptual_layer_check_confirmation", False))

    def validate_promotion(self, payload: dict) -> GovernanceDecision:
        normalized = self._normalize_promotion_payload(payload)
        missing = [field for field in PROMOTION_FIELDS if field not in normalized]
        if missing:
            return GovernanceDecision(False, f"promotion blocked; missing fields: {', '.join(missing)}")
        if not self.conceptual_layer_check(normalized):
            return GovernanceDecision(False, "promotion blocked; conceptual layer check failed")
        return GovernanceDecision(True, "promotion gate passed")

    def detect_symbolic_dependency_leakage(self, runtime_config: dict) -> GovernanceDecision:
        symbolic_keys = {
            "toki_pona_required_for_resume",
            "binary_required_for_transition_validation",
            "light_language_required_for_capability_loading",
            "harmonic_frequency_required_for_mode_legality",
        }
        leaking = [key for key in symbolic_keys if runtime_config.get(key) is True]
        if leaking:
            return GovernanceDecision(False, f"symbolic dependency leakage detected: {', '.join(leaking)}")
        return GovernanceDecision(True, "no symbolic dependency leakage detected")


@dataclass
class ContextBundle:
    bundle_id: str
    created_at: str
    active_mode: str
    structural_context: Dict[str, Any] = field(default_factory=dict)
    artifact_context: Dict[str, Any] = field(default_factory=dict)
    memory_context: Dict[str, Any] = field(default_factory=dict)
    environment_context: Dict[str, Any] = field(default_factory=dict)
    supplemental_ethereonic_context: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _run_git(args: List[str], cwd: Path) -> Optional[str]:
    try:
        proc = subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True, check=True)
        return proc.stdout.strip()
    except Exception:
        return None


class ContextBundleBuilder:
    """Builds bounded, replayable context while keeping Ethereonic content supplemental."""

    def __init__(
        self,
        output_dir: str | Path,
        ethereonic_layer_registry: Optional[Any] = None,
        canon_lineage_store: Optional[Any] = None,
    ):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.ethereonic_layer_registry = ethereonic_layer_registry
        self.canon_lineage_store = canon_lineage_store

    def _resolve_canon_lineage_head(self, fallback: Optional[str] = None) -> Optional[str]:
        if self.canon_lineage_store is not None:
            head = self.canon_lineage_store.current_head()
            if head:
                return head.get("canon_version")
        return fallback

    def attach_project_orientation_vector(
        self,
        bundle: ContextBundle,
        vector: Any,
    ) -> ContextBundle:
        coerced = _coerce_project_orientation_vector(vector)
        if coerced is None:
            return bundle
        if attach_project_orientation_to_supplemental is None:
            raise ValueError("ProjectOrientationVector attachment is unavailable in this runtime")
        payload = bundle.to_dict()
        payload["supplemental_ethereonic_context"] = attach_project_orientation_to_supplemental(
            payload.get("supplemental_ethereonic_context", {}),
            coerced,
        )
        return ContextBundle(**payload)

    def build(
        self,
        *,
        repo_path: Optional[str | Path] = None,
        active_mode: str = "Continuity",
        artifacts: Optional[List[str]] = None,
        canon_lineage_head: Optional[str] = None,
        continuation_notes: Optional[List[str]] = None,
        available_tools: Optional[List[str]] = None,
        ethereonic_context: Optional[Dict[str, Any]] = None,
        project_orientation_vector: Optional[Any] = None,
    ) -> ContextBundle:
        repo = infer_repo_root(repo_path)
        structural_context = self._collect_structural_context(repo)
        vector = _coerce_project_orientation_vector(project_orientation_vector)
        ordered_artifacts = (
            orient_artifacts(list(artifacts or []), vector)
            if vector is not None and orient_artifacts is not None
            else list(artifacts or [])
        )
        notes = list(continuation_notes or [])
        if vector is not None and orientation_resume_note is not None:
            note = orientation_resume_note(vector)
            if note and note not in notes:
                notes.append(note)

        bundle = ContextBundle(
            bundle_id=str(uuid.uuid4()),
            created_at=utc_now(),
            active_mode=active_mode,
            structural_context=structural_context,
            artifact_context={
                "active_design_docs": ordered_artifacts,
                "canon_lineage_head": self._resolve_canon_lineage_head(canon_lineage_head),
                "canon_lineage_source": "store" if self.canon_lineage_store is not None else "provided_or_none",
            },
            memory_context={"session_continuation_notes": notes},
            environment_context={
                "current_utc": utc_now(),
                "available_tools": list(available_tools or []),
                "runtime_root": str(infer_runtime_root()) if infer_runtime_root() is not None else None,
            },
            supplemental_ethereonic_context={},
        )
        if ethereonic_context:
            if self.ethereonic_layer_registry is None:
                raise ValueError("Ethereonic attachment requires EthereonicLayerRegistry; direct injection is not allowed")
            bundle = self.attach_ethereonic_context(bundle, ethereonic_context)
        if vector is not None:
            bundle = self.attach_project_orientation_vector(bundle, vector)
        self.save(bundle)
        return bundle

    def attach_ethereonic_context(
        self,
        bundle: ContextBundle,
        ethereonic_context: Optional[Dict[str, Any]] = None,
        *,
        include_artifact_ids: Optional[List[str]] = None,
    ) -> ContextBundle:
        if self.ethereonic_layer_registry is None:
            raise ValueError("Ethereonic attachment requires EthereonicLayerRegistry")
        payload = self.ethereonic_layer_registry.attach_to_context_bundle(
            bundle.to_dict(),
            include_artifact_ids=include_artifact_ids,
            extra_context=ethereonic_context or {},
        )
        return ContextBundle(**payload)

    def save(self, bundle: ContextBundle) -> Path:
        path = self.output_dir / f"{bundle.bundle_id}.json"
        with path.open("w", encoding="utf-8") as f:
            json.dump(bundle.to_dict(), f, indent=2)
        return path

    def _collect_structural_context(self, repo_path: Optional[Path]) -> Dict[str, Any]:
        if not repo_path or not repo_path.exists():
            return {"repo_available": False}
        branch = _run_git(["rev-parse", "--abbrev-ref", "HEAD"], repo_path)
        status = _run_git(["status", "--short"], repo_path)
        commits = _run_git(["log", "--oneline", "-5"], repo_path)
        return {
            "repo_available": True,
            "repo_path": str(repo_path),
            "runtime_root": str(infer_runtime_root()) if infer_runtime_root() is not None else None,
            "current_branch": branch,
            "changed_files": status.splitlines() if status else [],
            "recent_commits": commits.splitlines() if commits else [],
        }


class GovernanceLog:
    """Append-only governance recorder backed by a verifiable integrity chain."""

    def __init__(self, log_path: str | Path):
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self.integrity_chain = GovernanceIntegrityChain(self.log_path) if GovernanceIntegrityChain is not None else None

    def append(
        self,
        *,
        event_type: str,
        session_id: str,
        previous_mode: Optional[str] = None,
        new_mode: Optional[str] = None,
        allowed: Optional[bool] = None,
        reason: Optional[str] = None,
        requested_action: Optional[str] = None,
        artifact_delta: Optional[Any] = None,
        canonical_change: Optional[bool] = None,
        validation_reference: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        metadata = dict(metadata or {})
        checkpoint_path = metadata.get("checkpoint_path")
        if checkpoint_path and self.integrity_chain is not None and "checkpoint_hash" not in metadata:
            metadata["checkpoint_hash"] = self.integrity_chain.compute_checkpoint_hash(checkpoint_path)

        if self.integrity_chain is None:
            record = {
                "timestamp_utc": utc_now(),
                "event_type": event_type,
                "session_identifier": session_id,
                "previous_mode": previous_mode,
                "new_mode": new_mode,
                "allowed": allowed,
                "reason": reason,
                "requested_action": requested_action,
                "artifact_delta": artifact_delta,
                "canonical_change": canonical_change,
                "validation_reference": validation_reference,
                "metadata": metadata,
            }
            with self.log_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(record) + "\n")
            return record

        return self.integrity_chain.append_verified(
            event_type=event_type,
            session_identifier=session_id,
            previous_mode=previous_mode,
            new_mode=new_mode,
            allowed=allowed,
            reason=reason,
            requested_action=requested_action,
            artifact_delta=artifact_delta,
            canonical_change=canonical_change,
            validation_reference=validation_reference,
            metadata=metadata,
        )

    def read_all(self) -> List[dict]:
        if not self.log_path.exists():
            return []
        rows: List[dict] = []
        with self.log_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    rows.append(json.loads(line))
        return rows

    def verify_chain(self) -> Dict[str, Any]:
        if self.integrity_chain is None:
            rows = self.read_all()
            return {
                "exists": self.log_path.exists(),
                "event_count": len(rows),
                "valid": True,
                "errors": [],
                "latest_event_hash": None,
                "log_path": str(self.log_path),
            }
        return self.integrity_chain.verify_chain()

    def latest_event_hash(self) -> Optional[str]:
        if self.integrity_chain is None:
            rows = self.read_all()
            return rows[-1].get("record_hash") if rows else None
        return self.integrity_chain.latest_event_hash()

    def compute_checkpoint_hash(self, checkpoint_path: str | Path) -> Optional[str]:
        if self.integrity_chain is None:
            return None
        return self.integrity_chain.compute_checkpoint_hash(checkpoint_path)

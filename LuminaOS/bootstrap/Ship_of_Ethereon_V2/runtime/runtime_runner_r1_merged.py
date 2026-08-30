from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
import argparse
import json

try:
    from .runtime_spine_r1 import ContextBundleBuilder, GovernanceLog, ModeGuard, SessionEngine
    from .canon_lineage_store_r1 import CanonLineageStore
except Exception:
    from runtime_spine_r1 import ContextBundleBuilder, GovernanceLog, ModeGuard, SessionEngine
    from canon_lineage_store_r1 import CanonLineageStore

try:
    from .psi42_transceiver_v1_6 import Config as Psi42Config, ResonanceTransceiverV16
except Exception:
    try:
        from psi42_transceiver_v1_6 import Config as Psi42Config, ResonanceTransceiverV16
    except Exception:
        Psi42Config = None
        ResonanceTransceiverV16 = None

try:
    from .psi42_transceiver_v1_7 import Config as Psi42V17Config, ResonanceTransceiverV17
except Exception:
    try:
        from psi42_transceiver_v1_7 import Config as Psi42V17Config, ResonanceTransceiverV17
    except Exception:
        Psi42V17Config = None
        ResonanceTransceiverV17 = None

try:
    from .input_integrity_layer_r1 import InputIntegrityAssessor
except Exception:
    try:
        from input_integrity_layer_r1 import InputIntegrityAssessor
    except Exception:
        InputIntegrityAssessor = None

try:
    from .ethereonic_layer_r1 import EthereonicLayerRegistry
except Exception:
    try:
        from ethereonic_layer_r1 import EthereonicLayerRegistry
    except Exception:
        EthereonicLayerRegistry = None

try:
    from .lumina_return_host_repo_native_bridge_r1 import ContinuityRestoreStore, LuminaWorkspaceHost
except Exception:
    try:
        from lumina_return_host_repo_native_bridge_r1 import ContinuityRestoreStore, LuminaWorkspaceHost
    except Exception:
        ContinuityRestoreStore = None
        LuminaWorkspaceHost = None

try:
    from .mycelial_field_replay_r1 import MycelialFieldReplayBridge
except Exception:
    try:
        from mycelial_field_replay_r1 import MycelialFieldReplayBridge
    except Exception:
        MycelialFieldReplayBridge = None


RUNTIME_SEED_VERSION = "0.4"
DEFAULT_EXPERIMENTAL_FEATURE_FLAGS = [
    "ETHEREON_CONTINUITY_RESTORE",
    "ETHEREON_LUMINA_HOST",
]


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


RUNTIME_ROOT = _repo_root() / "LuminaOS" / "bootstrap" / "Ship_of_Ethereon_V2" / "runtime"
STATE_ROOT = _repo_root() / ".lumina_state" / "ship_of_ethereon_v2"

BASE_DIR = STATE_ROOT / "runtime_runner_r1_actiontype_logging"
REGISTRY_PATH = RUNTIME_ROOT / "capability_registry_r1.json"
DEFAULT_ARTIFACTS = [
    "runtime_spine_r1.py",
    "runtime_runner_r1_merged.py",
    "runtime_runner_return_host_bridge_r1.py",
    "project_return_repo_native_r1.py",
    "workspace_host_repo_native_r1.py",
    "lumina_return_host_repo_native_bridge_r1.py",
    "sea_trials_set_one_r1_merged.py",
    "sea_trials_lumina_return_host_r1.py",
    "capability_registry_r1.json",
    "input_integrity_layer_r1.py",
    "governance_integrity_r1.py",
    "canon_lineage_store_r1.py",
]
VALID_ACTION_TYPES = {"transition", "mutation", "promotion", "audit"}


def _deep_merge_dicts(base_payload: Dict[str, Any], overrides: Dict[str, Any]) -> Dict[str, Any]:
    merged = dict(base_payload)
    for key, value in (overrides or {}).items():
        existing = merged.get(key)
        if isinstance(existing, dict) and isinstance(value, dict):
            merged[key] = _deep_merge_dicts(existing, value)
        else:
            merged[key] = value
    return merged


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class RunnerResult:
    run_id: str
    created_at: str
    requested_mode: str
    target_mode: str
    requested_action: str
    action_type: str
    session_id: str
    context_bundle_id: str
    governance: Dict[str, Any]
    exposed_capabilities: List[Dict[str, Any]]
    checkpoint_path: str
    session_path: str
    log_path: str
    governance_log_path: str
    governance_chain_status: Dict[str, Any] = field(default_factory=dict)
    canon_lineage: Optional[Dict[str, Any]] = None
    halted: bool = False
    halt_reason: Optional[str] = None
    probe_artifacts: Optional[Dict[str, Any]] = None
    lumina_return_host_artifacts: Optional[Dict[str, Any]] = None
    mycelial_field_replay: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class CapabilityRegistry:
    """Loads the flat project registry and exposes capabilities by mode and feature flag."""

    def __init__(self, registry_path: str | Path = REGISTRY_PATH):
        self.registry_path = Path(registry_path)
        if not self.registry_path.exists():
            raise FileNotFoundError(f"Capability registry not found: {self.registry_path}")
        with self.registry_path.open("r", encoding="utf-8") as f:
            payload = json.load(f)
        self.version = payload.get("version", "unknown")
        self.capabilities = payload.get("capabilities", [])

    def exposed_for_mode(
        self,
        mode: str,
        *,
        enabled_feature_flags: Optional[List[str]] = None,
        include_categories: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        enabled = set(enabled_feature_flags or [])
        categories = set(include_categories or [])
        exposed: List[Dict[str, Any]] = []
        for capability in self.capabilities:
            if mode not in capability.get("allowed_modes", []):
                continue
            if categories and capability.get("category") not in categories:
                continue
            feature_flag = capability.get("feature_flag")
            if feature_flag and feature_flag not in enabled:
                continue
            exposed.append(capability)
        return exposed


class RuntimeRunner:
    """Tiny orchestration loop for Ethereon Runtime Spine sea-trials and day-one use."""

    def __init__(
        self,
        *,
        base_dir: str | Path = BASE_DIR,
        registry_path: str | Path = REGISTRY_PATH,
    ):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir = self.base_dir / "logs"
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.governance_log_path = self.base_dir / "governance_log_r1.jsonl"
        self.canon_lineage_path = self.base_dir / "canon_lineage_r1.jsonl"

        self.session_engine = SessionEngine(self.base_dir)
        self.mode_guard = ModeGuard(repo_root=_repo_root())
        self.registry = CapabilityRegistry(registry_path)
        self.governance_log = GovernanceLog(self.governance_log_path)
        self.input_integrity_assessor = InputIntegrityAssessor(self.base_dir / "input_integrity_ledger_r1.json") if InputIntegrityAssessor is not None else None
        self.ethereonic_layer_registry = (
            EthereonicLayerRegistry(self.base_dir / "ethereonic_layer_registry_r1.json")
            if EthereonicLayerRegistry is not None
            else None
        )
        self.canon_lineage_store = CanonLineageStore(self.canon_lineage_path)
        self.context_builder = ContextBundleBuilder(
            self.base_dir / "context_bundles",
            ethereonic_layer_registry=self.ethereonic_layer_registry,
            canon_lineage_store=self.canon_lineage_store,
        )
        self.mycelial_field_replay_base_dir = self.base_dir / "mycelial_field_replay_r1"
        self.mycelial_field_replay_bridge = None
        self._mycelial_field_replay_by_session: Dict[str, Dict[str, Any]] = {}
        self._active_session_id: Optional[str] = None

    @staticmethod
    def _safe_slug(value: str) -> str:
        slug = "".join(c if c.isalnum() or c in "-_" else "_" for c in value.strip())
        return slug or "lumina-core"

    def _resolve_enabled_feature_flags(self, enabled_feature_flags: Optional[List[str]]) -> List[str]:
        if enabled_feature_flags is None:
            return list(DEFAULT_EXPERIMENTAL_FEATURE_FLAGS)
        merged = list(enabled_feature_flags)
        for flag in DEFAULT_EXPERIMENTAL_FEATURE_FLAGS:
            if flag not in merged:
                merged.append(flag)
        return merged

    def _append_governance_event(
        self,
        *,
        event_type: str,
        session_id: str,
        previous_mode: Optional[str],
        new_mode: Optional[str],
        allowed: Optional[bool],
        reason: Optional[str],
        requested_action: str,
        action_type: str,
        validation_reference: Optional[str] = None,
        artifact_delta: Optional[Any] = None,
        canonical_change: Optional[bool] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        metadata = dict(metadata or {})
        return self.governance_log.append(
            event_type=event_type,
            session_id=session_id,
            previous_mode=previous_mode,
            new_mode=new_mode,
            allowed=allowed,
            reason=reason,
            requested_action=requested_action,
            artifact_delta=artifact_delta,
            canonical_change=canonical_change,
            validation_reference=validation_reference,
            metadata={"action_type": action_type, **metadata},
        )

    def _record_decision(
        self,
        *,
        event_type: str,
        session_id: str,
        previous_mode: Optional[str],
        new_mode: Optional[str],
        decision: Dict[str, Any],
        requested_action: str,
        action_type: str,
        artifact_delta: Optional[Any] = None,
        canonical_change: Optional[bool] = None,
    ) -> Dict[str, Any]:
        validation_reference = None
        metadata = dict(decision.get("audit_event") or {})
        if event_type == "promotion":
            validation_reference = metadata.get("validation_artifact_id")
        return self._append_governance_event(
            event_type=event_type,
            session_id=session_id,
            previous_mode=previous_mode,
            new_mode=new_mode,
            allowed=decision.get("allowed"),
            reason=decision.get("reason"),
            requested_action=requested_action,
            action_type=action_type,
            validation_reference=validation_reference,
            artifact_delta=artifact_delta,
            canonical_change=canonical_change,
            metadata=metadata,
        )

    def _current_chain_status(self) -> Dict[str, Any]:
        status = self.governance_log.verify_chain()
        status["latest_event_hash"] = self.governance_log.latest_event_hash()
        return status

    def _current_canon_metadata(self) -> Optional[Dict[str, Any]]:
        head = self.canon_lineage_store.current_head()
        verify = self.canon_lineage_store.verify_lineage()
        if head is None:
            return {"current_head": None, "record_count": verify["record_count"], "valid": verify["valid"]}
        return {
            "current_head": head.get("canon_version"),
            "record_count": verify["record_count"],
            "valid": verify["valid"],
            "last_record": head,
        }

    def assess_input_integrity(
        self,
        raw_input: str,
        *,
        context_terms: Optional[List[str]] = None,
        preferred_terms: Optional[List[str]] = None,
        is_load_bearing: bool = False,
        action_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        if self.input_integrity_assessor is None:
            raise RuntimeError("InputIntegrityAssessor is unavailable")
        return self.input_integrity_assessor.assess(
            raw_input,
            context_terms=context_terms,
            preferred_terms=preferred_terms,
            is_load_bearing=is_load_bearing,
            action_type=action_type,
        ).to_dict()

    def _write_context_bundle_payload(self, payload: Dict[str, Any]) -> None:
        path = self.context_builder.output_dir / f"{payload['bundle_id']}.json"
        with path.open("w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

    @staticmethod
    def _absent_mycelial_field_replay() -> Dict[str, Any]:
        if MycelialFieldReplayBridge is not None:
            return MycelialFieldReplayBridge.absent_result()
        return {
            "schema_version": "lumina-mycelial-field-replay-v0.1",
            "status": "absent",
            "present": False,
            "input_count": 0,
            "accepted_count": 0,
            "replay_count": 0,
            "quarantine_count": 0,
            "decisions": [],
            "context_receipts": [],
            "authority_effect": False,
            "authority_event_created": False,
        }

    def _process_mycelial_field_replay(self, receipts: Optional[List[Dict[str, Any]]]) -> Dict[str, Any]:
        if receipts is None:
            inputs: List[Any] = []
        elif isinstance(receipts, list):
            inputs = list(receipts)
        else:
            inputs = [receipts]
        if not inputs:
            return self._absent_mycelial_field_replay()
        if self.mycelial_field_replay_bridge is None:
            if MycelialFieldReplayBridge is None:
                return {
                    **self._absent_mycelial_field_replay(),
                    "status": "unavailable",
                    "present": True,
                    "input_count": len(inputs),
                    "error": "mycelial field replay bridge is unavailable; input was not attached",
                }
            self.mycelial_field_replay_bridge = MycelialFieldReplayBridge(
                self.mycelial_field_replay_base_dir
            )
        try:
            return self.mycelial_field_replay_bridge.ingest(inputs)
        except Exception as exc:
            return {
                **self._absent_mycelial_field_replay(),
                "status": "failed_closed",
                "present": True,
                "input_count": len(inputs),
                "error": f"{type(exc).__name__}: {exc}",
            }

    def _mycelial_field_replay_for_session(self, session_id: str) -> Dict[str, Any]:
        return dict(
            self._mycelial_field_replay_by_session.get(
                session_id,
                self._absent_mycelial_field_replay(),
            )
        )

    def _ethereonic_context_terms(self) -> List[str]:
        if self.ethereonic_layer_registry is None:
            return []
        snapshot = self.ethereonic_layer_registry.runtime_snapshot()
        return list(snapshot.get("active_artifact_ids", []))

    def _resolve_lumina_project_id(self, project_id: Optional[str], requested_action: str, raw_user_input: Optional[str]) -> str:
        if project_id:
            return self._safe_slug(project_id)
        if raw_user_input:
            return self._safe_slug(raw_user_input[:80])
        return self._safe_slug(requested_action)

    def _maybe_run_lumina_return_host(
        self,
        *,
        target_mode: str,
        requested_action: str,
        raw_user_input: Optional[str],
        project_id: Optional[str],
        exposed_capabilities: List[Dict[str, Any]],
        artifacts_in_scope: List[str],
    ) -> Optional[Dict[str, Any]]:
        if ContinuityRestoreStore is None:
            return None
        capability_ids = {cap.get("capability_id") for cap in exposed_capabilities}
        if "continuity_restore_store" not in capability_ids:
            return None

        resolved_project_id = self._resolve_lumina_project_id(project_id, requested_action, raw_user_input)
        run_slug = self._safe_slug(f"{resolved_project_id}_{requested_action}_{target_mode}")
        base_dir = self.base_dir / "lumina_return_host_artifacts" / (self._active_session_id or "session") / run_slug

        continuity = ContinuityRestoreStore(base_dir)
        session = continuity.create_session(
            project_id=resolved_project_id,
            mode=target_mode,
            artifacts_in_scope=list(artifacts_in_scope),
            workspace_state={"active_mode": target_mode, "requested_action": requested_action},
            continuation_notes=[f"runtime cycle: {requested_action}"],
        )
        session.pending_next_action = f"continue from {requested_action}"
        session.last_completed_action = f"runtime_cycle:{requested_action}"
        continuity.save_session(session)

        checkpoint_one = continuity.write_checkpoint(session.session_id, f"{requested_action}_{target_mode}_checkpoint_only")
        payload_one = continuity.project_return_payload(resolved_project_id)

        artifacts: Dict[str, Any] = {
            "project_id": resolved_project_id,
            "base_dir": str(base_dir),
            "capability_ids": sorted(capability_ids & {"continuity_restore_store", "lumina_workspace_host"}),
            "checkpoint_only": {
                "checkpoint_path": str(checkpoint_one),
                "payload": payload_one,
            },
        }

        if "lumina_workspace_host" not in capability_ids or LuminaWorkspaceHost is None:
            return artifacts

        host = LuminaWorkspaceHost(base_dir)
        host_session = host.create_host_session(
            project_id=resolved_project_id,
            mode=target_mode,
            active_layout_id="runtime-cycle-layout",
            focus_target=requested_action,
            artifacts_in_scope=list(artifacts_in_scope),
            linked_restore_checkpoint=str(checkpoint_one),
            continuation_notes=["workspace host remains bounded and checkpoint-linked"],
        )
        host.upsert_panel(
            host_session.host_session_id,
            panel_id="runtime-summary",
            panel_type="summary",
            title="Runtime Summary",
            zone="center",
            priority=10,
            payload={"requested_action": requested_action, "target_mode": target_mode},
        )
        host.bind_tool(
            host_session.host_session_id,
            tool_id="resolve-latest-project-return",
            label="Resolve Latest Project Return Payload",
            launch_target="project_return_repo_native_r1.py::project_return_payload",
            context_keys=["project_id"],
            pinned=True,
        )
        host.attach_reference(
            host_session.host_session_id,
            reference_id="bootstrap-readme",
            label="Bootstrap README",
            source="LuminaOS/bootstrap/Ship_of_Ethereon_V2/README.md",
            kind="runtime-reference",
        )
        host_snapshot = host.write_host_snapshot(
            host_session.host_session_id,
            last_completed_action=f"runtime_cycle:{requested_action}",
        )
        host_bundle = host.emit_host_bundle(resolved_project_id)

        checkpoint_two = continuity.write_checkpoint(session.session_id, f"{requested_action}_{target_mode}_checkpoint_plus_host")
        payload_two = continuity.project_return_payload(resolved_project_id)

        artifacts["checkpoint_plus_host"] = {
            "checkpoint_path": str(checkpoint_two),
            "payload": payload_two,
            "host_bundle": host_bundle,
            "host_snapshot_id": host_snapshot.snapshot_id,
        }
        return artifacts

    def _maybe_run_psi42_probe(
        self,
        *,
        target_mode: str,
        requested_action: str,
        ethereonic_overlay: Optional[Dict[str, Any]],
        exposed_capabilities: List[Dict[str, Any]],
    ) -> Optional[Dict[str, Any]]:
        if Psi42Config is None:
            return None
        capability_ids = {cap.get("capability_id") for cap in exposed_capabilities}
        if "psi42_transceiver_v16" not in capability_ids and "psi42_transceiver_v17" not in capability_ids and "psi42_probe_interface" not in capability_ids:
            return None
        if target_mode not in {"Observation", "Sandbox"}:
            return None
        overlay = ethereonic_overlay or {}
        anchors = overlay.get("anchor_language", ["english"])
        language_mode = "ethereonic" if any(x in anchors for x in ["toki_pona", "binary", "light_language"]) else "neutral"
        run_slug = "".join(c if c.isalnum() or c in "-_" else "_" for c in f"{requested_action}_{target_mode}")[:80]
        output_dir = self.base_dir / "psi42_artifacts" / (self._active_session_id or "session") / run_slug
        if "psi42_transceiver_v17" in capability_ids and ResonanceTransceiverV17 is not None and Psi42V17Config is not None:
            rt = ResonanceTransceiverV17(Psi42V17Config(language_mode=language_mode, output_dir=str(output_dir), probe_mode="hybrid"))
            result = rt.run(f"{requested_action} :: {target_mode}", {"OBSERVATION": 1.0 if target_mode == "Observation" else 0.0, "SANDBOX": 1.0 if target_mode == "Sandbox" else 0.0, "CONTINUITY": 0.8, "HABITAT": 0.7})
            return {
                "instrument_version": "v1.7",
                "instrument_class": result.get("instrument_class"),
                "probe_mode": result.get("probe_mode"),
                "metrics": result.get("metrics"),
                "paths": result.get("paths"),
                "topology_receipt": result.get("topology_receipt"),
                "signal_run_id": (result.get("signal_result") or {}).get("run_id"),
                "signal_pulse_id": (result.get("signal_result") or {}).get("pulse_id"),
                "authority_boundary": result.get("authority_boundary"),
            }
        elif ResonanceTransceiverV16 is not None:
            rt = ResonanceTransceiverV16(Psi42Config(language_mode=language_mode, output_dir=str(output_dir)))
        else:
            return None
        result = rt.run(f"{requested_action} :: {target_mode}", {"OBSERVATION": 1.0 if target_mode == "Observation" else 0.0, "SANDBOX": 1.0 if target_mode == "Sandbox" else 0.0, "CONTINUITY": 0.8})
        return {
            "instrument_version": "v1.6",
            "run_id": result.get("run_id"),
            "pulse_id": result.get("pulse_id"),
            "metrics": result.get("metrics"),
            "paths": result.get("paths"),
            "frame": result.get("frame"),
        }

    def _halted_result(
        self,
        *,
        session_id: str,
        current_mode: str,
        target_mode: str,
        requested_action: str,
        action_type: str,
        context_bundle_id: str,
        governance: Dict[str, Any],
        checkpoint_label: str,
        halt_reason: str,
    ) -> RunnerResult:
        checkpoint = self.session_engine.write_checkpoint(session_id, checkpoint_label)
        self._append_governance_event(
            event_type="halt",
            session_id=session_id,
            previous_mode=current_mode,
            new_mode=target_mode,
            allowed=False,
            reason=halt_reason,
            requested_action=requested_action,
            action_type=action_type,
            metadata={"checkpoint_label": checkpoint_label, "checkpoint_path": str(checkpoint)},
        )
        result = self._finalize_result(
            session_id=session_id,
            current_mode=current_mode,
            target_mode=target_mode,
            requested_action=requested_action,
            action_type=action_type,
            context_bundle_id=context_bundle_id,
            governance=governance,
            exposed_capabilities=[],
            checkpoint_path=checkpoint,
            probe_artifacts=None,
            lumina_return_host_artifacts=None,
            canon_lineage=None,
        )
        result.halted = True
        result.halt_reason = halt_reason
        return result

    def run_cycle(
        self,
        *,
        current_mode: str = "Continuity",
        target_mode: Optional[str] = None,
        requested_action: str = "sea_trial_cycle",
        action_type: str = "transition",
        artifacts: Optional[List[str]] = None,
        continuation_notes: Optional[List[str]] = None,
        available_tools: Optional[List[str]] = None,
        canon_lineage_head: Optional[str] = None,
        ethereonic_overlay: Optional[Dict[str, Any]] = None,
        enabled_feature_flags: Optional[List[str]] = None,
        target_is_canonical: bool = False,
        promotion_payload: Optional[Dict[str, Any]] = None,
        runtime_config: Optional[Dict[str, Any]] = None,
        repo_path: Optional[str | Path] = None,
        raw_user_input: Optional[str] = None,
        context_bundle_overrides: Optional[Dict[str, Any]] = None,
        project_id: Optional[str] = None,
        coupling_receipts: Optional[List[Dict[str, Any]]] = None,
    ) -> RunnerResult:
        target_mode = target_mode or current_mode
        action_type = action_type.lower().strip()
        if action_type not in VALID_ACTION_TYPES:
            raise ValueError(f"Invalid action_type '{action_type}'. Expected one of: {sorted(VALID_ACTION_TYPES)}")
        if action_type == "promotion" and promotion_payload is None:
            raise ValueError("action_type='promotion' requires promotion_payload")

        artifacts = list(artifacts or DEFAULT_ARTIFACTS)
        available_tools = list(available_tools or ["runtime_spine", "runtime_runner", "sea_trials", "capability_registry", "continuity_restore", "lumina_workspace_host"])
        continuation_notes = list(continuation_notes or [])
        enabled_feature_flags = self._resolve_enabled_feature_flags(enabled_feature_flags)
        load_bearing_action = action_type in {"transition", "mutation", "promotion"}

        session = self.session_engine.create_session(
            mode=current_mode,
            artifacts_in_scope=artifacts,
            ethereonic_overlay=ethereonic_overlay or {},
        )
        context_bundle = self.context_builder.build(
            repo_path=repo_path,
            active_mode=current_mode,
            artifacts=artifacts,
            canon_lineage_head=canon_lineage_head,
            continuation_notes=continuation_notes,
            available_tools=available_tools,
            ethereonic_context=ethereonic_overlay or None,
        )
        self.session_engine.initialize_turn(session.session_id, context_bundle_id=context_bundle.bundle_id, artifacts_in_scope=artifacts)

        mycelial_field_replay = self._process_mycelial_field_replay(coupling_receipts)
        self._mycelial_field_replay_by_session[session.session_id] = mycelial_field_replay

        governance: Dict[str, Any] = {}
        canon_lineage_result: Optional[Dict[str, Any]] = None

        self._append_governance_event(
            event_type="cycle_start",
            session_id=session.session_id,
            previous_mode=current_mode,
            new_mode=target_mode,
            allowed=True,
            reason="cycle initialized",
            requested_action=requested_action,
            action_type=action_type,
            metadata={"context_bundle_id": context_bundle.bundle_id, "enabled_feature_flags": enabled_feature_flags},
        )

        if raw_user_input is not None and not isinstance(raw_user_input, str):
            return self._halted_result(
                session_id=session.session_id,
                current_mode=current_mode,
                target_mode=target_mode,
                requested_action=requested_action,
                action_type=action_type,
                context_bundle_id=context_bundle.bundle_id,
                governance=governance,
                checkpoint_label="input_integrity_invalid_type",
                halt_reason="input integrity gate requires raw_user_input to be text",
            )

        if raw_user_input and self.input_integrity_assessor is not None:
            integrity = self.assess_input_integrity(
                raw_user_input,
                context_terms=[current_mode, target_mode, requested_action, action_type, *self._ethereonic_context_terms()],
                preferred_terms=["ethereon", "canon", "sandbox", "drydock", "observation", "continuity"],
                is_load_bearing=load_bearing_action,
                action_type=action_type,
            )
            governance["input_integrity"] = {"allowed": not integrity.get("should_halt", False), **integrity}
            self._append_governance_event(
                event_type="input_integrity",
                session_id=session.session_id,
                previous_mode=current_mode,
                new_mode=target_mode,
                allowed=not integrity.get("should_halt", False),
                reason=integrity.get("confidence_reason"),
                requested_action=requested_action,
                action_type=action_type,
                metadata={
                    "recommended_behavior": integrity.get("recommended_behavior"),
                    "raw_input": raw_user_input,
                    "chosen_interpretation": integrity.get("chosen_interpretation"),
                },
            )
            if integrity.get("should_halt"):
                return self._halted_result(
                    session_id=session.session_id,
                    current_mode=current_mode,
                    target_mode=target_mode,
                    requested_action=requested_action,
                    action_type=action_type,
                    context_bundle_id=context_bundle.bundle_id,
                    governance=governance,
                    checkpoint_label="input_integrity_confirmation_required",
                    halt_reason="input integrity gate requires confirmation before load-bearing action",
                )

        if self.ethereonic_layer_registry is not None:
            independence = self.ethereonic_layer_registry.validate_runtime_independence(runtime_config or {})
            governance["ethereonic_layer_independence"] = independence
            self._append_governance_event(
                event_type="ethereonic_layer_independence",
                session_id=session.session_id,
                previous_mode=current_mode,
                new_mode=target_mode,
                allowed=independence.get("allowed"),
                reason=independence.get("reason"),
                requested_action=requested_action,
                action_type=action_type,
                metadata={"violations": independence.get("violations", [])},
            )
            if not independence.get("allowed", True):
                return self._halted_result(
                    session_id=session.session_id,
                    current_mode=current_mode,
                    target_mode=target_mode,
                    requested_action=requested_action,
                    action_type=action_type,
                    context_bundle_id=context_bundle.bundle_id,
                    governance=governance,
                    checkpoint_label="ethereonic_independence_denied",
                    halt_reason=independence.get("reason", "ethereonic layer independence failed"),
                )

        context_bundle_payload = context_bundle.to_dict()
        if context_bundle_overrides:
            context_bundle_payload = _deep_merge_dicts(context_bundle_payload, context_bundle_overrides)
        if MycelialFieldReplayBridge is not None:
            context_bundle_payload = MycelialFieldReplayBridge.attach_to_context_bundle(
                context_bundle_payload,
                mycelial_field_replay,
            )

        if self.ethereonic_layer_registry is not None:
            attachment = self.ethereonic_layer_registry.validate_context_attachment(context_bundle_payload)
            governance["ethereonic_attachment"] = attachment
            self._append_governance_event(
                event_type="ethereonic_attachment",
                session_id=session.session_id,
                previous_mode=current_mode,
                new_mode=target_mode,
                allowed=attachment.get("allowed"),
                reason=attachment.get("reason"),
                requested_action=requested_action,
                action_type=action_type,
                metadata={"embedded_locations": attachment.get("embedded_locations", [])},
            )
            if not attachment.get("allowed", True):
                return self._halted_result(
                    session_id=session.session_id,
                    current_mode=current_mode,
                    target_mode=target_mode,
                    requested_action=requested_action,
                    action_type=action_type,
                    context_bundle_id=context_bundle.bundle_id,
                    governance=governance,
                    checkpoint_label="ethereonic_attachment_denied",
                    halt_reason=attachment.get("reason", "ethereonic attachment boundary violated"),
                )
        self._write_context_bundle_payload(context_bundle_payload)

        if current_mode != target_mode:
            transition = asdict(self.mode_guard.validate_transition(current_mode, target_mode))
            governance["transition"] = transition
            self._record_decision(
                event_type="transition",
                session_id=session.session_id,
                previous_mode=current_mode,
                new_mode=target_mode,
                decision=transition,
                requested_action=requested_action,
                action_type=action_type,
            )
            if not transition["allowed"]:
                loaded = self.session_engine.load_session(session.session_id)
                loaded.continuity_state.unauthorized_transition_attempts += 1
                self.session_engine.save_session(loaded)
                return self._halted_result(
                    session_id=session.session_id,
                    current_mode=current_mode,
                    target_mode=target_mode,
                    requested_action=requested_action,
                    action_type=action_type,
                    context_bundle_id=context_bundle.bundle_id,
                    governance=governance,
                    checkpoint_label="transition_denied",
                    halt_reason=transition["reason"],
                )
            self.session_engine.change_mode(session.session_id, target_mode)

        mutation_subject_mode = current_mode if action_type == "promotion" else target_mode
        mutation = asdict(self.mode_guard.mutation_allowed(mutation_subject_mode, target_is_canonical=target_is_canonical))
        governance["mutation"] = mutation
        self._record_decision(
            event_type="mutation",
            session_id=session.session_id,
            previous_mode=mutation_subject_mode,
            new_mode=target_mode,
            decision=mutation,
            requested_action=requested_action,
            action_type=action_type,
            canonical_change=target_is_canonical,
        )
        if action_type in {"mutation", "promotion"} and not mutation["allowed"]:
            return self._halted_result(
                session_id=session.session_id,
                current_mode=current_mode,
                target_mode=target_mode,
                requested_action=requested_action,
                action_type=action_type,
                context_bundle_id=context_bundle.bundle_id,
                governance=governance,
                checkpoint_label="mutation_denied",
                halt_reason=mutation["reason"],
            )

        if runtime_config is not None:
            symbolic = asdict(self.mode_guard.detect_symbolic_dependency_leakage(runtime_config))
            governance["symbolic_dependency"] = symbolic
            self._record_decision(
                event_type="symbolic_dependency",
                session_id=session.session_id,
                previous_mode=target_mode,
                new_mode=target_mode,
                decision=symbolic,
                requested_action=requested_action,
                action_type=action_type,
            )
            if not symbolic["allowed"]:
                return self._halted_result(
                    session_id=session.session_id,
                    current_mode=current_mode,
                    target_mode=target_mode,
                    requested_action=requested_action,
                    action_type=action_type,
                    context_bundle_id=context_bundle.bundle_id,
                    governance=governance,
                    checkpoint_label="symbolic_dependency_denied",
                    halt_reason=symbolic["reason"],
                )

        promotion_record: Optional[Dict[str, Any]] = None
        if action_type == "promotion":
            promotion = asdict(self.mode_guard.validate_promotion(promotion_payload or {}))
            governance["promotion"] = promotion
            promotion_record = self._record_decision(
                event_type="promotion",
                session_id=session.session_id,
                previous_mode=current_mode,
                new_mode=target_mode,
                decision=promotion,
                requested_action=requested_action,
                action_type=action_type,
                canonical_change=(target_mode == "Canon"),
            )
            if not promotion["allowed"]:
                return self._halted_result(
                    session_id=session.session_id,
                    current_mode=current_mode,
                    target_mode=target_mode,
                    requested_action=requested_action,
                    action_type=action_type,
                    context_bundle_id=context_bundle.bundle_id,
                    governance=governance,
                    checkpoint_label="promotion_denied",
                    halt_reason=promotion["reason"],
                )

        exposed = self.registry.exposed_for_mode(target_mode, enabled_feature_flags=enabled_feature_flags)
        governance["capability_exposure"] = {
            "allowed": True,
            "enabled_feature_flags": enabled_feature_flags,
            "capability_ids": [cap.get("capability_id") for cap in exposed],
        }
        self._append_governance_event(
            event_type="capability_exposure",
            session_id=session.session_id,
            previous_mode=target_mode,
            new_mode=target_mode,
            allowed=True,
            reason=f"exposed {len(exposed)} capabilities",
            requested_action=requested_action,
            action_type=action_type,
            metadata={"capability_ids": [cap.get("capability_id") for cap in exposed], "enabled_feature_flags": enabled_feature_flags},
        )

        self._active_session_id = session.session_id
        lumina_return_host_artifacts = self._maybe_run_lumina_return_host(
            target_mode=target_mode,
            requested_action=requested_action,
            raw_user_input=raw_user_input,
            project_id=project_id,
            exposed_capabilities=exposed,
            artifacts_in_scope=artifacts,
        )
        probe_artifacts = self._maybe_run_psi42_probe(
            target_mode=target_mode,
            requested_action=requested_action,
            ethereonic_overlay=ethereonic_overlay,
            exposed_capabilities=exposed,
        )
        self._active_session_id = None

        if lumina_return_host_artifacts is not None:
            self._append_governance_event(
                event_type="lumina_return_host_execution",
                session_id=session.session_id,
                previous_mode=target_mode,
                new_mode=target_mode,
                allowed=True,
                reason="executed lawful Lumina return/host handshake",
                requested_action=requested_action,
                action_type=action_type,
                metadata={
                    "project_id": lumina_return_host_artifacts.get("project_id"),
                    "capability_ids": lumina_return_host_artifacts.get("capability_ids", []),
                    "has_checkpoint_plus_host": "checkpoint_plus_host" in lumina_return_host_artifacts,
                },
            )

        if probe_artifacts is not None:
            self._append_governance_event(
                event_type="probe_execution",
                session_id=session.session_id,
                previous_mode=target_mode,
                new_mode=target_mode,
                allowed=True,
                reason="executed lawful Ψ-42 probe",
                requested_action=requested_action,
                action_type=action_type,
                metadata={
                    "probe_run_id": probe_artifacts.get("run_id"),
                    "pulse_id": probe_artifacts.get("pulse_id"),
                },
            )

        if action_type == "promotion" and target_mode == "Canon":
            if promotion_record is None:
                return self._halted_result(
                    session_id=session.session_id,
                    current_mode=current_mode,
                    target_mode=target_mode,
                    requested_action=requested_action,
                    action_type=action_type,
                    context_bundle_id=context_bundle.bundle_id,
                    governance=governance,
                    checkpoint_label="promotion_record_missing",
                    halt_reason="promotion lineage commit requires a promotion governance record",
                )
            canon_lineage_result = self.canon_lineage_store.promote(
                canon_commit_summary=(promotion_payload or {}).get("change_summary", requested_action),
                validation_artifact_reference=(promotion_payload or {}).get("validation_artifact_id", "unknown"),
                governance_event_hash=promotion_record.get("record_hash", ""),
                promotion_payload=dict(promotion_payload or {}),
                runtime_seed_version=RUNTIME_SEED_VERSION,
                notes="Promoted through guarded runtime path.",
            )
            governance["canon_lineage"] = canon_lineage_result
            self._append_governance_event(
                event_type="canon_lineage_commit",
                session_id=session.session_id,
                previous_mode=target_mode,
                new_mode=target_mode,
                allowed=True,
                reason=f"canon lineage committed as {canon_lineage_result['canon_version']}",
                requested_action=requested_action,
                action_type=action_type,
                validation_reference=canon_lineage_result["validation_artifact_reference"],
                canonical_change=True,
                metadata={
                    "canon_version": canon_lineage_result["canon_version"],
                    "canon_parent": canon_lineage_result["canon_parent"],
                    "lineage_record_hash": canon_lineage_result["lineage_record_hash"],
                },
            )

        checkpoint = self.session_engine.write_checkpoint(session.session_id, f"{requested_action}_{target_mode}")
        self._append_governance_event(
            event_type="checkpoint",
            session_id=session.session_id,
            previous_mode=target_mode,
            new_mode=target_mode,
            allowed=True,
            reason="checkpoint written",
            requested_action=requested_action,
            action_type=action_type,
            metadata={"checkpoint_path": str(checkpoint)},
        )

        return self._finalize_result(
            session_id=session.session_id,
            current_mode=current_mode,
            target_mode=target_mode,
            requested_action=requested_action,
            action_type=action_type,
            context_bundle_id=context_bundle.bundle_id,
            governance=governance,
            exposed_capabilities=exposed,
            checkpoint_path=checkpoint,
            probe_artifacts=probe_artifacts,
            lumina_return_host_artifacts=lumina_return_host_artifacts,
            canon_lineage=canon_lineage_result,
        )

    def _finalize_result(
        self,
        *,
        session_id: str,
        current_mode: str,
        target_mode: str,
        requested_action: str,
        action_type: str,
        context_bundle_id: str,
        governance: Dict[str, Any],
        exposed_capabilities: List[Dict[str, Any]],
        checkpoint_path: str | Path,
        probe_artifacts: Optional[Dict[str, Any]],
        lumina_return_host_artifacts: Optional[Dict[str, Any]],
        canon_lineage: Optional[Dict[str, Any]],
    ) -> RunnerResult:
        session_path = self.session_engine.session_path(session_id)
        result = RunnerResult(
            run_id=f"run-{session_id[:12]}",
            created_at=utc_now(),
            requested_mode=current_mode,
            target_mode=target_mode,
            requested_action=requested_action,
            action_type=action_type,
            session_id=session_id,
            context_bundle_id=context_bundle_id,
            governance=governance,
            exposed_capabilities=exposed_capabilities,
            checkpoint_path=str(checkpoint_path),
            session_path=str(session_path),
            log_path="",
            governance_log_path=str(self.governance_log_path),
            governance_chain_status=self._current_chain_status(),
            canon_lineage=canon_lineage or self._current_canon_metadata(),
            probe_artifacts=probe_artifacts,
            lumina_return_host_artifacts=lumina_return_host_artifacts,
            mycelial_field_replay=self._mycelial_field_replay_for_session(session_id),
        )
        log_path = self.logs_dir / f"{result.run_id}.json"
        payload = result.to_dict()
        payload["log_path"] = str(log_path)
        with log_path.open("w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
        result.log_path = str(log_path)
        return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run one tiny Ethereon runtime cycle.")
    parser.add_argument("--current-mode", default="Continuity")
    parser.add_argument("--target-mode", default=None)
    parser.add_argument("--action", default="sea_trial_cycle")
    parser.add_argument("--action-type", default="transition", choices=sorted(VALID_ACTION_TYPES))
    parser.add_argument("--target-is-canonical", action="store_true")
    parser.add_argument("--repo-path", default=None)
    parser.add_argument("--project-id", default=None)
    parser.add_argument("--enable-flag", action="append", dest="feature_flags", default=[])
    parser.add_argument("--artifact", action="append", dest="artifacts", default=[])
    parser.add_argument("--note", action="append", dest="notes", default=[])
    parser.add_argument("--lineage", default=None)
    parser.add_argument("--overlay-json", default=None, help="JSON object for Ethereonic overlay")
    parser.add_argument("--runtime-config-json", default=None, help="JSON object for symbolic dependency leakage checks")
    parser.add_argument("--promotion-json", default=None, help="JSON object for promotion validation")
    parser.add_argument("--raw-user-input", default=None, help="Raw user phrasing to assess before load-bearing action")
    parser.add_argument("--context-overrides-json", default=None, help="JSON object merged into context bundle before boundary checks")
    parser.add_argument(
        "--coupling-receipt-json",
        action="append",
        dest="coupling_receipt_json",
        default=[],
        help="Repeatable non-governing coupling receipt JSON object for diagnostic intake.",
    )
    return parser.parse_args()


def _maybe_json(text: Optional[str]) -> Optional[Dict[str, Any]]:
    if not text:
        return None
    return json.loads(text)


def _json_objects(values: List[str]) -> List[Dict[str, Any]]:
    payloads: List[Dict[str, Any]] = []
    for value in values:
        payload = json.loads(value)
        if not isinstance(payload, dict):
            raise ValueError("--coupling-receipt-json requires a JSON object")
        payloads.append(payload)
    return payloads


if __name__ == "__main__":
    args = parse_args()
    runner = RuntimeRunner()
    result = runner.run_cycle(
        current_mode=args.current_mode,
        target_mode=args.target_mode,
        requested_action=args.action,
        action_type=args.action_type,
        artifacts=args.artifacts or None,
        continuation_notes=args.notes or None,
        canon_lineage_head=args.lineage,
        ethereonic_overlay=_maybe_json(args.overlay_json),
        enabled_feature_flags=args.feature_flags or None,
        target_is_canonical=args.target_is_canonical,
        promotion_payload=_maybe_json(args.promotion_json),
        runtime_config=_maybe_json(args.runtime_config_json),
        repo_path=args.repo_path,
        raw_user_input=args.raw_user_input,
        context_bundle_overrides=_maybe_json(args.context_overrides_json),
        project_id=args.project_id,
        coupling_receipts=_json_objects(args.coupling_receipt_json) or None,
    )
    print(json.dumps(result.to_dict(), indent=2))

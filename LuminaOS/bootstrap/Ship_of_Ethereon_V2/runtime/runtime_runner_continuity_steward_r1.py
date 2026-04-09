from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional
import argparse
import json

from runtime_runner_r1_merged import BASE_DIR, REGISTRY_PATH, RuntimeRunner
from continuity_steward_r1 import ContinuitySteward


DEFAULT_STEWARD_REGISTRY_PATH = Path(__file__).with_name("capability_registry_continuity_steward_r1.json")


class StewardedRuntimeRunner(RuntimeRunner):
    """Preferred entry point when the continuity steward should be active in a lawful, bounded way."""

    def __init__(self, *, base_dir: str | Path = BASE_DIR, registry_path: Optional[str | Path] = None):
        chosen_registry = Path(registry_path) if registry_path else (
            DEFAULT_STEWARD_REGISTRY_PATH if DEFAULT_STEWARD_REGISTRY_PATH.exists() else REGISTRY_PATH
        )
        super().__init__(base_dir=base_dir, registry_path=chosen_registry)
        self.continuity_steward = ContinuitySteward(self.base_dir / "continuity_steward")

    def run_cycle(self, **kwargs: Any) -> Dict[str, Any]:
        result = super().run_cycle(**kwargs)
        payload = result.to_dict()

        residue_entry = self.continuity_steward.ingest_runner_result(payload)
        session_state = self.session_engine.load_session(result.session_id).to_dict()
        steward_decision = self.continuity_steward.evaluate(session_state)

        self._append_governance_event(
            event_type="continuity_steward",
            session_id=result.session_id,
            previous_mode=result.target_mode,
            new_mode=steward_decision.get("lawful_target_mode"),
            allowed=True,
            reason=steward_decision.get("reason"),
            requested_action=result.requested_action,
            action_type=result.action_type,
            metadata={
                "steward_should_wake": steward_decision.get("should_wake"),
                "steward_should_sleep": steward_decision.get("should_sleep"),
                "residue_path": str(self.continuity_steward.residue_path),
                "state_path": str(self.continuity_steward.state_path),
            },
        )

        payload["continuity_steward"] = {
            "residue_entry": residue_entry,
            "decision": steward_decision,
            "residue_path": str(self.continuity_steward.residue_path),
            "state_path": str(self.continuity_steward.state_path),
            "resume_brief": self.continuity_steward.build_resume_brief(session_id=result.session_id),
        }
        payload["governance_chain_status"] = self._current_chain_status()

        log_path = Path(result.log_path)
        with log_path.open("w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
        return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run one stewarded Ethereon runtime cycle.")
    parser.add_argument("--current-mode", default="Continuity")
    parser.add_argument("--target-mode", default=None)
    parser.add_argument("--action", default="stewarded_cycle")
    parser.add_argument("--action-type", default="audit")
    parser.add_argument("--target-is-canonical", action="store_true")
    parser.add_argument("--repo-path", default=None)
    parser.add_argument("--registry-path", default=None)
    parser.add_argument("--enable-flag", action="append", dest="feature_flags", default=[])
    parser.add_argument("--artifact", action="append", dest="artifacts", default=[])
    parser.add_argument("--note", action="append", dest="notes", default=[])
    parser.add_argument("--lineage", default=None)
    parser.add_argument("--overlay-json", default=None)
    parser.add_argument("--runtime-config-json", default=None)
    parser.add_argument("--promotion-json", default=None)
    parser.add_argument("--raw-user-input", default=None)
    parser.add_argument("--context-overrides-json", default=None)
    return parser.parse_args()


def _maybe_json(text: Optional[str]) -> Optional[Dict[str, Any]]:
    if not text:
        return None
    return json.loads(text)


if __name__ == "__main__":
    args = parse_args()
    runner = StewardedRuntimeRunner(registry_path=args.registry_path)
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
    )
    print(json.dumps(result, indent=2))

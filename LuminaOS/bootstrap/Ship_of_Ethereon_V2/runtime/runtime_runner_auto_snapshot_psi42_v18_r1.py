from __future__ import annotations

"""Auto-snapshot runner shim routed through the Psi-42 v1.8 adapter."""

from typing import Any, Dict, Optional
import argparse
import json

try:
    from .runtime_runner_psi42_v18_adapter_r1 import RuntimeRunner, VALID_ACTION_TYPES
    from .runtime_ui_snapshot_emitter_r1 import build_ui_snapshot, snapshot_write_plan, write_snapshot
    from .runtime_truth_public_snapshot_r1 import build_public_runtime_truth_snapshot
except Exception:
    from runtime_runner_psi42_v18_adapter_r1 import RuntimeRunner, VALID_ACTION_TYPES
    from runtime_ui_snapshot_emitter_r1 import build_ui_snapshot, snapshot_write_plan, write_snapshot
    from runtime_truth_public_snapshot_r1 import build_public_runtime_truth_snapshot


class AutoSnapshotRuntimeRunner(RuntimeRunner):
    """RuntimeRunner v1.8 wrapper that emits a Chamber-readable UI receipt.

    The snapshot is display-only. It does not grant Chamber authority to execute
    tools, alter governance, mutate canon, expose capabilities, or change mode
    legality. Public evidence is refreshed only when the semantic observation
    changes; local state may still receive every completed cycle.
    """

    def run_cycle(self, *args: Any, emit_public_snapshot: bool = True, emit_state_snapshot: bool = True, **kwargs: Any):
        result = super().run_cycle(*args, **kwargs)
        payload = result.to_dict()
        snapshot = build_ui_snapshot(payload)
        plan = snapshot_write_plan(
            snapshot,
            emit_public_snapshot=emit_public_snapshot,
            emit_state_snapshot=emit_state_snapshot,
        )
        write_snapshot(snapshot, plan["paths"])

        runtime_truth_emitted = False
        runtime_truth_error = None
        if plan["public_snapshot_changed"]:
            try:
                build_public_runtime_truth_snapshot()
                runtime_truth_emitted = True
            except Exception as exc:
                runtime_truth_error = str(exc)

        payload["public_snapshot_changed"] = plan["public_snapshot_changed"]
        payload["runtime_truth_snapshot_emitted"] = runtime_truth_emitted
        payload["runtime_truth_snapshot_error"] = runtime_truth_error
        return result


def _maybe_json(text: Optional[str]) -> Optional[Dict[str, Any]]:
    if not text:
        return None
    return json.loads(text)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run one Lumina runtime cycle through Psi-42 v1.8 and emit the Chamber UI snapshot.")
    parser.add_argument("--current-mode", default="Continuity")
    parser.add_argument("--target-mode", default="Observation")
    parser.add_argument("--action", default="chamber_observation_cycle")
    parser.add_argument("--action-type", default="audit", choices=sorted(VALID_ACTION_TYPES))
    parser.add_argument("--target-is-canonical", action="store_true")
    parser.add_argument("--repo-path", default=None)
    parser.add_argument("--enable-flag", action="append", dest="feature_flags", default=[])
    parser.add_argument("--artifact", action="append", dest="artifacts", default=[])
    parser.add_argument("--note", action="append", dest="notes", default=[])
    parser.add_argument("--lineage", default=None)
    parser.add_argument("--overlay-json", default=None)
    parser.add_argument("--runtime-config-json", default=None)
    parser.add_argument("--promotion-json", default=None)
    parser.add_argument("--raw-user-input", default=None)
    parser.add_argument("--project-id", default=None)
    parser.add_argument("--context-overrides-json", default=None)
    parser.add_argument("--no-public-snapshot", action="store_true")
    parser.add_argument("--no-state-snapshot", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    runner = AutoSnapshotRuntimeRunner()
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
        emit_public_snapshot=not args.no_public_snapshot,
        emit_state_snapshot=not args.no_state_snapshot,
    )
    print(json.dumps(result.to_dict(), indent=2))

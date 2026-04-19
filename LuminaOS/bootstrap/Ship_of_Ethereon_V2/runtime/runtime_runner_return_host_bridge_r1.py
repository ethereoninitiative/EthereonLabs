import argparse
import json

try:
    from . import runtime_runner_r1_merged as runner_mod
    from .lumina_return_host_repo_native_bridge_r1 import ContinuityRestoreStore, LuminaWorkspaceHost
except Exception:
    import runtime_runner_r1_merged as runner_mod
    from lumina_return_host_repo_native_bridge_r1 import ContinuityRestoreStore, LuminaWorkspaceHost


runner_mod.ContinuityRestoreStore = ContinuityRestoreStore
runner_mod.LuminaWorkspaceHost = LuminaWorkspaceHost


class ReturnHostBridgedRuntimeRunner(runner_mod.RuntimeRunner):
    """Preferred repo-native runner when Lumina return/host behavior should use the bootstrap-local bridge layer."""

    pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run one tiny Ethereon runtime cycle with repo-native return/host bridging.")
    parser.add_argument("--current-mode", default="Continuity")
    parser.add_argument("--target-mode", default=None)
    parser.add_argument("--action", default="sea_trial_cycle")
    parser.add_argument("--action-type", default="transition", choices=sorted(runner_mod.VALID_ACTION_TYPES))
    parser.add_argument("--target-is-canonical", action="store_true")
    parser.add_argument("--repo-path", default=None)
    parser.add_argument("--project-id", default=None)
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


def _maybe_json(text):
    if not text:
        return None
    return json.loads(text)


if __name__ == "__main__":
    args = parse_args()
    runner = ReturnHostBridgedRuntimeRunner()
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
    )
    print(json.dumps(result.to_dict(), indent=2))

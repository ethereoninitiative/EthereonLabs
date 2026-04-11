from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional
import argparse
import json

try:
    from .runtime_runner_r1_merged import RuntimeRunner, VALID_ACTION_TYPES
except Exception:
    from runtime_runner_r1_merged import RuntimeRunner, VALID_ACTION_TYPES


class OrientationAwareRuntimeRunner(RuntimeRunner):
    """Small adapter that injects ProjectOrientationVector into context bundle construction."""

    def run_cycle(
        self,
        *,
        project_orientation_vector: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ):
        original_build = self.context_builder.build

        def build_with_orientation(*args: Any, **inner_kwargs: Any):
            if project_orientation_vector is not None:
                inner_kwargs.setdefault("project_orientation_vector", project_orientation_vector)
            return original_build(*args, **inner_kwargs)

        self.context_builder.build = build_with_orientation
        try:
            return super().run_cycle(**kwargs)
        finally:
            self.context_builder.build = original_build

    def context_bundle_path(self, context_bundle_id: str) -> Path:
        return self.context_builder.output_dir / f"{context_bundle_id}.json"

    def read_context_bundle(self, context_bundle_id: str) -> Dict[str, Any]:
        path = self.context_bundle_path(context_bundle_id)
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run one tiny Ethereon runtime cycle with ProjectOrientationVector support.")
    parser.add_argument("--current-mode", default="Continuity")
    parser.add_argument("--target-mode", default=None)
    parser.add_argument("--action", default="sea_trial_cycle")
    parser.add_argument("--action-type", default="transition", choices=sorted(VALID_ACTION_TYPES))
    parser.add_argument("--target-is-canonical", action="store_true")
    parser.add_argument("--repo-path", default=None)
    parser.add_argument("--enable-flag", action="append", dest="feature_flags", default=[])
    parser.add_argument("--artifact", action="append", dest="artifacts", default=[])
    parser.add_argument("--note", action="append", dest="notes", default=[])
    parser.add_argument("--lineage", default=None)
    parser.add_argument("--overlay-json", default=None, help="JSON object for Ethereonic overlay")
    parser.add_argument("--orientation-json", default=None, help="JSON object for ProjectOrientationVector")
    parser.add_argument("--runtime-config-json", default=None, help="JSON object for symbolic dependency leakage checks")
    parser.add_argument("--promotion-json", default=None, help="JSON object for promotion validation")
    parser.add_argument("--raw-user-input", default=None, help="Raw user phrasing to assess before load-bearing action")
    parser.add_argument("--context-overrides-json", default=None, help="JSON object merged into context bundle before boundary checks")
    return parser.parse_args()


def _maybe_json(text: Optional[str]) -> Optional[Dict[str, Any]]:
    if not text:
        return None
    return json.loads(text)


if __name__ == "__main__":
    args = parse_args()
    runner = OrientationAwareRuntimeRunner()
    result = runner.run_cycle(
        current_mode=args.current_mode,
        target_mode=args.target_mode,
        requested_action=args.action,
        action_type=args.action_type,
        artifacts=args.artifacts or None,
        continuation_notes=args.notes or None,
        canon_lineage_head=args.lineage,
        ethereonic_overlay=_maybe_json(args.overlay_json),
        project_orientation_vector=_maybe_json(args.orientation_json),
        enabled_feature_flags=args.feature_flags or None,
        target_is_canonical=args.target_is_canonical,
        promotion_payload=_maybe_json(args.promotion_json),
        runtime_config=_maybe_json(args.runtime_config_json),
        repo_path=args.repo_path,
        raw_user_input=args.raw_user_input,
        context_bundle_overrides=_maybe_json(args.context_overrides_json),
    )
    print(json.dumps(result.to_dict(), indent=2))

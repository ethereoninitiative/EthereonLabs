from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional
import argparse
import importlib
import json

from runtime_runner_continuity_steward_r1 import StewardedRuntimeRunner as StewardedRuntimeRunnerR1


class StewardedRuntimeRunner(StewardedRuntimeRunnerR1):
    """Stewarded runner with explicit governance-integrity observability."""

    def _inspect_governance_integrity(self, log_path: str | Path) -> Dict[str, Any]:
        path = Path(log_path)
        rows: List[Dict[str, Any]] = []
        if path.exists():
            with path.open("r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        rows.append(json.loads(line))

        latest_record_hash = rows[-1].get("record_hash") if rows else None
        hashed_rows = sum(1 for row in rows if row.get("record_hash"))
        missing_hash_rows = sum(1 for row in rows if not row.get("record_hash"))

        import_error = None
        module_importable = True
        try:
            importlib.import_module("governance_integrity_r1")
        except Exception as exc:
            module_importable = False
            import_error = f"{type(exc).__name__}: {exc}"

        integrity_chain_active = bool(latest_record_hash)
        integrity_mode = "verified_chain" if integrity_chain_active else "plain_append_only"

        return {
            "integrity_mode": integrity_mode,
            "integrity_chain_active": integrity_chain_active,
            "integrity_chain_import_error": import_error,
            "integrity_module_importable": module_importable,
            "latest_event_hash": latest_record_hash,
            "hashed_row_count": hashed_rows,
            "missing_hash_row_count": missing_hash_rows,
            "event_count": len(rows),
            "log_path": str(path),
        }

    def run_cycle(self, **kwargs: Any) -> Dict[str, Any]:
        payload = super().run_cycle(**kwargs)
        integrity_status = self._inspect_governance_integrity(payload.get("governance_log_path", ""))

        governance_chain_status = dict(payload.get("governance_chain_status", {}))
        governance_chain_status.update(integrity_status)
        payload["governance_chain_status"] = governance_chain_status

        log_path = Path(payload["log_path"])
        with log_path.open("w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
        return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run one stewarded Ethereon runtime cycle with explicit integrity observability.")
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

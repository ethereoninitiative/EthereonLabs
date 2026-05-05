from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable, Optional
import argparse
import json


def _repo_root() -> Path:
    path = Path(__file__).resolve()
    for parent in [path.parent, *path.parents]:
        if (parent / ".git").exists() or (parent / "chamber.html").exists():
            return parent
    return path.parents[4]


REPO_ROOT = _repo_root()
PUBLIC_SNAPSHOT_PATH = REPO_ROOT / "public" / "runtime" / "latest_cycle.json"
STATE_SNAPSHOT_PATH = REPO_ROOT / ".lumina_state" / "ship_of_ethereon_v2" / "runtime_outputs" / "latest_cycle.json"


def _read_json(path: str | Path) -> Dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as f:
        return json.load(f)


def _allowed(governance: Dict[str, Any], key: str) -> Optional[bool]:
    value = governance.get(key)
    if isinstance(value, dict):
        allowed = value.get("allowed")
        return allowed if isinstance(allowed, bool) else None
    return None


def _probe_metric(probe: Optional[Dict[str, Any]], *names: str) -> Optional[float]:
    if not isinstance(probe, dict):
        return None
    metrics = probe.get("metrics") or {}
    for name in names:
        value = metrics.get(name)
        if isinstance(value, (int, float)):
            return float(value)
    return None


def build_ui_snapshot(result: Dict[str, Any]) -> Dict[str, Any]:
    governance = result.get("governance") or {}
    chain = result.get("governance_chain_status") or {}
    canon = result.get("canon_lineage") or {}
    probe = result.get("probe_artifacts")
    capabilities = [
        capability.get("capability_id")
        for capability in result.get("exposed_capabilities", [])
        if isinstance(capability, dict) and capability.get("capability_id")
    ]

    halted = bool(result.get("halted", False))
    return {
        "schema_version": "lumina-runtime-ui-cycle-v0.1",
        "timestamp": result.get("created_at"),
        "run_id": result.get("run_id"),
        "requested_action": result.get("requested_action"),
        "action_type": result.get("action_type"),
        "mode": {
            "requested": result.get("requested_mode"),
            "current": result.get("target_mode"),
        },
        "status": {
            "halted": halted,
            "reason": result.get("halt_reason"),
            "label": "Halted" if halted else "Stable",
        },
        "governance": {
            "transition": _allowed(governance, "transition"),
            "mutation": _allowed(governance, "mutation"),
            "promotion": _allowed(governance, "promotion"),
            "symbolic_dependency": _allowed(governance, "symbolic_dependency"),
            "ethereonic_attachment": _allowed(governance, "ethereonic_attachment"),
            "chain_valid": chain.get("valid"),
        },
        "canon": {
            "current_head": canon.get("current_head") or canon.get("canon_version"),
            "valid": canon.get("valid"),
            "record_count": canon.get("record_count"),
        },
        "capabilities": capabilities,
        "probe": {
            "active": probe is not None,
            "coherence": _probe_metric(probe, "coherence", "coherence_score"),
            "presence": _probe_metric(probe, "presence"),
            "lock": _probe_metric(probe, "alignment_strength", "lock"),
        },
        "authority_boundary": "Display receipt only; does not authorize action, alter governance, mutate canon, change mode legality, expose capabilities, or execute tools.",
    }


def write_snapshot(snapshot: Dict[str, Any], paths: Iterable[str | Path]) -> None:
    for path in paths:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("w", encoding="utf-8") as f:
            json.dump(snapshot, f, indent=2)
            f.write("\n")


def emit_from_result_file(result_path: str | Path, *, public: bool = True, state: bool = True) -> Dict[str, Any]:
    result = _read_json(result_path)
    snapshot = build_ui_snapshot(result)
    paths = []
    if public:
        paths.append(PUBLIC_SNAPSHOT_PATH)
    if state:
        paths.append(STATE_SNAPSHOT_PATH)
    write_snapshot(snapshot, paths)
    return {"snapshot": snapshot, "paths": [str(path) for path in paths]}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Emit a Chamber-readable Lumina runtime UI snapshot from a runner result JSON file.")
    parser.add_argument("result_json", help="Path to a RuntimeRunner result JSON file")
    parser.add_argument("--no-public", action="store_true", help="Do not write public/runtime/latest_cycle.json")
    parser.add_argument("--no-state", action="store_true", help="Do not write .lumina_state runtime_outputs/latest_cycle.json")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    emitted = emit_from_result_file(args.result_json, public=not args.no_public, state=not args.no_state)
    print(json.dumps(emitted, indent=2))

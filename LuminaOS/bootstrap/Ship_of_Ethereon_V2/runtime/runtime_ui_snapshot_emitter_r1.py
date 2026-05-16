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
PUBLIC_RUNTIME_DIR = REPO_ROOT / "public" / "runtime"
PUBLIC_SNAPSHOT_PATH = PUBLIC_RUNTIME_DIR / "latest_cycle.json"
PUBLIC_HISTORY_DIR = PUBLIC_RUNTIME_DIR / "history"
PUBLIC_HISTORY_INDEX = PUBLIC_HISTORY_DIR / "index.json"
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
    if not isinstance(metrics, dict):
        return None
    for name in names:
        value = metrics.get(name)
        if isinstance(value, (int, float)):
            return float(value)
    return None


def _probe_metrics(probe: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if not isinstance(probe, dict):
        return {}
    metrics = probe.get("metrics") or {}
    return metrics if isinstance(metrics, dict) else {}


def _probe_run_id(probe: Optional[Dict[str, Any]]) -> Optional[str]:
    if not isinstance(probe, dict):
        return None
    signal = probe.get("signal_result") if isinstance(probe.get("signal_result"), dict) else {}
    return probe.get("run_id") or probe.get("signal_run_id") or signal.get("run_id")


def _probe_pulse_id(probe: Optional[Dict[str, Any]]) -> Optional[str]:
    if not isinstance(probe, dict):
        return None
    signal = probe.get("signal_result") if isinstance(probe.get("signal_result"), dict) else {}
    return probe.get("pulse_id") or probe.get("signal_pulse_id") or signal.get("pulse_id")


def _topology_metrics(probe: Optional[Dict[str, Any]]) -> Dict[str, Optional[float]]:
    metrics = _probe_metrics(probe)
    keys = ("RTC", "RDS", "RRS", "HRC", "node_coherence", "edge_coherence", "anchor_coherence")
    return {key: float(metrics[key]) for key in keys if isinstance(metrics.get(key), (int, float))}


def build_ui_snapshot(result: Dict[str, Any]) -> Dict[str, Any]:
    governance = result.get("governance") or {}
    chain = result.get("governance_chain_status") or {}
    canon = result.get("canon_lineage") or {}
    probe = result.get("probe_artifacts")
    capabilities = [
        c.get("capability_id")
        for c in result.get("exposed_capabilities", [])
        if isinstance(c, dict) and c.get("capability_id")
    ]
    halted = bool(result.get("halted", False))
    return {
        "schema_version": "lumina-runtime-ui-cycle-v0.3",
        "timestamp": result.get("created_at"),
        "run_id": result.get("run_id"),
        "requested_action": result.get("requested_action"),
        "action_type": result.get("action_type"),
        "mode": {"requested": result.get("requested_mode"), "current": result.get("target_mode")},
        "status": {"halted": halted, "reason": result.get("halt_reason"), "label": "Halted" if halted else "Stable"},
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
            "active": isinstance(probe, dict),
            "instrument_version": probe.get("instrument_version") if isinstance(probe, dict) else None,
            "instrument_class": probe.get("instrument_class") if isinstance(probe, dict) else None,
            "probe_mode": probe.get("probe_mode") if isinstance(probe, dict) else None,
            "run_id": _probe_run_id(probe),
            "pulse_id": _probe_pulse_id(probe),
            "coherence": _probe_metric(
                probe,
                "hybrid_continuity_coherence",
                "continuity_coherence",
                "coherence",
                "coherence_score",
            ),
            "presence": _probe_metric(probe, "presence"),
            "lock": _probe_metric(probe, "alignment_strength", "lock"),
            "hybrid_continuity_coherence": _probe_metric(probe, "hybrid_continuity_coherence"),
            "topology_metrics": _topology_metrics(probe),
            "topology_receipt_present": isinstance(probe, dict) and isinstance(probe.get("topology_receipt"), dict),
        },
        "authority_boundary": "Display receipt only; does not authorize action, alter governance, mutate canon, change mode legality, expose capabilities, or execute tools.",
    }


def _archive_public_snapshot(snapshot: Dict[str, Any]) -> None:
    PUBLIC_HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    run_id = snapshot.get("run_id") or "unknown-run"
    safe_run = str(run_id).replace("/", "-").replace(":", "-")
    ts = str(snapshot.get("timestamp") or "unknown-time").replace(":", "-").replace("+", "_")
    archive_name = f"{ts}_{safe_run}.json"
    archive_path = PUBLIC_HISTORY_DIR / archive_name
    with archive_path.open("w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=2)
        f.write("\n")

    index = []
    if PUBLIC_HISTORY_INDEX.exists():
        try:
            index = _read_json(PUBLIC_HISTORY_INDEX)
        except Exception:
            index = []

    entry = {
        "timestamp": snapshot.get("timestamp"),
        "run_id": run_id,
        "status": snapshot.get("status", {}).get("label"),
        "mode": snapshot.get("mode", {}).get("current"),
        "file": f"/runtime/history/{archive_name}",
        "probe_instrument_version": snapshot.get("probe", {}).get("instrument_version"),
        "hybrid_continuity_coherence": snapshot.get("probe", {}).get("hybrid_continuity_coherence"),
    }
    index = [entry] + [e for e in index if e.get("run_id") != run_id]
    index = index[:25]
    with PUBLIC_HISTORY_INDEX.open("w", encoding="utf-8") as f:
        json.dump(index, f, indent=2)
        f.write("\n")


def write_snapshot(snapshot: Dict[str, Any], paths: Iterable[str | Path]) -> None:
    wrote_public = False
    for path in paths:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("w", encoding="utf-8") as f:
            json.dump(snapshot, f, indent=2)
            f.write("\n")
        if target == PUBLIC_SNAPSHOT_PATH:
            wrote_public = True
    if wrote_public:
        _archive_public_snapshot(snapshot)


def emit_from_result_file(result_path: str | Path, *, public: bool = True, state: bool = True) -> Dict[str, Any]:
    result = _read_json(result_path)
    snapshot = build_ui_snapshot(result)
    paths = []
    if public:
        paths.append(PUBLIC_SNAPSHOT_PATH)
    if state:
        paths.append(STATE_SNAPSHOT_PATH)
    write_snapshot(snapshot, paths)
    return {"snapshot": snapshot, "paths": [str(p) for p in paths]}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("result_json")
    parser.add_argument("--no-public", action="store_true")
    parser.add_argument("--no-state", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    emitted = emit_from_result_file(args.result_json, public=not args.no_public, state=not args.no_state)
    print(json.dumps(emitted, indent=2))

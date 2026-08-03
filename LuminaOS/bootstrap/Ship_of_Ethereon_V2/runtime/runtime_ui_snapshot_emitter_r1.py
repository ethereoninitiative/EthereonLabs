from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable, Optional
import argparse
import hashlib
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
SEMANTIC_TOP_LEVEL_KEYS = (
    "schema_version",
    "requested_action",
    "action_type",
    "mode",
    "status",
    "canon",
    "capabilities",
    "authority_boundary",
)
SEMANTIC_GOVERNANCE_KEYS = ("transition", "mutation", "promotion", "chain_valid")
VOLATILE_PROBE_KEYS = {"run_id", "pulse_id"}


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
        "schema_version": "lumina-runtime-ui-cycle-v0.4",
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


def runtime_snapshot_semantic_payload(snapshot: Dict[str, Any]) -> Dict[str, Any]:
    """Return the stable observation represented by a public runtime receipt.

    Timestamps, run identifiers, probe identifiers, history pointers, and runtime
    truth projection fields are intentionally excluded. The observation cycle may
    still write fresh local state, but tracked public evidence changes only when
    this payload changes.
    """

    if not isinstance(snapshot, dict):
        return {}
    payload = {key: snapshot.get(key) for key in SEMANTIC_TOP_LEVEL_KEYS}
    governance = snapshot.get("governance") if isinstance(snapshot.get("governance"), dict) else {}
    payload["governance"] = {key: governance.get(key) for key in SEMANTIC_GOVERNANCE_KEYS}
    probe = snapshot.get("probe") if isinstance(snapshot.get("probe"), dict) else {}
    payload["probe"] = {key: value for key, value in probe.items() if key not in VOLATILE_PROBE_KEYS}
    return payload


def runtime_snapshot_semantic_fingerprint(snapshot: Dict[str, Any]) -> str:
    canonical = json.dumps(
        runtime_snapshot_semantic_payload(snapshot),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def public_snapshot_semantically_changed(
    snapshot: Dict[str, Any],
    existing_path: str | Path = PUBLIC_SNAPSHOT_PATH,
) -> bool:
    path = Path(existing_path)
    if not path.exists():
        return True
    try:
        existing = _read_json(path)
    except (OSError, json.JSONDecodeError, TypeError, ValueError):
        return True
    if not isinstance(existing, dict) or not existing:
        return True
    return runtime_snapshot_semantic_fingerprint(existing) != runtime_snapshot_semantic_fingerprint(snapshot)


def snapshot_write_plan(
    snapshot: Dict[str, Any],
    *,
    emit_public_snapshot: bool = True,
    emit_state_snapshot: bool = True,
    public_snapshot_path: str | Path = PUBLIC_SNAPSHOT_PATH,
    state_snapshot_path: str | Path = STATE_SNAPSHOT_PATH,
) -> Dict[str, Any]:
    public_changed = bool(
        emit_public_snapshot
        and public_snapshot_semantically_changed(snapshot, existing_path=public_snapshot_path)
    )
    paths: list[Path] = []
    if public_changed:
        paths.append(Path(public_snapshot_path))
    if emit_state_snapshot:
        paths.append(Path(state_snapshot_path))
    return {
        "paths": paths,
        "public_snapshot_changed": public_changed,
        "semantic_fingerprint": runtime_snapshot_semantic_fingerprint(snapshot),
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
    plan = snapshot_write_plan(
        snapshot,
        emit_public_snapshot=public,
        emit_state_snapshot=state,
    )
    write_snapshot(snapshot, plan["paths"])
    return {
        "snapshot": snapshot,
        "paths": [str(p) for p in plan["paths"]],
        "public_snapshot_changed": plan["public_snapshot_changed"],
        "semantic_fingerprint": plan["semantic_fingerprint"],
    }


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

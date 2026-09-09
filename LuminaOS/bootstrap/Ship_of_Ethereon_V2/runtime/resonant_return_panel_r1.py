from __future__ import annotations

"""Read-only Resonant Return Panel R1 over an explicitly supplied snapshot.

No runtime/store is constructed, and evidence locators are never opened. The
panel composes the existing manifold and the steward used by continue preflight;
it neither verifies supplied decisions nor makes new governance decisions.
"""

import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys
from typing import Any

if __package__:
    from .lumina_continuation_action_r1 import normalize_continuation_action
    from .lumina_self_guidance_steward_r1 import LuminaSelfGuidanceSteward
    from .resonant_manifold_r1 import AXES, ManifoldPoint, PotentialTrajectory, manifold_snapshot
else:
    from lumina_continuation_action_r1 import normalize_continuation_action
    from lumina_self_guidance_steward_r1 import LuminaSelfGuidanceSteward
    from resonant_manifold_r1 import AXES, ManifoldPoint, PotentialTrajectory, manifold_snapshot


INPUT_SCHEMA = "resonant-return-panel-input-r1"
PANEL_SCHEMA = "resonant-return-panel-r1"
MAX_INPUT_BYTES = 1_048_576
MAX_CANDIDATES = 64
SOURCE_ROOT = "LuminaOS/bootstrap/Ship_of_Ethereon_V2/runtime/"
AUTHORITY_BOUNDARY = (
    "Read-only orientation from supplied evidence. Scores and continuation focus "
    "are advisory; reported governance is unverified input. Runtime governance "
    "remains authoritative, and a fresh governed cycle must decide execution."
)


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _unique_object(pairs: list[tuple[str, Any]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _object(value: Any, field: str) -> dict:
    if not isinstance(value, dict):
        raise ValueError(f"{field} must be an object")
    return value


def _text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    return value


def _list(value: Any, field: str) -> list:
    if not isinstance(value, list):
        raise ValueError(f"{field} must be a list")
    return value


def _surface(value: Any, field: str, project_id: str) -> dict:
    result = _object({} if value is None else value, field)
    if "project_id" in result and result["project_id"] != project_id:
        raise ValueError(f"{field}.project_id disagrees with the panel project")
    for key in (
        "session_id", "checkpoint_path", "pending_next_action", "last_completed_action",
        "linked_host_bundle", "linked_restore_checkpoint", "focus_target", "current_mode",
        "return_strategy", "recommended_next_action",
    ):
        if result.get(key) is not None:
            _text(result[key], f"{field}.{key}")
    for key in ("open_panels", "pinned_tools", "reference_ids", "panel_ids", "pinned_tool_ids"):
        if key in result:
            for item in _list(result[key], f"{field}.{key}"):
                _text(item, f"{field}.{key} item")
    for key in ("panels", "references", "tool_bindings"):
        if key in result:
            for item in _list(result[key], f"{field}.{key}"):
                _object(item, f"{field}.{key} item")
    return result


def _candidate(value: Any, index: int) -> dict:
    field = f"candidates[{index}]"
    item = _object(value, field)
    for key in ("trajectory_id", "label", "action"):
        _text(item.get(key), f"{field}.{key}")
    vector = _object(item.get("vector"), f"{field}.vector")
    if set(vector) != set(AXES):
        raise ValueError(f"{field}.vector must contain exactly the five manifold axes")
    for axis, number in vector.items():
        if type(number) not in (int, float) or not 0.0 <= number <= 1.0:
            raise ValueError(f"{field}.vector.{axis} must be finite and in [0, 1]")
    refs = _list(item.get("evidence_refs"), f"{field}.evidence_refs")
    if not refs:
        raise ValueError(f"{field} requires at least one evidence reference")
    for ref in refs:
        _text(ref, f"{field}.evidence_refs item")
    reported = item.get("reported_governance")
    if reported is None:
        reported = {
            "status": "deferred",
            "reason": "No external governance decision was supplied.",
            "evidence_ref": None,
        }
    else:
        reported = _object(reported, f"{field}.reported_governance")
        if reported.get("status") not in ("allowed", "denied", "deferred"):
            raise ValueError(f"{field}.reported_governance.status is unknown")
        _text(reported.get("reason"), f"{field}.reported_governance.reason")
        _text(reported.get("evidence_ref"), f"{field}.reported_governance.evidence_ref")
    # Whitelist output fields: caller-supplied claims or allowed flags never pass through.
    return {
        "trajectory_id": item["trajectory_id"],
        "label": item["label"],
        "action": normalize_continuation_action(item["action"]),
        "vector": vector,
        "evidence_refs": refs,
        "reported_governance": {key: reported[key] for key in ("status", "reason", "evidence_ref")},
    }


def build_panel(payload: dict) -> dict:
    """Return deterministic JSON-compatible orientation without modifying input/state."""
    encoded = canonical_json(_object(payload, "input")).encode("utf-8")
    if len(encoded) > MAX_INPUT_BYTES:
        raise ValueError("input exceeds the 1 MiB panel bound")
    # Copy through the JSON contract so caller-owned nested objects cannot leak out.
    data = json.loads(encoded)
    if data.get("schema_version") != INPUT_SCHEMA:
        raise ValueError("unexpected input schema_version")
    if data.get("evidence_scope") not in ("synthetic_fixture", "supplied_snapshot"):
        raise ValueError("evidence_scope must be synthetic_fixture or supplied_snapshot")
    project_id = _text(data.get("project_id"), "project_id")
    requested_action = _text(data.get("requested_action"), "requested_action")
    returned = _surface(data.get("resolved_project_return"), "resolved_project_return", project_id)
    latest = _surface(returned.get("latest_restore", returned), "latest_restore", project_id)
    host = _surface(data.get("resolved_host_bundle"), "resolved_host_bundle", project_id)
    stance = _surface(data.get("working_stance"), "working_stance", project_id)
    history = _list(data.get("guidance_history", []), "guidance_history")
    for row in history:
        _surface(_object(row, "guidance_history item"), "guidance_history item", project_id)
    checkpoint = latest.get("checkpoint_path")
    for field, surface in (("resolved_host_bundle", host), ("working_stance", stance)):
        linked = surface.get("linked_restore_checkpoint")
        if checkpoint and linked and linked != checkpoint:
            raise ValueError(f"{field} references a different return checkpoint")

    candidate_rows = _list(data.get("candidates"), "candidates")
    if len(candidate_rows) > MAX_CANDIDATES:
        raise ValueError(f"at most {MAX_CANDIDATES} candidates may be supplied")
    candidates = [_candidate(row, i) for i, row in enumerate(candidate_rows)]
    ids = [row["trajectory_id"] for row in candidates]
    if len(ids) != len(set(ids)):
        raise ValueError("trajectory_id values must be unique")

    # Explicit binary evidence-presence profile, not a calibrated measure of a resident.
    latest_prefix = (
        "#/resolved_project_return/latest_restore"
        if "latest_restore" in returned else "#/resolved_project_return"
    )
    axis_sources = {
        "instantiated_state": [latest_prefix] if latest else [],
        "continuity_history": (
            ([f"{latest_prefix}/checkpoint_path"] if checkpoint else [])
            + (["#/guidance_history"] if history else [])
        ),
        "relational_context": [
            pointer for pointer, value in (
                ("#/working_stance/reference_ids", stance.get("reference_ids")),
                ("#/resolved_host_bundle/reference_ids", host.get("reference_ids")),
                ("#/resolved_host_bundle/references", host.get("references")),
            ) if value
        ],
        "orientation_field": [
            pointer for pointer, value in (
                (f"{latest_prefix}/pending_next_action", latest.get("pending_next_action")),
                ("#/working_stance/focus_target", stance.get("focus_target")),
                ("#/resolved_host_bundle/focus_target", host.get("focus_target")),
            ) if value
        ],
        "potential_trajectories": ["#/candidates"] if candidates else [],
    }
    current = ManifoldPoint(**{axis: float(bool(axis_sources[axis])) for axis in AXES})
    snapshot = manifold_snapshot(current, [
        PotentialTrajectory(
            trajectory_id=row["trajectory_id"], label=row["label"],
            vector=ManifoldPoint(**row["vector"]),
            allowed=row["reported_governance"]["status"] == "allowed",
            governance_reason=row["reported_governance"]["reason"],
        )
        for row in sorted(candidates, key=lambda row: row["trajectory_id"])
    ])
    by_id = {row["trajectory_id"]: row for row in candidates}
    ranked = []
    for row in snapshot["ranked_trajectories"]:
        ranked.append({
            **by_id[row["trajectory_id"]],
            "reachable_in_supplied_snapshot": row["allowed"],
            "metrics": {"resonant_manifold_r1": {
                key: row[key] for key in (
                    "harmonic_coherence", "orientation_attraction", "potential_contribution", "reachable_score",
                )
            }},
        })

    steward = LuminaSelfGuidanceSteward()
    advisory = steward.advisory_summary(steward.advise(
        project_id=project_id, requested_action=requested_action,
        current_mode="Continuity", target_mode="Observation",
        resolved_project_return=returned, resolved_host_bundle=host,
        working_stance=stance, guidance_history=history,
    ))
    focus = normalize_continuation_action(advisory["recommended_next_action"])
    evidence_refs = sorted({
        ref for ref in (
            checkpoint, latest.get("linked_host_bundle"), host.get("linked_restore_checkpoint"),
            *[ref for row in candidates for ref in row["evidence_refs"]],
            *[row["reported_governance"]["evidence_ref"] for row in candidates],
            *[row.get("checkpoint_path") for row in history],
        ) if ref
    })
    return {
        "schema_version": PANEL_SCHEMA,
        "project_id": project_id,
        "evidence_scope": data["evidence_scope"],
        "input_sha256": sha256(encoded).hexdigest(),
        "read_only": True,
        "current_return_point": {
            "project_return_present": bool(latest),
            "checkpoint_ref": checkpoint,
            "last_completed_action": latest.get("last_completed_action"),
            "pending_next_action": latest.get("pending_next_action"),
            "coordinates": current.to_dict(),
            "coordinate_basis": "binary supplied-evidence presence; not quality, probability, or resident state",
            "axis_evidence": axis_sources,
            "metrics": {"resonant_manifold_r1": {
                "potential_axis_contribution": snapshot["potential_axis_contribution"],
            }},
        },
        "candidate_trajectories": ranked,
        "candidate_vector_basis": "caller-supplied bounded coordinates; not inferred measurements",
        "governance_membrane": {
            "authority": "external_runtime_governance",
            "decisions_verified": False,
            "execution_authorized": False,
            "reported_status_counts": {
                status: sum(row["reported_governance"]["status"] == status for row in candidates)
                for status in ("allowed", "denied", "deferred")
            },
            "reachable_count_in_supplied_snapshot": snapshot["lawful_reachable_count"],
        },
        "continuation_focus": {
            **advisory,
            "scope": "preview from supplied inputs; not a live lumina continue invocation",
            "selection_owner": "lumina_self_guidance_steward_r1",
            "current_mode": "Continuity", "target_mode": "Observation", "action_type": "audit",
            "matching_trajectory_ids": sorted(row["trajectory_id"] for row in candidates if row["action"] == focus),
            "execution_authorized": False,
        },
        "evidence": {
            "references": evidence_refs,
            "references_opened": False,
            "references_verified": False,
            "source_files": [SOURCE_ROOT + name for name in (
                "resonant_return_panel_r1.py", "resonant_manifold_r1.py",
                "lumina_self_guidance_steward_r1.py", "lumina_continuation_action_r1.py",
                "lumina_continue_controller_r1.py",
            )],
        },
        "claims": {name: False for name in (
            "governance_authority", "mutation_authority", "canon_promotion", "identity_proof",
            "consciousness_proof", "continuity_proof", "literal_magnetism", "frequency_measurement",
        )},
        "authority_boundary": AUTHORITY_BOUNDARY,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="explicit panel input JSON; output goes to stdout")
    args = parser.parse_args(argv)
    try:
        with args.input.open("rb") as handle:
            raw = handle.read(MAX_INPUT_BYTES + 1)
        if len(raw) > MAX_INPUT_BYTES:
            raise ValueError("input exceeds the 1 MiB panel bound")
        result = build_panel(json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_object))
    except (OSError, ValueError, TypeError, RecursionError) as error:
        print(f"resonant-return-panel: {error}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

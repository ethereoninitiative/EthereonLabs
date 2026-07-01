#!/usr/bin/env python3
"""Lumina Bridge Field Viewer R1.

Read-only verification and projection of the committed Resonant Field Reveal
sample into the local Bridge surface.

This module reads existing artifacts only. It does not regenerate a field,
select trajectories, create governance decisions, establish identity, or prove
continuity.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Dict, List, Mapping


SCHEMA_VERSION = "lumina-bridge-field-viewer-r1"
FIELD_SAMPLE_RELATIVE = Path(
    "LuminaOS/bootstrap/Ship_of_Ethereon_V2/"
    "artifacts/resonant_field_reveal/sample_0001"
)
INPUT_FILE = "resonant_field_reveal_r1_input.json"
REVEAL_JSON_FILE = "resonant_field_reveal_r1.json"
REVEAL_SVG_FILE = "resonant_field_reveal_r1.svg"
RECEIPT_FILE = "resonant_field_reveal_r1_receipt.json"

FIELD_AUTHORITY_BOUNDARY = (
    "Bridge Field Viewer R1 displays and verifies a committed inspection "
    "artifact. It does not regenerate the field, create governance decisions, "
    "establish identity, prove observer continuity, claim literal magnetism, "
    "or authorize a trajectory."
)

OBSERVER_NOTE = (
    "Bridge is the witness surface. The rendered geometry is an observed "
    "pattern of computed relations, not the observer itself and not proof of "
    "identity."
)

CONTINUITY_NOTE = (
    "The committed sample is a stable return coordinate for comparison. Its "
    "repeatability demonstrates artifact continuity, not metaphysical "
    "continuity."
)

INTERPRETIVE_KEY = [
    {
        "toki_pona": "lukin",
        "ethereonic": "witnessing the field",
        "computational": "read-only inspection of committed artifacts",
    },
    {
        "toki_pona": "awen",
        "ethereonic": "that which remains",
        "computational": "continuity history and byte-reproducible return",
    },
    {
        "toki_pona": "poka",
        "ethereonic": "relation and nearness",
        "computational": "relational context within the manifold point",
    },
    {
        "toki_pona": "nasin",
        "ethereonic": "a possible path",
        "computational": "one derived potential trajectory",
    },
    {
        "toki_pona": "linja suno",
        "ethereonic": "luminous thread",
        "computational": "the deterministic visible trace of a trajectory",
    },
    {
        "toki_pona": "lawa",
        "ethereonic": "the boundary that holds",
        "computational": "external governance classification and membrane",
    },
    {
        "toki_pona": "kama sin",
        "ethereonic": "returning again",
        "computational": "reproducible reappearance from the same input",
    },
]


def _read_bytes(path: Path) -> bytes:
    try:
        return path.read_bytes()
    except OSError:
        return b""


def _read_json_bytes(payload: bytes) -> Dict[str, Any]:
    try:
        value = json.loads(payload.decode("utf-8"))
        return value if isinstance(value, dict) else {}
    except (UnicodeDecodeError, json.JSONDecodeError):
        return {}


def _digest(payload: bytes) -> str:
    return sha256(payload).hexdigest()


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _thread_projection(thread: Mapping[str, Any]) -> Dict[str, Any]:
    metrics = _safe_dict(thread.get("metrics"))
    geometry = _safe_dict(thread.get("geometry"))
    return {
        "thread_id": thread.get("thread_id"),
        "trajectory_id": thread.get("trajectory_id"),
        "label": thread.get("label"),
        "allowed": thread.get("allowed") is True,
        "status": thread.get("status"),
        "governance_reason": thread.get("governance_reason"),
        "metrics": {
            "harmonic_coherence": metrics.get("harmonic_coherence"),
            "orientation_attraction": metrics.get("orientation_attraction"),
            "potential_contribution": metrics.get("potential_contribution"),
            "reachable_score": metrics.get("reachable_score"),
        },
        "geometry": {
            "endpoint_radius": geometry.get("endpoint_radius"),
            "membrane_radius": geometry.get("membrane_radius"),
        },
    }


def load_bridge_field(repo_root: Path) -> Dict[str, Any]:
    """Load and verify the committed field sample without mutating it."""
    sample_dir = repo_root / FIELD_SAMPLE_RELATIVE
    paths = {
        "input": sample_dir / INPUT_FILE,
        "reveal_json": sample_dir / REVEAL_JSON_FILE,
        "reveal_svg": sample_dir / REVEAL_SVG_FILE,
        "receipt": sample_dir / RECEIPT_FILE,
    }
    payloads = {name: _read_bytes(path) for name, path in paths.items()}
    present = all(payloads.values())

    if not present:
        return {
            "schema_version": SCHEMA_VERSION,
            "present": False,
            "verified": False,
            "status": "missing_or_incomplete",
            "sample_id": None,
            "threads": [],
            "thread_count": 0,
            "allowed_count": 0,
            "denied_count": 0,
            "verification": {
                "all_files_present": False,
                "receipt_hashes_match": False,
                "receipt_scope_exact": False,
                "thread_contract_holds": False,
                "governance_geometry_holds": False,
                "claims_bounded": False,
                "svg_contract_holds": False,
            },
            "artifact": {
                "sample_dir": str(sample_dir),
                "svg_href": "/field.svg",
            },
            "interpretive_key": INTERPRETIVE_KEY,
            "observer_note": OBSERVER_NOTE,
            "continuity_note": CONTINUITY_NOTE,
            "authority_boundary": FIELD_AUTHORITY_BOUNDARY,
        }

    manifest = _read_json_bytes(payloads["input"])
    reveal = _read_json_bytes(payloads["reveal_json"])
    receipt = _read_json_bytes(payloads["receipt"])
    svg = payloads["reveal_svg"].decode("utf-8", errors="replace")

    receipt_inputs = _safe_dict(receipt.get("input_artifact"))
    receipt_outputs = _safe_dict(receipt.get("artifacts"))
    scope_exact = (
        set(receipt_inputs) == {INPUT_FILE}
        and set(receipt_outputs) == {REVEAL_JSON_FILE, REVEAL_SVG_FILE}
    )
    hashes_match = (
        receipt_inputs.get(INPUT_FILE) == _digest(payloads["input"])
        and receipt_outputs.get(REVEAL_JSON_FILE) == _digest(payloads["reveal_json"])
        and receipt_outputs.get(REVEAL_SVG_FILE) == _digest(payloads["reveal_svg"])
    )

    raw_threads = [
        item for item in _safe_list(reveal.get("threads")) if isinstance(item, dict)
    ]
    threads = [_thread_projection(item) for item in raw_threads]
    trajectory_ids = [item.get("trajectory_id") for item in threads]
    unique_ids = (
        all(isinstance(item, str) and item for item in trajectory_ids)
        and len(trajectory_ids) == len(set(trajectory_ids))
    )
    thread_contract = (
        reveal.get("thread_count") == len(threads)
        and unique_ids
        and len(threads) > 0
    )

    geometry_checks = []
    for thread in threads:
        endpoint = thread["geometry"].get("endpoint_radius")
        membrane = thread["geometry"].get("membrane_radius")
        if not isinstance(endpoint, (int, float)) or not isinstance(
            membrane, (int, float)
        ):
            geometry_checks.append(False)
        elif thread["allowed"]:
            geometry_checks.append(endpoint > membrane)
        else:
            geometry_checks.append(
                abs(float(endpoint) - float(membrane)) < 0.01
                and thread.get("status") == "governance_denied"
            )
    governance_geometry = bool(geometry_checks) and all(geometry_checks)

    claims = _safe_dict(reveal.get("claims"))
    claims_bounded = claims == {
        "governance_authority": False,
        "identity_proof": False,
        "literal_magnetism": False,
    }
    svg_contract = (
        'data-role="current-attractor"' in svg
        and 'data-role="governance-membrane"' in svg
        and all(item in svg for item in trajectory_ids if isinstance(item, str))
    )
    identity_matches = (
        receipt.get("sample_id") == manifest.get("sample_id")
        and receipt.get("reveal_id") == reveal.get("reveal_id")
        and manifest.get("reveal_id") == reveal.get("reveal_id")
        and manifest.get("source_model_id") == reveal.get("source_model_id")
    )

    verification = {
        "all_files_present": True,
        "receipt_hashes_match": hashes_match,
        "receipt_scope_exact": scope_exact,
        "identity_matches": identity_matches,
        "thread_contract_holds": thread_contract,
        "governance_geometry_holds": governance_geometry,
        "claims_bounded": claims_bounded,
        "svg_contract_holds": svg_contract,
    }
    verified = all(verification.values())
    allowed_count = sum(1 for item in threads if item["allowed"])
    denied_count = len(threads) - allowed_count

    return {
        "schema_version": SCHEMA_VERSION,
        "present": True,
        "verified": verified,
        "status": "verified_committed_fixture" if verified else "verification_failed",
        "sample_id": receipt.get("sample_id"),
        "reveal_id": reveal.get("reveal_id"),
        "source_model_id": reveal.get("source_model_id"),
        "reveal_class": reveal.get("reveal_class"),
        "current_point": _safe_dict(reveal.get("current_point")),
        "thread_count": len(threads),
        "allowed_count": allowed_count,
        "denied_count": denied_count,
        "threads": threads,
        "claims": claims,
        "verification": verification,
        "artifact": {
            "sample_dir": str(sample_dir),
            "input_path": str(paths["input"]),
            "json_path": str(paths["reveal_json"]),
            "svg_path": str(paths["reveal_svg"]),
            "receipt_path": str(paths["receipt"]),
            "svg_href": "/field.svg",
            "input_sha256": _digest(payloads["input"]),
            "json_sha256": _digest(payloads["reveal_json"]),
            "svg_sha256": _digest(payloads["reveal_svg"]),
        },
        "interpretive_key": INTERPRETIVE_KEY,
        "observer_note": OBSERVER_NOTE,
        "continuity_note": CONTINUITY_NOTE,
        "source_authority_boundary": reveal.get("authority_boundary"),
        "authority_boundary": FIELD_AUTHORITY_BOUNDARY,
    }


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[4]
    print(json.dumps(load_bridge_field(root), indent=2))

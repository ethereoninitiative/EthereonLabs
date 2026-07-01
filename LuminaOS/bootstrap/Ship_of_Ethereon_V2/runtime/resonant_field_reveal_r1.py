from __future__ import annotations

"""Resonant Field Reveal R1.

A deterministic reveal layer for Resonant Manifold observations.

The module translates already-derived manifold relations into inspectable JSON
and SVG artifacts. It does not create governance decisions, establish identity,
or claim literal electromagnetic fields.
"""

from hashlib import sha256
from html import escape
import json
from math import cos, pi, sin, sqrt
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Sequence, Tuple

from resonant_manifold_r1 import ManifoldPoint, PotentialTrajectory, manifold_snapshot


REVEAL_ID = "resonant-field-reveal-r1"
REVEAL_CLASS = "deterministic computational field visualization"
LITERAL_MAGNETISM_CLAIM = False
IDENTITY_PROOF_CLAIM = False
GOVERNANCE_AUTHORITY_CLAIM = False

AUTHORITY_BOUNDARY = (
    "The Resonant Field Reveal renders derived manifold relations only. "
    "It does not create governance decisions, establish identity, prove "
    "continuity, or claim literal magnetism."
)


def _round(value: float) -> float:
    return round(float(value), 3)


def _stable_angle(identifier: str) -> float:
    digest = sha256(identifier.encode("utf-8")).hexdigest()
    fraction = int(digest[:12], 16) / float(16**12 - 1)
    return fraction * 2.0 * pi


def _distance(point: Mapping[str, float], center: Tuple[float, float]) -> float:
    return sqrt((point["x"] - center[0]) ** 2 + (point["y"] - center[1]) ** 2)


def _thread_geometry(
    item: Mapping[str, Any],
    center: Tuple[float, float],
    membrane_radius: float,
) -> Dict[str, Any]:
    """Map one ranked trajectory into deterministic reveal geometry."""
    angle = _stable_angle(str(item["trajectory_id"]))
    direction = (cos(angle), sin(angle))
    normal = (-direction[1], direction[0])

    coherence = float(item["harmonic_coherence"])
    attraction = float(item["orientation_attraction"])
    potential = float(item["potential_contribution"])
    relational = float(item["vector"]["relational_context"])

    start_radius = 34.0
    if item["allowed"]:
        end_radius = membrane_radius * (1.08 + 0.36 * float(item["reachable_score"]))
        status = "lawful_reachable"
    else:
        end_radius = membrane_radius
        status = "governance_denied"

    # Potential contribution influences curvature without changing authority.
    bend = membrane_radius * (
        (potential * 0.28)
        + ((attraction - 0.5) * 0.16)
        + ((relational - 0.5) * 0.08)
    )

    start = {
        "x": _round(center[0] + direction[0] * start_radius),
        "y": _round(center[1] + direction[1] * start_radius),
    }
    end = {
        "x": _round(center[0] + direction[0] * end_radius),
        "y": _round(center[1] + direction[1] * end_radius),
    }
    control_1 = {
        "x": _round(center[0] + direction[0] * end_radius * 0.34 + normal[0] * bend),
        "y": _round(center[1] + direction[1] * end_radius * 0.34 + normal[1] * bend),
    }
    control_2 = {
        "x": _round(center[0] + direction[0] * end_radius * 0.72 + normal[0] * bend * 0.45),
        "y": _round(center[1] + direction[1] * end_radius * 0.72 + normal[1] * bend * 0.45),
    }

    return {
        "thread_id": f"thread-{item['trajectory_id']}",
        "trajectory_id": item["trajectory_id"],
        "label": item["label"],
        "allowed": bool(item["allowed"]),
        "status": status,
        "governance_reason": item["governance_reason"],
        "metrics": {
            "harmonic_coherence": coherence,
            "orientation_attraction": attraction,
            "potential_contribution": potential,
            "reachable_score": float(item["reachable_score"]),
        },
        "geometry": {
            "start": start,
            "control_1": control_1,
            "control_2": control_2,
            "end": end,
            "angle_radians": _round(angle),
            "endpoint_radius": _round(_distance(end, center)),
            "membrane_radius": _round(membrane_radius),
        },
        "style": {
            "stroke_width": _round(1.4 + coherence * 4.2),
            "opacity": _round((0.32 + attraction * 0.62) if item["allowed"] else 0.48),
            "dash_pattern": None if item["allowed"] else "10 9",
        },
    }


def build_reveal(
    current: ManifoldPoint,
    trajectories: Iterable[PotentialTrajectory],
    denied_ids: Sequence[str] = (),
    *,
    width: int = 1200,
    height: int = 800,
) -> Dict[str, Any]:
    """Build the deterministic JSON reveal model."""
    if width < 480 or height < 360:
        raise ValueError("reveal canvas must be at least 480 x 360")

    trajectory_list = list(trajectories)
    snapshot = manifold_snapshot(current, trajectory_list, denied_ids=denied_ids)
    center = (_round(width / 2.0), _round(height / 2.0))
    membrane_radius = _round(min(width, height) * 0.30)

    ranked = sorted(snapshot["ranked_trajectories"], key=lambda item: item["trajectory_id"])
    threads = [
        _thread_geometry(item, center, membrane_radius)
        for item in ranked
    ]

    return {
        "reveal_id": REVEAL_ID,
        "reveal_class": REVEAL_CLASS,
        "source_model_id": snapshot["model_id"],
        "canvas": {
            "width": int(width),
            "height": int(height),
            "center": {"x": center[0], "y": center[1]},
            "governance_membrane_radius": membrane_radius,
        },
        "current_point": snapshot["current_point"],
        "thread_count": len(threads),
        "threads": threads,
        "claims": {
            "literal_magnetism": LITERAL_MAGNETISM_CLAIM,
            "identity_proof": IDENTITY_PROOF_CLAIM,
            "governance_authority": GOVERNANCE_AUTHORITY_CLAIM,
        },
        "authority_boundary": AUTHORITY_BOUNDARY,
    }


def _path_data(thread: Mapping[str, Any]) -> str:
    geometry = thread["geometry"]
    start = geometry["start"]
    c1 = geometry["control_1"]
    c2 = geometry["control_2"]
    end = geometry["end"]
    return (
        f"M {start['x']} {start['y']} "
        f"C {c1['x']} {c1['y']}, {c2['x']} {c2['y']}, {end['x']} {end['y']}"
    )


def render_svg(reveal: Mapping[str, Any]) -> str:
    """Render one reveal model as a standalone deterministic SVG."""
    canvas = reveal["canvas"]
    width = int(canvas["width"])
    height = int(canvas["height"])
    center = canvas["center"]
    membrane_radius = canvas["governance_membrane_radius"]

    thread_markup: List[str] = []
    denied_markers: List[str] = []
    for thread in reveal["threads"]:
        path = _path_data(thread)
        style = thread["style"]
        dash = (
            f' stroke-dasharray="{style["dash_pattern"]}"'
            if style["dash_pattern"]
            else ""
        )
        status = escape(str(thread["status"]))
        trajectory_id = escape(str(thread["trajectory_id"]))
        label = escape(str(thread["label"]))
        thread_markup.append(
            f'<g data-trajectory-id="{trajectory_id}" data-status="{status}">'
            f"<title>{label}</title>"
            f'<path d="{path}" class="thread-glow" '
            f'stroke-width="{style["stroke_width"] + 5.0:.3f}" '
            f'opacity="{max(0.12, style["opacity"] * 0.32):.3f}"{dash}/>'
            f'<path d="{path}" class="thread-core" '
            f'stroke-width="{style["stroke_width"]:.3f}" '
            f'opacity="{style["opacity"]:.3f}"{dash}/>'
            "</g>"
        )
        if not thread["allowed"]:
            end = thread["geometry"]["end"]
            denied_markers.append(
                f'<g class="denied-marker" data-trajectory-id="{trajectory_id}">'
                f'<circle cx="{end["x"]}" cy="{end["y"]}" r="11"/>'
                f'<path d="M {end["x"] - 6} {end["y"] - 6} '
                f'L {end["x"] + 6} {end["y"] + 6} '
                f'M {end["x"] + 6} {end["y"] - 6} '
                f'L {end["x"] - 6} {end["y"] + 6}"/>'
                "</g>"
            )

    description = escape(str(reveal["authority_boundary"]))
    return "\n".join(
        [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
            f'role="img" aria-labelledby="reveal-title reveal-desc">',
            '<title id="reveal-title">Resonant Field Reveal R1</title>',
            f'<desc id="reveal-desc">{description}</desc>',
            "<defs>",
            '<radialGradient id="field-bg" cx="50%" cy="50%" r="70%">',
            '<stop offset="0%" stop-color="#171321"/>',
            '<stop offset="58%" stop-color="#08070d"/>',
            '<stop offset="100%" stop-color="#020204"/>',
            "</radialGradient>",
            '<radialGradient id="attractor-fill" cx="42%" cy="38%" r="68%">',
            '<stop offset="0%" stop-color="#332318"/>',
            '<stop offset="62%" stop-color="#0b0808"/>',
            '<stop offset="100%" stop-color="#000000"/>',
            "</radialGradient>",
            '<filter id="thread-blur" x="-50%" y="-50%" width="200%" height="200%">',
            '<feGaussianBlur stdDeviation="6"/>',
            "</filter>",
            "</defs>",
            f'<rect width="{width}" height="{height}" fill="url(#field-bg)"/>',
            f'<circle cx="{center["x"]}" cy="{center["y"]}" r="{membrane_radius}" '
            'fill="none" stroke="#d89b58" stroke-width="1.5" '
            'stroke-dasharray="4 10" opacity="0.42" data-role="governance-membrane"/>',
            f'<circle cx="{center["x"]}" cy="{center["y"]}" r="{membrane_radius * 0.62:.3f}" '
            'fill="none" stroke="#9f6c3f" stroke-width="1" opacity="0.18"/>',
            '<g fill="none" stroke="#f0a75b" stroke-linecap="round" stroke-linejoin="round">',
            *thread_markup,
            "</g>",
            '<g class="denied-markers" fill="#120b0a" stroke="#ffd2a1" stroke-width="2.2">',
            *denied_markers,
            "</g>",
            f'<circle cx="{center["x"]}" cy="{center["y"]}" r="48" '
            'fill="#f0a75b" opacity="0.12" filter="url(#thread-blur)"/>',
            f'<circle cx="{center["x"]}" cy="{center["y"]}" r="34" '
            'fill="url(#attractor-fill)" stroke="#f0a75b" stroke-width="1.8" '
            'data-role="current-attractor"/>',
            "</svg>",
        ]
    )


def _sha256_text(text: str) -> str:
    return sha256(text.encode("utf-8")).hexdigest()


def emit_reveal_artifacts(
    output_dir: Path | str,
    current: ManifoldPoint,
    trajectories: Iterable[PotentialTrajectory],
    denied_ids: Sequence[str] = (),
    *,
    width: int = 1200,
    height: int = 800,
) -> Dict[str, Any]:
    """Write JSON, SVG, and a hash receipt to an explicit output directory."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    reveal = build_reveal(
        current,
        trajectories,
        denied_ids=denied_ids,
        width=width,
        height=height,
    )
    reveal_json = json.dumps(reveal, indent=2, sort_keys=True) + "\n"
    reveal_svg = render_svg(reveal) + "\n"

    json_path = output_path / "resonant_field_reveal_r1.json"
    svg_path = output_path / "resonant_field_reveal_r1.svg"
    receipt_path = output_path / "resonant_field_reveal_r1_receipt.json"

    json_path.write_text(reveal_json, encoding="utf-8")
    svg_path.write_text(reveal_svg, encoding="utf-8")

    receipt = {
        "receipt_id": "resonant-field-reveal-r1-receipt",
        "reveal_id": REVEAL_ID,
        "artifacts": {
            json_path.name: _sha256_text(reveal_json),
            svg_path.name: _sha256_text(reveal_svg),
        },
        "authority_boundary": AUTHORITY_BOUNDARY,
    }
    receipt_path.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return receipt

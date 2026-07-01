#!/usr/bin/env python3
"""Sea trial for Lumina Bridge Field Viewer R1."""
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
STUDIO = ROOT / "studio"
if str(STUDIO) not in sys.path:
    sys.path.insert(0, str(STUDIO))

from lumina_bridge_field_r1 import FIELD_AUTHORITY_BOUNDARY, load_bridge_field  # noqa: E402
from lumina_bridge_server_r2 import HTML  # noqa: E402
from lumina_bridge_state_r1 import REPO_ROOT  # noqa: E402


def main() -> int:
    field = load_bridge_field(REPO_ROOT)
    thread_ids = {item.get("trajectory_id") for item in field.get("threads", [])}
    denied = [item for item in field.get("threads", []) if not item.get("allowed")]
    toki_pona = {item.get("toki_pona") for item in field.get("interpretive_key", [])}

    checks = {
        "committed_field_present": field.get("present") is True,
        "committed_field_verified": field.get("verified") is True,
        "five_luminous_threads_visible": field.get("thread_count") == 5 and len(thread_ids) == 5,
        "lawful_and_denied_paths_visible": (
            field.get("allowed_count") == 4
            and field.get("denied_count") == 1
            and len(denied) == 1
            and denied[0].get("status") == "governance_denied"
        ),
        "observer_continuity_boundary_present": (
            "not the observer itself" in field.get("observer_note", "")
            and "artifact continuity" in field.get("continuity_note", "")
        ),
        "toki_pona_key_preserved": {
            "lukin", "awen", "poka", "nasin", "linja suno", "lawa", "kama sin"
        }.issubset(toki_pona),
        "field_authority_boundary_present": (
            "does not regenerate the field" in FIELD_AUTHORITY_BOUNDARY
            and "prove observer continuity" in FIELD_AUTHORITY_BOUNDARY
        ),
        "bridge_html_contains_field_surface": (
            "Luminous Threads" in HTML
            and "Toki Pona Interpretive Key" in HTML
            and "/api/field" in HTML
            and "/field.svg" in HTML
        ),
        "bridge_html_has_no_mutating_form": (
            'method="post"' not in HTML.lower()
            and 'action="/run"' not in HTML.lower()
        ),
    }
    summary = {
        "suite": "Lumina Bridge Field Viewer R1",
        "passed": all(checks.values()),
        "checks": checks,
        "field_schema": field.get("schema_version"),
        "sample_id": field.get("sample_id"),
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if summary["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

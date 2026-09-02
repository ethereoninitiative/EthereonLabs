from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_PATHS = [
    "README.md",
    "START_HERE_HUMANS.md",
    "CURRENT_OPERATING_MAP.md",
    "START_HERE_LUMINA_OS.md",
    "START_HERE_RUNTIME_PATH.md",
    "docs/README.md",
    "docs/ACTIVE_SURFACE_REGISTRY_R1.json",
    "docs/ARTIFACT_TRUTH_CONTRACT.md",
    "docs/archive/README.md",
    "LuminaOS/bootstrap/Ship_of_Ethereon_V2/ACTIVE_RUNTIME_INDEX.md",
]

REQUIRED_MARKERS = {
    "README.md": [
        "START_HERE_HUMANS.md",
        "CURRENT_OPERATING_MAP.md",
        "docs/README.md",
    ],
    "START_HERE_HUMANS.md": [
        "CURRENT_OPERATING_MAP.md",
        "docs/README.md",
        "START_HERE_LUMINA_OS.md",
    ],
    "CURRENT_OPERATING_MAP.md": [
        "docs/README.md",
        "docs/ACTIVE_SURFACE_REGISTRY_R1.json",
        "LuminaOS/bootstrap/Ship_of_Ethereon_V2/ACTIVE_RUNTIME_INDEX.md",
    ],
    "docs/README.md": [
        "## Truth order",
        "## Current operating documentation",
        "## Research and non-governing inquiry",
        "## Archive and lineage",
        "## Front-door hierarchy",
        "docs/ACTIVE_SURFACE_REGISTRY_R1.json",
        "docs/ARTIFACT_TRUTH_CONTRACT.md",
        "docs/archive/",
        "START_HERE_RUNTIME_PATH.md",
    ],
}

FORBIDDEN_ACTIVE_ARCHIVE_MARKERS = [
    "docs/archive/runtime-history/",
    "docs/archive/orientation-history/",
    "docs/archive/continuity-history/",
]


def fail(message: str) -> None:
    print(f"FAIL documentation-front-door: {message}")
    raise SystemExit(1)


def read(relative: str) -> str:
    path = ROOT / relative
    if not path.is_file():
        fail(f"missing required file: {relative}")
    return path.read_text(encoding="utf-8")


def main() -> int:
    for relative in REQUIRED_PATHS:
        if not (ROOT / relative).exists():
            fail(f"missing required path: {relative}")

    for relative, markers in REQUIRED_MARKERS.items():
        text = read(relative)
        missing = [marker for marker in markers if marker not in text]
        if missing:
            fail(f"{relative} is missing navigation markers: {missing}")

    operating_map = read("CURRENT_OPERATING_MAP.md")
    for archived in FORBIDDEN_ACTIVE_ARCHIVE_MARKERS:
        if archived in operating_map:
            fail(
                "CURRENT_OPERATING_MAP.md must not present archived implementation "
                f"families as current lanes: {archived}"
            )

    docs_front_door = read("docs/README.md")
    if "does not create runtime, governance, canon, capability" not in docs_front_door:
        fail("docs/README.md must state its non-authority boundary")

    compatibility = read("START_HERE_RUNTIME_PATH.md")
    if "compatibility waypoint" not in compatibility.lower():
        fail("START_HERE_RUNTIME_PATH.md must remain explicitly compatibility-only")

    print("PASS documentation-front-door")
    print("primary_hierarchy=README -> HUMAN_START -> OPERATING_MAP -> DOCS_FRONT_DOOR")
    print("runtime_branch=START_HERE_LUMINA_OS -> ACTIVE_RUNTIME_INDEX -> bin/lumina")
    return 0


if __name__ == "__main__":
    sys.exit(main())

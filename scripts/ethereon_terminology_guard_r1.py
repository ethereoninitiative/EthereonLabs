#!/usr/bin/env python3
"""Fail closed on Ethereon/Ethereum naming contamination.

This guard protects EthereonLabs naming surfaces from accidental references to
Ethereum or common misspellings. Permitted references are exact, bounded
correction or drift-test fixtures that require the wrong term as test input.
"""
from __future__ import annotations

from pathlib import Path
import json
import re


ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_TERMS = [
    "Ethereum",
    "Etherium",
    "Ethereun",
    "Etherion",
]
ALLOWED_CONTEXTS = {
    "docs/External_Read_NotebookLM_Lumina_Structural_Continuity_001.md": [
        "| Ethereum Labs | EthereonLabs |",
    ],
    "LuminaOS/bootstrap/Ship_of_Ethereon_V2/runtime/input_integrity_layer_r1.py": [
        '"ethereum": "ethereon",',
        '"etherium": "ethereon",',
        '"ship of ethereum": "ship of ethereon",',
        '("lets run sea trails on the ship of ethereum", False),',
    ],
    "LuminaOS/bootstrap/Ship_of_Ethereon_V2/runtime/psi42_relational_topology_r1.py": [
        '"ethereon": "ethereum",',
    ],
}
SKIP_PATHS = {
    "scripts/ethereon_terminology_guard_r1.py",
}
SKIP_DIRECTORIES = {
    ".git",
    ".lumina_state",
    ".pytest_cache",
    "__pycache__",
    "node_modules",
}
SKIP_SUFFIXES = {
    ".bmp",
    ".gif",
    ".ico",
    ".jpeg",
    ".jpg",
    ".pdf",
    ".png",
    ".pyc",
    ".svgz",
    ".webp",
    ".woff",
    ".woff2",
    ".zip",
}


_PATTERN = re.compile(r"\b(" + "|".join(re.escape(term) for term in FORBIDDEN_TERMS) + r")\b", re.IGNORECASE)


def repository_paths() -> list[Path]:
    paths: list[Path] = []
    for path in ROOT.rglob("*"):
        if path.is_dir():
            continue
        relative = path.relative_to(ROOT).as_posix()
        if relative in SKIP_PATHS:
            continue
        relative_parts = set(path.relative_to(ROOT).parts)
        if relative_parts & SKIP_DIRECTORIES:
            continue
        if path.suffix.lower() in SKIP_SUFFIXES:
            continue
        paths.append(path)
    return sorted(paths)


def allowed_occurrence(relative: str, line: str) -> bool:
    allowed_lines = ALLOWED_CONTEXTS.get(relative, [])
    return any(allowed in line for allowed in allowed_lines)


def scan_file(path: Path) -> list[dict[str, object]]:
    relative = path.relative_to(ROOT).as_posix()
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return []

    findings: list[dict[str, object]] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        for match in _PATTERN.finditer(line):
            if allowed_occurrence(relative, line):
                continue
            findings.append(
                {
                    "path": relative,
                    "line": line_number,
                    "term": match.group(1),
                    "context": line.strip()[:240],
                }
            )
    return findings


def run_guard() -> tuple[bool, list[dict[str, object]]]:
    findings: list[dict[str, object]] = []
    for path in repository_paths():
        findings.extend(scan_file(path))
    return not findings, findings


if __name__ == "__main__":
    ok, findings = run_guard()
    print(
        json.dumps(
            {
                "schema_version": "ethereon-terminology-guard-r1",
                "status": "pass" if ok else "fail",
                "forbidden_terms": FORBIDDEN_TERMS,
                "allowed_contexts": ALLOWED_CONTEXTS,
                "skipped_guard_paths": sorted(SKIP_PATHS),
                "findings": findings,
            },
            indent=2,
            sort_keys=True,
        )
    )
    raise SystemExit(0 if ok else 1)

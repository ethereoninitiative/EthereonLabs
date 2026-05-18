from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Iterable
import json
import re
import subprocess


WATCH_TERMS = {
    "flattening_verbs": ["ensures", "guarantees", "maintains", "automatically", "verifies", "proves"],
    "symbolic_terms": ["ethereonic", "resonance", "harmonic", "toki", "pona", "light language", "psi42", "psi-42"],
    "authority_terms": ["governance", "canon", "promotion", "mode legality", "capability loading", "checkpoint legality"],
}

SCAN_GLOBS = [
    "README.md",
    "docs/**/*.md",
    "artifacts/**/*.md",
    "artifacts/**/*.json",
    "public/runtime/*.json",
    "LuminaOS/bootstrap/Ship_of_Ethereon_V2/runtime/**/*.py",
]


@dataclass
class Finding:
    category: str
    severity: str
    path: str
    line: int
    excerpt: str
    recommendation: str


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / ".git").exists() or (parent / "LuminaOS").exists():
            return parent
    return Path.cwd()


def iter_files(root: Path) -> Iterable[Path]:
    seen = set()
    for pattern in SCAN_GLOBS:
        for path in root.glob(pattern):
            if path.is_file() and path not in seen:
                seen.add(path)
                yield path


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(errors="ignore")


def scan_file(root: Path, path: Path) -> List[Finding]:
    rel = str(path.relative_to(root))
    findings: List[Finding] = []
    lines = read_text(path).splitlines()
    for idx, line in enumerate(lines, start=1):
        lowered = line.lower()
        for verb in WATCH_TERMS["flattening_verbs"]:
            if re.search(rf"\b{re.escape(verb)}\b", lowered):
                findings.append(Finding(
                    category="flattening_verb",
                    severity="watch",
                    path=rel,
                    line=idx,
                    excerpt=line.strip()[:220],
                    recommendation="Confirm this verb points to an implementation, test, or receipt; soften if mechanism is partial.",
                ))
        if any(s in lowered for s in WATCH_TERMS["symbolic_terms"]) and any(a in lowered for a in WATCH_TERMS["authority_terms"]):
            findings.append(Finding(
                category="symbolic_authority_collision",
                severity="high",
                path=rel,
                line=idx,
                excerpt=line.strip()[:220],
                recommendation="Verify symbolic context is supplemental only and not load-bearing for authority.",
            ))
        if "summary_only" in lowered or "pending_wiring" in lowered or "missing_input" in lowered:
            findings.append(Finding(
                category="implementation_gap_marker",
                severity="medium",
                path=rel,
                line=idx,
                excerpt=line.strip()[:220],
                recommendation="Resolve or keep explicitly listed as known uncertainty.",
            ))
    return findings


def git_recent_commits(root: Path, n: int = 8) -> List[str]:
    try:
        proc = subprocess.run(["git", "log", "--oneline", f"-{n}"], cwd=str(root), capture_output=True, text=True, check=True)
        return proc.stdout.strip().splitlines()
    except Exception:
        return []


def build_report() -> Dict[str, object]:
    root = repo_root()
    findings: List[Finding] = []
    for path in iter_files(root):
        findings.extend(scan_file(root, path))

    counts: Dict[str, int] = {}
    for finding in findings:
        counts[finding.category] = counts.get(finding.category, 0) + 1

    report = {
        "schema_version": "meta-pulse-r1",
        "generated_at": utc_now(),
        "repo_root": str(root),
        "recent_commits": git_recent_commits(root),
        "finding_counts": counts,
        "findings": [asdict(f) for f in findings[:200]],
        "principle": "Verifiable systems must audit their own failure modes before expanding claims.",
        "next_action": "Convert repeated implementation_gap_marker findings into tracked issues or automated checks.",
    }
    return report


def write_report(report: Dict[str, object]) -> Dict[str, str]:
    root = repo_root()
    out_dir = root / "artifacts" / "meta_pulse"
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "latest_report.json"
    md_path = out_dir / "latest_report.md"
    json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    lines = [
        "# Meta-Pulse Report",
        "",
        f"Generated: {report['generated_at']}",
        "",
        "## Finding Counts",
        "",
    ]
    for key, value in sorted((report.get("finding_counts") or {}).items()):
        lines.append(f"- {key}: {value}")
    lines.extend([
        "",
        "## Principle",
        "",
        str(report.get("principle")),
        "",
        "## Next Action",
        "",
        str(report.get("next_action")),
        "",
    ])
    md_path.write_text("\n".join(lines), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path)}


if __name__ == "__main__":
    result = build_report()
    paths = write_report(result)
    print(json.dumps({"paths": paths, "finding_counts": result.get("finding_counts", {})}, indent=2))

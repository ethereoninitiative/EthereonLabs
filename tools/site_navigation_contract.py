from __future__ import annotations

from pathlib import Path
from typing import List, Tuple
import re


ARRAY_START_TEMPLATE = r"{group_name}:\s*\["
PAIR_RE = re.compile(r"\['([^']+)',\s*'((?:\\'|[^'])+)'\]")


def extract_array_block(nav_text: str, group_name: str) -> str:
    """Return the body of one array in site-navigation-data.js."""
    start_match = re.search(ARRAY_START_TEMPLATE.format(group_name=re.escape(group_name)), nav_text)
    if not start_match:
        raise ValueError(f"navigation group not found: {group_name}")

    start = start_match.end()
    next_match = re.search(r"\n\s*[A-Za-z_$][\w$]*:\s*\[", nav_text[start:])
    end = start + next_match.start() if next_match else nav_text.find("\n};", start)
    if end == -1:
        end = len(nav_text)
    return nav_text[start:end]


def extract_nav_pairs(nav_text: str, group_name: str) -> List[Tuple[str, str]]:
    body = extract_array_block(nav_text, group_name)
    pairs = [
        (href, label.replace("\\'", "'"))
        for href, label in PAIR_RE.findall(body)
    ]
    if not pairs:
        raise ValueError(f"navigation group contains no parseable pairs: {group_name}")
    return pairs


def load_primary_navigation(root: Path) -> List[Tuple[str, str]]:
    """Load the ordered canonical primary navigation contract."""
    nav_path = root / "assets" / "js" / "site-navigation-data.js"
    nav_text = nav_path.read_text(encoding="utf-8")
    pairs = extract_nav_pairs(nav_text, "primary")

    hrefs = [href for href, _ in pairs]
    labels = [label for _, label in pairs]
    if len(hrefs) != len(set(hrefs)):
        raise ValueError("primary navigation contains duplicate hrefs")
    if len(labels) != len(set(labels)):
        raise ValueError("primary navigation contains duplicate labels")

    missing_targets = [href for href in hrefs if not (root / href).is_file()]
    if missing_targets:
        raise ValueError(
            "primary navigation references missing root HTML targets: "
            + ", ".join(missing_targets)
        )
    return pairs

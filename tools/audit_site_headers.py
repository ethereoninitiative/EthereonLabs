from __future__ import annotations

from pathlib import Path
import re

CANONICAL_PRIMARY = [
    ("index.html", "Home"),
    ("lumina.html", "Lumina"),
    ("continuity.html", "Continuity"),
    ("roadmap.html", "Roadmap"),
    ("harmonics.html", "Harmonics"),
    ("rse.html", "RSE"),
    ("rse-whitepaper.html", "The Spiral"),
    ("explore.html", "Explore"),
    ("chamber.html", "Chamber"),
    ("about.html", "About"),
    ("contact.html", "Contact"),
]

NAV_RE = re.compile(r'<nav[^>]*class="[^"]*nav-links[^"]*"[^>]*>(.*?)</nav>', re.DOTALL)
LINK_RE = re.compile(r'<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>', re.DOTALL)


def extract_nav_links(html: str):
    match = NAV_RE.search(html)
    if not match:
        return None
    return [(href, re.sub(r"<.*?>", "", label).strip()) for href, label in LINK_RE.findall(match.group(1))]


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    html_files = sorted(path for path in root.glob("*.html") if path.is_file())
    drifted = []
    missing = []
    for path in html_files:
        links = extract_nav_links(path.read_text(encoding="utf-8"))
        if links is None:
            missing.append(path.name)
            continue
        if links != CANONICAL_PRIMARY:
            drifted.append((path.name, links))

    print("Site header canonical audit")
    print(f"html_files={len(html_files)}")
    print(f"missing_nav={len(missing)}")
    print(f"drifted_nav={len(drifted)}")
    if missing:
        print("\nMissing nav:")
        for name in missing:
            print(f"- {name}")
    if drifted:
        print("\nDrifted nav:")
        for name, links in drifted:
            rendered = ", ".join(label for _, label in links)
            print(f"- {name}: {rendered}")
    return 1 if missing or drifted else 0


if __name__ == "__main__":
    raise SystemExit(main())

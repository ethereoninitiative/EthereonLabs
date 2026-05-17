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

NAV_RE = re.compile(r'<nav([^>]*)class="([^"]*\bnav-links\b[^"]*)"([^>]*)>.*?</nav>', re.DOTALL)
BRAND_STRONG_RE = re.compile(r'<span class="brand-text"><strong>.*?</strong><span>', re.DOTALL)


def canonical_nav_for(page_name: str) -> str:
    parts = []
    for href, label in CANONICAL_PRIMARY:
        current = ' aria-current="page"' if href == page_name else ""
        parts.append(f'<a href="{href}"{current}>{label}</a>')
    return '<nav class="nav-links" aria-label="Primary">' + ''.join(parts) + '</nav>'


def canonicalize_html(path: Path) -> bool:
    original = path.read_text(encoding="utf-8")
    html = original
    page_name = path.name
    html = NAV_RE.sub(canonical_nav_for(page_name), html, count=1)
    html = BRAND_STRONG_RE.sub(
        '<span class="brand-text"><strong><span class="brand-cap">E</span>THEREON<span class="brand-cap brand-cap-l">L</span>ABS</strong><span>',
        html,
        count=1,
    )
    if html != original:
        path.write_text(html, encoding="utf-8")
        return True
    return False


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    changed = []
    for path in sorted(root.glob("*.html")):
        if canonicalize_html(path):
            changed.append(path.name)
    print("Canonicalized site headers")
    print(f"changed={len(changed)}")
    for name in changed:
        print(f"- {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

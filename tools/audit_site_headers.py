from __future__ import annotations

from pathlib import Path
import re

from site_navigation_contract import load_primary_navigation

INTENTIONAL_NO_NAV_PAGES = {
    "artist-spencer.html",
    "lumina-dashboard-restored.html",
    "revelation.html",
}

NAV_RE = re.compile(r'<nav[^>]*class="[^"]*nav-links[^"]*"[^>]*>(.*?)</nav>', re.DOTALL)
LINK_RE = re.compile(r'<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>', re.DOTALL)


def extract_nav_links(html: str):
    match = NAV_RE.search(html)
    if not match:
        return None
    return [
        (href, re.sub(r"<.*?>", "", label).strip())
        for href, label in LINK_RE.findall(match.group(1))
    ]


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    try:
        canonical_primary = load_primary_navigation(root)
    except (OSError, ValueError) as error:
        print("Site header canonical audit")
        print(f"navigation_contract_error={error}")
        return 1

    html_files = sorted(path for path in root.glob("*.html") if path.is_file())
    drifted = []
    missing = []
    skipped = []

    for path in html_files:
        links = extract_nav_links(path.read_text(encoding="utf-8"))
        if links is None:
            if path.name in INTENTIONAL_NO_NAV_PAGES:
                skipped.append(path.name)
            else:
                missing.append(path.name)
            continue
        if links != canonical_primary:
            drifted.append((path.name, links))

    print("Site header canonical audit")
    print("canonical_source=assets/js/site-navigation-data.js")
    print(f"canonical_primary_links={len(canonical_primary)}")
    print(f"html_files={len(html_files)}")
    print(f"intentional_no_nav={len(skipped)}")
    print(f"missing_nav={len(missing)}")
    print(f"drifted_nav={len(drifted)}")

    if skipped:
        print("\nIntentional no-nav pages:")
        for name in skipped:
            print(f"- {name}")
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

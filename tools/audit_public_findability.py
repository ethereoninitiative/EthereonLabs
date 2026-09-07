from __future__ import annotations

from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

BASE = "https://ethereonlabs.com"
FORBIDDEN_DIRS = {
    "LuminaOS",
    "artifacts",
    "chamber-app",
    "deploy",
    "docs",
    "metadata",
    "public",
    "research",
    "scripts",
    "studio",
    "tools",
}


def meta_robots(html: str) -> str:
    match = re.search(r'<meta\s+name=["\']robots["\']\s+content=["\']([^"\']+)["\']', html, flags=re.I)
    return match.group(1).lower() if match else ""


def canonical(html: str) -> str:
    match = re.search(r'<link\s+rel=["\']canonical["\']\s+href=["\']([^"\']+)["\']', html, flags=re.I)
    return match.group(1) if match else ""


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def main() -> int:
    site = Path(sys.argv[1] if len(sys.argv) > 1 else "_site").resolve()
    errors: list[str] = []

    if not site.exists():
        print(f"Missing prepared site: {site}")
        return 1

    for dirname in FORBIDDEN_DIRS:
        if (site / dirname).exists():
            fail(errors, f"forbidden repository surface published: /{dirname}/")

    for required in ("index.html", "robots.txt", "sitemap.xml", "llms.txt", ".nojekyll", "CNAME"):
        if not (site / required).exists():
            fail(errors, f"missing public file: {required}")

    root_source_like = [p.name for p in site.iterdir() if p.is_file() and p.suffix.lower() in {".md", ".py", ".sql", ".ts", ".yml", ".yaml"}]
    if root_source_like:
        fail(errors, "source/document files leaked at public root: " + ", ".join(sorted(root_source_like)))

    indexable_urls: set[str] = set()
    for path in sorted(site.glob("*.html")):
        html = path.read_text(encoding="utf-8")
        robots = meta_robots(html)
        canon = canonical(html)
        expected = f"{BASE}/" if path.name == "index.html" else f"{BASE}/{path.name}"
        if not canon:
            fail(errors, f"missing canonical: {path.name}")
        if "noindex" not in robots:
            if canon != expected:
                fail(errors, f"canonical mismatch: {path.name}: {canon!r} != {expected!r}")
            if "index" not in robots or "follow" not in robots:
                fail(errors, f"indexable page lacks explicit index,follow: {path.name}")
            if "application/ld+json" not in html:
                fail(errors, f"indexable page lacks structured data: {path.name}")
            indexable_urls.add(expected)
        if path.name != "404.html" and "data-secondary-footer-links" not in html and "noindex" not in robots:
            fail(errors, f"crawlable secondary footer links missing: {path.name}")

    app_checks = {
        site / "app" / "index.html": f"{BASE}/app/",
        site / "app" / "runtime.html": f"{BASE}/app/runtime.html",
    }
    for path, expected in app_checks.items():
        if not path.exists():
            fail(errors, f"missing public app page: {path.relative_to(site)}")
            continue
        html = path.read_text(encoding="utf-8")
        if canonical(html) != expected:
            fail(errors, f"app canonical mismatch: {path.relative_to(site)}")
        if "noindex" in meta_robots(html):
            fail(errors, f"app page unexpectedly noindex: {path.relative_to(site)}")
        indexable_urls.add(expected)

    sitemap_path = site / "sitemap.xml"
    if sitemap_path.exists():
        try:
            tree = ET.parse(sitemap_path)
            ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
            sitemap_urls = {node.text.strip() for node in tree.findall("sm:url/sm:loc", ns) if node.text}
        except Exception as exc:
            fail(errors, f"invalid sitemap.xml: {exc}")
            sitemap_urls = set()
        missing = indexable_urls - sitemap_urls
        extra = sitemap_urls - indexable_urls
        if missing:
            fail(errors, "indexable URLs missing from sitemap: " + ", ".join(sorted(missing)))
        if extra:
            fail(errors, "sitemap contains non-indexable/unknown URLs: " + ", ".join(sorted(extra)))
        for url in sitemap_urls:
            if url != f"{BASE}/" and not (url.endswith(".html") or url == f"{BASE}/app/"):
                fail(errors, f"non-final/extensionless URL in sitemap: {url}")

    robots = (site / "robots.txt").read_text(encoding="utf-8") if (site / "robots.txt").exists() else ""
    if "Sitemap: https://ethereonlabs.com/sitemap.xml" not in robots:
        fail(errors, "robots.txt does not advertise canonical sitemap")
    if re.search(r"(?im)^\s*Disallow:\s*/\s*$", robots):
        fail(errors, "robots.txt blocks the entire site")

    if errors:
        print("Findability audit FAILED")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Findability audit PASSED")
    print(f"indexable_urls={len(indexable_urls)}")
    print("public surface excludes repository implementation/canon directories")
    print("canonicals, structured data, raw-HTML discovery links, sitemap, robots aligned")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

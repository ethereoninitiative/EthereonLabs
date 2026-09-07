from __future__ import annotations

from datetime import date
from html import unescape
from pathlib import Path
import json
import re
import shutil

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "_site"
BASE = "https://ethereonlabs.com"

PUBLIC_DIRS = ("assets", "app", "data")
LEGACY_ALIAS_DIRS = ("about", "lumina")
ROOT_FILES = (".nojekyll", "CNAME", "robots.txt", "sitemap.xml", "llms.txt")
INDEXNOW_KEY = "7d4b3f1c9a2e6d8f0b5c4a7e1f3d9b62"

SEO_TITLES = {
    "index.html": "EthereonLabs | Lumina Continuity Software for Complex Work",
    "lumina.html": "Lumina Continuity Workspace | EthereonLabs",
    "how-lumina-works.html": "How Lumina Works | Governed AI Continuity | EthereonLabs",
    "build.html": "What EthereonLabs Is Building | Lumina Continuity Software",
    "prototype.html": "Lumina Prototype & Harbor | EthereonLabs",
    "roadmap.html": "Lumina Roadmap | EthereonLabs",
    "continuity.html": "AI Continuity & Project Return | EthereonLabs",
    "about.html": "About EthereonLabs | Lumina & Continuity Research",
    "explore.html": "EthereonLabs Research | Continuity, RSE & Harmonics",
    "principles.html": "EthereonLabs Principles | Human-Controlled AI Systems",
    "realm.html": "EthereonLabs Realm | Continuity System Architecture",
    "rse.html": "Recursive Symbolic Emergence (RSE) | EthereonLabs",
    "rse-whitepaper.html": "The Referential Spiral Equation | EthereonLabs",
    "rse-companion.html": "RSE Companion | EthereonLabs",
    "harmonics.html": "Harmonics Research | EthereonLabs",
    "terrarium.html": "Lumina Terrarium | Continuity Research | EthereonLabs",
    "embodiment.html": "Lumina Embodiment Research | EthereonLabs",
    "chamber.html": "Lumina Chamber | Governed Advisory Research | EthereonLabs",
    "lumina-dashboard.html": "Lumina Dashboard | Continuity State Prototype",
    "lumina-weather.html": "Lumina Weather | Continuity Diagnostics | EthereonLabs",
    "specimen.html": "Lumina Specimen | EthereonLabs",
    "lexicon.html": "EthereonLabs Lexicon | Lumina, RSE & Continuity",
    "faq.html": "EthereonLabs FAQ | Lumina Continuity Workspace",
    "updates.html": "EthereonLabs Updates | Lumina Development",
    "contact.html": "Contact EthereonLabs | Lumina Continuity Software",
}

SECONDARY_LINKS = (
    ("how-lumina-works.html", "How Lumina works"),
    ("principles.html", "Principles"),
    ("realm.html", "Realm"),
    ("lumina-dashboard.html", "Dashboard"),
    ("harmonics.html", "Harmonics"),
    ("rse.html", "RSE"),
    ("specimen.html", "Specimen"),
    ("lexicon.html", "Lexicon"),
    ("faq.html", "FAQ"),
    ("updates.html", "Updates"),
)

ROBOTS_INDEX = "index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1"
ROBOTS_NOINDEX = "noindex,follow"


def replace_or_insert(html: str, pattern: str, replacement: str, anchor: str = "</head>") -> str:
    if re.search(pattern, html, flags=re.I | re.S):
        return re.sub(pattern, replacement, html, count=1, flags=re.I | re.S)
    return html.replace(anchor, f"  {replacement}\n{anchor}", 1)


def meta_content(html: str, name: str) -> str:
    match = re.search(
        rf'<meta\s+name=["\']{re.escape(name)}["\']\s+content=["\']([^"\']*)["\']\s*/?>',
        html,
        flags=re.I,
    )
    return unescape(match.group(1)).strip() if match else ""


def title_text(html: str) -> str:
    match = re.search(r"<title>(.*?)</title>", html, flags=re.I | re.S)
    return unescape(re.sub(r"\s+", " ", match.group(1)).strip()) if match else "EthereonLabs"


def canonical_for_top_level(path: Path) -> str:
    return f"{BASE}/" if path.name == "index.html" else f"{BASE}/{path.name}"


def page_type(name: str) -> str:
    if name == "about.html":
        return "AboutPage"
    if name == "contact.html":
        return "ContactPage"
    if name == "explore.html":
        return "CollectionPage"
    return "WebPage"


def common_graph(canonical: str, title: str, description: str, name: str) -> dict:
    graph = [
        {
            "@type": "Organization",
            "@id": f"{BASE}/#organization",
            "name": "EthereonLabs",
            "url": f"{BASE}/",
            "description": "EthereonLabs develops Lumina, an adaptive continuity workspace for returning to complex creative and technical work with context, governance, and inspectable records intact.",
            "sameAs": ["https://github.com/ethereoninitiative/EthereonLabs"],
            "knowsAbout": [
                "Lumina",
                "continuity software",
                "human-AI collaboration",
                "governed AI systems",
                "project context restoration",
                "Recursive Symbolic Emergence",
            ],
        },
        {
            "@type": page_type(name),
            "@id": f"{canonical}#webpage",
            "url": canonical,
            "name": title,
            "description": description,
            "isPartOf": {"@id": f"{BASE}/#website"},
            "about": {"@id": f"{BASE}/#organization"},
            "inLanguage": "en-US",
        },
    ]
    if name == "index.html":
        graph.insert(
            1,
            {
                "@type": "WebSite",
                "@id": f"{BASE}/#website",
                "url": f"{BASE}/",
                "name": "EthereonLabs",
                "publisher": {"@id": f"{BASE}/#organization"},
                "inLanguage": "en-US",
            },
        )
    if name in {"index.html", "lumina.html", "prototype.html", "how-lumina-works.html"}:
        graph.append(
            {
                "@type": "SoftwareApplication",
                "@id": f"{BASE}/lumina.html#software",
                "name": "Lumina",
                "applicationCategory": "ProductivityApplication",
                "operatingSystem": "Web, Windows developer preview",
                "url": f"{BASE}/lumina.html",
                "description": "Lumina is an adaptive continuity workspace under active development for restoring bounded project context, governing next actions, and leaving inspectable checkpoints and receipts.",
                "publisher": {"@id": f"{BASE}/#organization"},
                "isAccessibleForFree": True,
            }
        )
    return {"@context": "https://schema.org", "@graph": graph}


def patch_top_level_html(path: Path) -> bool:
    html = path.read_text(encoding="utf-8")
    canonical = canonical_for_top_level(path)
    original_robots = meta_content(html, "robots").lower()
    has_refresh = bool(re.search(r'<meta[^>]+http-equiv=["\']refresh["\']', html, flags=re.I))
    noindex = "noindex" in original_robots or has_refresh

    if path.name in SEO_TITLES:
        html = re.sub(r"<title>.*?</title>", f"<title>{SEO_TITLES[path.name]}</title>", html, count=1, flags=re.I | re.S)

    html = replace_or_insert(
        html,
        r'<link\s+rel=["\']canonical["\'][^>]*>',
        f'<link rel="canonical" href="{canonical}" />',
    )
    html = replace_or_insert(
        html,
        r'<meta\s+property=["\']og:url["\'][^>]*>',
        f'<meta property="og:url" content="{canonical}" />',
    )
    html = replace_or_insert(
        html,
        r'<meta\s+name=["\']robots["\'][^>]*>',
        f'<meta name="robots" content="{ROBOTS_NOINDEX if noindex else ROBOTS_INDEX}" />',
    )
    html = replace_or_insert(
        html,
        r'<meta\s+name=["\']author["\'][^>]*>',
        '<meta name="author" content="EthereonLabs" />',
    )
    html = replace_or_insert(
        html,
        r'<link\s+rel=["\']alternate["\']\s+type=["\']text/plain["\'][^>]*>',
        f'<link rel="alternate" type="text/plain" href="{BASE}/llms.txt" title="EthereonLabs machine-readable overview" />',
    )

    # Remove a prior generated graph if this script is run repeatedly.
    html = re.sub(
        r'\s*<script\s+type=["\']application/ld\+json["\']\s+data-ethereon-seo>.*?</script>',
        "",
        html,
        flags=re.I | re.S,
    )
    description = meta_content(html, "description") or "EthereonLabs develops Lumina, an adaptive continuity workspace for complex creative and technical work."
    graph = json.dumps(common_graph(canonical, title_text(html), description, path.name), ensure_ascii=False, separators=(",", ":"))
    html = html.replace("</head>", f'  <script type="application/ld+json" data-ethereon-seo>{graph}</script>\n</head>', 1)

    # Make the existing JS-enhanced secondary footer links crawlable in raw HTML too.
    if "data-secondary-footer-links" not in html and "</footer>" in html:
        links = "".join(f'<a href="{href}">{label}</a>' for href, label in SECONDARY_LINKS)
        nav = f'<nav class="footer-secondary-links" data-secondary-footer-links aria-label="Explore EthereonLabs">{links}</nav>'
        html = html.replace("</footer>", f"{nav}</footer>", 1)

    path.write_text(html, encoding="utf-8")
    return not noindex


def patch_app_page(path: Path, canonical: str, title: str | None = None) -> None:
    html = path.read_text(encoding="utf-8")
    if title:
        html = re.sub(r"<title>.*?</title>", f"<title>{title}</title>", html, count=1, flags=re.I | re.S)
    html = replace_or_insert(html, r'<link\s+rel=["\']canonical["\'][^>]*>', f'<link rel="canonical" href="{canonical}" />')
    html = replace_or_insert(html, r'<meta\s+name=["\']robots["\'][^>]*>', f'<meta name="robots" content="{ROBOTS_INDEX}" />')
    html = replace_or_insert(html, r'<meta\s+property=["\']og:url["\'][^>]*>', f'<meta property="og:url" content="{canonical}" />')
    description = meta_content(html, "description") or "A public Lumina continuity prototype from EthereonLabs."
    graph = {
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": "Lumina Harbor" if path.name == "index.html" else "Harbor Light — Lumina Runtime",
        "url": canonical,
        "applicationCategory": "ProductivityApplication",
        "description": description,
        "publisher": {"@type": "Organization", "name": "EthereonLabs", "url": f"{BASE}/"},
        "isAccessibleForFree": True,
    }
    html = re.sub(r'\s*<script\s+type=["\']application/ld\+json["\']\s+data-ethereon-seo>.*?</script>', "", html, flags=re.I | re.S)
    html = html.replace("</head>", f'  <script type="application/ld+json" data-ethereon-seo>{json.dumps(graph, ensure_ascii=False, separators=(",", ":"))}</script>\n</head>', 1)
    path.write_text(html, encoding="utf-8")


def patch_legacy_alias(path: Path, target: str) -> None:
    html = path.read_text(encoding="utf-8")
    html = replace_or_insert(html, r'<link\s+rel=["\']canonical["\'][^>]*>', f'<link rel="canonical" href="{BASE}/{target}" />')
    html = replace_or_insert(html, r'<meta\s+name=["\']robots["\'][^>]*>', f'<meta name="robots" content="{ROBOTS_NOINDEX}" />')
    path.write_text(html, encoding="utf-8")


def write_sitemap(indexable_top_level: list[str]) -> None:
    urls = [f"{BASE}/"]
    urls.extend(f"{BASE}/{name}" for name in indexable_top_level if name != "index.html")
    urls.extend((f"{BASE}/app/", f"{BASE}/app/runtime.html"))
    # Stable order: homepage, key product pages first, then alphabetic remainder.
    preferred = [
        f"{BASE}/",
        f"{BASE}/lumina.html",
        f"{BASE}/how-lumina-works.html",
        f"{BASE}/build.html",
        f"{BASE}/prototype.html",
        f"{BASE}/roadmap.html",
        f"{BASE}/continuity.html",
        f"{BASE}/about.html",
        f"{BASE}/explore.html",
        f"{BASE}/app/",
        f"{BASE}/app/runtime.html",
    ]
    ordered = []
    seen = set()
    for url in preferred + sorted(urls):
        if url in urls and url not in seen:
            ordered.append(url)
            seen.add(url)
    lastmod = date.today().isoformat()
    body = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for url in ordered:
        body.append(f"  <url><loc>{url}</loc><lastmod>{lastmod}</lastmod></url>")
    body.append("</urlset>")
    (OUT / "sitemap.xml").write_text("\n".join(body) + "\n", encoding="utf-8")


def write_404() -> None:
    html = f'''<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8" /><meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Not Found | EthereonLabs</title><meta name="robots" content="noindex,follow" /><link rel="canonical" href="{BASE}/404.html" />
<link rel="stylesheet" href="assets/css/styles.css" /></head><body><main class="section"><div class="container feature-callout"><small>404</small><h1>This route is not part of the current public surface.</h1><p class="section-copy">The EthereonLabs repository evolves quickly. The current public paths are collected on the homepage and Research page.</p><div class="hero-actions"><a class="button primary" href="/">Return to EthereonLabs</a><a class="button secondary" href="/explore.html">Open Research</a></div></div></main></body></html>'''
    (OUT / "404.html").write_text(html, encoding="utf-8")


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()

    for path in sorted(ROOT.glob("*.html")):
        shutil.copy2(path, OUT / path.name)

    for name in ROOT_FILES:
        source = ROOT / name
        if source.exists():
            shutil.copy2(source, OUT / name)

    key_source = ROOT / f"{INDEXNOW_KEY}.txt"
    if key_source.exists():
        shutil.copy2(key_source, OUT / key_source.name)

    for dirname in PUBLIC_DIRS:
        source = ROOT / dirname
        if source.exists():
            shutil.copytree(source, OUT / dirname)

    # README files belong to the repository, not the search-facing application surface.
    app_readme = OUT / "app" / "README.md"
    if app_readme.exists():
        app_readme.unlink()

    for dirname in LEGACY_ALIAS_DIRS:
        source = ROOT / dirname / "index.html"
        if source.exists():
            target_dir = OUT / dirname
            target_dir.mkdir(exist_ok=True)
            shutil.copy2(source, target_dir / "index.html")

    indexable = []
    for path in sorted(OUT.glob("*.html")):
        if patch_top_level_html(path):
            indexable.append(path.name)

    if (OUT / "app" / "index.html").exists():
        patch_app_page(OUT / "app" / "index.html", f"{BASE}/app/", "Lumina Harbor | Local-First Continuity Prototype")
    if (OUT / "app" / "runtime.html").exists():
        patch_app_page(OUT / "app" / "runtime.html", f"{BASE}/app/runtime.html", "Harbor Light | Lumina Runtime Witness")

    if (OUT / "about" / "index.html").exists():
        patch_legacy_alias(OUT / "about" / "index.html", "about.html")
    if (OUT / "lumina" / "index.html").exists():
        patch_legacy_alias(OUT / "lumina" / "index.html", "lumina.html")

    write_sitemap(indexable)
    write_404()

    print("Prepared curated EthereonLabs public artifact")
    print(f"top_level_html={len(list(OUT.glob('*.html')))}")
    print(f"indexable_top_level={len(indexable)}")
    print("published_dirs=" + ",".join(PUBLIC_DIRS + LEGACY_ALIAS_DIRS))
    print("excluded_repo_surfaces=LuminaOS,artifacts,chamber-app,deploy,docs,metadata,public,research,scripts,studio,tools,root source/docs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

"""Sea Trials: EthereonLabs public website surface r1.

Static validator for the public site after the clarity/navigation/footer pass.
It checks the kinds of barnacles that recently appeared:
- RSE naming drift
- missing essential public nav links
- stale Explore labeling on rendered-helper source
- internal .html links pointing at missing files
- shared footer/nav behavior drifting away from canonical data

Run from the repository root:
    python scripts/sea_trials_website_public_surface_r1.py
"""

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Set
import json
import re

ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "_site_trials"
REPORT_PATH = REPORT_DIR / "website_public_surface_r1_report.json"

REQUIRED_PRIMARY_LABELS = {
    "Home",
    "Lumina",
    "What we're building",
    "Prototype",
    "Roadmap",
    "Continuity",
    "The Spiral",
    "Chamber",
    "About",
    "Contact",
    "Research",
}

REQUIRED_SECONDARY_LABELS = {
    "Principles",
    "Realm",
    "Dashboard",
    "Harmonics",
    "RSE",
    "Specimen",
    "Lexicon",
    "FAQ",
    "Updates",
}

EXPECTED_PRIMARY_TARGETS = {
    "index.html",
    "lumina.html",
    "build.html",
    "prototype.html",
    "roadmap.html",
    "continuity.html",
    "rse-whitepaper.html",
    "chamber.html",
    "about.html",
    "contact.html",
    "explore.html",
}

EXPECTED_SECONDARY_TARGETS = {
    "principles.html",
    "realm.html",
    "lumina-dashboard.html",
    "harmonics.html",
    "rse.html",
    "specimen.html",
    "lexicon.html",
    "faq.html",
    "updates.html",
}

EXTERNAL_PREFIXES = (
    "http://",
    "https://",
    "mailto:",
    "tel:",
    "#",
    "javascript:",
)


@dataclass
class Check:
    name: str
    passed: bool
    details: Dict[str, object]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def top_level_html_files() -> List[Path]:
    return sorted(path for path in ROOT.glob("*.html") if path.is_file())


def extract_array_block(nav_text: str, group_name: str) -> str:
    start_match = re.search(rf"{group_name}:\s*\[", nav_text)
    if not start_match:
        return ""
    start = start_match.end()
    next_match = re.search(r"\n\s*[A-Za-z_$][\w$]*:\s*\[", nav_text[start:])
    end = start + next_match.start() if next_match else nav_text.find("\n};", start)
    if end == -1:
        end = len(nav_text)
    return nav_text[start:end]


def extract_nav_pairs(nav_text: str, group_name: str) -> Dict[str, str]:
    body = extract_array_block(nav_text, group_name)
    pairs = re.findall(r"\['([^']+)',\s*'((?:\\'|[^'])+)'\]", body)
    return {label.replace("\\'", "'"): href for href, label in pairs}


def check_navigation_data() -> Check:
    nav_path = ROOT / "assets" / "js" / "site-navigation-data.js"
    nav = read(nav_path)
    primary = extract_nav_pairs(nav, "primary")
    secondary = extract_nav_pairs(nav, "secondaryFooter")
    primary_labels = set(primary.keys())
    secondary_labels = set(secondary.keys())
    primary_targets = set(primary.values())
    secondary_targets = set(secondary.values())
    details = {
        "missing_primary_labels": sorted(REQUIRED_PRIMARY_LABELS - primary_labels),
        "missing_secondary_labels": sorted(REQUIRED_SECONDARY_LABELS - secondary_labels),
        "missing_primary_targets": sorted(EXPECTED_PRIMARY_TARGETS - primary_targets),
        "missing_secondary_targets": sorted(EXPECTED_SECONDARY_TARGETS - secondary_targets),
        "primary_count": len(primary_labels),
        "secondary_count": len(secondary_labels),
    }
    return Check(
        "navigation_data_has_required_public_doors",
        not any(v for k, v in details.items() if k.startswith("missing_")),
        details,
    )


def check_shared_site_js() -> Check:
    site_path = ROOT / "assets" / "js" / "site.js"
    js = read(site_path)
    required_fragments = [
        "enhancePrimaryNav",
        "enhanceFooter",
        "normalizeLegacyExploreLabels",
        "installSoundToggle",
        "footer-brand-block",
        "join('')",
        "← Back to Research",
        "Research and deeper system",
    ]
    forbidden_fragments = [
        "join(' · ')",
    ]
    details = {
        "missing_required_fragments": [fragment for fragment in required_fragments if fragment not in js],
        "present_forbidden_fragments": [fragment for fragment in forbidden_fragments if fragment in js],
    }
    return Check(
        "shared_site_js_renders_canonical_nav_footer_and_sound",
        not details["missing_required_fragments"] and not details["present_forbidden_fragments"],
        details,
    )


def check_rse_naming() -> Check:
    offenders: List[str] = []
    for path in top_level_html_files():
        text = read(path)
        if "Recursive Spiral Equation" in text:
            offenders.append(str(path.relative_to(ROOT)))
    rse_text = read(ROOT / "rse.html") if (ROOT / "rse.html").exists() else ""
    details = {
        "recursive_name_offenders": offenders,
        "rse_page_has_referential_name": "Referential Spiral Equation" in rse_text,
    }
    return Check("rse_uses_referential_name", not offenders and details["rse_page_has_referential_name"], details)


def normalize_internal_href(href: str) -> str | None:
    href = href.strip()
    if not href or href.startswith(EXTERNAL_PREFIXES):
        return None
    href = href.split("#", 1)[0].split("?", 1)[0]
    if not href.endswith(".html"):
        return None
    return href


def check_internal_links() -> Check:
    existing: Set[str] = {path.name for path in top_level_html_files()}
    existing.update({"index.html"})
    missing: Dict[str, List[str]] = {}
    href_pattern = re.compile(r"href=\"([^\"]+)\"")
    for path in top_level_html_files():
        text = read(path)
        for raw_href in href_pattern.findall(text):
            href = normalize_internal_href(raw_href)
            if href is None:
                continue
            target_name = Path(href).name
            if target_name not in existing:
                missing.setdefault(str(path.relative_to(ROOT)), []).append(href)
    details = {
        "missing_internal_html_links": missing,
        "html_file_count": len(existing),
    }
    return Check("internal_html_links_resolve", not missing, details)


def check_footer_css_no_pseudo_only_brand() -> Check:
    css = read(ROOT / "assets" / "css" / "styles.css")
    js = read(ROOT / "assets" / "js" / "site.js")
    details = {
        "has_footer_panel": ".footer-row" in css and "border-radius: 24px" in css,
        "has_mobile_footer_rules": "footer-secondary-links" in css and "@media (max-width: 760px)" in css,
        "has_old_pseudo_footer_text": ".footer-row > div:first-child::before" in css or ".footer-row > div:first-child::after" in css,
        "drydock_js_overrides_old_pseudo_footer_text": "data-ethereon-drydock-styles" in js,
        "footer_brand_is_real_dom": "footer-brand-block" in js and "footer-tagline" in js,
    }
    passed = (
        details["has_footer_panel"]
        and details["has_mobile_footer_rules"]
        and details["drydock_js_overrides_old_pseudo_footer_text"]
        and details["footer_brand_is_real_dom"]
    )
    return Check("footer_bottom_surface_has_panel_and_render_override", passed, details)


def run() -> Dict[str, object]:
    checks = [
        check_navigation_data(),
        check_shared_site_js(),
        check_rse_naming(),
        check_internal_links(),
        check_footer_css_no_pseudo_only_brand(),
    ]
    report = {
        "suite": "Sea Trials Website Public Surface r1",
        "passed": all(check.passed for check in checks),
        "checks": [asdict(check) for check in checks],
        "report_path": str(REPORT_PATH.relative_to(ROOT)),
    }
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))

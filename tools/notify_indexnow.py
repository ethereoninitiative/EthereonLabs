from __future__ import annotations

from pathlib import Path
import json
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET

BASE = "https://ethereonlabs.com"
KEY = "7d4b3f1c9a2e6d8f0b5c4a7e1f3d9b62"
ENDPOINT = "https://api.indexnow.org/indexnow"


def canonical_urls(sitemap: Path) -> list[str]:
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    root = ET.parse(sitemap).getroot()
    return [node.text.strip() for node in root.findall("sm:url/sm:loc", ns) if node.text]


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    urls = canonical_urls(root / "sitemap.xml")
    payload = json.dumps(
        {
            "host": "ethereonlabs.com",
            "key": KEY,
            "keyLocation": f"{BASE}/{KEY}.txt",
            "urlList": urls,
        },
        separators=(",", ":"),
    ).encode("utf-8")
    request = urllib.request.Request(
        ENDPOINT,
        data=payload,
        headers={"Content-Type": "application/json; charset=utf-8", "User-Agent": "EthereonLabs-IndexNow/1.0"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            status = response.status
            body = response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as error:
        status = error.code
        body = error.read().decode("utf-8", errors="replace")
    except Exception as error:
        print(f"IndexNow request failed: {error}")
        return 1

    print(f"IndexNow HTTP {status}; submitted_urls={len(urls)}")
    if body:
        print(body[:1000])
    return 0 if status in {200, 202} else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Compile the staged Lumina Desktop Beta R1 Windows setup package."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess


BUILD_ID = "lumina-windows-installer-build-r1"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def find_iscc(explicit: str | None) -> Path:
    candidates: list[Path] = []
    if explicit:
        candidates.append(Path(explicit))
    for root in (Path("C:/Program Files (x86)"), Path("C:/Program Files")):
        candidates.extend(
            [
                root / "Inno Setup 6" / "ISCC.exe",
                root / "Inno Setup 7" / "ISCC.exe",
            ]
        )
    for candidate in candidates:
        if candidate.is_file():
            return candidate.resolve()
    raise FileNotFoundError("Inno Setup command-line compiler was not found")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--payload-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--iscc")
    args = parser.parse_args()

    source_root = args.source_root.resolve()
    payload_root = args.payload_root.resolve()
    output_root = args.output_root.resolve()
    output_root.mkdir(parents=True, exist_ok=True)

    if not (payload_root / "EthereonLabs").is_dir():
        raise FileNotFoundError("staged Lumina release payload is missing")

    definition = source_root / "deploy" / "windows_desktop_r1" / "LuminaDesktopBetaR1.iss"
    subprocess.run(
        [
            str(find_iscc(args.iscc)),
            f"/DPayloadRoot={payload_root}",
            f"/DOutputRoot={output_root}",
            str(definition),
        ],
        check=True,
    )

    setup_path = output_root / "LuminaDesktopBetaR1-Setup.exe"
    if not setup_path.is_file():
        raise FileNotFoundError("compiled Lumina setup executable is missing")

    try:
        commit = subprocess.check_output(
            ["git", "-C", str(source_root), "rev-parse", "HEAD"],
            text=True,
        ).strip()
    except Exception:
        commit = "unknown"

    receipt = {
        "schema_version": "lumina-windows-installer-build-receipt-r1",
        "build_id": BUILD_ID,
        "built_at": datetime.now(timezone.utc).isoformat(),
        "source_commit": commit,
        "installer_name": setup_path.name,
        "installer_sha256": sha256_file(setup_path),
        "installer_size_bytes": setup_path.stat().st_size,
        "installer_framework": "Inno Setup",
        "bundles_python": True,
        "requires_system_python": False,
        "current_user_install": True,
        "signed": False,
        "state_preserved_on_upgrade": True,
        "state_preserved_on_uninstall_contract": True,
        "uninstall_validated": False,
        "authority_boundary": (
            "Desktop packaging places and launches Lumina; it does not alter "
            "runtime governance, canon, or continuity truth."
        ),
    }
    receipt_path = output_root / "LuminaDesktopBetaR1-Setup-receipt.json"
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

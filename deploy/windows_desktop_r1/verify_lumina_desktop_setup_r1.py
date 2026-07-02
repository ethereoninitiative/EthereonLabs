#!/usr/bin/env python3
"""Validate the Lumina desktop package on a Windows host."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess


TRIAL_ID = "lumina-desktop-setup-r1"


def run_checked(command: list[str]) -> None:
    completed = subprocess.run(command, check=False)
    if completed.returncode:
        raise RuntimeError(
            f"command failed with exit code {completed.returncode}: {command[0]}"
        )


def run_cmd(path: Path, *arguments: str) -> None:
    run_checked(["cmd.exe", "/d", "/c", str(path), *arguments])


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--setup", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--install-root", type=Path)
    args = parser.parse_args()

    setup = args.setup.resolve()
    receipt_path = args.receipt.resolve()
    local_app_data = os.environ.get("LOCALAPPDATA")
    if not local_app_data and args.install_root is None:
        raise RuntimeError("LOCALAPPDATA is unavailable")
    install_root = (
        args.install_root.resolve()
        if args.install_root is not None
        else Path(local_app_data) / "Lumina"
    )

    install_log = Path(os.environ.get("RUNNER_TEMP", install_root.parent)) / "lumina-install.log"
    upgrade_log = Path(os.environ.get("RUNNER_TEMP", install_root.parent)) / "lumina-upgrade.log"
    silent = ["/VERYSILENT", "/SUPPRESSMSGBOXES", "/NORESTART", "/SP-"]

    run_checked([str(setup), *silent, f"/LOG={install_log}"])

    lumina = install_root / "bin" / "lumina.cmd"
    bridge = install_root / "bin" / "lumina-bridge.cmd"
    python_executable = install_root / "runtime" / "python" / "python.exe"
    if not lumina.is_file() or not bridge.is_file() or not python_executable.is_file():
        raise RuntimeError("required installed launch surfaces are missing")

    run_cmd(lumina, "doctor", "--json")
    run_cmd(lumina, "project", "create", "Installer Project", "--open", "--json")
    run_cmd(lumina, "session", "create", "Installer Session", "--open", "--json")
    run_cmd(lumina, "dashboard")
    run_cmd(bridge, "--help")

    marker = (
        install_root
        / "state"
        / "ship_of_ethereon_v2"
        / "installer-continuity-marker.txt"
    )
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text("continuity-held\n", encoding="utf-8")

    run_checked([str(setup), *silent, f"/LOG={upgrade_log}"])
    if marker.read_text(encoding="utf-8").strip() != "continuity-held":
        raise RuntimeError("continuity marker did not return after upgrade")
    run_cmd(lumina, "project", "active", "--json")
    run_cmd(lumina, "session", "active", "--json")

    receipt = json.loads(receipt_path.read_text(encoding="utf-8-sig"))
    if receipt.get("installer_sha256") != sha256_file(setup):
        raise RuntimeError("setup receipt hash does not match")
    if receipt.get("signed") is not False:
        raise RuntimeError("developer preview signing claim must remain false")
    if receipt.get("state_preserved_on_upgrade") is not True:
        raise RuntimeError("upgrade continuity boundary is missing")
    if receipt.get("state_preserved_on_uninstall") is not True:
        raise RuntimeError("uninstall continuity boundary is missing")

    uninstaller = install_root / "unins000.exe"
    if not uninstaller.is_file():
        raise RuntimeError("desktop uninstaller is missing")
    run_checked([str(uninstaller), *silent])

    if not marker.is_file():
        raise RuntimeError("default removal deleted continuity state")
    if lumina.exists() or bridge.exists() or python_executable.exists():
        raise RuntimeError("default removal left replaceable application files")

    result = {
        "trial_id": TRIAL_ID,
        "passed": True,
        "setup_sha256": sha256_file(setup),
        "install_root": str(install_root),
        "state_preserved_after_upgrade": True,
        "state_preserved_after_uninstall": True,
        "application_removed": True,
        "authority_boundary": (
            "The setup trial verifies packaging and state preservation only; "
            "runtime governance remains authoritative."
        ),
    }
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Validate Lumina desktop installer lifecycle behavior on Windows."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import traceback


TRIAL_ID = "lumina-desktop-setup-lifecycle-r1"
AUTHORITY_BOUNDARY = (
    "The setup lifecycle trial verifies Windows desktop packaging, installed "
    "Studio execution, upgrade, uninstall, and state preservation only; it does "
    "not alter runtime governance, canon, mode legality, capability authority, "
    "identity, or primary continuity truth."
)
CONTINUITY_MARKER_TEXT = "continuity-held"
LAUNCHABLE_SUFFIXES = {".bat", ".cmd", ".exe", ".ps1", ".py"}
STUDIO_PROMPT = "Review Lumina OS progress and produce the next governed action receipt."
STUDIO_PROJECT_ID = "lumina-os"
STUDIO_ACTION = "studio_runtime_cycle_v0_3_2"


def run_checked(command: list[str]) -> None:
    completed = subprocess.run(command, check=False)
    if completed.returncode:
        raise RuntimeError(
            f"command failed with exit code {completed.returncode}: {command[0]}"
        )


def run_json_checked(command: list[str]) -> dict[str, object]:
    completed = subprocess.run(
        command,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if completed.returncode:
        detail = completed.stderr.strip() or completed.stdout.strip()
        raise RuntimeError(
            f"command failed with exit code {completed.returncode}: {command[0]}: {detail}"
        )
    try:
        payload = json.loads(completed.stdout)
    except Exception as exc:
        raise RuntimeError(
            f"command did not emit a JSON object: {command[0]}: {completed.stdout[-1200:]}"
        ) from exc
    if not isinstance(payload, dict):
        raise RuntimeError(f"command emitted non-object JSON: {command[0]}")
    return payload


def run_cmd(path: Path, *arguments: str) -> None:
    run_checked(["cmd.exe", "/d", "/c", str(path), *arguments])


def read_json_object(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"expected JSON object receipt: {path}")
    return payload


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def default_lifecycle_receipt_path(setup_receipt: Path) -> Path:
    if setup_receipt.name.endswith("-receipt.json"):
        return setup_receipt.with_name(
            setup_receipt.name.replace("-receipt.json", "-lifecycle-receipt.json")
        )
    return setup_receipt.with_name(f"{setup_receipt.stem}-lifecycle-receipt.json")


def write_lifecycle_receipt(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def find_inno_uninstaller(install_root: Path) -> Path:
    uninstallers = sorted(
        (candidate for candidate in install_root.glob("unins*.exe") if candidate.is_file()),
        key=lambda candidate: (candidate.stat().st_mtime, candidate.name),
        reverse=True,
    )
    if not uninstallers:
        raise RuntimeError(
            "Inno Setup uninstaller is missing; hosted uninstall cannot be verified"
        )
    return uninstallers[0]


def assert_marker_text(marker: Path, failure: str) -> None:
    if not marker.is_file():
        raise RuntimeError(failure)
    if marker.read_text(encoding="utf-8").strip() != CONTINUITY_MARKER_TEXT:
        raise RuntimeError(failure)


def validate_installed_studio_cycle(
    *,
    python_executable: Path,
    app_payload_root: Path,
    action: str,
) -> dict[str, object]:
    studio_cli = (
        app_payload_root
        / "LuminaOS"
        / "bootstrap"
        / "Ship_of_Ethereon_V2"
        / "studio"
        / "lumina_cli.py"
    )
    if not studio_cli.is_file():
        raise RuntimeError(f"installed Studio CLI is missing: {studio_cli}")

    receipt = run_json_checked(
        [
            str(python_executable),
            str(studio_cli),
            STUDIO_PROMPT,
            "--current-mode",
            "Continuity",
            "--target-mode",
            "Observation",
            "--action-type",
            "audit",
            "--action",
            action,
            "--project-id",
            STUDIO_PROJECT_ID,
            "--focus",
            "continuity",
            "--depth",
            "structural",
            "--intent",
            "verify",
            "--receipt-json",
        ]
    )

    if receipt.get("halted") is not False:
        raise RuntimeError(f"installed Studio cycle halted: {receipt.get('halt_reason')}")
    if receipt.get("governance_chain_valid") is not True:
        raise RuntimeError("installed Studio cycle did not return a valid governance chain")
    if receipt.get("lumina_project_id") != STUDIO_PROJECT_ID:
        raise RuntimeError("installed Studio cycle did not preserve the requested project ID")

    checkpoint_path = Path(str(receipt.get("checkpoint_path", "")))
    log_path = Path(str(receipt.get("log_path", "")))
    if not checkpoint_path.is_file():
        raise RuntimeError(f"installed Studio cycle checkpoint is missing: {checkpoint_path}")
    if not log_path.is_file():
        raise RuntimeError(f"installed Studio cycle receipt is missing: {log_path}")

    capabilities = set(receipt.get("exposed_capability_ids") or [])
    required_capabilities = {"continuity_restore_store", "lumina_workspace_host"}
    if not required_capabilities.issubset(capabilities):
        raise RuntimeError(
            "installed Studio cycle did not expose the return/host capabilities: "
            + ", ".join(sorted(required_capabilities - capabilities))
        )

    return receipt


def assert_replaceable_machinery_removed_or_inactive(install_root: Path) -> None:
    app_root = install_root / "app"
    runtime_root = install_root / "runtime"
    bin_root = install_root / "bin"
    app_payload_root = app_root / "EthereonLabs"
    ship_root = app_payload_root / "LuminaOS" / "bootstrap" / "Ship_of_Ethereon_V2"

    expected_active_paths = [
        bin_root / "lumina.cmd",
        bin_root / "lumina-bridge.cmd",
        runtime_root / "python" / "python.exe",
        ship_root / "bin" / "lumina",
        ship_root / "bin" / "lumina-bridge",
        app_payload_root / "deploy" / "windows_desktop_r1" / "launchers" / "lumina.cmd",
        app_payload_root
        / "deploy"
        / "windows_desktop_r1"
        / "launchers"
        / "lumina-bridge.cmd",
        app_payload_root / ".lumina_state",
    ]
    remaining_expected = [str(path) for path in expected_active_paths if path.exists()]
    if remaining_expected:
        raise RuntimeError(
            "replaceable installer machinery remains active after uninstall: "
            + ", ".join(remaining_expected)
        )

    for root in (app_root, runtime_root, bin_root):
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if path.is_file() and path.suffix.lower() in LAUNCHABLE_SUFFIXES:
                raise RuntimeError(
                    "replaceable installer machinery still contains a launchable file "
                    f"after uninstall: {path}"
                )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--setup", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--lifecycle-receipt", type=Path)
    parser.add_argument("--install-root", type=Path)
    args = parser.parse_args()

    setup = args.setup.resolve()
    receipt_path = args.receipt.resolve()
    lifecycle_receipt_path = (
        args.lifecycle_receipt.resolve()
        if args.lifecycle_receipt is not None
        else default_lifecycle_receipt_path(receipt_path)
    )
    local_app_data = os.environ.get("LOCALAPPDATA")
    if not local_app_data and args.install_root is None:
        raise RuntimeError("LOCALAPPDATA is unavailable")
    install_root = (
        args.install_root.resolve()
        if args.install_root is not None
        else Path(local_app_data) / "Lumina"
    )

    diagnostic_root = Path(os.environ.get("RUNNER_TEMP", install_root.parent))
    install_log = diagnostic_root / "lumina-install.log"
    upgrade_log = diagnostic_root / "lumina-upgrade.log"
    uninstall_log = diagnostic_root / "lumina-uninstall.log"
    silent = ["/VERYSILENT", "/SUPPRESSMSGBOXES", "/NORESTART", "/SP-"]

    installer_sha256 = sha256_file(setup)
    lifecycle_receipt: dict[str, object] = {
        "schema_version": "lumina-windows-installer-lifecycle-receipt-r1",
        "trial_id": TRIAL_ID,
        "passed": False,
        "install_validated": False,
        "studio_cycle_validated": False,
        "upgrade_validated": False,
        "studio_upgrade_cycle_validated": False,
        "uninstall_validated": False,
        "state_preserved_on_upgrade": False,
        "state_preserved_on_uninstall": False,
        "replaceable_machinery_removed_or_inactive": False,
        "studio_cycle_receipts": {},
        "signed": None,
        "installer_sha256": installer_sha256,
        "install_root": str(install_root),
        "setup_receipt": str(receipt_path),
        "logs": {
            "install": str(install_log),
            "upgrade": str(upgrade_log),
            "uninstall": str(uninstall_log),
        },
        "authority_boundary": AUTHORITY_BOUNDARY,
    }

    try:
        receipt = read_json_object(receipt_path)
        lifecycle_receipt["signed"] = receipt.get("signed")
        if receipt.get("installer_sha256") != installer_sha256:
            raise RuntimeError("setup receipt hash does not match")
        if receipt.get("signed") is not False:
            raise RuntimeError("developer preview signing claim must remain false")
        if receipt.get("state_preserved_on_upgrade") is not True:
            raise RuntimeError("upgrade continuity boundary is missing")
        if receipt.get("state_preserved_on_uninstall_contract") is not True:
            raise RuntimeError("uninstall state-preservation contract is missing")
        if receipt.get("uninstall_validated") is not False:
            raise RuntimeError("build receipt must not claim uninstall validation")

        run_checked([str(setup), *silent, f"/LOG={install_log}"])

        lumina = install_root / "bin" / "lumina.cmd"
        bridge = install_root / "bin" / "lumina-bridge.cmd"
        python_executable = install_root / "runtime" / "python" / "python.exe"
        app_payload_root = install_root / "app" / "EthereonLabs"
        if not lumina.is_file() or not bridge.is_file() or not python_executable.is_file():
            raise RuntimeError("required installed launch surfaces are missing")

        run_cmd(lumina, "doctor", "--json")
        run_cmd(lumina, "project", "create", "Installer Project", "--open", "--json")
        run_cmd(lumina, "session", "create", "Installer Session", "--open", "--json")
        run_cmd(bridge, "--help")
        lifecycle_receipt["install_validated"] = True

        install_studio_receipt = validate_installed_studio_cycle(
            python_executable=python_executable,
            app_payload_root=app_payload_root,
            action=STUDIO_ACTION,
        )
        lifecycle_receipt["studio_cycle_receipts"]["install"] = install_studio_receipt
        lifecycle_receipt["studio_cycle_validated"] = True

        marker = (
            install_root
            / "state"
            / "ship_of_ethereon_v2"
            / "installer-continuity-marker.txt"
        )
        marker.parent.mkdir(parents=True, exist_ok=True)
        marker.write_text(CONTINUITY_MARKER_TEXT + "\n", encoding="utf-8")

        run_checked([str(setup), *silent, f"/LOG={upgrade_log}"])
        assert_marker_text(marker, "continuity marker did not return after upgrade")
        lifecycle_receipt["state_preserved_on_upgrade"] = True
        run_cmd(lumina, "project", "active", "--json")
        run_cmd(lumina, "session", "active", "--json")
        lifecycle_receipt["upgrade_validated"] = True

        upgrade_studio_receipt = validate_installed_studio_cycle(
            python_executable=python_executable,
            app_payload_root=app_payload_root,
            action=f"{STUDIO_ACTION}_upgrade",
        )
        lifecycle_receipt["studio_cycle_receipts"]["upgrade"] = upgrade_studio_receipt
        lifecycle_receipt["studio_upgrade_cycle_validated"] = True

        uninstaller = find_inno_uninstaller(install_root)
        run_checked([str(uninstaller), *silent, f"/LOG={uninstall_log}"])
        assert_marker_text(marker, "continuity marker did not remain after uninstall")
        lifecycle_receipt["state_preserved_on_uninstall"] = True
        assert_replaceable_machinery_removed_or_inactive(install_root)
        lifecycle_receipt["replaceable_machinery_removed_or_inactive"] = True
        lifecycle_receipt["uninstall_validated"] = True

    except Exception as exc:
        lifecycle_receipt["failure"] = str(exc)
        write_lifecycle_receipt(lifecycle_receipt_path, lifecycle_receipt)
        raise

    lifecycle_receipt["passed"] = True
    write_lifecycle_receipt(lifecycle_receipt_path, lifecycle_receipt)
    print(json.dumps(lifecycle_receipt, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception:
        diagnostic_root = Path(os.environ.get("RUNNER_TEMP", Path.cwd()))
        diagnostic_path = diagnostic_root / "lumina-lifecycle.log"
        with diagnostic_path.open("a", encoding="utf-8") as handle:
            handle.write("\n--- Lumina setup sea-trial traceback ---\n")
            handle.write(traceback.format_exc())
        raise

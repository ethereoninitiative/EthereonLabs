#!/usr/bin/env python3
"""Lumina deployment doctor r1.

Non-mutating preflight checker for the Ubuntu Server appliance scaffold.
It inspects host registry, env placeholder risk, path presence, and service files.
It does not start services, edit files, or grant authority.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
import argparse
import getpass
import json
import os

DEFAULT_REPO_ROOT = Path(os.environ.get("REPO_ROOT", "/opt/lumina/EthereonLabs"))
DEFAULT_ENV_FILE = Path(os.environ.get("LUMINA_ENV_FILE", "/etc/lumina/lumina-appliance.env"))
DEFAULT_REGISTRY_PATH = Path(os.environ.get("LUMINA_HOST_REGISTRY", "deploy/ubuntu_server_lts/host_registry.example.json"))
DEFAULT_HOST_ID = os.environ.get("LUMINA_HOST_ID", "host-local-dev-001")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class CheckResult:
    check_id: str
    passed: bool
    severity: str
    detail: str


class DeploymentDoctor:
    def __init__(self, *, repo_root: Path, env_file: Path, registry_path: Path, host_id: str):
        self.repo_root = repo_root
        self.env_file = env_file
        self.registry_path = registry_path if registry_path.is_absolute() else repo_root / registry_path
        self.host_id = host_id
        self.checks: List[CheckResult] = []
        self.host_record: Optional[Dict[str, Any]] = None

    def add(self, check_id: str, passed: bool, severity: str, detail: str) -> None:
        self.checks.append(CheckResult(check_id, passed, severity, detail))

    def load_registry(self) -> None:
        if not self.registry_path.exists():
            self.add("host_registry_exists", False, "halt", f"Host registry not found: {self.registry_path}")
            return
        try:
            payload = json.loads(self.registry_path.read_text(encoding="utf-8"))
        except Exception as exc:
            self.add("host_registry_parse", False, "halt", f"Host registry could not be parsed: {exc}")
            return
        hosts = payload.get("hosts", [])
        for host in hosts:
            if host.get("host_id") == self.host_id:
                self.host_record = host
                break
        self.add("host_registry_exists", True, "info", f"Host registry loaded: {self.registry_path}")
        self.add("host_record_found", self.host_record is not None, "halt", f"Host id requested: {self.host_id}")

    def check_host_record(self) -> None:
        host = self.host_record
        if not host:
            return
        required_fields = [
            "host_id",
            "host_label",
            "host_type",
            "runtime_scope",
            "approved_by_user_id",
            "operator_user_ids",
            "allowed_runtime_paths",
            "allowed_action_types",
            "state_root",
            "log_root",
            "service_user",
            "created_at",
        ]
        missing = [field for field in required_fields if field not in host or host.get(field) in (None, "", [])]
        self.add("host_required_fields", not missing, "halt", f"Missing fields: {missing}" if missing else "All required host fields present")
        self.add("host_not_revoked", host.get("revoked_at") in (None, ""), "halt", f"revoked_at={host.get('revoked_at')}")

        expected_user = host.get("service_user")
        current_user = getpass.getuser()
        self.add(
            "service_user_context_visible",
            bool(expected_user),
            "warn",
            f"expected service_user={expected_user}; current process user={current_user}",
        )

    def check_paths(self) -> None:
        host = self.host_record or {}
        self.add("repo_root_exists", self.repo_root.exists(), "halt", f"repo_root={self.repo_root}")
        runtime_paths = host.get("allowed_runtime_paths", [])
        for idx, raw_path in enumerate(runtime_paths):
            path = Path(raw_path)
            self.add(f"runtime_path_exists_{idx}", path.exists(), "halt", f"runtime_path={path}")
        state_root = Path(host.get("state_root", "/var/lib/lumina"))
        log_root = Path(host.get("log_root", "/var/log/lumina"))
        self.add("state_root_exists", state_root.exists(), "warn", f"state_root={state_root}")
        self.add("log_root_exists", log_root.exists(), "warn", f"log_root={log_root}")

    def check_env_file(self) -> None:
        if not self.env_file.exists():
            self.add("env_file_exists", False, "halt", f"env_file={self.env_file}")
            return
        text = self.env_file.read_text(encoding="utf-8", errors="replace")
        self.add("env_file_exists", True, "info", f"env_file={self.env_file}")
        placeholder_terms = ["SET_USER", "SET_PASSWORD", "SET_DBNAME", "change-me", "https://example.com"]
        present = [term for term in placeholder_terms if term in text]
        self.add("env_placeholders_removed", not present, "halt", f"placeholder terms present: {present}" if present else "No known placeholder terms present")

    def check_service_files(self) -> None:
        service_files = [
            self.repo_root / "deploy/ubuntu_server_lts/lumina-orchestrator.service",
            self.repo_root / "deploy/ubuntu_server_lts/lumina-orchestrator.timer",
            self.repo_root / "deploy/ubuntu_server_lts/chamber-advisory.service",
        ]
        for path in service_files:
            self.add(f"service_file_exists:{path.name}", path.exists(), "halt", str(path))

    def run(self) -> Dict[str, Any]:
        self.load_registry()
        self.check_host_record()
        self.check_paths()
        self.check_env_file()
        self.check_service_files()
        halt_conditions = [asdict(check) for check in self.checks if not check.passed and check.severity == "halt"]
        warning_conditions = [asdict(check) for check in self.checks if not check.passed and check.severity == "warn"]
        return {
            "doctor": "deployment_doctor_r1",
            "created_at": utc_now(),
            "host_id": self.host_id,
            "repo_root": str(self.repo_root),
            "env_file": str(self.env_file),
            "registry_path": str(self.registry_path),
            "host_record_present": self.host_record is not None,
            "passed": not halt_conditions,
            "halt_conditions": halt_conditions,
            "warning_conditions": warning_conditions,
            "checks": [asdict(check) for check in self.checks],
            "recommendation": "ready_for_next_drydock" if not halt_conditions else "remain_in_drydock",
        }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a non-mutating Lumina deployment preflight check.")
    parser.add_argument("--repo-root", default=str(DEFAULT_REPO_ROOT))
    parser.add_argument("--env-file", default=str(DEFAULT_ENV_FILE))
    parser.add_argument("--registry", default=str(DEFAULT_REGISTRY_PATH))
    parser.add_argument("--host-id", default=DEFAULT_HOST_ID)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    doctor = DeploymentDoctor(
        repo_root=Path(args.repo_root),
        env_file=Path(args.env_file),
        registry_path=Path(args.registry),
        host_id=args.host_id,
    )
    print(json.dumps(doctor.run(), indent=2))

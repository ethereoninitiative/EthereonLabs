#!/usr/bin/env python3
"""Lumina local project registry helper.

This helper creates and maintains local Harbor/workspace project metadata under
`.lumina_state/ship_of_ethereon_v2/projects`. It is host-layer workspace
infrastructure only. It does not own runtime governance, canon lineage, mode
legality, mutation authority, checkpoint legality, or capability authority.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
import argparse
import json
import re

BOOTSTRAP_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[4]
STATE_ROOT = REPO_ROOT / ".lumina_state" / "ship_of_ethereon_v2"
PROJECTS_ROOT = STATE_ROOT / "projects"
ACTIVE_PROJECT_PATH = STATE_ROOT / "active_project.json"
PROJECT_SCHEMA_VERSION = "lumina-project-r1"
ACTIVE_SCHEMA_VERSION = "lumina-active-project-r1"

PROJECT_SLUG_RE = re.compile(r"[^A-Za-z0-9_.-]+")
PROJECT_SUBDIRS = ["receipts", "bundles", "checkpoints", "notes", "timeline", "artifacts"]


@dataclass
class ProjectRecord:
    schema_version: str
    name: str
    slug: str
    status: str
    created_at: str
    updated_at: str
    project_root: str
    description: str
    default_mode: str
    tags: List[str]
    authority_boundary: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def slugify(name: str) -> str:
    slug = PROJECT_SLUG_RE.sub("-", name.strip()).strip("-._")
    return slug or "project"


def project_dir(slug: str) -> Path:
    return PROJECTS_ROOT / slug


def project_file(slug: str) -> Path:
    return project_dir(slug) / "project.json"


def read_json(path: Path) -> Optional[Dict[str, Any]]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else None
    except Exception:
        return None


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def create_project(name: str, *, description: str = "", default_mode: str = "Observation", tags: Optional[List[str]] = None, open_project: bool = False) -> Dict[str, Any]:
    slug = slugify(name)
    root = project_dir(slug)
    path = project_file(slug)
    if path.exists():
        raise SystemExit(f"Lumina project already exists: {slug}")
    stamp = now_iso()
    root.mkdir(parents=True, exist_ok=True)
    for subdir in PROJECT_SUBDIRS:
        (root / subdir).mkdir(parents=True, exist_ok=True)
    record = ProjectRecord(
        schema_version=PROJECT_SCHEMA_VERSION,
        name=name,
        slug=slug,
        status="active",
        created_at=stamp,
        updated_at=stamp,
        project_root=str(root),
        description=description,
        default_mode=default_mode,
        tags=tags or [],
        authority_boundary="Project registry organizes local workspace metadata only; runtime governance remains authoritative.",
    ).to_dict()
    write_json(path, record)
    if open_project:
        set_active_project(slug)
    return record


def load_project(slug_or_name: str) -> Dict[str, Any]:
    slug = slugify(slug_or_name)
    path = project_file(slug)
    payload = read_json(path)
    if payload is None:
        # Allow exact name fallback across registry.
        for item in list_projects(include_archived=True):
            if item.get("name") == slug_or_name:
                payload = read_json(project_file(str(item["slug"])))
                break
    if payload is None:
        raise SystemExit(f"Lumina project not found: {slug_or_name}")
    return payload


def list_projects(*, include_archived: bool = False) -> List[Dict[str, Any]]:
    if not PROJECTS_ROOT.exists():
        return []
    records: List[Dict[str, Any]] = []
    for path in sorted(PROJECTS_ROOT.glob("*/project.json")):
        payload = read_json(path)
        if not payload:
            continue
        if payload.get("status") == "archived" and not include_archived:
            continue
        records.append(payload)
    return records


def set_active_project(slug_or_name: str) -> Dict[str, Any]:
    record = load_project(slug_or_name)
    payload = {
        "schema_version": ACTIVE_SCHEMA_VERSION,
        "active_project_slug": record["slug"],
        "active_project_name": record["name"],
        "project_root": record["project_root"],
        "set_at": now_iso(),
        "authority_boundary": "Active project marker is host workspace orientation only; runtime governance remains authoritative.",
    }
    write_json(ACTIVE_PROJECT_PATH, payload)
    return payload


def active_project() -> Optional[Dict[str, Any]]:
    payload = read_json(ACTIVE_PROJECT_PATH)
    if not payload:
        return None
    slug = payload.get("active_project_slug")
    if not slug:
        return payload
    try:
        payload["project"] = load_project(str(slug))
    except SystemExit:
        payload["project_missing"] = True
    return payload


def archive_project(slug_or_name: str) -> Dict[str, Any]:
    record = load_project(slug_or_name)
    record["status"] = "archived"
    record["updated_at"] = now_iso()
    write_json(project_file(str(record["slug"])), record)
    active = active_project()
    if active and active.get("active_project_slug") == record.get("slug"):
        ACTIVE_PROJECT_PATH.unlink(missing_ok=True)
    return record


def restore_project(slug_or_name: str) -> Dict[str, Any]:
    record = load_project(slug_or_name)
    record["status"] = "active"
    record["updated_at"] = now_iso()
    write_json(project_file(str(record["slug"])), record)
    return record


def registry_snapshot(*, include_archived: bool = False) -> Dict[str, Any]:
    projects = list_projects(include_archived=include_archived)
    return {
        "schema_version": "lumina-project-registry-snapshot-r1",
        "projects_root": str(PROJECTS_ROOT),
        "project_count": len(projects),
        "projects": projects,
        "active": active_project(),
        "authority_boundary": "Project registry is Harbor/workspace organization only; runtime governance remains authoritative.",
    }


def print_project_table(projects: List[Dict[str, Any]]) -> None:
    if not projects:
        print("No Lumina projects yet.")
        return
    print("Lumina projects")
    for record in projects:
        print(f"  {record.get('slug'):24} {record.get('status'):8} {record.get('name')}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Manage the local Lumina project registry.")
    sub = parser.add_subparsers(dest="command", required=True)

    create = sub.add_parser("create")
    create.add_argument("name")
    create.add_argument("--description", default="")
    create.add_argument("--default-mode", default="Observation")
    create.add_argument("--tag", action="append", default=[])
    create.add_argument("--open", action="store_true")
    create.add_argument("--json", action="store_true")

    open_cmd = sub.add_parser("open")
    open_cmd.add_argument("name")
    open_cmd.add_argument("--json", action="store_true")

    list_cmd = sub.add_parser("list")
    list_cmd.add_argument("--include-archived", action="store_true")
    list_cmd.add_argument("--json", action="store_true")

    active_cmd = sub.add_parser("active")
    active_cmd.add_argument("--json", action="store_true")

    archive = sub.add_parser("archive")
    archive.add_argument("name")
    archive.add_argument("--json", action="store_true")

    restore = sub.add_parser("restore")
    restore.add_argument("name")
    restore.add_argument("--json", action="store_true")

    args = parser.parse_args()
    if args.command == "create":
        payload = create_project(args.name, description=args.description, default_mode=args.default_mode, tags=args.tag, open_project=args.open)
        print(json.dumps(payload, indent=2) if args.json else f"Created Lumina project: {payload['slug']}")
    elif args.command == "open":
        payload = set_active_project(args.name)
        print(json.dumps(payload, indent=2) if args.json else f"Opened Lumina project: {payload['active_project_slug']}")
    elif args.command == "list":
        payload = registry_snapshot(include_archived=args.include_archived)
        print(json.dumps(payload, indent=2) if args.json else print_project_table(payload["projects"]))
    elif args.command == "active":
        payload = active_project() or {"active_project_slug": None, "active_project_name": None}
        print(json.dumps(payload, indent=2) if args.json else f"Active Lumina project: {payload.get('active_project_slug') or 'none'}")
    elif args.command == "archive":
        payload = archive_project(args.name)
        print(json.dumps(payload, indent=2) if args.json else f"Archived Lumina project: {payload['slug']}")
    elif args.command == "restore":
        payload = restore_project(args.name)
        print(json.dumps(payload, indent=2) if args.json else f"Restored Lumina project: {payload['slug']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

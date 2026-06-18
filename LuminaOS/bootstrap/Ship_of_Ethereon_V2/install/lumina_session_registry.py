#!/usr/bin/env python3
"""Lumina local session registry helper.

This helper creates and maintains host-layer session metadata under
`.lumina_state/ship_of_ethereon_v2/sessions`. It is Harbor/workspace
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

REPO_ROOT = Path(__file__).resolve().parents[4]
STATE_ROOT = REPO_ROOT / ".lumina_state" / "ship_of_ethereon_v2"
SESSIONS_ROOT = STATE_ROOT / "sessions"
ACTIVE_SESSION_PATH = STATE_ROOT / "active_session.json"
PROJECTS_ROOT = STATE_ROOT / "projects"
SESSION_SCHEMA_VERSION = "lumina-session-r1"
ACTIVE_SCHEMA_VERSION = "lumina-active-session-r1"
SLUG_RE = re.compile(r"[^A-Za-z0-9_.-]+")
SESSION_SUBDIRS = ["receipts", "notes", "artifacts", "context"]


@dataclass
class SessionRecord:
    schema_version: str
    session_id: str
    title: str
    status: str
    created_at: str
    updated_at: str
    project_slug: Optional[str]
    session_root: str
    mode_hint: str
    tags: List[str]
    receipt_count: int
    note_count: int
    authority_boundary: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def slugify(text: str) -> str:
    slug = SLUG_RE.sub("-", text.strip()).strip("-._")
    return slug or "session"


def read_json(path: Path) -> Optional[Dict[str, Any]]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else None
    except Exception:
        return None


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def active_project_slug() -> Optional[str]:
    payload = read_json(STATE_ROOT / "active_project.json")
    if not payload:
        return None
    slug = payload.get("active_project_slug")
    return str(slug) if slug else None


def project_sessions_root(project_slug: Optional[str]) -> Path:
    if project_slug:
        return PROJECTS_ROOT / project_slug / "sessions"
    return SESSIONS_ROOT


def next_session_id(project_slug: Optional[str]) -> str:
    root = project_sessions_root(project_slug)
    existing = [path.name for path in root.glob("session-*") if path.is_dir()] if root.exists() else []
    nums: List[int] = []
    for name in existing:
        try:
            nums.append(int(name.split("-")[-1]))
        except Exception:
            continue
    return f"session-{(max(nums) + 1) if nums else 1:04d}"


def session_dir(session_id: str, project_slug: Optional[str]) -> Path:
    return project_sessions_root(project_slug) / session_id


def session_file(session_id: str, project_slug: Optional[str]) -> Path:
    return session_dir(session_id, project_slug) / "session.json"


def create_session(title: str, *, project_slug: Optional[str] = None, mode_hint: str = "Observation", tags: Optional[List[str]] = None, open_session: bool = False) -> Dict[str, Any]:
    project_slug = project_slug or active_project_slug()
    session_id = next_session_id(project_slug)
    root = session_dir(session_id, project_slug)
    stamp = now_iso()
    root.mkdir(parents=True, exist_ok=True)
    for subdir in SESSION_SUBDIRS:
        (root / subdir).mkdir(parents=True, exist_ok=True)
    record = SessionRecord(
        schema_version=SESSION_SCHEMA_VERSION,
        session_id=session_id,
        title=title,
        status="active",
        created_at=stamp,
        updated_at=stamp,
        project_slug=project_slug,
        session_root=str(root),
        mode_hint=mode_hint,
        tags=tags or [],
        receipt_count=0,
        note_count=0,
        authority_boundary="Session registry organizes local workspace metadata only; runtime governance remains authoritative.",
    ).to_dict()
    write_json(session_file(session_id, project_slug), record)
    if open_session:
        set_active_session(session_id, project_slug=project_slug)
    return record


def iter_session_files(project_slug: Optional[str] = None, *, include_projectless: bool = True) -> List[Path]:
    paths: List[Path] = []
    if project_slug:
        paths.extend(sorted((PROJECTS_ROOT / project_slug / "sessions").glob("session-*/session.json")))
    else:
        if PROJECTS_ROOT.exists():
            paths.extend(sorted(PROJECTS_ROOT.glob("*/sessions/session-*/session.json")))
        if include_projectless:
            paths.extend(sorted(SESSIONS_ROOT.glob("session-*/session.json")))
    return paths


def list_sessions(project_slug: Optional[str] = None, *, include_archived: bool = False) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    for path in iter_session_files(project_slug):
        payload = read_json(path)
        if not payload:
            continue
        if payload.get("status") == "archived" and not include_archived:
            continue
        records.append(payload)
    return sorted(records, key=lambda item: str(item.get("created_at", "")), reverse=True)


def load_session(session_id: str, project_slug: Optional[str] = None) -> Dict[str, Any]:
    if project_slug:
        payload = read_json(session_file(session_id, project_slug))
        if payload:
            return payload
    for item in list_sessions(include_archived=True):
        if item.get("session_id") == session_id or item.get("title") == session_id:
            return item
    raise SystemExit(f"Lumina session not found: {session_id}")


def set_active_session(session_id: str, *, project_slug: Optional[str] = None) -> Dict[str, Any]:
    record = load_session(session_id, project_slug=project_slug)
    payload = {
        "schema_version": ACTIVE_SCHEMA_VERSION,
        "active_session_id": record["session_id"],
        "active_session_title": record["title"],
        "project_slug": record.get("project_slug"),
        "session_root": record["session_root"],
        "set_at": now_iso(),
        "authority_boundary": "Active session marker is host workspace orientation only; runtime governance remains authoritative.",
    }
    write_json(ACTIVE_SESSION_PATH, payload)
    return payload


def active_session() -> Optional[Dict[str, Any]]:
    payload = read_json(ACTIVE_SESSION_PATH)
    if not payload:
        return None
    try:
        payload["session"] = load_session(str(payload.get("active_session_id")), project_slug=payload.get("project_slug"))
    except SystemExit:
        payload["session_missing"] = True
    return payload


def archive_session(session_id: str) -> Dict[str, Any]:
    record = load_session(session_id)
    record["status"] = "archived"
    record["updated_at"] = now_iso()
    write_json(session_file(str(record["session_id"]), record.get("project_slug")), record)
    active = active_session()
    if active and active.get("active_session_id") == record.get("session_id"):
        ACTIVE_SESSION_PATH.unlink(missing_ok=True)
    return record


def restore_session(session_id: str) -> Dict[str, Any]:
    record = load_session(session_id)
    record["status"] = "active"
    record["updated_at"] = now_iso()
    write_json(session_file(str(record["session_id"]), record.get("project_slug")), record)
    return record


def registry_snapshot(*, project_slug: Optional[str] = None, include_archived: bool = False) -> Dict[str, Any]:
    sessions = list_sessions(project_slug=project_slug, include_archived=include_archived)
    return {
        "schema_version": "lumina-session-registry-snapshot-r1",
        "sessions_root": str(SESSIONS_ROOT),
        "project_slug": project_slug,
        "session_count": len(sessions),
        "sessions": sessions,
        "active": active_session(),
        "authority_boundary": "Session registry is Harbor/workspace organization only; runtime governance remains authoritative.",
    }


def print_session_table(sessions: List[Dict[str, Any]]) -> None:
    if not sessions:
        print("No Lumina sessions yet.")
        return
    print("Lumina sessions")
    for record in sessions:
        print(f"  {record.get('session_id'):14} {record.get('status'):8} {record.get('project_slug') or '-':18} {record.get('title')}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Manage the local Lumina session registry.")
    sub = parser.add_subparsers(dest="command", required=True)

    create = sub.add_parser("create")
    create.add_argument("title")
    create.add_argument("--project", default=None)
    create.add_argument("--mode", default="Observation")
    create.add_argument("--tag", action="append", default=[])
    create.add_argument("--open", action="store_true")
    create.add_argument("--json", action="store_true")

    open_cmd = sub.add_parser("open")
    open_cmd.add_argument("session_id")
    open_cmd.add_argument("--project", default=None)
    open_cmd.add_argument("--json", action="store_true")

    list_cmd = sub.add_parser("list")
    list_cmd.add_argument("--project", default=None)
    list_cmd.add_argument("--include-archived", action="store_true")
    list_cmd.add_argument("--json", action="store_true")

    active_cmd = sub.add_parser("active")
    active_cmd.add_argument("--json", action="store_true")

    archive = sub.add_parser("archive")
    archive.add_argument("session_id")
    archive.add_argument("--json", action="store_true")

    restore = sub.add_parser("restore")
    restore.add_argument("session_id")
    restore.add_argument("--json", action="store_true")

    args = parser.parse_args()
    if args.command == "create":
        payload = create_session(args.title, project_slug=args.project, mode_hint=args.mode, tags=args.tag, open_session=args.open)
        print(json.dumps(payload, indent=2) if args.json else f"Created Lumina session: {payload['session_id']}")
    elif args.command == "open":
        payload = set_active_session(args.session_id, project_slug=args.project)
        print(json.dumps(payload, indent=2) if args.json else f"Opened Lumina session: {payload['active_session_id']}")
    elif args.command == "list":
        payload = registry_snapshot(project_slug=args.project, include_archived=args.include_archived)
        print(json.dumps(payload, indent=2) if args.json else print_session_table(payload["sessions"]))
    elif args.command == "active":
        payload = active_session() or {"active_session_id": None, "active_session_title": None}
        print(json.dumps(payload, indent=2) if args.json else f"Active Lumina session: {payload.get('active_session_id') or 'none'}")
    elif args.command == "archive":
        payload = archive_session(args.session_id)
        print(json.dumps(payload, indent=2) if args.json else f"Archived Lumina session: {payload['session_id']}")
    elif args.command == "restore":
        payload = restore_session(args.session_id)
        print(json.dumps(payload, indent=2) if args.json else f"Restored Lumina session: {payload['session_id']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

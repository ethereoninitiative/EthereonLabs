#!/usr/bin/env python3
"""Lumina Partnership R1: durable, local human/AI project collaboration.

This is a host workspace, not the governed runtime or an AI model. AI participants
may submit *proposals*; only a local human action can approve them. No proposal
executes a tool, modifies project files, or acquires runtime authority.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import sqlite3
import sys
from urllib.request import Request, urlopen
from urllib.error import URLError
from uuid import uuid4

BOOTSTRAP_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BOOTSTRAP_ROOT / "runtime"))
from repo_paths_r1 import state_root  # noqa: E402

SCHEMA = "lumina-partnership-r1"
PROJECT_PATTERN = re.compile(r"^[A-Za-z0-9_.-]{1,80}$")
PARTICIPANT_PATTERN = re.compile(r"^[A-Za-z0-9_.-]{1,64}$")
BOUNDARY = (
    "Local collaborative workspace only; participant labels are not authenticated "
    "identities. AI proposals cannot execute actions, access tools, alter canon, "
    "or bypass Lumina runtime governance. Human approval records a decision only."
)


def stamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def required(value: str, label: str, limit: int) -> str:
    value = value.strip()
    if not value or len(value) > limit or "\x00" in value:
        raise ValueError(f"{label} must be 1-{limit} non-NUL characters")
    return value


def safe_id(value: str, label: str, pattern: re.Pattern[str]) -> str:
    if not pattern.fullmatch(value):
        raise ValueError(f"invalid {label}: use letters, numbers, _, -, or .")
    return value


def project_name(selected: str | None = None) -> str:
    if selected:
        return safe_id(selected, "project", PROJECT_PATTERN)
    active = state_root() / "active_project.json"
    try:
        name = json.loads(active.read_text(encoding="utf-8")).get("active_project_slug")
        if isinstance(name, str) and PROJECT_PATTERN.fullmatch(name):
            return name
    except (OSError, ValueError, TypeError):
        pass
    return "harbor"


def default_db() -> Path:
    override = os.environ.get("LUMINA_PARTNERSHIP_DB")
    return Path(override).expanduser() if override else state_root() / "partnership" / "partnership_r1.sqlite3"


class Workspace:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS participants (
                    id TEXT PRIMARY KEY, name TEXT NOT NULL, kind TEXT NOT NULL
                        CHECK (kind IN ('human', 'ai')),
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY, project TEXT NOT NULL, title TEXT NOT NULL,
                    detail TEXT NOT NULL, status TEXT NOT NULL
                        CHECK (status IN ('open', 'done')),
                    created_at TEXT NOT NULL, updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS proposals (
                    id TEXT PRIMARY KEY, project TEXT NOT NULL, task_id TEXT NOT NULL
                        REFERENCES tasks(id), participant_id TEXT NOT NULL
                        REFERENCES participants(id), body TEXT NOT NULL,
                    status TEXT NOT NULL CHECK (status IN ('pending', 'approved', 'rejected')),
                    created_at TEXT NOT NULL, decided_at TEXT, source_model TEXT
                );
                CREATE TABLE IF NOT EXISTS activity (
                    seq INTEGER PRIMARY KEY AUTOINCREMENT, project TEXT NOT NULL,
                    at TEXT NOT NULL, actor TEXT NOT NULL, verb TEXT NOT NULL,
                    subject_id TEXT NOT NULL, detail TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS tasks_project ON tasks(project);
                CREATE INDEX IF NOT EXISTS proposals_project ON proposals(project);
                CREATE INDEX IF NOT EXISTS activity_project ON activity(project, seq);
            """)
            db.execute(
                "INSERT OR IGNORE INTO participants (id,name,kind,created_at) VALUES (?,?,?,?)",
                ("human", "Local human", "human", stamp()),
            )

    def connect(self) -> sqlite3.Connection:
        db = sqlite3.connect(self.path, timeout=10)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys = ON")
        db.execute("PRAGMA busy_timeout = 10000")
        return db

    @staticmethod
    def record(db: sqlite3.Connection, project: str, actor: str, verb: str, subject: str, detail: str) -> None:
        db.execute(
            "INSERT INTO activity(project,at,actor,verb,subject_id,detail) VALUES (?,?,?,?,?,?)",
            (project, stamp(), actor, verb, subject, detail),
        )

    def join(self, participant_id: str, name: str, kind: str = "ai") -> dict:
        participant_id = safe_id(participant_id, "participant ID", PARTICIPANT_PATTERN)
        name = required(name, "name", 120)
        if kind != "ai":
            raise ValueError("Only AI profiles are registered here; local human is built in")
        with self.connect() as db:
            try:
                db.execute(
                    "INSERT INTO participants(id,name,kind,created_at) VALUES (?,?,?,?)",
                    (participant_id, name, kind, stamp()),
                )
            except sqlite3.IntegrityError as exc:
                raise ValueError(f"participant already exists: {participant_id}") from exc
        return {"id": participant_id, "name": name, "kind": kind}

    def add_task(self, project: str, title: str, detail: str = "") -> dict:
        title = required(title, "title", 200)
        detail = required(detail, "detail", 8000) if detail.strip() else ""
        item_id, at = uuid4().hex, stamp()
        with self.connect() as db:
            db.execute(
                "INSERT INTO tasks(id,project,title,detail,status,created_at,updated_at) "
                "VALUES (?,?,?,?,?,?,?)",
                (item_id, project, title, detail, "open", at, at),
            )
            self.record(db, project, "human", "task_created", item_id, title)
        return {"id": item_id, "project": project, "title": title, "status": "open"}

    def propose(self, project: str, task_id: str, participant_id: str, body: str, source_model: str | None = None) -> dict:
        body = required(body, "proposal", 10000)
        item_id, at = uuid4().hex, stamp()
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            profile = db.execute(
                "SELECT kind FROM participants WHERE id = ?", (participant_id,)
            ).fetchone()
            task = db.execute(
                "SELECT status FROM tasks WHERE id = ? AND project = ?",
                (task_id, project),
            ).fetchone()
            if profile is None or profile["kind"] != "ai":
                raise ValueError("registered AI participant required")
            if task is None or task["status"] != "open":
                raise ValueError("task does not exist or is closed in this project")
            db.execute(
                "INSERT INTO proposals(id,project,task_id,participant_id,body,status,created_at,source_model) "
                "VALUES (?,?,?,?,?,?,?,?)",
                (item_id, project, task_id, participant_id, body, "pending", at, source_model),
            )
            self.record(db, project, participant_id, "proposal_submitted", item_id, task_id)
        return {"id": item_id, "task_id": task_id, "participant_id": participant_id, "status": "pending"}

    def think(self, project: str, task_id: str, participant_id: str, model: str) -> dict:
        """Invite an explicitly installed local Ollama model to submit a proposal.

        Network destination is fixed to the user's loopback, and no prompt or
        response is sent to a remote model provider by this command.
        """
        model = required(model, "model", 120)
        if not re.fullmatch(r"[A-Za-z0-9._:/-]+", model):
            raise ValueError("invalid local model name")
        with self.connect() as db:
            participant = db.execute(
                "SELECT kind FROM participants WHERE id=?", (participant_id,)
            ).fetchone()
            task = db.execute(
                "SELECT title,detail,status FROM tasks WHERE id=? AND project=?",
                (task_id, project),
            ).fetchone()
        if participant is None or participant["kind"] != "ai":
            raise ValueError("registered AI participant required")
        if task is None or task["status"] != "open":
            raise ValueError("task does not exist or is closed in this project")
        request_body = json.dumps({
            "model": model,
            "stream": False,
            "messages": [
                {"role": "system", "content": (
                    "You are a collaborator in a local human-AI project workspace. "
                    "Suggest a concrete, useful next contribution. State uncertainties. "
                    "Do not claim to have run tools, modified files, or completed the task. "
                    "Your response is a proposal requiring human review."
                )},
                {"role": "user", "content": (
                    f"Project: {project}\nTask: {task['title']}\nContext: {task['detail']}\n"
                    "Offer one practical proposal in under 500 words."
                )},
            ],
        }).encode("utf-8")
        request = Request(
            "http://127.0.0.1:11434/api/chat",
            data=request_body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=60) as response:
                raw = response.read(200001)
            if len(raw) > 200000:
                raise ValueError("local model response exceeded size budget")
            payload = json.loads(raw)
            body = payload["message"]["content"]
            if not isinstance(body, str):
                raise ValueError("local model did not return proposal text")
        except (URLError, TimeoutError, OSError) as exc:
            raise ValueError("local Ollama is unavailable; start it and install the requested model") from exc
        except (KeyError, TypeError, json.JSONDecodeError) as exc:
            raise ValueError("local model response was not valid Ollama chat JSON") from exc
        result = self.propose(project, task_id, participant_id, body, source_model=model)
        result["source_model"] = model
        return result

    def decide(self, project: str, proposal_id: str, decision: str) -> dict:
        if decision not in ("approved", "rejected"):
            raise ValueError("decision must be approved or rejected")
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            proposal = db.execute(
                "SELECT status,task_id FROM proposals WHERE id = ? AND project = ?",
                (proposal_id, project),
            ).fetchone()
            if proposal is None or proposal["status"] != "pending":
                raise ValueError("proposal is absent or already decided")
            task = db.execute(
                "SELECT status FROM tasks WHERE id = ? AND project = ?",
                (proposal["task_id"], project),
            ).fetchone()
            if task is None or task["status"] != "open":
                raise ValueError("cannot decide a proposal for a completed task")
            db.execute(
                "UPDATE proposals SET status = ?, decided_at = ? WHERE id = ?",
                (decision, stamp(), proposal_id),
            )
            self.record(db, project, "human", "proposal_" + decision, proposal_id, proposal["task_id"])
        return {"id": proposal_id, "status": decision, "execution": "none"}

    def complete(self, project: str, task_id: str) -> dict:
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            result = db.execute(
                "UPDATE tasks SET status='done', updated_at=? "
                "WHERE id=? AND project=? AND status='open'",
                (stamp(), task_id, project),
            )
            if result.rowcount != 1:
                raise ValueError("task not found or already complete")
            self.record(db, project, "human", "task_completed", task_id, "")
        return {"id": task_id, "status": "done"}

    def board(self, project: str) -> dict:
        with self.connect() as db:
            participants = [dict(x) for x in db.execute(
                "SELECT * FROM participants ORDER BY created_at,id"
            )]
            tasks = [dict(x) for x in db.execute(
                "SELECT * FROM tasks WHERE project=? ORDER BY created_at,id", (project,)
            )]
            proposals = [dict(x) for x in db.execute(
                "SELECT * FROM proposals WHERE project=? ORDER BY created_at,id", (project,)
            )]
            activity = [dict(x) for x in db.execute(
                "SELECT * FROM (SELECT * FROM activity WHERE project=? ORDER BY seq DESC LIMIT 40) ORDER BY seq ASC",
                (project,),
            )]
        return {
            "schema_version": SCHEMA, "project": project,
            "participants": participants, "tasks": tasks, "proposals": proposals,
            "activity": activity, "authority_boundary": BOUNDARY,
        }


def configure_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--project", help="Project slug; default is the active Lumina project, otherwise harbor")
    parser.add_argument("--db", type=Path, help=argparse.SUPPRESS)
    sub = parser.add_subparsers(dest="partnership_command", required=True)
    sub.add_parser("board", help="Print a machine-readable shared project board")
    join = sub.add_parser("join", help="Register a named AI participant (not an identity proof)")
    join.add_argument("id")
    join.add_argument("name")
    task = sub.add_parser("task", help="Create a human-owned shared task")
    task.add_argument("title")
    task.add_argument("--detail", default="")
    proposal = sub.add_parser("propose", help="Submit a non-executing AI proposal for a task")
    proposal.add_argument("task_id")
    proposal.add_argument("--by", required=True, dest="participant")
    proposal.add_argument("--text", required=True)
    think = sub.add_parser("think", help="Ask an installed local Ollama model for a reviewable proposal")
    think.add_argument("task_id")
    think.add_argument("--by", dest="participant", required=True)
    think.add_argument("--model", required=True)
    decide = sub.add_parser("decide", help="Record human approval/rejection; never execute")
    decide.add_argument("proposal_id")
    decide.add_argument("decision", choices=("approved", "rejected"))
    done = sub.add_parser("done", help="Mark a task complete")
    done.add_argument("task_id")
    serve = sub.add_parser("serve", help="Open local-first human partnership dashboard")
    serve.add_argument("--port", type=int, default=8768)
    serve.add_argument("--no-browser", action="store_true")


def execute(args: argparse.Namespace) -> int:
    try:
        project = project_name(args.project)
        workspace = Workspace(args.db or default_db())
        cmd = args.partnership_command
        if cmd == "board":
            result = workspace.board(project)
        elif cmd == "join":
            result = workspace.join(args.id, args.name)
        elif cmd == "task":
            result = workspace.add_task(project, args.title, args.detail)
        elif cmd == "propose":
            result = workspace.propose(project, args.task_id, args.participant, args.text)
        elif cmd == "think":
            result = workspace.think(project, args.task_id, args.participant, args.model)
        elif cmd == "decide":
            result = workspace.decide(project, args.proposal_id, args.decision)
        elif cmd == "done":
            result = workspace.complete(project, args.task_id)
        elif cmd == "serve":
            from lumina_partnership_ui_r1 import serve as serve_ui
            serve_ui(workspace, project, args.port, open_browser=not args.no_browser)
            return 0
        else:
            raise ValueError("unsupported command")
        print(json.dumps(result, indent=2))
        return 0
    except (ValueError, OSError, sqlite3.Error) as exc:
        print(f"Lumina partnership: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    root = argparse.ArgumentParser(description=__doc__)
    configure_parser(root)
    raise SystemExit(execute(root.parse_args()))

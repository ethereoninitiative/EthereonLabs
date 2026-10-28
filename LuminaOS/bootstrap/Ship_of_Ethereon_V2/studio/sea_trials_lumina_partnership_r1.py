#!/usr/bin/env python3
"""Dependency-free sea trials for the local partnership workspace."""
from __future__ import annotations

from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from threading import Thread
import unittest

STUDIO = Path(__file__).resolve().parent
sys.path.insert(0, str(STUDIO))
from lumina_partnership_r1 import Workspace, configure_parser  # noqa: E402
from lumina_partnership_ui_r1 import make_handler, HTML_PATH  # noqa: E402
import argparse


class WorkspaceTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "kept" / "partnership.db"
        self.space = Workspace(self.path)

    def test_first_run_persistence_and_provenance(self):
        initial = self.space.board("my-project")
        self.assertEqual(initial["tasks"], [])
        self.assertEqual(initial["participants"][0]["kind"], "human")
        self.space.join("atelier", "Atelier Agent")
        task = self.space.add_task("my-project", "Design a shared garden", "List three features")
        contribution = self.space.propose("my-project", task["id"], "atelier", "Begin with a sketch")
        returned = Workspace(self.path).board("my-project")
        self.assertEqual(len(returned["tasks"]), 1)
        self.assertEqual(returned["proposals"][0]["body"], "Begin with a sketch")
        self.assertIn("AI proposals cannot execute", returned["authority_boundary"])
        decision = self.space.decide("my-project", contribution["id"], "approved")
        self.assertEqual(decision["execution"], "none")
        self.assertEqual(Workspace(self.path).board("my-project")["proposals"][0]["status"], "approved")
        self.space.complete("my-project", task["id"])
        board = Workspace(self.path).board("my-project")
        self.assertEqual(board["tasks"][0]["status"], "done")
        self.assertEqual(
            [event["verb"] for event in board["activity"]],
            ["task_created", "proposal_submitted", "proposal_approved", "task_completed"],
        )

    def test_permissions_boundary_and_replay(self):
        task = self.space.add_task("alpha", "Investigate")
        self.space.join("sage", "Sage")
        with self.assertRaisesRegex(ValueError, "registered AI"):
            self.space.propose("alpha", task["id"], "human", "Spoofed agent")
        with self.assertRaisesRegex(ValueError, "registered AI"):
            self.space.propose("alpha", task["id"], "unknown", "Unregistered")
        with self.assertRaisesRegex(ValueError, "closed"):
            self.space.propose("beta", task["id"], "sage", "Cross-project")
        proposal = self.space.propose("alpha", task["id"], "sage", "Investigation plan")
        with self.assertRaisesRegex(ValueError, "already decided|absent"):
            self.space.decide("beta", proposal["id"], "approved")
        self.space.decide("alpha", proposal["id"], "rejected")
        with self.assertRaisesRegex(ValueError, "already decided"):
            self.space.decide("alpha", proposal["id"], "approved")
        with self.assertRaisesRegex(ValueError, "already complete"):
            self.space.complete("alpha", "unknown")

    def test_closed_task_blocks_proposals_and_decisions(self):
        self.space.join("sage", "Sage")
        task = self.space.add_task("harbor", "Build a habitat")
        proposal = self.space.propose("harbor", task["id"], "sage", "One small room")
        self.space.complete("harbor", task["id"])
        with self.assertRaisesRegex(ValueError, "closed"):
            self.space.propose("harbor", task["id"], "sage", "Another room")
        with self.assertRaisesRegex(ValueError, "completed"):
            self.space.decide("harbor", proposal["id"], "approved")

    def test_bad_input_does_not_mutate(self):
        with self.assertRaises(ValueError):
            self.space.join("../escape", "Unsafe")
        with self.assertRaises(ValueError):
            self.space.add_task("harbor", "  ")
        with self.assertRaises(ValueError):
            self.space.add_task("harbor", "Valid", "x" * 8001)
        self.assertEqual(self.space.board("harbor")["activity"], [])

    def test_host_cli_parser(self):
        parser = argparse.ArgumentParser()
        configure_parser(parser)
        args = parser.parse_args(["--project", "alpha", "propose", "task123", "--by", "sage", "--text", "hello"])
        self.assertEqual((args.project, args.partnership_command, args.participant), ("alpha", "propose", "sage"))

    def test_ui_uses_text_not_html_insertion(self):
        page = HTML_PATH.read_text(encoding="utf-8")
        self.assertIn("textContent", page)
        self.assertNotIn("innerHTML", page)


class HttpTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.space = Workspace(Path(self.temp.name) / "db.sqlite")
        self.token = "test-intent-token"
        server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(self.space, "harbor", self.token))
        server.daemon_threads = True
        self.server = server
        self.thread = Thread(target=server.serve_forever, daemon=True)
        self.thread.start()
        self.addCleanup(self.stop)

    def stop(self):
        self.server.shutdown()
        self.thread.join(timeout=3)
        self.server.server_close()

    def request(self, method, path, data=None, headers=None):
        conn = HTTPConnection("127.0.0.1", self.server.server_port, timeout=3)
        try:
            payload = json.dumps(data).encode() if data is not None else None
            h = {"Host": f"127.0.0.1:{self.server.server_port}"}
            if payload:
                h["Content-Type"] = "application/json"
            h.update(headers or {})
            conn.request(method, path, payload, h)
            response = conn.getresponse()
            body = response.read()
            return response.status, body
        finally:
            conn.close()

    def test_read_and_local_mutation(self):
        status, body = self.request("GET", "/api/board")
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body)["tasks"], [])
        status, _ = self.request("POST", "/api/task", {"title": "Build"}, {"X-Lumina-Intent": self.token})
        self.assertEqual(status, 200)
        self.assertEqual(len(self.space.board("harbor")["tasks"]), 1)

    def test_reject_unauthorized_and_cross_site(self):
        status, _ = self.request("POST", "/api/task", {"title": "Bad"})
        self.assertEqual(status, 403)
        status, _ = self.request("POST", "/api/task", {"title": "Bad"}, {
            "X-Lumina-Intent": self.token, "Origin": "https://attacker.test"
        })
        self.assertEqual(status, 403)
        status, _ = self.request("POST", "/api/task", {"title": "Bad"}, {
            "X-Lumina-Intent": self.token, "Sec-Fetch-Site": "cross-site"
        })
        self.assertEqual(status, 403)
        status, _ = self.request("GET", "/api/board", headers={"Host": "attacker.test"})
        self.assertEqual(status, 403)
        self.assertEqual(self.space.board("harbor")["tasks"], [])

    def test_html_has_explicit_csrf_token(self):
        status, body = self.request("GET", "/")
        self.assertEqual(status, 200)
        self.assertIn(self.token.encode(), body)
        self.assertNotIn(b"__LUMINA_CSRF_TOKEN__", body)


if __name__ == "__main__":
    unittest.main(verbosity=2)

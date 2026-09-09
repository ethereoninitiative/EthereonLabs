"""Live-owner, malformed-evidence and HTTP boundaries for the read-only Bridge."""
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import tempfile
from threading import Thread
import unittest
from unittest.mock import patch
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from http.server import ThreadingHTTPServer

from lumina_bridge_return_r1 import load_bridge_return, SnapshotReader, MAX_FILE_BYTES
from lumina_bridge_server_r2 import LuminaBridgeHandler
from lumina_continue_controller_r1 import DEFAULT_FEATURE_FLAGS, SAFE_RUNTIME_CONFIG, LuminaContinueController
from runtime_runner_self_guided_bridge_r1 import SelfGuidedReturnHostRuntimeRunner


def seed(root):
    base = root / 'runtime_runner_r1_actiontype_logging'
    runner = SelfGuidedReturnHostRuntimeRunner(base_dir=base)
    runner.run_cycle(current_mode='Continuity', target_mode='Observation',
                     requested_action='inspect_saved_work', action_type='audit',
                     project_id='bridge-trial', enabled_feature_flags=DEFAULT_FEATURE_FLAGS,
                     runtime_config=SAFE_RUNTIME_CONFIG, artifacts=['runtime/runtime_spine_r1.py'],
                     continuation_notes=['Return to the saved inspection.'])
    (root / 'active_project.json').write_text(json.dumps({
        'active_project_slug': 'bridge-trial', 'active_project_name': 'Bridge trial'}), encoding='utf-8')
    return runner


class BridgeReturnTrial(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.runner = seed(self.root)
        self.now = datetime.now(timezone.utc)
        self.good = self.load()
        self.assertEqual(self.good['status'], 'ready', self.good.get('message'))
        self.paths = {row['role']: Path(row['path']) for row in self.good['provenance']}

    def load(self, **kwargs):
        return load_bridge_return(state_root=self.root, now=kwargs.pop('now', self.now), **kwargs)

    def edit(self, role, **values):
        path = self.paths[role]
        value = json.loads(path.read_text())
        value.update(values)
        path.write_text(json.dumps(value), encoding='utf-8')

    def rejected(self):
        result = self.load()
        self.assertFalse(result['verified'])
        self.assertIsNone(result['panel'])
        return result

    def test_real_owner_two_checkpoint_relationship_and_no_permission(self):
        self.assertEqual(self.good['host_linkage']['status'], 'matching_previous_checkpoint')
        self.assertNotEqual(self.paths['host_checkpoint'], self.paths['return_checkpoint'])
        self.assertFalse(self.good['execution_authorized'])
        self.assertFalse(self.good['governance_verified'])
        self.assertTrue(self.good['panel']['candidate_trajectories'])
        for row in self.good['panel']['candidate_trajectories']:
            self.assertEqual(row['reported_governance']['status'], 'deferred')
            self.assertFalse(row['reachable_in_supplied_snapshot'])

    def test_focus_matches_actual_continue_preflight(self):
        expected = LuminaContinueController(runner=self.runner).preflight(project_id='bridge-trial')
        actual = self.good['panel']['continuation_focus']
        self.assertEqual(actual['recommended_next_action'], expected['recommended_next_action'])

    def test_repeat_reads_never_write_or_start_processes(self):
        before = {p: p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        with patch.object(Path, 'mkdir', side_effect=AssertionError('write')), \
                patch('subprocess.run', side_effect=AssertionError('process')):
            self.assertEqual(self.load(), self.good)
        self.assertEqual(before, {p: p.read_bytes() for p in self.root.rglob('*') if p.is_file()})
        absent = self.root / 'absent'
        self.assertEqual(load_bridge_return(state_root=absent)['status'], 'no_active_project')
        self.assertFalse(absent.exists())

    def test_missing_checkpoint_removes_suggestions(self):
        self.paths['return_checkpoint'].unlink()
        self.assertEqual(self.rejected()['status'], 'missing_evidence')

    def test_wrong_session_or_project_fails_closed(self):
        self.edit('return_session', pending_next_action='unexpected')
        self.rejected()
        self.edit('active_project', active_project_slug='other-project')
        self.rejected()

    def test_host_snapshot_disagreement(self):
        self.edit('host_snapshot', focus_target='different')
        self.rejected()

    def test_host_checkpoint_must_be_matching_predecessor(self):
        path = self.paths['return_checkpoint']
        value = json.loads(path.read_text())
        value['session_state']['last_checkpoint'] = 'unrelated'
        path.write_text(json.dumps(value))
        self.rejected()

    def test_checkpoint_path_escape(self):
        self.edit('project_return', checkpoint_path=str(self.root / 'outside.json'))
        self.assertIn('owning store', self.rejected()['message'])

    def test_symlinked_file_is_rejected(self):
        path = self.paths['return_checkpoint']
        target = self.root / 'copied.json'
        target.write_bytes(path.read_bytes())
        path.unlink()
        try:
            path.symlink_to(target)
        except OSError:
            self.skipTest('symlinks unavailable on this host')
        self.assertIn('Symlink', self.rejected()['message'])

    def test_malformed_duplicate_nonfinite_and_oversized_sources(self):
        path = self.paths['project_return']
        for raw in ('bad json', '{"x":1,"x":2}', '{"x":NaN}', ' ' * (MAX_FILE_BYTES + 1)):
            with self.subTest(raw=raw[:30]):
                path.write_text(raw)
                self.rejected()

    def test_history_must_be_project_scoped(self):
        self.paths['guidance_history'].write_text(json.dumps({
            'project_id': 'other', 'timestamp_utc': self.now.isoformat()}) + '\n')
        self.rejected()

    def test_old_saved_state_remains_useful_and_future_state_is_rejected(self):
        result = self.load(now=self.now + timedelta(days=3))
        self.assertTrue(result['verified'])
        self.assertEqual(result['freshness']['status'], 'older_saved_state')
        self.edit('project_return', captured_at=(self.now + timedelta(days=1)).isoformat())
        self.rejected()

    def test_changed_source_during_read_removes_panel(self):
        original = SnapshotReader.ensure_stable
        def changed(reader):
            self.edit('active_project', active_project_name='Changed during read')
            original(reader)
        with patch.object(SnapshotReader, 'ensure_stable', changed):
            self.assertEqual(self.rejected()['status'], 'changed_during_read')

    def test_optional_absence_is_checked_again(self):
        path = self.paths['guidance_history']
        path.unlink()
        original = SnapshotReader.ensure_stable
        def changed(reader):
            path.write_text('{}\n')
            original(reader)
        with patch.object(SnapshotReader, 'ensure_stable', changed):
            self.assertEqual(self.rejected()['status'], 'changed_during_read')

    def test_http_live_state_and_write_rejection(self):
        server = ThreadingHTTPServer(('127.0.0.1', 0), LuminaBridgeHandler)
        server.lumina_state_root = self.root
        server.lumina_runtime_base = self.runner.base_dir
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            url = f'http://127.0.0.1:{server.server_port}'
            with urlopen(url + '/api/return') as response:
                self.assertIn('no-store', response.headers['Cache-Control'])
                self.assertTrue(json.load(response)['verified'])
            with urlopen(url + '/api/bridge') as response:
                self.assertEqual(json.load(response)['workspace']['project']['slug'], 'bridge-trial')
            for method in ('POST', 'PUT', 'PATCH', 'DELETE'):
                with self.assertRaises(HTTPError) as caught:
                    urlopen(Request(url + '/api/return', method=method))
                self.assertEqual(caught.exception.code, 405)
            with self.assertRaises(HTTPError) as caught:
                urlopen(url + '/api/return?path=outside')
            self.assertEqual(caught.exception.code, 400)
            self.paths['return_checkpoint'].unlink()
            with urlopen(url + '/api/return') as response:
                self.assertIsNone(json.load(response)['panel'])
        finally:
            server.shutdown()
            server.server_close()
            thread.join()


def run_trial():
    result = unittest.TestResult()
    unittest.defaultTestLoader.loadTestsFromTestCase(BridgeReturnTrial).run(result)
    return {'trial_id': 'sea-trials-lumina-bridge-return-r1', 'passed': result.wasSuccessful(),
            'tests_run': result.testsRun,
            'failures': [{'test': str(t), 'detail': d} for t, d in result.failures],
            'errors': [{'test': str(t), 'detail': d} for t, d in result.errors]}


if __name__ == '__main__':
    receipt = run_trial()
    print(json.dumps(receipt, indent=2))
    raise SystemExit(0 if receipt['passed'] else 1)

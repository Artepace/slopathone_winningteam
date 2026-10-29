"""Safety and lifecycle tests; every subprocess is a local synthetic runner."""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import stat
import sys
import tempfile
import time
import unittest
from unittest.mock import patch
import zipfile

SCRIPT = Path(__file__).resolve().parents[1] / 'controller.py'
spec = importlib.util.spec_from_file_location('experiment_controller', SCRIPT)
controller = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(controller)


def make_submission(root: Path) -> Path:
    root.mkdir(parents=True)
    (root / 'manifest.json').write_text(json.dumps({'team': 'Winning team', 'name': 'fixture', 'mode': 'agent'}))
    (root / 'README.md').write_text('Real fixture instructions')
    (root / 'design').mkdir()
    (root / 'design/skills_design.md').write_text('Design instructions')
    (root / 'design/decision_report.md').write_text('Decision report')
    (root / 'skills/core').mkdir(parents=True)
    (root / 'skills/core/SKILL.md').write_text('---\nname: core\ndescription: Fixture skill\n---\nPlay carefully.')
    return root


def make_archive(root: Path, destination: Path, prefix: str = 'solution/') -> Path:
    with zipfile.ZipFile(destination, 'w') as archive:
        for path in root.rglob('*'):
            if path.is_file():
                archive.write(path, prefix + path.relative_to(root).as_posix())
    return destination


class ControllerTests(unittest.TestCase):
    def setUp(self):
        scratch = SCRIPT.parent / '.test-tmp'
        scratch.mkdir(exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(dir=scratch)
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.workspace = self.root / 'workspace'
        self.workspace.mkdir()
        self.state = self.workspace / '.experiments'
        self.solution = make_submission(self.root / 'source')

    def stage(self):
        return controller.stage_submission(self.solution, self.state, 'baseline')

    def test_stage_handles_wrapped_and_bare_archives_and_stable_hash(self):
        archive = make_archive(self.solution, self.root / 'one.zip')
        first = controller.stage_submission(archive, self.state, 'baseline')
        second = self.stage()
        self.assertEqual(first['id'], second['id'])
        self.assertEqual(first['sha256'], second['sha256'])
        bare = make_archive(self.solution, self.root / 'bare.zip', '')
        third = controller.stage_submission(bare, self.state, 'same-content')
        self.assertEqual(first['sha256'], third['sha256'])
        self.assertEqual(first['status'], 'awaiting_approval')

    def test_path_traversal_absolute_windows_and_private_entries_rejected(self):
        for name in ('../escape', '/tmp/escape', 'C:/escape', 'solution\\..\\escape', 'solution/.env', 'solution/.git/config'):
            with self.subTest(name=name):
                archive = self.root / 'bad.zip'
                with zipfile.ZipFile(archive, 'w') as bundle:
                    bundle.writestr(name, 'secret')
                with self.assertRaises(controller.ControllerError):
                    controller.stage_submission(archive, self.state)
        self.assertFalse((self.root / 'escape').exists())

    def test_duplicate_paths_symlink_and_bomb_rejected(self):
        archive = self.root / 'bad.zip'
        with zipfile.ZipFile(archive, 'w') as bundle:
            bundle.writestr('README.md', 'a')
            bundle.writestr('readme.md', 'b')
        with self.assertRaises(controller.ControllerError):
            controller.stage_submission(archive, self.state)
        info = zipfile.ZipInfo('link')
        info.create_system = 3
        info.external_attr = (stat.S_IFLNK | 0o777) << 16
        with zipfile.ZipFile(archive, 'w') as bundle:
            bundle.writestr(info, '/tmp/secret')
        with self.assertRaises(controller.ControllerError):
            controller.stage_submission(archive, self.state)
        with zipfile.ZipFile(archive, 'w') as bundle:
            bundle.writestr('big.txt', 'a' * 50)
        with patch.object(controller, 'MAX_SINGLE_BYTES', 40):
            with self.assertRaises(controller.ControllerError):
                controller.stage_submission(archive, self.state)

    def test_missing_required_document_rejected_without_publishing_candidate(self):
        (self.solution / 'design/decision_report.md').unlink()
        with self.assertRaises(controller.ControllerError):
            self.stage()
        self.assertEqual(list((self.state / 'candidates').iterdir()), [])

    def test_tampered_candidate_cannot_run(self):
        candidate = self.stage()
        path = Path(candidate['submission']) / 'README.md'
        path.chmod(0o644)
        path.write_text('tampered')
        with self.assertRaisesRegex(controller.ControllerError, 'changed after staging'):
            controller.get_candidate(self.state, candidate['id'])

    def test_approval_gate_precedes_all_game_work(self):
        with patch.object(controller.subprocess, 'Popen') as process:
            with self.assertRaisesRegex(controller.ControllerError, 'approval'):
                controller.run_candidate(self.workspace, self.state, 'anything', approved=False)
            process.assert_not_called()

    def test_lock_prevents_second_run_and_cannot_recover_live_owner(self):
        controller.initialize(self.state)
        lock = self.state / 'run.lock'
        with controller.RunLock(lock, 'run-one'):
            with self.assertRaises(controller.ControllerError):
                with controller.RunLock(lock, 'run-two'):
                    pass
            with self.assertRaisesRegex(controller.ControllerError, 'still running'):
                controller.recover_lock(self.state)
        self.assertFalse(lock.exists())

    def test_external_game_blocks_run_before_preflight(self):
        candidate = self.stage()
        with patch.object(controller, 'find_game_processes', return_value=[{'pid': 123}]), \
                patch.object(controller, 'runtime_preflight') as preflight:
            with self.assertRaisesRegex(controller.ControllerError, 'Another'):
                controller.run_candidate(self.workspace, self.state, candidate['id'], True)
            preflight.assert_not_called()
        self.assertFalse((self.state / 'run.lock').exists())

    def prepare_report(self, output_name='new', submission=None):
        root = controller.runtime_root(self.workspace)
        output = root / 'outputs/Winning team' / output_name
        output.mkdir(parents=True)
        (root / 'last_output_dir.txt').write_text(str(output))
        report = {'submission_dir': str(submission or self.solution), 'play_exit_code': 0, 'termination_reason': None,
                  'ending_score': {'quantitative_score': 26.24, 'survival_months': 19, 'completed': False, 'outcome': 'fired'},
                  'token_usage': {'total_tokens': 1000}}
        controller.write_json(output / 'score_report.json', report)
        return output, report

    def test_early_game_failure_is_a_valid_result(self):
        _, report = self.prepare_report()
        self.assertEqual(controller.summarize_report(report, 0)['status'], 'awaiting_analysis')
        report['termination_reason'] = 'api_error'
        self.assertEqual(controller.summarize_report(report, 1)['status'], 'infrastructure_error')

    def test_old_report_wrong_submission_and_path_escape_are_not_attributed(self):
        output, _ = self.prepare_report()
        before = controller.report_stamp(output)
        with self.assertRaisesRegex(controller.ControllerError, 'old unchanged'):
            controller.fresh_output(self.workspace, before, time.time() - 1)
        with self.assertRaisesRegex(controller.ControllerError, 'another submission'):
            controller.fresh_output(self.workspace, None, time.time() - 1, self.root / 'different')
        (controller.runtime_root(self.workspace) / 'last_output_dir.txt').write_text(str(self.root))
        with self.assertRaisesRegex(controller.ControllerError, 'outside'):
            controller.output_pointer(self.workspace)

    def test_progress_is_from_structured_tool_result_not_agent_text(self):
        output, _ = self.prepare_report()
        event = output / 'events-one.jsonl'
        rows = [{'kind': 'tool_result', 'ts': 'first', 'payload': {'delta': {
                    'tool_name': 'mcp_career-emulator-engine_observe', 'raw_output': {'result': json.dumps({
                        'current_state': {'time': {'current_month': 18}},
                        'choices': [{'future_month': 48, 'current_month': 48}]})}}}},
                {'kind': 'text', 'ts': 'last', 'month': 48}]
        event.write_text('\n'.join(json.dumps(row) for row in rows) + '\n')
        details = controller.public_progress(output)
        self.assertEqual(details['latest_observed_month'], 18)
        self.assertEqual(details['last_event_at'], 'last')

    def test_watch_remains_active_for_external_game_when_controller_idle(self):
        self.assertTrue(controller.watch_active({'status': 'idle', 'external_game_processes': [{'pid': 123}]}))
        self.assertFalse(controller.watch_active({'status': 'awaiting_approval', 'external_game_processes': []}))

    def test_new_managed_run_does_not_display_previous_game_progress(self):
        output, _ = self.prepare_report()
        (output / 'events-one.jsonl').write_text(json.dumps({'kind': 'frame_final', 'ts': 'old'}) + '\n')
        controller.initialize(self.state)
        controller.write_json(self.state / 'status.json', {
            'status': 'running', 'controller_pid': os.getpid(), 'started_at': controller.now(),
            'previous_output_dir': str(output)})
        with patch.object(controller, 'find_game_processes', return_value=[]):
            self.assertIsNone(controller.current_status(self.workspace, self.state)['progress'])

    def install_fake_runner(self, exit_code=0, write_report=True):
        module = self.workspace / 'career_sim_runner'
        module.mkdir()
        (module / '__init__.py').write_text('')
        (module / '__main__.py').write_text('''import json,sys,time
from pathlib import Path
root=Path.cwd()/'.career_sim_runner'/'career_emu'
output=root/'outputs'/'Fixture'/str(time.time_ns())
output.mkdir(parents=True)
(root/'last_output_dir.txt').write_text(str(output))
submission=sys.argv[sys.argv.index('--submission')+1]
print('Month 48: fixture complete', flush=True)
report={'submission_dir': submission, 'play_exit_code': EXIT, 'termination_reason': None,
        'ending_score': {'quantitative_score': 65, 'survival_months':48,'outcome':'completed','completed':True},
        'token_usage':{'total_tokens':99}}
if WRITE: (output/'score_report.json').write_text(json.dumps(report))
sys.exit(EXIT)
'''.replace('EXIT', str(exit_code)).replace('WRITE', repr(write_report)))

    def fake_run(self, candidate):
        with patch.object(controller, 'runtime_preflight'), \
                patch.object(controller, 'ensure_service'), \
                patch.object(controller, 'find_game_processes', return_value=[]), \
                patch.object(controller, 'python_executable', return_value=Path(sys.executable)), \
                contextlib.redirect_stdout(io.StringIO()):
            return controller.run_candidate(self.workspace, self.state, candidate['id'], True, 60)

    def test_full_local_lifecycle_freezes_snapshot_and_waits_for_analysis(self):
        self.install_fake_runner()
        candidate = self.stage()
        result = self.fake_run(candidate)
        self.assertEqual(result['status'], 'awaiting_analysis')
        self.assertFalse((self.state / 'run.lock').exists())
        self.assertEqual(controller.read_json(self.state / 'status.json')['status'], 'awaiting_analysis')
        self.assertEqual(controller.submission_digest(Path(result['submission'])), candidate['sha256'])
        run_root = self.state / 'runs' / result['id']
        self.assertTrue((run_root / 'summary.json').exists())
        self.assertIn('fixture complete', (run_root / 'console.log').read_text())
        self.assertEqual(len(list((self.state / 'runs').iterdir())), 1)

    def test_failed_subprocess_does_not_reuse_previous_score(self):
        self.prepare_report(output_name='old')
        self.install_fake_runner(exit_code=1, write_report=False)
        result = self.fake_run(self.stage())
        self.assertEqual(result['status'], 'infrastructure_error')
        self.assertNotIn('summary', result)
        self.assertIn('without a score report', result['error'])

    def test_real_recorded_reports_all_count_as_game_results(self):
        fixtures = Path(os.environ.get('CAREER_TEST_REPORTS', str(SCRIPT.parent.parent / 'analysis_results3_final')))
        if not fixtures.is_dir():
            fixtures = SCRIPT.parent / 'tests/fixtures/reports'
        found = list(fixtures.glob('career_emu_*/score_report.json'))
        self.assertEqual(len(found), 3)
        months = []
        for path in found:
            summary = controller.summarize_report(json.loads(path.read_text()), 0)
            self.assertEqual(summary['status'], 'awaiting_analysis')
            months.append(summary['survival_months'])
        self.assertIn(19, months)
        self.assertEqual(months.count(48), 2)

    def test_reviewed_marker_prevents_repeating_analysis_and_does_not_launch(self):
        self.install_fake_runner()
        candidate = self.stage()
        result = self.fake_run(candidate)
        analysis = self.workspace / 'analysis.md'
        analysis.write_text('Observed outcome and proposed changes.')
        with patch.object(controller.subprocess, 'Popen') as process:
            reviewed = controller.mark_reviewed(self.workspace, self.state, result['id'], analysis, candidate['id'])
            process.assert_not_called()
        self.assertEqual(reviewed['status'], 'awaiting_approval')
        self.assertEqual(controller.read_json(self.state / 'status.json')['status'], 'awaiting_approval')

    def test_existing_ready_service_is_reused(self):
        with patch.object(controller, 'backend_reachable', return_value=True), \
                patch.object(controller.subprocess, 'Popen') as process:
            self.assertEqual(controller.ensure_service(self.workspace, self.state), 'reused')
            process.assert_not_called()

    def test_stopped_service_is_started_once_and_checked(self):
        binary_dir = self.root / 'bin'
        binary_dir.mkdir()
        binary = binary_dir / ('jiuwenswarm-start.exe' if os.name == 'nt' else 'jiuwenswarm-start')
        binary.write_text('fixture')
        fake = unittest.mock.MagicMock()
        fake.pid = 987654
        fake.poll.return_value = None
        listed = subprocess_result = unittest.mock.Mock(returncode=0, stdout='career_emu stopped - /home/user/instance 19092/20000/20001/6173')
        with patch.object(controller, 'backend_reachable', side_effect=[False, True]), \
                patch.object(controller, 'python_executable', return_value=binary_dir / 'python'), \
                patch.object(controller.subprocess, 'run', return_value=listed), \
                patch.object(controller.subprocess, 'Popen', return_value=fake) as process:
            self.assertEqual(controller.ensure_service(self.workspace, self.state), 'started')
            self.assertEqual(process.call_count, 1)
            self.assertTrue((self.state / 'service.json').exists())


if __name__ == '__main__':
    unittest.main()

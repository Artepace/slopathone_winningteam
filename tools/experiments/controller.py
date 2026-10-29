#!/usr/bin/env python3
"""Local, explicit-approval Career Survival experiment controller (no model API).

Only the ``run --approved`` command starts a game. All other commands are local
file inspection or staging. Run this file with the project's Python environment.
"""
from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import math
import os
from pathlib import Path, PurePosixPath
import queue
import re
import shutil
import signal
import stat
import subprocess
import sys
import tempfile
import threading
import time
from datetime import datetime, timezone
from typing import Any
import uuid
import zipfile

SCHEMA_VERSION = 1
MAX_FILES = 2000
MAX_BYTES = 150 * 1024 * 1024
MAX_SINGLE_BYTES = 100 * 1024 * 1024
REQUIRED = ('manifest.json', 'README.md', 'design/skills_design.md', 'design/decision_report.md')
FORBIDDEN_PARTS = {'.git', '.venv', '__pycache__', '.career_sim_runner', '.experiments', 'node_modules'}
TERMINAL = {'awaiting_analysis', 'infrastructure_error', 'timed_out', 'interrupted'}


class ControllerError(RuntimeError):
    """An actionable controller error."""


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_json(path: Path, default: Any = None) -> Any:
    try:
        return json.loads(path.read_text(encoding='utf-8-sig'))
    except FileNotFoundError:
        return default
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ControllerError(f'Invalid JSON file: {path}') from exc


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + '.' + uuid.uuid4().hex + '.tmp')
    try:
        temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def inside(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def file_digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def submission_digest(path: Path) -> str:
    digest = hashlib.sha256()
    # pathlib sorting is case-insensitive on Windows; use the same order on Linux.
    for item in sorted(path.rglob('*'), key=lambda item: item.relative_to(path).parts):
        if item.is_symlink():
            raise ControllerError(f'Symlink in submission: {item}')
        if item.is_file():
            digest.update(item.relative_to(path).as_posix().encode('utf-8'))
            digest.update(b'\0')
            digest.update(bytes.fromhex(file_digest(item)))
    return digest.hexdigest()


def checked_member(name: str) -> PurePosixPath:
    if '\\' in name or '\x00' in name:
        raise ControllerError(f'Unsafe archive path: {name!r}')
    path = PurePosixPath(name)
    if path.is_absolute() or '..' in path.parts or not path.parts:
        raise ControllerError(f'Unsafe archive path: {name!r}')
    if any(':' in part for part in path.parts):
        raise ControllerError(f'Unsafe archive path: {name!r}')
    if any(part.casefold() in FORBIDDEN_PARTS or part.casefold().startswith('.env') for part in path.parts):
        raise ControllerError(f'Unexpected private/runtime file in submission archive: {name!r}')
    return path


def extract_archive(archive: Path, target: Path) -> None:
    seen: set[str] = set()
    total = 0
    try:
        with zipfile.ZipFile(archive) as bundle:
            entries = bundle.infolist()
            if len(entries) > MAX_FILES:
                raise ControllerError('Archive has too many entries')
            for entry in entries:
                rel = checked_member(entry.filename)
                key = str(rel).casefold().rstrip('/')
                if key in seen:
                    raise ControllerError(f'Duplicate archive path: {entry.filename}')
                seen.add(key)
                mode = (entry.external_attr >> 16) & 0xFFFF
                if stat.S_ISLNK(mode) or (mode and stat.S_IFMT(mode) not in (0, stat.S_IFREG, stat.S_IFDIR)):
                    raise ControllerError(f'Unsupported archive entry: {entry.filename}')
                if entry.flag_bits & 1:
                    raise ControllerError('Encrypted archives are not supported')
                total += entry.file_size
                if entry.file_size > MAX_SINGLE_BYTES or total > MAX_BYTES:
                    raise ControllerError('Archive exceeds the extraction size limit')
                destination = target.joinpath(*rel.parts)
                if not inside(destination, target):
                    raise ControllerError('Archive path escapes extraction folder')
                if entry.is_dir():
                    destination.mkdir(parents=True, exist_ok=True)
                    continue
                destination.parent.mkdir(parents=True, exist_ok=True)
                with bundle.open(entry) as source, destination.open('xb') as output:
                    copied = 0
                    while block := source.read(1024 * 1024):
                        copied += len(block)
                        if copied > entry.file_size or copied > MAX_SINGLE_BYTES:
                            raise ControllerError('Archive entry exceeds declared size')
                        output.write(block)
    except (zipfile.BadZipFile, OSError, RuntimeError) as exc:
        if isinstance(exc, ControllerError):
            raise
        raise ControllerError(f'Cannot extract archive: {exc}') from exc


def copy_submission_tree(source: Path, destination: Path) -> None:
    files = list(source.rglob('*'))
    if len(files) > MAX_FILES:
        raise ControllerError('Submission contains too many files')
    total = 0
    for item in files:
        relative = item.relative_to(source)
        checked_member(relative.as_posix())
        if item.is_symlink():
            raise ControllerError(f'Symlinks are not allowed: {relative}')
        if item.is_file():
            size = item.stat().st_size
            total += size
            if size > MAX_SINGLE_BYTES or total > MAX_BYTES:
                raise ControllerError('Submission exceeds the size limit')
        elif not item.is_dir():
            raise ControllerError(f'Unsupported special file: {relative}')
    shutil.copytree(source, destination)


def find_submission_root(extracted: Path) -> Path:
    candidates = [parent for parent in [extracted, *extracted.rglob('*')]
                  if parent.is_dir() and (parent / 'manifest.json').is_file() and (parent / 'skills').is_dir()]
    if len(candidates) != 1:
        raise ControllerError(f'Expected exactly one submission root; found {len(candidates)}')
    return candidates[0]


def validate_basic(path: Path) -> dict[str, Any]:
    for relative in REQUIRED:
        item = path / relative
        if not item.is_file() or not item.read_text(encoding='utf-8-sig').strip():
            raise ControllerError(f'Missing or empty required file: {relative}')
    manifest = read_json(path / 'manifest.json')
    if not isinstance(manifest, dict) or manifest.get('mode') != 'agent':
        raise ControllerError('manifest.json must set mode to agent')
    if not str(manifest.get('team', '')).strip() or str(manifest.get('team', '')).casefold() in {'your-team-name', 'enter your team name here'}:
        raise ControllerError('manifest.json must contain a real team name')
    skills = list((path / 'skills').glob('*/SKILL.md'))
    if not skills:
        raise ControllerError('No skills/*/SKILL.md found')
    for skill in skills:
        text = skill.read_text(encoding='utf-8-sig')
        if not text.startswith('---\n') and not text.startswith('---\r\n'):
            raise ControllerError(f'Missing skill front matter: {skill.relative_to(path)}')
    return {'team': manifest['team'], 'mode': manifest['mode'], 'skill_count': len(skills)}


def make_read_only(root: Path) -> None:
    for path in root.rglob('*'):
        if path.is_file():
            path.chmod(stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
    # Directories stay traversable/writable for portable copying and cleanup.
    # A content hash is rechecked immediately before each run as the integrity guard.


def python_executable(workspace: Path) -> Path:
    executable = workspace / '.venv' / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
    if not executable.is_file():
        raise ControllerError(f'Project Python not found: {executable}. Run uv sync first.')
    return executable


def process_identity(pid: int) -> str | None:
    try:
        text = Path(f'/proc/{pid}/stat').read_text()
        return text[text.rindex(')') + 2:].split()[19]
    except (FileNotFoundError, PermissionError, ValueError, IndexError):
        return None


def process_alive(pid: int | None, identity: str | None = None) -> bool:
    if not pid:
        return False
    if os.name == 'nt':
        # os.kill(pid, 0) is not a harmless probe on Windows. Query a handle.
        import ctypes
        kernel = ctypes.WinDLL('kernel32', use_last_error=True)
        kernel.OpenProcess.restype = ctypes.c_void_p
        kernel.OpenProcess.argtypes = (ctypes.c_ulong, ctypes.c_int, ctypes.c_ulong)
        kernel.GetExitCodeProcess.argtypes = (ctypes.c_void_p, ctypes.POINTER(ctypes.c_ulong))
        kernel.CloseHandle.argtypes = (ctypes.c_void_p,)
        handle = kernel.OpenProcess(0x1000, False, int(pid))
        if not handle:
            return ctypes.get_last_error() == 5
        try:
            code = ctypes.c_ulong()
            return bool(kernel.GetExitCodeProcess(handle, ctypes.byref(code))) and code.value == 259
        finally:
            kernel.CloseHandle(handle)
    try:
        os.kill(int(pid), 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return not identity or process_identity(int(pid)) == identity


def find_game_processes(workspace: Path | None = None) -> list[dict[str, Any]]:
    """Read Linux process command lines only; never inspect the game database."""
    proc = Path('/proc')
    if not proc.is_dir():
        return []
    result = []
    for item in proc.iterdir():
        if not item.name.isdigit():
            continue
        try:
            args = (item / 'cmdline').read_bytes().decode('utf-8', 'replace').split('\0')
        except (FileNotFoundError, PermissionError, ProcessLookupError):
            continue
        if 'career_sim_runner' in args and 'play' in args:
            if workspace is not None:
                try:
                    if (item / 'cwd').resolve() != workspace.resolve():
                        continue
                except OSError:
                    continue
            pid = int(item.name)
            result.append({'pid': pid, 'identity': process_identity(pid)})
    return result


class RunLock:
    def __init__(self, path: Path, run_id: str):
        self.path = path
        self.record = {'run_id': run_id, 'controller_pid': os.getpid(), 'controller_identity': process_identity(os.getpid()),
                       'created_at': now(), 'token': uuid.uuid4().hex}

    def __enter__(self) -> 'RunLock':
        self.path.parent.mkdir(parents=True, exist_ok=True)
        try:
            descriptor = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except FileExistsError as exc:
            raise ControllerError('A run lock exists. Use status; recover-lock is allowed only after all game processes stop.') from exc
        with os.fdopen(descriptor, 'w', encoding='utf-8') as handle:
            json.dump(self.record, handle)
        return self

    def child_started(self, pid: int) -> None:
        self.record.update(child_pid=pid, child_identity=process_identity(pid))
        write_json(self.path, self.record)

    def __exit__(self, *_: Any) -> None:
        current = read_json(self.path, {})
        if current.get('token') == self.record['token']:
            self.path.unlink(missing_ok=True)


def runtime_root(workspace: Path) -> Path:
    return workspace / '.career_sim_runner' / 'career_emu'


def output_pointer(workspace: Path) -> Path | None:
    pointer = runtime_root(workspace) / 'last_output_dir.txt'
    if not pointer.is_file():
        return None
    text = pointer.read_text(encoding='utf-8').strip()
    if not text:
        return None
    output = Path(text)
    if not output.is_absolute():
        output = workspace / output
    if not inside(output, runtime_root(workspace) / 'outputs'):
        raise ControllerError('Runner output pointer is outside its public output directory')
    return output.resolve()


def report_stamp(path: Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    report = path / 'score_report.json'
    if not report.is_file():
        return {'output': str(path), 'report_hash': None}
    return {'output': str(path), 'report_hash': file_digest(report)}


def public_progress(output: Path | None) -> dict[str, Any] | None:
    """Read only a bounded tail of the public event stream; no hidden game state."""
    if output is None or not output.is_dir():
        return None
    streams = list(output.glob('events-*.jsonl'))
    if not streams:
        return None
    stream = max(streams, key=lambda path: path.stat().st_mtime)
    details: dict[str, Any] = {'events_file': str(stream), 'events_modified_at': stream.stat().st_mtime,
                               'events_size_bytes': stream.stat().st_size}
    with stream.open('rb') as handle:
        offset = max(0, stream.stat().st_size - 256 * 1024)
        handle.seek(offset)
        lines = handle.read().decode('utf-8', 'replace').splitlines()
    if offset and lines:
        lines = lines[1:]
    for raw in lines:
        try:
            event = json.loads(raw)
        except json.JSONDecodeError:
            continue
        details['last_event_at'] = event.get('ts')
        details['last_event_kind'] = event.get('kind')
        # Month is reported only from tool-result structured state, not agent prose.
        if event.get('kind') not in {'tool_result', 'tool_call_result'}:
            continue
        payload = event.get('payload', event)
        if not isinstance(payload, dict):
            continue
        payload = payload.get('delta', payload)
        if not isinstance(payload, dict):
            continue
        tool_name = payload.get('tool_name', '')
        if tool_name not in {'mcp_career-emulator-engine_observe', 'mcp_career-emulator-engine_take_action',
                             'mcp_career-emulator-engine_new_game'}:
            continue
        value = payload.get('raw_output')
        for _ in range(6):
            if isinstance(value, str):
                try:
                    value = json.loads(value)
                except (json.JSONDecodeError, RecursionError):
                    break
            elif isinstance(value, dict) and isinstance(value.get('current_state'), dict):
                current_time = value['current_state'].get('time', {})
                month = current_time.get('current_month') if isinstance(current_time, dict) else None
                if isinstance(month, int) and not isinstance(month, bool) and 0 <= month <= 48:
                    details['latest_observed_month'] = month
                break
            elif isinstance(value, dict) and 'result' in value:
                value = value['result']
            else:
                break
    return details


def fresh_output(workspace: Path, before: dict[str, Any] | None, started_at: float,
                 expected_submission: Path | None = None) -> Path:
    output = output_pointer(workspace)
    if output is None:
        raise ControllerError('Runner did not record an output directory')
    report = output / 'score_report.json'
    if not report.is_file():
        raise ControllerError('Runner ended without a score report')
    after = report_stamp(output)
    if before == after:
        raise ControllerError('Only an old unchanged score report exists')
    if report.stat().st_mtime < started_at - 2:
        raise ControllerError('Score report predates this run')
    payload = read_json(report)
    if expected_submission is not None:
        raw = payload.get('submission_dir')
        if not isinstance(raw, str) or Path(raw).resolve() != expected_submission.resolve():
            raise ControllerError('Score report belongs to another submission')
    return output


def number(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (float, int)) or not math.isfinite(value):
        return None
    return value


def summarize_report(report: dict[str, Any], process_exit_code: int | None = None) -> dict[str, Any]:
    ending = report.get('ending_score') or {}
    usage = report.get('token_usage') or {}
    score = number(ending.get('quantitative_score'))
    months = number(ending.get('survival_months'))
    outcome = ending.get('outcome')
    valid_outcome = isinstance(outcome, str) and outcome.strip() and outcome not in {'unknown', 'in_progress'}
    valid_terminal = (valid_outcome and score is not None and 0 <= score <= 100 and
                      months is not None and 0 <= months <= 48 and report.get('play_exit_code') == 0 and
                      process_exit_code in (None, 0) and not report.get('termination_reason'))
    return {'status': 'awaiting_analysis' if valid_terminal else 'infrastructure_error',
            'quantitative_score': score, 'survival_months': months, 'completed': ending.get('completed'),
            'outcome': outcome, 'token_usage': usage, 'termination_reason': report.get('termination_reason'),
            'play_exit_code': report.get('play_exit_code'), 'process_exit_code': process_exit_code,
            'dimensions': ending.get('dimensions', []), 'scored_at': report.get('scored_at'),
            'session_id': report.get('session_id'), 'output_dir': report.get('output_dir')}


def load_layout(workspace: Path, state_dir: Path | None = None) -> tuple[Path, Path]:
    workspace = workspace.expanduser().resolve()
    state = (state_dir or workspace / '.experiments').expanduser().resolve()
    if state == workspace or state in workspace.parents:
        raise ControllerError('State directory cannot be the workspace or an ancestor')
    return workspace, state


def initialize(state: Path) -> None:
    for child in ('candidates', 'runs', 'incoming'):
        (state / child).mkdir(parents=True, exist_ok=True)
    if not (state / 'state.json').exists():
        write_json(state / 'state.json', {'schema_version': SCHEMA_VERSION, 'created_at': now(), 'latest_run': None})
    if not (state / 'status.json').exists():
        write_json(state / 'status.json', {'schema_version': SCHEMA_VERSION, 'status': 'idle', 'updated_at': now()})


def stage_submission(source: Path, state: Path, name: str | None = None, provenance: str = 'local') -> dict[str, Any]:
    initialize(state)
    source = source.expanduser().resolve(strict=True)
    with tempfile.TemporaryDirectory(prefix='stage-', dir=state) as temporary:
        staging = Path(temporary)
        if source.is_dir():
            copy_submission_tree(source, staging / 'extracted')
        else:
            (staging / 'extracted').mkdir()
            extract_archive(source, staging / 'extracted')
        root = find_submission_root(staging / 'extracted')
        layout = validate_basic(root)
        digest = submission_digest(root)
        slug = re.sub(r'[^a-z0-9]+', '-', (name or source.stem).lower()).strip('-')[:40] or 'solution'
        candidate_id = f'{slug}-{digest[:12]}'
        destination = state / 'candidates' / candidate_id
        metadata = {'schema_version': SCHEMA_VERSION, 'id': candidate_id, 'name': name or source.stem,
                    'created_at': now(), 'sha256': digest, 'source': provenance,
                    'source_path': str(source), 'archive_sha256': file_digest(source) if source.is_file() else None,
                    'submission': str(destination / 'submission'), 'validation': layout,
                    'status': 'awaiting_approval'}
        if destination.exists():
            existing = read_json(destination / 'candidate.json')
            if submission_digest(destination / 'submission') != digest:
                raise ControllerError('Existing candidate has changed; stage under a new name')
            return existing
        complete = staging / 'candidate'
        complete.mkdir()
        copy_submission_tree(root, complete / 'submission')
        make_read_only(complete / 'submission')
        write_json(complete / 'candidate.json', metadata)
        os.rename(complete, destination)
        return metadata


def get_candidate(state: Path, candidate_id: str) -> tuple[Path, dict[str, Any]]:
    if not re.fullmatch(r'[a-z0-9][a-z0-9-]*', candidate_id):
        raise ControllerError('Invalid candidate id')
    root = state / 'candidates' / candidate_id
    metadata = read_json(root / 'candidate.json')
    if not metadata:
        raise ControllerError(f'Candidate does not exist: {candidate_id}')
    if submission_digest(root / 'submission') != metadata['sha256']:
        raise ControllerError('Candidate content changed after staging; stage the changed directory as a new candidate')
    return root, metadata


def update_status(state: Path, run: dict[str, Any]) -> None:
    record = dict(run, updated_at=now(), schema_version=SCHEMA_VERSION)
    write_json(state / 'runs' / run['id'] / 'run.json', record)
    write_json(state / 'status.json', record)
    registry = read_json(state / 'state.json', {})
    registry['latest_run'] = run['id']
    registry['updated_at'] = now()
    write_json(state / 'state.json', registry)


def runtime_preflight(workspace: Path, submission: Path) -> None:
    executable = python_executable(workspace)
    program = (
        'import asyncio,sys; from pathlib import Path; '
        'from career_sim_runner.validate import validate_submission; '
        'from career_sim_runner.setup import resolve_instance_ws_url; '
        'from career_sim_runner.ws_client import check_backend; '
        'r=validate_submission(Path(sys.argv[1]),require_presentation=False); '
        'assert r.ok, str(r); '
        'assert asyncio.run(check_backend(resolve_instance_ws_url())), "JiuwenSwarm backend is not reachable"; '
        'print("Local validation and backend connection: OK")'
    )
    env = os.environ.copy()
    env['PATH'] = str(executable.parent) + os.pathsep + env.get('PATH', '')
    result = subprocess.run([str(executable), '-c', program, str(submission)], cwd=workspace,
                            env=env, capture_output=True, text=True, timeout=30)
    if result.returncode:
        detail = (result.stderr or result.stdout)[-4000:]
        raise ControllerError(f'Preflight failed (no game started): {detail}')


def project_environment(workspace: Path) -> dict[str, str]:
    env = os.environ.copy()
    env['PATH'] = str(python_executable(workspace).parent) + os.pathsep + env.get('PATH', '')
    return env


def backend_reachable(workspace: Path) -> bool:
    program = ('import asyncio; from career_sim_runner.setup import resolve_instance_ws_url; '
               'from career_sim_runner.ws_client import check_backend; '
               'raise SystemExit(0 if asyncio.run(check_backend(resolve_instance_ws_url(),timeout_s=2)) else 1)')
    result = subprocess.run([str(python_executable(workspace)), '-c', program], cwd=workspace,
                            env=project_environment(workspace), stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL, timeout=10)
    return result.returncode == 0


def ensure_service(workspace: Path, state: Path, wait_seconds: int = 60) -> str:
    """Start a stopped configured service only as part of an approved game launch."""
    if backend_reachable(workspace):
        return 'reused'
    binary = python_executable(workspace).parent / ('jiuwenswarm-start.exe' if os.name == 'nt' else 'jiuwenswarm-start')
    if not binary.is_file():
        raise ControllerError(f'JiuwenSwarm launcher not found: {binary}')
    result = subprocess.run([str(binary), '--list'], cwd=workspace, env=project_environment(workspace),
                            capture_output=True, text=True, timeout=15)
    if result.returncode:
        raise ControllerError('Cannot list JiuwenSwarm instances; run project setup first')
    line = next((line.split() for line in result.stdout.splitlines() if line.split() and line.split()[0] == 'career_emu'), None)
    if not line or len(line) < 2 or line[1] not in {'running', 'stopped'}:
        raise ControllerError('Configured career_emu instance not found; run project setup first')
    started = False
    service = None
    if line[1] == 'stopped':
        state.mkdir(parents=True, exist_ok=True)
        with (state / 'service.log').open('a', encoding='utf-8') as log:
            service = subprocess.Popen([str(binary), '--name', 'career_emu', 'all'], cwd=workspace,
                                       env=project_environment(workspace), stdout=log, stderr=subprocess.STDOUT,
                                       stdin=subprocess.DEVNULL, start_new_session=os.name == 'posix')
        write_json(state / 'service.json', {'pid': service.pid, 'identity': process_identity(service.pid),
                                          'started_at': now(), 'log': str(state / 'service.log')})
        started = True
    deadline = time.monotonic() + wait_seconds
    while time.monotonic() < deadline:
        if backend_reachable(workspace):
            return 'started' if started else 'waited_for_existing'
        if service is not None and service.poll() is not None:
            raise ControllerError(f'JiuwenSwarm stopped during startup; inspect {state / "service.log"}')
        time.sleep(2)
    raise ControllerError('JiuwenSwarm did not become ready. No duplicate service or game was started; inspect service.log.')


def terminate_child(child: subprocess.Popen[str]) -> None:
    if child.poll() is None:
        with contextlib.suppress(ProcessLookupError):
            if os.name == 'posix':
                os.killpg(child.pid, signal.SIGTERM)
            else:
                child.terminate()
        try:
            child.wait(timeout=8)
        except subprocess.TimeoutExpired:
            if os.name == 'posix':
                os.killpg(child.pid, signal.SIGKILL)
            else:
                child.kill()
            child.wait()


def run_candidate(workspace: Path, state: Path, candidate_id: str, approved: bool,
                  timeout_seconds: int = 7500, isolated: bool = False) -> dict[str, Any]:
    if not approved:
        raise ControllerError('Game not started: explicit approval is required. Add --approved only after user authorization.')
    if not 60 <= timeout_seconds <= 14400:
        raise ControllerError('Timeout must be between 60 and 14400 seconds')
    if isolated:
        validate_worker_isolation(workspace)
    initialize(state)
    source, candidate = get_candidate(state, candidate_id)
    run_id = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-' + uuid.uuid4().hex[:6]
    with RunLock(state / 'run.lock', run_id) as lock:
        if (find_game_processes(workspace) if isolated else find_game_processes()):
            raise ControllerError('Another Career Survival game is running. Current run was left untouched.')
        ensure_service(workspace, state)
        runtime_preflight(workspace, source / 'submission')
        run_root = state / 'runs' / run_id
        run_root.mkdir()
        copy_submission_tree(source / 'submission', run_root / 'submission')
        make_read_only(run_root / 'submission')
        snapshot = run_root / 'submission'
        if submission_digest(snapshot) != candidate['sha256']:
            raise ControllerError('Candidate changed while snapshotting; no game was started')
        before = report_stamp(output_pointer(workspace))
        started_at = time.time()
        run = {'id': run_id, 'candidate_id': candidate_id, 'submission_sha256': candidate['sha256'],
               'submission': str(snapshot), 'status': 'running', 'started_at': now(),
               'controller_pid': os.getpid(), 'controller_identity': process_identity(os.getpid()),
               'timeout_seconds': timeout_seconds, 'approved': True, 'output_dir': None,
               'previous_output_dir': before.get('output') if before else None,
               'console_log': str(run_root / 'console.log')}
        update_status(state, run)
        executable = python_executable(workspace)
        command = [str(executable), '-u', '-m', 'career_sim_runner', 'play', '--submission', str(snapshot),
                   '--timeout-s', str(max(30, timeout_seconds - 15))]
        env = os.environ.copy()
        env['PATH'] = str(executable.parent) + os.pathsep + env.get('PATH', '')
        env['PYTHONUNBUFFERED'] = '1'
        env['NO_COLOR'] = '1'
        child: subprocess.Popen[str] | None = None
        terminal_state: str | None = None
        print(f'Run {run_id} | {candidate_id}', flush=True)
        try:
            child = subprocess.Popen(command, cwd=workspace, env=env, stdout=subprocess.PIPE,
                                     stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='replace',
                                     start_new_session=os.name == 'posix', bufsize=1)
            lock.child_started(child.pid)
            run.update(child_pid=child.pid, child_identity=process_identity(child.pid))
            update_status(state, run)
            lines: queue.Queue[str | None] = queue.Queue(maxsize=1000)

            def reader() -> None:
                assert child is not None and child.stdout is not None
                try:
                    for line in child.stdout:
                        lines.put(line)
                finally:
                    lines.put(None)

            reader_thread = threading.Thread(target=reader, daemon=True)
            reader_thread.start()
            ended = False
            with (run_root / 'console.log').open('w', encoding='utf-8') as log:
                while not ended:
                    if time.time() - started_at > timeout_seconds:
                        terminal_state = 'timed_out'
                        terminate_child(child)
                    try:
                        line = lines.get(timeout=0.5)
                    except queue.Empty:
                        if child.poll() is not None and not reader_thread.is_alive():
                            break
                        continue
                    if line is None:
                        ended = True
                    else:
                        log.write(line)
                        log.flush()
                        print(line, end='', flush=True)
            child.wait()
            run['process_exit_code'] = child.returncode
            if terminal_state:
                run['status'] = terminal_state
            else:
                output = fresh_output(workspace, before, started_at, snapshot)
                report = read_json(output / 'score_report.json')
                summary = summarize_report(report, child.returncode)
                summary.update(run_id=run_id, candidate_id=candidate_id, submission_sha256=candidate['sha256'])
                write_json(run_root / 'score_report.json', report)
                write_json(run_root / 'summary.json', summary)
                run.update(status=summary['status'], output_dir=str(output), summary=str(run_root / 'summary.json'))
        except KeyboardInterrupt:
            run['status'] = 'interrupted'
            if child:
                terminate_child(child)
        except Exception as exc:
            run.update(status='infrastructure_error', error=str(exc))
            if child:
                terminate_child(child)
        finally:
            if child and child.stdout:
                child.stdout.close()
            run['finished_at'] = now()
            update_status(state, run)
        print(f'\nRun finished: {run["status"]}. A next game needs a new explicit approval.', flush=True)
        return run


def validate_worker_isolation(workspace: Path) -> None:
    """Allow scoped concurrency only inside a verified separate worker workspace."""
    marker = read_json(workspace / '.career-lab-worker.json')
    if not marker:
        raise ControllerError('Missing worker isolation manifest')
    parent = Path(marker['parent_workspace']).resolve()
    home = Path(marker['home']).resolve()
    expected = Path(marker['workspace']).resolve()
    if (workspace.resolve() != expected or not inside(workspace, parent / '.experiments' / 'parallel')
            or home == Path(marker['parent_home']).resolve() or not inside(home, workspace.parent)
            or Path.home().resolve() != home or os.environ.get('JIUWENSWARM_HOME') != str(home)
            or os.environ.get('JIUWENSWARM_DATA_DIR') != str(home / '.jiuwenswarm-instances' / 'career_emu')):
        raise ControllerError('Worker HOME, workspace and JiuwenSwarm paths are not isolated')


def current_status(workspace: Path, state: Path) -> dict[str, Any]:
    status = read_json(state / 'status.json', {'schema_version': 1, 'status': 'not_initialized'})
    if status.get('status') == 'running':
        owner_alive = process_alive(status.get('controller_pid'), status.get('controller_identity'))
        child_alive = process_alive(status.get('child_pid'), status.get('child_identity'))
        if not owner_alive:
            status = dict(status, status='orphaned_running' if child_alive else 'interrupted',
                          recovery_required=True, note='Controller exited; no automatic rerun is permitted.')
    status['external_game_processes'] = find_game_processes()
    output = output_pointer(workspace)
    progress = public_progress(output)
    if status.get('status') == 'running' and progress:
        try:
            started = datetime.fromisoformat(status['started_at']).timestamp()
        except (KeyError, ValueError):
            started = 0
        if str(output) == status.get('previous_output_dir') or progress['events_modified_at'] < started - 2:
            progress = None
    status['progress'] = progress
    return status


def watch_active(status: dict[str, Any]) -> bool:
    return status.get('status') in {'running', 'orphaned_running'} or bool(status.get('external_game_processes'))


def observe_workspace(workspace: Path) -> dict[str, Any]:
    processes = find_game_processes()
    output = output_pointer(workspace)
    result: dict[str, Any] = {'observed_at': now(), 'game_processes': processes,
                             'status': 'external_running' if processes else 'idle',
                             'output_dir': str(output) if output else None}
    if output:
        result['progress'] = public_progress(output)
        report = output / 'score_report.json'
        if report.is_file():
            summary = summarize_report(read_json(report))
            result['last_report'] = summary
            result['report_file'] = str(report)
            result['report_sha256'] = file_digest(report)
            result['attribution'] = 'External run: submission snapshot was not frozen by this controller.'
            if not processes:
                result['status'] = summary['status']
    return result


def recover_lock(state: Path) -> dict[str, Any]:
    path = state / 'run.lock'
    record = read_json(path)
    if not record:
        return {'status': 'no_lock'}
    if (process_alive(record.get('controller_pid'), record.get('controller_identity')) or
            process_alive(record.get('child_pid'), record.get('child_identity')) or find_game_processes()):
        raise ControllerError('Cannot recover a lock while its controller or any game is still running')
    if any(process_alive(child.get('pid'),child.get('identity')) for child in record.get('children',[])):
        raise ControllerError('Cannot recover a lock while an isolated worker is still running')
    path.unlink()
    return {'status': 'lock_recovered', 'previous_run': record.get('run_id')}


def mark_reviewed(workspace: Path, state: Path, run_id: str, analysis: Path, candidate_id: str | None = None) -> dict[str, Any]:
    if not re.fullmatch(r'[A-Za-z0-9-]+', run_id):
        raise ControllerError('Invalid run id')
    run_file = state / 'runs' / run_id / 'run.json'
    run = read_json(run_file)
    if not run or run.get('status') not in {'awaiting_analysis', 'awaiting_approval'}:
        raise ControllerError('Only a completed run awaiting analysis can be marked reviewed')
    analysis = analysis.expanduser().resolve(strict=True)
    if not analysis.is_file() or analysis.suffix.lower() != '.md' or analysis.stat().st_size > 1024 * 1024:
        raise ControllerError('Analysis must be a Markdown file smaller than 1 MB')
    if not inside(analysis, workspace) and not inside(analysis, state):
        raise ControllerError('Analysis must be saved inside the workspace or experiment state directory')
    if candidate_id:
        get_candidate(state, candidate_id)
    run.update(status='awaiting_approval', reviewed_at=now(), analysis_file=str(analysis),
               analysis_sha256=file_digest(analysis), proposed_candidate_id=candidate_id)
    latest = read_json(state / 'state.json', {}).get('latest_run')
    if latest == run_id:
        update_status(state, run)
    else:
        write_json(run_file, run)
    return run


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace', type=Path, default=Path('/home/gulebi/career-team'))
    parser.add_argument('--state-dir', type=Path)
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('init')
    stage = commands.add_parser('stage')
    stage.add_argument('source', type=Path)
    stage.add_argument('--name')
    stage.add_argument('--source', dest='provenance', default='local')
    commands.add_parser('list')
    run = commands.add_parser('run')
    run.add_argument('candidate')
    run.add_argument('--approved', action='store_true')
    run.add_argument('--timeout-seconds', type=int, default=7500)
    status = commands.add_parser('status')
    status.add_argument('--watch', action='store_true')
    status.add_argument('--json', action='store_true')
    commands.add_parser('observe').add_argument('--json', action='store_true')
    summary = commands.add_parser('summarize')
    summary.add_argument('run_id', nargs='?')
    commands.add_parser('recover-lock')
    reviewed = commands.add_parser('reviewed')
    reviewed.add_argument('run_id')
    reviewed.add_argument('--analysis', type=Path, required=True)
    reviewed.add_argument('--candidate')
    args = parser.parse_args(argv)
    try:
        workspace, state = load_layout(args.workspace, args.state_dir)
        if args.command == 'init':
            initialize(state)
            result: Any = {'workspace': str(workspace), 'state_dir': str(state), 'status': 'ready'}
        elif args.command == 'stage':
            result = stage_submission(args.source, state, args.name, args.provenance)
        elif args.command == 'list':
            result = [read_json(item) for item in sorted((state / 'candidates').glob('*/candidate.json'))]
        elif args.command == 'run':
            result = run_candidate(workspace, state, args.candidate, args.approved, args.timeout_seconds)
        elif args.command == 'status':
            while True:
                result = current_status(workspace, state)
                if not args.watch:
                    break
                print(json.dumps(result, ensure_ascii=False), flush=True)
                if not watch_active(result):
                    return 0
                time.sleep(3)
        elif args.command == 'observe':
            result = observe_workspace(workspace)
        elif args.command == 'summarize':
            run_id = args.run_id or read_json(state / 'state.json', {}).get('latest_run')
            if not run_id or not re.fullmatch(r'[A-Za-z0-9-]+', run_id):
                raise ControllerError('No valid run selected')
            result = read_json(state / 'runs' / run_id / 'summary.json')
            if result is None:
                raise ControllerError('No summary exists; check run status and console.log')
        elif args.command == 'reviewed':
            result = mark_reviewed(workspace, state, args.run_id, args.analysis, args.candidate)
        else:
            result = recover_lock(state)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        if isinstance(result, dict) and result.get('status') in {'infrastructure_error', 'timed_out', 'interrupted'}:
            return 1
        return 0
    except (ControllerError, OSError, subprocess.TimeoutExpired, ValueError) as exc:
        print(json.dumps({'status': 'error', 'error': str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())

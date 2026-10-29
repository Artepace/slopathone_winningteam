"""Prepare isolated Linux workers; launch a fixed, explicitly approved batch."""
from __future__ import annotations
import argparse
import contextlib
import json
import os
from pathlib import Path
import queue
import shutil
import signal
import socket
import subprocess
import sys
import threading
import time
import uuid
import controller as c

PORT_KEYS = ('JIUWENSWARM_AGENT_SERVER_PORT', 'JIUWENSWARM_WEB_PORT',
             'JIUWENSWARM_GATEWAY_PORT', 'JIUWENSWARM_FRONTEND_PORT')


def batch_path(workspace, batch_id):
    import re
    if not re.fullmatch(r'[A-Za-z0-9-]+', batch_id):
        raise c.ControllerError('Invalid batch id')
    return workspace / '.experiments' / 'parallel' / batch_id


def worker_environment(worker):
    env = os.environ.copy()
    # A real private home for this child only; the user's shell/home is unchanged.
    env['HOME'] = worker['home']
    env['JIUWENSWARM_HOME'] = worker['home']
    env['JIUWENSWARM_DATA_DIR'] = str(Path(worker['home']) / '.jiuwenswarm-instances' / 'career_emu')
    env['XDG_CACHE_HOME'] = str(Path(worker['home']) / '.cache')
    env['XDG_CONFIG_HOME'] = str(Path(worker['home']) / '.config')
    env['XDG_DATA_HOME'] = str(Path(worker['home']) / '.local/share')
    env.pop('PYTHONPATH', None)
    env['PATH'] = str(Path(worker['workspace']) / '.venv/bin') + os.pathsep + env.get('PATH', '')
    env['PYTHONUNBUFFERED'] = '1'
    env['NO_COLOR'] = '1'
    # Named career_emu gets index 1. Configure distinct bases as well as paths.
    env.update({key: str(port - 1000) for key, port in zip(PORT_KEYS, worker['ports'])})
    return env


def reserve_ports(count):
    """Bind all prospective ports together, detecting intra-group collisions."""
    for base in range(31000, 60000 - count * 10, 100):
        ports = [[base + slot * 10 + n for n in range(4)] for slot in range(count)]
        held = []
        try:
            for group in ports:
                for port in group:
                    sock = socket.socket()
                    held.append(sock)
                    sock.bind(('127.0.0.1', port))
            return ports
        except OSError:
            pass
        finally:
            for sock in held: sock.close()
    raise c.ControllerError('No available port groups')


def prepare(workspace, candidate_id, version='V4', count=3):
    import re
    if os.name != 'posix': raise c.ControllerError('Prepare workers inside Debian, not native Windows')
    if not re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]{0,47}', version): raise c.ControllerError('Invalid version label')
    if count not in (2, 3): raise c.ControllerError('Supported parallel count: 2 or 3')
    state = workspace / '.experiments'
    source, candidate = c.get_candidate(state, candidate_id)
    executable = c.python_executable(workspace)
    stamp = time.strftime('%Y%m%dT%H%M%SZ', time.gmtime()) + '-' + uuid.uuid4().hex[:6]
    root = batch_path(workspace, stamp)
    root.mkdir(parents=True)
    batch = {'id': stamp, 'version': version, 'candidate_id': candidate_id, 'count': count,
             'submission_sha256': candidate['sha256'], 'status': 'preparing', 'created_at': c.now(), 'workers': []}
    c.write_json(root / 'batch.json', batch)
    try:
        groups = reserve_ports(count)
        # Copy only organizer-provided model fields; never print their contents.
        credentials = []
        for line in (workspace / '.env').read_text().splitlines():
            if '=' in line and line.split('=', 1)[0].strip() in {'API_BASE', 'API_KEY', 'MODEL_NAME'}:
                credentials.append(line)
        if len(credentials) != 3: raise c.ControllerError('Expected three model settings in project .env')
        for slot in range(count):
            worker_root = root / 'workers' / str(slot + 1)
            target, home = worker_root / 'workspace', worker_root / 'home'
            target.mkdir(parents=True)
            home.mkdir(mode=0o700)
            shutil.copytree(workspace / 'career_sim_runner', target / 'career_sim_runner',
                            ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
            (target / '.venv').symlink_to(executable.parent.parent, target_is_directory=True)
            secret = target / '.env'
            secret.write_text('\n'.join(credentials) + '\n')
            secret.chmod(0o600)
            worker = {'slot': slot + 1, 'label': f'{version}_{slot + 1}', 'workspace': str(target),
                      'home': str(home), 'parent_workspace': str(workspace), 'parent_home': str(Path.home()),
                      'ports': groups[slot]}
            c.write_json(target / '.career-lab-worker.json', worker)
            staged = c.stage_submission(source / 'submission', target / '.experiments', version, candidate['source'])
            worker['candidate_id'] = staged['id']
            batch['workers'].append(worker)
            c.write_json(root / 'batch.json', batch)
            # Local initialization/configuration only: no service, model or game.
            with (worker_root / 'setup.log').open('w') as log:
                result = subprocess.run([str(executable), '-m', 'career_sim_runner', 'setup'],
                    cwd=target, env=worker_environment(worker), stdout=log, stderr=subprocess.STDOUT, timeout=90)
            if result.returncode: raise c.ControllerError(f"Setup failed for {worker['label']}; inspect its private setup.log")
            probe = ('import json; from career_sim_runner.constants import INSTANCE_ROOT,REPO_ROOT,DEFAULT_DB_PATH; '
                     'from jiuwenswarm.instance_manager.status import get_instance_config; '
                     'v=get_instance_config("career_emu"); print(json.dumps({"home":str(INSTANCE_ROOT.parent.parent),'
                     '"workspace":str(REPO_ROOT),"db":str(DEFAULT_DB_PATH),"ports":list(v.ports.values())}))')
            result = subprocess.run([str(executable), '-c', probe], cwd=target, env=worker_environment(worker),
                                    capture_output=True, text=True, timeout=15)
            if result.returncode: raise c.ControllerError(f"Isolation check failed for {worker['label']}")
            actual = json.loads(result.stdout.strip().splitlines()[-1])
            if actual['home'] != str(home) or actual['workspace'] != str(target) or set(actual['ports']) != set(worker['ports']):
                raise c.ControllerError(f"Isolation/port mismatch for {worker['label']}; no game started")
            if not c.inside(Path(actual['db']), target): raise c.ControllerError('Worker database is not isolated')
            worker['database'] = actual['db']
        batch['status'] = 'awaiting_approval'
    except Exception as error:
        batch.update(status='preparation_error', error=str(error))
        c.write_json(root / 'batch.json', batch)
        raise
    c.write_json(root / 'batch.json', batch)
    c.write_json(state / 'parallel-latest.json', {'batch_id': stamp})
    return batch


def collect_summary(batch):
    outcomes = []
    for worker in batch['workers']:
        state = Path(worker['workspace']) / '.experiments'
        status = c.read_json(state / 'status.json', {})
        item = {'label': worker['label'], 'status': status.get('status', 'not_started')}
        if worker.get('exit_code') not in (None,0) and item['status'] in {'idle','not_started'}:
            item.update(status='infrastructure_error',process_exit_code=worker['exit_code'])
        if status.get('id'):
            summary = c.read_json(state / 'runs' / status['id'] / 'summary.json')
            if summary:
                item.update(summary)
                item['label'] = worker['label']
        outcomes.append(item)
    valid = [v for v in outcomes if v.get('status') in {'awaiting_analysis', 'awaiting_approval'}
             and c.number(v.get('quantitative_score')) is not None]
    return {'batch_id': batch['id'], 'version': batch['version'], 'expected_runs': batch['count'],
            'valid_runs': len(valid), 'runs': outcomes,
            'mean_score': sum(v['quantitative_score'] for v in valid) / len(valid) if len(valid) == batch['count'] else None,
            'worst_score': min((v['quantitative_score'] for v in valid), default=None),
            'full_careers': sum(v.get('survival_months') == 48 for v in valid)}


def stop_worker(worker, process=None):
    if process is not None and process.poll() is None:
        with contextlib.suppress(ProcessLookupError): process.send_signal(signal.SIGINT)
        try: process.wait(timeout=15)
        except subprocess.TimeoutExpired:
            with contextlib.suppress(ProcessLookupError): process.kill()
            process.wait()
    # Only PIDs with matching Linux start identities from this worker's records.
    state = Path(worker['workspace']) / '.experiments'
    records = [c.read_json(state / 'status.json', {}), c.read_json(state / 'service.json', {})]
    for record in records:
        pid = record.get('child_pid') or record.get('pid')
        identity = record.get('child_identity') or record.get('identity')
        if pid and identity and c.process_alive(pid, identity):
            with contextlib.suppress(ProcessLookupError): os.killpg(pid, signal.SIGTERM)


def run_batch(workspace, batch_id, approved):
    if not approved: raise c.ControllerError('Batch not started: explicit authorization for all games is required')
    root = batch_path(workspace, batch_id)
    batch = c.read_json(root / 'batch.json')
    if not batch or batch['status'] != 'awaiting_approval': raise c.ControllerError('Batch is not ready or already consumed')
    children = []
    lines = queue.Queue()
    with c.RunLock(workspace / '.experiments/run.lock', 'batch-' + batch_id) as batch_lock:
        if c.find_game_processes(): raise c.ControllerError('Another game is active; it was left untouched')
        probes=[]
        try:
            for worker in batch['workers']:
                _,candidate=c.get_candidate(Path(worker['workspace'])/'.experiments',worker['candidate_id'])
                if candidate['sha256']!=batch['submission_sha256']: raise c.ControllerError('Batch worker content changed')
                for port in worker['ports']:
                    sock=socket.socket();probes.append(sock);sock.bind(('127.0.0.1',port))
        finally:
            for sock in probes: sock.close()
        batch.update(status='running', started_at=c.now(), controller_pid=os.getpid(), controller_identity=c.process_identity(os.getpid()))
        c.write_json(root / 'batch.json', batch)
        try:
            for worker in batch['workers']:
                command = [str(c.python_executable(workspace)), '-u', str(Path(__file__).resolve()),
                           '--workspace', str(workspace), 'worker', batch_id, '--slot', str(worker['slot']), '--approved']
                child = subprocess.Popen(command, cwd=worker['workspace'], env=worker_environment(worker),
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='replace', start_new_session=True)
                children.append((worker, child))
                worker.update(pid=child.pid,identity=c.process_identity(child.pid))
                batch_lock.record.setdefault('children',[]).append({'pid':child.pid,'identity':worker['identity']})
                c.write_json(batch_lock.path,batch_lock.record)
                c.write_json(root/'batch.json',batch)
                def read_stream(w=worker, p=child):
                    with (Path(w['workspace']).parent / 'console.log').open('w') as log:
                        for line in p.stdout:
                            log.write(line); log.flush(); lines.put((w['label'], line))
                    p.stdout.close()
                threading.Thread(target=read_stream, daemon=True).start()
            while any(p.poll() is None for _, p in children) or not lines.empty():
                try:
                    label, line = lines.get(timeout=0.3)
                    print(f'[{label}] {line}', end='', flush=True)
                except queue.Empty: pass
        except KeyboardInterrupt:
            batch['status'] = 'interrupted'
        finally:
            for worker, child in children:
                stop_worker(worker, child)
                worker['exit_code']=child.returncode
            summary = collect_summary(batch)
            if batch['status'] != 'interrupted':
                batch['status'] = 'awaiting_analysis' if summary['valid_runs'] == batch['count'] else 'partial_failure'
            batch['finished_at'] = c.now()
            c.write_json(root / 'summary.json', summary)
            c.write_json(root / 'batch.json', batch)
    return batch


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--workspace', type=Path, required=True)
    cmds = p.add_subparsers(dest='command', required=True)
    prep = cmds.add_parser('prepare'); prep.add_argument('candidate'); prep.add_argument('--version', default='V4'); prep.add_argument('--count', type=int, default=3)
    run = cmds.add_parser('run'); run.add_argument('batch'); run.add_argument('--approved', action='store_true')
    worker = cmds.add_parser('worker'); worker.add_argument('batch'); worker.add_argument('--slot', type=int, required=True); worker.add_argument('--approved', action='store_true')
    status = cmds.add_parser('status'); status.add_argument('batch', nargs='?')
    args = p.parse_args(); workspace = args.workspace.resolve()
    try:
        if args.command == 'prepare': result = prepare(workspace, args.candidate, args.version, args.count)
        elif args.command == 'run': result = run_batch(workspace, args.batch, args.approved)
        elif args.command == 'worker':
            if not args.approved: raise c.ControllerError('Worker launch not approved')
            batch = c.read_json(batch_path(workspace,args.batch) / 'batch.json')
            if not batch or batch['status'] != 'running': raise c.ControllerError('No running approved batch')
            if not 1 <= args.slot <= len(batch['workers']): raise c.ControllerError('Invalid worker slot')
            w = batch['workers'][args.slot-1]; target = Path(w['workspace'])
            with (target.parent/'launch.claim').open('x') as claim: claim.write(c.now())
            result = c.run_candidate(target,target/'.experiments',w['candidate_id'],True,isolated=True)
        else:
            batch_id = args.batch or c.read_json(workspace/'.experiments/parallel-latest.json',{}).get('batch_id')
            if not batch_id: result = {'status':'not_prepared'}
            else:
                batch = c.read_json(batch_path(workspace,batch_id)/'batch.json')
                if not batch: raise c.ControllerError('Batch does not exist')
                if batch and batch.get('status')=='running' and not c.process_alive(batch.get('controller_pid'),batch.get('controller_identity')):
                    batch=dict(batch,status='orphaned_running' if any(c.process_alive(w.get('pid'),w.get('identity')) or c.find_game_processes(Path(w['workspace'])) for w in batch['workers']) else 'interrupted',
                               recovery_required=True,note='Batch supervisor exited; never retry automatically.')
                result = {'batch':batch,'summary':collect_summary(batch)}
        print(json.dumps(result,ensure_ascii=False,indent=2))
        return 1 if result.get('status') in {'infrastructure_error','partial_failure','interrupted'} else 0
    except (c.ControllerError,OSError,ValueError,KeyError,subprocess.TimeoutExpired) as error:
        print(json.dumps({'status':'error','error':str(error)}),file=sys.stderr); return 2


if __name__ == '__main__': raise SystemExit(main())

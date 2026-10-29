import contextlib
import importlib.util
import io
import hashlib
import json
import os
from pathlib import Path
import sys
import subprocess
import tempfile
import unittest
from unittest.mock import patch,MagicMock

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import controller as c
import parallel as p
import catalog


def solution(root):
    root.mkdir(parents=True)
    for name,body in [('manifest.json',json.dumps({'team':'Winning team','mode':'agent'})),('README.md','readme'),
                      ('design/skills_design.md','design'),('design/decision_report.md','decision'),
                      ('skills/core/SKILL.md','---\nname: core\ndescription: play\n---\nPlay')]:
        path=root/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(body)
    return root


class ParallelCatalogTests(unittest.TestCase):
    def setUp(self):
        scratch=ROOT/'.test-tmp';scratch.mkdir(exist_ok=True)
        self.temp=tempfile.TemporaryDirectory(dir=scratch);self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)

    def test_catalog_refuses_version_replacement_and_deduplicates_report(self):
        sol=solution(self.root/'source');root=self.root/'lab'
        catalog.register(root,'V4',sol)
        report=self.root/'report.json'
        report.write_text(json.dumps({'play_exit_code':0,'termination_reason':None,
            'ending_score':{'outcome':'eliminated','survival_months':24,'quantitative_score':19.48},
            'token_usage':{'total_tokens':123,'total_cost':0.2},'api_key':'NEVER_EXPORT','output_dir':'PRIVATE'}))
        first=catalog.import_report(root,'V4',report,sol)
        second=catalog.import_report(root,'V4',report,sol)
        self.assertEqual(first['run_label'],'V4_1');self.assertEqual(second['run_label'],'V4_1')
        text=(root/'results/V4/V4_1/summary.json').read_text()
        self.assertNotIn('NEVER_EXPORT',text);self.assertNotIn('PRIVATE',text)
        (sol/'README.md').write_text('changed')
        with self.assertRaises(c.ControllerError):catalog.register(root,'V4',sol)
        with self.assertRaises(c.ControllerError):catalog.import_report(root,'V4',report,self.root)

    def test_catalog_rejects_unsafe_version(self):
        for value in ('../V4','V4/x','V4\\x'):
            with self.assertRaises(c.ControllerError):catalog.version_label(value)

    def test_content_hash_order_is_identical_on_windows_and_linux(self):
        source=solution(self.root/'hash-source')
        names=sorted([f.relative_to(source).as_posix() for f in source.rglob('*') if f.is_file()])
        digest=hashlib.sha256()
        for name in names:
            digest.update(name.encode());digest.update(b'\0');digest.update(hashlib.sha256((source/name).read_bytes()).digest())
        self.assertEqual(c.submission_digest(source),digest.hexdigest())

    def test_managed_import_requires_finished_matching_snapshot(self):
        sol=solution(self.root/'managed-source');root=self.root/'catalog'
        catalog.register(root,'V4',sol)
        run=self.root/'run';run.mkdir();catalog.copy_content(sol,run/'submission')
        metadata={'id':'run1','status':'running','submission':str((run/'submission').resolve())}
        c.write_json(run/'run.json',metadata)
        with self.assertRaises(c.ControllerError):catalog.import_managed(root,'V4',run)
        metadata['status']='awaiting_analysis';c.write_json(run/'run.json',metadata)
        report={'submission_dir':'wrong','play_exit_code':0,'termination_reason':None,
                'ending_score':{'outcome':'completed','quantitative_score':60,'survival_months':48}}
        c.write_json(run/'score_report.json',report)
        with self.assertRaises(c.ControllerError):catalog.import_managed(root,'V4',run)
        report['submission_dir']=metadata['submission'];c.write_json(run/'score_report.json',report)
        result=catalog.import_managed(root,'V4',run)
        self.assertTrue(result['provided_snapshot_matches']);self.assertEqual(result['quantitative_score'],60)

    def test_child_environment_does_not_mutate_parent_and_separates_paths(self):
        before=os.environ.copy()
        a={'home':str(self.root/'home1'),'workspace':str(self.root/'worker1'),'ports':[31000,31001,31002,31003]}
        b=dict(a,home=str(self.root/'home2'),workspace=str(self.root/'worker2'),ports=[31010,31011,31012,31013])
        ea=p.worker_environment(a);eb=p.worker_environment(b)
        self.assertNotEqual(ea['HOME'],eb['HOME']);self.assertNotEqual(ea['JIUWENSWARM_DATA_DIR'],eb['JIUWENSWARM_DATA_DIR'])
        self.assertNotEqual(ea['JIUWENSWARM_AGENT_SERVER_PORT'],eb['JIUWENSWARM_AGENT_SERVER_PORT'])
        self.assertEqual(dict(os.environ),before)

    def test_batch_approval_precedes_any_start(self):
        with patch.object(p.subprocess,'Popen') as start:
            with self.assertRaises(c.ControllerError):p.run_batch(self.root,'any',False)
            start.assert_not_called()

    def test_unisolated_workspace_cannot_bypass_global_game_guard(self):
        with self.assertRaises(c.ControllerError):c.validate_worker_isolation(self.root)

    def test_aggregate_does_not_average_missing_or_failed_games(self):
        workers=[]
        for i in range(3):
            work=self.root/str(i);state=work/'.experiments';run=state/'runs'/'run1'
            c.write_json(state/'status.json',{'id':'run1','status':'awaiting_analysis' if i<2 else 'infrastructure_error'})
            if i<2:c.write_json(run/'summary.json',{'status':'awaiting_analysis','quantitative_score':50+i,'survival_months':48})
            workers.append({'workspace':str(work),'label':f'V4_{i+1}'})
        result=p.collect_summary({'id':'b','version':'V4','count':3,'workers':workers})
        self.assertEqual(result['valid_runs'],2);self.assertIsNone(result['mean_score']);self.assertEqual(result['full_careers'],2)

    def test_port_groups_do_not_overlap(self):
        groups=p.reserve_ports(3)
        self.assertEqual(len({v for group in groups for v in group}),12)

    def synthetic_batch(self, failed_slot=None):
        workspace=self.root/'parent';workspace.mkdir()
        root=workspace/'.experiments/parallel/batch1'
        workers=[];source=solution(self.root/'batch-source')
        for i,ports in enumerate(p.reserve_ports(3),1):
            target=root/'workers'/str(i)/'workspace';target.mkdir(parents=True)
            candidate=c.stage_submission(source,target/'.experiments','V4')
            workers.append({'slot':i,'label':f'V4_{i}','workspace':str(target),'home':str(target.parent/'home'),
                            'ports':ports,'candidate_id':candidate['id']})
        batch={'id':'batch1','version':'V4','count':3,'status':'awaiting_approval',
               'submission_sha256':candidate['sha256'],'workers':workers}
        c.write_json(root/'batch.json',batch)
        real_popen=subprocess.Popen
        program='''import json,sys,time,sqlite3
from pathlib import Path
w=Path.cwd();state=w/'.experiments';now=time.time()
sqlite3.connect(w/'fixture.sqlite').close()
(w/'started').write_text(str(now));print('fixture started',flush=True)
time.sleep(0.3)
if sys.argv[1]!='fail':
 p=state/'runs/r';p.mkdir(parents=True)
 (p/'summary.json').write_text(json.dumps({'status':'awaiting_analysis','quantitative_score':50,'survival_months':48}))
 (state/'status.json').write_text(json.dumps({'id':'r','status':'awaiting_analysis'}))
(w/'finished').write_text(str(time.time()))
sys.exit(1 if sys.argv[1]=='fail' else 0)
'''
        def launch(command,**kwargs):
            slot=int(command[command.index('--slot')+1])
            return real_popen([sys.executable,'-u','-c',program,'fail' if slot==failed_slot else 'ok'],**kwargs)
        with patch.object(c,'find_game_processes',return_value=[]),patch.object(c,'python_executable',return_value=Path(sys.executable)), \
             patch.object(p.subprocess,'Popen',side_effect=launch),contextlib.redirect_stdout(io.StringIO()):
            result=p.run_batch(workspace,'batch1',True)
        starts=[float((Path(w['workspace'])/'started').read_text()) for w in workers]
        finishes=[float((Path(w['workspace'])/'finished').read_text()) for w in workers]
        self.assertLess(max(starts),min(finishes),'All three fixtures must actually overlap')
        return result,c.read_json(root/'summary.json')

    def test_three_real_synthetic_processes_overlap_and_complete(self):
        result,summary=self.synthetic_batch()
        self.assertEqual(result['status'],'awaiting_analysis');self.assertEqual(summary['mean_score'],50)

    def test_one_failed_synthetic_worker_does_not_stop_siblings(self):
        result,summary=self.synthetic_batch(2)
        self.assertEqual(result['status'],'partial_failure');self.assertEqual(summary['valid_runs'],2)
        self.assertIsNone(summary['mean_score'])
        self.assertEqual(summary['runs'][1]['status'],'infrastructure_error')


if __name__=='__main__':unittest.main()

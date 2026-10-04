import copy
import shutil
import subprocess
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from common import load, write, allocate, topological
from schedule import compute
from validate import validate

class CalculationTests(unittest.TestCase):
    def setUp(self):
        self.calendar={'work_weekdays':[0,1,2,3,4],'holidays':['2026-10-06']}
        self.capacity={'valid_from':'2026-10-05','valid_until':'2026-11-30',
                       'people':{'a':{'fraction':0.5,'leave':['2026-10-07']},'b':{'fraction':1.0,'leave':[]}}}
    def wp(self,id,person,deps=None,gate=None):
        return {'id':id,'assigned_to':person,'depends_on':deps or [],'not_before':gate,'priority':int(id[-1])}
    def est(self,id,value):
        return {'id':id,'effort_pd':{'low':value,'expected':value,'high':value}}
    def test_calendar_fraction_and_leave(self):
        rows=allocate(date(2026,10,5),'a',1.5,self.capacity,self.calendar)
        self.assertEqual([r['date'] for r in rows],['2026-10-05','2026-10-08','2026-10-09'])
        self.assertAlmostEqual(sum(r['effort_pd'] for r in rows),1.5)
    def test_dependency_and_same_resource_do_not_overlap(self):
        packages=[self.wp('W1','b'),self.wp('W2','b'),self.wp('W3','a',['W1','W2'])]
        result=compute(packages,[self.est('W1',1),self.est('W2',1),self.est('W3',0.5)],self.capacity,self.calendar,'expected',date(2026,10,5))
        tasks={t['id']:t for t in result['tasks']}
        self.assertEqual(tasks['W1']['finish'],'2026-10-05')
        self.assertEqual(tasks['W2']['start'],'2026-10-07')
        self.assertEqual(tasks['W3']['start'],'2026-10-08')
        allocations=[(t['assigned_to'],a['date']) for t in result['tasks'] for a in t['allocations']]
        self.assertEqual(len(allocations),len(set(allocations)))
    def test_external_gate_ignores_available_prior_days(self):
        result=compute([self.wp('W1','b',gate='2026-10-12')],[self.est('W1',1)],self.capacity,self.calendar,'expected',date(2026,10,5))
        self.assertEqual(result['finish_date'],'2026-10-12')
    def test_cycle_and_dangling_dependency_rejected(self):
        for rows in [[self.wp('W1','a',['W2']),self.wp('W2','a',['W1'])],[self.wp('W1','a',['MISSING'])]]:
            with self.assertRaises(ValueError): topological(rows)
    def test_capacity_window_is_enforced(self):
        with self.assertRaisesRegex(ValueError,'validity'):
            allocate(date(2026,11,30),'a',2,self.capacity,self.calendar)

class ArtifactTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.root=Path(self.tmp.name)/'repo'
        shutil.copytree(ROOT,self.root,ignore=shutil.ignore_patterns('.git','.venv','__pycache__'))
        self.req=self.root/'requirements/REQ-TEST'
        shutil.copytree(self.root/'templates/requirement',self.req)
        for path in self.req.rglob('*'):
            if path.is_file():
                path.write_text(path.read_text().replace('{{REQ_ID}}','REQ-TEST'))
        # Test inputs exist only in this isolated temporary directory, not as repository examples.
        req=load(self.req/'requirement.yaml')
        req.update(status='assessed',goal='Validate a delivered capability',
                   functional_requirements=[{'id':'FR-01','statement':'Deliver required behavior'}],
                   acceptance_criteria=[{'id':'AC-01','requirement_ids':['FR-01'],'statement':'Expected observable outcome'}],
                   questions=[])
        write(self.req/'requirement.yaml',req)
        write(self.root/'config/project.yaml',{'schema_version':1,'owner':'test-owner'})
        write(self.root/'planning/people.yaml',{'schema_version':1,'people':[{'id':'worker','skills':['engineering']},{'id':'other','skills':[]}]})
        write(self.root/'planning/capacity.yaml',{'schema_version':1,'valid_from':'2026-10-05','valid_until':'2026-11-30',
              'people':{'worker':{'fraction':1.0,'leave':[]},'other':{'fraction':1.0,'leave':[]}}})
        write(self.root/'planning/calendar.yaml',{'schema_version':1,'start_date':'2026-10-05','work_weekdays':[0,1,2,3,4],'holidays':[]})
        write(self.root/'planning/historical-delivery.yaml',{'schema_version':1,'samples':[{'id':'H-01','synthetic':True}]})
        write(self.req/'work-breakdown.yaml',{'schema_version':1,'work_packages':[{'id':'WP-01','name':'Delivery',
              'work_type':'domain-model-change','complexity':'medium','deliverable':'Delivered capability','done_when':'AC-01 verified',
              'acceptance_ids':['AC-01'],'evidence_ids':[],'priority':1,'depends_on':[],
              'skills':['engineering'],'assigned_to':'worker','not_before':None}]})
        write(self.req/'estimation.yaml',{'schema_version':1,'estimates':[{'id':'WP-01','basis':'expert-judgement',
              'historical_refs':[],'confidence':'low','rationale':'Bounded effort for tool validation',
              'effort_pd':{'low':1,'expected':2,'high':3},'risk_ids':[]}]})
        write(self.req/'traceability.yaml',{'schema_version':1,'links':[{'acceptance_id':'AC-01',
              'work_packages':['WP-01'],'test_status':'planned','test_evidence':None}]})
        write(self.req/'assessment.yaml',{'schema_version':1,'status':'draft','ready_for_planning':True,
              'reviewed_by':'test-reviewer','reviewed_at':'2026-10-04','assumptions':['Fixed tool-validation capacity'],
              'blockers':[],'owner_confirmation':None})
        self.blocked=self.root/'requirements/REQ-BLOCKED'
        shutil.copytree(self.root/'templates/requirement',self.blocked)
        for path in self.blocked.rglob('*'):
            if path.is_file():
                path.write_text(path.read_text().replace('{{REQ_ID}}','REQ-BLOCKED'))
    def tearDown(self): self.tmp.cleanup()
    def test_ready_fixture_and_blocked_fixture(self):
        self.assertEqual(validate(self.root,self.req,True),[])
        errors=validate(self.root,self.blocked,True)
        self.assertTrue(any('blocking' in e.lower() for e in errors))
    def test_synthetic_history_cannot_estimate_real_work(self):
        data=load(self.req/'estimation.yaml'); data['estimates'][0]['historical_refs']=['H-01']; write(self.req/'estimation.yaml',data)
        self.assertTrue(any('synthetic history' in e for e in validate(self.root,self.req)))
    def test_unknown_reference_and_unordered_estimates_rejected(self):
        data=load(self.req/'estimation.yaml'); data['estimates'][0]['historical_refs']=['NONEXISTENT']
        data['estimates'][0]['effort_pd']['low']=99; write(self.req/'estimation.yaml',data)
        errors=validate(self.root,self.req)
        self.assertTrue(any('historical reference' in e for e in errors))
        self.assertTrue(any('unordered' in e for e in errors))
    def test_wrong_skill_assignment_rejected(self):
        data=load(self.req/'work-breakdown.yaml'); data['work_packages'][0]['assigned_to']='other'; write(self.req/'work-breakdown.yaml',data)
        self.assertTrue(any('lacks required skills' in e for e in validate(self.root,self.req,True)))
    def test_real_planning_rejects_synthetic_resources(self):
        req=load(self.req/'requirement.yaml'); req['synthetic']=False; write(self.req/'requirement.yaml',req)
        data=load(self.req/'estimation.yaml')
        for e in data['estimates']:
            e['basis']='expert-judgement'; e['historical_refs']=[]
        write(self.req/'estimation.yaml',data)
        capacity=load(self.root/'planning/capacity.yaml'); capacity['synthetic']=True; write(self.root/'planning/capacity.yaml',capacity)
        write(self.root/'config/project.yaml',{'schema_version':1,'owner':None})
        errors=validate(self.root,self.req,True)
        self.assertTrue(any('synthetic people/capacity/calendar' in e for e in errors))
        self.assertTrue(any('configured project owner' in e for e in errors))
    def test_baseline_cannot_lack_confirmation(self):
        data=load(self.req/'assessment.yaml'); data['status']='baseline'; write(self.req/'assessment.yaml',data)
        self.assertTrue(any('owner_confirmation' in e for e in validate(self.root,self.req)))
    def test_schedule_cli_refuses_blocker_without_dates(self):
        result=subprocess.run([sys.executable,str(self.root/'scripts/schedule.py'),'--requirement','REQ-BLOCKED'],capture_output=True,text=True)
        self.assertNotEqual(result.returncode,0)
        self.assertFalse((self.blocked/'schedule-expected.yaml').exists())
    def test_intake_creation_and_no_overwrite(self):
        command=[sys.executable,str(self.root/'scripts/init_requirement.py'),'REQ-NEW']
        self.assertEqual(subprocess.run(command,capture_output=True).returncode,0)
        self.assertEqual(validate(self.root,self.root/'requirements/REQ-NEW'),[])
        self.assertNotEqual(subprocess.run(command,capture_output=True).returncode,0)
    def test_unconfigured_intake_allowed_but_scheduling_blocked(self):
        write(self.root/'planning/capacity.yaml',{'schema_version':1,'valid_from':None,'valid_until':None,'people':{}})
        write(self.root/'planning/calendar.yaml',{'schema_version':1,'start_date':None,'work_weekdays':[],'holidays':[]})
        self.assertEqual(validate(self.root,self.blocked),[])
        errors=validate(self.root,self.req,True)
        self.assertTrue(any('validity dates' in e for e in errors))
        self.assertTrue(any('start_date' in e for e in errors))
    def test_bad_id_does_not_escape_directory(self):
        result=subprocess.run([sys.executable,str(self.root/'scripts/init_requirement.py'),'../../escape'],capture_output=True)
        self.assertNotEqual(result.returncode,0)

if __name__=='__main__': unittest.main()

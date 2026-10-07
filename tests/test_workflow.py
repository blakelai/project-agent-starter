"""Lifecycle and project-level scenarios run only in isolated temporary repositories."""
import copy
import shutil
import subprocess
import sys
import unittest

import test_tools
from common import load, write
from validate import validate
from workflow import materialize
from schedule_project import build, save
from baseline import preview, create, verify

AT='2026-10-07T22:00:00+08:00'
DECISION={'by':'test-owner','at':AT,'source':'test://explicit-human-decision'}


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.fixture=test_tools.ArtifactTests('test_ready_fixture_and_blocked_fixture'); self.fixture.setUp()
        self.root,self.req=self.fixture.root,self.fixture.req

    def tearDown(self): self.fixture.tearDown()

    def cli(self, script, *args):
        return subprocess.run([sys.executable,str(self.root/'scripts'/script),*args],cwd=self.root,capture_output=True,text=True)

    def project(self, two=True):
        result=self.cli('init_project.py','PROJ-TEST'); self.assertEqual(result.returncode,0,result.stderr)
        if two:
            second=self.root/'vault/requirements/REQ-SECOND'; shutil.copytree(self.req,second)
            req=load(second/'requirement.md'); req['id']='REQ-SECOND'; write(second/'requirement.md',req)
        path=self.root/'vault/projects/PROJ-TEST/project.md'; data=load(path)
        data.update(name='Test scope',owner='test-owner',goal='Verify delivery',scope=['Test work'],
                    success_criteria=['Evidence-backed completion'],requirements=[{'id':'REQ-TEST','priority':1}],dependencies=[])
        if two: data['requirements'].append({'id':'REQ-SECOND','priority':2})
        write(path,data); return path

    def progress(self, req_id, status='in-progress', remaining=1, actual=1):
        row={'id':'WP-01','status':status,'actual_effort_pd':actual,
             'remaining_effort_pd':{'low':remaining,'expected':remaining,'high':remaining}}
        if actual is None: row['actual_unknown_reason']='No measured actuals available'
        if status=='done': row.update(completed_on='2026-10-06',completion_evidence='test://delivery-evidence')
        if status=='cancelled': row['cancellation']={**DECISION,'reason':'Approved scope removal'}
        data={'schema_version':1,'as_of':'2026-10-06','work':[row],'blockers':[],'closure':None}
        path=self.root/'vault/requirements'/req_id/'progress.md'; write(path,data); return path

    def test_initialization_and_phase_materialization_preserve_existing_content(self):
        result=self.cli('init_requirement.py','REQ-NEW'); self.assertEqual(result.returncode,0,result.stderr)
        path=self.root/'vault/requirements/REQ-NEW'
        self.assertEqual({p.name for p in path.glob('*.md')}, {'index.md','requirement.md','assessment.md','evidence.md','traceability.md'})
        before=(path/'requirement.md').read_bytes()
        materialize(self.root,'REQ-NEW','planning')
        self.assertTrue((path/'estimation.md').exists()); self.assertFalse((path/'progress.md').exists())
        self.assertEqual(before,(path/'requirement.md').read_bytes())
        self.assertEqual(materialize(self.root,'REQ-NEW','planning'),[])
        materialize(self.root,'REQ-NEW','delivery'); self.assertTrue((path/'progress.md').exists())

    def test_clarification_does_not_require_work_packages_or_estimates(self):
        req=load(self.req/'requirement.md'); req['status']='clarified'; write(self.req/'requirement.md',req)
        assessment=load(self.req/'assessment.md'); assessment['ready_for_planning']=False; write(self.req/'assessment.md',assessment)
        for name in ['work-breakdown.md','estimation.md','risks.md']: (self.req/name).unlink()
        write(self.req/'traceability.md',{'schema_version':1,'links':[]})
        self.assertEqual(validate(self.root,self.req,stage='requirements'),[])
        self.assertTrue(validate(self.root,self.req,stage='planning'))

    def test_question_blocks_only_its_stage_and_later_stages(self):
        req=load(self.req/'requirement.md'); req['status']='clarified'
        req['questions']=[{'id':'Q-PLAN','question':'Capacity confirmation needed','owner':'test-owner',
                           'blocking':True,'status':'open','blocks':['planning'],'affected_work':['WP-01']}]
        write(self.req/'requirement.md',req)
        assessment=load(self.req/'assessment.md'); assessment['ready_for_planning']=False; write(self.req/'assessment.md',assessment)
        self.assertEqual(validate(self.root,self.req,stage='requirements'),[])
        self.assertTrue(any('blocking questions' in e for e in validate(self.root,self.req,stage='planning')))

    def test_early_risk_can_reference_requirement_before_work_exists(self):
        req=load(self.req/'requirement.md'); req['status']='clarified'; write(self.req/'requirement.md',req)
        assessment=load(self.req/'assessment.md'); assessment['ready_for_planning']=False; write(self.req/'assessment.md',assessment)
        for name in ['work-breakdown.md','estimation.md']: (self.req/name).unlink()
        write(self.req/'traceability.md',{'schema_version':1,'links':[]})
        risk={'id':'R-EARLY','probability':'medium','impact':'high','owner':'test-owner',
              'trigger':'External policy changes','mitigation':'Review external policy',
              'affected_requirements':[req['functional_requirements'][0]['id']],
              'affected_work':[],'treatment':'monitor-only'}
        write(self.req/'risks.md',{'schema_version':1,'risks':[risk]})
        self.assertEqual(validate(self.root,self.req,stage='requirements'),[])
        risk['affected_requirements']=['FR-MISSING']; write(self.req/'risks.md',{'schema_version':1,'risks':[risk]})
        self.assertTrue(validate(self.root,self.req,stage='requirements'))

    def test_closed_cannot_bypass_acceptance_with_earlier_stage_flag(self):
        req=load(self.req/'requirement.md'); req['status']='closed'; write(self.req/'requirement.md',req)
        self.progress('REQ-TEST','done',0,2)
        errors=validate(self.root,self.req,stage='intake')
        self.assertTrue(any('acceptance/waiver' in e for e in errors),errors)

    def test_close_command_requires_tests_human_acceptance_and_closure_decision(self):
        path=self.progress('REQ-TEST','done',0,2)
        before=(self.req/'requirement.md').read_bytes()
        self.assertNotEqual(self.cli('close_requirement.py','--requirement','REQ-TEST').returncode,0)
        self.assertEqual(before,(self.req/'requirement.md').read_bytes())
        trace=load(self.req/'traceability.md'); trace['links'][0].update(test_status='passed',test_evidence='test://test-report',
             acceptance={**DECISION,'status':'accepted'}); write(self.req/'traceability.md',trace)
        data=load(path); data['closure']={**DECISION,'summary':'Test scope accepted; measurement lessons captured'}; write(path,data)
        result=self.cli('close_requirement.py','--requirement','REQ-TEST')
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(load(self.req/'requirement.md')['status'],'closed')

    def test_explicit_waiver_requires_reason_and_does_not_fake_test_pass(self):
        path=self.progress('REQ-TEST','cancelled',0,None)
        trace=load(self.req/'traceability.md'); trace['links'][0]['acceptance']={**DECISION,'status':'waived'}
        write(self.req/'traceability.md',trace)
        data=load(path); data['closure']={**DECISION,'summary':'Scope cancelled by owner'}; write(path,data)
        self.assertTrue(validate(self.root,self.req,stage='closure'))
        trace['links'][0]['acceptance']['reason']='Explicitly cancelled scope'; write(self.req/'traceability.md',trace)
        self.assertEqual(validate(self.root,self.req,stage='closure'),[])
        self.assertEqual(load(self.req/'traceability.md')['links'][0]['test_status'],'planned')

    def test_combined_schedule_never_double_books_shared_capacity(self):
        self.project(); result=build(self.root,'PROJ-TEST')
        slots=[(task['assigned_to'],allocation['date']) for task in result['tasks'] for allocation in task['allocations']]
        self.assertEqual(len(slots),len(set(slots)))
        self.assertEqual([t['id'] for t in result['tasks']],['REQ-TEST/WP-01','REQ-SECOND/WP-01'])
        self.assertEqual(result['finish_date'],'2026-10-08')
        self.assertEqual(result['total_effort_pd'],4)

    def test_cross_requirement_dependencies_and_cycle_detection(self):
        path=self.project(); data=load(path)
        endpoint=lambda r:{'requirement_id':r,'work_package_id':'WP-01'}
        data['dependencies']=[{'predecessor':endpoint('REQ-SECOND'),'successor':endpoint('REQ-TEST')}]
        write(path,data); result=build(self.root,'PROJ-TEST')
        self.assertEqual(result['tasks'][0]['id'],'REQ-SECOND/WP-01')
        data['dependencies'].append({'predecessor':endpoint('REQ-TEST'),'successor':endpoint('REQ-SECOND')}); write(path,data)
        with self.assertRaisesRegex(ValueError,'cycle'): build(self.root,'PROJ-TEST')

    def test_forecast_preserves_completed_work_and_uses_explicit_remaining_effort(self):
        self.project(); self.progress('REQ-TEST','done',0,2); self.progress('REQ-SECOND',remaining=1,actual=1)
        before={p:p.read_bytes() for p in (self.root/'vault/requirements').glob('REQ-*/progress.md')}
        result=build(self.root,'PROJ-TEST',as_of='2026-10-06')
        self.assertEqual(result['mode'],'remaining-work'); self.assertEqual(result['total_effort_pd'],1)
        self.assertEqual(result['tasks'][0]['start'],'2026-10-07'); self.assertEqual(result['finish_date'],'2026-10-07')
        self.assertEqual([t['id'] for t in result['tasks']],['REQ-SECOND/WP-01'])
        self.assertEqual(result['actual_effort_known_pd'],3)
        self.assertTrue(all(p.read_bytes()==content for p,content in before.items()))

    def test_forecast_rejects_unknown_remaining_inconsistent_cutoffs_and_unknown_unblock_dates(self):
        self.project(False); path=self.progress('REQ-TEST')
        data=load(path); data['work'][0]['remaining_effort_pd']=None; write(path,data)
        with self.assertRaisesRegex(ValueError,'remaining effort'): build(self.root,'PROJ-TEST',as_of='2026-10-06')
        self.progress('REQ-TEST')
        with self.assertRaisesRegex(ValueError,'cutoff'): build(self.root,'PROJ-TEST',as_of='2026-10-07')
        data=load(path); data['work'][0]['status']='blocked'; write(path,data)
        with self.assertRaisesRegex(ValueError,'unblock'): build(self.root,'PROJ-TEST',as_of='2026-10-06')
        data['work'][0].update(resume_on='2026-10-09',resume_source='test://external-date'); write(path,data)
        self.assertEqual(build(self.root,'PROJ-TEST',as_of='2026-10-06')['tasks'][0]['start'],'2026-10-09')

    def test_cancellation_is_not_automatically_treated_as_a_satisfied_dependency(self):
        path=self.project(); data=load(path)
        data['dependencies']=[{'predecessor':{'requirement_id':'REQ-TEST','work_package_id':'WP-01'},
                               'successor':{'requirement_id':'REQ-SECOND','work_package_id':'WP-01'}}]
        write(path,data); self.progress('REQ-TEST','cancelled',0,0); self.progress('REQ-SECOND')
        with self.assertRaisesRegex(ValueError,'Cancelled predecessor'): build(self.root,'PROJ-TEST',as_of='2026-10-06')

    def test_open_blocker_cannot_be_ignored_by_forecast_status(self):
        self.project(False); path=self.progress('REQ-TEST'); data=load(path)
        data['blockers']=[{'id':'B-1','description':'External readiness','owner':'test-owner',
                          'status':'open','work_packages':['WP-01']}]
        write(path,data)
        with self.assertRaisesRegex(ValueError,'blocked work status'): build(self.root,'PROJ-TEST',as_of='2026-10-06')
        data['work'][0].update(status='blocked',resume_on='2026-10-09',resume_source='test://confirmed-date')
        write(path,data)
        self.assertEqual(build(self.root,'PROJ-TEST',as_of='2026-10-06')['tasks'][0]['start'],'2026-10-09')

    def test_all_completed_forecast_has_no_new_work_and_unknown_actuals_stay_unknown(self):
        self.project(False); self.progress('REQ-TEST','done',0,None)
        result=build(self.root,'PROJ-TEST',as_of='2026-10-06')
        self.assertEqual(result['tasks'],[]); self.assertEqual(result['total_effort_pd'],0)
        self.assertEqual(result['actual_effort_unknown'],['REQ-TEST/WP-01'])

    def test_project_cli_does_not_overwrite_previous_report_when_inputs_fail(self):
        self.project(); result=self.cli('schedule_project.py','--project','PROJ-TEST')
        self.assertEqual(result.returncode,0,result.stderr)
        report=self.root/'vault/projects/PROJ-TEST/schedule-expected.md'; before=report.read_bytes()
        req=load(self.req/'requirement.md'); req['questions']=[{'id':'Q-BLOCK','question':'Clarify','blocking':True,'status':'open','owner':'requester'}]
        write(self.req/'requirement.md',req)
        self.assertNotEqual(self.cli('schedule_project.py','--project','PROJ-TEST').returncode,0)
        self.assertEqual(before,report.read_bytes())

    def test_baseline_records_exact_reviewed_snapshot_and_detects_tampering(self):
        self.project(False); directory=self.root/'vault/projects/PROJ-TEST'
        save(directory/'schedule-expected.md',build(self.root,'PROJ-TEST'))
        _,version=preview(self.root,'PROJ-TEST','schedule-expected.md')
        target=create(self.root,'PROJ-TEST','v1','schedule-expected.md',version,**{k:v for k,v in DECISION.items()})
        verify(self.root,'PROJ-TEST','v1')
        with self.assertRaisesRegex(ValueError,'overwrite'):
            create(self.root,'PROJ-TEST','v1','schedule-expected.md',version,**DECISION)
        req=load(self.req/'requirement.md'); req['goal']='New goal'; write(self.req/'requirement.md',req)
        verify(self.root,'PROJ-TEST','v1')
        with self.assertRaisesRegex(ValueError,'inputs changed'): preview(self.root,'PROJ-TEST','schedule-expected.md')
        snapshot=target/'snapshot/vault/requirements/REQ-TEST/requirement.md'; snapshot.write_text(snapshot.read_text()+'\nChanged\n')
        with self.assertRaisesRegex(ValueError,'content changed'): verify(self.root,'PROJ-TEST','v1')

    def test_requirement_attachments_are_preserved_and_invalidate_stale_report(self):
        self.project(False); directory=self.root/'vault/projects/PROJ-TEST'
        asset=self.req/'assets/evidence.bin'; asset.parent.mkdir(); asset.write_bytes(bytes(range(256)))
        save(directory/'schedule-expected.md',build(self.root,'PROJ-TEST'))
        _,version=preview(self.root,'PROJ-TEST','schedule-expected.md')
        target=create(self.root,'PROJ-TEST','v1','schedule-expected.md',version,**DECISION)
        self.assertEqual((target/'snapshot'/asset.relative_to(self.root)).read_bytes(),asset.read_bytes())
        asset.write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError,'inputs changed'): preview(self.root,'PROJ-TEST','schedule-expected.md')
        verify(self.root,'PROJ-TEST','v1')


if __name__=='__main__': unittest.main()

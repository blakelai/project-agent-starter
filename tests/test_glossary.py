"""Domain terminology fixtures remain in temporary repositories, never in the starter vault."""
import copy
import subprocess
import sys
import unittest

import test_tools
import test_brd
from common import digest, load, write
from glossary import START, END, read_term, term_errors, validate_catalog
from terminology import create_term, confirm, link, refresh, report
from validate import validate

AT = '2026-10-07T20:00:00+08:00'
REVIEW = {'status': 'reviewed', 'by': 'test-reviewer', 'at': AT, 'notes': 'Reviewed fixture scope and meaning'}


class GlossaryTests(unittest.TestCase):
    def setUp(self):
        self.fixture = test_tools.ArtifactTests('test_ready_fixture_and_blocked_fixture')
        self.fixture.setUp()
        self.root, self.req = self.fixture.root, self.fixture.req
        self.assessment = load(self.req/'assessment.md')
        write(self.root/'vault/knowledge/glossary/contexts.md', {'schema_version': 1, 'contexts': [
            {'id': 'CTX-TEST', 'name': '測試上下文', 'definition': '供隔離測試使用的業務邊界。'},
            {'id': 'CTX-OTHER', 'name': '另一上下文', 'definition': '獨立的業務邊界。'}]})

    def tearDown(self):
        self.fixture.tearDown()

    def cli(self, *args):
        return subprocess.run([sys.executable, str(self.root/'scripts/terminology.py'), *args],
                              cwd=self.root, capture_output=True, text=True)

    def term(self, identifier='TERM-TEST', context='CTX-TEST'):
        return create_term(self.root, identifier, '測試用語', context)

    def define(self, identifier='TERM-TEST', name='測試概念'):
        term = read_term(self.root, identifier); path = term['path']
        content = path.read_text()
        before, rest = content.split(START); _, after = rest.split(END)
        path.write_text(before + START + '\n\n此測試概念有明確的業務邊界。\n\n' + END + after)
        data = load(path)
        data['names']['zh-TW'] = name
        data['sources'] = [{'path': 'test://human/decision', 'revision': 'fixture-v1', 'quote': '人類提供的測試定義。'}]
        data['questions'][0].update(status='resolved', answer='已提供明確定義與邊界。',
                                     answered_by='test-domain-owner', answered_at=AT, source='test://human/decision')
        data['status'] = 'proposed'
        write(path, data)

    def approve(self, identifier='TERM-TEST'):
        confirm(self.root, identifier, read_term(self.root, identifier)['definition_revision'],
                'test-domain-owner', AT, 'test://human/approval')

    def ready(self, directory=None):
        directory = directory or self.req
        req = load(directory/'requirement.md')
        req.update(status='assessed', terminology_review=copy.deepcopy(REVIEW))
        for ref in req.get('term_refs', []):
            ref['review'] = copy.deepcopy(REVIEW)
            term = read_term(self.root, ref['term_id'])
            for q in req['questions']:
                if q.get('term_question', {}).get('term_id') != ref['term_id']:
                    continue
                shared = next(tq for tq in term['data']['questions'] if tq['id'] == q['term_question']['question_id'])
                if shared['status'] == 'resolved':
                    q.update(status='resolved', answer='已依共用答案完成本需求影響檢閱。',
                             source=f'{ref["term_id"]}/{shared["id"]}', term_revision=ref['source_revision'])
        write(directory/'requirement.md', req)
        write(directory/'assessment.md', copy.deepcopy(self.assessment))

    def confirmed_link(self):
        self.term(); self.define(); self.approve()
        link(self.root, 'REQ-TEST', 'TERM-TEST', ['FR-01'])
        self.ready()

    def test_cli_creates_only_unknown_stub_and_refuses_overwrite_or_bad_ids(self):
        result = self.cli('init', 'TERM-NEW', '--label', '未明縮寫')
        self.assertEqual(result.returncode, 0, result.stderr)
        term = read_term(self.root, 'TERM-NEW')
        self.assertEqual(term['definition'], '')
        self.assertIsNone(term['data']['context_id'])
        self.assertEqual(term['data']['names'], {'zh-TW': None, 'en': None})
        self.assertIsNone(term['data']['confirmation'])
        self.assertEqual(validate_catalog(self.root), [])
        self.assertNotEqual(self.cli('init', 'TERM-NEW', '--label', '覆寫').returncode, 0)
        self.assertNotEqual(self.cli('init', '../escape', '--label', '測試').returncode, 0)
        queue = (term['path'].parent/'clarification-queue.md').read_text()
        self.assertIn('TERM-NEW/TQ-01', queue)

    def test_confirmation_requires_human_metadata_content_scope_and_resolved_questions(self):
        path = self.term(context=None)
        with self.assertRaises(ValueError):
            self.approve()
        self.define()
        with self.assertRaisesRegex(ValueError, 'context'):
            self.approve()
        data = load(path); data['context_id'] = 'CTX-TEST'; write(path, data)
        before = path.read_bytes()
        current = read_term(self.root, 'TERM-TEST')['definition_revision']
        with self.assertRaises(ValueError):
            confirm(self.root, 'TERM-TEST', current, '', AT, 'test://approval')
        with self.assertRaises(ValueError):
            confirm(self.root, 'TERM-TEST', current, 'human', '2026-10-07', 'test://approval')
        self.assertEqual(before, path.read_bytes())
        data['questions'][0]['status'] = 'open'; write(path, data)
        with self.assertRaisesRegex(ValueError, 'Open definition'):
            self.approve()

    def test_reviewed_revision_cannot_confirm_later_edits(self):
        path = self.term(); self.define()
        old = read_term(self.root, 'TERM-TEST')['definition_revision']
        path.write_text(path.read_text().replace('明確的業務邊界', '不同的業務邊界'))
        before = path.read_bytes()
        with self.assertRaisesRegex(ValueError, 'changed since human review'):
            confirm(self.root, 'TERM-TEST', old, 'human', AT, 'test://approval')
        self.assertEqual(before, path.read_bytes())

    def test_same_word_in_different_contexts_is_allowed_but_conflicting_aliases_are_not(self):
        self.term(); self.define(); self.approve()
        self.term('TERM-OTHER', 'CTX-OTHER'); self.define('TERM-OTHER'); self.approve('TERM-OTHER')
        self.assertEqual(validate_catalog(self.root), [])
        path = self.term('TERM-CONFLICT'); self.define('TERM-CONFLICT', '別的名稱')
        data = load(path); data['aliases'] = [{'language': 'zh-TW', 'value': '測試概念'}]; write(path, data)
        with self.assertRaisesRegex(ValueError, 'Ambiguous confirmed label'):
            self.approve('TERM-CONFLICT')

    def test_unconfirmed_meaning_cannot_pass_even_after_local_question_is_downgraded(self):
        self.term(); link(self.root, 'REQ-TEST', 'TERM-TEST', ['FR-01']); self.ready()
        req = load(self.req/'requirement.md'); req['questions'][0]['blocking'] = False
        write(self.req/'requirement.md', req)
        errors = validate(self.root, self.req, True)
        self.assertTrue(any('unconfirmed meaning' in e for e in errors), errors)
        req['questions'][0].update(status='resolved', answer='Guess', source='Assumed')
        write(self.req/'requirement.md', req)
        self.assertTrue(validate(self.root, self.req, True))

    def test_accepted_definition_with_unresolved_optional_translation_can_proceed(self):
        path = self.term(); self.define()
        data = load(path); data['questions'].append({'id': 'TQ-02', 'question': '正式英文譯名為何？',
            'affects_definition': False, 'status': 'open', 'owner': None}); write(path, data)
        self.approve(); link(self.root, 'REQ-TEST', 'TERM-TEST', ['FR-01']); self.ready()
        self.assertEqual(validate(self.root, self.req, True), [])
        self.assertFalse(load(self.req/'requirement.md')['questions'][0]['blocking'])

    def test_background_unknown_can_proceed_with_exclusion_reason_but_cannot_define_fr(self):
        self.term()
        with self.assertRaises(ValueError):
            link(self.root, 'REQ-TEST', 'TERM-TEST', ['FR-01'], usage='background', reason='Not applicable')
        link(self.root, 'REQ-TEST', 'TERM-TEST', usage='background', reason='Quoted background outside this scope')
        self.ready(); self.assertEqual(validate(self.root, self.req, True), [])
        req = load(self.req/'requirement.md'); req['term_refs'][0]['functional_requirement_ids'] = ['FR-01']
        write(self.req/'requirement.md', req)
        self.assertTrue(any('cannot define an FR' in e for e in validate(self.root, self.req, True)))

    def test_shared_answer_is_not_auto_closed_or_approved_across_assessments(self):
        self.term()
        link(self.root, 'REQ-TEST', 'TERM-TEST')
        link(self.root, 'REQ-BLOCKED', 'TERM-TEST')
        self.define(); self.approve()
        for identifier in ['REQ-TEST', 'REQ-BLOCKED']:
            self.assertEqual(refresh(self.root, identifier), ['TERM-TEST'])
            directory = self.root/'vault/requirements'/identifier
            req = load(directory/'requirement.md')
            q = next(q for q in req['questions'] if q.get('term_question'))
            self.assertEqual(q['status'], 'open')
            self.assertNotIn('answer', q)
            self.assertFalse(load(directory/'assessment.md')['ready_for_planning'])

    def test_definition_and_context_changes_invalidate_confirmation_and_source_references(self):
        self.confirmed_link(); self.assertEqual(validate(self.root, self.req, True), [])
        path = read_term(self.root, 'TERM-TEST')['path']
        original = path.read_text(); path.write_text(original.replace('明確的業務邊界', '另一個業務邊界'))
        self.assertTrue(any('human reconfirmation' in e for e in validate(self.root, self.req, True)))
        path.write_text(original)
        context = self.root/'vault/knowledge/glossary/contexts.md'; data = load(context)
        data['contexts'][0]['definition'] = 'Changed business boundary'; write(context, data)
        self.assertTrue(any('human reconfirmation' in e for e in validate(self.root, self.req, True)))

    def test_definition_image_changes_and_unsupported_images_are_detected(self):
        path = self.term(); self.define()
        image = path.parent/'assets/TERM-TEST/figure.png'; image.parent.mkdir(parents=True); image.write_bytes(b'fixture image')
        original = path.read_text()
        path.write_text(original.replace(END, '![圖](assets/TERM-TEST/figure.png)\n\n' + END))
        self.approve(); link(self.root, 'REQ-TEST', 'TERM-TEST'); self.ready()
        self.assertEqual(validate(self.root, self.req, True), [])
        image.write_bytes(b'changed fixture image')
        self.assertTrue(any('human reconfirmation' in e for e in validate(self.root, self.req, True)))
        for value in ['![image](https://example.invalid/image.png)', '![[figure.png]]', '![image](../../outside.png)']:
            path.write_text(original.replace(END, value+'\n'+END))
            with self.assertRaises(ValueError):
                read_term(self.root, 'TERM-TEST')

    def test_system_mapping_changes_do_not_confirm_or_change_business_definition(self):
        self.confirmed_link()
        term = read_term(self.root, 'TERM-TEST'); path = term['path']; data = term['data']
        data['system_mappings'] = [{'id': 'MAP-01', 'kind': 'proposed', 'path': 'test://adr/1',
            'revision': 'v1', 'description': 'Proposed implementation', 'decision_ref': 'Draft ADR'}]
        write(path, data)
        updated = read_term(self.root, 'TERM-TEST')
        self.assertEqual(term['definition_revision'], updated['definition_revision'])
        self.assertEqual(term_errors(self.root, updated), [])
        self.assertNotEqual(term['source_revision'], updated['source_revision'])
        data['system_mappings'][0]['kind'] = 'current'; write(path, data)
        self.assertTrue(any('verification evidence' in e for e in term_errors(self.root, read_term(self.root, 'TERM-TEST'))))

    def test_refresh_preserves_analysis_and_custom_fields_but_resets_readiness(self):
        self.confirmed_link()
        req = load(self.req/'requirement.md'); req['term_refs'][0]['custom'] = 'keep'; write(self.req/'requirement.md', req)
        fr_before = copy.deepcopy(req['functional_requirements'])
        self.assertEqual(refresh(self.root, 'REQ-TEST'), [])
        path = read_term(self.root, 'TERM-TEST')['path']
        path.write_text(path.read_text().replace('明確的業務邊界', '修訂的業務邊界'))
        self.approve()
        self.assertEqual(refresh(self.root, 'REQ-TEST'), ['TERM-TEST'])
        req = load(self.req/'requirement.md')
        self.assertEqual(req['functional_requirements'], fr_before)
        self.assertEqual(req['term_refs'][0]['custom'], 'keep')
        self.assertEqual(req['term_refs'][0]['review']['status'], 'pending')
        self.assertEqual(req['terminology_review']['status'], 'pending')
        self.assertFalse(load(self.req/'assessment.md')['ready_for_planning'])
        self.assertEqual(len(load(path)['confirmation_history']), 1)
        self.ready(); self.assertEqual(validate(self.root, self.req, True), [])

    def test_baseline_and_closed_assessments_are_not_modified(self):
        self.confirmed_link()
        for state in ['baseline', 'closed']:
            req = load(self.req/'requirement.md'); req['status'] = state; write(self.req/'requirement.md', req)
            before = {p: p.read_bytes() for p in self.req.glob('*.md')}
            with self.assertRaisesRegex(ValueError, 'baseline/closed'):
                refresh(self.root, 'REQ-TEST')
            self.assertTrue(all(p.read_bytes() == content for p, content in before.items()))

    def test_reports_show_impacted_requirements_and_unrelated_unknown_terms_do_not_block(self):
        self.confirmed_link(); self.term('TERM-UNRELATED')
        self.assertEqual(validate(self.root, self.req, True), [])
        path = read_term(self.root, 'TERM-TEST')['path']; path.write_text(path.read_text()+'\n修訂備註。\n')
        report(self.root)
        queue = (path.parent/'clarification-queue.md').read_text()
        self.assertIn('REQ-TEST', queue); self.assertIn('引用版本已變更', queue); self.assertIn('TERM-UNRELATED/TQ-01', queue)

    def test_missing_review_dangling_links_and_deleted_questions_are_rejected(self):
        self.term(); link(self.root, 'REQ-TEST', 'TERM-TEST')
        self.define(); self.approve(); refresh(self.root, 'REQ-TEST'); self.ready()
        req = load(self.req/'requirement.md'); req['terminology_review']['status'] = 'pending'; write(self.req/'requirement.md', req)
        self.assertTrue(any('review is pending' in e for e in validate(self.root, self.req, True)))
        self.ready(); path = read_term(self.root, 'TERM-TEST')['path']; data = load(path); data['questions'] = []; write(path, data)
        refresh(self.root, 'REQ-TEST')
        self.assertTrue(any('dangling term question' in e for e in validate(self.root, self.req)))
        req = load(self.req/'requirement.md'); req['term_refs'][0]['term_id'] = 'TERM-MISSING'; write(self.req/'requirement.md', req)
        self.assertTrue(validate(self.root, self.req))

    def test_schedule_tracks_terms_and_preserves_old_output_on_source_drift(self):
        self.confirmed_link()
        command = [sys.executable, str(self.root/'scripts/schedule.py'), '--requirement', 'REQ-TEST']
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        path = read_term(self.root, 'TERM-TEST')['path']
        output = self.req/'schedule-expected.md'
        self.assertEqual(load(output)['input_sha256']['term:TERM-TEST'], digest(path))
        before = output.read_bytes(); path.write_text(path.read_text()+'\nUpdated note.\n')
        self.assertNotEqual(subprocess.run(command, capture_output=True).returncode, 0)
        self.assertEqual(before, output.read_bytes())

    def test_brd_term_cli_workflow_and_source_refresh_revoke_terminology_review(self):
        from refresh_brd import refresh as refresh_sources
        brd = test_brd.BRDTests.document(self, image=False)
        test_brd.BRDTests.attach_ready(self, brd)
        self.assertEqual(self.cli('init', 'TERM-TEST', '--label', '測試用語', '--context', 'CTX-TEST').returncode, 0)
        before = (self.req/'requirement.md').read_bytes()
        self.assertNotEqual(self.cli('link', 'REQ-TEST', 'TERM-TEST', '--source-item', 'BRD-TEST/br-999').returncode, 0)
        self.assertEqual(before, (self.req/'requirement.md').read_bytes())
        result = self.cli('link', 'REQ-TEST', 'TERM-TEST', '--fr', 'FR-01', '--source-item', 'BRD-TEST/br-001')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.define()
        version = self.cli('revision', 'TERM-TEST').stdout.strip()
        result = self.cli('confirm', 'TERM-TEST', '--revision', version, '--by', 'test-human', '--at', AT, '--source', 'test://approval')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.cli('refresh', 'REQ-TEST').returncode, 0)
        self.ready(); self.assertEqual(validate(self.root, self.req, True), [])
        brd.write_text(brd.read_text()+'\n原文新增說明。\n')
        refresh_sources(self.root, self.req)
        req = load(self.req/'requirement.md')
        self.assertEqual(req['terminology_review']['status'], 'pending')
        self.assertEqual(req['term_refs'][0]['review']['status'], 'pending')
        self.assertFalse(load(self.req/'assessment.md')['ready_for_planning'])


if __name__ == '__main__':
    unittest.main()

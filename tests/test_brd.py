"""BRD fixtures and binary attachments exist only in isolated temporary repositories."""
import base64
import copy
from pathlib import Path
import subprocess
import sys
import unittest

import test_tools
from brd import capture_brd, pending_coverage, read_brd, registered_sources
from common import digest, load, write
from okf import render_note, split_note
from refresh_brd import refresh
from validate import validate

PNG = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jRZkAAAAASUVORK5CYII=')


class BRDTests(unittest.TestCase):
    def setUp(self):
        self.fixture = test_tools.ArtifactTests('test_ready_fixture_and_blocked_fixture')
        self.fixture.setUp()
        self.root, self.req = self.fixture.root, self.fixture.req

    def tearDown(self):
        self.fixture.tearDown()

    def cli(self, script, *args):
        return subprocess.run([sys.executable, str(self.root/'scripts'/script), *args],
                              cwd=self.root, capture_output=True, text=True)

    def document(self, identifier='BRD-TEST', items=1, image=True, extra=''):
        folder = self.root/'vault/intake'/identifier
        (folder/'assets').mkdir(parents=True)
        metadata = {'type':'Business Requirements Document', 'id':identifier,
                    'title':'使用者原始需求', 'status':'draft'}
        sections = ['# 使用者原始需求', '| 項目 | 原始要求 |', '|---|---|', '| 結果 | 保留原始表格 |']
        for i in range(items):
            sections += [f'## br-{i+1:03}', '**標題：** 需要評估的成果', '使用者提供的原始敘述。']
        if image:
            (folder/'assets/diagram.png').write_bytes(PNG)
            sections += ['![FIG-001：來源流程圖](assets/diagram.png)']
        (folder/'brd.md').write_text(render_note(metadata, '\n\n'.join(sections)+'\n'+extra), encoding='utf-8')
        return folder/'brd.md'

    def attach_ready(self, path):
        doc = capture_brd(self.root, path)
        for asset in doc['assets']:
            asset.update(review_status='reviewed', reviewed_by='test-reviewer',
                         reviewed_at='2026-10-07T12:00:00+08:00', notes='Fixture image inspection record')
        req = load(self.req/'requirement.md')
        req['source_documents'] = [doc]
        req['functional_requirements'][0]['source_refs'] = [
            {'document_id':doc['id'], 'item_id':item} for item in doc['item_ids']]
        trace = load(self.req/'traceability.md')
        trace['source_coverage'] = pending_coverage([doc])
        for row in trace['source_coverage']:
            row.update(disposition='analyzed', functional_requirement_ids=['FR-01'])
        write(self.req/'requirement.md', req)
        write(self.req/'traceability.md', trace)
        write(self.root/'vault/knowledge/sources.md', registered_sources(self.root, [doc]))
        return doc

    def test_blank_brd_creation_and_no_overwrite(self):
        command = ('BRD-NEW', '--title', '正式標題')
        result = self.cli('init_brd.py', *command)
        self.assertEqual(result.returncode, 0, result.stderr)
        path = self.root/'vault/intake/BRD-NEW/brd.md'
        metadata, _, _ = split_note(path.read_text())
        self.assertEqual(metadata['id'], 'BRD-NEW')
        self.assertEqual(metadata['title'], '正式標題')
        self.assertTrue((path.parent/'assets').is_dir())
        self.assertIn('BRD-NEW/index.md', (path.parent.parent/'index.md').read_text())
        self.assertNotEqual(self.cli('init_brd.py', *command).returncode, 0)
        self.assertNotEqual(self.cli('init_brd.py', '../escape', '--title', 'Title').returncode, 0)
        result = self.cli('init_requirement.py', 'REQ-EMPTY', '--source', str(path))
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.root/'vault/requirements/REQ-EMPTY').exists())

    def test_multiple_sources_preserve_original_bytes_and_start_unreviewed(self):
        first = self.document(items=2)
        second = self.document('BRD-SECOND', image=False)
        template_asset = self.root/'vault/templates/requirement/assets/fixture.png'
        template_asset.parent.mkdir()
        template_asset.write_bytes(PNG)
        original, image_bytes = first.read_bytes(), (first.parent/'assets/diagram.png').read_bytes()
        result = self.cli('init_requirement.py', 'REQ-IMPORT', '--source', str(first), '--source', str(second))
        self.assertEqual(result.returncode, 0, result.stderr)
        directory = self.root/'vault/requirements/REQ-IMPORT'
        self.assertEqual((directory/'assets/fixture.png').read_bytes(), PNG)
        req = load(directory/'requirement.md')
        self.assertEqual(len(req['source_documents']), 2)
        self.assertEqual(req['source_documents'][0]['assets'][0]['review_status'], 'pending')
        self.assertEqual(len(load(directory/'traceability.md')['source_coverage']), 3)
        self.assertFalse(load(directory/'assessment.md')['ready_for_planning'])
        self.assertEqual(first.read_bytes(), original)
        self.assertEqual((first.parent/'assets/diagram.png').read_bytes(), image_bytes)
        self.assertEqual(validate(self.root, directory), [])
        self.assertIn('../../intake/BRD-TEST/brd.md', (directory/'requirement.md').read_text())
        # A second REQ can reference the same BRD without duplicating its registry identity.
        self.assertEqual(self.cli('init_requirement.py', 'REQ-SPLIT', '--source', str(first)).returncode, 0)
        self.assertEqual(len(load(self.root/'vault/knowledge/sources.md')['sources']), 2)

    def test_invalid_import_has_no_partial_requirement_or_registry_update(self):
        path = self.document()
        (path.parent/'assets/diagram.png').unlink()
        registry = (self.root/'vault/knowledge/sources.md').read_bytes()
        result = self.cli('init_requirement.py', 'REQ-BAD', '--source', str(path))
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.root/'vault/requirements/REQ-BAD').exists())
        self.assertEqual((self.root/'vault/knowledge/sources.md').read_bytes(), registry)

    def test_duplicate_ids_and_unsupported_or_external_images_are_rejected(self):
        path = self.document(image=False)
        original = path.read_text()
        invalid = ['## br-001\nDuplicate', '## BR-002\nWrong case',
                   '![image](https://example.invalid/image.png)', '![[assets/image.png]]',
                   '![image][ref]\n[ref]: assets/image.png', '<img src="assets/image.png">',
                   '![image](../../outside.png)', f'![image]({path.parent}/assets/image.png)',
                   '```md\nunterminated']
        for text in invalid:
            with self.subTest(text=text):
                path.write_text(original+'\n'+text)
                with self.assertRaises(ValueError):
                    read_brd(self.root, path)

    def test_code_examples_are_not_requirements_or_image_inputs(self):
        path = self.document(extra='```md\n## br-001\n![code](missing.png)\n```\n`![inline](missing.png)`')
        result = read_brd(self.root, path)
        self.assertEqual(result['item_ids'], ['br-001'])
        self.assertEqual(len(result['assets']), 1)

    def test_symlink_escape_is_rejected(self):
        path = self.document()
        image = path.parent/'assets/diagram.png'
        image.unlink()
        outside = self.root/'outside.png'; outside.write_bytes(PNG)
        image.symlink_to(outside)
        with self.assertRaisesRegex(ValueError, 'out-of-bounds'):
            read_brd(self.root, path)

    def test_pending_or_unreadable_images_block_readiness(self):
        self.attach_ready(self.document())
        self.assertEqual(validate(self.root, self.req, True), [])
        req = load(self.req/'requirement.md')
        for state in ['pending','unreadable']:
            req['source_documents'][0]['assets'][0]['review_status'] = state
            write(self.req/'requirement.md', req)
            errors = validate(self.root, self.req, True)
            self.assertTrue(any('image not reviewed' in e for e in errors), errors)
        req['source_documents'][0]['assets'][0].update(review_status='reviewed', notes=None)
        write(self.req/'requirement.md', req)
        self.assertTrue(any('image review needs' in e for e in validate(self.root, self.req)))

    def test_missing_or_inconsistent_original_item_coverage_is_rejected(self):
        self.attach_ready(self.document(items=2, image=False))
        self.assertEqual(validate(self.root, self.req, True), [])
        trace = load(self.req/'traceability.md')
        removed = trace['source_coverage'].pop()
        write(self.req/'traceability.md', trace)
        self.assertTrue(any('every original item' in e for e in validate(self.root, self.req)))
        trace['source_coverage'].append(removed)
        trace['source_coverage'][0]['functional_requirement_ids'] = []
        write(self.req/'traceability.md', trace)
        self.assertTrue(any('differs from FR' in e for e in validate(self.root, self.req)))

    def test_deferred_scope_needs_a_decision_before_planning(self):
        self.attach_ready(self.document(items=2, image=False))
        req = load(self.req/'requirement.md')
        req['functional_requirements'][0]['source_refs'].pop()
        write(self.req/'requirement.md', req)
        trace = load(self.req/'traceability.md')
        trace['source_coverage'][1].update(disposition='deferred', functional_requirement_ids=[], reason='Await next scope decision')
        write(self.req/'traceability.md', trace)
        self.assertTrue(any('decision_ref' in e for e in validate(self.root, self.req, True)))
        trace['source_coverage'][1]['decision_ref'] = 'Recorded test scope decision'
        write(self.req/'traceability.md', trace)
        self.assertEqual(validate(self.root, self.req, True), [])

    def test_brd_and_image_changes_are_detected(self):
        path = self.document()
        self.attach_ready(path)
        original = path.read_bytes()
        path.write_bytes(original+b'\nSource clarification.\n')
        self.assertTrue(any('attachment changed' in e for e in validate(self.root, self.req)))
        path.write_bytes(original)
        (path.parent/'assets/diagram.png').write_bytes(PNG+b'changed')
        self.assertTrue(any('attachment changed' in e for e in validate(self.root, self.req)))

    def test_refresh_preserves_analysis_and_invalidates_only_changed_sources(self):
        path = self.document()
        doc = self.attach_ready(path)
        original_fr = copy.deepcopy(load(self.req/'requirement.md')['functional_requirements'])
        self.assertEqual(refresh(self.root, self.req), [])
        self.assertEqual(load(self.req/'requirement.md')['source_documents'][0], doc)
        path.write_text(path.read_text()+'\n## br-002\n\n**標題：** 新增需求\n補充原文。\n')
        self.assertEqual(refresh(self.root, self.req), ['BRD-TEST'])
        req = load(self.req/'requirement.md')
        self.assertEqual(req['functional_requirements'], original_fr)
        self.assertEqual(req['status'], 'intake')
        self.assertEqual(req['source_documents'][0]['assets'][0]['review_status'], 'pending')
        self.assertFalse(load(self.req/'assessment.md')['ready_for_planning'])
        self.assertIsNone(load(self.req/'assessment.md')['reviewed_by'])
        self.assertEqual([r['disposition'] for r in load(self.req/'traceability.md')['source_coverage']], ['pending','pending'])
        self.assertEqual(validate(self.root, self.req), [])
        self.assertEqual(refresh(self.root, self.req), [])

    def test_removed_item_references_are_not_silently_erased(self):
        path = self.document(items=2, image=False)
        self.attach_ready(path)
        path.write_text(path.read_text().split('## br-002')[0])
        refresh(self.root, self.req)
        errors = validate(self.root, self.req)
        self.assertTrue(any('unknown BRD item' in e for e in errors), errors)
        self.assertEqual(len(load(self.req/'requirement.md')['functional_requirements'][0]['source_refs']), 2)

    def test_baseline_refresh_is_refused_without_changes(self):
        self.attach_ready(self.document())
        assess = load(self.req/'assessment.md'); assess['status'] = 'baseline'
        write(self.req/'assessment.md', assess)
        before = {p:p.read_bytes() for p in self.req.glob('*.md')}
        with self.assertRaisesRegex(ValueError, 'baseline/closed'):
            refresh(self.root, self.req)
        self.assertTrue(all(p.read_bytes() == data for p,data in before.items()))

    def test_evidence_revision_and_schedule_provenance(self):
        path = self.document()
        doc = self.attach_ready(path)
        evidence = {'schema_version':1, 'evidence':[{'id':'E-01', 'source_id':doc['id'],
                    'path':doc['path']+'#br-001', 'source_revision':'wrong', 'observed_at':'2026-10-07',
                    'state':'CONFIRMED', 'claim':'The original item states this request.'}]}
        write(self.req/'evidence.md', evidence)
        self.assertTrue(any('stale BRD evidence' in e for e in validate(self.root, self.req)))
        evidence['evidence'][0]['source_revision'] = doc['source_revision']
        write(self.req/'evidence.md', evidence)
        result = self.cli('schedule.py', '--requirement', 'REQ-TEST')
        self.assertEqual(result.returncode, 0, result.stderr)
        schedule = load(self.req/'schedule-expected.md')
        self.assertEqual(schedule['input_sha256']['brd:BRD-TEST'], digest(path))
        image = doc['assets'][0]
        self.assertEqual(schedule['input_sha256']['asset:'+image['path']], image['sha256'])
        (path.parent/'assets/diagram.png').write_bytes(PNG+b'changed')
        old_output = (self.req/'schedule-expected.md').read_bytes()
        self.assertNotEqual(self.cli('schedule.py', '--requirement', 'REQ-TEST').returncode, 0)
        self.assertEqual((self.req/'schedule-expected.md').read_bytes(), old_output)


if __name__ == '__main__':
    unittest.main()

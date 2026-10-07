import tempfile
import unittest
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from okf import PROFILE, data_block, render_note, check_note, split_note, load_data, write_data


class OKFTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.bundle=Path(self.tmp.name)
        self.path=self.bundle/'note.md'
        self.metadata={'type':'Custom Project Type','status':'draft','project_profile':PROFILE,
                       'extension':{'keep':'unchanged'}}
        self.data={'schema_version':1,'status':'assessed','extension':{'keep':[1,2]}}
        self.body='# 說明\n\n保留作者的文字與 [連結](other.md)。\n\n'+data_block(self.data)+'\n\n## 判斷\n\n尚待確認。'
        self.path.write_text(render_note(self.metadata,self.body),encoding='utf-8')
    def tearDown(self):
        self.tmp.cleanup()
    def test_update_preserves_metadata_unknown_fields_and_surrounding_prose(self):
        original=self.path.read_text()
        updated=load_data(self.path)
        updated['status']='baseline'
        write_data(self.path,updated)
        text=self.path.read_text()
        self.assertEqual(split_note(original)[0],split_note(text)[0])
        self.assertEqual(load_data(self.path)['extension'],{'keep':[1,2]})
        self.assertIn('保留作者的文字與 [連結](other.md)。',text)
        self.assertIn('## 判斷\n\n尚待確認。',text)
    def test_okf_and_workflow_status_are_independent(self):
        check_note(self.path,self.bundle)
        self.metadata['status']='assessed'
        self.path.write_text(render_note(self.metadata,self.body))
        with self.assertRaisesRegex(ValueError,'OKF status'):
            check_note(self.path,self.bundle)
    def test_duplicate_block_is_rejected(self):
        self.path.write_text(render_note(self.metadata,self.body+'\n'+data_block(self.data)))
        with self.assertRaisesRegex(ValueError,'exactly one'):
            load_data(self.path)
    def test_duplicate_yaml_key_is_rejected(self):
        self.path.write_text(self.path.read_text().replace('schema_version: 1','schema_version: 1\nschema_version: 2'))
        with self.assertRaisesRegex(ValueError,'Duplicate YAML key'):
            load_data(self.path)
    def test_broken_data_fence_and_missing_frontmatter_rejected(self):
        self.path.write_text(render_note(self.metadata,self.body.replace('```yaml','```json')))
        with self.assertRaisesRegex(ValueError,'fenced yaml'):
            load_data(self.path)
        self.path.write_text('# missing metadata\n')
        with self.assertRaisesRegex(ValueError,'frontmatter'):
            check_note(self.path,self.bundle)
    def test_index_exception_is_only_at_bundle_root(self):
        path=self.bundle/'index.md'
        path.write_text('---\nokf_version: "0.2"\n---\n# 導覽\n')
        check_note(path,self.bundle)
        nested=self.bundle/'nested'; nested.mkdir()
        (nested/'index.md').write_text(path.read_text())
        with self.assertRaisesRegex(ValueError,'bundle-root'):
            check_note(nested/'index.md',self.bundle)
    def test_provenance_requires_resource_and_timezone(self):
        self.metadata['sources']=[{'id':'repo-with-no-resource'}]
        self.path.write_text(render_note(self.metadata,self.body))
        with self.assertRaisesRegex(ValueError,'resource'):
            check_note(self.path,self.bundle)
        self.metadata['sources']=[{'resource':'other.md'}]
        self.metadata['verified']={'by':'human:reviewer','at':'2026-10-07T12:00:00'}
        self.path.write_text(render_note(self.metadata,self.body))
        with self.assertRaisesRegex(ValueError,'UTC offset'):
            check_note(self.path,self.bundle)
        self.metadata['verified']['at']='2026-10-07T12:00:00+08:00'
        self.path.write_text(render_note(self.metadata,self.body))
        check_note(self.path,self.bundle)


if __name__=='__main__': unittest.main()

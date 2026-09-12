import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location('prepare_study', Path(__file__).resolve().parents[1] / 'tools/prepare_study.py')
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)


class StagingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.src = self.root / 'r003.blend'
        self.src.write_bytes(b'file-copy-test-fixture-not-a-rendered-asset\x00')
        self.out = self.root / 'r004'

    def test_dry_run_does_not_create_directory(self):
        self.assertEqual(M.make_plan(self.src, self.out)['status'], 'DRY_RUN')
        self.assertFalse(self.out.exists())

    def test_hash_is_sha256(self):
        import hashlib
        self.assertEqual(M.sha256(self.src), hashlib.sha256(self.src.read_bytes()).hexdigest())

    def test_wrong_expected_hash_rejected(self):
        with self.assertRaises(ValueError): M.make_plan(self.src, self.out, '0' * 64)
        self.assertFalse(self.out.exists())

    def test_malformed_expected_hash_rejected(self):
        with self.assertRaises(ValueError): M.make_plan(self.src, self.out, 'unknown')

    def test_backup_not_automatically_accepted(self):
        backup = self.root / 'r003.blend1'; backup.write_bytes(b'backup')
        with self.assertRaises(ValueError): M.make_plan(backup, self.out)

    def test_existing_output_is_not_replaced(self):
        self.out.mkdir(); marker = self.out / 'keep'; marker.write_text('user work')
        with self.assertRaises(FileExistsError): M.make_plan(self.src, self.out)
        self.assertEqual(marker.read_text(), 'user work')

    def test_staged_copies_match_and_original_unchanged(self):
        before = self.src.read_bytes(); record = M.stage(M.make_plan(self.src, self.out))
        self.assertEqual(self.src.read_bytes(), before)
        for key in ('baseline_name', 'candidate_name'):
            self.assertEqual((self.out / record[key]).read_bytes(), before)
        self.assertFalse(record['geometry_evaluated'])

    def test_record_labels_unapproved(self):
        M.stage(M.make_plan(self.src, self.out))
        record = json.loads((self.out / 'staging_record.json').read_text())
        self.assertEqual(record['status'], 'STAGED_UNAPPROVED_SOURCE_COPIES')
        self.assertFalse(record['blender_executed'])

    def test_changed_source_after_plan_is_rejected(self):
        plan = M.make_plan(self.src, self.out); self.src.write_bytes(b'new user work')
        with self.assertRaises(RuntimeError): M.stage(plan)
        self.assertFalse(self.out.exists())

    def test_second_stage_cannot_overwrite(self):
        plan = M.make_plan(self.src, self.out); M.stage(plan)
        with self.assertRaises(FileExistsError): M.stage(plan)

    def test_missing_source_rejected(self):
        with self.assertRaises(FileNotFoundError): M.make_plan(self.root / 'missing.blend', self.out)

    def test_matching_expected_hash_accepted(self):
        self.assertEqual(M.make_plan(self.src, self.out, M.sha256(self.src))['source_sha256'], M.sha256(self.src))


if __name__ == '__main__': unittest.main()

"""Fault injection: reusable blank records must never grant readiness or acceptance."""
import importlib.util
import json
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('pipeline_validator', ROOT / 'tools/production/validate_creature_pipeline.py')
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


class TemplateGateTests(unittest.TestCase):
    def validate_modified_template(self, name, change):
        target = validator.PACK / 'templates' / name
        original_read = Path.read_text
        document = json.loads(original_read(target, encoding='utf-8'))
        change(document)
        def read(path, *args, **kwargs):
            return json.dumps(document) if path == target else original_read(path, *args, **kwargs)
        with patch.object(Path, 'read_text', read):
            return validator.validate()['errors']

    def test_real_blank_templates_are_valid(self):
        self.assertEqual(validator.validate()['errors'], [])

    def test_unexecuted_deformation_cannot_start_passed(self):
        errors = self.validate_modified_template('candidate.json', lambda x: x['engineering_checkpoints']['G3B_deformation'].update(status='pass'))
        self.assertTrue(any('checkpoint' in e for e in errors))

    def test_mirrored_camera_slot_is_rejected(self):
        errors = self.validate_modified_template('camera-set.json', lambda x: x['views'][1].update(camera_side='+Y'))
        self.assertTrue(any('anatomical' in e for e in errors))

    def test_unselected_budget_cannot_claim_measured_zero(self):
        errors = self.validate_modified_template('budget-profile.json', lambda x: x['limits'].update(animation_cpu_ms_per_piece=0))
        self.assertTrue(any('Budget' in e for e in errors))

    def test_template_cannot_contain_live_asset_claim(self):
        errors = self.validate_modified_template('unreal-contracts.json', lambda x: x['contracts'].update({'/Game/Fake': {'class': 'SkeletalMesh'}}))
        self.assertTrue(any('live contracts' in e for e in errors))


if __name__ == '__main__': unittest.main()

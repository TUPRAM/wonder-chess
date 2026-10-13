"""In-memory four-view template checks; no files or provider jobs are changed."""
import importlib.util
import json
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    'baseline_faults', ROOT / 'reports/creature-pipeline-20260921/validate_handbook_faults.py')
baseline = importlib.util.module_from_spec(spec)
spec.loader.exec_module(baseline)


def run():
    previous = baseline.run()
    validator = baseline.validator
    original_read = Path.read_text
    cases = [
        ('missing_view', 'view-set.json', lambda o: o['views'].pop(), 'exactly once in order'),
        ('duplicate_slot', 'view-set.json', lambda o: o['views'][3].update(slot='left'), 'exactly once in order'),
        ('wrong_anatomical_side', 'view-set.json', lambda o: o['views'][1].update(anatomical_view='anatomical_right'), 'exactly once in order'),
        ('invalid_view_records', 'view-set.json', lambda o: o.update(views=['not a record']), 'list of records'),
        ('invented_approval', 'view-set.json', lambda o: o.update(owner_approval='fabricated'), 'unreviewed and not ready'),
        ('false_readiness', 'view-set.json', lambda o: o.update(ready_for_submission=True), 'unreviewed and not ready'),
        ('invented_input', 'view-set.json', lambda o: o['views'][0].update(file='fabricated.png'), 'invented images'),
        ('single_image_default', 'candidate.json', lambda o: o['fixed_owner_choices'].update(new_geometry_input_mode='single_image'), 'four-view default'),
    ]
    results = []
    for name, filename, mutation, expected in cases:
        target = (validator.PACK / 'templates' / filename).resolve()

        def altered_read(path, *args, **kwargs):
            text = original_read(path, *args, **kwargs)
            if path.resolve() != target:
                return text
            obj = json.loads(text)
            mutation(obj)
            return json.dumps(obj)

        with patch.object(Path, 'read_text', altered_read):
            result = validator.validate()
        rejected = result['status'] == 'FAIL' and any(expected in e for e in result['errors'])
        assert rejected, (name, result['errors'])
        results.append({'case': name, 'rejected_as_expected': rejected})
    return {'status': 'PASS', 'scope': 'Documentation/template faults only; no actual image or 3D validation.',
            'existing_faults_rejected': previous['faults_rejected'],
            'four_view_faults_rejected': len(results), 'cases': results}


if __name__ == '__main__':
    print(json.dumps(run(), indent=2))

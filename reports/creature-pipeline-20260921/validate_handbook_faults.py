"""Read-only, in-memory fault checks for the handbook validator.

No live document, template, asset, provider or editor is changed.
"""
import importlib.util
import json
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    'handbook_validator', ROOT / 'tools/production/validate_creature_pipeline.py')
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)
original_read = Path.read_text


def json_change(source, mutation):
    obj = json.loads(source)
    mutation(obj)
    return json.dumps(obj)


def run():
    baseline = validator.validate()
    assert not baseline['errors'], baseline['errors']
    template = 'production/creature-pipeline/templates/'
    cases = [
        ('false_completion', template + 'candidate.json',
         lambda s: json_change(s, lambda o: o.update(complete_for_intended_use=True)),
         'explicitly incomplete'),
        ('false_stage_evidence', template + 'candidate.json',
         lambda s: json_change(s, lambda o: o['stages']['G0'].update(status='accepted_current')),
         'must not contain execution/approval evidence'),
        ('invented_approval', template + 'candidate.json',
         lambda s: json_change(s, lambda o: o.update(approvals=['fabricated'])),
         'must not grant approval'),
        ('default_spending', template + 'candidate.json',
         lambda s: json_change(s, lambda o: o['permissions'].update(new_credit_authorization_from_template=20)),
         'must not grant approval or credits'),
        ('invented_job', template + 'generation-receipt.json',
         lambda s: json_change(s, lambda o: o.update(job_id='fabricated')),
         'must not claim a submitted task'),
        ('paid_job_cap', template + 'generation-receipt.json',
         lambda s: json_change(s, lambda o: o['permission'].update(maximum_credits=20)),
         'must not authorize maximum_credits'),
        ('invented_look_approval', template + 'lighting-profile.json',
         lambda s: json_change(s, lambda o: o.update(owner_approval='fabricated')),
         'must not imply an approved or implemented profile'),
        ('malformed_json', template + 'candidate.json', lambda s: '{', 'Invalid JSON'),
        ('fabricated_csv_result', template + 'audio-cue-sheet.csv',
         lambda s: s + '\nfabricated,pass\n', 'no fabricated rows'),
        ('duplicate_csv_column', template + 'audio-cue-sheet.csv',
         lambda s: s.rstrip() + ',asset_id\n', 'unique header fields'),
        ('broken_local_link', 'production/creature-pipeline/README.md',
         lambda s: s + '\n[Missing test file](missing-validation-fixture.md)\n', 'Broken local link'),
    ]
    results = []
    for name, relative, mutation, expected in cases:
        target = (ROOT / relative).resolve()

        def altered_read(path, *args, **kwargs):
            source = original_read(path, *args, **kwargs)
            return mutation(source) if path.resolve() == target else source

        with patch.object(Path, 'read_text', altered_read):
            result = validator.validate()
        rejected = result['status'] == 'FAIL' and any(expected in e for e in result['errors'])
        assert rejected, (name, result['errors'])
        results.append({'case': name, 'rejected_as_expected': rejected})
    return {'status': 'PASS', 'baseline': baseline['status'],
            'scope': 'In-memory document faults only; no art or runtime validation.',
            'faults_rejected': len(results), 'cases': results}


if __name__ == '__main__':
    print(json.dumps(run(), indent=2))

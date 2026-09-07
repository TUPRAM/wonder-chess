"""Compare actual same-fixture native runs, excluding measured wall time only."""
import csv
import hashlib
import json
from pathlib import Path
import sys


def compare(root):
    result = {'status': 'PASS', 'boundary': 'Actual native before/after regression; no Unreal visual acceptance', 'files': []}
    before = root / 'baseline'
    after = root / 'current'
    names = sorted(path.name for path in before.glob('*.csv'))
    if not names or names != sorted(path.name for path in after.glob('*.csv')):
        raise ValueError('Before/after CSV evidence sets differ or are empty')
    for name in names:
        first, second = (folder / name for folder in (before, after))
        a, b = list(csv.DictReader(first.open(newline=''))), list(csv.DictReader(second.open(newline='')))
        if name == 'tournaments.csv':
            for row in a + b:
                row.pop('wall_ms')
        same = a == b
        result['files'].append({'file': name, 'rows_before': len(a), 'rows_after': len(b), 'equal_except_wall_ms': same,
            'before_sha256': hashlib.sha256(first.read_bytes()).hexdigest(), 'after_sha256': hashlib.sha256(second.read_bytes()).hexdigest()})
        if not same:
            result['status'] = 'FAIL'
    (root / 'equivalence.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
    return result['status'] == 'PASS'


if __name__ == '__main__':
    raise SystemExit(0 if compare(Path(sys.argv[1]).resolve()) else 1)

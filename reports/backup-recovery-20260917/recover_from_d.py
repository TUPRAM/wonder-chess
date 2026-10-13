import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BACKUP = Path('D:/Wonder Chess').resolve()
OUT = Path(__file__).resolve().parent

def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

previous = json.loads((ROOT / 'reports/new-pc-repair-20260916/recovery/final-path-audit.json').read_text())
targets = [r for r in previous if r['status'] in ('missing', 'newly_generated_cache_not_recovered')]
results = []
for row in targets:
    rel = Path(row['path'])
    source = (BACKUP / rel).resolve()
    destination = (ROOT / rel).resolve()
    assert source.is_relative_to(BACKUP) and destination.is_relative_to(ROOT)
    item = {'path': row['path'], 'expected_sha256': row['expected_sha256'], 'source': str(source)}
    if not source.is_file():
        item['status'] = 'backup_missing'
    elif source.stat().st_size != row['expected_bytes'] or digest(source) != row['expected_sha256']:
        item['status'] = 'backup_mismatch'
    elif destination.exists() and digest(destination) == row['expected_sha256']:
        item['status'] = 'already_exact'
    elif destination.exists() and row['status'] != 'newly_generated_cache_not_recovered':
        item['status'] = 'existing_local_file_preserved'
    else:
        if destination.exists():
            saved = OUT / 'preserved-generated-cache' / rel
            saved.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(destination, saved)
            item['previous_generated_cache_backup'] = str(saved)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        assert destination.stat().st_size == row['expected_bytes'] and digest(destination) == row['expected_sha256']
        item['status'] = 'restored_exact'
    results.append(item)
    if len(results) % 50 == 0:
        print('Checked', len(results), 'of', len(targets), flush=True)
counts = {status: sum(r['status'] == status for r in results) for status in sorted({r['status'] for r in results})}
summary = {'backup': str(BACKUP), 'destination': str(ROOT), 'target_count': len(targets), 'counts': counts, 'backup_modified': False, 'backup_manifest_matches_original': digest(BACKUP / 'TRANSFER_MANIFEST.jsonl') == digest(ROOT / 'TRANSFER_MANIFEST.jsonl')}
(OUT / 'recovery-files.json').write_text(json.dumps(results, indent=2), encoding='utf-8')
(OUT / 'recovery-summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
print(json.dumps(summary, indent=2), flush=True)

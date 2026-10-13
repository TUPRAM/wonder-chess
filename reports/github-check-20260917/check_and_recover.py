import hashlib
import json
from pathlib import Path
import urllib.request
import urllib.parse

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
REV = '123647ae220efc4b34e34baa13f8ac0dea87eb17'
BASE = 'https://raw.githubusercontent.com/TUPRAM/wonder-chess/' + REV + '/'

def get(url):
    request = urllib.request.Request(url, headers={'User-Agent': 'WonderChess-transfer-verification'})
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read()

manifest = {r['path']: r for r in map(json.loads, (ROOT / 'TRANSFER_MANIFEST.jsonl').read_text().splitlines()) if 'path' in r}
previous = json.loads((ROOT / 'reports/backup-recovery-20260917/recovery-files.json').read_text())
results = []
for previous_row in previous:
    if previous_row['status'] == 'restored_exact':
        continue
    rel = previous_row['path']
    expected = manifest[rel]
    target = (ROOT / rel).resolve()
    assert target.is_relative_to(ROOT)
    url = BASE + urllib.parse.quote(rel)
    item = {'path': rel, 'source_url': url, 'expected_sha256': expected['sha256']}
    try:
        body = get(url)
        item['actual_bytes'] = len(body)
        item['actual_sha256'] = hashlib.sha256(body).hexdigest()
        if len(body) != expected['bytes'] or item['actual_sha256'] != expected['sha256']:
            item['status'] = 'remote_mismatch_not_copied'
        elif target.exists():
            item['status'] = 'already_exact' if hashlib.sha256(target.read_bytes()).hexdigest() == expected['sha256'] else 'existing_file_preserved'
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open('xb') as output:
                output.write(body)
            assert hashlib.sha256(target.read_bytes()).hexdigest() == expected['sha256']
            item['status'] = 'restored_exact'
    except Exception as exc:
        item['status'] = 'error'
        item['error'] = str(exc)
    results.append(item)
    print(item['status'], rel, flush=True)
    (OUT / 'archive-recovery.json').write_text(json.dumps(results, indent=2), encoding='utf-8')

for rel in ['TRANSFER_TO_NEW_PC.md', 'reports/repository-sync/20260915/PUBLISHING_REPORT.md']:
    (OUT / ('github-' + Path(rel).name)).write_bytes(get(BASE + rel))
comparison = json.loads(get('https://api.github.com/repos/TUPRAM/wonder-chess/compare/d80635f615810a93c3161c6bfd6c34c758b08260...' + REV))
summary = {'remote_revision': REV, 'local_head': 'd80635f615810a93c3161c6bfd6c34c758b08260', 'compare_status': comparison['status'], 'remote_ahead_by': comparison['ahead_by'], 'remote_behind_by': comparison['behind_by'], 'commits': [{'sha': c['sha'], 'message': c['commit']['message']} for c in comparison['commits']], 'archive_counts': {status: sum(r['status'] == status for r in results) for status in sorted({r['status'] for r in results})}, 'scope': 'Read repository publication and guide; restore only exact previously missing archives under existing recovery authorization. No pull, merge, reset, or branch change.'}
(OUT / 'summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
print(json.dumps(summary, indent=2), flush=True)

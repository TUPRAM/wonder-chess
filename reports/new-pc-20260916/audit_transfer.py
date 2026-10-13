import collections, hashlib, json, pathlib, time

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = pathlib.Path(__file__).resolve().parent
counts = collections.Counter()
groups = collections.defaultdict(collections.Counter)
rows_hash = hashlib.sha256()
total_bytes = 0
footer = None
start = time.time()
with (ROOT / 'TRANSFER_MANIFEST.jsonl').open('rb') as source, (OUT / 'transfer-issues.jsonl').open('w', encoding='utf-8') as issues:
    for line in source:
        row = json.loads(line)
        if row.get('type') == 'complete':
            footer = row
            continue
        rows_hash.update(line)
        counts['manifest_files'] += 1
        total_bytes += row['bytes']
        rel = pathlib.PurePosixPath(row['path'])
        target = ROOT.joinpath(*rel.parts)
        status = 'matched'
        detail = None
        try:
            if not target.is_file():
                status = 'missing'
            elif target.stat().st_size != row['bytes']:
                status = 'size_mismatch'
            else:
                h = hashlib.sha256()
                with target.open('rb') as payload:
                    for block in iter(lambda: payload.read(8 * 1024 * 1024), b''):
                        h.update(block)
                if h.hexdigest() != row['sha256']:
                    status = 'hash_mismatch'
        except OSError as exc:
            status, detail = 'read_error', str(exc)
        counts[status] += 1
        groups[rel.parts[0]][status] += 1
        if status != 'matched':
            issues.write(json.dumps({'path': row['path'], 'status': status, 'detail': detail}) + '\n')
        if counts['manifest_files'] % 5000 == 0:
            print(dict(counts), flush=True)
result = {'counts': dict(counts), 'groups': {k: dict(v) for k,v in groups.items()}, 'manifest_complete': bool(footer and footer['files'] == counts['manifest_files'] and footer['bytes'] == total_bytes and footer['rows_sha256'] == rows_hash.hexdigest()), 'elapsed_seconds': time.time()-start, 'root': str(ROOT)}
(OUT / 'transfer-summary.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
print(json.dumps(result, indent=2), flush=True)

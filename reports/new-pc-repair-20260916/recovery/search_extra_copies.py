import collections
import hashlib
import json
import os
import pathlib
import time
import zipfile

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent
missing = {r['path']:r for r in json.loads((OUT/'unresolved.json').read_text()) if not (ROOT/r['path']).exists()}
identity = collections.defaultdict(list)
for p,r in missing.items(): identity[(r['bytes'],r['sha256'])].append(p)
sizes = {r['bytes'] for r in missing.values()}
start = time.time()
examined = archives = restored = 0
errors = []

def match(data, source):
    global restored
    key = (len(data), hashlib.sha256(data).hexdigest())
    for rel in identity.get(key, []):
        target = ROOT/rel
        if target.exists(): continue
        assert target.resolve().is_relative_to(ROOT)
        assert rel.startswith(('tools/', 'tests/', 'support/', '.git/refs/codex/turn-diffs/captures/'))
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open('xb') as f: f.write(data)
        assert hashlib.sha256(target.read_bytes()).hexdigest() == key[1]
        record = {'path':rel, 'bytes':key[0], 'sha256':key[1], 'source':source, 'verified_after_write':True}
        with (OUT/'restored.jsonl').open('a', encoding='utf-8') as f: f.write(json.dumps(record, ensure_ascii=False)+'\n')
        restored += 1
        missing.pop(rel)

for scope in [ROOT, pathlib.Path('C:/Users/USER/Downloads'), pathlib.Path('C:/Users/USER/Desktop')]:
    for directory, children, filenames in os.walk(scope):
        children[:] = [x for x in children if x not in {'.git', '.venv', '.venv-mcp', 'node_modules'}]
        for filename in filenames:
            p = pathlib.Path(directory)/filename
            try:
                size = p.stat().st_size
                if size in sizes:
                    match(p.read_bytes(), {'kind':'local_file_size_scan', 'path':str(p)})
                    examined += 1
                if p.suffix.lower() == '.zip':
                    with zipfile.ZipFile(p) as z:
                        for item in z.infolist():
                            if item.file_size in sizes and not item.is_dir():
                                match(z.read(item), {'kind':'local_zip_entry', 'path':str(p), 'entry':item.filename})
                    archives += 1
            except (OSError, zipfile.BadZipFile) as e:
                errors.append({'path':str(p), 'error':str(e)})
result = {'stage':'extra_local_copies_complete', 'restored_this_phase':restored, 'remaining':len(missing),
    'files_hashed':examined, 'zip_archives_scanned':archives, 'remaining_groups':dict(collections.Counter(p.split('/')[0] for p in missing)),
    'elapsed_seconds':time.time()-start, 'errors':errors}
(OUT/'extra-copy-scan.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
(OUT/'unresolved.json').write_text(json.dumps(list(missing.values()), indent=2), encoding='utf-8')
print(json.dumps(result), flush=True)

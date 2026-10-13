"""Restore absent transferred payloads only when bytes match the frozen manifest.

No tracked content is replaced and no Git objects, index or existing refs change.
"""
import collections
import hashlib
import json
import pathlib
import subprocess
import time

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent
ORIGINAL = json.loads((ROOT/'reports/new-pc-20260916/missing-inventory.json').read_text())['paths']
MANIFEST = {}
for line in (ROOT/'TRANSFER_MANIFEST.jsonl').read_text(encoding='utf-8').splitlines():
    row = json.loads(line)
    if 'path' in row:
        MANIFEST[row['path']] = row
WANTED = {p: MANIFEST[p] for p in ORIGINAL if not (ROOT/p).exists()}
by_identity = collections.defaultdict(list)
for path, row in WANTED.items():
    by_identity[(row['bytes'], row['sha256'])].append(path)
evidence = []
start = time.time()

def digest(data):
    return hashlib.sha256(data).hexdigest()

def save_matching(data, source):
    identity = (len(data), digest(data))
    for relative in by_identity.get(identity, []):
        target = ROOT/relative
        if target.exists():
            continue
        assert target.resolve().is_relative_to(ROOT)
        assert relative.startswith(('tools/', 'tests/', 'support/', '.git/refs/codex/turn-diffs/captures/'))
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open('xb') as output:
            output.write(data)
        written = target.read_bytes()
        assert (len(written), digest(written)) == identity
        record = {'path': relative, 'bytes': identity[0], 'sha256': identity[1], 'source': source,
                  'verified_after_write': True}
        evidence.append(record)
        with (OUT/'restored.jsonl').open('a', encoding='utf-8') as log:
            log.write(json.dumps(record, ensure_ascii=False)+'\n')
        del WANTED[relative]

def summary(stage):
    result = {'stage': stage, 'restored_this_run': len(evidence), 'remaining': len(WANTED),
              'remaining_groups': dict(collections.Counter(p.split('/')[0] for p in WANTED)),
              'elapsed_seconds': time.time()-start}
    (OUT/'progress.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    (OUT/'unresolved.json').write_text(json.dumps(list(WANTED.values()), indent=2), encoding='utf-8')
    print(json.dumps(result), flush=True)

summary('start')
for relative, row in MANIFEST.items():
    if (row['bytes'], row['sha256']) not in by_identity:
        continue
    path = ROOT/relative
    if path.is_file() and path.stat().st_size == row['bytes']:
        data = path.read_bytes()
        if digest(data) == row['sha256']:
            save_matching(data, {'kind': 'manifest_identical_local_copy', 'path': relative})
summary('manifest_copies_complete')

objects = subprocess.check_output(['git', 'cat-file', '--batch-all-objects', '--batch-check=%(objectname) %(objecttype) %(objectsize)'], cwd=ROOT).decode().splitlines()
needed_sizes = {row['bytes'] for row in WANTED.values()}
batch = subprocess.Popen(['git', 'cat-file', '--batch'], cwd=ROOT, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
examined = 0
for line in objects:
    oid, kind, size_text = line.split()
    if kind == 'commit':
        for suffix in (b'\n', b'\r\n', b''):
            save_matching(oid.encode()+suffix, {'kind': 'git_existing_commit_ref_bytes', 'object': oid})
    size = int(size_text)
    if kind != 'blob' or (size > 2*1024*1024 and size not in needed_sizes):
        continue
    batch.stdin.write(oid.encode()+b'\n')
    batch.stdin.flush()
    header = batch.stdout.readline().split()
    data = batch.stdout.read(int(header[2]))
    assert batch.stdout.read(1) == b'\n'
    save_matching(data, {'kind': 'git_blob', 'object': oid, 'transform': 'none'})
    if b'\x00' not in data and b'\n' in data:
        lf = data.replace(b'\r\n', b'\n')
        save_matching(lf, {'kind': 'git_blob', 'object': oid, 'transform': 'CRLF_to_LF'})
        save_matching(lf.replace(b'\n', b'\r\n'), {'kind': 'git_blob', 'object': oid, 'transform': 'LF_to_CRLF'})
    examined += 1
    if examined % 2000 == 0:
        summary(f'git_blobs_{examined}')
batch.stdin.close()
batch.wait()
summary('git_blobs_complete')

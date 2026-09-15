import collections
import json
from pathlib import Path
import re
import subprocess

root = Path(r'C:\Users\iputu\Documents\Wonder Chess')
out = Path(__file__).parent
patterns = {
    'private_key': re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----'),
    'github_token': re.compile(rb'\b(?:gh[pousr]_[A-Za-z0-9]{30,255}|github_pat_[A-Za-z0-9_]{40,255})\b'),
    'openai_key': re.compile(rb'\bsk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{32,255}\b'),
    'aws_access': re.compile(rb'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b'),
    'slack_token': re.compile(rb'\bxox[baprs]-[A-Za-z0-9-]{20,255}\b'),
    'credential_url': re.compile(rb'https?://[^\s/<>"\x27]{1,80}:[^\s/<>"\x27]{4,100}@'),
    'assigned_secret': re.compile(rb'(?i)["\x27]?(?:api[_-]?key|access[_-]?token|auth[_-]?token|client[_-]?secret|password)["\x27]?\s*[:=]\s*["\x27]([^"\x27\r\n]{12,200})["\x27]'),
}
hits = []
checked = 0
def scan(data, name):
    global checked
    if b'\0' in data[:8192]:
        return
    checked += 1
    for kind, pattern in patterns.items():
        for match in pattern.finditer(data):
            hits.append({'path': name, 'kind': kind, 'line': data.count(b'\n', 0, match.start()) + 1})

raw = subprocess.check_output(['git', 'ls-files', '--cached', '--others', '--exclude-standard', '-z'], cwd=root)
paths = sorted(set(raw.decode().strip('\0').split('\0')))
rows = []
text_ext = {'.py','.ps1','.cmd','.json','.jsonl','.csv','.log','.txt','.md','.h','.cpp','.ini','.cs','.uproject','.html','.mjs','.toml','.yml','.yaml','.xml','.bat','.sh','.fixture'}
for name in paths:
    path = root / name
    if not path.is_file():
        continue
    size = path.stat().st_size
    rows.append({'path': name, 'bytes': size})
    if path.suffix.lower() in text_ext or name.startswith('.') or path.suffix == '':
        scan(path.read_bytes(), name)

objects = subprocess.check_output(['git','rev-list','--objects','HEAD'], cwd=root)
p = subprocess.Popen(['git','cat-file','--batch'], cwd=root, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
history_blobs = 0
history_large = []
for entry in objects.splitlines():
    oid, _, name = entry.partition(b' ')
    p.stdin.write(oid + b'\n'); p.stdin.flush()
    header = p.stdout.readline().split()
    size = int(header[2]); content = p.stdout.read(size); p.stdout.read(1)
    if header[1] == b'blob':
        history_blobs += 1
        if size > 100 * 1024 * 1024:
            history_large.append({'oid':oid.decode(),'bytes':size,'path':name.decode(errors='replace')})
        scan(content, 'history:' + oid.decode() + ':' + name.decode(errors='replace'))
p.stdin.close(); p.wait()
report = {'candidate_files': len(rows), 'candidate_bytes': sum(r['bytes'] for r in rows), 'text_inputs_scanned': checked,
          'history_blobs_checked': history_blobs, 'over_100_mib': [r for r in rows if r['bytes'] > 100 * 1024 * 1024],
          'history_over_100_mib': history_large, 'secret_pattern_findings': hits,
          'scope': 'Pattern scan of candidate text and all reachable HEAD blobs; not a guarantee that no sensitive content exists.'}
(out / 'eligible-files.json').write_text(json.dumps(rows, indent=2))
(out / 'audit.json').write_text(json.dumps(report, indent=2))
print(json.dumps(report, indent=2))

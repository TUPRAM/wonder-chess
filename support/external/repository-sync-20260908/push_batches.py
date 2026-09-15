"""Upload the reviewed current checkout in bounded, ordinary fast-forward pushes."""
import json
from pathlib import Path
import subprocess
from datetime import datetime, timezone

root = Path(r'C:\Users\iputu\Documents\Wonder Chess')
ops = Path(__file__).parent
def git(*args, **kwargs):
    return subprocess.check_output(['git', *args], cwd=root, **kwargs)

assert git('branch', '--show-current').decode().strip() == 'main'
assert git('remote', 'get-url', 'origin').decode().strip() == 'https://github.com/TUPRAM/wonder-chess.git'
audit = json.loads((ops / 'audit.json').read_text())
assert not audit['over_100_mib'] and not audit['history_over_100_mib']
assert not audit['secret_pattern_findings'], 'Review findings before uploading'
rows = json.loads((ops / 'eligible-files.json').read_text())
core = [r['path'] for r in rows if not r['path'].startswith('reports/')]
core += ['reports/implementation_state.json']
evidence = [r for r in rows if r['path'].startswith('reports/') and r['path'] != 'reports/implementation_state.json']
batches = [('Publish Wonder Chess source assets, Unreal project and Blender MCP setup', core)]
bucket = []; size = 0
for row in evidence:
    if bucket and size + row['bytes'] > 512 * 1024 * 1024:
        batches.append((f'Preserve Wonder Chess research and execution evidence batch {len(batches):02d}', bucket))
        bucket = []; size = 0
    bucket.append(row['path']); size += row['bytes']
if bucket:
    batches.append((f'Preserve Wonder Chess research and execution evidence batch {len(batches):02d}', bucket))
(ops / 'batches.json').write_text(json.dumps([{'message':m,'files':fs} for m,fs in batches],indent=2))
for i, (message, files) in enumerate(batches):
    print(f'BATCH {i + 1}/{len(batches)}: staging {len(files)} paths', flush=True)
    spec = ops / f'batch-{i:02d}.paths'
    spec.write_bytes(b'\0'.join(f.encode('utf-8') for f in files) + b'\0')
    with (ops / f'batch-{i:02d}.log').open('ab') as log:
        subprocess.run(['git','add','--pathspec-from-file='+str(spec),'--pathspec-file-nul'], cwd=root, stdout=log, stderr=log, check=True)
        changed = subprocess.run(['git','diff','--cached','--quiet'],cwd=root).returncode
        if changed == 1:
            subprocess.run(['git','commit','-m',message],cwd=root,stdout=log,stderr=log,check=True)
        elif changed != 0:
            raise RuntimeError('Could not check index')
        head = git('rev-parse','HEAD').decode().strip()
        print(f'BATCH {i + 1}/{len(batches)}: pushing {head[:12]}',flush=True)
        subprocess.run(['git','-c','pack.threads=4','push','--set-upstream','origin','main'],cwd=root,stdout=log,stderr=log,check=True)
    remote = git('ls-remote','origin','refs/heads/main').decode().split()[0]
    if remote != head:
        raise RuntimeError(f'Remote advanced unexpectedly: {remote}')
    with (ops / 'pushed.jsonl').open('a') as f:
        f.write(json.dumps({'batch':i+1,'head':head,'paths':len(files),'utc':datetime.now(timezone.utc).isoformat()})+'\n')
    print(f'BATCH {i + 1}/{len(batches)} VERIFIED on GitHub',flush=True)
print('ALL BATCHES PUSHED',flush=True)

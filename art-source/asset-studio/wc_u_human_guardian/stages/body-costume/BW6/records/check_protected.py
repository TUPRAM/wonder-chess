import hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parent
before=json.loads((R/'protected_before.json').read_text())
rows=[]
for name,expected in before.items():
 p=Path(name);h=hashlib.sha256()
 if p.exists():
  with p.open('rb') as f:
   for chunk in iter(lambda:f.read(8*1024*1024),b''):h.update(chunk)
  actual=h.hexdigest()
 else:actual=None
 rows.append({'path':name,'before':expected,'after':actual,'matches':actual==expected})
out={'checked':len(rows),'matching':sum(r['matches'] for r in rows),'failures':[r for r in rows if not r['matches']],'files':rows}
(R/'protected_after.json').write_text(json.dumps(out,indent=2))
print(json.dumps({k:v for k,v in out.items() if k!='files'}))
assert not out['failures']

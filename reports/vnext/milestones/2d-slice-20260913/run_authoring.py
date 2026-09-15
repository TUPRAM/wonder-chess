import hashlib,json,subprocess,time,sys
from pathlib import Path
root=Path(__file__).resolve().parents[4]
evidence=root/'reports/vnext/milestones/2d-slice-20260913'
checks=[
 ['python','-m','unittest','discover','-s','tests','-v'],
 ['python','tools/build_documents.py','--check'],
 ['python','tools/compile_catalog.py','--check'],
 ['python','tools/vnext/catalog.py','--check'],
]
rows=[]
for i,cmd in enumerate(checks):
 cmd[0]=sys.executable
 started=time.monotonic()
 p=subprocess.run(cmd,cwd=root,capture_output=True,text=True,encoding='utf-8',errors='replace')
 log=evidence/f'authoring-r2-{i}.log'
 log.write_text(p.stdout+p.stderr,encoding='utf-8')
 rows.append(dict(command=cmd,exit_code=p.returncode,seconds=time.monotonic()-started,log=log.name))
 print(json.dumps(rows[-1]),flush=True)
(evidence/'authoring-checks-r2.json').write_text(json.dumps(rows,indent=2))
raise SystemExit(any(x['exit_code'] for x in rows))

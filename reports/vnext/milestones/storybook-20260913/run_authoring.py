import json, subprocess, time, sys
from pathlib import Path
root=Path(__file__).resolve().parents[4]
evidence=Path(__file__).resolve().parent
checks=[
 [sys.executable,"tools/validate_kit.py"],
 [sys.executable,"-m","unittest","discover","-s","tests","-v"],
 [sys.executable,"tools/build_documents.py","--check"],
 [sys.executable,"tools/compile_catalog.py","--check"],
 [sys.executable,"tools/vnext/catalog.py","--check"],
]
rows=[]
for i,cmd in enumerate(checks):
 start=time.monotonic()
 p=subprocess.run(cmd,cwd=root,capture_output=True,text=True,encoding="utf-8",errors="replace")
 log=evidence/f"authoring-{i}.log"
 log.write_text(p.stdout+p.stderr,encoding="utf-8")
 rows.append(dict(command=cmd,exit_code=p.returncode,seconds=time.monotonic()-start,log=log.name))
 print(json.dumps(rows[-1]),flush=True)
(evidence/"authoring-checks.json").write_text(json.dumps(rows,indent=2))
raise SystemExit(any(x["exit_code"] for x in rows))

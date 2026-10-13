import collections, hashlib, json, pathlib, subprocess
ROOT=pathlib.Path(__file__).resolve().parents[3]
OUT=pathlib.Path(__file__).resolve().parent
missing={r['path']:r for r in json.loads((OUT/'unresolved.json').read_text()) if r['path'].startswith(('tools/','tests/')) and '__pycache__' not in r['path']}
found=collections.defaultdict(list)
for line in subprocess.check_output(['git','rev-list','--objects','--all'],cwd=ROOT).decode().splitlines():
    oid, _, path=line.partition(' ')
    if path not in missing: continue
    data=subprocess.check_output(['git','cat-file','blob',oid],cwd=ROOT)
    lf=data.replace(b'\r\n',b'\n')
    dest=OUT/'git-source-candidates'/oid
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_bytes(data)
    row={'object':oid,'bytes':len(data),'lines':data.count(b'\n'),'lf_bytes':len(lf),'crlf_bytes':len(lf)+lf.count(b'\n'),'expected_bytes':missing[path]['bytes'],'expected_sha256':missing[path]['sha256']}
    found[path].append(row)
for path in missing: found[path]
(OUT/'source-version-candidates.json').write_text(json.dumps(found,indent=2),encoding='utf-8')
print(json.dumps(found,indent=2))

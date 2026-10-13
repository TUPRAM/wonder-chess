import collections,json,pathlib,subprocess
ROOT=pathlib.Path(__file__).resolve().parents[3]; OUT=pathlib.Path(__file__).resolve().parent
missing={r['path']:r for r in json.loads((OUT/'unresolved.json').read_text()) if r['path'].startswith(('tools/','tests/')) and '__pycache__' not in r['path']}
names={pathlib.PurePosixPath(p).name:p for p in missing}
found=collections.defaultdict(set)
batch=subprocess.Popen(['git','cat-file','--batch'],cwd=ROOT,stdin=subprocess.PIPE,stdout=subprocess.PIPE)
def blob(oid):
    batch.stdin.write(oid.encode()+b'\n');batch.stdin.flush();h=batch.stdout.readline().split();b=batch.stdout.read(int(h[2]));assert batch.stdout.read(1)==b'\n';return b
for line in (OUT/'git-objects.txt').read_text().splitlines():
    oid,kind,size=line.split()
    if kind!='tree':continue
    data=blob(oid); i=0
    while i<len(data):
        null=data.index(0,i);meta=data[i:null];child=data[null+1:null+21].hex();i=null+21
        name=meta.partition(b' ')[2].decode(errors='replace')
        if name in names:found[names[name]].add(child)
result={}
for p,oids in found.items():
    result[p]=[]
    for oid in oids:
        data=blob(oid);lf=data.replace(b'\r\n',b'\n')
        dest=OUT/'git-source-candidates'/oid;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
        result[p].append({'object':oid,'bytes':len(data),'lf_bytes':len(lf),'crlf_bytes':len(lf)+lf.count(b'\n'),'expected_bytes':missing[p]['bytes']})
batch.stdin.close();batch.wait()
for p in missing:result.setdefault(p,[])
(OUT/'unreachable-source-versions.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))

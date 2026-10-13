"""Search exact original newline representations; accept only manifest hash matches."""
import collections, hashlib, json, pathlib, subprocess, time
ROOT=pathlib.Path(__file__).resolve().parents[3]
OUT=pathlib.Path(__file__).resolve().parent
original=json.loads((OUT/'unresolved.json').read_text())
wanted={r['path']:r for r in original if (r['path'].startswith(('tools/','tests/')) and '__pycache__' not in r['path']) or r['path'].startswith('.git/')}
identity={(r['bytes'],r['sha256']):p for p,r in wanted.items()}
examined=attempts=restored=0
start=time.time()

def match(data, source):
    global restored, attempts
    attempts += 1
    key=(len(data),hashlib.sha256(data).hexdigest())
    rel=identity.get(key)
    if not rel or (ROOT/rel).exists(): return
    target=ROOT/rel
    target.parent.mkdir(parents=True,exist_ok=True)
    with target.open('xb') as f:f.write(data)
    assert hashlib.sha256(target.read_bytes()).hexdigest()==key[1]
    with (OUT/'restored.jsonl').open('a',encoding='utf-8') as f:
        f.write(json.dumps({'path':rel,'bytes':key[0],'sha256':key[1],'source':source,'verified_after_write':True})+'\n')
    restored+=1
    print('RECOVERED '+rel, flush=True)

objects=subprocess.check_output(['git','cat-file','--batch-all-objects','--batch-check=%(objectname) %(objecttype) %(objectsize)'],cwd=ROOT).decode().splitlines()
(OUT/'git-objects.txt').write_text('\n'.join(objects)+'\n')
batch=subprocess.Popen(['git','cat-file','--batch'],cwd=ROOT,stdin=subprocess.PIPE,stdout=subprocess.PIPE)
seen=set()
for line in objects:
    oid,kind,size_text=line.split()
    for suffix in (b'\n',b'\r\n',b''):
        match(oid.encode()+suffix,{'kind':'git_existing_object_ref_bytes','object':oid,'object_type':kind})
    if kind!='blob' or int(size_text)>max(r['bytes'] for r in wanted.values()):continue
    batch.stdin.write(oid.encode()+b'\n'); batch.stdin.flush()
    header=batch.stdout.readline().split()
    raw=batch.stdout.read(int(header[2])); assert batch.stdout.read(1)==b'\n'
    if b'\x00' in raw:continue
    normalized=raw.replace(b'\r\n',b'\n')
    dh=hashlib.sha256(normalized).digest()
    if dh in seen:continue
    seen.add(dh)
    examined+=1
    for bom in (b'',b'\xef\xbb\xbf'):
        for ending in (None,b'\n',b''):
            lf=normalized if ending is None else normalized.rstrip(b'\r\n')+ending
            pieces=lf.splitlines(keepends=True)
            n=sum(p.endswith(b'\n') for p in pieces)
            applicable=[r for p,r in wanted.items() if not (ROOT/p).exists() and len(bom)+len(lf)<=r['bytes']<=len(bom)+len(lf)+n]
            if not applicable:continue
            for target in applicable:
                count=target['bytes']-len(bom)-len(lf)
                # A single consecutive run of CRLFs, or a single run of LFs.
                for invert,block_length in [(False,count),(True,n-count)]:
                    for first in range(n-block_length+1):
                        data=bom+b''.join(p.replace(b'\n',b'\r\n') if ((first<=i<first+block_length) != invert) else p for i,p in enumerate(pieces))
                        match(data,{'kind':'git_blob_newline_reconstruction','object':oid,'bom':bool(bom),'ending':str(ending),'crlf_outside_block':invert,'block_first':first,'block_length':block_length})
    if examined%5000==0:print(json.dumps({'blobs':examined,'attempts':attempts,'restored':restored}),flush=True)
batch.stdin.close();batch.wait()
remaining=[r for r in original if not (ROOT/r['path']).exists()]
(OUT/'unresolved.json').write_text(json.dumps(remaining,indent=2),encoding='utf-8')
result={'restored':restored,'normalized_blobs_examined':examined,'representations_hashed':attempts,'remaining':len(remaining),'elapsed_seconds':time.time()-start}
(OUT/'mixed-newline-scan.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result),flush=True)

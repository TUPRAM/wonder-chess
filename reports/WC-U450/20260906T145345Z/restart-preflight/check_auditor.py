from pathlib import Path
import sys,json,hashlib,subprocess
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path('tests/runtime').resolve()))
from audit_packaged_restart import describe_match,payload_checks
root=Path('reports/WC-U450/20260906T145345Z/restart-preflight')
p=root/'auditor-fixture';p.mkdir();f=p/'payload.pak';f.write_bytes(b'actual fixture bytes')
item={'group':'packaged_payload','path':str(f.resolve()),'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()}
manifest={'package_root':str(p.resolve()),'files':[item],'input_files_stable_during_capture':True}
launch={'payload_verification':{'status':'PASS','file_count':1,'files':[item]}}
checks=[]
def test(name,value):assert value,name;checks.append(name)
test('valid complete payload and retained preflight pass',all(c['status']=='PASS' for c in payload_checks(manifest,launch)))
test('legacy launch with no preflight cannot claim payload binding',any(c['status']=='FAIL' for c in payload_checks(manifest,{})))
f.write_bytes(b'changed fixture data')
test('modified packaged bytes fail audit',any(c['status']=='FAIL' for c in payload_checks(manifest,launch)))
f.write_bytes(b'actual fixture bytes');(p/'extra.pak').write_bytes(b'extra')
test('added unmanifested package file fails audit',any(c['status']=='FAIL' for c in payload_checks(manifest,launch)))
s={'namespace':3,'actual_authority_seed':161803,'rounds':20,'elimination_round':15,'human_place':8,'accepted_replies':24,'deliberate_rejected_replies':6,'passed_probes':6,'probes':8,'results_utc':'fixture'}
text=describe_match(s);test('failed probes described as6of8 not universal success','6/8 probes passed' in text and 'all' not in text)
s['passed_probes']=8;test('complete probes described precisely','8/8 probes passed' in describe_match(s))
result={'status':'PASS','checks':len(checks),'cases':checks,'boundary':'Synthetic auditor tests; no packaged game launched'}
(root/'auditor-focused-checks.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
process=subprocess.run([sys.executable,'-B','-m','unittest','discover','-s','tests/runtime','-p','test_session_transition_audit.py','-v'],capture_output=True,text=True)
(root/'transition-checks.log').write_text(process.stdout+process.stderr)
assert process.returncode==0,process.stderr
print(process.stderr)

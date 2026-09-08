"""Synthetic analyzer fixtures only; no machines, connections or game execution."""
import copy
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'tests/runtime'))
import audit_shipping_network as module

base=Path(__file__).parent/'synthetic-physical-exports'
base.mkdir()
provenance={'package_root':'D:\\Original\\Windows','configuration':'Shipping','package_report':{'exit_code':0},
            'input_files_stable_during_capture':True,'catalog_digest':'f'*64,'files':[{'group':'packaged_payload',
            'path':'D:\\Original\\Windows\\WonderChess.exe','sha256':'a'*64,'bytes':32}]}
manifest=base/'provenance.json'
manifest.write_text(json.dumps(provenance))
manifest_hash=hashlib.sha256(manifest.read_bytes()).hexdigest()
launches=[];sessions=[]
probes=['out_of_order_sequence_rejected','original_idempotent_lock_request','duplicate_request_applies_once',
        'changed_payload_same_request_rejected','stale_revision_rejected','foreign_unit_sale_rejected','combat_phase_buy_rejected']
for seat,role in enumerate(('host','client')):
    directory=base/role;directory.mkdir()
    public={'phase':1,'round':1,'matchNamespace':1,'schemaVersion':'3.1.0','protocolVersion':5,'contentDigest':'f'*64,
            'seats':[{'id':i,'human':i<2,'health':30,'wins':0,'place':0} for i in range(8)],
            'pairs':[{'a':0,'b':1,'ghost':False}], 'encounters':[{'a':0,'b':1,'ghost':False,'tick':10,'units':[]}],
            'recap':{'round':1}}
    session={'match_namespace':1,'process_id':500,'seat':seat,'network_mode':2+seat,'authority_process':seat==0,
             'received_state_privacy_violations':[],'round':1,'command_probes':[{'name':name,'status':'PASS'} for name in probes],
             'extended_authority_checks':True,'actual_accepted_replies':3,'actual_rejected_replies':2,'complete':True,
             'aborted':False,'public_snapshot':json.dumps(public)}
    sessions.append(session)
    (directory/f'match-1-seat-{seat}-pid-500-session.json').write_text(json.dumps(session))
    (directory/f'match-1-seat-{seat}-pid-500-snapshots.jsonl').write_text(json.dumps({'public':public,'owner_private':{'seat':seat,'revision':1<<32}})+'\n')
    current=f'C:\\Copied{seat}\\Windows'
    mapping={'relative_path':'WonderChess.exe','original_path':provenance['files'][0]['path'],'current_path':current+'\\WonderChess.exe','expected_sha256':'a'*64,'expected_bytes':32}
    relocation={'status':'PASS','original_package_root':provenance['package_root'],'current_package_root':current,'mapping':[mapping],
                'payload':{'status':'PASS','file_count':1,'files':[{'path':mapping['current_path'],'sha256':'a'*64,'bytes':32}]}}
    launch={'role':role,'hardware':{'hostname':f'PHYSICAL_FIXTURE_PC_{seat}','smbios_uuid_sha256':str(seat)*64},
            'local_ipv4':[{'IPAddress':f'192.168.1.{20+seat}'}],'host_address':'192.168.1.20','port':7780,
            'process_id':500,'status':'EXITED_AUDIT_REQUIRED','exit_code':0,'provenance_sha256':manifest_hash,'catalog_digest':'f'*64,
            'relocated_payload_verification':relocation,'post_run_relocated_payload_verification':copy.deepcopy(relocation),
            'listen_owner':[{'OwningProcess':500,'LocalPort':7780}] if seat==0 else None,
            'arguments':['-WCHost','-Port=7780'] if seat==0 else ['-WCJoin=192.168.1.20:7780']}
    launches.append(launch)
    (directory/'physical-launch.json').write_text(json.dumps(launch))

def check(rows):
    return module.physical_identity_checks(rows,sessions,provenance,manifest_hash)

checks=[]
valid=check(launches)
assert all(row['status']=='PASS' for row in valid),valid
checks.append('same numeric PID on different bound hostnames is valid')
mutations=[('same_hostname',lambda x:x[1]['hardware'].update(hostname=x[0]['hardware']['hostname'])),
           ('same_uuid',lambda x:x[1]['hardware'].update(smbios_uuid_sha256=x[0]['hardware']['smbios_uuid_sha256'])),
           ('loopback',lambda x:[row.update(host_address='127.0.0.1') for row in x]),
           ('wrong_manifest',lambda x:x[1].update(provenance_sha256='0'*64)),
           ('wrong_process',lambda x:x[1].update(process_id=501)),
           ('wrong_route',lambda x:x[1].update(arguments=['-WCJoin=127.0.0.1:7780'])),
           ('wrong_payload',lambda x:x[1]['relocated_payload_verification']['mapping'][0].update(expected_sha256='0'*64)),
           ('missing_postflight',lambda x:x[1].pop('post_run_relocated_payload_verification')),
           ('same_machine_target',lambda x:x[1].update(local_ipv4=[{'IPAddress':'192.168.1.20'}]))]
for name,mutate in mutations:
    variant=copy.deepcopy(launches);mutate(variant)
    assert any(row['status']=='FAIL' for row in check(variant)),name
    checks.append(name+' rejected')
result=module.audit_physical(base,manifest)
assert result['status']=='PASS',result
report=json.loads((base/'physical-audit/physical-network-analysis.json').read_text())
assert report['raw_same_host_paired_reader']['status']=='FAIL'
assert {row['check'] for row in report['raw_same_host_paired_reader']['checks'] if row['status']=='FAIL'}=={'distinct_processes'}
assert report['physical_device_observation']=='NOT_RUN_BY_ANALYZER'
checks.append('full physical branch preserves raw PID failure and evaluates machine plus PID without changing exports')
assert json.loads((base/'host/match-1-seat-0-pid-500-session.json').read_text())['process_id']==500
assert json.loads((base/'client/match-1-seat-1-pid-500-session.json').read_text())['process_id']==500
checks.append('original identical PIDs remain unchanged')
record={'status':'PASS','checks':len(checks),'results':checks,'evidence_kind':'SYNTHETIC_ANALYZER_FIXTURES_ONLY',
        'game_launched':False,'connection_attempted':False,'physical_lan_acceptance':'NOT_RUN',
        'auditor_sha256':hashlib.sha256((ROOT/'tests/runtime/audit_shipping_network.py').read_bytes()).hexdigest()}
(base.parent/'physical-auditor-fixtures.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record,indent=2))


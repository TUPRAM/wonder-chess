from pathlib import Path
import importlib.util,json,copy
from unittest.mock import patch
root=Path.cwd(); spec=importlib.util.spec_from_file_location('asset_report',root/'tools/report_update_assets.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
u=m.read(root/'data/units.json')['units'][0];p=root/'reports/WC-U430/20260906T135823Z/ada8-audio-import/import-wc_u_human_guardian.json';container=m.read(p);entry=container['heroes'][0]
checks=[]
def case(name,check):
 assert check,name
 checks.append(name)
r,rows=m.report_asset(u,'hero',[(p,container,entry)]);case('actual matching imported source and exports bind',r['import_report_matches_current_source_export'] and len(rows)==7 and all(x['import_report_matches_current_source_export'] for x in rows))
fake=copy.deepcopy(entry);fake['source_sha256']='0'*64
r,_=m.report_asset(u,'hero',[(p,container,fake)]);case('stale source hash never binds',not r['import_report_matches_current_source_export'] and r['import_reports'][0]['binding']=='STALE_OR_MISMATCH')
fake=copy.deepcopy(entry);fake.pop('source_sha256')
r,_=m.report_asset(u,'hero',[(p,container,fake)]);case('unbound report stays unknown',not r['import_report_matches_current_source_export'] and r['import_reports'][0]['binding']=='UNKNOWN_UNBOUND_REPORT')
fake=copy.deepcopy(entry);fake['clips'][0]['path']='/Game/Wrong/Wrong.Wrong'
_,rows=m.report_asset(u,'hero',[(p,container,fake)]);case('wrong clip object path does not bind',not rows[0]['import_report_matches_current_source_export'])
r,_=m.report_asset(u,'hero',[(p,dict(container,passed=False),entry)]);case('overall failed report cannot bind',not r['import_report_matches_current_source_export'])
missing=next(x for x in m.read(root/'data/units.json')['units'] if x['id']=='wc_u_halfling_warrior')
r,rows=m.report_asset(missing,'hero',[]);case('missing source retained with seven missing clips',not r['source']['present'] and len(rows)==7 and all(x['export_hash_status']=='MISSING' for x in rows))
try:m.scoped(root/'../forbidden')
except ValueError:case('workspace path escape rejected',True)
else:raise AssertionError('escape accepted')
real_sha=m.sha
with patch.object(m,'sha',side_effect=lambda path:'0'*64 if path.name=='AN_wc_u_human_guardian_Idle.fbx' else real_sha(path)):
 r,rows=m.report_asset(u,'hero',[(p,container,entry)]);case('changed clip bytes invalidate export and import binding',r['export_hash_status']=='INCOMPLETE_OR_MISMATCH' and not r['import_report_matches_current_source_export'])
report={'status':'PASS','checks':len(checks),'cases':checks};print(json.dumps(report,indent=2));Path('reports/WC-U450/20260906T144159Z/asset-readiness/utility-checks.json').write_text(json.dumps(report,indent=2)+'\n')

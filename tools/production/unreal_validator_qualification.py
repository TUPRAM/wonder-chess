"""Cold-reopen and real subsystem fault injection, confined to diagnostic assets."""
import json
import sys
from pathlib import Path
import unreal as u

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/production'))
import unreal_asset_validator as v
BASE='/Game/WonderChess/Diagnostics/PipelineTools20260921'
results=[]


def test(name, asset_path, contract, expected_error):
    asset=u.load_asset(asset_path)
    if not asset: raise RuntimeError('Cold reopen failed: '+asset_path)
    observations=v.validate(asset,contract)
    errors=[e for o in observations for e in o['errors']]
    correct=not errors if expected_error is None else any(expected_error in e for e in errors)
    results.append({'name':name,'asset':asset_path,'expected_error':expected_error,
                    'observed_errors':errors,'status':'pass' if correct else 'fail',
                    'actual_subsystem_callback':True})


test('valid_scale',BASE+'/SM_QualificationLow',{'class':'StaticMesh','dimensions_cm':[100,100,100]},None)
test('wrong_scale',BASE+'/SM_QualificationLow',{'dimensions_cm':[1,1,1]},'Wrong scale')
test('missing_clip',BASE+'/SM_QualificationLow',{'required_assets':[BASE+'/A_DeliberatelyMissing']},'Missing dependency')
test('valid_private_skeleton',BASE+'/SK_QualificationEditable',{'required_bones':['qualification_socket_bone']},None)
test('missing_socket',BASE+'/SK_QualificationEditable',{'required_sockets':['deliberately_missing_socket']},'Missing socket')
test('broken_binding',BASE+'/LS_Qualification',{'required_binding_ids':['00000000-0000-0000-0000-000000000001']},'Missing sequence binding')
texture=u.load_asset(BASE+'/T_QualificationNormal')
results.append({'name':'cold_reopen_bake','status':'pass' if texture and texture.blueprint_get_size_x()==256 else 'fail'})
result={'scope':'tool_qualification_not_creature_acceptance','tests':results,
        'status':'pass' if all(x['status']=='pass' for x in results) else 'fail'}
(ROOT/'reports/pipeline-tools-20260921/unreal-validator-tests.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
if result['status']!='pass': raise RuntimeError('Validator fault test failed')

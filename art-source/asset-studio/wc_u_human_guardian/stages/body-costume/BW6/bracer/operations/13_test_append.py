import bpy,json,sys,hashlib,ast
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R));from append_bracers import append_bracers
source=R/'ada_bw6_bracer_checkpoint_r002_REVIEW_CANDIDATE.blend';bpy.ops.wm.read_factory_settings(use_empty=True)
with bpy.data.libraries.load(str(source),link=False) as (available,loaded):loaded.objects=['BW6_Bracer_Independent_Rig']
rig=loaded.objects[0];s=bpy.context.scene;s.collection.objects.link(rig);s.frame_set(1)
p=R/'operations/11_freeze_and_capture.py';t=ast.parse(p.read_text());exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,ast.FunctionDef) and n.name in ['sig','action_sig']],type_ignores=[]),str(p),'exec'),globals())
before=action_sig(rig.animation_data.action);report=append_bracers(rig,s);assert before==action_sig(rig.animation_data.action)
expected={}
for folder in [R,R/'left']:
 rec=json.loads((folder/'records/verification.json').read_text());expected.update(rec.get('save_reopen_mesh_signatures') or rec['signatures'])
for n in report['objects']:assert sig(bpy.data.objects[n])==expected[n]
report['eight_appended_mesh_weight_signatures_match_frozen']=True;report['source_action_signature_preserved']=True
bpy.ops.wm.save_as_mainfile(filepath=str(R/'append_replay_check.blend'))
(R/'records/append_helper_verification.json').write_text(json.dumps(report,indent=2));print('APPEND_HELPER_PASSED',report['objects'])

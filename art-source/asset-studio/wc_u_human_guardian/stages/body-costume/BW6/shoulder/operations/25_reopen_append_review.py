import bpy,sys,json,hashlib,numpy as np
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'operations'));import check_shoulder as ck;from append_bw6_shoulder import append_bw6_shoulder
source=R/'ada_bw6_shoulder_checkpoint_r002_LOCAL_REVIEW.blend';s=ck.load(source);names=json.loads(s['BW6_SHOULDER_ACTIVE']);poseframes=[1,25,49,73,78,86,97];before={}
for f in poseframes:
 s.frame_set(f);bpy.context.view_layer.update();before[f]={n:ck.geom(bpy.data.objects[n])[0] for n in names}
root_source=Path(s['BW6_COAT_CONTEXT_SOURCE']);root_sha=hashlib.sha256(root_source.read_bytes()).hexdigest();assert root_sha==s['BW6_COAT_CONTEXT_SHA256']
s=ck.load(root_source);applied=append_bw6_shoulder(s,bpy.data.objects['BW4_Armor_Independent_Rig']);s['BW6_SHOULDER_COAT']='BW6_PaddedCoat_Tailored';errors={}
for f in poseframes:
 s.frame_set(f);bpy.context.view_layer.update();errors[f]={n:float(np.max(np.abs(ck.geom(bpy.data.objects[n])[0]-before[f][n]))) for n in names}
assert max(v for d in errors.values() for v in d.values())<2e-6
s.frame_set(1);combined=R/'ada_bw6_shoulder_combined_review.blend';bpy.ops.wm.save_as_mainfile(filepath=str(combined));s=ck.load(combined)
record={'frozen_source':str(source),'frozen_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'append_target_context':str(root_source),'append_target_sha256':root_sha,'separate_combined_file':str(combined),'combined_sha256':hashlib.sha256(combined.read_bytes()).hexdigest(),'evaluated_replay_max_axis_errors_m':errors,'three_meshes_seven_helpers_only':applied,'scope':'Independent append and reopened combined candidate; not canonical replacement, second-body fit, universal recipe or runtime evidence.'}
extra=list(np.arange(54.5,89,1.0));record['additional_half_frames']=ck.audit(s,extra)
(R/'records/r002_reopen_append_and_critical_halves.json').write_text(json.dumps(record,indent=2))
adj=[]
targets=['BW6_FrontPlate','BW6_BackPlate','BW6_Front_Neck_TurnedBorder','BW6_Back_Neck_TurnedBorder']
for f in poseframes:
 s.frame_set(f);bpy.context.view_layer.update();gs={n:ck.geom(bpy.data.objects[n]) for n in names};gt={n:ck.geom(bpy.data.objects[n]) for n in targets};adj.append({'frame':f,'pairs':{a+' / '+b:ck.cross(gs[a],gt[b]) for a in names for b in targets}})
(R/'records/r002_adjacent_torso_checks.json').write_text(json.dumps({'combined_source':str(combined),'sha256':record['combined_sha256'],'frames':adj},indent=2))
for cam,pose in [('front','lowered'),('shoulder','lowered'),('rear_three_quarter',73),('shoulder',78)]:s=ck.load(combined);ck.render(s,f'r002_combined_{cam}_{pose}',cam,pose)
s=ck.load(combined);ck.render(s,'r002_clay','shoulder',1,clay=True)
s=ck.load(combined);key=bpy.data.objects['BW4_Key'];key.location.x=-key.location.x;key.location.y=-key.location.y;key.rotation_euler=(Vector((.22,-.04,1.45))-key.location).to_track_quat('-Z','Y').to_euler();ck.render(s,'r002_reversed_clay','shoulder',1,clay=True)
s=ck.load(combined);ck.render(s,'r002_actual_cage','shoulder',1,cage=True)
assert hashlib.sha256(source.read_bytes()).hexdigest()==record['frozen_sha256'];assert hashlib.sha256(root_source.read_bytes()).hexdigest()==root_sha
print('R002_REOPEN_REPLAY_REVIEW_COMPLETE')

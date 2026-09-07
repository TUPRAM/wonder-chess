"""Raise only Tala's Active shield-hand path to clear the measured lower rim."""
import argparse,hashlib,json,shutil,sys
from pathlib import Path
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/blender'))
from refine_update_ada import invariants,action_curve_digest,use_clip
from refine_neris_tala_motion import mesh_digest,clip_views,publish
from hand_contacts import place_hand
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
p=argparse.ArgumentParser();p.add_argument('--report',type=Path,required=True);p.add_argument('--publish',action='store_true');a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);report=a.report.resolve();uid='wc_u_orc_guardian'
if a.publish:publish(uid,report);raise SystemExit
report.mkdir(parents=True,exist_ok=False);source=ROOT/f'art-source/heroes/{uid}/{uid}.blend';folder=ROOT/f'exports/heroes/{uid}';m=json.loads((folder/'export_manifest.json').read_text());assert m['source_revision']==5 and sha(source)==m['source_sha256'];shutil.copy2(source,report/'before.blend');shutil.copy2(folder/'export_manifest.json',report/'before-export-manifest.json');(report/'executed-candidate.py').write_bytes(Path(__file__).read_bytes());bpy.ops.wm.open_mainfile(filepath=str(source));arm=bpy.data.objects['Armature'];before=invariants(arm);geometry=mesh_digest();hashes={action.name:action_curve_digest(action) for action in bpy.data.actions};spec=m['clips']['Active'];use_clip(arm,'Active',1,unit_id=uid);poses=[]
for frame in range(1,spec['frames'][1]+1):
    bpy.context.scene.frame_set(frame);bpy.context.view_layer.update();hand=arm.pose.bones['hand_l'];poses.append({'basis':{b.name:b.matrix_basis.copy() for b in arm.pose.bones},'palm':hand.tail.copy(),'rotation':hand.matrix.to_3x3()@hand.bone.matrix_local.to_3x3().inverted()})
maximum=0;previous={}
for frame,pose in enumerate(poses,1):
    bpy.context.scene.frame_set(frame)
    for bone in arm.pose.bones:bone.matrix_basis=pose['basis'][bone.name]
    bpy.context.view_layer.update();release=spec['release_frame'];end=spec['frames'][1];t=(frame-1)/(release-1) if frame<=release else (frame-release)/(end-release);progress=t*t*(3-2*t) if frame<=release else 1-t*t*(3-2*t);maximum=max(maximum,place_hand(arm,'l',pose['palm']+Vector((0,0,.024*progress)),pose['rotation'],m['height_m']))
    for name in ['upperarm_l','lowerarm_l','hand_l']:
        bone=arm.pose.bones[name];bone.rotation_euler=bone.rotation_euler.to_quaternion().to_euler('XYZ',previous.get(name,bone.rotation_euler));previous[name]=bone.rotation_euler.copy();bone.keyframe_insert('rotation_euler',frame=frame,group=name)
assert maximum<.002;assert geometry==mesh_digest();after=invariants(arm);assert before['rest_skeleton_sha256']==after['rest_skeleton_sha256'];changed=[action.name for action in bpy.data.actions if action_curve_digest(action)!=hashes[action.name]];assert changed==[spec['action']];use_clip(arm,'Idle',1,unit_id=uid);bpy.ops.wm.save_as_mainfile(filepath=str(report/'candidate.blend'),check_existing=False);clip_views(uid,report,['Active'],m,'candidate');(report/'candidate-result.json').write_text(json.dumps({'status':'MEASURED_SHIELD_RIM_CLEARANCE_CANDIDATE','unit_id':uid,'candidate_sha256':sha(report/'candidate.blend'),'source_before_sha256':m['source_sha256'],'before_invariants':before,'after_invariants':after,'geometry_digest':geometry,'before_action_hashes':hashes,'changed_actions':changed,'selected_clips':['Active'],'maximum_hand_reach_clamp_m':{'Active':maximum},'fix':'24mm peak upward hand-path adjustment to address measured20mm rim penetration; existing mace transfer/right-hand/body/feet curves unchanged'},indent=2)+'\n');assert sha(source)==m['source_sha256'];print('WC_TALA_SHIELD_CLEARANCE_CANDIDATE_PASS')

"""Give Rowan's existing active an explicit gather, push and recovery."""
import argparse,json,math,shutil,sys
from pathlib import Path
import bpy
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[2];UID='wc_u_human_mage'
sys.path.insert(0,str(ROOT/'tools/blender'))
from hand_contacts import place_hand
from refine_update_ada import sha,invariants,action_curve_digest,mesh_geometry_digest
def assign(arm,action,frame):
    arm.animation_data.action=action;arm.animation_data.action_slot=action.slots[0]
    bpy.context.scene.frame_set(frame);bpy.context.view_layer.update()
def interpolate(frame,times,values):
    for i in range(1,len(times)):
        if frame<=times[i]:
            t=(frame-times[i-1])/(times[i]-times[i-1]);t=t*t*(3-2*t)
            return values[i-1].lerp(values[i],t)
    return values[-1]
parser=argparse.ArgumentParser();parser.add_argument('--input',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);src=args.input.resolve();out=args.output.resolve();out.mkdir(parents=True,exist_ok=False)
refined=json.loads((src/'refinement.json').read_text());candidate=Path(refined['candidate'])
assert sha(candidate)==refined['candidate_sha256'];bpy.ops.wm.open_mainfile(filepath=str(candidate))
arm=bpy.data.objects['Armature'];old=invariants(arm);geometry=mesh_geometry_digest()
unchanged={clip:action_curve_digest(bpy.data.actions[f'AN_{UID}_{clip}']) for clip in ('Idle','Move','Attack','Hit','Defeat','Victory')}
manifest=json.loads((src/'before-export-manifest.json').read_text());spec=manifest['clips']['Active'];start,end=spec['frames'];release=spec['release_frame']
original=bpy.data.actions[spec['action']];assign(arm,original,start)
anchors={side:arm.pose.bones['hand_'+side].tail.copy() for side in ('l','r')}
rotations={side:arm.pose.bones['hand_'+side].matrix.to_3x3()@arm.pose.bones['hand_'+side].bone.matrix_local.to_3x3().inverted() for side in ('l','r')}
baseline={}
for frame in range(start,end+1):
    assign(arm,original,frame)
    baseline[frame]={b.name:(b.location.copy(),b.rotation_euler.copy(),b.scale.copy()) for b in arm.pose.bones}
action=original.copy();action.use_fake_user=True;original.name='BASELINE_'+spec['action'];action.name=spec['action']
names=[bone+'_'+side for side in ('l','r') for bone in ('upperarm','lowerarm','hand')]
for layer in action.layers:
    for strip in layer.strips:
        for bag in strip.channelbags:
            for curve in list(bag.fcurves):
                if any(f'pose.bones["{name}"]' in curve.data_path for name in names):bag.fcurves.remove(curve)
assign(arm,action,start);max_clamp=0;times=[start,(start+release)//2,release,(release+end)//2,end]
for frame in range(start,end+1):
    bpy.context.scene.frame_set(frame)
    for name,(location,rotation,scale) in baseline[frame].items():
        bone=arm.pose.bones[name];bone.location=location;bone.rotation_euler=rotation;bone.scale=scale
    bpy.context.view_layer.update()
    right=interpolate(frame,times,[anchors['r'],Vector((-.27,.18,1.03)),Vector((-.33,.36,1.04)),Vector((-.40,.23,.93)),anchors['r']])
    left=interpolate(frame,times,[anchors['l'],Vector((.04,.22,1.09)),Vector((.08,.34,1.10)),Vector((.22,.22,.96)),anchors['l']])
    amount=math.sin(math.pi*(frame-start)/(end-start))
    turn=Matrix.Rotation(math.radians(-8*amount),3,'X')@Matrix.Rotation(math.radians(-12*amount),3,'Y')
    max_clamp=max(max_clamp,place_hand(arm,'r',right,rotations['r']@turn,1.78),place_hand(arm,'l',left,rotations['l'],1.78))
    for name in names:
        arm.pose.bones[name].keyframe_insert(data_path='location',frame=frame,group=name)
        arm.pose.bones[name].keyframe_insert(data_path='rotation_euler',frame=frame,group=name)
if max_clamp>.025:raise RuntimeError(f'Rowan active reach clamp {max_clamp}')
for layer in action.layers:
    for strip in layer.strips:
        for bag in strip.channelbags:
            for curve in bag.fcurves:
                if any(f'pose.bones["{name}"]' in curve.data_path for name in names):
                    for key in curve.keyframe_points:key.interpolation='LINEAR'
bpy.data.actions.remove(original)
assert geometry==mesh_geometry_digest() and invariants(arm)['rest_skeleton_sha256']==old['rest_skeleton_sha256']
for clip,digest in unchanged.items():assert action_curve_digest(bpy.data.actions[f'AN_{UID}_{clip}'])==digest
assign(arm,bpy.data.actions[f'AN_{UID}_Idle'],1);target=out/'rowan-update24-revision7.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(target),check_existing=False)
for name in ('before-source.blend','before-export-manifest.json','after-front.png','after-side.png','after-back.png','after-three-quarter.png'):shutil.copy2(src/name,out/name)
refined.update(candidate=str(target),candidate_sha256=sha(target),verified_candidate_invariants=invariants(arm),
    unchanged_action_sha256=unchanged,action_refinement_script_sha256=sha(Path(__file__)),
    changed_clips=[{'clip':'Active','frames_baked':end-start+1,'release_frame':release,'maximum_support_reach_clamp_m':max_clamp}],
    geometry_unchanged_from_rendered_candidate=True,rendered_geometry_source=str(src))
(out/'refinement.json').write_text(json.dumps(refined,indent=2)+'\n');print('WC_ROWAN_ACTIVE_REFINED',flush=True)

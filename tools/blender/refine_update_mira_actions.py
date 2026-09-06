"""Refine three observed Mira gestures on the isolated geometry candidate."""
import argparse, json, math, shutil, sys
from pathlib import Path
import bpy
from mathutils import Vector, Matrix

ROOT=Path(__file__).resolve().parents[2];UID='wc_u_human_priest'
sys.path.insert(0,str(ROOT/'tools/blender'))
from hand_contacts import place_hand
from refine_update_ada import sha,invariants,mesh_geometry_digest,action_curve_digest

def assign(arm,action,frame):
    arm.animation_data.action=action;arm.animation_data.action_slot=action.slots[0]
    bpy.context.scene.frame_set(frame);bpy.context.view_layer.update()
def rotation(x=0,y=0,z=0):
    return Matrix.Rotation(math.radians(z),3,'Z')@Matrix.Rotation(math.radians(y),3,'Y')@Matrix.Rotation(math.radians(x),3,'X')
def interpolate(frame,times,values):
    for i in range(1,len(times)):
        if frame<=times[i]:
            t=(frame-times[i-1])/(times[i]-times[i-1]);t=t*t*(3-2*t)
            return values[i-1].lerp(values[i],t)
    return values[-1]

parser=argparse.ArgumentParser();parser.add_argument('--input',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);src=args.input.resolve();out=args.output.resolve()
out.mkdir(parents=True,exist_ok=False)
refined=json.loads((src/'refinement.json').read_text());candidate=Path(refined['candidate'])
assert sha(candidate)==refined['candidate_sha256'];bpy.ops.wm.open_mainfile(filepath=str(candidate))
arm=bpy.data.objects['Armature'];old=invariants(arm);geometry=mesh_geometry_digest()
unchanged={name:action_curve_digest(bpy.data.actions[f'AN_{UID}_{name}']) for name in ('Idle','Move','Attack','Defeat')}
manifest=json.loads((src/'before-export-manifest.json').read_text());records=[]
for clip in ('Active','Hit','Victory'):
    spec=manifest['clips'][clip];start,end=spec['frames'];original=bpy.data.actions[spec['action']]
    assign(arm,original,start)
    anchors={side:arm.pose.bones['hand_'+side].tail.copy() for side in ('r','l')}
    shoulders={side:arm.pose.bones['upperarm_'+side].head.copy() for side in ('r','l')}
    rotations={side:arm.pose.bones['hand_'+side].matrix.to_3x3()@arm.pose.bones['hand_'+side].bone.matrix_local.to_3x3().inverted() for side in ('r','l')}
    baseline={}
    for frame in range(start,end+1):
        assign(arm,original,frame)
        baseline[frame]={b.name:(b.location.copy(),b.rotation_euler.copy(),b.scale.copy()) for b in arm.pose.bones}
    assign(arm,bpy.data.actions[f'AN_{UID}_Idle'],1)
    idle_left={name:(arm.pose.bones[name].location.copy(),arm.pose.bones[name].rotation_euler.copy()) for name in ('upperarm_l','lowerarm_l','hand_l')}
    action=original.copy();action.use_fake_user=True;original.name='BASELINE_'+spec['action'];action.name=spec['action']
    names=['upperarm_r','lowerarm_r','hand_r']
    if clip in ('Active','Victory'):names+=['upperarm_l','lowerarm_l','hand_l']
    for layer in action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for curve in list(bag.fcurves):
                    if any(f'pose.bones["{name}"]' in curve.data_path for name in names):bag.fcurves.remove(curve)
    assign(arm,action,start);max_clamp=0
    for frame in range(start,end+1):
        bpy.context.scene.frame_set(frame)
        for name,(location,angles,scale) in baseline[frame].items():
            bone=arm.pose.bones[name];bone.location=location;bone.rotation_euler=angles;bone.scale=scale
        bpy.context.view_layer.update();amount=math.sin(math.pi*(frame-start)/(end-start))
        if clip=='Active':
            times=[1,10,22,31,40]
            right=interpolate(frame,times,[anchors['r'],Vector((-.43,.20,.84)),Vector((-.31,.37,1.08)),Vector((-.39,.23,.92)),anchors['r']])
            angles=interpolate(frame,times,[Vector(),Vector((-8,0,0)),Vector((-28,-5,0)),Vector((-12,0,0)),Vector()])
            left=anchors['l'].lerp(Vector((-.05,.27,1.04)),max(0,amount))
            max_clamp=max(max_clamp,place_hand(arm,'r',right,rotations['r']@rotation(*angles),1.7))
            max_clamp=max(max_clamp,place_hand(arm,'l',left,rotations['l'],1.7))
        else:
            follow=arm.pose.bones['upperarm_r'].head-shoulders['r']
            offset=Vector((.015,.025,-.015)) if clip=='Hit' else Vector((.03,.04,.09))
            max_clamp=max(max_clamp,place_hand(arm,'r',anchors['r']+follow+offset*amount,rotations['r']@rotation(-5*amount,0,0),1.7))
            if clip=='Victory':
                for name,(location,angles) in idle_left.items():arm.pose.bones[name].location=location;arm.pose.bones[name].rotation_euler=angles
        for name in names:
            arm.pose.bones[name].keyframe_insert(data_path='location',frame=frame,group=name)
            arm.pose.bones[name].keyframe_insert(data_path='rotation_euler',frame=frame,group=name)
    for layer in action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for curve in bag.fcurves:
                    if any(f'pose.bones["{name}"]' in curve.data_path for name in names):
                        for key in curve.keyframe_points:key.interpolation='LINEAR'
    bpy.data.actions.remove(original)
    records.append({'clip':clip,'frames_baked':end-start+1,'maximum_support_reach_clamp_m':max_clamp,'release_frame':spec['release_frame']})
    if max_clamp>.025:raise RuntimeError(f'{clip}: reach clamp {max_clamp}')
assert geometry==mesh_geometry_digest() and invariants(arm)['rest_skeleton_sha256']==old['rest_skeleton_sha256']
for name,expected in unchanged.items():assert action_curve_digest(bpy.data.actions[f'AN_{UID}_{name}'])==expected
assign(arm,bpy.data.actions[f'AN_{UID}_Idle'],1)
target=out/'mira-update24-revision7.blend';bpy.ops.wm.save_as_mainfile(filepath=str(target),check_existing=False)
for name in ('before-source.blend','before-export-manifest.json','after-front.png','after-side.png','after-back.png','after-three-quarter.png'):
    shutil.copy2(src/name,out/name)
refined.update(candidate=str(target),candidate_sha256=sha(target),verified_candidate_invariants=invariants(arm),
    changed_clips=records,unchanged_action_sha256=unchanged,action_refinement_script_sha256=sha(Path(__file__)),
    geometry_unchanged_from_rendered_candidate=True,rendered_geometry_source=str(src))
(out/'refinement.json').write_text(json.dumps(refined,indent=2)+'\n')
print('WC_MIRA_GESTURE_TRIAL_PASS '+json.dumps(records),flush=True)

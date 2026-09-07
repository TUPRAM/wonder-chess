"""Incremental selected-clip trials preserving source geometry, rig and other actions."""
import argparse,hashlib,json,math,runpy,shutil,sys
from pathlib import Path
import bpy
from mathutils import Matrix,Vector
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/blender'))
from refine_update_ada import invariants,action_curve_digest,use_clip
from hand_contacts import place_hand
from author_alpha import export_fbx_raw
from normalized_fbx import export_normalized_copy
from author_update_pippa import place_foot
DIAGNOSTICS=[]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def smooth(t):t=max(0,min(1,t));return t*t*(3-2*t)
def mesh_digest():
    h=hashlib.sha256()
    for ob in sorted((o for o in bpy.data.objects if o.type=='MESH'),key=lambda o:o.name):
        h.update(ob.name.encode())
        for v in ob.data.vertices:h.update(repr((tuple(v.co),[(g.group,g.weight) for g in v.groups])).encode())
        for poly in ob.data.polygons:h.update(repr(tuple(poly.vertices)).encode())
    return h.hexdigest()
def clip_views(uid,report,clips,m,tag):
    scene=bpy.context.scene;arm=bpy.data.objects['Armature'];h=m['height_m'];scene.render.resolution_x=scene.render.resolution_y=512;scene.cycles.samples=4
    for clip in clips:
        spec=m['clips'][clip];frame=spec['release_frame'] or spec['frames'][1]//2;use_clip(arm,clip,frame,unit_id=uid)
        for name,pos in [('front',(0,h*3.5,h*1.2)),('side',(h*3.5,0,h*1.2)),('three-quarter',(h*1.6,h*3,h*1.4))]:
            scene.camera.location=pos;scene.camera.data.ortho_scale=h*1.44;scene.camera.rotation_euler=(Vector((0,0,h*.54))-scene.camera.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(report/f'{tag}-{clip}-{name}.png');bpy.ops.render.render(write_still=True)
def selected_pose(uid,arm,clip,frame,spec,h):
    end=spec['frames'][1];release=spec['release_frame'] or max(2,end//3)
    times=[1,max(2,release//2),release,min(end,release+9),end];values=[0,1,1,.4,0]
    for i in range(1,5):
        if frame<=times[i]:a=values[i-1]+(values[i]-values[i-1])*smooth((frame-times[i-1])/max(1,times[i]-times[i-1]));break
    else:a=0
    spine=arm.pose.bones['spine_02'];body=spine.matrix@spine.bone.matrix_local.inverted();rot=body.to_3x3()
    def turn(x=0,y=0,z=0):return rot@Matrix.Rotation(math.radians(z),3,'Z')@Matrix.Rotation(math.radians(y),3,'Y')@Matrix.Rotation(math.radians(x),3,'X')
    def hand(side,xyz,rotation):return place_hand(arm,side,body@(Vector(xyz)*h),rotation,h)
    if uid=='wc_u_elf_mage':
        # Lens center lies .104 body heights above its held base: raise the base
        # toward .80 so the focus aligns with the actual .90-height eye line.
        wave=math.sin((frame-1)/(end-1)*math.tau)
        errors=[hand('l',(.19-.10*a,.16+.025*a,.56+.24*a+.003*wave),turn(-8+2*a)),hand('r',(-.22+.225*a,.10+.105*a,.48+.355*a),turn(-12+6*a,0,-25*a))]
    elif clip=='Hit':
        # Keep protection attached, but lower/angle the shield away from the face.
        errors=[hand('l',(.285,.14,.46),turn(7,0,-12))]
    else:
        progress=smooth((frame-1)/(release-1)) if frame<=release else 1-smooth((frame-release)/(end-release))
        placed=smooth(progress/.60);freed=smooth((progress-.60)/.40)
        pelvis=arm.pose.bones['pelvis'];matrix=pelvis.matrix.copy();matrix.translation.z-=.22*h*progress;pelvis.matrix=matrix;bpy.context.view_layer.update()
        errors=[]
        for side in ('l','r'):
            target=arm.data.bones['foot_'+side].head_local/h+Vector((0,0,.002/h));errors.append(place_foot(arm,side,target,h))
        # A short braced crouch puts the existing shield bottom on the board.
        left=Vector((.26,.14+.03*progress,.51-.248*progress))*h
        leftrot=Matrix.Rotation(math.radians(-8*(1-progress)),3,'Z')@Matrix.Rotation(math.radians(-5*(1-progress)),3,'X')
        errors.append(place_hand(arm,'l',left,leftrot,h))
        # Carry the mace across to a visible rest against shield/left forearm,
        # then free the right hand. Reverse the transfer in recovery.
        original=Vector((-.29,.11,.50))*h
        rest=Vector((-.12,.18,.51))*h
        prop_point=original.lerp(rest,placed)
        originalrot=Matrix.Rotation(math.radians(-30),3,'X')
        restrot=Matrix.Rotation(math.radians(90),3,'Y')
        proprot=originalrot.to_quaternion().slerp(restrot.to_quaternion(),placed).to_matrix()
        palm=prop_point.lerp(Vector((-.285,.28,.465))*h,freed)
        palmrot=proprot.to_quaternion().slerp(Matrix.Rotation(math.radians(-12),3,'Z').to_quaternion(),freed).to_matrix()
        errors.append(place_hand(arm,'r',palm,palmrot,h))
        rest_grip=arm.data.bones['hand_r'].tail_local
        deformation=proprot.to_4x4();deformation.translation=prop_point-proprot@rest_grip
        arm.pose.bones['weapon_r'].matrix=deformation@arm.data.bones['weapon_r'].matrix_local
        arm.pose.bones['weapon_r'].scale=(1,1,1);bpy.context.view_layer.update()
        DIAGNOSTICS.append({'frame':frame,'progress':progress,'clamps_m':dict(zip(['foot_l','foot_r','hand_l','hand_r'],errors)),'left_palm_target':list(left),'right_palm_target':list(palm),'left_shoulder':list(arm.pose.bones['upperarm_l'].head),'right_shoulder':list(arm.pose.bones['upperarm_r'].head)})
    return max(errors)
def candidate(uid,report,clips):
    report.mkdir(parents=True,exist_ok=False);source=ROOT/f'art-source/heroes/{uid}/{uid}.blend';out=ROOT/f'exports/heroes/{uid}';m=json.loads((out/'export_manifest.json').read_text());assert sha(source)==m['source_sha256'];shutil.copy2(source,report/'before.blend');shutil.copy2(out/'export_manifest.json',report/'before-export-manifest.json');(report/'executed-candidate.py').write_bytes(Path(__file__).read_bytes());bpy.ops.wm.open_mainfile(filepath=str(source));arm=bpy.data.objects['Armature'];before=invariants(arm);geometry=mesh_digest();hashes={a.name:action_curve_digest(a) for a in bpy.data.actions};reach={}
    if not a.skip_before:clip_views(uid,report,clips,m,'before')
    for clip in clips:
        spec=m['clips'][clip];use_clip(arm,clip,1,unit_id=uid);action=arm.animation_data.action;previous={};maximum=0;original=[]
        for frame in range(spec['frames'][0],spec['frames'][1]+1):
            bpy.context.scene.frame_set(frame);original.append({b.name:b.matrix_basis.copy() for b in arm.pose.bones})
        for frame in range(spec['frames'][0],spec['frames'][1]+1):
            bpy.context.scene.frame_set(frame)
            for bone in arm.pose.bones:bone.matrix_basis=original[frame-spec['frames'][0]][bone.name]
            bpy.context.view_layer.update();maximum=max(maximum,selected_pose(uid,arm,clip,frame,spec,m['height_m']))
            for bone in arm.pose.bones:
                if uid=='wc_u_orc_guardian' and clip=='Active':
                    if not bone.name.startswith(('upperarm_','lowerarm_','hand_','weapon_r','pelvis','thigh_','calf_','foot_')):continue
                else:
                    if not bone.name.startswith(('upperarm_','lowerarm_','hand_')):continue
                    if uid=='wc_u_orc_guardian' and not bone.name.endswith('_l'):continue
                bone.rotation_euler=bone.rotation_euler.to_quaternion().to_euler('XYZ',previous.get(bone.name,bone.rotation_euler));previous[bone.name]=bone.rotation_euler.copy();bone.keyframe_insert('rotation_euler',frame=frame,group=bone.name)
                if uid=='wc_u_orc_guardian' and clip=='Active':bone.keyframe_insert('location',frame=frame,group=bone.name)
        reach[clip]=maximum
    after=invariants(arm);assert before['rest_skeleton_sha256']==after['rest_skeleton_sha256'];assert geometry==mesh_digest();changed=[a.name for a in bpy.data.actions if action_curve_digest(a)!=hashes[a.name]];assert set(changed)=={m['clips'][c]['action'] for c in clips}
    (report/'reach-diagnostics.json').write_text(json.dumps(DIAGNOSTICS,indent=2)+'\n');assert max(reach.values())<.005,reach
    use_clip(arm,'Idle',1,unit_id=uid);bpy.ops.wm.save_as_mainfile(filepath=str(report/'candidate.blend'),check_existing=False);clip_views(uid,report,clips,m,'candidate');assert sha(source)==m['source_sha256'];(report/'candidate-result.json').write_text(json.dumps({'status':'SELECTED_CLIP_TRIAL_RENDERED_NOT_PUBLISHED','unit_id':uid,'source_before_sha256':m['source_sha256'],'candidate_sha256':sha(report/'candidate.blend'),'before_invariants':before,'after_invariants':after,'geometry_digest':geometry,'before_action_hashes':hashes,'changed_actions':changed,'selected_clips':clips,'maximum_hand_reach_clamp_m':reach},indent=2)+'\n');print('WC_SELECTED_MOTION_CANDIDATE_PASS',uid)
p=argparse.ArgumentParser();p.add_argument('--unit',choices=['wc_u_elf_mage','wc_u_orc_guardian'],required=True);p.add_argument('--report',type=Path,required=True);p.add_argument('--clips',nargs='+',required=True);p.add_argument('--skip-before',action='store_true');a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);candidate(a.unit,a.report.resolve(),a.clips)

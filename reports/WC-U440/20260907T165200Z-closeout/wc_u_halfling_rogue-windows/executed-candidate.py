"""Author two complete attack presentations in one asset using frozen hero sources."""
import argparse,hashlib,json,math,runpy,shutil,sys
from pathlib import Path
import bpy
from mathutils import Matrix,Vector
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/blender'))
from refine_update_ada import invariants,action_curve_digest,use_clip
from refine_neris_tala_motion import mesh_digest
from author_alpha import export_fbx_raw
from normalized_fbx import export_normalized_copy
ALLOWED=['wc_u_elf_rogue','wc_u_orc_warrior','wc_u_orc_rogue','wc_u_halfling_rogue']
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def record(arm):return {b.name:{'basis':b.matrix_basis.copy(),'world':b.matrix.copy(),'location':b.location.copy(),'scale':b.scale.copy()} for b in arm.pose.bones}
def key_pose(arm,frame,previous):
    for bone in arm.pose.bones:
        if bone.rotation_mode=='QUATERNION':
            if bone.name in previous and bone.rotation_quaternion.dot(previous[bone.name])<0:bone.rotation_quaternion.negate()
            previous[bone.name]=bone.rotation_quaternion.copy();bone.keyframe_insert('rotation_quaternion',frame=frame,group=bone.name)
        else:
            bone.rotation_euler=bone.rotation_euler.to_quaternion().to_euler(bone.rotation_mode,previous.get(bone.name,bone.rotation_euler));previous[bone.name]=bone.rotation_euler.copy();bone.keyframe_insert('rotation_euler',frame=frame,group=bone.name)
        bone.keyframe_insert('location',frame=frame,group=bone.name)
def candidate(uid,report):
    report.mkdir(parents=True,exist_ok=False);source=ROOT/f'art-source/heroes/{uid}/{uid}.blend';folder=ROOT/f'exports/heroes/{uid}';m=json.loads((folder/'export_manifest.json').read_text());u=next(x for x in json.loads((ROOT/'data/units.json').read_text())['units'] if x['id']==uid);assert sha(source)==m['source_sha256'];spec=m['clips']['Attack'];assert 'presentation_windows' not in spec;end=spec['frames'][1];release=spec['release_frame'];assert spec['frames'][0]==1 and release==round(u['stats']['attack_windup_ms']*.06)+1
    shutil.copy2(source,report/'before.blend');shutil.copy2(folder/'export_manifest.json',report/'before-export-manifest.json');shutil.copy2(folder/(spec['action']+'.fbx'),report/'before-Attack.fbx');(report/'executed-candidate.py').write_bytes(Path(__file__).read_bytes());bpy.ops.wm.open_mainfile(filepath=str(source));arm=bpy.data.objects['Armature'];before=invariants(arm);geometry=mesh_digest();hashes={a.name:action_curve_digest(a) for a in bpy.data.actions};use_clip(arm,'Attack',1,unit_id=uid);old=arm.animation_data.action;snapshots=[]
    for frame in range(1,end+1):bpy.context.scene.frame_set(frame);bpy.context.view_layer.update();snapshots.append(record(arm))
    start=snapshots[0];finish=snapshots[-1];boundary_error=max(abs(start[name]['world'][i][j]-finish[name]['world'][i][j]) for name in start for i in range(4) for j in range(4));assert boundary_error<1e-4,boundary_error
    arm.animation_data_clear();bpy.data.actions.remove(old);previous={}
    # Bake actual original 60Hz poses; no regenerated first strike or new event.
    for frame,snapshot in enumerate(snapshots,1):
        for bone in arm.pose.bones:bone.matrix_basis=snapshot[bone.name]['basis']
        key_pose(arm,frame,previous)
    mirror=Matrix.Diagonal((-1,1,1,1));ordered=sorted(arm.pose.bones,key=lambda b:len(b.parent_recursive))
    for index,snapshot in enumerate(snapshots):
        frame=end+index
        for bone in ordered:
            name=bone.name
            source_name=name if uid=='wc_u_orc_warrior' else name[:-2]+('_r' if name.endswith('_l') else '_l') if name.endswith(('_l','_r')) else name
            relative=snapshot[source_name]['world']@start[source_name]['world'].inverted()
            target=mirror@relative@mirror@start[name]['world']
            bone.matrix=target
            # Retain joint attachment and all source local translations. The
            # reflected relative orientation changes swing direction, not reach.
            bone.location=start[name]['location'];bone.scale=start[name]['scale'];bpy.context.view_layer.update()
        key_pose(arm,frame,previous)
    action=arm.animation_data.action;action.name=spec['action'];action.use_fake_user=True
    for layer in action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for curve in bag.fcurves:
                    for key in curve.keyframe_points:key.interpolation='LINEAR'
    windows=[{'name':'R','start_frame':1,'release_frame':release,'end_frame':end},{'name':'L','start_frame':end,'release_frame':end+release-1,'end_frame':2*end-1}]
    assert list(action.frame_range)==[1,2*end-1];seams=[]
    for frame in [1,end,2*end-1]:
        bpy.context.scene.frame_set(frame);bpy.context.view_layer.update();seams.append(record(arm))
    seam_error=max(abs(seams[0][name]['world'][i][j]-s[name]['world'][i][j]) for s in seams[1:] for name in start for i in range(4) for j in range(4));assert seam_error<1e-4,seam_error
    assert mesh_digest()==geometry;after=invariants(arm);assert after['rest_skeleton_sha256']==before['rest_skeleton_sha256'];changed=[a.name for a in bpy.data.actions if action_curve_digest(a)!=hashes[a.name]];assert changed==[spec['action']]
    use_clip(arm,'Idle',1,unit_id=uid);bpy.ops.wm.save_as_mainfile(filepath=str(report/'candidate.blend'),check_existing=False);scene=bpy.context.scene;h=m['height_m'];scene.render.resolution_x=scene.render.resolution_y=512;scene.cycles.samples=4;scene.camera.location=(h*1.5,h*3,h*1.35);scene.camera.data.ortho_scale=h*1.5;scene.camera.rotation_euler=(Vector((0,0,h*.54))-scene.camera.location).to_track_quat('-Z','Y').to_euler()
    captures=[]
    for window in windows:
        frames=sorted(set([window['start_frame'],window['start_frame']+(release-1)//2,window['release_frame'],min(window['end_frame'],window['release_frame']+9),window['end_frame']]))
        for frame in frames:
            use_clip(arm,'Attack',frame,unit_id=uid);path=report/f"{window['name']}-{frame:03d}.png";scene.render.filepath=str(path);bpy.ops.render.render(write_still=True);captures.append({'window':window['name'],'frame':frame,'image':str(path)})
    assert sha(source)==m['source_sha256'];(report/'candidate-result.json').write_text(json.dumps({'status':'TWO_FULL_ATTACK_WINDOWS_CANDIDATE','unit_id':uid,'candidate_sha256':sha(report/'candidate.blend'),'source_before_sha256':m['source_sha256'],'before_invariants':before,'after_invariants':after,'geometry_digest':geometry,'before_action_hashes':hashes,'presentation_windows':windows,'original_boundary_matrix_max_error':boundary_error,'three_boundary_matrix_max_error':seam_error,'captures':captures,'direction_contract':'Rok retains one-handed axe/open off-hand and alternates sweep direction; other dual-prop heroes exchange leading hands.','limits':['Actual sampled poses need review','No extra combat packet or hit event; runtime chooses exactly one window per basic','Geometry/other6 actions remain unchanged; no final art approval']},indent=2)+'\n');print('WC_ALTERNATING_CANDIDATE',uid)
def publish(uid,report):
    source=ROOT/f'art-source/heroes/{uid}/{uid}.blend';folder=ROOT/f'exports/heroes/{uid}';info=json.loads((report/'candidate-result.json').read_text());m=json.loads((report/'before-export-manifest.json').read_text());assert sha(source)==info['source_before_sha256'];assert sha(report/'candidate.blend')==info['candidate_sha256'];(report/'executed-publish.py').write_bytes(Path(__file__).read_bytes());bpy.ops.wm.open_mainfile(filepath=str(report/'candidate.blend'));arm=bpy.data.objects['Armature'];assert mesh_digest()==info['geometry_digest'];assert invariants(arm)==info['after_invariants'];spec=m['clips']['Attack'];spec['frames']=[1,info['presentation_windows'][-1]['end_frame']];spec['presentation_windows']=info['presentation_windows'];spec['duration_seconds']=(spec['frames'][1]-1)/60
    stage=report/'normalized-export';stage.mkdir(exist_ok=False);use_clip(arm,'Attack',1,unit_id=uid);bpy.context.scene.frame_start=1;bpy.context.scene.frame_end=spec['frames'][1];export_normalized_copy(stage/(spec['action']+'.fbx'),[arm],True,export_fbx_raw);use_clip(arm,'Idle',1,unit_id=uid);assert mesh_digest()==info['geometry_digest'];bpy.ops.wm.save_as_mainfile(filepath=str(source),check_existing=False);shutil.copy2(stage/(spec['action']+'.fbx'),folder/(spec['action']+'.fbx'));m.update({'source_revision':m['source_revision']+1,'animation_revision':m['animation_revision']+1,'source_sha256':sha(source),'alternating_attack_evidence':str(report),'alternating_attack_author_sha256':sha(report/'executed-candidate.py'),'alternating_attack_publisher_sha256':sha(report/'executed-publish.py'),'files':{p.name:sha(p) for p in folder.iterdir() if p.is_file() and p.name!='export_manifest.json'}});(folder/'export_manifest.json').write_text(json.dumps(m,indent=2)+'\n');(report/'published-result.json').write_text(json.dumps({'status':'TWO_ATTACK_WINDOWS_PUBLISHED_PENDING_READBACK','unit_id':uid,'source_revision':m['source_revision'],'animation_revision':m['animation_revision'],'source_sha256':sha(source),'manifest_sha256':sha(folder/'export_manifest.json'),'presentation_windows':spec['presentation_windows']},indent=2)+'\n');print('WC_ALTERNATING_PUBLISHED',uid)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--unit',choices=ALLOWED,required=True);p.add_argument('--report',type=Path,required=True);p.add_argument('--publish',action='store_true');a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);publish(a.unit,a.report.resolve()) if a.publish else candidate(a.unit,a.report.resolve())

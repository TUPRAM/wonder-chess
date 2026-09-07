"""Extend existing elf sleeve roots into the torso and inspect the saved asset."""
import argparse,bmesh,hashlib,json,math,runpy,shutil,sys
from pathlib import Path
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/blender'))
from refine_update_ada import components,invariants,action_curve_digest,use_clip
from author_alpha import export_fbx_raw
from normalized_fbx import export_normalized_copy
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def clean(ob):
    bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));seen=set();remove=[]
    for f in bm.faces:
        key=tuple(sorted(tuple(round(x,5) for x in v.co) for v in f.verts))
        if key in seen or f.calc_area()<1e-8:remove.append(f)
        else:seen.add(key)
    if remove:bmesh.ops.delete(bm,geom=remove,context='FACES_ONLY')
    bm.to_mesh(ob.data);bm.free();ob.data.calc_loop_triangles()
def action_hashes():return {a.name:action_curve_digest(a) for a in bpy.data.actions}
def check_invariants(before,after,uid):
    assert before['rest_skeleton_sha256']==after['rest_skeleton_sha256'];assert before['fps']==after['fps']==60;assert before['unit_scale_m']==after['unit_scale_m']==1;assert before['action_names']==after['action_names']
def render_views(uid,report,h):
    scene=bpy.context.scene;scene.cycles.samples=10;scene.render.resolution_x=scene.render.resolution_y=768
    for name,loc in [('front',(0,4,1.8)),('side',(4,0,1.8)),('back',(0,-4,1.8)),('three-quarter',(3,5,2.7))]:
        scene.camera.location=loc;scene.camera.data.ortho_scale=h*1.42;scene.camera.rotation_euler=(Vector((0,0,h*.54))-scene.camera.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(report/(name+'.png'));bpy.ops.render.render(write_still=True)
def candidate(uid,report):
    source=ROOT/f'art-source/heroes/{uid}/{uid}.blend';out=ROOT/f'exports/heroes/{uid}';report.mkdir(parents=True,exist_ok=False);m=json.loads((out/'export_manifest.json').read_text());assert m['source_revision']==7 and sha(source)==m['source_sha256'];shutil.copy2(source,report/'before.blend');shutil.copy2(out/'export_manifest.json',report/'before-export-manifest.json');shutil.copy2(out/'portrait.png',report/'before-portrait.png');(report/'executed-repair.py').write_bytes(Path(__file__).read_bytes());bpy.ops.wm.open_mainfile(filepath=str(source));arm=bpy.data.objects['Armature'];before=invariants(arm);hashes=action_hashes();u=next(u for u in json.load(open(ROOT/'data/units.json'))['units'] if u['id']==uid);h=u['height_m'];changes=[]
    for ob in [bpy.data.objects['SK_'+uid],*list(bpy.data.collections['BODY'].objects)]:
        if ob.type!='MESH':continue
        for c in components(ob):
            if c['count']!=112 or len(c['groups'])!=2 or not all(('upperarm' in g or 'lowerarm' in g) for g in c['groups']):continue
            side='l' if 'upperarm_l' in c['groups'] else 'r';verts=[ob.data.vertices[i] for i in c['indices']];root=sum((v.co.copy() for v in verts[:16]),Vector())/16;target=arm.data.bones['upperarm_'+side].head_local.copy();target.x-= (1 if side=='l' else -1)*h*.045;target.z-=h*.004
            for v in verts[:16]:
                radial=v.co-root;v.co=target+radial.normalized()*(h*.04)
                for group in ob.vertex_groups:group.remove([v.index])
                ob.vertex_groups['spine_03'].add([v.index],1,'REPLACE')
            for v in verts[16:32]:
                for group in ob.vertex_groups:group.remove([v.index])
                ob.vertex_groups['spine_03'].add([v.index],.15,'REPLACE');ob.vertex_groups['upperarm_'+side].add([v.index],.85,'REPLACE')
            changes.append({'object':ob.name,'side':side,'existing_sleeve_vertices':112,'modified_root_ring_vertices':16,'blended_second_ring_vertices':16,'old_root_center_m':list(root),'new_root_center_m':list(target)})
    assert len(changes)==4
    if uid=='wc_u_elf_rogue':
        use_clip(arm,'Attack',unit_id=uid)
        # The off-hand closes the guard during recovery; frame16 remains the sole hit release.
        keys=[(1,(.122173,0,-.087266),(.174533,0,0)),(10,(.122173,0,-.087266),(.174533,0,0)),(16,(.23,0,.08),(.42,0,0)),(22,(.47,0,-.14),(.16,0,0)),(29,(.23,0,-.19),(.26,0,0)),(40,(.122173,0,-.087266),(.174533,0,0))]
        for frame,upper,lower in keys:
            for bone,value in [('upperarm_l',upper),('lowerarm_l',lower)]:
                arm.pose.bones[bone].rotation_euler=value;arm.pose.bones[bone].keyframe_insert('rotation_euler',frame=frame,group=bone)
        action=arm.animation_data.action
        for layer in action.layers:
            for strip in layer.strips:
                for bag in strip.channelbags:
                    for curve in bag.fcurves:
                        if any(x in curve.data_path for x in ['upperarm_l','lowerarm_l']):
                            for k in curve.keyframe_points:k.interpolation='BEZIER';k.handle_left_type='AUTO_CLAMPED';k.handle_right_type='AUTO_CLAMPED'
    after=invariants(arm);check_invariants(before,after,uid);after_hashes=action_hashes();changed=[name for name in hashes if hashes[name]!=after_hashes[name]];assert changed==([f'AN_{uid}_Attack'] if uid=='wc_u_elf_rogue' else []);use_clip(arm,'Idle',unit_id=uid);bpy.ops.wm.save_as_mainfile(filepath=str(report/'candidate.blend'),check_existing=False);render_views(uid,report,h)
    assert sha(source)==m['source_sha256'];(report/'candidate-result.json').write_text(json.dumps({'status':'ACTUAL_SLEEVE_REPAIR_CANDIDATE_RENDERED_NOT_PUBLISHED','unit_id':uid,'source_before_sha256':m['source_sha256'],'candidate_sha256':sha(report/'candidate.blend'),'before_invariants':before,'after_invariants':after,'before_action_hashes':hashes,'after_action_hashes':after_hashes,'changed_actions':changed,'changes':changes,'preserved':['Mantle/hair/palette/gear and every sleeve vertex beyond the two root rings','Rest skeleton and canonical clip timing','All seven Liora actions; other six Sylas actions'],'Sylas_motion_boundary':'Left blade now contributes a recovery guard follow-through after existing right-blade release16. One composite Attack cycle, not proven alternating successive combat attacks. No extra damage or notify.'},indent=2)+'\n');print('WC_ELF_SLEEVE_CANDIDATE',uid)
def publish(uid,report):
    source=ROOT/f'art-source/heroes/{uid}/{uid}.blend';out=ROOT/f'exports/heroes/{uid}';(report/'executed-publish.py').write_bytes(Path(__file__).read_bytes());info=json.loads((report/'candidate-result.json').read_text());m=json.loads((report/'before-export-manifest.json').read_text());assert sha(source)==info['source_before_sha256'];assert sha(report/'candidate.blend')==info['candidate_sha256'];bpy.ops.wm.open_mainfile(filepath=str(report/'candidate.blend'));arm=bpy.data.objects['Armature'];assert invariants(arm)==info['after_invariants'];mesh=bpy.data.objects['SK_'+uid];saved=sys.argv
    try:
        sys.argv=['inspect_scene.py','--','--collection','EXPORT','--require-skin','--output',str(report/'candidate-structure.json')];runpy.run_path(str(ROOT/'tools/blender/inspect_scene.py'),run_name='__main__')
        sys.argv=['audit_motion.py','--','--unit',uid,'--output',str(report/'candidate-motion.json')];runpy.run_path(str(ROOT/'tools/blender/audit_motion.py'),run_name='__main__')
    finally:sys.argv=saved
    assert not json.loads((report/'candidate-structure.json').read_text())['errors'];assert not json.loads((report/'candidate-motion.json').read_text())['errors'];stage=report/'normalized-export';stage.mkdir(exist_ok=False);arm.data.pose_position='REST';lods=[]
    for level,ratio in [(1,.5),(2,.25)]:
        bpy.data.objects.remove(bpy.data.objects[f'SK_{uid}_LOD{level}'],do_unlink=True);lod=mesh.copy();lod.data=mesh.data.copy();lod.name=f'SK_{uid}_LOD{level}';bpy.data.collections['LOD_SOURCE'].objects.link(lod);bpy.context.view_layer.objects.active=lod;mod=lod.modifiers.new('WC_SilhouetteReduction','DECIMATE');mod.ratio=ratio;bpy.ops.object.modifier_apply(modifier=mod.name);clean(lod);export_normalized_copy(stage/(lod.name+'.fbx'),[arm,lod],False,export_fbx_raw);lods.append({'lod':level,'triangles':len(lod.data.loop_triangles),'ratio_target':ratio,'visual_acceptance':'pending'});lod.hide_render=True;lod.hide_set(True)
    export_normalized_copy(stage/('SK_'+uid+'.fbx'),[arm,mesh],False,export_fbx_raw);arm.data.pose_position='POSE'
    if info['changed_actions']:
        use_clip(arm,'Attack',unit_id=uid);bpy.context.scene.frame_start=1;bpy.context.scene.frame_end=m['clips']['Attack']['frames'][1];export_normalized_copy(stage/('AN_'+uid+'_Attack.fbx'),[arm,mesh],True,export_fbx_raw)
    use_clip(arm,'Idle',unit_id=uid);assert invariants(arm)==info['after_invariants'];bpy.ops.wm.save_as_mainfile(filepath=str(source),check_existing=False)
    for p in stage.glob('*.fbx'):shutil.copy2(p,out/p.name)
    shutil.copy2(report/'three-quarter.png',out/'portrait.png');mesh.data.calc_loop_triangles();m.update({'source_revision':8,'geometry_source_revision':8,'animation_revision':7 if uid=='wc_u_elf_rogue' else m['animation_revision'],'source_sha256':sha(source),'triangles':len(mesh.data.loop_triangles),'lods':lods,'update_refinement_script_sha256':sha(report/'executed-repair.py'),'update_export_script_sha256':sha(report/'executed-publish.py'),'update_refinement_evidence':str(report),'shoulder_repair':{'changed_actions':info['changed_actions'],'source_action_hashes':info['after_action_hashes'],'boundary':info['Sylas_motion_boundary']},'files':{p.name:sha(p) for p in out.iterdir() if p.is_file() and p.name!='export_manifest.json'}});(out/'export_manifest.json').write_text(json.dumps(m,indent=2)+'\n');(report/'published-result.json').write_text(json.dumps({'status':'ELF_SOURCE8_EXPORTED_PENDING_FRESH_VERIFICATION','unit_id':uid,'source_sha256':sha(source),'manifest_sha256':sha(out/'export_manifest.json'),'triangles':m['triangles'],'lods':lods,'changed_actions':info['changed_actions']},indent=2)+'\n');print('WC_ELF_SLEEVE_PUBLISHED',uid)
p=argparse.ArgumentParser();p.add_argument('--unit',choices=['wc_u_elf_ranger','wc_u_elf_rogue'],required=True);p.add_argument('--report',type=Path,required=True);p.add_argument('--publish',action='store_true');a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);publish(a.unit,a.report.resolve()) if a.publish else candidate(a.unit,a.report.resolve())

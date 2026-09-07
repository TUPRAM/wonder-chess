"""Fresh saved-source checks, actual mesh-FBX readback and optional 1x motion evidence."""
import argparse,hashlib,json,math,runpy,sys
from pathlib import Path
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
p=argparse.ArgumentParser();p.add_argument('--unit',required=True);p.add_argument('--report',type=Path,required=True);p.add_argument('--render-motion',action='store_true');a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);uid=a.unit;report=a.report.resolve();report.mkdir(parents=True,exist_ok=False);out=ROOT/f'exports/heroes/{uid}';source=ROOT/f'art-source/heroes/{uid}/{uid}.blend';m=json.loads((out/'export_manifest.json').read_text());assert sha(source)==m['source_sha256']
for filename,digest in m['files'].items():assert sha(out/filename)==digest,filename
bpy.ops.wm.open_mainfile(filepath=str(source));arm=bpy.data.objects['Armature'];assert len(arm.data.bones)==m['bones'];assert set(m['clips'])=={'Idle','Move','Attack','Active','Hit','Defeat','Victory'};sys.path.insert(0,str(ROOT/'tools/blender'));saved_argv=sys.argv
try:
    for collection in ('EXPORT','LOD_SOURCE'):
        sys.argv=['inspect_scene.py','--','--collection',collection,'--require-skin','--output',str(report/(collection+'-inspection.json'))];runpy.run_path(str(ROOT/'tools/blender/inspect_scene.py'),run_name='__main__')
    sys.argv=['audit_motion.py','--','--unit',uid,'--output',str(report/'motion-invariants.json')];runpy.run_path(str(ROOT/'tools/blender/audit_motion.py'),run_name='__main__')
finally:sys.argv=saved_argv
expected={}
for suffix in ('','_LOD1','_LOD2'):
    mesh=bpy.data.objects['SK_'+uid+suffix];pts=[mesh.matrix_world@v.co for v in mesh.data.vertices];mesh.data.calc_loop_triangles();expected[suffix]={'dimensions_m':[max(v[i] for v in pts)-min(v[i] for v in pts) for i in range(3)],'triangles':len(mesh.data.loop_triangles)}
readbacks=[]
for suffix,spec in expected.items():
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=1;bpy.ops.import_scene.fbx(filepath=str(out/('SK_'+uid+suffix+'.fbx')),use_anim=False)
    meshes=[x for x in bpy.context.scene.objects if x.type=='MESH'];arms=[x for x in bpy.context.scene.objects if x.type=='ARMATURE'];assert len(meshes)==len(arms)==1
    mesh=meshes[0];pts=[mesh.matrix_world@v.co for v in mesh.data.vertices];dimensions=[max(v[i] for v in pts)-min(v[i] for v in pts) for i in range(3)];mesh.data.calc_loop_triangles()
    assert all(abs(x-y)<.001 for x,y in zip(dimensions,spec['dimensions_m'])),(suffix,dimensions,spec)
    assert len(mesh.data.loop_triangles)==spec['triangles'],(suffix,len(mesh.data.loop_triangles),spec['triangles'])
    assert len(arms[0].data.bones)==m['bones'];assert len(mesh.data.uv_layers)==1 and len(mesh.data.materials)==1
    assert all(v.groups for v in mesh.data.vertices);assert all(math.isfinite(c) for p in pts for c in p)
    readbacks.append({'mesh_suffix':suffix,'dimensions_m':dimensions,'triangles':len(mesh.data.loop_triangles),'bones':len(arms[0].data.bones),'materials':len(mesh.data.materials),'uv_layers':len(mesh.data.uv_layers),'weighted_vertices':len(mesh.data.vertices)})
record={'status':'PASS_SAVED_SOURCE_SKIN_MOTION_AND_MESH_FBX_READBACK','unit_id':uid,'source_sha256':sha(source),'manifest_sha256':sha(out/'export_manifest.json'),'source_revision':m['source_revision'],'geometry_revision':m['geometry_source_revision'],'animation_revision':m['animation_revision'],'blender_version':bpy.app.version_string,'files_verified':len(m['files']),'source_clips_verified':7,'mesh_fbx_readbacks':readbacks,'animation_fbx_import_verified':False,'Unreal_import_verified':False,'final_art_accepted':False};(report/'published-verification.json').write_text(json.dumps(record,indent=2)+'\n');print('WC_NEW_HERO_READBACK_PASS '+json.dumps(record),flush=True)
if a.render_motion:
    bpy.ops.wm.open_mainfile(filepath=str(source));scene=bpy.context.scene;arm=bpy.data.objects['Armature'];scene.render.resolution_x=scene.render.resolution_y=384;scene.render.resolution_percentage=100;scene.cycles.samples=4;h=m['height_m'];scene.camera.data.ortho_scale=h*1.60;scene.camera.location=(h*1.6,h*2.8,h*1.55);scene.camera.rotation_euler=(Vector((0,0,h*.54))-scene.camera.location).to_track_quat('-Z','Y').to_euler();sequences=[]
    for clip,spec in m['clips'].items():
        folder=report/'motion-frames'/clip;folder.mkdir(parents=True,exist_ok=False);action=bpy.data.actions[spec['action']];arm.animation_data.action=action;arm.animation_data.action_slot=action.slots[0];frames=list(range(spec['frames'][0],spec['frames'][1],3))
        for index,frame in enumerate(frames):scene.frame_set(frame);scene.render.filepath=str(folder/f'{index:04d}.png');bpy.ops.render.render(write_still=True)
        sequences.append({'clip':clip,'source_fps':60,'sample_step_frames':3,'playback_fps':20,'duration_ms':(spec['frames'][1]-spec['frames'][0])*1000//60,'frame_count':len(frames),'source_frames':frames,'frames_directory':str(folder)});print('WC_NEW_HERO_CLIP_RENDERED '+uid+' '+clip,flush=True)
    assert sha(source)==m['source_sha256'];(report/'motion-sequences.json').write_text(json.dumps({'status':'ACTUAL_RENDERED_REVIEW_SEQUENCES','unit_id':uid,'candidate_sha256':sha(source),'clips':sequences,'render_size':[384,384],'limits':['20 fps samples of authored 60 fps source','No continuous Unreal playback or art acceptance claim']},indent=2)+'\n')

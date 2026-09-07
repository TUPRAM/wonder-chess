"""Actual candidate arm deformation review before the source/export promotion."""
import argparse,hashlib,json,math,sys
from pathlib import Path
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/blender'))
from refine_update_ada import use_clip,components
p=argparse.ArgumentParser();p.add_argument('--unit',required=True);p.add_argument('--candidate',type=Path,required=True);p.add_argument('--report',type=Path,required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);a.report=a.report.resolve();a.candidate=a.candidate.resolve();a.report.mkdir(parents=True,exist_ok=False);bpy.ops.wm.open_mainfile(filepath=str(a.candidate));m=json.loads((a.candidate.parent/'before-export-manifest.json').read_text());scene=bpy.context.scene;arm=bpy.data.objects['Armature'];ob=bpy.data.objects['SK_'+a.unit];h=m['height_m'];scene.render.engine='BLENDER_WORKBENCH';scene.display.shading.light='STUDIO';scene.display.shading.color_type='TEXTURE';scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True;scene.render.resolution_x=scene.render.resolution_y=384;scene.render.resolution_percentage=100;scene.camera.location=(h*1.15,h*3,h*1.2);scene.camera.data.ortho_scale=h*1.46;scene.camera.rotation_euler=(Vector((0,0,h*.54))-scene.camera.location).to_track_quat('-Z','Y').to_euler();rows=[]
for clip,spec in m['clips'].items():
    frames=sorted(set([spec['frames'][0],spec.get('release_frame') or (spec['frames'][1]//4),spec['frames'][1]//2,(spec['frames'][1]*3)//4,spec['frames'][1]]));records=[]
    for frame in range(spec['frames'][0],spec['frames'][1]+1):
        use_clip(arm,clip,frame,unit_id=a.unit);ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh();coords=[ev.matrix_world@v.co for v in mesh.vertices];assert all(math.isfinite(x) for co in coords for x in co);records.append({'frame':frame,'minimum_z_m':min(v.z for v in coords),'bounds_m':[[min(v[i] for v in coords),max(v[i] for v in coords)] for i in range(3)]});ev.to_mesh_clear()
    images=[]
    for frame in frames:
        use_clip(arm,clip,frame,unit_id=a.unit);path=a.report/f'{clip}-{frame:03d}.png';scene.render.filepath=str(path);bpy.ops.render.render(write_still=True);images.append(str(path))
    rows.append({'clip':clip,'frames_evaluated':len(records),'all_frame_bounds':records,'sample_frames':frames,'images':images})
(a.report/'candidate-deformation-review.json').write_text(json.dumps({'status':'ACTUAL_ALL_FRAME_EVALUATION_AND_35_POSE_RENDERS','candidate_sha256':hashlib.sha256(a.candidate.read_bytes()).hexdigest(),'unit_id':a.unit,'clips':rows,'continuous_review':False,'limits':['Workbench material preview','Rendered poses need human/model visual inspection','All-frame finite/bounds evaluation does not certify self-intersection absence']},indent=2)+'\n');print('WC_ELF_CANDIDATE_DEFORMATION_RENDERED',a.unit)

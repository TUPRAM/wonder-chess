"""Fix observed low-LOD duplication and Orla lantern occlusion on saved candidates."""
import argparse,hashlib,json,shutil,sys
from pathlib import Path
import bpy,bmesh
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/blender'))
from refine_update_ada import components,invariants,action_curve_digest
from author_alpha import export_fbx_raw
from normalized_fbx import export_normalized_copy
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
p=argparse.ArgumentParser();p.add_argument('--unit',required=True,choices=['wc_u_human_warrior','wc_u_elf_mage','wc_u_dwarf_priest','wc_u_orc_guardian']);p.add_argument('--report',type=Path,required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);uid=a.unit;out=ROOT/f'exports/heroes/{uid}';source=ROOT/f'art-source/heroes/{uid}/{uid}.blend';report=a.report.resolve();report.mkdir(parents=True,exist_ok=False);m=json.loads((out/'export_manifest.json').read_text());assert sha(source)==m['source_sha256'];assert m['source_revision']=={'wc_u_human_warrior':3,'wc_u_elf_mage':2,'wc_u_dwarf_priest':1,'wc_u_orc_guardian':1}[uid]
shutil.copy2(source,report/'before.blend');shutil.copy2(out/'export_manifest.json',report/'before-export-manifest.json');(report/'executed-refinement.py').write_bytes(Path(__file__).read_bytes());retained=report/'prior-mesh-exports';retained.mkdir()
for file in out.glob('SK_*.fbx'):shutil.copy2(file,retained/file.name)
bpy.ops.wm.open_mainfile(filepath=str(source));scene=bpy.context.scene;arm=bpy.data.objects['Armature'];mesh=bpy.data.objects['SK_'+uid];saved=invariants(arm);actions={c:action_curve_digest(bpy.data.actions[s['action']]) for c,s in m['clips'].items()};h=m['height_m'];changes=[]
parts=[mesh,*list(bpy.data.collections['BODY'].objects),*list(bpy.data.collections['COSTUME'].objects),*list(bpy.data.collections['EQUIPMENT'].objects)]
for part in parts:
    remove=[]
    for poly in part.data.polygons:
        uv=part.data.uv_layers.active.data[poly.loop_start].uv;col=int(uv.x*4)+4*int(uv.y*4)
        if col==0:poly.use_smooth=True
        if uid=='wc_u_dwarf_priest' and col==2:
            verts=[part.data.vertices[i] for i in poly.vertices];zs=[v.co.z/h for v in verts];groups={part.vertex_groups[g.group].name for v in verts for g in v.groups}
            if groups=={'weapon_r'} and min(zs)>=.150 and max(zs)<=.296 and max(zs)-min(zs)>.13:remove.append(poly.index)
    if remove:
        bm=bmesh.new();bm.from_mesh(part.data);bm.faces.ensure_lookup_table();bmesh.ops.delete(bm,geom=[bm.faces[i] for i in remove],context='FACES_ONLY');bm.to_mesh(part.data);bm.free();changes.append({'part':part.name,'removed_opaque_lantern_wall_faces':len(remove)})
def cleanup(ob):
    bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));seen=set();remove=[]
    for face in bm.faces:
        key=tuple(sorted(tuple(round(x,5) for x in v.co) for v in face.verts))
        if key in seen or face.calc_area()<1e-8:remove.append(face)
        else:seen.add(key)
    if remove:bmesh.ops.delete(bm,geom=remove,context='FACES_ONLY')
    bm.to_mesh(ob.data);bm.free();ob.data.calc_loop_triangles();changes.append({'part':ob.name,'removed_duplicate_or_degenerate_faces':len(remove)})
cleanup(mesh);scene.cycles.samples=12;scene.render.resolution_x=scene.render.resolution_y=768
for label,loc in [('front',(0,4,1.8)),('side',(4,0,1.8)),('back',(0,-4,1.8)),('three-quarter',(3,5,2.7))]:
    scene.camera.location=loc;scene.camera.rotation_euler=(Vector((0,0,h*.54))-scene.camera.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(report/(label+'.png'));bpy.ops.render.render(write_still=True)
shutil.copy2(out/'portrait.png',report/'before-portrait.png');shutil.copy2(report/'three-quarter.png',out/'portrait.png');arm.data.pose_position='REST';lods=[]
for level,ratio in ((1,.5),(2,.25)):
    bpy.data.objects.remove(bpy.data.objects[f'SK_{uid}_LOD{level}'],do_unlink=True);lod=mesh.copy();lod.data=mesh.data.copy();lod.name=f'SK_{uid}_LOD{level}';bpy.data.collections['LOD_SOURCE'].objects.link(lod);bpy.context.view_layer.objects.active=lod;mod=lod.modifiers.new('WC_SilhouetteReduction','DECIMATE');mod.ratio=ratio;bpy.ops.object.modifier_apply(modifier=mod.name);cleanup(lod)
    export_normalized_copy(out/(lod.name+'.fbx'),[arm,lod],False,export_fbx_raw);lods.append({'lod':level,'triangles':len(lod.data.loop_triangles),'ratio_target':ratio,'visual_acceptance':'pending'});lod.hide_render=True;lod.hide_set(True)
export_normalized_copy(out/('SK_'+uid+'.fbx'),[arm,mesh],False,export_fbx_raw);arm.data.pose_position='POSE';assert invariants(arm)==saved
for c,spec in m['clips'].items():assert action_curve_digest(bpy.data.actions[spec['action']])==actions[c]
bpy.ops.wm.save_as_mainfile(filepath=str(source),check_existing=False);m.update({'source_revision':m['source_revision']+1,'geometry_source_revision':m['geometry_source_revision']+1,'source_sha256':sha(source),'triangles':len(mesh.data.loop_triangles),'lods':lods,'update_refinement_script_sha256':sha(report/'executed-refinement.py'),'update_refinement_evidence':str(report),'files':{p.name:sha(p) for p in out.iterdir() if p.is_file() and p.name!='export_manifest.json'}});(out/'export_manifest.json').write_text(json.dumps(m,indent=2)+'\n');(report/'refinement-result.json').write_text(json.dumps({'status':'SOURCE_REFINED_PENDING_FRESH_CHECKS','source_sha256':sha(source),'manifest_sha256':sha(out/'export_manifest.json'),'unchanged_actions':actions,'changes':changes},indent=2)+'\n');print('WC_FITTED_NEW_HERO '+uid+' '+json.dumps(changes),flush=True)

"""Add fitted shoulder gussets and supported Neris headpiece to actual saved candidates."""
import argparse,hashlib,json,math,shutil,sys
from pathlib import Path
import bpy,bmesh
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/blender'))
from refine_update_ada import components,invariants,action_curve_digest
from author_alpha import Geometry,make_mesh,export_fbx_raw
from normalized_fbx import export_normalized_copy
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
p=argparse.ArgumentParser();p.add_argument('--unit',required=True,choices=['wc_u_human_warrior','wc_u_elf_mage']);p.add_argument('--report',type=Path,required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);uid=a.unit;out=ROOT/f'exports/heroes/{uid}';source=ROOT/f'art-source/heroes/{uid}/{uid}.blend';report=a.report.resolve();report.mkdir(parents=True,exist_ok=False);m=json.loads((out/'export_manifest.json').read_text());assert sha(source)==m['source_sha256'];assert m['source_revision']==(2 if uid=='wc_u_human_warrior' else 1)
shutil.copy2(source,report/'before.blend');shutil.copy2(out/'export_manifest.json',report/'before-export-manifest.json');(report/'executed-refinement.py').write_bytes(Path(__file__).read_bytes());bpy.ops.wm.open_mainfile(filepath=str(source));scene=bpy.context.scene;arm=bpy.data.objects['Armature'];mesh=bpy.data.objects['SK_'+uid];saved=invariants(arm);actions={c:action_curve_digest(bpy.data.actions[s['action']]) for c,s in m['clips'].items()};u=next(x for x in json.loads((ROOT/'data/units.json').read_text())['units'] if x['id']==uid);h=u['height_m'];g=Geometry();changes=[]
for side,s in [('l',1),('r',-1)]:
    shoulder=arm.data.bones['upperarm_'+side].head_local/h;elbow=arm.data.bones['lowerarm_'+side].head_local/h;radius=.053 if uid=='wc_u_human_warrior' else .043
    g.tube([(shoulder.x*.64,0,shoulder.z-.033),tuple(shoulder),tuple(shoulder.lerp(elbow,.22))],[radius*.90,radius*.93,radius*.96],0,'upperarm_'+side,16,weights=[{'spine_03':1},{'spine_03':.28,'upperarm_'+side:.72},{'upperarm_'+side:1}])
changes.append('Two fitted cloth shoulder gussets with explicit spine-to-arm weights')
if uid=='wc_u_elf_mage':
    for part in [mesh,*list(bpy.data.collections['BODY'].objects),*list(bpy.data.collections['COSTUME'].objects)]:
        for comp in components(part):
            if comp['groups']==['head'] and comp['bounds_min_m'][2]/h>1.0:
                for i in comp['indices']:part.data.vertices[i].co.z-=.070*h
            if comp['groups']==['hand_l'] and comp['bounds_min_m'][2]/h<.35 and comp['count']==21:
                palm=arm.data.bones['hand_l'].tail_local.z/h
                for i in comp['indices']:
                    v=part.data.vertices[i];relative=v.co.z/h-palm
                    if relative<-.01:v.co.z=(palm-.01+(-relative-.01)*.65)*h
    for s in (-1,1):g.tube([(s*.080,-.009,.955),(s*.092,-.009,.974),(s*.119,-.005,.984)],[.013,.012,.014],2,'head',9)
    changes += ['Lowered broken-circle arc and added two visible temple brackets','Curved left fingers upward beneath the supported lens']
extra=make_mesh(g,u,arm,mesh.data.materials[0]);extra.name='COSTUME_Tailoring_'+uid
preserved=extra.copy();preserved.data=extra.data.copy();bpy.data.collections['COSTUME'].objects.link(preserved);preserved.hide_render=True;preserved.hide_set(True)
bpy.ops.object.select_all(action='DESELECT');mesh.select_set(True);extra.select_set(True);bpy.context.view_layer.objects.active=mesh;bpy.ops.object.join();mesh=bpy.context.object
bm=bmesh.new();bm.from_mesh(mesh.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(mesh.data);bm.free();mesh.data.calc_loop_triangles()
scene.cycles.samples=12;scene.render.resolution_x=scene.render.resolution_y=768
for label,loc in [('front',(0,4,1.8)),('side',(4,0,1.8)),('back',(0,-4,1.8)),('three-quarter',(3,5,2.7))]:
    scene.camera.location=loc;scene.camera.rotation_euler=(Vector((0,0,h*.54))-scene.camera.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(report/(label+'.png'));bpy.ops.render.render(write_still=True)
shutil.copy2(out/'portrait.png',report/'before-portrait.png');shutil.copy2(report/'three-quarter.png',out/'portrait.png');arm.data.pose_position='REST';lods=[]
for level,ratio in ((1,.5),(2,.25)):
    bpy.data.objects.remove(bpy.data.objects[f'SK_{uid}_LOD{level}'],do_unlink=True);lod=mesh.copy();lod.data=mesh.data.copy();lod.name=f'SK_{uid}_LOD{level}';bpy.data.collections['LOD_SOURCE'].objects.link(lod);bpy.context.view_layer.objects.active=lod;mod=lod.modifiers.new('WC_SilhouetteReduction','DECIMATE');mod.ratio=ratio;bpy.ops.object.modifier_apply(modifier=mod.name)
    bm=bmesh.new();bm.from_mesh(lod.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(lod.data);bm.free();lod.data.calc_loop_triangles();export_normalized_copy(out/(lod.name+'.fbx'),[arm,lod],False,export_fbx_raw);lods.append({'lod':level,'triangles':len(lod.data.loop_triangles),'ratio_target':ratio,'visual_acceptance':'pending'});lod.hide_render=True;lod.hide_set(True)
export_normalized_copy(out/('SK_'+uid+'.fbx'),[arm,mesh],False,export_fbx_raw);arm.data.pose_position='POSE';assert invariants(arm)==saved
for c,spec in m['clips'].items():assert action_curve_digest(bpy.data.actions[spec['action']])==actions[c]
bpy.ops.wm.save_as_mainfile(filepath=str(source),check_existing=False);m.update({'source_revision':m['source_revision']+1,'geometry_source_revision':m['geometry_source_revision']+1,'source_sha256':sha(source),'triangles':len(mesh.data.loop_triangles),'lods':lods,'update_refinement_script_sha256':sha(report/'executed-refinement.py'),'update_refinement_evidence':str(report),'files':{p.name:sha(p) for p in out.iterdir() if p.is_file() and p.name!='export_manifest.json'}});(out/'export_manifest.json').write_text(json.dumps(m,indent=2)+'\n');(report/'refinement-result.json').write_text(json.dumps({'status':'SOURCE_REFINED_PENDING_FRESH_CHECKS','source_sha256':sha(source),'manifest_sha256':sha(out/'export_manifest.json'),'unchanged_actions':actions,'changes':changes},indent=2)+'\n');print('WC_FITTED_NEW_HERO '+uid,flush=True)

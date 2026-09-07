"""Incrementally fit Cass's eye relief and shoulder construction to his saved source."""
import argparse,hashlib,json,math,shutil,sys
from pathlib import Path
import bpy,bmesh
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/blender'))
from refine_update_ada import components,invariants,action_curve_digest
from author_alpha import export_fbx_raw
from normalized_fbx import export_normalized_copy
UID='wc_u_human_warrior';SOURCE=ROOT/f'art-source/heroes/{UID}/{UID}.blend';OUT=ROOT/f'exports/heroes/{UID}'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
parser=argparse.ArgumentParser();parser.add_argument('--report',type=Path,required=True);a=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);report=a.report.resolve();report.mkdir(parents=True,exist_ok=False)
before=json.loads((OUT/'export_manifest.json').read_text());assert before['source_revision']==1 and sha(SOURCE)==before['source_sha256'];shutil.copy2(SOURCE,report/'before.blend');shutil.copy2(OUT/'export_manifest.json',report/'before-export-manifest.json');(report/'executed-refinement.py').write_bytes(Path(__file__).read_bytes())
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));arm=bpy.data.objects['Armature'];saved=invariants(arm);actions={c:action_curve_digest(bpy.data.actions[s['action']]) for c,s in before['clips'].items()};height=before['height_m'];changes=[]
for mesh in [bpy.data.objects['SK_'+UID],*list(bpy.data.collections['BODY'].objects),*list(bpy.data.collections['COSTUME'].objects)]:
    colors={}
    for poly in mesh.data.polygons:
        uv=mesh.data.uv_layers.active.data[poly.loop_start].uv;col=int(uv.x*4)+4*int(uv.y*4)
        for i in poly.vertices:colors[i]=col
    for comp in components(mesh):
        center=[x/height for x in comp['center_m']];indices=comp['indices'];col=colors[indices[0]]
        if comp['groups']==['head'] and .900<center[2]<.919 and col in (8,9,15):
            cy=sum(mesh.data.vertices[i].co.y for i in indices)/len(indices)/height;relief={8:.0025,9:.0035,15:.0045}[col]
            for i in indices:
                v=mesh.data.vertices[i];x=v.co.x/height;v.co.y=(.006+.079*math.sqrt(max(.01,1-(x/.081)**2))+relief+(v.co.y/height-cy)*.15)*height
                if col==8:v.co.z=(.908+(v.co.z/height-.908)*.85)*height
            changes.append({'object':mesh.name,'part':'fitted_eye_relief','vertices':len(indices),'palette':col})
        if comp['groups']==['clavicle_l'] and center[2]>.76 and col==4:
            for i in indices:
                v=mesh.data.vertices[i];v.co.z=(.780+(v.co.z/height-.780)*.72)*height
                mesh.vertex_groups['clavicle_l'].remove([i]);mesh.vertex_groups['clavicle_l'].add([i],.18,'REPLACE');mesh.vertex_groups['upperarm_l'].add([i],.82,'REPLACE')
            changes.append({'object':mesh.name,'part':'supported_shoulder_guard','vertices':len(indices)})
        if comp['count']==42 and any(x.startswith('upperarm_') for x in comp['groups']) and 'spine_03' in comp['groups']:
            side='l' if center[0]>0 else 'r';first=indices[:14];c=sum((mesh.data.vertices[i].co for i in first),Vector())/len(first)
            for i in first:
                v=mesh.data.vertices[i];v.co=c+(v.co-c)*1.28
            for i in indices:
                for group in list(mesh.data.vertices[i].groups):mesh.vertex_groups[group.group].remove([i])
                mesh.vertex_groups['upperarm_'+side].add([i],.80,'REPLACE');mesh.vertex_groups['clavicle_'+side].add([i],.20,'REPLACE')
            changes.append({'object':mesh.name,'part':'sleeve_cap_contour','side':side,'vertices':len(indices)})
    mesh.data.update()
mesh=bpy.data.objects['SK_'+UID];scene=bpy.context.scene;scene.cycles.samples=12;scene.render.resolution_x=scene.render.resolution_y=768
for label,loc in [('front',(0,4,1.8)),('side',(4,0,1.8)),('back',(0,-4,1.8)),('three-quarter',(3,5,2.7))]:
    scene.camera.location=loc;scene.camera.rotation_euler=(Vector((0,0,height*.54))-scene.camera.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(report/(label+'.png'));bpy.ops.render.render(write_still=True)
shutil.copy2(OUT/'portrait.png',report/'before-portrait.png');shutil.copy2(report/'three-quarter.png',OUT/'portrait.png')
arm.data.pose_position='REST';lods=[]
for level,ratio in ((1,.5),(2,.25)):
    old=bpy.data.objects[f'SK_{UID}_LOD{level}'];bpy.data.objects.remove(old,do_unlink=True);lod=mesh.copy();lod.data=mesh.data.copy();lod.name=f'SK_{UID}_LOD{level}';bpy.data.collections['LOD_SOURCE'].objects.link(lod);bpy.context.view_layer.objects.active=lod;mod=lod.modifiers.new('WC_SilhouetteReduction','DECIMATE');mod.ratio=ratio;bpy.ops.object.modifier_apply(modifier=mod.name)
    bm=bmesh.new();bm.from_mesh(lod.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(lod.data);bm.free();lod.data.calc_loop_triangles();export_normalized_copy(OUT/(lod.name+'.fbx'),[arm,lod],False,export_fbx_raw);lods.append({'lod':level,'triangles':len(lod.data.loop_triangles),'ratio_target':ratio,'visual_acceptance':'pending'});lod.hide_render=True;lod.hide_set(True)
export_normalized_copy(OUT/('SK_'+UID+'.fbx'),[arm,mesh],False,export_fbx_raw);arm.data.pose_position='POSE';assert invariants(arm)==saved
for c,spec in before['clips'].items():assert action_curve_digest(bpy.data.actions[spec['action']])==actions[c]
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE),check_existing=False);before.update({'source_revision':2,'geometry_source_revision':2,'source_sha256':sha(SOURCE),'lods':lods,'update_refinement_script_sha256':sha(report/'executed-refinement.py'),'update_refinement_evidence':str(report),'files':{p.name:sha(p) for p in OUT.iterdir() if p.is_file() and p.name!='export_manifest.json'}});(OUT/'export_manifest.json').write_text(json.dumps(before,indent=2)+'\n');(report/'refinement-result.json').write_text(json.dumps({'status':'SOURCE_REFINED_PENDING_FRESH_CHECKS','source_sha256':sha(SOURCE),'manifest_sha256':sha(OUT/'export_manifest.json'),'unchanged_actions':actions,'changes':changes},indent=2)+'\n');print('WC_CASS_REFINEMENT_RENDERED '+json.dumps(changes),flush=True)

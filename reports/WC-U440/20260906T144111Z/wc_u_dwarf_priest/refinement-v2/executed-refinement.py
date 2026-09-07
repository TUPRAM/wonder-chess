"""Replace intersecting sleeve caps, complete the cloth hood and repair lantern posts."""
import argparse,hashlib,json,math,shutil,sys
from pathlib import Path
import bpy,bmesh
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/blender'))
from refine_update_ada import components,invariants,action_curve_digest
from author_alpha import Geometry,make_mesh,export_fbx_raw
from normalized_fbx import export_normalized_copy
UID='wc_u_dwarf_priest';SOURCE=ROOT/f'art-source/heroes/{UID}/{UID}.blend';OUT=ROOT/f'exports/heroes/{UID}'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
p=argparse.ArgumentParser();p.add_argument('--report',type=Path,required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);report=a.report.resolve();report.mkdir(parents=True,exist_ok=False);m=json.loads((OUT/'export_manifest.json').read_text());assert m['source_revision']==2 and sha(SOURCE)==m['source_sha256'];shutil.copy2(SOURCE,report/'before.blend');shutil.copy2(OUT/'export_manifest.json',report/'before-export-manifest.json');(report/'executed-refinement.py').write_bytes(Path(__file__).read_bytes());bpy.ops.wm.open_mainfile(filepath=str(SOURCE));arm=bpy.data.objects['Armature'];mesh=bpy.data.objects['SK_'+UID];saved=invariants(arm);u=next(x for x in json.loads((ROOT/'data/units.json').read_text())['units'] if x['id']==UID);h=u['height_m'];changes=[]
for part in [mesh,*list(bpy.data.collections['COSTUME'].objects)]:
    remove=set()
    for comp in components(part):
        groups=set(comp['groups'])
        for side in ('l','r'):
            if 'upperarm_'+side in groups and groups <= {'upperarm_'+side,'lowerarm_'+side,'clavicle_'+side,'spine_03'}:remove.update(comp['indices'])
    if remove:
        bm=bmesh.new();bm.from_mesh(part.data);bm.verts.ensure_lookup_table();bmesh.ops.delete(bm,geom=[bm.verts[i] for i in sorted(remove)],context='VERTS');bm.to_mesh(part.data);bm.free();changes.append({'object':part.name,'removed_intersecting_cap_sleeve_vertices':len(remove)})
g=Geometry()
for side,s in [('l',1),('r',-1)]:
    sh=arm.data.bones['upperarm_'+side].head_local/h;el=arm.data.bones['lowerarm_'+side].head_local/h;wr=arm.data.bones['hand_'+side].head_local/h;r=.077
    pts=[(sh.x*.57,0,sh.z-.032),(sh.x*.80,0,sh.z+.006),tuple(sh.lerp(el,.12)),tuple(sh.lerp(el,.40)),tuple(sh.lerp(el,.76)),tuple(el),tuple(el.lerp(wr,.32)),tuple(el.lerp(wr,.73)),tuple(wr)]
    weights=[{'spine_03':1},{'spine_03':.62,'upperarm_'+side:.38},{'spine_03':.12,'upperarm_'+side:.88},{'upperarm_'+side:1},{'upperarm_'+side:.85,'lowerarm_'+side:.15},{'upperarm_'+side:.5,'lowerarm_'+side:.5},{'lowerarm_'+side:1},{'lowerarm_'+side:1},{'lowerarm_'+side:1}]
    g.tube(pts,[r*.86,r*.95,r,r*.93,r*.79,r*.69,r*.81,r*.66,r*.50],0,'upperarm_'+side,20,weights=weights)
# Closed padded hood shell around the back and sides, open at the adult face.
sections=[(.846,.102,.079),(.914,.126,.099),(.969,.115,.098),(1.017,.074,.061),(1.034,.013,.018)];verts=[];faces=[];count=17
for inner in (False,True):
    for z,rx,ry in sections:
        for j in range(count):
            ang=math.pi+j*math.pi/(count-1);verts.append(((rx-(.007 if inner else 0))*math.cos(ang),-.033+(ry-(.007 if inner else 0))*math.sin(ang),z-(.005 if inner else 0)))
n=len(sections)*count
for row in range(len(sections)-1):
    for j in range(count-1):
        i=row*count+j;faces += [(i,i+1,i+1+count,i+count),(n+i+count,n+i+count+1,n+i+1,n+i)]
boundary=list(range(count))+[r*count+count-1 for r in range(1,len(sections))]+list(range(n-2,n-count-1,-1))+[r*count for r in range(len(sections)-2,0,-1)]
for x,y in zip(boundary,boundary[1:]+boundary[:1]):faces.append((x,y,n+y,n+x))
g.add(verts,faces,0,'head');right=arm.data.bones['hand_r'].tail_local/h
for j in range(8):
    angle=j*math.pi/4;x=right.x+.107*math.cos(angle);y=right.y+.094*math.sin(angle);g.tube([(x,y,right.z-.223),(x,y,right.z-.083)],[.0085,.0085],2,'weapon_r',7)
extra=make_mesh(g,u,arm,mesh.data.materials[0]);extra.name='Orla_Hood_Sleeves_Lantern_Posts';part=extra.copy();part.data=extra.data.copy();bpy.data.collections['COSTUME'].objects.link(part);part.hide_render=True;part.hide_set(True);bpy.ops.object.select_all(action='DESELECT');mesh.select_set(True);extra.select_set(True);bpy.context.view_layer.objects.active=mesh;bpy.ops.object.join();mesh=bpy.context.object
def cleanup(ob):
    bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));seen=set();remove=[]
    for face in bm.faces:
        key=tuple(sorted(tuple(round(x,5) for x in v.co) for v in face.verts))
        if key in seen or face.calc_area()<1e-8:remove.append(face)
        else:seen.add(key)
    if remove:bmesh.ops.delete(bm,geom=remove,context='FACES_ONLY')
    bm.to_mesh(ob.data);bm.free();ob.data.calc_loop_triangles()
    for poly in ob.data.polygons:
        uv=ob.data.uv_layers.active.data[poly.loop_start].uv
        if int(uv.x*4)+4*int(uv.y*4)==0:poly.use_smooth=True
cleanup(mesh);scene=bpy.context.scene;scene.cycles.samples=12;scene.render.resolution_x=scene.render.resolution_y=768
for label,loc in [('front',(0,4,1.8)),('side',(4,0,1.8)),('back',(0,-4,1.8)),('three-quarter',(3,5,2.7))]:
    scene.camera.location=loc;scene.camera.rotation_euler=(Vector((0,0,h*.54))-scene.camera.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(report/(label+'.png'));bpy.ops.render.render(write_still=True)
shutil.copy2(OUT/'portrait.png',report/'before-portrait.png');shutil.copy2(report/'three-quarter.png',OUT/'portrait.png');arm.data.pose_position='REST';lods=[]
for level,ratio in ((1,.5),(2,.25)):
    bpy.data.objects.remove(bpy.data.objects[f'SK_{UID}_LOD{level}'],do_unlink=True);lod=mesh.copy();lod.data=mesh.data.copy();lod.name=f'SK_{UID}_LOD{level}';bpy.data.collections['LOD_SOURCE'].objects.link(lod);bpy.context.view_layer.objects.active=lod;mod=lod.modifiers.new('WC_SilhouetteReduction','DECIMATE');mod.ratio=ratio;bpy.ops.object.modifier_apply(modifier=mod.name);cleanup(lod);export_normalized_copy(OUT/(lod.name+'.fbx'),[arm,lod],False,export_fbx_raw);lods.append({'lod':level,'triangles':len(lod.data.loop_triangles),'ratio_target':ratio,'visual_acceptance':'pending'});lod.hide_render=True;lod.hide_set(True)
export_normalized_copy(OUT/('SK_'+UID+'.fbx'),[arm,mesh],False,export_fbx_raw);arm.data.pose_position='POSE';assert invariants(arm)==saved;bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE),check_existing=False);m.update({'source_revision':3,'geometry_source_revision':3,'source_sha256':sha(SOURCE),'triangles':len(mesh.data.loop_triangles),'lods':lods,'update_refinement_script_sha256':sha(report/'executed-refinement.py'),'update_refinement_evidence':str(report),'files':{p.name:sha(p) for p in OUT.iterdir() if p.is_file() and p.name!='export_manifest.json'}});(OUT/'export_manifest.json').write_text(json.dumps(m,indent=2)+'\n');(report/'refinement-result.json').write_text(json.dumps({'status':'SOURCE_REFINED_PENDING_FRESH_CHECKS','source_sha256':sha(SOURCE),'manifest_sha256':sha(OUT/'export_manifest.json'),'changes':changes+['continuous tailored sleeves','closed padded travel hood','eight lantern posts']},indent=2)+'\n');print('WC_ORLA_CONSTRUCTION_REPAIRED',flush=True)

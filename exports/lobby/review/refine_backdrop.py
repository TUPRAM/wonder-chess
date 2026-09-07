"""Preserve candidate one, ground its beacon and frame the complete authored backdrop."""
import hashlib,json,math,shutil,sys
from pathlib import Path
import bpy,bmesh
from mathutils import Vector
ROOT=Path('C:/Users/iputu/Documents/Wonder Chess')
sys.path.insert(0,str(ROOT/'tools/blender'))
from author_alpha import Geometry,export_fbx_raw
from normalized_fbx import export_normalized_copy
OUT=ROOT/'exports/lobby'; REVIEW=OUT/'review'; SOURCE=ROOT/'art-source/lobby/brighthaven_approach.blend'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
old=json.loads((OUT/'lobby_manifest.json').read_text());assert sha(SOURCE)==old['source_sha256']
archive=REVIEW/'revision1';archive.mkdir(exist_ok=False)
for p in [SOURCE,ROOT/'tools/blender/author_brighthaven_approach.py',OUT/'lobby_manifest.json',*OUT.glob('*.fbx'),*OUT.glob('*.png'),*REVIEW.glob('*.png')]:shutil.copy2(p,archive/p.name)
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));scene=bpy.context.scene
beacon=bpy.data.objects['SM_WC_ApproachBeacon']
for vertex in beacon.data.vertices:vertex.co.z*=.78
platform=bpy.data.objects['SM_WC_ApproachPlatform'];g=Geometry()
g.plate([(-1.5,-.31),(1.5,-.31),(1.5,-.01),(-1.5,-.01)],-6.35,2.0,0,'root',.04)
data=platform.data; vertices=[tuple(v.co) for v in data.vertices];faces=[tuple(p.vertices) for p in data.polygons];uvs=[tuple(x.uv) for x in data.uv_layers.active.data];offset=len(vertices)
new=bpy.data.meshes.new(platform.name+'_Grounded');new.from_pydata(vertices+g.vertices,[],faces+[tuple(i+offset for i in f) for f in g.faces]);new.update();uv=new.uv_layers.new(name='BrighthavenAtlas')
for i,value in enumerate(uvs):uv.data[i].uv=value
for face,col in zip(list(new.polygons)[len(faces):],g.colors):
    for li in face.loop_indices:
        v=new.vertices[new.loops[li].vertex_index].co;uv.data[li].uv=((col%4+.18+.64*((v.x+v.y)*.5%1))/4,(col//4+.18+.64*(v.z*.5%1))/4)
bm=bmesh.new();bm.from_mesh(new);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(new);bm.free();new.materials.append(data.materials[0]);platform.data=new
modules=[bpy.data.objects[name] for name in old['modules']]
for module in modules:export_normalized_copy(OUT/(module.name+'.fbx'),[module],False,export_fbx_raw)
for name in [x['mesh'] for x in old['lods']]:bpy.data.objects.remove(bpy.data.objects[name],do_unlink=True)
bpy.ops.object.select_all(action='DESELECT');copies=[]
for module in modules:
    ob=module.copy();ob.data=module.data.copy();scene.collection.objects.link(ob);ob.select_set(True);copies.append(ob)
bpy.context.view_layer.objects.active=copies[0];bpy.ops.object.join();combined=bpy.context.object;combined.name='SM_WC_BrighthavenApproach';combined.data.name=combined.name
lods=[]
for level,ratio in ((0,1),(1,.5),(2,.25)):
    ob=combined if level==0 else combined.copy()
    if level:
        ob.data=combined.data.copy();scene.collection.objects.link(ob);ob.name=combined.name+'_LOD'+str(level);bpy.context.view_layer.objects.active=ob;mod=ob.modifiers.new('Measured_LOD','DECIMATE');mod.ratio=ratio;bpy.ops.object.modifier_apply(modifier=mod.name)
    ob.data.calc_loop_triangles();export_normalized_copy(OUT/(ob.name+'.fbx'),[ob],False,export_fbx_raw);lods.append({'level':level,'mesh':ob.name,'triangles':len(ob.data.loop_triangles)});ob.hide_render=True;ob.hide_set(True)
scene.camera.data.ortho_scale=18.0
for label,location,target in [('approach-front',(0,15,7),(0,-2,1.75)),('approach-three-quarter',(11,15,10),(0,-2,1.5)),('approach-back',(0,-18,9),(0,-2,1.75))]:
    scene.camera.location=location;scene.camera.rotation_euler=(Vector(target)-scene.camera.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(REVIEW/(label+'.png'));bpy.ops.render.render(write_still=True)
scene.camera.location=(0,15,7);scene.camera.rotation_euler=(Vector((0,-2,1.75))-scene.camera.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE),check_existing=False)
for suffix in ('BaseColor','Normal','ORM'):shutil.copy2(OUT/f'T_wc_brighthaven_approach_{suffix}.png',OUT/f'{suffix}.png')
points=[v.co for v in combined.data.vertices];old.update({'source_sha256':sha(SOURCE),'source_revision':2,'refinement_script_sha256':sha(Path(__file__)),'prior_candidate':str(archive),'lods':lods,'bounds':{'min_m':[min(v[i] for v in points) for i in range(3)],'max_m':[max(v[i] for v in points) for i in range(3)]},'files':{p.name:sha(p) for p in OUT.iterdir() if p.is_file() and p.name!='lobby_manifest.json'}})
(OUT/'lobby_manifest.json').write_text(json.dumps(old,indent=2)+'\n');print('WC_LOBBY_REVISION_2 '+json.dumps(lods),flush=True)

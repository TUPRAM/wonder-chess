import bpy,json,hashlib,sys
from pathlib import Path
from mathutils import Vector
ROOT=Path('C:/Users/iputu/Documents/Wonder Chess');sys.path.insert(0,str(ROOT/'tools/blender'))
from refine_update_ada import components,invariants,use_clip
UID='wc_u_human_warrior';out=Path(__file__).parent;source=ROOT/f'art-source/heroes/{UID}/{UID}.blend';before=hashlib.sha256(source.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(source));arm=bpy.data.objects['Armature'];use_clip(arm,'Idle',unit_id=UID);mesh=bpy.data.objects['SK_'+UID];col={}
for p in mesh.data.polygons:
 uv=mesh.data.uv_layers.active.data[p.loop_start].uv
 for i in p.vertices:col[i]=int(uv.x*4)+4*int(uv.y*4)
result=[{k:v for k,v in c.items() if k!='indices'}|{'palette':col[c['indices'][0]]} for c in components(mesh) if c['groups']==['head']];(out/'source4-face-components.json').write_text(json.dumps(result,indent=2)+'\n');(out/'source4-invariants.json').write_text(json.dumps(invariants(arm),indent=2)+'\n')
scene=bpy.context.scene;scene.cycles.samples=12;scene.render.resolution_x=scene.render.resolution_y=768
for name,loc in [('before-face',(0,4,1.85)),('before-face-three-quarter',(2.5,4,1.95))]:
 scene.camera.data.ortho_scale=.62;scene.camera.location=loc;scene.camera.rotation_euler=(Vector((0,.02,1.73))-scene.camera.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
assert hashlib.sha256(source.read_bytes()).hexdigest()==before;print('WC_CASS4_READ_ONLY '+before)

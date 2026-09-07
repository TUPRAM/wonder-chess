import bpy,json,sys,hashlib
from pathlib import Path
from mathutils import Vector
ROOT=Path('C:/Users/iputu/Documents/Wonder Chess');sys.path.insert(0,str(ROOT/'tools/blender'))
from refine_update_ada import components,invariants,use_clip
uid='wc_u_human_guardian';source=ROOT/f'art-source/heroes/{uid}/{uid}.blend';out=Path(__file__).parent/'inspection8';out.mkdir(parents=True,exist_ok=False)
before=hashlib.sha256(source.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(source));arm=bpy.data.objects['Armature'];use_clip(arm,'Idle');scene=bpy.context.scene;scene.cycles.samples=12;scene.render.resolution_x=scene.render.resolution_y=768
records={}
for ob in bpy.data.objects:
 if ob.type!='MESH' or (ob.name!='SK_'+uid and not ob.name.startswith(('BODY_','COSTUME_','EQUIPMENT_'))):continue
 color={}
 for p in ob.data.polygons:
  uv=ob.data.uv_layers.active.data[p.loop_start].uv
  for i in p.vertices:color[i]=int(uv.x*4)+4*int(uv.y*4)
 records[ob.name]=[{k:v for k,v in c.items() if k!='indices'}|{'palette':sorted(set(color.get(i) for i in c['indices']))} for c in components(ob)]
(out/'components.json').write_text(json.dumps(records,indent=2)+'\n');(out/'source-invariants.json').write_text(json.dumps(invariants(arm),indent=2)+'\n')
for label,location,target,size in [('front',(0,5,1.45),(0,0,.97),2.5),('side',(5,0,1.45),(0,0,.97),2.5),('back',(0,-5,1.45),(0,0,.97),2.5),('three-quarter',(3,5,2.7),(0,0,.97),2.5),('face',(0,4,1.75),(0,.02,1.635),.55),('face-three-quarter',(2.5,4,1.83),(0,.02,1.635),.58),('sword-grip',(-2,4,1.4),(-.61,.21,.73),.6),('shield-rear',(2,-4,1.4),(.57,.25,1),.75)]:
 scene.camera.data.ortho_scale=size;scene.camera.location=location;scene.camera.rotation_euler=(Vector(target)-scene.camera.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(out/(label+'.png'));bpy.ops.render.render(write_still=True)
assert hashlib.sha256(source.read_bytes()).hexdigest()==before
print('WC_ADA_SOURCE8_ACTUALLY_INSPECTED '+before)

"""Read-only close inspection of the frozen Neris, Orla or Tala source asset."""
import argparse,hashlib,json,sys
from pathlib import Path
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/blender'))
from refine_update_ada import components,invariants,use_clip
p=argparse.ArgumentParser();p.add_argument('--unit',choices=['wc_u_elf_mage','wc_u_dwarf_priest','wc_u_orc_guardian'],required=True);p.add_argument('--report',type=Path,required=True)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);report=a.report.resolve();report.mkdir(parents=True,exist_ok=False)
source=ROOT/f'art-source/heroes/{a.unit}/{a.unit}.blend';before=hashlib.sha256(source.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(source));arm=bpy.data.objects['Armature'];mesh=bpy.data.objects['SK_'+a.unit];use_clip(arm,'Idle',unit_id=a.unit)
colors={}
for poly in mesh.data.polygons:
    uv=mesh.data.uv_layers.active.data[poly.loop_start].uv
    for i in poly.vertices:colors[i]=int(uv.x*4)+4*int(uv.y*4)
parts=[]
for c in components(mesh):
    if c['groups']==['head']:
        c['palette']=colors[c['indices'][0]];c['dimensions_m']=[hi-lo for hi,lo in zip(c['bounds_max_m'],c['bounds_min_m'])];c.pop('indices');parts.append(c)
head=max((c for c in parts if c['palette']==6),key=lambda c:c['dimensions_m'][0]*c['dimensions_m'][1]*c['dimensions_m'][2])
z=head['center_m'][2];size=max(head['dimensions_m'])*2.08
(report/'face-components.json').write_text(json.dumps({'source_sha256':before,'unit_id':a.unit,'parts':parts,'invariants':invariants(arm),'head':head},indent=2)+'\n')
(report/'executed-inspection.py').write_bytes(Path(__file__).read_bytes())
scene=bpy.context.scene;scene.cycles.samples=12;scene.render.resolution_x=scene.render.resolution_y=768
for name,loc in [('face',(0,4,z+.14)),('face-three-quarter',(2.5,4,z+.18))]:
    scene.camera.data.ortho_scale=size;scene.camera.location=loc;scene.camera.rotation_euler=(Vector((0,.01,z+.018))-scene.camera.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(report/(name+'.png'));bpy.ops.render.render(write_still=True)
assert hashlib.sha256(source.read_bytes()).hexdigest()==before
print('WC_READONLY_FACE_INSPECTION_COMPLETE',a.unit)

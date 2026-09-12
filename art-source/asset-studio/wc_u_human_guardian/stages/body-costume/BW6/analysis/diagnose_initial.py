"""Disposable, read-only decomposition of BW6 initial collar/waist defects."""
from pathlib import Path
import bpy, json, hashlib
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parent
SOURCE=ROOT.parent/'armor/ada_bw6_torso_initial.blend'
bpy.ops.wm.open_mainfile(filepath=str(SOURCE),use_scripts=False)
s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s;s.frame_set(1)
dg=bpy.context.evaluated_depsgraph_get()
def geometry(o):
 e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh()
 vs=[e.matrix_world@v.co for v in m.vertices];fs=[tuple(p.vertices) for p in m.polygons]
 e.to_mesh_clear();return vs,fs,BVHTree.FromPolygons(vs,fs)
def scan(bv):
 out=[]
 for z in [1.08,1.12,1.16,1.20,1.25,1.30,1.35,1.40,1.45,1.48]:
  for x in [0,.05,.10,.13,.15,.17]:
   h=bv.ray_cast(Vector((x,1,z)),Vector((0,-1,0)),2)
   if h[0] is not None:out.append({'x':x,'z':z,'y':h[0].y,'face':h[2]})
 return out
report={'source':str(SOURCE),'sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'frame':1,'objects':{},'source_saved':False}
for name in ['BW6_PaddedCoat_Tailored','BW6_FrontPlate','BW6_NavyWaist','BW4_CONTEXT_BW1_IndexedBody']:
 o=bpy.data.objects[name]
 rec={'matrix_world':[list(r) for r in o.matrix_world],'base_vertices':len(o.data.vertices),'base_faces':len(o.data.polygons),'modifiers':[], 'stages':{}}
 for m in o.modifiers:
  r={'name':m.name,'type':m.type,'viewport':m.show_viewport}
  for p in ['thickness','offset','use_even_offset','levels','render_levels','object']:
   if hasattr(m,p):
    v=getattr(m,p);r[p]=v.name if hasattr(v,'name') else v
  rec['modifiers'].append(r)
 active=[m for m in o.modifiers if m.show_viewport]
 for stage in ['evaluated','without_armature','base']:
  for m in o.modifiers:m.show_viewport=(m in active and (stage=='evaluated' or (stage=='without_armature' and m.type!='ARMATURE')))
  bpy.context.view_layer.update()
  vs,fs,bv=geometry(o)
  rec['stages'][stage]={'vertices':len(vs),'faces':len(fs),'bounds':[[min(v[k] for v in vs) for k in range(3)],[max(v[k] for v in vs) for k in range(3)]],'front_rays':scan(bv)}
  if stage=='base' and 'Coat' in name:
   selected=[]
   for p in o.data.polygons:
    coords=[vs[i] for i in p.vertices]
    if any(.10<abs(v.x)<.18 and 1.075<v.z<1.27 and v.y>0 for v in coords):
     selected.append({'face':p.index,'vertices':list(p.vertices),'world':[list(v) for v in coords], 'weights':[[[o.vertex_groups[g.group].name,g.weight] for g in o.data.vertices[i].groups] for i in p.vertices]})
   rec['lower_front_faces']=selected
 for m in o.modifiers:m.show_viewport=m in active
 report['objects'][name]=rec
body=bpy.data.objects['BW4_CONTEXT_BW1_IndexedBody']
vs,fs,bv=geometry(body)
report['lateral_body_ray_diagnosis']=[]
for x,z in [(.13696009,1.221140),(.14740306,1.229417),(.15001811,1.247699),(.14263922,1.241533)]:
 start=Vector((x,1,z));hits=[]
 for _ in range(8):
  h=bv.ray_cast(start,Vector((0,-1,0)),2)
  if h[0] is None:break
  hits.append({'point':list(h[0]),'normal':list(h[1]),'face':h[2]})
  start=h[0]+Vector((0,-.00001,0))
 report['lateral_body_ray_diagnosis'].append({'x':x,'z':z,'hits':hits})
(ROOT/'initial_decomposition.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print('WROTE initial_decomposition.json; source not saved')

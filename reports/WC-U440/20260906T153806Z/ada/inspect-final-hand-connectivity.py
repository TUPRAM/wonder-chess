import bpy,json,sys,hashlib
from pathlib import Path
ROOT=Path('C:/Users/iputu/Documents/Wonder Chess');sys.path.insert(0,str(ROOT/'tools/blender'))
from refine_update_ada import components,invariants
UID='wc_u_human_guardian';out=Path(__file__).parent;source=ROOT/f'art-source/heroes/{UID}/{UID}.blend';before=hashlib.sha256(source.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(source));mesh=bpy.data.objects['SK_'+UID];col={}
for p in mesh.data.polygons:
 uv=mesh.data.uv_layers.active.data[p.loop_start].uv
 for i in p.vertices:col[i]=int(uv.x*4)+4*int(uv.y*4)
result=[]
for side in ('l','r'):
 groups=[c for c in components(mesh) if c['groups']==['hand_'+side] and col[c['indices'][0]]==6];assert len(groups)==1
 indices=set(groups[0]['indices']);edges={}
 for p in mesh.data.polygons:
  if not set(p.vertices)<=indices:continue
  for i,j in zip(p.vertices,(*p.vertices[1:],p.vertices[0])):
   edge=tuple(sorted((i,j)));edges[edge]=edges.get(edge,0)+1
 assert all(count==2 for count in edges.values())
 result.append({'side':side,'connected_components':1,'vertices':len(indices),'boundary_or_nonmanifold_edges':sum(count!=2 for count in edges.values()),'single_deform_bone':'hand_'+side})
assert hashlib.sha256(source.read_bytes()).hexdigest()==before
(out/'final-hand-connectivity.json').write_text(json.dumps({'status':'PASS_LOCAL_HAND_TOPOLOGY','source_sha256':before,'hands':result,'limits':['Connectivity and manifold edges do not certify close-up art or physical gripping accuracy.']},indent=2)+'\n');print(json.dumps(result))

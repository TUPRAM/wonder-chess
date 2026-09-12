import bpy,json,ast,hashlib,sys
import numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).parent
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
source=Path(args[0]) if args else R.parent/'armor/ada_bw5_armor_initial.blend'
prefix=args[1] if len(args)>1 else 'initial'
bpy.ops.wm.open_mainfile(filepath=str(source),use_scripts=False);s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s;s.frame_set(1)
query=R.parents[1]/'BW2/r001/integrated-independent/audit_integrated_geometry.py';tree=ast.parse(query.read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='segment_triangle'],type_ignores=[]),str(query),'exec'),globals())
def geom(ob):
 ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();me.calc_loop_triangles();v=np.array([ev.matrix_world@v.co for v in me.vertices]);tri=np.array([tuple(t.vertices) for t in me.loop_triangles]);ev.to_mesh_clear();return v,tri,BVHTree.FromPolygons([Vector(p) for p in v],tri,all_triangles=True)
coat=bpy.data.objects['BW4_CONTEXT_BW1_CoatUpper_Continuous'];qb,tb,bb=geom(coat);rows=[]
for name in ['BW4_Breastplate_ControlSurface','BW4_Backplate_ControlSurface','BW4_Front_Neck_Return','BW4_Front_Side_L_Return','BW4_Front_Side_R_Return','BW4_Back_Side_L_Return','BW4_Back_Side_R_Return','BW5_Tailored_Collar','BW5_Navy_Waist_Enclosure']:
 if name not in bpy.data.objects or bpy.data.objects[name].hide_render:continue
 qa,ta,ba=geom(bpy.data.objects[name]);points=[];indices=[]
 for ia,ib in ba.overlap(bb):
  aa=qa[ta[ia]];ab=qb[tb[ib]];pts=[]
  for one,two in [(aa,ab),(ab,aa)]:
   for i in range(3):
    p=segment_triangle(one[i],one[(i+1)%3],two)
    if p is not None:pts.append(p)
  if pts:points.append(np.mean(pts,axis=0).tolist());indices.append([int(ia),int(ib)])
 p=np.array(points);rows.append({'name':name,'pairs':len(points),'bbox_m':[p.min(axis=0).tolist(),p.max(axis=0).tolist()] if len(p) else None,'points':points,'triangle_pairs':indices})
def project(p):
 q=world_to_camera_view(s,bpy.data.objects['BW4_Camera_front'],Vector(p));return [q.x*s.render.resolution_x,(1-q.y)*s.render.resolution_y]
front=bpy.data.objects['BW4_Breastplate_ControlSurface'];v=[front.matrix_world@v.co for v in front.data.vertices];collar=bpy.data.objects.get('BW5_Tailored_Collar');collar=collar if collar is not None and not collar.hide_render else bpy.data.objects['BW4_CONTEXT_BW1_PaddedCollar'];cv,_,_=geom(collar);pv=np.array([project(p) for p in v]);cp=np.array([project(p) for p in cv]);w=float(pv[:,0].max()-pv[:,0].min());n=len(v)//10;ih=9*n+n//2;ib=n//2;H=abs(project(v[ih])[1]-project(v[ib])[1]);c=float(cp[:,0].max()-cp[:,0].min())
belts=[o for o in s.objects if o.type=='MESH' and not o.hide_render and any(x in o.name for x in ['Belt','Buckle'])];beltmeta=[];top=None
for o in belts:
 g,_,_=geom(o);beltmeta.append({'name':o.name,'bounds':[[float(g[:,i].min()),float(g[:,i].max())] for i in range(3)]});sel=g[np.abs(g[:,0])<.04]
 if len(sel):
  q=sel[np.argmax(sel[:,2])];top=q if top is None or q[2]>top[2] else top
u=project(top)[1]-project(v[ib])[1] if top is not None else None
landmarks={'neckline_center_cage':list(v[ih]),'hem_center_cage':list(v[ib]),'plate_width_left':list(v[np.argmin(pv[:,0])]),'plate_width_right':list(v[np.argmax(pv[:,0])]),'belt_center_top':list(top) if top is not None else None}
out={'source':str(source),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'frame':1,'crossings_vs_final_coat':rows,'projected_ratios':{'policy':'Saved BW4 front camera and native 960px frame. Plate cage semantic center hem/neckline and maximal transverse span; collar evaluated maximal exterior width. Waist uses highest evaluated center belt/buckle surface. Screen boundaries may differ from manual source pixels; no independent image stretch.','W_px':w,'H_px':H,'C_px':c,'U_px':u,'H/W':H/w,'C/W':c/w,'U/H':u/H if u is not None else None,'landmarks_m':landmarks,'landmarks_px':{k:project(p) if p else None for k,p in landmarks.items()},'belt_records':beltmeta}}

# Distinguish the intended TOP opening span from any lower flare.
edge_counts={}
for face in collar.data.polygons:
 ids=list(face.vertices)
 for a,b in zip(ids,ids[1:]+ids[:1]):
  key=tuple(sorted((a,b)));edge_counts[key]=edge_counts.get(key,0)+1
adj={}
for (a,b),count in edge_counts.items():
 if count==1:adj.setdefault(a,set()).add(b);adj.setdefault(b,set()).add(a)
seen=set();loops=[]
for seed in adj:
 if seed in seen:continue
 todo=[seed];seen.add(seed);loop=[]
 while todo:
  i=todo.pop();loop.append(i)
  for j in adj[i]-seen:seen.add(j);todo.append(j)
 loops.append(loop)
if loops:
 top_loop=max(loops,key=lambda ids:sum((collar.matrix_world@collar.data.vertices[i].co).z for i in ids)/len(ids))
 top_points=[collar.matrix_world@collar.data.vertices[i].co for i in top_loop];top_px=[project(p) for p in top_points];ct=max(p[0] for p in top_px)-min(p[0] for p in top_px)
 out['projected_ratios']['C_top_opening_cage_px']=ct;out['projected_ratios']['C_top/W']=ct/w
 out['projected_ratios']['top_opening_policy']='Upper open boundary cage loop, maximal projected width; separately from evaluated full-collar silhouette C/W.'
 out['projected_ratios']['collar_top_loop_indices']=top_loop
(R/(prefix+'_fit_diagnosis.json')).write_text(json.dumps(out,indent=2,default=float));print(json.dumps([{k:v for k,v in row.items() if k not in ['points','triangle_pairs']} for row in rows],indent=2));print(json.dumps(out['projected_ratios'],indent=2,default=float))


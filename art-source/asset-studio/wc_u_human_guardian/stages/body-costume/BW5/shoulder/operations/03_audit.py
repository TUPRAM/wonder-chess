import bpy,json,ast,numpy as np,sys,hashlib,itertools
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];args=sys.argv[sys.argv.index('--')+1:];src=R/args[0];label=args[1]
bpy.ops.wm.open_mainfile(filepath=str(src),use_scripts=False);s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s
rig=bpy.data.objects['BW4_Armor_Independent_Rig'];coat=bpy.data.objects['BW4_CONTEXT_BW1_CoatUpper_Continuous'];q=R.parents[1]/'BW2/r001/integrated-independent/audit_integrated_geometry.py'
tree=ast.parse(q.read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='segment_triangle'],type_ignores=[]),str(q),'exec'),globals())
def geom(o,raw=False):
 if raw:
  ev=o;me=o.data;me.calc_loop_triangles();bone=o.get('owner_bone');mat=o.matrix_world
  if bone:mat=rig.matrix_world@rig.pose.bones[bone].matrix@rig.data.bones[bone].matrix_local.inverted()@rig.matrix_world.inverted()@mat
  co=[mat@v.co for v in me.vertices]
 else:
  ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();me.calc_loop_triangles();co=[ev.matrix_world@v.co for v in me.vertices]
 tri=[tuple(t.vertices) for t in me.loop_triangles]
 if not raw:ev.to_mesh_clear()
 return np.array(co),tri,BVHTree.FromPolygons(co,tri,all_triangles=True)
def cross(a,b):
 qa,ta,ba=a;qb,tb,bb=b;out=[]
 for ia,ib in ba.overlap(bb):
  aa=qa[list(ta[ia])];ab=qb[list(tb[ib])];pts=[]
  for one,two in [(aa,ab),(ab,aa)]:
   for i in range(3):
    p=segment_triangle(one[i],one[(i+1)%3],two)
    if p is not None:pts.append(p)
  if pts:out.append({'triangles':[ia,ib],'point_world_m':np.mean(pts,axis=0).tolist()})
 return {'count':len(out),'examples':out[:6]}
names=['BW4_Pauldron_R_'+n for n in ['Cap','Cap_LowerReturn','Lame1','Lame1_LowerReturn','Lame2','Lame2_LowerReturn']]
if 'BW5_SHOULDER_EXPLICIT_ACTIVE' in s:names=json.loads(s['BW5_SHOULDER_EXPLICIT_ACTIVE'])
frames=list(range(1,98)) if len(args)<3 else [1,19,19.5,20,20.5,24.5,25,25.5,37,49,61,73,97]
out=[]
for fr in frames:
 s.frame_set(int(fr),subframe=fr-int(fr));bpy.context.view_layer.update();gc=geom(coat);gs={n:geom(bpy.data.objects[n]) for n in names};raw={n:geom(bpy.data.objects[n],True) for n in names};r={'frame':fr,'evaluated_coat':{n:cross(gs[n],gc) for n in names},'cage_vs_evaluated_coat':{n:cross(raw[n],gc) for n in names},'plate_pairs':{}}
 # Include returns and adjoining shells explicitly, without a generic adjacency exclusion.
 for a,b in itertools.combinations(names,2):r['plate_pairs'][a+' / '+b]=cross(gs[a],gs[b])
 out.append(r)
 if fr in [1,20,25,37,49,61,73,97]:print('AUDIT',fr,{n:x['count'] for n,x in r['evaluated_coat'].items()},flush=True)
summary={}
for category in ['evaluated_coat','cage_vs_evaluated_coat','plate_pairs']:
 summary[category]={n:{'first':next((f['frame'] for f in out if f[category][n]['count']),None),'max':max(f[category][n]['count'] for f in out),'worst_frames':[f['frame'] for f in out if f[category][n]['count']==max(x[category][n]['count'] for x in out)]} for n in out[0][category]}
(R/'records'/f'{label}_audit.json').write_text(json.dumps({'source':str(src),'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'scope':'Noncoplanar transverse triangle screen; raw rigid cage and final evaluated plate vs final evaluated coat; finite samples only, tangency/coplanar/contained regions not certified. Authoring diagnostic only, not game clips.','summary':summary,'frames':out},indent=2))
print(json.dumps(summary,indent=2))

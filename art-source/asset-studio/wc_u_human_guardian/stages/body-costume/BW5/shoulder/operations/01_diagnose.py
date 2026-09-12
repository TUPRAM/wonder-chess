import bpy,json,ast,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1]
B4=R.parents[1]/'BW4/r001/armor'
bpy.ops.wm.open_mainfile(filepath=str(B4/'ada_armor_checkpoint_FINAL_ART_REVISE.blend'),use_scripts=False)
s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s
rig=bpy.data.objects['BW4_Armor_Independent_Rig'];coat=bpy.data.objects['BW4_CONTEXT_BW1_CoatUpper_Continuous']
q=R.parents[1]/'BW2/r001/integrated-independent/audit_integrated_geometry.py'
tree=ast.parse(q.read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='segment_triangle'],type_ignores=[]),str(q),'exec'),globals())
def geom(o):
 ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();me.calc_loop_triangles();co=[ev.matrix_world@v.co for v in me.vertices];tri=[tuple(t.vertices) for t in me.loop_triangles];ev.to_mesh_clear();return np.array(co),tri,BVHTree.FromPolygons(co,tri,all_triangles=True)
def cross(a,b):
 qa,ta,ba=a;qb,tb,bb=b;out=[]
 for ia,ib in ba.overlap(bb):
  aa=qa[list(ta[ia])];ab=qb[list(tb[ib])];pts=[]
  for one,two in [(aa,ab),(ab,aa)]:
   for i in range(3):
    p=segment_triangle(one[i],one[(i+1)%3],two)
    if p is not None:pts.append(p)
  if pts:out.append(np.mean(pts,axis=0).tolist())
 return out
a=Vector((.18184635,-.04636158,1.44498372));axis=(Vector((.36106092,-.04210385,1.24891078))-a).normalized();front=Vector((0,1,0));front=(front-axis*front.dot(axis)).normalized();outer=axis.cross(front)
def local(p):
 d=Vector(p)-a;return [d.dot(axis),d.dot(front),d.dot(outer)]
record={'frame_basis':{'origin':list(a),'axis':list(axis),'front':list(front),'outer':list(outer)},'cages':{},'frames':[]}
names=['BW4_Pauldron_R_'+n for n in ['Cap','Cap_LowerReturn','Lame1','Lame1_LowerReturn','Lame2','Lame2_LowerReturn']]
for nm in names:
 o=bpy.data.objects[nm];record['cages'][nm]={'vertices':[local(o.matrix_world@v.co) for v in o.data.vertices],'polygons':[list(p.vertices) for p in o.data.polygons],'modifiers':[{k:getattr(m,k,None) for k in ['name','type','thickness','offset','levels','show_render']} for m in o.modifiers]}
for fr in [1,20,25,37,49,61,73,85,97]:
 s.frame_set(fr);bpy.context.view_layer.update();gc=geom(coat);bm=rig.matrix_world@rig.pose.bones['upperarm01.R'].matrix@rig.data.bones['upperarm01.R'].matrix_local.inverted()@rig.matrix_world.inverted();di=bm.inverted();rec={'frame':fr,'parts':{}}
 for nm in names:
  pts=cross(geom(bpy.data.objects[nm]),gc);loc=[local(di@Vector(p)) for p in pts];rec['parts'][nm]={'count':len(pts),'points_rest_local':loc,'percentiles':np.percentile(loc,[0,25,50,75,100],axis=0).tolist() if loc else []}
 record['frames'].append(rec);print('DIAG',fr,{n:v['count'] for n,v in rec['parts'].items()},flush=True)
(R/'records/baseline_local_conflicts.json').write_text(json.dumps(record,indent=2))

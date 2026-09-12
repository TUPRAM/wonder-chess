import bpy,json,ast
import numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).parent;S=R.parents[1]/'BW4/r001/armor';source=S/'ada_armor_checkpoint_FINAL_ART_REVISE.blend'
bpy.ops.wm.open_mainfile(filepath=str(source),use_scripts=False);s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s
rig=bpy.data.objects['BW4_Armor_Independent_Rig'];coat=bpy.data.objects['BW4_CONTEXT_BW1_CoatUpper_Continuous']
query=R.parents[1]/'BW2/r001/integrated-independent/audit_integrated_geometry.py';tree=ast.parse(query.read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='segment_triangle'],type_ignores=[]),str(query),'exec'),globals())
def geom(ob):
 ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();me.calc_loop_triangles();v=np.array([ev.matrix_world@v.co for v in me.vertices]);tri=np.array([tuple(t.vertices) for t in me.loop_triangles]);ev.to_mesh_clear();return v,tri,BVHTree.FromPolygons([Vector(p) for p in v],tri,all_triangles=True)
origin=Vector((.18184635,-.04636158,1.44498372));end=Vector((.36106092,-.04210385,1.24891078));axis=(end-origin).normalized();front=Vector((0,1,0));front=(front-axis*front.dot(axis)).normalized();outer=axis.cross(front)
out=[]
for name,frames in [('BW4_Backplate_ControlSurface',[1,29]),('BW4_Pauldron_R_Cap',[1,54]),('BW4_Pauldron_R_Lame2',[20,28])]:
 ob=bpy.data.objects[name];owner=ob['owner_bone'];cage=np.array([v.co for v in ob.data.vertices])
 for fr in frames:
  s.frame_set(fr);bpy.context.view_layer.update();qa,ta,ba=geom(ob);qb,tb,bb=geom(coat);mi=(rig.matrix_world@rig.pose.bones[owner].matrix@rig.data.bones[owner].matrix_local.inverted()@rig.matrix_world.inverted()@ob.matrix_world).inverted();points=[];nearest=[];sectors=[]
  for ia,ib in ba.overlap(bb):
   aa=qa[ta[ia]];ab=qb[tb[ib]];pts=[]
   for one,two in [(aa,ab),(ab,aa)]:
    for i in range(3):
     p=segment_triangle(one[i],one[(i+1)%3],two)
     if p is not None:pts.append(p)
   if pts:
    p=mi@Vector(np.mean(pts,axis=0));points.append(list(p));nearest.append(int(np.argmin(np.sum((cage-np.array(p))**2,axis=1))));d=p-origin;sectors.append([d.dot(axis),d.dot(front),d.dot(outer)])
  pp=np.array(points);ss=np.array(sectors);out.append({'part':name,'frame':fr,'pairs':len(points),'undeformed_bbox_m':[pp.min(axis=0).tolist(),pp.max(axis=0).tolist()],'arm_u_front_out_bbox_m':[ss.min(axis=0).tolist(),ss.max(axis=0).tolist()],'nearest_cage_vertex_histogram':{str(i):nearest.count(i) for i in sorted(set(nearest))},'points_undeformed_m':points})
(R/'bw4_conflict_local_regions.json').write_text(json.dumps({'scope':'Exact noncoplanar crossing means, transformed back from posed rigid owner into undeformed plate coordinates; near cage vertices localize only, not provenance of subdivided faces. Arm frame u distal, front +Y projection, outer axis cross front.','arm_origin':list(origin),'arm_axis':list(axis),'front':list(front),'outer':list(outer),'regions':out},indent=2))
for x in out:print({k:v for k,v in x.items() if k!='points_undeformed_m'},flush=True)

import bpy,json,math,ast
import numpy as np
from pathlib import Path
from mathutils import Vector,Matrix,Quaternion
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];B=R.parents[1]
bpy.ops.wm.open_mainfile(filepath=str(B/'BW5/armor/ada_bw5_armor_checkpoint_r003_ART_REVISE.blend'),use_scripts=False,load_ui=False)
s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s;s.frame_set(1);rig=bpy.data.objects['BW4_Armor_Independent_Rig'];rig.animation_data_clear()
for p in rig.pose.bones:p.matrix_basis=Matrix.Identity(4)
bpy.context.view_layer.update()
rest={n:(rig.matrix_world@rig.pose.bones[n].matrix).copy() for n in ['upperleg02.R','lowerleg01.R','foot.R']}
out={'rest':{n:[list(r) for r in m] for n,m in rest.items()},'samples':{}}
for deg,capdeg in [(0,0),(10,4),(30,12),(60,25),(90,40),(120,56)]:
 rig.pose.bones['lowerleg01.R'].rotation_mode='XYZ';rig.pose.bones['lowerleg01.R'].rotation_euler=(math.radians(deg),0,0);bpy.context.view_layer.update()
 knee=rig.matrix_world@rig.pose.bones['lowerleg01.R'].head;ankle=rig.matrix_world@rig.pose.bones['foot.R'].head
 D=rig.matrix_world@rig.pose.bones['lowerleg01.R'].matrix@rest['lowerleg01.R'].inverted();q=D.to_quaternion();axis,a=q.to_axis_angle();Q=Quaternion(axis,math.radians(capdeg));front=Q@Vector((0,1,0));up=Q@Vector((0,0,1));lat=Q@Vector((1,0,0))
 row={'knee_world':list(knee),'ankle_world':list(ankle),'world_bend_axis':list(axis),'world_bend_degrees':math.degrees(a),'cap_degrees':capdeg,'rays':{}}
 for name in ['BW4_CONTEXT_BW1_IndexedBody','BW4_CONTEXT_BW1_Leggings']:
  o=bpy.data.objects[name];e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh();m.calc_loop_triangles();tree=BVHTree.FromPolygons([e.matrix_world@v.co for v in m.vertices],[t.vertices[:] for t in m.loop_triangles],all_triangles=True);e.to_mesh_clear();r=[]
  for z in [-.07,-.035,0,.035,.07]:
   for x in [-.055,-.03,0,.03,.055]:
    origin=knee+up*z+lat*x+front*.25;hit,normal,idx,d=tree.ray_cast(origin,-front,.5)
    if hit:r.append({'x':x,'z':z,'front':(hit-knee).dot(front),'hit':list(hit)})
  row['rays'][name]=r
 out['samples'][deg]=row
(R/'records/knee_sections.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))

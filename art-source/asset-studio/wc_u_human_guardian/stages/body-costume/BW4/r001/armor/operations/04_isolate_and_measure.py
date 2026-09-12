import bpy,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW4/r001/armor')
s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s
parts=[bpy.data.objects[n] for n in json.loads(s['armor_parts'])];context=[bpy.data.objects[n] for n in json.loads(s['context_parts'])];coat=bpy.data.objects['BW4_CONTEXT_BW1_CoatUpper_Continuous'];body=bpy.data.objects['BW4_CONTEXT_BW1_IndexedBody'];dg=bpy.context.evaluated_depsgraph_get()
o=coat.evaluated_get(dg);me=o.to_mesh();co=[o.matrix_world@v.co for v in me.vertices];bvh=BVHTree.FromPolygons(co,[tuple(p.vertices) for p in me.polygons]);o.to_mesh_clear()
out=[]
for name in ['BW4_Breastplate_ControlSurface','BW4_Backplate_ControlSurface']:
 ob=bpy.data.objects[name];ev=ob.evaluated_get(dg);me=ev.to_mesh();front='Breast' in name;d=[]
 for v in me.vertices:
  p=ev.matrix_world@v.co;origin=Vector((p.x,1 if front else -1,p.z));hit=bvh.ray_cast(origin,Vector((0,-1 if front else 1,0)),2)
  if hit[0]:d.append((p.y-hit[0].y)*(1 if front else -1))
 out.append({'part':name,'samples':len(d),'min_coat_clearance_mm':min(d)*1000,'negative':sum(x<0 for x in d),'less3mm':sum(x<.003 for x in d)})
 ev.to_mesh_clear()
(R/'records/initial_clearance.json').write_text(json.dumps(out,indent=2));print(out)
s.camera=bpy.data.objects['BW4_Camera_three_quarter']
for o in context:o.hide_render=True
s.render.filepath=str(R/'captures/initial_shell_isolated.png');bpy.ops.render.render(write_still=True)
for o in parts:o.hide_render=True
coat.hide_render=False;body.hide_render=False
s.render.filepath=str(R/'captures/initial_sleeve_body_isolated.png');bpy.ops.render.render(write_still=True)

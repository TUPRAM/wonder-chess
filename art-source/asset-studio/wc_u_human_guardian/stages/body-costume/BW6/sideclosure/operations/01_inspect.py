import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];SOURCE=R.parent/'armor/ada_bw6_upper_combined_r001.blend';bpy.ops.wm.open_mainfile(filepath=str(SOURCE),use_scripts=False)
s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s;s.frame_set(1);out={'source':str(SOURCE),'sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'objects':{}}
for nm in ['BW6_FrontPlate','BW6_BackPlate','BW6_SideEnclosure_1','BW6_SideEnclosure_-1']:
 o=bpy.data.objects[nm];out['objects'][nm]={'co':[[v.index,*list(o.matrix_world@v.co)] for v in o.data.vertices],'faces':[list(f.vertices) for f in o.data.polygons],'modifiers':[(m.name,m.type) for m in o.modifiers],'groups':[g.name for g in o.vertex_groups]}
out['side_objects']=[o.name for o in s.objects if any(x in o.name.lower() for x in ['side','closure'])]
out['sections']={}
for nm in ['BW4_CONTEXT_BW1_IndexedBody','BW6_PaddedCoat_Tailored','BW6_FrontPlate','BW6_BackPlate']:
 o=bpy.data.objects[nm];ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();bvh=BVHTree.FromPolygons([ev.matrix_world@v.co for v in me.vertices],[list(f.vertices) for f in me.polygons]);ev.to_mesh_clear();rows=[]
 for z in [1.20,1.23,1.27,1.31,1.34]:
  for y in [.10,.06,.02,-.02,-.06,-.10,-.14]:
   h=bvh.ray_cast(Vector((1,y,z)),Vector((-1,0,0)),2);rows.append({'z':z,'y':y,'right_x':h[0].x if h[0] else None})
 out['sections'][nm]=rows
(R/'records/current_side_interface.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))

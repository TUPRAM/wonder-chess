import bpy, bmesh, json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1]
src=R.parents[1]/'BW5/armor/ada_bw5_armor_checkpoint_r003_ART_REVISE.blend'
bpy.ops.wm.open_mainfile(filepath=str(src),use_scripts=False)
s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s;s.frame_set(1)
result={}
for name in ['BW4_CONTEXT_BW1_CoatUpper_Continuous','BW4_CONTEXT_BW1_IndexedBody','BW4_CONTEXT_BW1_PaddedCollar','BW4_CONTEXT_BW1_WaistBelt']:
 o=bpy.data.objects[name];bm=bmesh.new();bm.from_mesh(o.data);bm.verts.ensure_lookup_table()
 boundary=[v for v in bm.verts if v.is_boundary]
 result[name]={'matrix_world':[list(x) for x in o.matrix_world],'vertices':len(o.data.vertices),'shape_keys':o.data.shape_keys.name if o.data.shape_keys else None,
  'boundary': [{'i':v.index,'co':list(o.matrix_world@v.co),'neighbors':[e.other_vert(v).index for e in v.link_edges if e.is_boundary]} for v in boundary],
  'groups':[g.name for g in o.vertex_groups]}
 bm.free()
 ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();bv=BVHTree.FromPolygons([ev.matrix_world@v.co for v in me.vertices],[tuple(f.vertices) for f in me.polygons]);ev.to_mesh_clear()
 samples=[]
 for z in [1.10,1.14,1.18,1.22,1.26,1.30,1.34,1.38,1.42,1.46,1.50,1.54,1.56]:
  row=[]
  for x in [0,.04,.08,.12,.16,.20]:
   row.append({'x':x,'front':list(h[0]) if (h:=bv.ray_cast(Vector((x,1,z)),Vector((0,-1,0)),2))[0] else None,'back':list(h[0]) if (h:=bv.ray_cast(Vector((x,-1,z)),Vector((0,1,0)),2))[0] else None})
  samples.append({'z':z,'rays':row})
 result[name]['samples']=samples
(R/'records/interface_baseline.json').write_text(json.dumps(result,indent=2))
print('BW6 interface inspection complete')

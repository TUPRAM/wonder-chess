import bpy,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'ada_bw6_torso_sectioned_coat.blend'),use_scripts=False)
s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s;s.frame_set(1)
out={'visible_meshes':[o.name for o in s.objects if o.type=='MESH' and not o.hide_render],'rays':{}}
for n in ['BW6_PaddedCoat_Tailored','BW6_FrontPlate','BW4_CONTEXT_BW1_IndexedBody']:
 o=bpy.data.objects[n];ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();bv=BVHTree.FromPolygons([ev.matrix_world@v.co for v in me.vertices],[tuple(f.vertices) for f in me.polygons]);ev.to_mesh_clear()
 rows=[]
 for z in [1.22,1.26,1.30,1.34,1.38,1.42,1.46]:
  row={'z':z,'front':[]}
  for x in [0,.04,.08,.12,.16]:
   h=bv.ray_cast(Vector((x,1,z)),Vector((0,-1,0)),2);row['front'].append((x,list(h[0]) if h[0] else None))
  rows.append(row)
 out['rays'][n]=rows
(R/'records/visibility_and_fit.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
for o in s.objects:
 if o.type=='MESH':o.hide_render=o.name!='BW6_PaddedCoat_Tailored'
s.camera=bpy.data.objects['BW4_Camera_front'];s.cycles.samples=8;s.render.threads=4;s.render.filepath=str(R/'captures/sectioned_coat_only.png');bpy.ops.render.render(write_still=True)

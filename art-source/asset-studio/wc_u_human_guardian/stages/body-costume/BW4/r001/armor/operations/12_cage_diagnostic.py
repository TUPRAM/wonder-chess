import bpy,json
from pathlib import Path
R=Path('C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW4/r001/armor');s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s;s.frame_set(1)
black=bpy.data.materials.new('TEMP_CAGE_EDGE_BLACK');black.use_nodes=True;black.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.005,.005,.005,1)
parts=[bpy.data.objects[n] for n in json.loads(s['armor_parts'])]
for ob in s.objects:
 if ob.type=='MESH' and ob not in parts:ob.hide_render=True
for ob in parts:
 ob.data.materials.append(black)
 for m in ob.modifiers:
  if m.type in ['SUBSURF','SOLIDIFY','BEVEL']:m.show_render=False
 w=ob.modifiers.new('Actual source cage edge diagnostic','WIREFRAME');w.thickness=.0009;w.use_replace=False;w.use_even_offset=False;w.material_offset=1;w.offset=1
s.camera=bpy.data.objects['BW4_Camera_three_quarter'];s.render.filepath=str(R/'captures/review_final_actual_cage_black_edges.png');bpy.ops.render.render(write_still=True)
print('DIAGNOSTIC_RENDER_ONLY_NO_BLEND_SAVE')

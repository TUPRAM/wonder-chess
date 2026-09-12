import bpy,json,bmesh
from pathlib import Path
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'ada_bw6_torso_interface_work.blend'),use_scripts=False)
s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s;s.frame_set(1)
out={}
for name in ['BW4_CONTEXT_BW1_IndexedBody','BW6_PaddedCoat_Tailored']:
 o=bpy.data.objects[name]
 out[name]={'modifiers':[{'name':m.name,'type':m.type,'viewport':m.show_viewport,'render':m.show_render,'mask_group':getattr(m,'vertex_group',None),'invert':getattr(m,'invert_vertex_group',None),'levels':getattr(m,'levels',None)} for m in o.modifiers],'groups':[(g.index,g.name) for g in o.vertex_groups],'base':len(o.data.vertices),'shape_keys':[(k.name,k.value) for k in o.data.shape_keys.key_blocks] if o.data.shape_keys else None}
 if 'IndexedBody' in name:
  for m in o.modifiers:
   if m.type in ['ARMATURE','SUBSURF']:m.show_viewport=False
  bpy.context.view_layer.update();ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh()
  out[name]['masked_base']={'vertices':len(me.vertices),'faces':len(me.polygons),'points':[{'i':v.index,'co':list(o.matrix_world@v.co),'groups':[(o.vertex_groups[g.group].name,g.weight) for g in v.groups if g.weight>.4]} for v in me.vertices if 1.47<(o.matrix_world@v.co).z<1.49][:12]}
  ev.to_mesh_clear()
(R/'records/foundation_survey.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))

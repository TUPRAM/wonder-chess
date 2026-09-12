import bpy,json,ast,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'shoulder_correction2.blend'),use_scripts=False);s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s;s.frame_set(1);rig=bpy.data.objects['BW4_Armor_Independent_Rig']
tree=ast.parse((R/'operations/03_audit.py').read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'audit_functions','exec'),globals())
query=R.parents[1]/'BW2/r001/integrated-independent/audit_integrated_geometry.py';tree=ast.parse(query.read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['segment_triangle','self_audit']],type_ignores=[]),'self_functions','exec'),globals())
cap=bpy.data.objects['BW4_Pauldron_R_Cap']
# Reconstruct the two intermediate saddle rows in their proper surface order.
# The prior rows doubled back across the new proximal opening. No extra volume offset.
for i in range(10):
 p=cap.data.vertices[10+i].co.copy();q=cap.data.vertices[40+i].co.copy()
 cap.data.vertices[20+i].co=p.lerp(q,.35);cap.data.vertices[30+i].co=p.lerp(q,.70)
cap.data.update();cap['BW5_method']='New open proximal saddle with ordered longitudinal control strips; former intermediate rows were reconstructed to remove foldback. Distal overlap unchanged.'
record={}
for name in ['BW4_Pauldron_R_Cap','BW4_Pauldron_R_Lame2']:
 ob=bpy.data.objects[name];record[name]={}
 for mode in ['all','no_bevel','no_solidify_bevel']:
  for m in ob.modifiers:
   if m.type=='BEVEL':m.show_viewport=(mode=='all')
   if m.type=='SOLIDIFY':m.show_viewport=(mode!='no_solidify_bevel')
  bpy.context.view_layer.update();q,tri,b=geom(ob);test=self_audit(q,[(i,t) for i,t in enumerate(tri)]);record[name][mode]=test['confirmed_nonadjacent_transverse_pairs']
 for m in ob.modifiers:
  if m.type in ['BEVEL','SOLIDIFY']:m.show_viewport=True
print(json.dumps(record,indent=2));(R/'records/ordered_patch_modifier_diagnosis.json').write_text(json.dumps(record,indent=2))
# Avoid the small bevel's generated edge fold where the explicitly returned cage is already shaped.
for n in ['BW4_Pauldron_R_Cap','BW4_Pauldron_R_Lame2']:
 o=bpy.data.objects[n]
 if record[n]['no_bevel']==0:
  for m in o.modifiers:
   if m.type=='BEVEL':m.show_viewport=False;m.show_render=False
  o['BW5_EDGE_POLICY']='Cage-derived shaped edge with 3mm shell; legacy all-edge bevel disabled after modifier isolation showed generated self-crossing.'
s['BW5_SHOULDER_STATUS']='ORDERED_PATCH_FOLLOWUP_PENDING_REVIEW';bpy.ops.wm.save_as_mainfile(filepath=str(R/'shoulder_ordered_surface.blend'))

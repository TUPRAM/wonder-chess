import bpy,sys,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'operations'));import check_shoulder as ck
s=ck.load(R/'ada_bw6_shoulder_final_interface.blend');o=bpy.data.objects['BW6_Pauldron_R_Cap'];changes=[];direction=o.matrix_world.to_3x3().inverted()@Vector((1,0,0))
for i,allowance in [(0,.004),(1,.004),(2,.0015)]:
 for j,w in enumerate([.5,1,1,.5,0]):
  if not w:continue
  n=i*13+j;before=o.data.vertices[n].co.copy();o.data.vertices[n].co+=direction*(allowance*w);changes.append({'vertex':n,'before':list(before),'after':list(o.data.vertices[n].co),'lateral_m':allowance*w})
o.data.update();o['BW6_final_collar_fit']='0-4mm local medial-rear lip clearance for supplied final collar. Evidence raw triangles2-4/27-29 crossing at81-86; evaluated cap was already clear. No global offset or suspension change.';p=R/'ada_bw6_shoulder_medial_rear_fitted.blend';bpy.ops.wm.save_as_mainfile(filepath=str(p));(R/'records/final_collar_local_fit.json').write_text(json.dumps({'source':'ada_bw6_shoulder_final_interface.blend','changes':changes,'cause':'final_interface_audit.json raw cage cap/collar atframes81-86'},indent=2))

import bpy,sys,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'operations'));import check_shoulder as ck
s=ck.load(R/'ada_bw6_shoulder_interface_candidate.blend');out=Vector(json.loads((R/'records/initial_construction.json').read_text())['basis']['out']);o=bpy.data.objects['BW6_Pauldron_R_Lame1'];changes=[]
# Actual rest/lowered intersections localize to the two newly added strips' rear-quarter region.
for i,allowance in [(0,.006),(1,.004)]:
 for j,w in enumerate([0,.5,.9,1,.9,.5,0]):
  if w:o.data.vertices[i*13+j].co+=out*(allowance*w);changes.append([i*13+j,allowance*w])
o.data.update();o['BW6_underlap_fit']='Localized 0-6mm rear-quarter allowance on the two new underlap strips, following the measured coat crossing at rest and lowered pose. Distal lames/cap unchanged.'
bpy.ops.wm.save_as_mainfile(filepath=str(R/'ada_bw6_shoulder_underlap_fitted.blend'))
(R/'records/underlap_local_fit.json').write_text(json.dumps({'evidence':'stable_interface_audit.json, rest world (.269,-.092,1.462)m; lowered (.264,-.093,1.413)m','changed_control_indices_and_outward_m':changes,'unchanged':'All existing distal first-lame geometry, second lame, cap, rig/body/coat.'},indent=2))

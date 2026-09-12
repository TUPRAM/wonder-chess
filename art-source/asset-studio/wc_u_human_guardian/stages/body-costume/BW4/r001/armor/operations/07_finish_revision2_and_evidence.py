import bpy,json,math
from pathlib import Path
from mathutils import Vector
R=Path('C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW4/r001/armor')
s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s;s.frame_set(1)
front=bpy.data.objects['BW4_Breastplate_ControlSurface'];old=[v.co.copy() for v in front.data.vertices]
# The final waist portion of corrective revision 2 incorporates review arriving during the same pass.
for v in front.data.vertices:
 j=v.index//11
 if j<=1:v.co.z+=.030
 elif j==2:v.co.z+=.010
front.data.update()
for name,idx in [('Waist',list(range(11))),('Side_L',[j*11 for j in range(10)]),('Side_R',[j*11+10 for j in range(10)])]:
 ob=bpy.data.objects['BW4_Front_'+name+'_Return']
 for k,i in enumerate(idx):
  d=front.data.vertices[i].co-old[i]
  ob.data.vertices[k*2].co+=d;ob.data.vertices[k*2+1].co+=d
 ob.data.update()
for side in [-1,1]:
 ob=bpy.data.objects['BW4_Thorax_SideReturn_'+str(side)]
 for j in range(7):
  d=front.data.vertices[j*11+(10 if side==1 else 0)].co-old[j*11+(10 if side==1 else 0)]
  for k,t in enumerate([0,.08,.46,.88,1]):ob.data.vertices[j*5+k].co+=d*(1-t)
 ob.data.update()
s['iteration']='Initial construction plus two substantive corrections. Revision2 includes upper clearance, bridge endpoints, central ridge, cap clearance, and waist lift from contemporaneous independent review. Geometry iteration stopped.'
s['status']='ART_REVISE';s['remaining_scope']='No canonical seven-action mapping or engine check. Neck/cuff and other BW1 context remain unresolved.'
s.camera=bpy.data.objects['BW4_Camera_three_quarter'];s.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(R/'ada_armor_work.blend'))
bpy.ops.wm.save_as_mainfile(filepath=str(R/'ada_armor_checkpoint_FINAL_ART_REVISE.blend'),copy=True)
parts=[bpy.data.objects[n] for n in json.loads(s['armor_parts'])];context=[bpy.data.objects[n] for n in json.loads(s['context_parts'])];baseline=[bpy.data.objects[n] for n in json.loads(s['baseline_parts'])]
def render(name,cam='three_quarter',fr=1):
 s.frame_set(fr);s.camera=bpy.data.objects['BW4_Camera_'+cam];s.render.filepath=str(R/'captures'/f'{name}.png');bpy.ops.render.render(write_still=True)
for cam in ['front','back','profile','three_quarter','rear_three_quarter','shoulder','context']:render('review_final_'+cam,cam)
render('review_final_raise','three_quarter',49);render('review_final_reach','three_quarter',73)
key=bpy.data.objects['BW4_Key'];prior=key.location.copy();rot=key.rotation_euler.copy();key.location.x=-key.location.x;key.rotation_euler=(Vector((0,0,1.3))-key.location).to_track_quat('-Z','Y').to_euler();render('review_final_reversed');render('review_final_shoulder_reversed','shoulder');key.location=prior;key.rotation_euler=rot
for o in context:o.hide_render=True
render('review_final_shell_only');render('review_final_shell_back','rear_three_quarter')
# Actual low-density cage edges from final new geometry, displayed in a separate diagnostic.
for o in parts:
 for m in o.modifiers:
  if m.type in ['SUBSURF','BEVEL','SOLIDIFY']:m.show_render=False
 w=o.modifiers.new('Diagnostic actual cage edges','WIREFRAME');w.thickness=.0006;w.use_replace=False;w.use_even_offset=False
render('review_final_actual_cage')
for o in parts:
 w=o.modifiers.get('Diagnostic actual cage edges')
 if w:o.modifiers.remove(w)
 for m in o.modifiers:m.show_render=True
for o in context:o.hide_render=False
# Genuine r003 geometry restored on duplicate for matched baseline; no source writes.
coat=bpy.data.objects['BW4_CONTEXT_BW1_CoatUpper_Continuous'];candidate_coat=coat.data;coat.data=bpy.data.objects['BW1_CoatUpper_Continuous'].data.copy()
for o in parts:o.hide_render=True
for o in baseline:o.hide_render=False
for cam in ['front','back','profile','three_quarter']:render('matched_r003_'+cam,cam)
coat.data=candidate_coat
for o in baseline:o.hide_render=True
for o in parts:o.hide_render=False
for o in s.objects:
 if o.type=='MESH' and o not in [coat,bpy.data.objects['BW4_CONTEXT_BW1_IndexedBody']]:o.hide_render=True
render('review_final_sleeve_only_rest');render('review_final_sleeve_only_raise','three_quarter',49);render('review_final_sleeve_only_reach','three_quarter',73)
print('FINAL_EVIDENCE_COMPLETE')

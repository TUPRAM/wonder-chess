import bpy,bmesh,math,json
from pathlib import Path
from mathutils import Vector
R=Path('C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW4/r001/armor')
s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s;s.frame_set(1)
front=bpy.data.objects['BW4_Breastplate_ControlSurface'];old=[v.co.copy() for v in front.data.vertices]
# Local upper-chest enclosure and stronger center/waist plane, without a global smooth pass.
for v in front.data.vertices:
 j,i=divmod(v.index,11);u=abs((i-5)/5)
 if j>=6:v.co.y+=.012
 if 2<=j<=6:
  if i==5:v.co.y+=.014
  if i in [4,6]:v.co.y+=.006
 if j<=1:v.co.z+=.012*u
front.data.update()
crease=front.data.attributes.new('crease_edge','FLOAT','EDGE')
for e in front.data.edges:
 a,b=e.vertices
 if a%11==5 and b%11==5:crease.data[e.index].value=.55
for name,idx in [('Neck',list(range(99,110))),('Waist',list(range(11))),('Side_L',[j*11 for j in range(10)]),('Side_R',[j*11+10 for j in range(10)])]:
 rim=bpy.data.objects['BW4_Front_'+name+'_Return']
 for k,i in enumerate(idx):
  d=front.data.vertices[i].co-old[i]
  for vi in [2*k,2*k+1]:rim.data.vertices[vi].co+=d
 rim.data.update()
# Sidewalls remain joined at the intended opening edge after front cage change.
for side in [-1,1]:
 o=bpy.data.objects['BW4_Thorax_SideReturn_'+str(side)]
 for j in range(7):
  i=j*11+(10 if side==1 else 0);d=front.data.vertices[i].co-old[i]
  for k,t in enumerate([0,.08,.46,.88,1]):o.data.vertices[j*5+k].co+=d*(1-t)
 o.data.update()
# Reconstruct both bridge strips to actually meet the moved plate instead of float behind it.
for side in [-1,1]:
 o=bpy.data.objects['BW4_ShoulderBridge_'+str(side)]
 endpoint=front.data.vertices[99+(9 if side==1 else 1)].co.copy()
 pts=[endpoint+Vector((0,.001,-.002)),Vector((side*.141,.036,1.512)),Vector((side*.137,-.038,1.532)),Vector((side*.138,-.105,1.512)),Vector((side*.145,-.150,1.480))]
 for i,p in enumerate(pts):
  # Width runs across the shoulder, staying clear of collar.
  o.data.vertices[2*i].co=p+Vector((-.013,0,0));o.data.vertices[2*i+1].co=p+Vector((.013,0,0))
 o.data.update()
# Increase only cap clearance and preserve lames; crease columns establish a broad top face.
a=Vector((.18184635,-.04636158,1.44498372));axis=(Vector((.36106092,-.04210385,1.24891078))-a).normalized()
cap=bpy.data.objects['BW4_Pauldron_R_Cap'];oldcap=[v.co.copy() for v in cap.data.vertices]
for v in cap.data.vertices:
 p=v.co-a;rad=p-axis*p.dot(axis)
 if rad.length>0:v.co+=rad.normalized()*.007
cap.data.update();cr=cap.data.attributes.new('crease_edge','FLOAT','EDGE')
for e in cap.data.edges:
 i,j=e.vertices
 if i%10==j%10 and i%10 in [3,6]:cr.data[e.index].value=.36
rim=bpy.data.objects['BW4_Pauldron_R_Cap_LowerReturn']
for i in range(10):
 d=cap.data.vertices[50+i].co-oldcap[50+i]
 rim.data.vertices[2*i].co+=d;rim.data.vertices[2*i+1].co+=d
rim.data.update()
s['iteration']='Corrective revision 2 of 2: upper-chest clearance, actual bridge endpoints, center plane/waist return, cap clearance/crown creases. Further defects require method review.'
s['status']='ART_REVISE_PENDING_LOCAL_EVIDENCE';s['cuff_bracer_scope']='Not changed by armor lane; retained BW1 only contextual.'
s.camera=bpy.data.objects['BW4_Camera_three_quarter'];s.render.resolution_x=960;s.render.resolution_y=960;s.cycles.samples=24
bpy.ops.wm.save_as_mainfile(filepath=str(R/'ada_armor_work.blend'))
bpy.ops.wm.save_as_mainfile(filepath=str(R/'ada_armor_checkpoint_r002_ART_REVISE.blend'),copy=True)
for name,cam,fr in [('final_front','front',1),('final_back','back',1),('final_profile','profile',1),('final_three_quarter','three_quarter',1),('final_rear_three_quarter','rear_three_quarter',1),('final_shoulder_close','shoulder',1),('final_raise','three_quarter',49),('final_reach','three_quarter',73),('final_fullbody_HEAD_AND_OTHER_PARTS_PENDING','context',1)]:
 s.frame_set(fr);s.camera=bpy.data.objects['BW4_Camera_'+cam];s.render.filepath=str(R/'captures'/f'{name}.png');bpy.ops.render.render(write_still=True)
print('FINAL_CORRECTION_DONE')

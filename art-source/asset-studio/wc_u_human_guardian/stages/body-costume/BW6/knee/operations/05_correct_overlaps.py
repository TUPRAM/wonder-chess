import bpy,json,math
from pathlib import Path
from mathutils import Vector,Quaternion
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'ada_bw6_knee_initial.blend'),use_scripts=False,load_ui=False);s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s
owned=json.loads(s['BW6_knee_owned']);record=json.loads(s['BW6_knee_record']);knee=Vector(record['knee_world_rest']);axis=Vector(record['verified_world_bend_axis'])
u=[-1,-.96,-.72,-.34,-.06,0,.06,.34,.72,.96,1]
o=bpy.data.objects['BW6_KneeCup_R']
for v in o.data.vertices:
 row=v.index//11;a=u[v.index%11]
 # Recut the lateral return into a shallower exterior plane; retain the medial coverage.
 v.co.y+=.015*max(0,a)+(.016 if row<3 else .008 if row>3 else .006)
 # Main top follows a shaped sloping edge rather than a horizontal belt-like cap.
 if row>=5:v.co.z-=.007*abs(a)
o=bpy.data.objects['BW6_KneeUpperLame_R']
for v in o.data.vertices:
 a=u[v.index%11];row=v.index//11;v.co.y+=.015*max(0,a)+.009;v.co.z-=.006*abs(a)
o=bpy.data.objects['BW6_KneeLowerLame_R']
for v in o.data.vertices:
 a=u[v.index%11];row=v.index//11;v.co.y+=.027+.018*max(0,a)
 # Broaden the lower overlap; keep actual thickness and separate surfaces.
 if row<2:v.co.z-=.008
for f,deg in [(1,0),(11,30),(21,60),(31,90),(41,120),(51,90),(61,60),(71,30),(81,0)]:
 s.frame_set(f);row=next(r for r in record['table'] if r[0]==deg)
 for name,ang in zip(owned,row[1:4]):
  c=bpy.data.objects[name+'_RigidControl'];q=Quaternion(axis,math.radians(ang));v=Vector((0,row[4],0))
  if 'Upper' in name:v.z-=dict([(0,0),(30,.005),(60,.019),(90,.034),(120,.048)])[deg]
  if 'Lower' in name:v.y+=dict([(0,0),(30,.003),(60,.008),(90,.009),(120,.008)])[deg]
  c.location=knee+q@v;c.rotation_quaternion=q;c.keyframe_insert('location',frame=f);c.keyframe_insert('rotation_quaternion',frame=f)
s.frame_set(1);s['BW6_knee_correction1']='Reconstructed lateral shell profile, broader underlap lip, deliberately keyed upper-lame slide preserving rigid dimensions. No body/sole change.'
bpy.ops.wm.save_as_mainfile(filepath=str(R/'ada_bw6_knee_correction1.blend'))
for f in [1,21,31,41]:
 s.frame_set(f)
 for view in ['front','profile','three_quarter']:
  s.camera=bpy.data.objects['BW6_KneeCamera_'+view];s.render.filepath=str(R/'captures'/f'correction1_{view}_{f}.png');bpy.ops.render.render(write_still=True)

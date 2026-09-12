import bpy,json,math
from pathlib import Path
from mathutils import Vector,Quaternion
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'ada_bw6_knee_correction1.blend'),use_scripts=False,load_ui=False);s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s;s.frame_set(1);bpy.context.view_layer.update()
record=json.loads(s['BW6_knee_record']);knee=Vector(record['knee_world_rest']);axis=Vector(record['verified_world_bend_axis']);owned=json.loads(s['BW6_knee_owned'])
# Preserve the lower three sections and original ankle interface. Recut only the upper two greave rows.
old=bpy.data.objects['BW4_CONTEXT_BW1_Greave_R'];w=old.matrix_world.copy();o=old.copy();o.data=old.data.copy();o.name='BW6_Greave_R_RebuiltUpper';s.collection.objects.link(o);o.matrix_world=w;inv=w.inverted();o.hide_render=False;o.hide_set(False)
for v in o.data.vertices:
 row=v.index//13
 if row>=3:
  p=w@v.co;z=.416 if row==3 else .435;angle=math.radians(-106+212*(v.index%13)/12);rx=.066 if row==3 else .059;ry=.073 if row==3 else .065
  ankle=Vector((.18817,-.03622,.07806));kn=Vector((.15343,-.01560,.50984));c=ankle+(kn-ankle)*((z-ankle.z)/(kn.z-ankle.z));p=c+Vector((rx*math.sin(angle),ry*math.cos(angle),0));p.z=z-(.012*abs(math.sin(angle)) if row==4 else 0);v.co=inv@p
old.hide_render=True;old.hide_set(True);owned.append(o.name)
table=[(0,0,0,0,0),(30,12,10,20,-.008),(60,25,22,42,-.019),(90,40,37,68,-.031),(120,56,53,94,-.043)]
for f,deg in [(1,0),(11,30),(21,60),(31,90),(41,120),(51,90),(61,60),(71,30),(81,0)]:
 s.frame_set(f);row=next(r for r in table if r[0]==deg);qc=Quaternion(axis,math.radians(row[1]));qu=Quaternion(axis,math.radians(row[2]));ql=Quaternion(axis,math.radians(row[3]));shift=row[4]
 c=bpy.data.objects['BW6_KneeUpperLame_R_RigidControl'];c.rotation_quaternion=qu;c.location=knee+qu@Vector((0,shift,-.014*deg/120));c.keyframe_insert('location',frame=f);c.keyframe_insert('rotation_quaternion',frame=f)
 # Place the top lip at the verified cup's distal overlap; lower orientation remains separately authored.
 c=bpy.data.objects['BW6_KneeLowerLame_R_RigidControl'];target=knee+qc@Vector((-.010,.094+shift,-.061));lip=Vector((-.010,.109,-.058));c.location=target-ql@lip;c.rotation_quaternion=ql;c.keyframe_insert('location',frame=f);c.keyframe_insert('rotation_quaternion',frame=f)
s.frame_set(1);s['BW6_knee_owned']=json.dumps(owned);s['BW6_knee_correction2']='Upper greave recut only, lower sections/sole preserved. Upper lame follows near-parallel nested overlap. Lower rigid lip anchored to explicit cup distal point, no scaling or skin blending.'
bpy.ops.wm.save_as_mainfile(filepath=str(R/'ada_bw6_knee_correction2.blend'))
for f in [1,11,21,31,41]:
 s.frame_set(f)
 for view in ['front','profile','three_quarter']:
  s.camera=bpy.data.objects['BW6_KneeCamera_'+view];s.render.filepath=str(R/'captures'/f'correction2_{view}_{f}.png');bpy.ops.render.render(write_still=True)

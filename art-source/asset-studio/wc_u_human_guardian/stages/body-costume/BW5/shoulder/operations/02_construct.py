import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];B4=R.parents[1]/'BW4/r001/armor'
bpy.ops.wm.open_mainfile(filepath=str(B4/'ada_armor_checkpoint_FINAL_ART_REVISE.blend'),use_scripts=False)
s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s;s.frame_set(1)
a=Vector((.18184635,-.04636158,1.44498372));axis=(Vector((.36106092,-.04210385,1.24891078))-a).normalized();front=Vector((0,1,0));front=(front-axis*front.dot(axis)).normalized();outer=axis.cross(front)
def local(p):
 d=p-a;return Vector((d.dot(axis),d.dot(front),d.dot(outer)))
def world(p):return a+axis*p[0]+front*p[1]+outer*p[2]
cap=bpy.data.objects['BW4_Pauldron_R_Cap'];old=[v.co.copy() for v in cap.data.vertices]
# Replace the narrow proximal closure with a deliberately open saddle edge.
# Crown and front/rear aperture independently set; distal overlap remains fixed.
top=[(.052,-.112,.036),(.036,-.104,.054),(.002,-.088,.086),(-.031,-.059,.103),(-.043,-.028,.110),(-.045,0,.111),(-.040,.028,.110),(-.017,.059,.098),(.032,.094,.063),(.057,.109,.036)]
second=[(.061,-.118,.025),(.044,-.109,.049),(.008,-.096,.088),(-.030,-.062,.114),(-.035,-.029,.121),(-.036,0,.122),(-.032,.029,.121),(-.005,.063,.109),(.045,.100,.062),(.069,.112,.029)]
new=[v.copy() for v in old]
for i,p in enumerate(top+second):new[i]=world(p)
for j in [2,3]:
 for i in range(10):
  p=local(old[j*10+i]);edge=max(0,(abs(i-4.5)-2)/2.5)
  p[0]+=(.052 if j==2 else .025)*edge
  p[2]+=(.043 if j==2 else .020)*edge
  new[j*10+i]=world(p)
# Rebuild the proximal faces as a new owned mesh with purposeful loop correspondence.
faces=[tuple(p.vertices) for p in cap.data.polygons];me=bpy.data.meshes.new('BW5_Cap_Reconstructed_ProximalSaddle');me.from_pydata(new,[],faces);me.update();oldme=cap.data;cap.data=me
for mat in oldme.materials:me.materials.append(mat)
bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
for p in me.polygons:p.use_smooth=True
cap.vertex_groups.clear();vg=cap.vertex_groups.new(name='upperarm01.R');vg.add(list(range(len(new))),1,'REPLACE')
cap['BW5_method']='New proximal saddle surface; crown is independent of front/rear aperture. Distal overlap unchanged, one rigid existing upper-arm attachment.'
# Recut the offending distal front corner along the arm axis; palm-facing radius is retained.
lame=bpy.data.objects['BW4_Pauldron_R_Lame2'];oldl=[v.co.copy() for v in lame.data.vertices]
for v in lame.data.vertices:
 j,i=divmod(v.index,10);weight=max(0,(i-5)/4)
 amount={2:.007,3:.017,4:.026}.get(j,0)*weight
 v.co-=axis*amount
lame.data.update();rim=bpy.data.objects['BW4_Pauldron_R_Lame2_LowerReturn']
for i in range(10):
 delta=lame.data.vertices[40+i].co-oldl[40+i]
 for k in [2*i,2*i+1]:rim.data.vertices[k].co+=delta
rim.data.update();lame['BW5_method']='Distal front corner recut by up to 26mm axially, retaining dorsal/rear length and transverse fit.'
s['BW5_SHOULDER_STATUS']='INITIAL_LOCAL_CONSTRUCTION_PENDING_REVIEW'
bpy.ops.wm.save_as_mainfile(filepath=str(R/'shoulder_initial.blend'))
# Saved matched cameras, fixed render policy and real target geometry.
s.render.engine='BLENDER_WORKBENCH';s.display.shading.light='STUDIO';s.display.shading.color_type='MATERIAL';s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.display.shading.cavity_type='BOTH';s.render.resolution_x=960;s.render.resolution_y=960
for tag,cam,fr in [('initial_rest','shoulder',1),('initial_raise','shoulder',49),('initial_rear','rear_three_quarter',1),('initial_firstconflict','shoulder',20),('initial_lowerlame_worst','shoulder',25)]:
 s.frame_set(fr);s.camera=bpy.data.objects['BW4_Camera_'+cam];s.render.filepath=str(R/'captures'/f'{tag}.png');bpy.ops.render.render(write_still=True)
print('SHOULDER_INITIAL_DONE',flush=True)

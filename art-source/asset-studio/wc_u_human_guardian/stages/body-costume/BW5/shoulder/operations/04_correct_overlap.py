import bpy,bmesh,math,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'shoulder_initial.blend'),use_scripts=False);s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s;s.frame_set(1)
a=Vector((.18184635,-.04636158,1.44498372));axis=(Vector((.36106092,-.04210385,1.24891078))-a).normalized()
def radial(p):
 d=p-a;return (d-axis*d.dot(axis)).normalized()
# First-lame lower edge now houses a deliberate 6 mm outward overlap return;
# its crown and top interface to the cap remain exactly fixed.
l1=bpy.data.objects['BW4_Pauldron_R_Lame1'];old=[v.co.copy() for v in l1.data.vertices]
for v in l1.data.vertices:
 j,i=divmod(v.index,10);v.co+=radial(v.co)*{2:.003,3:.006,4:.006}.get(j,0)
l1.data.update();r1=bpy.data.objects['BW4_Pauldron_R_Lame1_LowerReturn']
for i in range(10):
 d=l1.data.vertices[40+i].co-old[40+i]
 for k in [2*i,2*i+1]:r1.data.vertices[k].co+=d
r1.data.update()
# The second lame enters under the preceding plate; do not let the two shells switch order.
l2=bpy.data.objects['BW4_Pauldron_R_Lame2']
for v in l2.data.vertices:
 j,i=divmod(v.index,10);v.co-=radial(v.co)*{0:.008,1:.008,2:.002}.get(j,0)
l2.data.update()
# Rebuild the terminal return as an adjoining short lip beyond the recut contour.
# It is a separate editable metal piece with a declared 0.8 mm butt-seam gap.
r2=bpy.data.objects['BW4_Pauldron_R_Lame2_LowerReturn'];vs=[]
for i in range(10):
 p=l2.data.vertices[40+i].co.copy();t=(p-l2.data.vertices[30+i].co).normalized();n=radial(p)
 vs.extend([p+t*.0008+n*.0006,p+t*.0043+n*.0018])
fs=[(i*2,i*2+1,i*2+3,i*2+2) for i in range(9)];me=bpy.data.meshes.new('BW5_Lame2_Distal_Return_Rebuilt');me.from_pydata(vs,[],fs);me.update();oldme=r2.data;r2.data=me
for mat in oldme.materials:me.materials.append(mat)
bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
for p in me.polygons:p.use_smooth=True
r2.vertex_groups.clear();g=r2.vertex_groups.new(name='upperarm01.R');g.add(list(range(len(vs))),1,'REPLACE')
for m in r2.modifiers:
 if m.type=='SOLIDIFY':m.thickness=.0015;m.offset=-1
r2['BW5_join']='Butt seam after recut corner, 0.8mm cage separation; evaluated review required.'
s['BW5_SHOULDER_STATUS']='CORRECTION1_OVERLAP_PENDING_REVIEW'
bpy.ops.wm.save_as_mainfile(filepath=str(R/'shoulder_correction1.blend'))
s.render.engine='BLENDER_WORKBENCH';s.display.shading.light='STUDIO';s.display.shading.color_type='MATERIAL';s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.display.shading.cavity_type='BOTH';s.render.resolution_x=960;s.render.resolution_y=960
for tag,cam,fr in [('correction1_rest','shoulder',1),('correction1_raise','shoulder',49),('correction1_rear','rear_three_quarter',1),('correction1_firstconflict','shoulder',20),('correction1_lowerlame_worst','shoulder',25)]:
 s.frame_set(fr);s.camera=bpy.data.objects['BW4_Camera_'+cam];s.render.filepath=str(R/'captures'/f'{tag}.png');bpy.ops.render.render(write_still=True)

import bpy,bmesh,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'shoulder_correction1.blend'),use_scripts=False);s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s;s.frame_set(1)
a=Vector((.18184635,-.04636158,1.44498372));axis=(Vector((.36106092,-.04210385,1.24891078))-a).normalized()
def radial(p):
 d=p-a;return (d-axis*d.dot(axis)).normalized()
lame=bpy.data.objects['BW4_Pauldron_R_Lame2'];old=lame.data;vs=[v.co.copy() for v in old.vertices];fs=[tuple(p.vertices) for p in old.polygons]
# Two intentional edge rows continue the existing surface into a turned terminal lip.
# These quads share the former lower boundary rather than overlap a second thick object.
for travel,rise in [(.0035,.0018),(.005,.0022)]:
 for i in range(10):
  p=vs[40+i];t=(p-vs[30+i]).normalized();vs.append(p+t*travel+radial(p)*rise)
for j in [4,5]:
 for i in range(9):
  k=j*10+i;fs.append((k,k+1,k+11,k+10))
me=bpy.data.meshes.new('BW5_Lame2_ContinuousReturnedEdge');me.from_pydata(vs,[],fs);me.update();lame.data=me
for mat in old.materials:me.materials.append(mat)
bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
for p in me.polygons:p.use_smooth=True
lame.vertex_groups.clear();g=lame.vertex_groups.new(name='upperarm01.R');g.add(list(range(len(vs))),1,'REPLACE')
crease=me.attributes.new('crease_edge','FLOAT','EDGE')
for e in me.edges:
 if all(40<=v<50 for v in e.vertices):crease.data[e.index].value=.42
retired=bpy.data.objects['BW4_Pauldron_R_Lame2_LowerReturn'];retired.hide_render=True;retired.hide_set(True);retired['BW5_STATE']='SUPERSEDED_FAILED_GEOMETRY_RETAINED: continuous return is now part of BW4_Pauldron_R_Lame2; not a cleared old seam.'
lame['BW5_method']='Recut distal front corner; concealed upper underlap; two shared-boundary quad rows produce one continuous returned edge. No separate intersecting terminal trim.'
s['BW5_SHOULDER_STATUS']='CORRECTION2_PENDING_FULL_AUDIT';s['BW5_SHOULDER_EXPLICIT_ACTIVE']=json.dumps(['BW4_Pauldron_R_Cap','BW4_Pauldron_R_Cap_LowerReturn','BW4_Pauldron_R_Lame1','BW4_Pauldron_R_Lame1_LowerReturn','BW4_Pauldron_R_Lame2'])
bpy.ops.wm.save_as_mainfile(filepath=str(R/'shoulder_correction2.blend'))
s.render.engine='BLENDER_WORKBENCH';s.display.shading.light='STUDIO';s.display.shading.color_type='MATERIAL';s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.display.shading.cavity_type='BOTH';s.render.resolution_x=960;s.render.resolution_y=960
for tag,cam,fr in [('correction2_rest','shoulder',1),('correction2_raise','shoulder',49),('correction2_rear','rear_three_quarter',1),('correction2_firstconflict','shoulder',20),('correction2_lowerlame_worst','shoulder',25)]:
 s.frame_set(fr);s.camera=bpy.data.objects['BW4_Camera_'+cam];s.render.filepath=str(R/'captures'/f'{tag}.png');bpy.ops.render.render(write_still=True)

import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'ada_bw6_torso_correction2.blend'),use_scripts=False)
s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s;s.frame_set(1)
front=bpy.data.objects['BW6_FrontPlate'];back=bpy.data.objects['BW6_BackPlate'];N=15
for sign in [-1,1]:
 ob=bpy.data.objects['BW6_SideEnclosure_'+str(sign)];vs=[];fs=[]
 for j in range(5):
  p=front.data.vertices[j*N+(N-1 if sign>0 else 0)].co.copy();q=back.data.vertices[j*N+(N-1 if sign>0 else 0)].co.copy()
  for k in range(13):
   t=k/12;r=p.lerp(q,t)
   r.x+=sign*.017*math.sin(math.pi*t)
   r.z-=.061*math.sin(math.pi*t)*(j/4)**2
   vs.append(r)
  if j:
   for k in range(12):a=(j-1)*13+k;fs.append((a,a+1,a+14,a+13))
 me=bpy.data.meshes.new(ob.name+'_OpenArmhole_Cage');me.from_pydata(vs,[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
 for mat in ob.data.materials:me.materials.append(mat)
 ob.data=me;ob.vertex_groups.clear();g=ob.vertex_groups.new(name='spine01');g.add(list(range(len(vs))),1,'REPLACE')
 for f in me.polygons:f.use_smooth=True
 ob['construction']='New lower side enclosure ends in a deliberate armhole below the moving shoulder; ordered vertical columns and curved transverse route. No high sidewall pushed into sleeve.'
navy=bpy.data.objects['BW6_NavyWaist']
for v in navy.data.vertices:
 d=Vector((v.co.x,v.co.y+.025,0));d.normalize();v.co+=d*.005
navy.data.update()
for name in ['BW6_LeatherBelt','BW4_CONTEXT_BW1_BeltBuckle']:
 ob=bpy.data.objects[name];ob.data=ob.data.copy()
 for v in ob.data.vertices:v.co.z+=.016
 ob.data.update()
s['BW6_side_intervention']='Purpose-built open armhole sidewall, nominal navy allowance35mm and fitted belt shifted16mm to natural-waist registration. Distinct scoped construction after useful main-plate correction.'
bpy.ops.wm.save_as_mainfile(filepath=str(R/'ada_bw6_torso_sideclosure.blend'))
s.cycles.samples=12;s.render.threads=4
for view in ['front','profile','back','three_quarter']:
 s.camera=bpy.data.objects['BW4_Camera_'+view];s.render.filepath=str(R/'captures'/('sideclosure_'+view+'.png'));bpy.ops.render.render(write_still=True)
print('BW6_SIDECLOSURE_RENDERED')

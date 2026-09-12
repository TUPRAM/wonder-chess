import bpy,bmesh,math,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'ada_bw6_torso_interface_work.blend'),use_scripts=False)
s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s;s.frame_set(1)
ob=bpy.data.objects['BW6_FrontPlate'];old=ob.data;ob.data=old.copy()
# Large constructed facets: a center keel, two upper chest fields and the
# shallow lower torso return. The ordered sections are independent of body volume.
u=[-1,-.82,-.42,0,.42,.82,1]
sections=[
 (1.181,.169,.133,.074,.017),
 (1.226,.171,.140,.080,.014),
 (1.310,.193,.157,.110,.052),
 (1.421,.167,.111,.073,.0),
 (1.481,.132,.081,.056,-.045)]
verts=[];faces=[]
for j,(z,w,mid,edge,dz) in enumerate(sections):
 for a in u:
  aa=abs(a);zz=z+(dz*aa if j<4 else dz*(1-aa)**1.4)
  yy=mid+(edge-mid)*aa
  if j==2:yy+=.006*math.sin(math.pi*aa)
  verts.append((a*w,yy,zz))
 if j:
  for i in range(len(u)-1):k=(j-1)*len(u)+i;faces.append((k,k+1,k+len(u)+1,k+len(u)))
me=bpy.data.meshes.new('BW6_Front_PlanarFields_Cage');me.from_pydata(verts,[],faces);me.update()
bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
for mat in old.materials:me.materials.append(mat)
ob.data=me;ob.vertex_groups.clear();g=ob.vertex_groups.new(name='spine01');g.add(list(range(len(verts))),1,'REPLACE')
for m in list(ob.modifiers):
 if m.type=='SUBSURF':ob.modifiers.remove(m)
be=ob.modifiers.new('Narrow manufactured facet edges','BEVEL');be.width=.001;be.segments=2;be.limit_method='ANGLE';be.angle_limit=.23
for p in me.polygons:p.use_smooth=False
ob['BW6_surface']='Reconstructed35vertex armor cage with24broad flat fields; no global smoothing or anatomy-shaped cups. Fixed rigid spine owner. Surface must pass fit queries.'
navy=bpy.data.objects['BW6_NavyWaist']
for v in navy.data.vertices:
 p=v.co.copy()
 if p.z<1.105 and p.y>.045 and abs(p.x)>.105:
  weight=max(0,min(1,(1.105-p.z)/.025))*max(0,min(1,(abs(p.x)-.105)/.025))
  v.co.y+=.005*weight
navy.data.update()
# Neck and hem boundary positions retained; source borders stay separate.
out=R/'ada_bw6_torso_faceted_study.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out))
s.cycles.samples=16;s.render.threads=4
for view in ['front','profile','three_quarter','back']:
 s.camera=bpy.data.objects['BW4_Camera_'+view];s.render.filepath=str(R/'captures'/('faceted_'+view+'.png'));bpy.ops.render.render(write_still=True)
print('BW6_FACETED_STUDY_COMPLETE')

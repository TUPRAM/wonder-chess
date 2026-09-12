import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'ada_bw6_torso_correction1.blend'),use_scripts=False)
s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s;s.frame_set(1)
front=bpy.data.objects['BW6_FrontPlate'];N=15
for v in front.data.vertices:
 j,i=divmod(v.index,N);a=abs(v.co.x)/max(abs(front.data.vertices[j*N].co.x),1e-5)
 if j==2:v.co.z=1.226+.018*a
 elif j==3:v.co.z=1.265+.036*a
 elif j==4:v.co.z=1.310+.052*a
 elif j==5:v.co.z=1.374+.019*a
 if 2<=j<=5:v.co.y+=.007*(1-a)-.007*a
crease=front.data.attributes.get('crease_edge') or front.data.attributes.new('crease_edge','FLOAT','EDGE')
for e in front.data.edges:
 a,b=e.vertices;ja,ia=divmod(a,N);jb,ib=divmod(b,N)
 if ia==ib==7:crease.data[e.index].value=.82
 elif ja==jb==4:crease.data[e.index].value=.62
front['BW6_correction2']='Anatomically located center keel and diagonal chest plane transition in source cage; no global smoothing or resolution increase.'
front.data.update()
# Give the rear shell a quiet spinal plane instead of a spherical back.
back=bpy.data.objects['BW6_BackPlate'];cr=back.data.attributes.get('crease_edge') or back.data.attributes.new('crease_edge','FLOAT','EDGE')
for e in back.data.edges:
 a,b=e.vertices
 if a%N==b%N==7:cr.data[e.index].value=.35
# Fit a new physical belt around the navy/coat waist on the same body frame.
body=bpy.data.objects['BW4_CONTEXT_BW1_IndexedBody'];ev=body.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();bv=BVHTree.FromPolygons([ev.matrix_world@v.co for v in me.vertices],[tuple(f.vertices) for f in me.polygons]);ev.to_mesh_clear()
vs=[];fs=[];K=64
for j,z in enumerate([1.069,1.074,1.117,1.123]):
 for i in range(K):
  a=2*math.pi*i/K;d=Vector((math.cos(a),math.sin(a),0));c=Vector((0,-.025,z));h=bv.ray_cast(c,d,.3)
  assert h[0] is not None
  vs.append(h[0]+d*.043)
 if j:
  for i in range(K):q=(i+1)%K;fs.append(((j-1)*K+i,(j-1)*K+q,j*K+q,j*K+i))
me=bpy.data.meshes.new('BW6_LeatherBelt_ControlCage');me.from_pydata(vs,[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
ob=bpy.data.objects.new('BW6_LeatherBelt',me);bpy.data.collections['BW6_TORSO_RECONSTRUCTION'].objects.link(ob)
for f in me.polygons:f.use_smooth=True
me.materials.append(bpy.data.materials['BW4_Underlayer_Clay']);vg=ob.vertex_groups.new(name='spine03');vg.add(list(range(len(vs))),1,'REPLACE')
mod=ob.modifiers.new('Belt contour','SUBSURF');mod.levels=1;mod.render_levels=1
mod=ob.modifiers.new('Leather wall','SOLIDIFY');mod.thickness=.005;mod.offset=-1;mod.use_even_offset=False
mod=ob.modifiers.new('Waist attachment','ARMATURE');mod.object=bpy.data.objects['BW4_Armor_Independent_Rig']
ob['owner_bone']='spine03';ob['construction']='Actual body-relative circumferential belt,43mm outer allowance from body,5mm leather; original oversized belt retained hidden.'
old=bpy.data.objects['BW4_CONTEXT_BW1_WaistBelt'];old.hide_render=True;old.hide_set(True)
s['BW6_owned_visible_parts']=json.dumps(json.loads(s['BW6_owned_visible_parts'])+[ob.name])
s['BW6_iteration']='Initial construction, circumferential garment correction, deliberate plate planes and belt enclosure correction. Evidence pending.'
bpy.ops.wm.save_as_mainfile(filepath=str(R/'ada_bw6_torso_correction2.blend'))
s.cycles.samples=16;s.render.threads=4
for name in ['front','profile','back','three_quarter']:
 s.camera=bpy.data.objects['BW4_Camera_'+name];s.render.filepath=str(R/'captures'/('correction2_'+name+'.png'));bpy.ops.render.render(write_still=True)
print('BW6_CHEST_PLANES_AND_BELT_RENDERED')

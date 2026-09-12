import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'ada_bw6_torso_oriented_work.blend'),use_scripts=False)
s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s;s.frame_set(1)
coat=bpy.data.objects['BW6_PaddedCoat_Tailored'];solid=next(m for m in coat.modifiers if m.type=='SOLIDIFY');solid.show_viewport=False;bpy.context.view_layer.update()
def bvh(o):
 e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh();b=BVHTree.FromPolygons([e.matrix_world@v.co for v in m.vertices],[tuple(f.vertices) for f in m.polygons]);e.to_mesh_clear();return b
cb=bvh(coat);solid.show_viewport=True
master=bpy.data.objects['BW4_CONTEXT_BW1_IndexedBody'];body=master.copy();body.data=master.data.copy();body.name='BW6_BodyFit_Candidate';bpy.data.collections['BW6_TORSO_RECONSTRUCTION'].objects.link(body)
assert body.data!=master.data and body.data.shape_keys!=master.data.shape_keys
master.hide_render=True;master.hide_set(True);body.hide_render=False;body.hide_set(False)
states=[m.show_viewport for m in body.modifiers]
for m in body.modifiers:m.show_viewport=False
bpy.context.view_layer.update();e=body.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh();points=[body.matrix_world@v.co for v in m.vertices];e.to_mesh_clear()
for md,state in zip(body.modifiers,states):md.show_viewport=state
key=body.shape_key_add(name='BW6_UnderPadding_LocalFit',from_mix=False);basis=body.data.shape_keys.key_blocks[0];inv=body.matrix_world.inverted().to_3x3();changes=[];misses=[]
for i,p in enumerate(points):
 if abs(p.x)>.175 or not 1.075<p.z<1.53:continue
 group=body.vertex_groups.get('body')
 if not any(g.group==group.index and g.weight>.5 for g in body.data.vertices[i].groups):continue
 front=cb.ray_cast(Vector((p.x,.8,p.z)),Vector((0,-1,0)),1.6)[0];back=cb.ray_cast(Vector((p.x,-.8,p.z)),Vector((0,1,0)),1.6)[0]
 if front is None or back is None or front.y-back.y<.05:continue
 lo=back.y+.009;hi=front.y-.009;target=max(lo,min(hi,p.y));delta=max(-.012,min(.012,target-p.y))
 if abs(delta)>1e-6:
  key.data[i].co=basis.data[i].co+inv@Vector((0,delta,0));changes.append({'index':i,'world_before':list(p),'delta_y_m':delta,'unclamped_delta_y_m':target-p.y})
key.value=1
body['BW6_scope']='Independent indexed source copy plus local torso under-padding fit key, maximum12mm depth displacement. Master source, existing38keys, head and limb dimensions preserved. Candidate fit requires visual and posed review.'
bpy.context.view_layer.update();bb=bvh(body)
# Explicit fabric waist envelope sampled against garment exterior, preserving
# the hemisphere of each radial direction and a deliberately short top overlap.
navy=bpy.data.objects['BW6_NavyWaist'];N=48;verts=[];faces=[]
for j,t in enumerate([0,.04,.34,.65,.88,.97,1]):
 for i in range(N):
  a=2*math.pi*i/N;front=math.sin(a)>0;ax=abs(math.cos(a))
  hem=1.181+.017*ax if front else 1.181+.018*(1-ax)
  top=hem+.010;z=1.072+(top-1.072)*t;d=Vector((math.cos(a),math.sin(a),0));origin=Vector((0,-.025,z))
  h=cb.ray_cast(origin,d,.4)[0]
  if h is not None:p=h+d*.004
  else:
   h=bb.ray_cast(origin,d,.4)[0];assert h is not None,(j,i);p=h+d*.03
  verts.append(p)
 if j:
  for i in range(N):k=(i+1)%N;faces.append(((j-1)*N+i,(j-1)*N+k,j*N+k,j*N+i))
me=bpy.data.meshes.new('BW6_Waist_GarmentRelative_Cage');me.from_pydata(verts,[],faces);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
samples=[f.normal.y for f in bm.faces if f.calc_center_median().y>.07]
if samples and sum(samples)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
for f in bm.faces:f.smooth=True
bm.to_mesh(me);bm.free()
for mat in navy.data.materials:me.materials.append(mat)
navy.data=me;navy.vertex_groups.clear();g=navy.vertex_groups.new(name='spine03');g.add(list(range(len(verts))),1,'REPLACE')
# Make space for the sewn waist overlap at the plate hem instead of driving
# the fabric through a narrow plate/body slot.
plate=bpy.data.objects['BW6_FrontPlate']
for v in plate.data.vertices:
 if v.co.z<1.24:v.co.y+=.006*max(0,1-abs(v.co.x)/.17)
plate.data.update()
for n in ['BW6_Front_Hem_TurnedBorder']:
 o=bpy.data.objects[n]
 for v in o.data.vertices:v.co.y+=.006*max(0,1-abs(v.co.x)/.17)
 o.data.update()
out=R/'ada_bw6_torso_layers_work.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out))
(R/'records/body_and_layer_fit.json').write_text(json.dumps({'body_candidate':body.name,'independent_mesh_and_keys':True,'original_keys':len(master.data.shape_keys.key_blocks),'new_keys':len(body.data.shape_keys.key_blocks),'changes':changes,'max_requested_delta_mm':max((abs(v['unclamped_delta_y_m'])*1000 for v in changes),default=0),'navy_method':'new garment-relative circumference and front/back hem-specific10mm overlap'},indent=2))
s.cycles.samples=12;s.render.threads=4
for view in ['front','profile','three_quarter','back']:
 s.camera=bpy.data.objects['BW4_Camera_'+view];s.render.filepath=str(R/'captures'/('layers_'+view+'.png'));bpy.ops.render.render(write_still=True)
print('BW6_LAYERS_COMPLETE')

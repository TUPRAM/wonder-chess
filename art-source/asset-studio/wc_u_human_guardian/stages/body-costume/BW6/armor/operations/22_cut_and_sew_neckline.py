import bpy,bmesh,math,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'ada_bw6_torso_layers_work.blend'),use_scripts=False)
s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s;s.frame_set(1)
coat=bpy.data.objects['BW6_PaddedCoat_Tailored'];bm=bmesh.new();bm.from_mesh(coat.data)
top_edges=[e for e in bm.edges if e.is_boundary and all(v.co.z>1.54 for v in e.verts)]
ring={v for e in top_edges for v in e.verts};assert len(ring)>30
remove=set();previous=set()
for j in range(4):
 adjacent={e.other_vert(v) for v in ring for e in v.link_edges if e.other_vert(v) not in ring and e.other_vert(v) not in previous}
 remove.update(f for v in ring for f in v.link_faces);previous,ring=ring,adjacent
bmesh.ops.delete(bm,geom=list(remove),context='FACES_ONLY');bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_faces],context='VERTS')
# Cut a true new neck aperture through the retained garment. This removes the
# inward neck yoke that previously forced a sloping/folded bridge to the collar.
center=Vector((0,-.05,0));rx=.110;ry=.112;count=24;ap=math.cos(math.pi/count)
for k in range(count):
 a=2*math.pi*k/count;normal=Vector((math.cos(a)/rx,math.sin(a)/ry,0));point=center+Vector((rx*math.cos(a)*ap,ry*math.sin(a)*ap,0))
 faces=[f for f in bm.faces if any(v.co.z>1.435 for v in f.verts) and any(abs(v.co.x)<.20 for v in f.verts)]
 edges={e for f in faces for e in f.edges};vs={v for f in faces for v in f.verts}
 bmesh.ops.bisect_plane(bm,geom=list(vs)+list(edges)+faces,dist=1e-7,plane_co=point,plane_no=normal,clear_inner=False,clear_outer=False)
faces=[f for f in bm.faces if any(v.co.z>1.435 for v in f.verts)];edges={e for f in faces for e in f.edges};vs={v for f in faces for v in f.verts}
bmesh.ops.bisect_plane(bm,geom=list(vs)+list(edges)+faces,dist=1e-7,plane_co=Vector((0,0,1.445)),plane_no=Vector((0,0,1)),clear_inner=False,clear_outer=False)
def inside(p):return all(math.cos(2*math.pi*k/count)*p.x/rx+math.sin(2*math.pi*k/count)*(p.y+.05)/ry<ap+1e-6 for k in range(count))
cut=[f for f in bm.faces if f.calc_center_median().z>1.445 and inside(f.calc_center_median())]
bmesh.ops.delete(bm,geom=cut,context='FACES_ONLY');bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_faces],context='VERTS')
edges=[e for e in bm.edges if e.is_boundary and all(v.co.z>1.44 for v in e.verts)];adj={}
for e in edges:
 for v in e.verts:adj.setdefault(v,[]).append(e.other_vert(v))
assert all(len(v)==2 for v in adj.values()),('aperture_not_simple',[(tuple(k.co),len(v)) for k,v in adj.items() if len(v)!=2])
start=max(adj,key=lambda v:v.co.x);loop=[start];prev=None
while len(loop)<len(adj):
 nxt=next(v for v in adj[loop[-1]] if v!=prev);assert nxt not in loop
 prev=loop[-1];loop.append(nxt)
points=[v.co.copy() for v in loop];n=len(loop);area=sum(points[i].x*points[(i+1)%n].y-points[(i+1)%n].x*points[i].y for i in range(n));sign=1 if area>0 else -1
angles=[math.atan2((p.y+.05)/ry,p.x/rx) for p in points]
for i in range(1,n):
 while angles[i]-angles[i-1]>math.pi:angles[i]-=2*math.pi
 while angles[i]-angles[i-1]<-math.pi:angles[i]+=2*math.pi
# Keep traversal and gently separate duplicate angular samples of the cut.
vals=[sign*a-i*.001 for i,a in enumerate(angles)];blocks=[]
for i,v in enumerate(vals):
 blocks.append([v,1,[i]])
 while len(blocks)>1 and blocks[-2][0]>blocks[-1][0]:
  b=blocks.pop();a=blocks.pop();w=a[1]+b[1];blocks.append([(a[0]*a[1]+b[0]*b[1])/w,w,a[2]+b[2]])
for value,_,ids in blocks:
 for i in ids:angles[i]=sign*(value+i*.001)
previous=loop
for t in [.08,.30,.85,1.]:
 new=[]
 for i,p in enumerate(points):
  a=angles[i];top=Vector((.128*math.cos(a),-.05+.122*math.sin(a),1.563-.006*max(0,math.sin(a))))
  assert top.z>p.z,(p,top)
  new.append(bm.verts.new(p.lerp(top,t)))
 for i in range(n):k=(i+1)%n;bm.faces.new((previous[i],previous[k],new[k],new[i]))
 previous=new
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.normal_update();samples=[f.normal.y for f in bm.faces if 1.18<f.calc_center_median().z<1.35 and abs(f.calc_center_median().x)<.08 and f.calc_center_median().y>.06]
if sum(samples)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
for f in bm.faces:f.smooth=True
bm.to_mesh(coat.data);bm.free();g=coat.vertex_groups.get('spine01')
for v in coat.data.vertices:
 if not v.groups:g.add([v.index],1,'REPLACE')
coat['BW6_neck']='True24-sided elliptical aperture cut through old neck yoke; collar sewn to that shared boundary, instead of stretching inward neck faces across the larger collar. Originalsource intact.'
bpy.ops.wm.save_as_mainfile(filepath=str(R/'ada_bw6_torso_recut_neck.blend'))
(R/'records/recut_neck.json').write_text(json.dumps({'aperture_vertices':n,'removed_faces':len(cut),'rx_m':rx,'ry_m':ry,'base_points':[list(p) for p in points],'method':coat['BW6_neck']},indent=2))
s.cycles.samples=12;s.render.threads=4
for view in ['front','profile','three_quarter','back']:
 s.camera=bpy.data.objects['BW4_Camera_'+view];s.render.filepath=str(R/'captures'/('recut_'+view+'.png'));bpy.ops.render.render(write_still=True)
print('BW6_RECUT_COMPLETE')

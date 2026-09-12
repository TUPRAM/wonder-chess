import bpy,bmesh,math,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'ada_bw6_torso_faceted_study.blend'),use_scripts=False)
s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s;s.frame_set(1)
old=bpy.data.objects['BW6_PaddedCoat_Tailored'];old.name='BW6_FAILED_RadialCoat';old.hide_render=True;old.hide_set(True)
source=bpy.data.objects['BW4_CONTEXT_BW1_CoatUpper_Continuous'];coat=source.copy();coat.data=source.data.copy();coat.name='BW6_PaddedCoat_Tailored';bpy.data.collections['BW6_TORSO_RECONSTRUCTION'].objects.link(coat);coat.hide_render=False;coat.hide_set(False)
# Insert measured horizontal control sections in the long garment faces.
bm=bmesh.new();bm.from_mesh(coat.data)
for z in [1.12,1.18,1.23,1.28,1.33,1.38,1.43,1.48]:
 bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=1e-7,plane_co=Vector((0,0,z)),plane_no=Vector((0,0,1)),clear_inner=False,clear_outer=False)
bm.to_mesh(coat.data);bm.free()
# A single continuous depth warp preserves the prior garment's ordering.
# No independent radial projections of neighboring chest vertices.
stations=[(1.06,.110,.070),(1.18,.120,.065),(1.26,.120,.050),(1.30,.135,.025),(1.34,.132,.018),(1.38,.111,.025),(1.42,.086,.028),(1.46,.058,.018),(1.50,.03,0)]
def profile(z):
 for a,b in zip(stations,stations[1:]):
  if a[0]<=z<=b[0]:
   t=(z-a[0])/(b[0]-a[0]);return a[1]+(b[1]-a[1])*t,a[2]+(b[2]-a[2])*t
 return None
changes=[]
for v in coat.data.vertices:
 p=v.co.copy();prof=profile(p.z)
 if prof and p.y>0 and abs(p.x)<.20:
  central,curve=prof;target=central-curve*(abs(p.x)/.16)**2
  # Original helper front is nearly flat: fit its envelope while retaining
  # depth differences through a positive affine map, with a side fade.
  reference=.1149+(min(1.30,max(1.18,p.z))-1.18)*.213
  if p.z>1.30:reference=.142
  if p.z>1.44:reference=.142-(p.z-1.44)*2.05
  reference=max(.04,reference)
  ratio=max(.20,min(1.20,target/reference));fade=min(1,(.20-abs(p.x))/.025)
  v.co.y=p.y*(1-fade+fade*ratio)
  changes.append(v.index)
bm=bmesh.new();bm.from_mesh(coat.data);bm.verts.ensure_lookup_table()
neck=[e for e in bm.edges if e.is_boundary and all(v.co.z>1.44 for v in e.verts)]
adj={}
for e in neck:
 for v in e.verts:adj.setdefault(v,[]).append(e.other_vert(v))
assert len(adj)>=38 and all(len(v)==2 for v in adj.values()),('neck',len(adj))
start=max(adj,key=lambda v:v.co.x);loop=[start];prev=None
while len(loop)<len(adj):
 nxt=next(v for v in adj[loop[-1]] if v!=prev);assert nxt not in loop
 prev=loop[-1];loop.append(nxt)
points=[v.co.copy() for v in loop];n=len(loop)
area=sum(points[i].x*points[(i+1)%n].y-points[(i+1)%n].x*points[i].y for i in range(n));sign=1 if area>0 else -1
actual=[math.atan2(p.y+.05,p.x) for p in points]
for i in range(1,n):
 while actual[i]-actual[i-1]>math.pi:actual[i]-=2*math.pi
 while actual[i]-actual[i-1]<-math.pi:actual[i]+=2*math.pi
# Isotonic angular fit repairs reversals without rotating the entire collar.
gap=.028;vals=[sign*a-i*gap for i,a in enumerate(actual)];blocks=[]
for i,v in enumerate(vals):
 blocks.append([v,1,[i]])
 while len(blocks)>1 and blocks[-2][0]>blocks[-1][0]:
  b=blocks.pop();a=blocks.pop();w=a[1]+b[1];blocks.append([(a[0]*a[1]+b[0]*b[1])/w,w,a[2]+b[2]])
fit=[0]*n
for value,_,ids in blocks:
 for i in ids:fit[i]=value+i*gap
angles=[sign*v for v in fit]
previous=loop;ring_records=[]
for t in [.12,.45,.92,1.]:
 new=[]
 for i,p in enumerate(points):
  a=angles[i];top=Vector((.128*math.cos(a),-.05+.122*math.sin(a),1.563-.006*max(0,math.sin(a))))
  q=p.lerp(top,t)
  assert q.z>=p.z
  new.append(bm.verts.new(q))
 for i in range(n):k=(i+1)%n;bm.faces.new((previous[i],previous[k],new[k],new[i]))
 previous=new;ring_records.append([list(v.co) for v in new])
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(coat.data);bm.free()
g=coat.vertex_groups.get('spine01') or coat.vertex_groups.new(name='spine01')
for v in coat.data.vertices:
 if not v.groups:g.add([v.index],1,'REPLACE')
# Native whole-garment projection rejected: it created new self folds.
# Surface fit and local remaining collisions are reviewed directly.
solid=next(m for m in coat.modifiers if m.type=='SOLIDIFY');assert abs(solid.thickness-.006)<1e-5 and not solid.use_even_offset
bpy.context.view_layer.objects.active=coat;bpy.ops.object.modifier_move_to_index(modifier=solid.name,index=len(coat.modifiers)-1)
coat['BW6_method']='Return to clean BW5 garment foundation. Continuous positive depth deformation; original neck boundary retained and extruded upwards with monotone arc-length correspondence. No downward bridge into retained shoulder faces.'
out=R/'ada_bw6_torso_fitted_coat.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out))
(R/'records/fitted_coat.json').write_text(json.dumps({'source_object':source.name,'method':coat['BW6_method'],'changed_chest_vertices':changes,'source_neck_points':[list(p) for p in points],'unwrapped_monotone_angles':angles,'new_rings':ring_records},indent=2))
s.cycles.samples=12;s.render.threads=4
for view in ['front','profile','three_quarter','back']:
 s.camera=bpy.data.objects['BW4_Camera_'+view];s.render.filepath=str(R/'captures'/('fitted_'+view+'.png'));bpy.ops.render.render(write_still=True)
print('BW6_FITTED_COAT_COMPLETE')

import bpy,bmesh,math,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'ada_bw6_torso_faceted_study.blend'),use_scripts=False)
s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s;s.frame_set(1)
old=bpy.data.objects['BW6_PaddedCoat_Tailored'];old.name='BW6_FAILED_RadialCoat';old.hide_render=True;old.hide_set(True)
source=bpy.data.objects['BW4_CONTEXT_BW1_CoatUpper_Continuous'];coat=source.copy();coat.data=source.data.copy();coat.name='BW6_PaddedCoat_Tailored';bpy.data.collections['BW6_TORSO_RECONSTRUCTION'].objects.link(coat);coat.hide_render=False;coat.hide_set(False)
# A single continuous depth warp preserves the prior garment's ordering.
# No independent radial projections of neighboring chest vertices.
stations=[(1.055,0),(1.18,0),(1.26,0),(1.30,.04),(1.34,.10),(1.38,.23),(1.42,.36),(1.45,.25),(1.48,0),(1.60,0)]
def factor(z):
 for (z0,a),(z1,b) in zip(stations,stations[1:]):
  if z0<=z<=z1:
   t=(z-z0)/(z1-z0);t=t*t*(3-2*t);return a+(b-a)*t
 return 0
changes=[]
for v in coat.data.vertices:
 p=v.co.copy();xw=max(0,min(1,(.225-abs(p.x))/.075))
 v.co.y-=max(0,p.y-.01)*factor(p.z)*xw
 if (v.co-p).length>1e-8:changes.append(v.index)
bm=bmesh.new();bm.from_mesh(coat.data);bm.verts.ensure_lookup_table()
neck=[e for e in bm.edges if e.is_boundary and all(v.co.z>1.44 for v in e.verts)]
adj={}
for e in neck:
 for v in e.verts:adj.setdefault(v,[]).append(e.other_vert(v))
assert len(adj)==38 and all(len(v)==2 for v in adj.values()),('neck',len(adj))
start=max(adj,key=lambda v:v.co.x);loop=[start];prev=None
while len(loop)<len(adj):
 nxt=next(v for v in adj[loop[-1]] if v!=prev);assert nxt not in loop
 prev=loop[-1];loop.append(nxt)
points=[v.co.copy() for v in loop];n=len(loop)
lengths=[(points[(i+1)%n]-points[i]).length for i in range(n)];perimeter=sum(lengths)
area=sum(points[i].x*points[(i+1)%n].y-points[(i+1)%n].x*points[i].y for i in range(n));sign=1 if area>0 else -1
theta=math.atan2(points[0].y+.05,points[0].x);angles=[];acc=0
for length in lengths:angles.append(theta+sign*2*math.pi*acc/perimeter);acc+=length
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
wrap=coat.modifiers.new('BW6 Cloth exterior clearance AUTHORING_ONLY','SHRINKWRAP');wrap.target=bpy.data.objects['BW4_CONTEXT_BW1_IndexedBody'];wrap.wrap_method='NEAREST_SURFACEPOINT';wrap.wrap_mode='OUTSIDE';wrap.offset=.018
solid=next(m for m in coat.modifiers if m.type=='SOLIDIFY');assert abs(solid.thickness-.006)<1e-5 and not solid.use_even_offset
bpy.context.view_layer.objects.active=coat;bpy.ops.object.modifier_move_to_index(modifier=solid.name,index=len(coat.modifiers)-1)
coat['BW6_method']='Return to clean BW5 garment foundation. Continuous positive depth deformation; original neck boundary retained and extruded upwards with monotone arc-length correspondence. No downward bridge into retained shoulder faces.'
out=R/'ada_bw6_torso_monotone_coat.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out))
(R/'records/monotone_coat.json').write_text(json.dumps({'source_object':source.name,'method':coat['BW6_method'],'changed_chest_vertices':changes,'source_neck_points':[list(p) for p in points],'unwrapped_monotone_angles':angles,'new_rings':ring_records},indent=2))
s.cycles.samples=12;s.render.threads=4
for view in ['front','profile','three_quarter','back']:
 s.camera=bpy.data.objects['BW4_Camera_'+view];s.render.filepath=str(R/'captures'/('monotone_'+view+'.png'));bpy.ops.render.render(write_still=True)
print('BW6_MONOTONE_COAT_COMPLETE')

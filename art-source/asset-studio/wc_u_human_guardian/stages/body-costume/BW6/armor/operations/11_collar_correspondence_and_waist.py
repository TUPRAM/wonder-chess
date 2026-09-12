import bpy,math,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'ada_bw6_torso_sideclosure.blend'),use_scripts=False)
s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s;s.frame_set(1)
coat=bpy.data.objects['BW6_PaddedCoat_Tailored'];me=coat.data
n=json.loads((R/'records/correction1_changes.json').read_text())['neck_outer_loop_count']
adj={i:[] for i in range(len(me.vertices))}
for e in me.edges:
 a,b=e.vertices;adj[a].append(b);adj[b].append(a)
edge_faces={tuple(sorted(e.vertices)):0 for e in me.edges}
for f in me.polygons:
 ids=list(f.vertices)
 for i in range(len(ids)):edge_faces[tuple(sorted((ids[i],ids[(i+1)%len(ids)])))]+=1
top_edges=[e for e,c in edge_faces.items() if c==1 and all(me.vertices[v].co.z>1.54 for v in e)]
boundary={}
for a,b in top_edges:boundary.setdefault(a,[]).append(b);boundary.setdefault(b,[]).append(a)
assert len(boundary)==n and all(len(v)==2 for v in boundary.values()),('top boundary',len(boundary),n)
top=[next(iter(boundary))];prev=None
while len(top)<n:
 nxt=next(v for v in boundary[top[-1]] if v!=prev)
 assert nxt not in top
 prev=top[-1];top.append(nxt)
rings=[top]
for step in range(7):
 current=set(rings[-1]);outside=set(rings[-2]) if len(rings)>1 else set();inner=[]
 for vid in rings[-1]:
  remaining=[v for v in adj[vid] if v not in current and v not in outside]
  assert len(remaining)==1,('ring walk',step,vid,remaining)
  inner.append(remaining[0])
 assert len(set(inner))==n
 rings.append(inner)
ordered=list(reversed(rings));outer_ids=ordered[0];new_rings=ordered[1:]
mapping=[]
for i in range(n):
 p=me.vertices[outer_ids[i]].co.copy()
 a=math.atan2(p.y+.062,p.x)
 lower=Vector((.108*math.cos(a),-.062+.112*math.sin(a),1.489+.032*math.cos(a)**2-.020*max(0,math.sin(a))))
 top=Vector((.130*math.cos(a),-.049+.124*math.sin(a),1.557-.006*max(0,math.sin(a))))
 for j,t in enumerate([.38,.72,1.]):me.vertices[new_rings[j][i]].co=p.lerp(lower,t)
 for j,t in enumerate([.05,.35,.88,1.]):me.vertices[new_rings[j+3][i]].co=lower.lerp(top,t)
 mapping.append({'outer_vertex':outer_ids[i],'new_ring_vertices':[r[i] for r in new_rings],'angle_radians':a})
me.update()
wrap=coat.modifiers.new('BW6 Garment outside body AUTHORING_ONLY','SHRINKWRAP');wrap.target=bpy.data.objects['BW4_CONTEXT_BW1_IndexedBody'];wrap.wrap_method='NEAREST_SURFACEPOINT';wrap.wrap_mode='OUTSIDE';wrap.offset=.012
solid=next(m for m in coat.modifiers if m.type=='SOLIDIFY');bpy.context.view_layer.objects.active=coat
bpy.ops.object.modifier_move_to_index(modifier=solid.name,index=len(coat.modifiers)-1)
coat['BW6_interface_method']='Collar rings follow actual outer-boundary angular correspondence instead of equal angular allocation. Raised saddle base. Whole garment outside-only body constraint precedes final6mm inward wall.'
# Refitted waist layer: top is an overlap behind the plate, not a visible lip.
navy=bpy.data.objects['BW6_NavyWaist'];original=[]
for v in navy.data.vertices:
 p=v.co.copy();d=Vector((p.x,p.y+.025,0)).normalized()
 t=max(0,min(1,(p.z-1.14)/.055))
 v.co-=d*(.009*t)
 original.append({'index':v.index,'before':list(p),'after':list(v.co)})
navy.data.update()
coat.hide_set(False);coat.hide_render=False
s['BW6_interface_revision']='Replaced ring correspondence at collar; outside-only body safeguard expanded to complete garment. Navy upper edge refitted inward9mm while keeping lower contour.'
out=R/'ada_bw6_torso_interface_work.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out))
(R/'records/collar_correspondence.json').write_text(json.dumps({'method':'New correspondence and saddle surface, not broad smoothing','collar_mapping':mapping,'navy_changes':original,'clearance_method':'Native OUTSIDE-only garment constraint; not rigid plate collision physics'},indent=2))
s.cycles.samples=12;s.render.threads=4
for view in ['front','profile','three_quarter','back']:
 s.camera=bpy.data.objects['BW4_Camera_'+view];s.render.filepath=str(R/'captures'/('interface_'+view+'.png'));bpy.ops.render.render(write_still=True)
print('BW6_INTERFACE_COMPLETE')

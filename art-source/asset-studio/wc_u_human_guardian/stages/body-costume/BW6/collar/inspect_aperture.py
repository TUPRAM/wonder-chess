import bpy,bmesh,json,math,hashlib
from pathlib import Path
R=Path(__file__).parent;src=R.parent/'armor/ada_bw6_upper_integrated_r002.blend';bpy.ops.wm.open_mainfile(filepath=str(src),use_scripts=False);o=bpy.data.objects['BW6_PaddedCoat_Tailored'];bm=bmesh.new();bm.from_mesh(o.data);ring={v for e in bm.edges if e.is_boundary and all(v.co.z>1.54 for v in e.verts) for v in e.verts};previous=set();bands=[]
for step in range(4):
 faces={f for v in ring for f in v.link_faces if not any(x in previous for x in f.verts)};next_ring={v for f in faces for v in f.verts if v not in ring};bands.append({'step':step,'ring':len(ring),'faces':len(faces),'next':len(next_ring)});previous,ring=ring,next_ring
# The prospective shared host boundary, before any mesh change.
edges=[e for e in bm.edges if all(v in ring for v in e.verts) and any(f in faces for f in e.link_faces)];adj={}
for e in edges:
 for v in e.verts:adj.setdefault(v,[]).append(e.other_vert(v))
print("BANDS",bands,"DEGREES",[(tuple(k.co),len(v)) for k,v in adj.items() if len(v)!=2]);assert all(len(v)==2 for v in adj.values());v=max(adj,key=lambda q:q.co.x);loop=[v];prev=None
while len(loop)<len(adj):
 nxt=next(q for q in adj[loop[-1]] if q!=prev);assert nxt not in loop;prev=loop[-1];loop.append(nxt)
points=[list(v.co) for v in loop];angles=[math.atan2((p[1]+.05)/.112,p[0]/.11) for p in points];area=sum(points[i][0]*points[(i+1)%len(points)][1]-points[(i+1)%len(points)][0]*points[i][1] for i in range(len(points)));sign=1 if area>0 else -1;steps=[]
for i,a in enumerate(angles):
 dt=(angles[(i+1)%len(angles)]-a+math.pi)%(2*math.pi)-math.pi;steps.append(sign*dt)
record={'source':str(src),'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'bands':bands,'boundary_controls':len(loop),'lower_z_m':[min(p[2] for p in points),max(p[2] for p in points)],'negative_angular_steps':sum(x<-.0001 for x in steps),'near_zero_steps_lt_001rad':sum(abs(x)<.001 for x in steps),'angular_step_range_rad':[min(steps),max(steps)],'steps_rad':steps,'points_m':points};(R/'records/aperture_inspection.json').write_text(json.dumps(record,indent=2));print({k:v for k,v in record.items() if k not in ['points_m','steps_rad']});bm.free()

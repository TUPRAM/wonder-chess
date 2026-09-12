import bpy, bmesh, math, json, hashlib
from pathlib import Path
from mathutils import Vector

R=Path(__file__).parent
src=R.parent/'armor/ada_bw6_upper_integrated_r002.blend'
source_hash=hashlib.sha256(src.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(src),use_scripts=False)
s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s;s.frame_set(1)
old=bpy.data.objects['BW6_PaddedCoat_Tailored']
o=old.copy();o.data=old.data.copy();o.name='BW6_CollarBalanced_CoatCandidate';s.collection.objects.link(o)
old.hide_render=True;old.hide_set(True);o.hide_render=False;o.hide_set(False)
bm=bmesh.new();bm.from_mesh(o.data);deform=bm.verts.layers.deform.verify()
ring={v for e in bm.edges if e.is_boundary and all(v.co.z>1.54 for v in e.verts) for v in e.verts}
previous=set();removed_faces=set();upper=set()
for step in range(4):
    faces={f for v in ring for f in v.link_faces if not any(x in previous for x in f.verts)}
    nxt={v for f in faces for v in f.verts if v not in ring}
    assert len(ring)==len(faces)==len(nxt)==92
    upper.update(ring);removed_faces.update(faces);previous,ring=ring,nxt
host=set(bm.verts)-upper
before={id(v):(v.co.copy(),dict(v[deform])) for v in host if v not in ring}
base_count=len(ring)
bmesh.ops.delete(bm,geom=list(removed_faces),context='FACES_ONLY')
bmesh.ops.delete(bm,geom=list(upper),context='VERTS')

def ordered_boundary():
    edges=[e for e in bm.edges if e.is_boundary and all(v.co.z>1.443 for v in e.verts)]
    adj={}
    for e in edges:
        for v in e.verts:adj.setdefault(v,[]).append(e.other_vert(v))
    assert adj and all(len(q)==2 for q in adj.values()),[(list(v.co),len(q)) for v,q in adj.items() if len(q)!=2]
    loop=[max(adj,key=lambda v:v.co.x)];prev=None
    while len(loop)<len(adj):
        nxt=next(q for q in adj[loop[-1]] if q!=prev);assert nxt not in loop
        prev=loop[-1];loop.append(nxt)
    area=sum(loop[i].co.x*loop[(i+1)%len(loop)].co.y-loop[(i+1)%len(loop)].co.x*loop[i].co.y for i in range(len(loop)))
    if area<0:loop=[loop[0]]+list(reversed(loop[1:]))
    return loop

def angle(v):return math.atan2((v.co.y+.05)/.112,v.co.x/.110)
def step(a,b):return (angle(b)-angle(a)+math.pi)%(2*math.pi)-math.pi
merges=[]
for iteration in range(100):
    loop=ordered_boundary();pairs=[(step(a,loop[(i+1)%len(loop)]),a,loop[(i+1)%len(loop)]) for i,a in enumerate(loop)]
    gap,a,b=min(pairs,key=lambda q:q[0])
    if gap>=.048:break
    co=(a.co+b.co)*.5
    merges.append({'a':list(a.co),'b':list(b.co),'result':list(co),'angle_rad':gap})
    bmesh.ops.pointmerge(bm,verts=[a,b],merge_co=co)
else:raise RuntimeError('Boundary consolidation did not terminate')

splits=[]
for iteration in range(100):
    loop=ordered_boundary();pairs=[(step(a,loop[(i+1)%len(loop)]),a,loop[(i+1)%len(loop)]) for i,a in enumerate(loop)]
    gap,a,b=max(pairs,key=lambda q:q[0])
    if gap<=.15:break
    edge=next(e for e in a.link_edges if e.other_vert(a)==b)
    splits.append({'a':list(a.co),'b':list(b.co),'angle_rad':gap})
    bmesh.utils.edge_split(edge,a,.5)
else:raise RuntimeError('Boundary subdivision did not terminate')

loop=ordered_boundary();n=len(loop);bands=[loop]
for t in [.22,.48,.74,1.0]:
    row=[]
    for v in loop:
        a=angle(v);top=Vector((.128*math.cos(a),-.05+.122*math.sin(a),1.563-.006*max(0,math.sin(a))))
        nv=bm.verts.new(v.co.lerp(top,t))
        for group,weight in v[deform].items():nv[deform][group]=weight
        row.append(nv)
    prior=bands[-1]
    for i in range(n):bm.faces.new((prior[i],prior[(i+1)%n],row[(i+1)%n],row[i]))
    bands.append(row)
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
# The coat's open ends do not establish global orientation; anchor it to an unchanged front field.
front=[f for f in bm.faces if .05<f.calc_center_median().y and 1.2<f.calc_center_median().z<1.4]
if sum(f.normal.y for f in front)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
for f in bm.faces:f.smooth=True
errors=[list(v.co) for v in bm.verts if id(v) in before and (v.co-before[id(v)][0]).length>1e-8]
assert not errors,errors
boundary_edges=[e for e in bm.edges if e.is_boundary]
nonmanifold=[e for e in bm.edges if len(e.link_faces)>2]
assert not nonmanifold
bm.verts.ensure_lookup_table();bm.verts.index_update()
final_angles=[step(v,loop[(i+1)%n]) for i,v in enumerate(loop)]
record={'source':str(src),'sha256':source_hash,'candidate_object':o.name,'method':'Remove four inherited collar bands. Consolidate only neighboring host aperture controls below .048 radians, split gaps above .15 radians, then author four evenly spaced height bands. No broad smoothing, wrap, or body/sleeve coordinate edits.','initial_controls':base_count,'final_controls':n,'merges':merges,'splits':splits,'angular_range_rad':[min(final_angles),max(final_angles)],'unrelated_host_coordinates_preserved':not errors,'base_vertex_indices':[v.index for v in loop],'top_vertex_indices':[v.index for v in bands[-1]],'boundary_edges':len(boundary_edges),'nonmanifold_edges':len(nonmanifold),'base_z_m':[min(v.co.z for v in loop),max(v.co.z for v in loop)],'top_edge_mm':[1000*(bands[-1][i].co-bands[-1][(i+1)%n].co).length for i in range(n)]}
bm.to_mesh(o.data);bm.free();o.data.update()
o['BW6_status']='ART_REVISE_UNREVIEWED';o['BW6_method']='Independent local aperture topology replacement; body/sleeve protected'
assert o.data!=old.data
out=R/'ada_bw6_balanced_collar_initial.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(out),check_existing=False)
record['candidate']=str(out);record['candidate_sha256']=hashlib.sha256(out.read_bytes()).hexdigest();assert hashlib.sha256(src.read_bytes()).hexdigest()==source_hash
(R/'records/balanced_initial_construction.json').write_text(json.dumps(record,indent=2))
print('COLLAR_INITIAL',n,len(merges),len(splits),min(record['top_edge_mm']),max(record['top_edge_mm']),record['candidate_sha256'])

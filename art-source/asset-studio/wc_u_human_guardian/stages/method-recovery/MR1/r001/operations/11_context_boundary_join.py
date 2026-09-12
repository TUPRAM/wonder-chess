import bpy,bmesh,json,math
from mathutils import Vector
root='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/method-recovery/MR1/r001'
sc=bpy.data.scenes['MR1_CONTEXT_HEAD_CANDIDATE'];bpy.context.window.scene=sc
bpy.ops.wm.save_as_mainfile(filepath=root+'/context_before_join.blend',copy=True)
col=bpy.data.collections['MR1_CONTEXT_CANDIDATE_ALLOWLIST']
# Join the two editable interface cages at their shared nose bridge first.
verts=[];faces=[]
for side in ['R','L']:
    o=bpy.data.objects['MR1_CONTEXT_Orbital_Cage_'+side];off=len(verts)
    for v in o.data.vertices:
        p=v.co.copy()
        if v.index in [80,81,98,99]:p.x=0
        verts.append(tuple(p))
    faces.extend([tuple(off+i for i in f.vertices) for f in o.data.polygons])
me=bpy.data.meshes.new('MR1_Context_Two_Eye_Cage_Mesh');me.from_pydata(verts,[],faces);me.update()
bm=bmesh.new();bm.from_mesh(me);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00001);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
cage=bpy.data.objects.new('MR1_CONTEXT_Two_Eye_Source_Cage',me);col.objects.link(cage);me.materials.append(bpy.data.materials['MR1_Uniform_Clay'])
sub=cage.modifiers.new('One level for contextual join','SUBSURF');sub.levels=1;sub.render_levels=1
for f in me.polygons:f.use_smooth=True
deps=bpy.context.evaluated_depsgraph_get();evaluated=cage.evaluated_get(deps);face_me=bpy.data.meshes.new_from_object(evaluated)
def boundary_loops(bm):
    boundary=[e for e in bm.edges if e.is_boundary];remaining=set(boundary);loops=[]
    while remaining:
        edge=remaining.pop();a,b=edge.verts;loop=[a,b];current=b;first=a
        while current!=first:
            opts=[e for e in current.link_edges if e in remaining]
            if not opts:break
            e=opts[0];remaining.remove(e);current=e.other_vert(current)
            if current!=first:loop.append(current)
        if current!=first:raise RuntimeError('Open branching boundary in contextual join')
        loops.append(loop)
    return loops
def perimeter(loop):
    return sum((loop[i].co-loop[(i+1)%len(loop)].co).length for i in range(len(loop)))
fb=bmesh.new();fb.from_mesh(face_me);fb.verts.ensure_lookup_table();face_loops=boundary_loops(fb);outer=max(face_loops,key=perimeter)
# Expand the curved interface contour slightly so old skin cannot remain beneath
# the new regional surface. The retained surface starts outside the new region.
outline=[(v.co.x*1.065,1.687+(v.co.z-1.687)*1.065) for v in outer]
def inside(x,z):
    hit=False;j=len(outline)-1
    for i in range(len(outline)):
        a,b=outline[i];c,d=outline[j]
        if ((b>z)!=(d>z)) and x<(c-a)*(z-b)/(d-b)+a:hit=not hit
        j=i
    return hit
hb=bmesh.new();hb.from_mesh(bpy.data.objects['ADA_Head_Continuous'].data)
remove=[f for f in hb.faces if f.calc_center_median().y>-.025 and inside(f.calc_center_median().x,f.calc_center_median().z)]
bmesh.ops.delete(hb,geom=remove,context='FACES');head_loops=boundary_loops(hb)
# The largest new face boundary is identified by perimeter and frontward center.
def face_boundary_score(loop):
    return perimeter(loop) if sum(v.co.y for v in loop)/len(loop)>-.04 else 0
border=max(head_loops,key=face_boundary_score)
# Build a continuous bridge with a zipper triangulation between unequal boundary
# counts. This is a contextual join outside the orbit, not an iris radial fan.
hb.verts.ensure_lookup_table();hb.faces.ensure_lookup_table();fb.verts.ensure_lookup_table()
outverts=[tuple(v.co) for v in hb.verts];outfaces=[tuple(v.index for v in f.verts) for f in hb.faces]
offset=len(outverts);outverts += [tuple(v.co) for v in fb.verts];outfaces += [tuple(offset+v.index for v in f.verts) for f in fb.faces]
A=[offset+v.index for v in outer];B=[v.index for v in border]
# Rotate both loops to the closest pair; choose their matching traversal.
best=(1e9,0,0)
for i,ai in enumerate(A):
    for j,bj in enumerate(B):
        d=(Vector(outverts[ai])-Vector(outverts[bj])).length_squared
        if d<best[0]:best=(d,i,j)
A=A[best[1]:]+A[:best[1]];B=B[best[2]:]+B[:best[2]]
if (Vector(outverts[A[1]])-Vector(outverts[B[-1]])).length_squared < (Vector(outverts[A[1]])-Vector(outverts[B[1]])).length_squared:B=[B[0]]+list(reversed(B[1:]))
i=j=0;bridge=0
while i<len(A) or j<len(B):
    ai=A[i%len(A)];bj=B[j%len(B)]
    if i==len(A):advance_a=False
    elif j==len(B):advance_a=True
    else:
        da=(Vector(outverts[A[(i+1)%len(A)]])-Vector(outverts[bj])).length_squared
        db=(Vector(outverts[ai])-Vector(outverts[B[(j+1)%len(B)]])).length_squared
        advance_a=da<db
    if advance_a:outfaces.append((ai,A[(i+1)%len(A)],bj));i+=1
    else:outfaces.append((ai,B[(j+1)%len(B)],bj));j+=1
    bridge+=1
joined_me=bpy.data.meshes.new('MR1_Context_Joined_Head_Mesh');joined_me.from_pydata(outverts,[],outfaces);joined_me.update()
jb=bmesh.new();jb.from_mesh(joined_me);bmesh.ops.recalc_face_normals(jb,faces=list(jb.faces));jb.to_mesh(joined_me)
audit={'head_cut_faces':len(remove),'eye_cage_boundary_loops':[len(l) for l in face_loops],'head_boundary_loops':[len(l) for l in head_loops],'outer_face_vertices':len(A),'outer_head_vertices':len(B),'bridge_faces':bridge,'degenerate_faces':sum(f.calc_area()<1e-12 for f in jb.faces),'nonmanifold_internal':sum(len(e.link_faces)>2 for e in jb.edges),'boundary_edges':sum(e.is_boundary for e in jb.edges)}
jb.free();fb.free();hb.free()
joined=bpy.data.objects.new('MR1_CONTEXT_Joined_Head_Diagnostic',joined_me);col.objects.link(joined);joined_me.materials.append(bpy.data.materials['MR1_Uniform_Clay'])
for f in joined_me.polygons:f.use_smooth=True
joined['scope']='Connected contextual evaluation mesh; editable orbital cage retained separately; production topology and expression unapproved';joined['mr1_join_audit']=json.dumps(audit)
for n in ['MR1_CONTEXT_Retained_Head_Outside_Orbital_Regions','MR1_CONTEXT_Orbital_Cage_R','MR1_CONTEXT_Orbital_Cage_L','MR1_CONTEXT_Two_Eye_Source_Cage']:
    o=bpy.data.objects[n];o.hide_render=True;o.hide_set(True)
sc['mr1_context_join_pass']=1
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
for v in ['front','three_quarter','profile']:
    sc.camera=bpy.data.objects['MR1_CONTEXT_'+v];sc.render.filepath=root+'/captures/context_joined_r001_'+v+'.png';bpy.ops.render.render(write_still=True)
print(json.dumps(audit))

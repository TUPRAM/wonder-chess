import bpy,bmesh,json,math
from mathutils import Vector
ROOT='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/head-polish/HP1/r001'
s=bpy.data.scenes['HP1_HEAD_POLISH'];bpy.context.window.scene=s
assert bpy.data.objects.get('HP1_HEAD_POLISH_Head_r008') is None
old=bpy.data.objects['HP1_HEAD_POLISH_Head_r007'];f=json.loads(old['feature_indices']);nose=f['nose']
verts=[tuple(v.co) for v in old.data.vertices];newrow=[];edge_mids={}
# Add a real transverse bulb section between the existing nostril/columella
# row and bridge. This gives the tip independent volume instead of relying
# on one pointed midline vertex. Split all adjoining edges consistently.
for j in range(9):
    a=nose[18+j];b=nose[27+j];p=(old.data.vertices[a].co+old.data.vertices[b].co)*.5
    q=(j-4)/4
    if 0<j<8:
        p.x=[0,-.014,-.010,-.0055,0,.0055,.010,.014,0][j]
        p.y=[0,.080,.087,.092,.093,.092,.087,.080,0][j]
        p.z=[0,1.658,1.661,1.663,1.664,1.663,1.661,1.658,0][j]
    idx=len(verts);newrow.append(idx);verts.append(tuple(p));edge_mids[tuple(sorted((a,b)))]=idx
strip={frozenset((nose[18+j],nose[18+j+1],nose[27+j+1],nose[27+j])):j for j in range(8)}
faces=[]
for poly in old.data.polygons:
    ids=list(poly.vertices);key=frozenset(ids)
    if key in strip:
        j=strip[key];a=nose[18+j];b=nose[18+j+1];c=nose[27+j+1];d=nose[27+j]
        faces.extend([(a,b,newrow[j+1],newrow[j]),(newrow[j],newrow[j+1],c,d)])
    else:
        out=[]
        for k,a in enumerate(ids):
            b=ids[(k+1)%len(ids)];out.append(a);edge=tuple(sorted((a,b)))
            if edge in edge_mids:out.append(edge_mids[edge])
        faces.append(tuple(out))
m=bpy.data.meshes.new('HP1_Head_r008_NasalBulb');m.from_pydata(verts,[],faces);m.update()
h=old.copy();h.data=m;h.name='HP1_HEAD_POLISH_Head_r008';s.collection.objects.link(h);old.hide_render=True;old.hide_set(True)
for mat in old.data.materials:m.materials.append(mat)
for p in m.polygons:p.use_smooth=True
h['nasal_bulb_section']=json.dumps(newrow)
# Additional clearance for the subdivided outer lid body. Control vertices
# on a globe do not guarantee the subdivided faces enclose that globe.
orbits=json.loads(h['orbital_rings'])
for ring in orbits:
    for layer in [2,3,4]:
        for i in ring[layer*20:(layer+1)*20]:
            p=m.vertices[i].co;p.y+=[0,0,.0011,.0018,.0008][layer]
    for i in ring[:20]:m.vertices[i].co.y+=.0008
for side in ['R','L']:bpy.data.objects['HP1_HEAD_POLISH_Eye_'+side].scale=(.0207/.0245,)*3
# Upper lip roll, preserving mouth contact and overall width.
for local,i in enumerate(f['mouth']):
    layer=local//34;p=m.vertices[i].co;q=min(1,abs(p.x)/.025)
    if p.z>1.626 and layer==4:p.y+=.002*(1-q*q);p.z+=.0014*(1-q*q)
    if p.z>1.628 and layer==5:p.z+=.0005*(1-q*q)
# A compact, gently rounded chin rather than the elongated frontal block.
for v in m.vertices:
    p=v.co
    if v.index<764 and p.y>.030 and 1.567<p.z<1.612:
        w=math.exp(-((p.z-1.580)/.012)**2)*math.exp(-(p.x/.045)**4)
        p.z+=.0035*w
        p.y+=.001*math.exp(-((p.z-1.591)/.011)**2)*math.exp(-(p.x/.035)**4)
m.update();bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(m);bm.free()
bpy.ops.object.select_all(action='DESELECT');h.select_set(True);bpy.context.view_layer.objects.active=h
h['revision_notes']='Independent added nasal bulb control section with shared edge splits, upper vermilion roll, compact chin and subdivided lid clearance.'
s['render_allowlist']=json.dumps([o.name for o in s.objects if not o.hide_render])
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
for label in ['front','profile','three_quarter','portrait']:
    s.camera=bpy.data.objects[s.name+'_'+label];s.render.filepath=ROOT+'/captures/r008_'+label+'.png';bpy.ops.render.render(write_still=True)
print('HP1 r008 independent nasal bulb and mouth/chin correction rendered.')

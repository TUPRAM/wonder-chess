import bpy,bmesh,json,math
from mathutils import Vector
assert bpy.data.scenes.get('FH1_COMBINED_HEAD') is None
if bpy.context.mode!='OBJECT':bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.wm.save_as_mainfile(filepath=ROOT+'/feature_studies_checkpoint.blend',copy=True)
source=bpy.data.objects['FH1_Head_Shape_Control_Cage']
verts=[tuple(v.co) for v in source.data.vertices[:840]];faces=[];groups={};joins={}
ear_r=(22,27,8,13);ear_l=(37,42,8,13)
ports=[NOSE_PORT,MOUTH_PORT,EYE_PORT_R,EYE_PORT_L,ear_r,ear_l]
for r in range(20):
    for c in range(40):
        skip=False
        for c0,c1,r0,r1 in ports:
            if r0<=r<r1 and any(k%40==c for k in range(c0,c1)):skip=True
        if not skip:faces.append((r*40+c,r*40+(c+1)%40,(r+1)*40+(c+1)%40,(r+1)*40+c))
# Taper the lower occiput into the mandibular/neck region. This is an explicit
# landmark shape correction, not smoothing over a face patch.
rear_depths=[-.057,-.064,-.073,-.084,-.092,-.098,-.103]
for r,rear in enumerate(rear_depths):
    z,w,front,side,old_rear=HEAD_ROWS[r]
    for j in range(1,16):
        idx=r*40+24+j;x,y,z=verts[idx];a=math.pi*j/16
        verts[idx]=(x,side+(rear-side)*math.sin(a),z)
# Replace the pole fan with a small quad crown patch, preserving its ring.
grid=[[None]*11 for r in range(11)]
perimeter=[(0,c) for c in range(10)]+[(r,10) for r in range(10)]+[(10,c) for c in range(10,0,-1)]+[(r,0) for r in range(10,0,-1)]
for j,(r,c) in enumerate(perimeter):grid[r][c]=800+j
for r in range(1,10):
    for c in range(1,10):
        u=c/10;v=r/10
        b=Vector(verts[grid[0][c]]);t=Vector(verts[grid[10][c]])
        l=Vector(verts[grid[r][0]]);rr=Vector(verts[grid[r][10]])
        bl=Vector(verts[grid[0][0]]);br=Vector(verts[grid[0][10]])
        tl=Vector(verts[grid[10][0]]);tr=Vector(verts[grid[10][10]])
        p=b*(1-v)+t*v+l*(1-u)+rr*u-(bl*(1-u)*(1-v)+br*u*(1-v)+tl*(1-u)*v+tr*u*v)
        p.z=1.794+.0035*math.sin(math.pi*u)*math.sin(math.pi*v)
        grid[r][c]=len(verts);verts.append(tuple(p))
for r in range(10):
    for c in range(10):faces.append((grid[r][c],grid[r][c+1],grid[r+1][c+1],grid[r+1][c]))

def attach_data(name,data,port,root_order=None,mirror=False):
    roots=data['root_loop'] if root_order is None else root_order
    target=[r*40+c%40 for r,c in port_coords(port)]
    assert len(roots)==len(target)
    remap={}
    for a,b in zip(roots,target):
        p=data['vertices'][a];verts[b]=(-p[0],p[1],p[2]) if mirror else p;remap[a]=b
    allids=[]
    for i,p in enumerate(data['vertices']):
        if i not in remap:
            remap[i]=len(verts);verts.append((-p[0],p[1],p[2]) if mirror else p)
        allids.append(remap[i])
    for f in data['faces']:faces.append(tuple(remap[i] for i in f))
    groups[name]=allids;joins[name]=target

def data_from_object(name):
    o=bpy.data.objects[name]
    return {'vertices':[tuple(v.co) for v in o.data.vertices],'faces':[list(p.vertices) for p in o.data.polygons],'root_loop':json.loads(o['interface_indices'])}

attach_data('Nose',data_from_object('FH1_Nose_Control_Cage_r002'),NOSE_PORT)
attach_data('Mouth',data_from_object('FH1_Mouth_Control_Cage_r002'),MOUTH_PORT)
ear=data_from_object('FH1_Ear_R_Control_Cage_r002')
attach_data('Ear_R',ear,ear_r,[(13-j)%20 for j in range(20)])
attach_data('Ear_L',ear,ear_l,[(7+j)%20 for j in range(20)],True)

def orbital_data():
    # Deliberate upper/lower and finite corner landmarks, ordered to match the
    # planned 20-vertex socket port. Only lid margins use the globe guide.
    aperture=[(20,1686),(26,1683.5),(33,1682.5),(40,1682.6),(47,1683.7),
              (55,1686),(58,1688),(58,1690),(56,1692.5),(53,1695.5),
              (49,1697.5),(43,1699),(36,1699),(29,1697.5),(24,1694.5),
              (20,1691.5),(19,1690),(18.8,1688.5),(19,1687.5),(19.5,1686.7)]
    outside=[grid_point(r,c) for r,c in port_coords(EYE_PORT_R)]
    vs=[]
    for layer in range(5):
        for j,(xm,zm) in enumerate(aperture):
            x=xm*.001;z=zm*.001;dx=x-.038;dz=z-1.690
            if layer==0:
                y=.026+math.sqrt(max(.000001,.0245**2-dx*dx-dz*dz))+.0006
            elif layer==1:
                x+=dx*.028;z+=dz*.07
                y=.026+math.sqrt(max(.000001,.0245**2-(x-.038)**2-(z-1.690)**2))+.0016
            elif layer==2:
                x+=dx*.08;z+=dz*.28
                y=.026+math.sqrt(max(.000001,.0245**2-(x-.038)**2-(z-1.690)**2))+.0024
            elif layer==3:
                p=Vector(vs[40+j])*.48+Vector(outside[j])*.52;x,y,z=p
                y+=.0015
            else:x,y,z=outside[j]
            vs.append((x,y,z))
    fs=[(k*20+j,k*20+(j+1)%20,(k+1)*20+(j+1)%20,(k+1)*20+j) for k in range(4) for j in range(20)]
    return {'vertices':vs,'faces':fs,'root_loop':list(range(80,100))}
orbital=orbital_data();attach_data('Orbital_R',orbital,EYE_PORT_R)
# Left port runs in the opposite anatomical order; mirrored right positions
# map directly to the mirrored grid keys, using an explicit key lookup.
right_keys=port_coords(EYE_PORT_R);left_keys=port_coords(EYE_PORT_L)
ordered=[80+right_keys.index((r,24-c)) for r,c in left_keys]
attach_data('Orbital_L',orbital,EYE_PORT_L,ordered,True)

# Discard unused scaffold vertices and reuse one index per shared boundary.
used=sorted({i for f in faces for i in f});mapping={old:new for new,old in enumerate(used)}
data={'vertices':[verts[i] for i in used],'faces':[tuple(mapping[i] for i in f) for f in faces],
      'root_loop':[mapping[i] for i in range(40)],
      'named_vertex_groups':{name:[mapping[i] for i in ids if i in mapping] for name,ids in groups.items()},
      'design_notes':'Original continuous sparse head with shared-index nose/mouth/orbital/ear interfaces, original jaw/skull, quad crown. No rejected head or zipper bridge used. Eyes remain diagnostic construction context.'}
scene,col=fh_scene('FH1_COMBINED_HEAD',(0,-.008,1.680),.290)
head=fh_mesh('FH1_Combined_Head_Control_Cage',data,col)
for name,ids in joins.items():
    vg=head.vertex_groups.new(name=name+'_Joined_Interface');vg.add([mapping[i] for i in ids],1,'REPLACE')
head['shared_interfaces']=json.dumps({name:len(ids) for name,ids in joins.items()})
for sign,label in [(1,'R'),(-1,'L')]:
    bpy.ops.mesh.primitive_uv_sphere_add(segments=64,ring_count=32,radius=.0245,location=(sign*.038,.026,1.690))
    o=bpy.context.object;o.name='FH1_Diagnostic_Eye_'+label
    for collection in list(o.users_collection):collection.objects.unlink(o)
    col.objects.link(o)
    for name in ['MR1_Diagnostic_Sclera','MR1_Diagnostic_Iris','MR1_Diagnostic_Pupil']:o.data.materials.append(bpy.data.materials[name])
    o.data.update()
    for f in o.data.polygons:
        f.use_smooth=True;p=f.center;r=math.sqrt(p.x*p.x+p.z*p.z)
        f.material_index=2 if p.y>0 and r<.0035 else 1 if p.y>0 and r<.0082 else 0
    o['status']='Diagnostic gaze and lid-clearance guide, no production material'
bpy.ops.object.select_all(action='DESELECT');head.select_set(True);bpy.context.view_layer.objects.active=head
scene['render_allowlist']=json.dumps([o.name for o in col.objects]);scene['status']='Combined head candidate, awaiting visual review; no human approval'
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
for label in ['front','profile','three_quarter','underside']:
    scene.camera=bpy.data.objects[scene.name+'_'+label];scene.render.filepath=ROOT+'/captures/combined_initial_'+label+'.png';bpy.ops.render.render(write_still=True)
print('FH1_COMBINED '+json.dumps({'vertices':len(head.data.vertices),'faces':len(head.data.polygons),'interfaces':head['shared_interfaces'],'allowlist':[o.name for o in col.objects]}))

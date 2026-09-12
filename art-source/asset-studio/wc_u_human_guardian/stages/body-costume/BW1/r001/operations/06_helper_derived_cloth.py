import bpy,math,json
from mathutils import Vector,Matrix
s=bpy.data.scenes['BW1_BODY_COSTUME'];body=bpy.data.objects['BW1_IndexedBody'];rig=bpy.data.objects['BW1_Temporary_Pose_Rig']
assert 'BW1_PaddedTorso' not in bpy.data.objects
states=[(m,m.show_viewport) for m in body.modifiers]
for m,_ in states:m.show_viewport=False
dg=bpy.context.evaluated_depsgraph_get();dg.update();ev=body.evaluated_get(dg)
points=[body.matrix_world@v.co for v in ev.data.vertices]
group_names={g.index:g.name for g in body.vertex_groups};bone_names=set(rig.data.bones.keys())
source_weights=[{group_names[g.group]:g.weight for g in v.groups if group_names[g.group] in bone_names and g.weight>.0001} for v in body.data.vertices]
helper_idx=body.vertex_groups['helper-tights'].index
helper_ids={v.index for v in body.data.vertices if any(g.group==helper_idx and g.weight>.5 for g in v.groups)}
helper_faces=[list(p.vertices) for p in body.data.polygons if all(i in helper_ids for i in p.vertices)]
for m,state in states:m.show_viewport=state
def make_part(name,verts,faces,weights=None,source_ids=None,thickness=0.003,subdivision=1):
    mesh=bpy.data.meshes.new(name+'_Cage');mesh.from_pydata(verts,[],faces);mesh.update()
    ob=bpy.data.objects.new(name,mesh);bpy.data.collections['BW1_CLOTH'].objects.link(ob);ob.data.materials.append(bpy.data.materials['BW1_Uniform_Clay'])
    for p in mesh.polygons:p.use_smooth=True
    ob['approval']='CANDIDATE';ob['wc_part_id']=name;ob['body_family']='MPFB_hm08_BW1'
    if source_ids:
        attr=mesh.attributes.new('mpfb_source_index','INT','POINT')
        for item,idx in zip(attr.data,source_ids):item.value=idx
    if weights:
        for bn in sorted({bn for w in weights for bn in w}):
            g=ob.vertex_groups.new(name=bn)
            for i,w in enumerate(weights):
                total=sum(w.values())
                if bn in w and total>0:g.add([i],w[bn]/total,'REPLACE')
        ob.parent=rig;ob.matrix_parent_inverse=rig.matrix_world.inverted();mod=ob.modifiers.new('Temporary articulation','ARMATURE');mod.object=rig;mod.use_deform_preserve_volume=False
    if subdivision:
        mod=ob.modifiers.new('Editable surface subdivision','SUBSURF');mod.levels=subdivision;mod.render_levels=subdivision
    if thickness:
        mod=ob.modifiers.new('Garment thickness','SOLIDIFY');mod.thickness=thickness;mod.offset=-1;mod.use_even_offset=True
    return ob
def center(face):return sum((points[i] for i in face),Vector())/len(face)
land=json.loads(s['body_landmarks_initial'])
def sleeve_offset(co,side):
    a=Vector((side*.18185,-.04636,1.44498));b=Vector((side*.36106,-.04210,1.24891));c=Vector((side*.48638,.11233,1.11225))
    best=None
    for p,q in [(a,b),(b,c)]:
        t=max(0,min(1,(co-p).dot(q-p)/(q-p).length_squared));axis=p+(q-p)*t;d=co-axis
        if best is None or d.length<best[0]:best=(d.length,axis,d)
    d=best[2];return co+d.normalized()*.017 if d.length>.001 else co
for name,kind in [('BW1_PaddedTorso','torso'),('BW1_Sleeve_R','right'),('BW1_Sleeve_L_Blockout','left'),('BW1_Leggings','legs')]:
    selected=[]
    for f in helper_faces:
        c=center(f);x=abs(c.x)
        keep=(c.z>1.075 and c.z<1.535 and x<.214) if kind=='torso' else ((c.x>.19 if kind=='right' else c.x<-.19) and x<.457 and c.z>1.115) if kind in {'right','left'} else .18<c.z<1.10
        if keep:selected.append(f)
    ids=sorted({i for f in selected for i in f});mapping={old:new for new,old in enumerate(ids)};verts=[]
    for i in ids:
        co=points[i].copy()
        if kind in {'right','left'}:co=sleeve_offset(co,1 if kind=='right' else -1)
        elif kind=='torso':
            cy=-.037;v=Vector((co.x,co.y-cy,0));r=v.length
            if r>.01:co+=v.normalized()*.018
            if co.y>cy and co.z<1.45:
                desired=.12-.055*min(1,(co.x/.22)**2)
                co.y=max(co.y,desired)
        else:
            side=1 if co.x>0 else -1
            if co.z<.94:
                a=Vector((side*.108,-.05,.932));b=Vector((side*.153,-.016,.510));c=Vector((side*.188,-.036,.078))
                seg=(a,b) if co.z>.51 else (b,c);p,q=seg;t=max(0,min(1,(co-p).dot(q-p)/(q-p).length_squared));axis=p+(q-p)*t;delta=co-axis
                if delta.length>.001:co+=delta.normalized()*.008
            else:co.y+=.008 if co.y>-.04 else -.008
        verts.append(tuple(co))
    ob=make_part(name,verts,[[mapping[i] for i in f] for f in selected],[source_weights[i] for i in ids],ids,.005 if kind!='legs' else .002)
    ob['construction']='MPFB helper-tights extraction with exact source-index deform weights; original fullness on derived garment only'
# Four separate hanging coat panels keep the knees clear and allow a rear center split.
for side in [-1,1]:
    for front in [True,False]:
        verts=[];faces=[];weights=[]
        for j in range(7):
            t=j/6;z=1.095-.43*t;rx=.18+.06*t;ry=.14+.04*t
            for i in range(9):
                u=i/8;theta=math.radians(5+83*u)*side
                x=rx*math.sin(theta);y=-.045+(1 if front else -1)*ry*math.cos(theta)
                y+=(1 if front else -1)*.006*math.sin(u*math.pi*4)*t
                verts.append((x,y,z));weights.append({'root':1.0})
                if j<6 and i<8:
                    k=j*9+i;faces.append((k,k+1,k+10,k+9) if front== (side==1) else (k+9,k+10,k+1,k))
        name='BW1_CoatPanel_'+('Front' if front else 'Back')+('_R' if side==1 else '_L')
        ob=make_part(name,verts,faces,weights,thickness=.006);ob['deformation_note']='Waist-attached study panels; hip/kneel clearance is a pose-review requirement, not cloth simulation.'
# Navy front point and two rear split halves; simple material IDs are assigned in a later diagnostic view.
for section in ['Front','Rear_R','Rear_L']:
    verts=[];faces=[];weights=[]
    for j in range(8):
        t=j/7
        for i in range(9):
            u=i/8
            if section=='Front':x=(u*2-1)*(.095+.018*t)
            elif section=='Rear_R':x=.009+u*(.11+.022*t)
            else:x=-.009-u*(.11+.022*t)
            z=1.105-.43*t
            if j==7:z-=.075*(1-abs(x)/.14)
            front=section=='Front';y=-.045+(1 if front else -1)*(.15+.043*t)-(.015*(x/.14)**2)*(1 if front else -1)
            verts.append((x,y,z));weights.append({'root':1})
            if j<7 and i<8:
                k=j*9+i;faces.append((k,k+1,k+10,k+9))
    ob=make_part('BW1_Tabard_'+section,verts,faces,weights,thickness=.004);ob['rear_split_m']=.018 if section!='Front' else 0
# Collar is an open padded ring, with an explicit neck clearance.
verts=[];faces=[]
for j,z in enumerate([1.455,1.47,1.54,1.55]):
    for i in range(32):
        a=2*math.pi*i/32;verts.append((.089*math.sin(a),-.039+.082*math.cos(a),z-.012*max(0,math.cos(a))))
        if j<3:k=j*32+i;n=j*32+(i+1)%32;faces.append((k,n,n+32,k+32))
ob=make_part('BW1_PaddedCollar',verts,faces,[{'spine01':1} for v in verts],thickness=.012)
print(json.dumps({'made':[o.name for o in bpy.data.collections['BW1_CLOTH'].objects],'source_raw_vertices':len(body.data.vertices),'source_shape_keys':len(body.data.shape_keys.key_blocks)},indent=2))
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
s.camera=bpy.data.objects['BW1_Camera_three_quarter'];s.render.filepath='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW1/r001/captures/cloth_blockout_r000.png';bpy.ops.render.render(write_still=True)


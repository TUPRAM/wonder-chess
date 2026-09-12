import bpy,math,bmesh,json
from mathutils import Vector,Matrix
s=bpy.data.scenes['BW1_BODY_COSTUME'];rig=bpy.data.objects['BW1_Temporary_Pose_Rig']
assert 'BW1_Breastplate' not in bpy.data.objects
def shell(name,verts,faces,bone,thickness=.004,bevel=.002):
    me=bpy.data.meshes.new(name+'_Cage');me.from_pydata(verts,[],faces);me.update()
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
    ob=bpy.data.objects.new(name,me);bpy.data.collections['BW1_ARMOR'].objects.link(ob);me.materials.append(bpy.data.materials['BW1_Uniform_Clay'])
    for p in me.polygons:p.use_smooth=False
    if thickness:m=ob.modifiers.new('Plate thickness','SOLIDIFY');m.thickness=thickness;m.offset=0;m.use_even_offset=True
    if bevel:m=ob.modifiers.new('Controlled edge bevel','BEVEL');m.width=bevel;m.segments=2
    ob.parent=rig;ob.parent_type='BONE';ob.parent_bone=bone;ob.matrix_world=Matrix.Identity(4)
    ob['wc_part_id']=name;ob['construction']='Original editable panel cage, sized around padded layer, rigid temporary attachment';ob['attachment_bone']=bone;ob['approval']='CANDIDATE'
    return ob
# Compact the padded waist while retaining chest fullness.
ob=bpy.data.objects['BW1_CoatUpper_Continuous']
for v in ob.data.vertices:
    if v.co.y>.06 and abs(v.co.x)<.20 and v.co.z<1.30:
        v.co.y-=.045*max(0,min(1,(1.30-v.co.z)/.20))
ob.data.update()
for ob in bpy.data.collections['BW1_CLOTH'].objects:
    if ob.name.startswith('BW1_CoatPanel'):
        side=1 if ob.name.endswith('_R') else -1;front='Front' in ob.name
        for v in ob.data.vertices:
            t=max(0,min(1,(1.095-v.co.z)/.43));a=math.radians(5+83*(v.index%9)/8)*side
            v.co.x=(.174+.096*t**.45)*math.sin(a);v.co.y=-.045+(1 if front else -1)*(.14+.069*t**.5)*math.cos(a)
    elif ob.name.startswith('BW1_Tabard'):
        front='Front' in ob.name
        for v in ob.data.vertices:
            t=max(0,min(1,(1.105-v.co.z)/.43));v.co.y=-.045+(1 if front else -1)*(.155+.068*t**.5)-.012*(v.co.x/.14)**2*(1 if front else -1)
# Breast and back have their own planar curvature, not copied breast contours.
rows=[(1.115,.166,.163),(1.14,.172,.172),(1.25,.195,.207),(1.35,.199,.218),(1.425,.19,.185),(1.46,.139,.164)]
for front in [True,False]:
    verts=[];faces=[];n=13
    for j,(z,rx,depth) in enumerate(rows):
        for i in range(n):
            a=math.radians(-79+158*i/(n-1));x=rx*math.sin(a);y=-.047+(1 if front else -1)*depth*math.cos(a)
            if front:y+=.010*(1-abs(math.sin(a)))
            zz=z
            if j==0:zz-=.026*(1-abs(math.sin(a)))
            if j==len(rows)-1:zz-=.020*math.cos(a)**2
            verts.append((x,y,zz))
            if j<len(rows)-1 and i<n-1:k=j*n+i;faces.append((k,k+1,k+1+n,k+n))
    shell('BW1_Breastplate' if front else 'BW1_Backplate',verts,faces,'spine03')
# Elliptical waist belt retains a readable opening and finite section.
verts=[];faces=[]
for j,z in enumerate([1.062,1.072,1.119,1.126]):
    for i in range(48):
        a=2*math.pi*i/48;verts.append((.181*math.sin(a),-.039+.164*math.cos(a),z))
        if j<3:k=j*48+i;n=j*48+(i+1)%48;faces.append((k,n,n+48,k+48))
belt=shell('BW1_WaistBelt',verts,faces,'root',.012,.002)
# Shoulder caps and overlapping lames use an arm-aligned shell section.
for side in [1,-1]:
    suffix='R' if side==1 else 'L_Blockout';bone='upperarm01.'+('R' if side==1 else 'L')
    a=Vector((side*.18185,-.04636,1.44498));b=Vector((side*.36106,-.04210,1.24891));axis=(b-a).normalized();front=Vector((0,1,0));front=(front-axis*front.dot(axis)).normalized();outer=axis.cross(front)*side
    layouts=[('Cap',[(-.065,.035),(-.045,.079),(.01,.106),(.074,.105),(.092,.100)]),('Lame1',[(.069,.109),(.095,.109),(.145,.091)]),('Lame2',[(.125,.099),(.152,.094),(.196,.077)])]
    for part,rs in layouts:
        verts=[];faces=[];n=15
        for j,(u,r) in enumerate(rs):
            for i in range(n):
                t=math.radians(-108+216*i/(n-1));rad=outer*math.cos(t)+front*math.sin(t);v=a+axis*u+rad*r
                verts.append(tuple(v))
                if j<len(rs)-1 and i<n-1:k=j*n+i;faces.append((k,k+1,k+n+1,k+n))
        ob=shell('BW1_Pauldron_'+suffix+'_'+part,verts,faces,bone,.004,.002)
        ob['overlap_m']=.022;ob['attachment_policy']='Rigid arm-carried study mount; high-elevation collision must be checked.'
    # Bracer is open behind the forearm and does not cross the elbow.
    wrist=Vector((side*.48638,.11233,1.11225));axis=(wrist-b).normalized();f=Vector((0,1,0));f=(f-axis*f.dot(axis)).normalized();across=axis.cross(f)
    verts=[];faces=[];n=17
    for j,(u,r) in enumerate([(.075,.055),(.087,.060),(.20,.048),(.233,.043)]):
        for i in range(n):
            t=math.radians(-135+270*i/(n-1));v=b+axis*u+(f*math.cos(t)+across*math.sin(t))*r;verts.append(tuple(v))
            if j<3 and i<n-1:k=j*n+i;faces.append((k,k+1,k+n+1,k+n))
    shell('BW1_Bracer_'+suffix,verts,faces,'lowerarm01.'+('R' if side==1 else 'L'),.004,.002)
    # Shin plate independent of ankle and kneecap.
    knee=Vector((side*.15343,-.01560,.50984));ankle=Vector((side*.18817,-.03622,.07806));verts=[];faces=[];n=13
    for j,(z,rx,ry) in enumerate([(.195,.046,.062),(.215,.055,.072),(.36,.065,.079),(.444,.074,.083),(.468,.062,.069)]):
        center=ankle+(knee-ankle)*((z-ankle.z)/(knee.z-ankle.z))
        for i in range(n):
            t=math.radians(-106+212*i/(n-1));v=center+Vector((rx*math.sin(t),ry*math.cos(t),0));v.z=z
            if j==4:v.z-=.018*abs(math.sin(t))
            verts.append(tuple(v))
            if j<4 and i<n-1:k=j*n+i;faces.append((k,k+1,k+n+1,k+n))
    shell('BW1_Greave_'+suffix,verts,faces,'lowerleg01.'+('R' if side==1 else 'L'),.004,.002)
    verts=[tuple(knee+Vector((0,.099,.012)))]
    outline=[(-.062,.033),(-.043,.068),(.035,.073),(.067,.034),(.049,-.047),(0,-.068),(-.05,-.045)]
    for x,z in outline:verts.append(tuple(knee+Vector((x,.066,z))))
    faces=[(0,1+i,1+(i+1)%len(outline)) for i in range(len(outline))]
    shell('BW1_KneePlate_'+suffix,verts,faces,'lowerleg01.'+('R' if side==1 else 'L'),.004,.002)
print(json.dumps({'armor_objects':len(bpy.data.collections['BW1_ARMOR'].objects),'head_status':'ART_REVISE_preserved'},indent=2))
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
s.camera=bpy.data.objects['BW1_Camera_three_quarter'];s.render.filepath='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW1/r001/captures/armor_blockout_r000.png';bpy.ops.render.render(write_still=True)


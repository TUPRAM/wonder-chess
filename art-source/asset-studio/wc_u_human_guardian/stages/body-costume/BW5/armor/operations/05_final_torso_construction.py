import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'ada_bw5_armor_correction1.blend'),use_scripts=False)
s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s;s.frame_set(1)
coat=bpy.data.objects['BW4_CONTEXT_BW1_CoatUpper_Continuous'];ev=coat.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();bv=BVHTree.FromPolygons([ev.matrix_world@v.co for v in me.vertices],[tuple(f.vertices) for f in me.polygons]);ev.to_mesh_clear()
front=bpy.data.objects['BW4_Breastplate_ControlSurface'];old=[v.co.copy() for v in front.data.vertices];N=19
F=[.142,.143,.147,.163,.167,.165,.153,.145,.138,.138]
# Deliberate broad front planes continue beyond the last torso hit; a missing
# lateral ray must not make the control surface dive into the padded chest.
for v in front.data.vertices:
    j,i=divmod(v.index,N);a=abs(v.co.x)/max(abs(front.data.vertices[j*N].co.x),1e-6)
    y=F[j]-.006*a+.003*(1-min(1,a/.16))
    nearby=[]
    for dx in [-.014,0,.014]:
        for dz in [-.013,0,.013]:
            h=bv.ray_cast(Vector((v.co.x+dx,1,v.co.z+dz)),Vector((0,-1,0)),2)
            if h[0] is not None:nearby.append(h[0].y)
    if nearby:y=max(y,max(nearby)+.016)
    v.co.y=y
front.data.update();front['BW5_correction2']='Continuous broad anterior planes through padded-chest lateral turn; missing ray no longer causes depth discontinuity. Local control support includes inter-row coat sections, not global smoothing.'
for name,idx in [('Neck',list(range(9*N,10*N))),('Waist',list(range(N))),('Side_L',[j*N for j in range(10)]),('Side_R',[j*N+N-1 for j in range(10)])]:
    ob=bpy.data.objects['BW4_Front_'+name+'_Return']
    for k,i in enumerate(idx):
        d=front.data.vertices[i].co-old[i]
        ob.data.vertices[2*k].co+=d;ob.data.vertices[2*k+1].co+=d
    ob.data.update()
back=bpy.data.objects['BW4_Backplate_ControlSurface']
for side in [-1,1]:
    ob=bpy.data.objects['BW4_Thorax_SideReturn_'+str(side)]
    for j in range(7):
        p=front.data.vertices[j*N+(N-1 if side==1 else 0)].co.copy();q=back.data.vertices[j*11+(10 if side==1 else 0)].co.copy()
        for k,t in enumerate([0,.08,.46,.88,1]):
            a=p.lerp(q,t);a.x+=side*.010*math.sin(math.pi*t);ob.data.vertices[j*5+k].co=a
    ob.data.update()
    # Move only the leading strap endpoint to its actual revised plate interface.
    bridge=bpy.data.objects['BW4_ShoulderBridge_'+str(side)];pt=front.data.vertices[9*N+(N-2 if side==1 else 1)].co
    for vi,dx in [(0,-.012),(1,.012)]:bridge.data.vertices[vi].co=pt+Vector((dx,.002,-.003))
    bridge.data.update()
# Final collar study seats its lower loop on the actual existing neck opening.
# It intentionally does not pretend to solve the tall reference collar by spreading onto sleeves.
indices=[48,49,50,51,444,176,544,539,540,538,542,543,1119,1121,1120,1115,1117,1116,1122,733,1013,601,600,599,598,1014,1109,1108,1107,1112,1113,1111,537,536,532,533,534,445]
pts=[coat.matrix_world@coat.data.vertices[i].co for i in indices];n=len(pts);center=Vector((0,-.063,1.535))
angles=[math.atan2(p.y-center.y,p.x) for p in pts]
for i in range(1,n):
    while angles[i]-angles[i-1]>math.pi:angles[i]-=2*math.pi
    while angles[i]-angles[i-1]<-math.pi:angles[i]+=2*math.pi
direction=1 if angles[-1]>angles[0] else -1
lengths=[0.]
for i in range(1,n):lengths.append(lengths[-1]+(pts[i]-pts[i-1]).length)
total=lengths[-1]+(pts[0]-pts[-1]).length
verts=[];faces=[]
for j,t in enumerate([0,.09,.84,.96,1]):
    for i,p in enumerate(pts):
        a=angles[0]+direction*2*math.pi*lengths[i]/total
        top=Vector((.127*math.cos(a),-.051+.110*math.sin(a),1.555-.004*max(0,math.sin(a))))
        start=p+Vector((0,0,.0015));q=start.lerp(top,t);verts.append(q)
    if j:
        for i in range(n):
            k=(i+1)%n;faces.append(((j-1)*n+i,(j-1)*n+k,j*n+k,j*n+i))
collar=bpy.data.objects['BW5_Tailored_Collar'];oldme=collar.data;me=bpy.data.meshes.new('BW5_SeatedNeck_Collar_Cage');me.from_pydata(verts,[],faces);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
for m in oldme.materials:me.materials.append(m)
collar.data=me;collar.vertex_groups.clear();vg=collar.vertex_groups.new(name='spine01');vg.add(list(range(len(verts))),1,'REPLACE')
for p in me.polygons:p.use_smooth=True
for m in collar.modifiers:
    if m.type=='SOLIDIFY':m.thickness=.003;m.offset=1;m.use_even_offset=False
collar['construction']='Provisional collar seated to actual 38-vertex neck boundary; rounded flared top. Full reference-height collar remains unresolved and requires local upper-coat neckline reconstruction.'
waist=bpy.data.objects['BW5_Navy_Waist_Enclosure']
for v in waist.data.vertices:
    p=v.co;d=Vector((p.x,p.y+.044,0))
    if d.length:v.co+=d.normalized()*.005
waist.data.update();waist['BW5_correction2']='5mm additional local garment allowance for evaluated interpolation, continuous connected torso section; body/coat unchanged. Belt/coat crossings remain subject to audit.'
s['BW5_iteration']='Initial plus 2 substantive torso corrections complete. Do not continue same fitting method on unresolved defects.'
s['status']='ART_REVISE';s['BW5_scope']='Shortened fitted front/back and waist candidate; provisional seated collar; original contextual BW4 shoulder retained. Separate BW5 shoulder experiment remains rejected.'
s.camera=bpy.data.objects['BW4_Camera_three_quarter'];s.render.threads=4;s.cycles.samples=16
bpy.ops.wm.save_as_mainfile(filepath=str(R/'ada_bw5_armor_correction2.blend'))
for view in ['front','profile','back','three_quarter','rear_three_quarter']:
    s.camera=bpy.data.objects['BW4_Camera_'+view];s.render.filepath=str(R/'captures'/('correction2_'+view+'.png'));bpy.ops.render.render(write_still=True)
print('BW5_FINAL_TORSO_CONSTRUCTION_RENDERED',flush=True)

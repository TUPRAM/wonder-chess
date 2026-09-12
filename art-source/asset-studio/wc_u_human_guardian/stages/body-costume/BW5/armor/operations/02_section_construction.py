import bpy,bmesh,json,math,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1]
src=R.parents[1]/'BW4/r001/armor/ada_armor_checkpoint_FINAL_ART_REVISE.blend'
bpy.ops.wm.open_mainfile(filepath=str(src),use_scripts=False)
s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s;s.frame_set(1)
rig=bpy.data.objects['BW4_Armor_Independent_Rig'];rig.data=rig.data.copy();rig.animation_data.action=rig.animation_data.action.copy()
rig.animation_data.action.name='BW5_Preserved97_Authoring_Diagnostic_NOT_GAME_CLIPS'
parts=[bpy.data.objects[n] for n in json.loads(s['armor_parts'])];col=bpy.data.collections['BW4_ARMOR_CANDIDATE']
for ob in parts:ob.data=ob.data.copy()
coat=bpy.data.objects['BW4_CONTEXT_BW1_CoatUpper_Continuous']
ev=coat.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();bv=BVHTree.FromPolygons([ev.matrix_world@v.co for v in me.vertices],[tuple(f.vertices) for f in me.polygons]);ev.to_mesh_clear()
def bound(x,z,sign):
    q=bv.ray_cast(Vector((x,sign*1.,z)),Vector((0,-sign,0)),2)
    return q[0].y if q[0] is not None else None
U=[-1,-.97,-.8,-.51,-.16,0,.16,.51,.8,.97,1]
Z=[1.174,1.181,1.207,1.245,1.298,1.352,1.392,1.428,1.466,1.472]
W=[.175,.176,.175,.184,.199,.201,.177,.151,.136,.136]
F=[.136,.137,.140,.157,.164,.157,.143,.129,.117,.117]
B=[-.155,-.157,-.164,-.164,-.160,-.154,-.145,-.140,-.139,-.139]
front=bpy.data.objects['BW4_Breastplate_ControlSurface'];back=bpy.data.objects['BW4_Backplate_ControlSurface'];fit=[]
for ob,sgn in [(front,1),(back,-1)]:
    previous=[v.co.copy() for v in ob.data.vertices]
    for v in ob.data.vertices:
        j,i=divmod(v.index,11);u=U[i];a=abs(u);z=Z[j];w=W[j]
        if sgn==1:
            if j<2:z+=.010*a
            if j>=7:z-=.051*(1-a)**2*((j-6)/3)
            y=F[j]-.095*a**1.75+.003*(1-min(1,a/.16))
        else:
            if j<2:z+=.015*(1-a)-.005*a
            if j>=6:w=[.151,.121,.113,.113][j-6]
            if j>=7:z-=.029*(1-a)**2*((j-6)/3)
            y=B[j]+.066*a**1.8
        x=w*u; coat_y=bound(x,z,sgn)
        # A fitting bound affects only the independent shell; body and padding unchanged.
        if coat_y is not None:
            y=max(y,coat_y+.013) if sgn==1 else min(y,coat_y-.013)
        v.co=(x,y,z);fit.append({'object':ob.name,'vertex':v.index,'section':j,'semantic_column':u,'coat_y_m':coat_y,'surface_m':list(v.co)})
    ob.data.update();ob['BW5_construction']='Direct semantic section editing; shortened center occupancy; independent chest depth and waist, side setbacks; front dips and back rises centrally.'
    for label,inds in [('Neck',list(range(99,110))),('Waist',list(range(11))),('Side_L',[j*11 for j in range(10)]),('Side_R',[j*11+10 for j in range(10)])]:
        rim=bpy.data.objects[('BW4_Front_' if sgn==1 else 'BW4_Back_')+label+'_Return']
        for k,i in enumerate(inds):
            delta=ob.data.vertices[i].co-previous[i]
            for vi in [2*k,2*k+1]:rim.data.vertices[vi].co+=delta
        rim.data.update()
    for name,inds in {'CenterHem':list(range(11)),'Waist':list(range(33)),'Chest':list(range(33,66)),'Armhole':list(range(66,99)),'Neckline':list(range(99,110))}.items():
        vg=ob.vertex_groups.new(name='BW5_'+name);vg.add(inds,1,'REPLACE')
# Reshape the entire side return against the new front and back boundaries.
for side in [-1,1]:
    ob=bpy.data.objects['BW4_Thorax_SideReturn_'+str(side)]
    for j in range(7):
        p=front.data.vertices[j*11+(10 if side==1 else 0)].co.copy();q=back.data.vertices[j*11+(10 if side==1 else 0)].co.copy()
        for k,t in enumerate([0,.08,.46,.88,1]):
            a=p.lerp(q,t);a.x+=side*.006*math.sin(math.pi*t);ob.data.vertices[j*5+k].co=a
    ob.data.update()
    # Existing closure strips are refitted at two useful torso stations.
    for zold,j in [(1.215,3),(1.335,5)]:
        ob=bpy.data.objects['BW4_SideClosure_'+str(side)+'_'+str(zold)]
        p=front.data.vertices[j*11+(10 if side==1 else 0)].co.copy();q=back.data.vertices[j*11+(10 if side==1 else 0)].co.copy()
        for k in range(11):
            p0=p.lerp(q,k/10);p0.x+=side*.008
            ob.data.vertices[k*2].co=p0+Vector((0,0,-.013));ob.data.vertices[k*2+1].co=p0+Vector((0,0,.013))
        ob.data.update()
    ob=bpy.data.objects['BW4_ShoulderBridge_'+str(side)]
    p=front.data.vertices[99+(9 if side==1 else 1)].co.copy();q=back.data.vertices[99+(9 if side==1 else 1)].co.copy()
    pts=[p+Vector((0,.002,-.003)),Vector((side*.14,.036,1.505)),Vector((side*.14,-.045,1.529)),Vector((side*.127,-.112,1.501)),q+Vector((0,-.002,-.003))]
    for k,p in enumerate(pts):
        ob.data.vertices[k*2].co=p+Vector((-.012,0,0));ob.data.vertices[k*2+1].co=p+Vector((.012,0,0))
    ob.data.update()
def garment(name,verts,faces,thickness):
    me=bpy.data.meshes.new(name+'_EditableCage');me.from_pydata(verts,[],faces);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
    ob=bpy.data.objects.new(name,me);col.objects.link(ob);me.materials.append(bpy.data.materials['BW4_Underlayer_Clay'])
    for p in me.polygons:p.use_smooth=True
    g=ob.vertex_groups.new(name='spine01');g.add(list(range(len(verts))),1,'REPLACE')
    m=ob.modifiers.new('Tailored broad surface','SUBSURF');m.levels=1;m.render_levels=1
    m=ob.modifiers.new('Cloth wall inward','SOLIDIFY');m.thickness=thickness;m.offset=-1;m.use_even_offset=False
    m=ob.modifiers.new('Local authoring spine attachment','ARMATURE');m.object=rig
    ob['owner_bone']='spine01';ob['status']='AUTHORING_ONLY_REVIEW_PENDING';parts.append(ob);return ob
verts=[];faces=[];n=48
for j,t in enumerate([0,.04,.28,.72,.96,1]):
    for i in range(n):
        a=2*math.pi*i/n;x=math.cos(a);y=math.sin(a);frontness=max(0,y)
        zbottom=1.471-.056*frontness**2
        z=zbottom*(1-t)+1.551*t
        rx=.134*(1-t)+.128*t;ry=.133*(1-t)+.113*t
        verts.append((rx*x,-.042+ry*y,z))
    if j:
        for i in range(n):
            k=(i+1)%n;faces.append(((j-1)*n+i,(j-1)*n+k,j*n+k,j*n+i))
collar=garment('BW5_Tailored_Collar',verts,faces,.006)
collar['construction']='Open flared padded collar, broad top opening, front base descends behind compact breastplate. Simple clay; ivory/navy assignment remains material planning.'
oldcollar=bpy.data.objects['BW4_CONTEXT_BW1_PaddedCollar'];oldcollar.hide_render=True;oldcollar.hide_set(True)
verts=[];faces=[]
for j,z in enumerate([1.095,1.101,1.126,1.165,1.203,1.214]):
    for i in range(n):
        a=2*math.pi*i/n;direction=Vector((math.cos(a),math.sin(a),0));center=Vector((0,-.044,z))
        hit=bv.ray_cast(center+direction*.5,-direction,1.)
        if hit[0] is None:raise RuntimeError('No coat section for navy enclosure')
        p=hit[0]+direction*.005;verts.append(p)
    if j:
        for i in range(n):
            k=(i+1)%n;faces.append(((j-1)*n+i,(j-1)*n+k,j*n+k,j*n+i))
waist=garment('BW5_Navy_Waist_Enclosure',verts,faces,.002)
waist['construction']='Continuous fitted garment envelope sampled around final evaluated coat. Full circumference with rear split unchanged below; overlaps behind torso plates and belt. Rigid local torso test only, not game cloth.'
s['armor_parts']=json.dumps([o.name for o in parts]);s['BW5_active_context']=json.dumps([x for x in json.loads(s['context_parts']) if x!=oldcollar.name])
s['status']='ART_REVISE_PENDING_LOCAL_EVIDENCE';s['BW5_iteration']='Initial section-based torso construction. Shoulder unchanged pending separate local proof.'
s['BW5_protection']='Body, evaluated padded coat, leggings, original shape keys, head/hair, sole and canonical game untouched. Historical cameras retained.'
s.camera=bpy.data.objects['BW4_Camera_three_quarter'];s.render.threads_mode='FIXED';s.render.threads=4;s.cycles.samples=16
(R/'records/initial_section_controls.json').write_text(json.dumps(fit,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(R/'ada_bw5_armor_initial.blend'))
for view in ['front','profile','back','three_quarter','rear_three_quarter']:
    s.camera=bpy.data.objects['BW4_Camera_'+view];s.render.filepath=str(R/'captures'/('initial_'+view+'.png'));bpy.ops.render.render(write_still=True)
print('BW5_INITIAL_TORSO_COMPLETE',flush=True)

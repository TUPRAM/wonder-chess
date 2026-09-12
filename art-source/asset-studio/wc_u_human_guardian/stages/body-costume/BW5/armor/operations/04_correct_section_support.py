import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'ada_bw5_armor_initial.blend'),use_scripts=False)
s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s;s.frame_set(1)
coat=bpy.data.objects['BW4_CONTEXT_BW1_CoatUpper_Continuous'];ev=coat.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();bv=BVHTree.FromPolygons([ev.matrix_world@v.co for v in me.vertices],[tuple(f.vertices) for f in me.polygons]);ev.to_mesh_clear()
def torso_exit(z,a):
    d=Vector((math.cos(a),math.sin(a),0));c=Vector((0,-.044,z));hits=[];origin=c.copy()
    for k in range(12):
        h=bv.ray_cast(origin,d,.45)
        if h[0] is None:break
        dist=(h[0]-c).length
        if hits and dist-hits[-1][0]>.018:break
        hits.append((dist,h[0].copy()));origin=h[0]+d*.0001
    return (hits[-1][1],d) if hits else (None,d)
def rebuild(ob,v,f):
    old=ob.data;me=bpy.data.meshes.new(ob.name+'_BW5_ControlCage');me.from_pydata(v,[],f);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
    for mat in old.materials:me.materials.append(mat)
    ob.data=me;ob.vertex_groups.clear();vg=ob.vertex_groups.new(name=ob.get('owner_bone','spine01'));vg.add(list(range(len(v))),1,'REPLACE')
    for p in me.polygons:p.use_smooth=True
def gridfaces(rows,n):return [(j*n+i,j*n+i+1,(j+1)*n+i+1,(j+1)*n+i) for j in range(rows-1) for i in range(n-1)]
U=[-1,-.985,-.93,-.85,-.75,-.65,-.51,-.35,-.16,0,.16,.35,.51,.65,.75,.85,.93,.985,1]
Z=[1.174,1.181,1.207,1.245,1.298,1.352,1.392,1.428,1.466,1.472]
W=[.175,.176,.175,.184,.199,.201,.177,.151,.136,.136];F=[.136,.137,.140,.157,.164,.157,.143,.129,.117,.117]
v=[]
for j in range(10):
    for u in U:
        a=abs(u);z=Z[j]+(.010*a if j<2 else 0)
        if j>=7:z-=.051*(1-a)**2*((j-6)/3)
        x=W[j]*u;y=F[j]-.095*a**1.75+.003*(1-min(1,a/.16))
        h=bv.ray_cast(Vector((x,1,z)),Vector((0,-1,0)),2)
        if h[0] is not None:y=max(y,h[0].y+.017)
        v.append((x,y,z))
front=bpy.data.objects['BW4_Breastplate_ControlSurface'];rebuild(front,v,gridfaces(10,len(U)))
front['BW5_construction']='Reconstructed lateral control columns at .51/.65/.75/.85/.93 width fractions hold evaluated garment curvature before side return; center depth and plate width preserved. Not increased render subdivision.'
cr=front.data.attributes.new('crease_edge','FLOAT','EDGE')
for e in front.data.edges:
    a,b=e.vertices
    if a%len(U)==b%len(U)==9:cr.data[e.index].value=.55
for name,idx in [('Neck',list(range(9*len(U),10*len(U)))),('Waist',list(range(len(U)))),('Side_L',[j*len(U) for j in range(10)]),('Side_R',[j*len(U)+len(U)-1 for j in range(10)])]:
    ob=bpy.data.objects['BW4_Front_'+name+'_Return'];vv=[]
    for k,i in enumerate(idx):
        p=Vector(v[i])+Vector((0,.0015,0));a=Vector(v[idx[max(0,k-1)]]);b=Vector(v[idx[min(len(idx)-1,k+1)]]);t=(b-a).normalized();ac=t.cross(Vector((0,1,0))).normalized()*.0035;vv.extend([p-ac,p+ac])
    rebuild(ob,vv,[(2*k,2*k+1,2*k+3,2*k+2) for k in range(len(idx)-1)])
for name,ids in {'CenterHem':range(len(U)),'Waist':range(3*len(U)),'Chest':range(3*len(U),6*len(U)),'Armhole':range(6*len(U),9*len(U)),'Neckline':range(9*len(U),10*len(U))}.items():
    g=front.vertex_groups.new(name='BW5_'+name);g.add(list(ids),1,'REPLACE')
# Navy enclosure uses the first connected inner/outer torso-shell crossings.
# Distant sleeve hits are kept out by radial continuity, never by deforming sleeves.
waist=bpy.data.objects['BW5_Navy_Waist_Enclosure'];n=48;records=[]
for j,z in enumerate([1.095,1.101,1.126,1.165,1.203,1.214]):
    for i in range(n):
        p,d=torso_exit(z,2*math.pi*i/n);fallback=False
        if p is None:
            p,d=torso_exit(1.14,2*math.pi*i/n);assert p is not None,(j,i,z)
            p.z=z;fallback=True
        p+=d*.005;waist.data.vertices[j*n+i].co=p;records.append({'row':j,'angular_column':i,'point_m':list(p),'extended_from_waist_section_for_open_coat_boundary':fallback})
waist.data.update();waist['BW5_correction']='Continuous torso component picked from first shell-crossing cluster; remote arm intersections excluded by connected radial interval. Same unmodified coat surface.'
# Collar lower edge spreads onto the shoulder/upper-coat envelope; top stays an open neck surround.
collar=bpy.data.objects['BW5_Tailored_Collar']
for j,t in enumerate([0,.04,.28,.72,.96,1]):
    for i in range(n):
        a=2*math.pi*i/n;x=math.cos(a);y=math.sin(a);zbottom=1.445-.030*max(0,y)**2
        ztop=1.551-.007*max(0,y)+.004*max(0,-y);z=zbottom*(1-t)+ztop*t
        rx=.153*(1-t)+.128*t;ry=.143*(1-t)+.113*t;p=Vector((rx*x,-.042+ry*y,z))
        h,d=torso_exit(z,a)
        if h is not None:
            center=Vector((0,-.044,z));rneed=(h-center).length+.009;rp=(p-center).length
            if rp<rneed:p=center+(p-center).normalized()*rneed
        collar.data.vertices[j*n+i].co=p
collar.data.update();collar['BW5_correction']='Flared lower collar tailored outside connected padded upper torso; open upper neckline descends anteriorly. Body and garment unchanged.'
s['BW5_iteration']='Correction 1: lateral front control reconstruction, connected-torso navy selection, collar lower flare. Shoulder independent.'
s.camera=bpy.data.objects['BW4_Camera_three_quarter'];s.render.threads=4;s.cycles.samples=16
(R/'records/waist_connected_sections.json').write_text(json.dumps(records,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(R/'ada_bw5_armor_correction1.blend'))
for view in ['front','profile','back','three_quarter']:
    s.camera=bpy.data.objects['BW4_Camera_'+view];s.render.filepath=str(R/'captures'/('correction1_'+view+'.png'));bpy.ops.render.render(write_still=True)
print('BW5_CORRECTION1_COMPLETE',flush=True)

import bpy
import math
import json
import bmesh
from mathutils import Vector
from math import sin, cos, pi, sqrt, exp
assert bpy.data.filepath.replace('\\','/').endswith('/live/ada_clay_study_r001.blend')
def collection(name):
    c=bpy.data.collections.get(name)
    if c is None:
        c=bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(c)
    return c
def mesh(name,verts,faces,col='STUDY_ORGANIC',smooth=True):
    assert bpy.data.objects.get(name) is None, 'Object already exists: '+name
    m=bpy.data.meshes.new(name+'_cage'); m.from_pydata(verts,[],faces); m.update()
    bm=bmesh.new(); bm.from_mesh(m); bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces)); bm.to_mesh(m); bm.free()
    o=bpy.data.objects.new(name,m); collection(col).objects.link(o)
    o['wc_part_id']=name; o['as1_method']='Original purpose-built editable mesh; no imported character geometry'
    for p in m.polygons: p.use_smooth=smooth
    o.color=(0.52,0.52,0.52,1)
    return o
def interp(rows,z,k):
    i=0
    while i<len(rows)-2 and z>rows[i+1][0]:i+=1
    t=max(0,min(1,(z-rows[i][0])/(rows[i+1][0]-rows[i][0])))
    a=rows[max(0,i-1)][k]; b=rows[i][k]; c=rows[i+1][k]; d=rows[min(len(rows)-1,i+2)][k]
    dz=rows[i+1][0]-rows[i][0]
    m0=(c-a)/(rows[i+1][0]-rows[max(0,i-1)][0])*dz
    m1=(d-b)/(rows[min(len(rows)-1,i+2)][0]-rows[i][0])*dz
    return (2*t**3-3*t*t+1)*b+(t**3-2*t*t+t)*m0+(-2*t**3+3*t*t)*c+(t**3-t*t)*m1
def loft(name,rows,col='STUDY_ORGANIC',N=64,steps=50):
    vs=[]
    for i in range(steps+1):
        z=rows[0][0]+(rows[-1][0]-rows[0][0])*i/steps
        w,dep,yc=[interp(rows,z,k) for k in (1,2,3)]
        for j in range(N):
            a=2*pi*j/N; vs.append((w*sin(a),yc+dep*cos(a),z))
    fs=[(i*N+j,i*N+(j+1)%N,(i+1)*N+(j+1)%N,(i+1)*N+j) for i in range(steps) for j in range(N)]
    fs.extend([tuple(range(N-1,-1,-1)),tuple(steps*N+j for j in range(N))])
    return mesh(name,vs,fs,col)
def tube(name,points,radii,col='STUDY_ORGANIC',sides=10):
    vs=[]
    for i,p in enumerate(points):
        p=Vector(p); tangent=Vector(points[min(len(points)-1,i+1)])-Vector(points[max(0,i-1)])
        tangent.normalize(); axis=Vector((0,1,0))
        if abs(tangent.dot(axis))>.94:axis=Vector((1,0,0))
        a=tangent.cross(axis).normalized(); b=tangent.cross(a).normalized()
        rr=radii[i] if isinstance(radii,list) else radii
        for j in range(sides):
            q=p+rr*(a*cos(2*pi*j/sides)+b*sin(2*pi*j/sides));vs.append(tuple(q))
    fs=[(i*sides+j,i*sides+(j+1)%sides,(i+1)*sides+(j+1)%sides,(i+1)*sides+j) for i in range(len(points)-1) for j in range(sides)]
    fs.extend([tuple(range(sides-1,-1,-1)),tuple((len(points)-1)*sides+j for j in range(sides))])
    return mesh(name,vs,fs,col)
def shell(o,thickness=.005,bevel=.002):
    mod=o.modifiers.new('Finite shell thickness','SOLIDIFY');mod.thickness=thickness;mod.offset=-1
    if bevel:
        m=o.modifiers.new('Controlled edge transition','BEVEL');m.width=bevel;m.segments=3
def view(pos,target,scale):
    for area in bpy.context.screen.areas:
        if area.type=='VIEW_3D':
            sp=area.spaces.active
            sp.region_3d.view_rotation=(Vector(target)-Vector(pos)).to_track_quat('-Z','Y')
            sp.region_3d.view_location=target;sp.region_3d.view_distance=scale
            sp.region_3d.view_perspective='ORTHO'
            sp.shading.type='SOLID';sp.shading.light='STUDIO';sp.shading.studiolight_rotate_z=.3
            sp.shading.color_type='SINGLE';sp.shading.single_color=(.56,.56,.56)
            sp.shading.show_cavity=True;sp.shading.cavity_type='BOTH'
            sp.overlay.show_floor=False;sp.overlay.show_axis_x=False;sp.overlay.show_axis_y=False
            sp.overlay.show_extras=False
            area.tag_redraw()

assert bpy.context.scene.get('as1_operation_id')=='clay-r001-assembly'
# Keep the original hair assembly editable; create a coherent sculpt surface from it.
sources=[o for o in collection('STUDY_HAIR').objects if o.name.startswith('ADA_Swept_Lock_') or o.name=='ADA_Hair_Foundation']
for o in sources:
    if o.name.startswith('ADA_Swept_Lock_'):
        for start in range(0,len(o.data.vertices),12):
            ring=list(o.data.vertices)[start:start+12]
            center=sum((v.co for v in ring),Vector())/len(ring)
            normal=(center-Vector((0,-.02,1.69))).normalized()
            for v in ring:v.co=center+(v.co-center)*1.35-normal*.003
    if o.name=='ADA_Hair_Foundation':
        for v in o.data.vertices:
            x,y,z=v.co
            a=math.atan2(x,(y+.021))
            v.co.z+=.003*cos(6*a)*max(0,min(1,(1.77-z)/.10))
vs=[];fs=[]
dg=bpy.context.evaluated_depsgraph_get()
for o in sources:
    ev=o.evaluated_get(dg);m=ev.to_mesh();off=len(vs)
    vs.extend(tuple(o.matrix_world@v.co) for v in m.vertices)
    fs.extend(tuple(off+i for i in p.vertices) for p in m.polygons);ev.to_mesh_clear()
    o.hide_set(True);o.hide_render=True
hair=mesh('ADA_Hair_Sculpt_Surface',vs,fs,'STUDY_HAIR')
mod=hair.modifiers.new('Union of original hair masses','REMESH');mod.mode='VOXEL';mod.voxel_size=.0012;mod.use_smooth_shade=True
s=hair.modifiers.new('Local surface relaxation','SMOOTH');s.factor=.45;s.iterations=3
hair['construction_sources']='Preserved hidden original scalp and eight swept clump meshes in STUDY_HAIR'
# Reshape collar as a fitted, padded, tapered garment with a dipped front.
o=bpy.data.objects['ADA_Padded_Collar'];vs=[];N=96;K=12
for side in range(2):
    for k in range(K+1):
        u=k/K
        for j in range(N):
            a=2*pi*j/N
            w=.087*(1-u)+.075*u+.0025*sin(pi*u)
            d=.066*(1-u)+.058*u+.0025*sin(pi*u)
            if side==1:w-=.011;d-=.011
            z=1.482*(1-u)+(1.565-.025*max(0,cos(a))+.004*sin(a))*u
            # Broad padded panel relief, not surface stitch detail.
            pad=.0018*(1-cos(8*a))*sin(pi*u) if side==0 else 0
            vs.append(((w+pad)*sin(a),-.019+(d+pad)*cos(a),z))
fs=[]
for side in range(2):
    off=side*(K+1)*N
    fs.extend((off+k*N+j,off+k*N+(j+1)%N,off+(k+1)*N+(j+1)%N,off+(k+1)*N+j) for k in range(K) for j in range(N))
off=(K+1)*N
for k in (0,K):
    fs.extend((k*N+j,k*N+(j+1)%N,off+k*N+(j+1)%N,off+k*N+j) for j in range(N))
o.data.clear_geometry();o.data.from_pydata(vs,[],fs);o.data.update()
bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
for p in o.data.polygons:p.use_smooth=True
bpy.data.objects['ADA_Collar_Upper_Piping'].hide_set(True);bpy.data.objects['ADA_Collar_Upper_Piping'].hide_render=True
pts=[(.075*sin(2*pi*j/96),-.019+.058*cos(2*pi*j/96),1.565-.025*max(0,cos(2*pi*j/96))+.004*sin(2*pi*j/96)) for j in range(97)]
tube('ADA_Collar_Fitted_Roll',pts,.0028,'STUDY_COSTUME')
# Tighten shoulder overlaps and lift front/back borders for a shorter, controlled assembly.
for o in collection('STUDY_ARMOR').objects:
    if o.name.startswith('ADA_Shoulder_R'):
        for v in o.data.vertices:
            v.co.z+=.018+.018*(min(1,abs((v.co.y+.023)/.119))**1.7)
# Preserve chest planes but remove polygon-strip shading from curved lateral cage.
for name in ['ADA_Breastplate','ADA_Backplate']:
    o=bpy.data.objects[name]
    for p in o.data.polygons:p.use_smooth=True
view((.8,2,1.68),(0,0,1.50),.91)
bpy.context.scene['as1_operation_id']='clay-r001-construction-refine'
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
bpy.context.scene.camera=bpy.data.objects['CAM_three_quarter']
bpy.context.scene.render.filepath='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/clay-study/r001/captures/assembly_after.png'
bpy.ops.render.render(write_still=True)
print('Coherent hair sculpt surface created; original source clumps retained hidden. Collar taper/front dip and shoulder overlap revised.')


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

assert bpy.context.scene.get('as1_operation_id')=='clay-r001-lid-fit'
vs=[];N=96;R=36
for i in range(R+1):
    u=i/R
    for j in range(N):
        a=2*pi*j/N;f=max(0,cos(a));back=max(0,-cos(a))
        end=1.76-.66*f+.17*back
        t=.025+(end-.025)*u
        x=.097*sin(t)*sin(a);y=-.021+(.088 if cos(a)>0 else .109)*sin(t)*cos(a);z=1.690+.123*cos(t)
        vs.append((x,y,z))
fs=[(i*N+j,i*N+(j+1)%N,(i+1)*N+(j+1)%N,(i+1)*N+j) for i in range(R) for j in range(N)]
cap=mesh('ADA_Hair_Foundation',vs,fs,'STUDY_HAIR');shell(cap,.008,0)
def smooth_path(points,samples=70):
    out=[]
    for i in range(samples):
        q=(len(points)-1)*i/(samples-1);k=min(len(points)-2,int(q));t=q-k
        a=Vector(points[max(0,k-1)]);b=Vector(points[k]);c=Vector(points[k+1]);d=Vector(points[min(len(points)-1,k+2)])
        p=.5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t);out.append(p)
    return out
def lock(name,points,width,depth):
    ps=smooth_path(points);vs=[];S=12
    for i,p in enumerate(ps):
        u=i/(len(ps)-1);t=(ps[min(len(ps)-1,i+1)]-ps[max(0,i-1)]).normalized()
        normal=(p-Vector((0,-.02,1.69))).normalized()
        side=t.cross(normal).normalized();normal=side.cross(t).normalized()
        r=(sin(pi*u)**.4)*.94+.035
        for j in range(S):
            a=2*pi*j/S;v=p+side*width*r*cos(a)+normal*depth*r*sin(a);vs.append(tuple(v))
    fs=[(i*S+j,i*S+(j+1)%S,(i+1)*S+(j+1)%S,(i+1)*S+j) for i in range(len(ps)-1) for j in range(S)]
    fs.extend([tuple(range(S-1,-1,-1)),tuple((len(ps)-1)*S+j for j in range(S))])
    return mesh(name,vs,fs,'STUDY_HAIR')
paths=[
[(-.079,.021,1.689),(-.081,.061,1.733),(-.054,.086,1.765),(-.013,.067,1.800),(.003,.002,1.817),(-.026,-.082,1.753)],
[(-.092,-.006,1.677),(-.095,.040,1.713),(-.077,.068,1.748),(-.036,.058,1.790),(-.027,-.029,1.802),(-.047,-.092,1.728)],
[(-.094,-.035,1.697),(-.091,-.001,1.744),(-.070,.016,1.790),(-.052,-.053,1.792),(-.064,-.105,1.706),(-.023,-.130,1.65)],
[(.012,.062,1.773),(.025,.074,1.788),(.059,.048,1.781),(.087,.008,1.745),(.084,-.060,1.697),(.025,-.126,1.65)],
[(.034,.071,1.754),(.061,.074,1.752),(.091,.040,1.720),(.098,-.016,1.691),(.076,-.085,1.667),(.005,-.137,1.641)],
[(.011,-.002,1.820),(.043,-.037,1.811),(.071,-.073,1.767),(.069,-.107,1.706),(.017,-.132,1.652)],
[(-.03,-.054,1.806),(-.03,-.100,1.77),(-.023,-.128,1.715),(.018,-.137,1.661),(.005,-.140,1.634)],
[(.035,-.081,1.782),(.037,-.119,1.735),(.001,-.137,1.695),(-.024,-.137,1.654)]]
for i,points in enumerate(paths):lock('ADA_Swept_Lock_%02d'%i,points,.018 if i<5 else .021,.009)
lock('ADA_Temple_Loose_Lock',[(-.078,.053,1.731),(-.090,.050,1.700),(-.077,.047,1.678),(-.086,.043,1.652),(-.077,.041,1.641)],.006,.004)
for k in range(3):
    pts=[];rs=[]
    for i in range(91):
        u=i/90;phase=u*5*pi+2*pi*k/3;rr=.021*(1-.55*u)
        pts.append((rr*sin(phase),-.137+.010*cos(2*phase)-.017*u,1.656-.213*u))
        rs.append(.013*(1-.50*u))
    tube('ADA_Braid_Strand_'+str(k),pts,rs,'STUDY_HAIR',12)
lock('ADA_Braid_Tail',[(0,-.151,1.45),(.008,-.159,1.425),(.011,-.152,1.397),(.023,-.151,1.39)],.014,.010)
view((.8,2,1.69),(0,0,1.60),.68)
bpy.context.scene['as1_operation_id']='clay-r001-hair'
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print('Swept asymmetric mesh clumps and three interwoven upper-back braid strands authored.')


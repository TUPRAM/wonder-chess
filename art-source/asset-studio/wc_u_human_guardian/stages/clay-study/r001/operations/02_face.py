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

head_rows=[(1.563,.009,.025,.035),(1.575,.035,.065,.045),(1.591,.054,.068,.059),(1.615,.071,.070,.073),(1.646,.083,.073,.086),(1.672,.084,.074,.091),(1.693,.080,.070,.096),(1.720,.080,.075,.095),(1.747,.075,.070,.089),(1.770,.062,.056,.075),(1.788,.036,.035,.045),(1.798,.002,.002,.002)]
def gauss(x,z,cx,cz,wx,wz,amp):return amp*exp(-((x-cx)/wx)**2-((z-cz)/wz)**2)
def face_y(x,z):
    w=interp(head_rows,z,1);df=interp(head_rows,z,2)
    v=-.012+df*sqrt(max(0,1-(x/max(w,.001))**2))
    v+=gauss(x,z,0,1.677,.013,.034,.026)
    v+=gauss(x,z,0,1.652,.015,.010,.033)
    v+=gauss(x,z,.014,1.644,.009,.007,.013)+gauss(x,z,-.014,1.644,.009,.007,.013)
    v+=gauss(x,z,0,1.620,.032,.022,.009)
    cup=.002*exp(-((abs(x)-.007)/.005)**2)
    v+=gauss(x,z,0,1.613+cup,.024,.003,.006)+gauss(x,z,0,1.604,.022,.004,.007)
    v-=gauss(x,z,0,1.608+.0015*(x/.024)**2,.024,.0012,.003)
    v+=gauss(x,z,0,1.584,.032,.011,.004)
    for sx in [-1,1]:
        v-=gauss(x,z,sx*.038,1.687,.025,.011,.014)
        v+=gauss(x,z,sx*.047,1.663,.029,.014,.009)
        v+=gauss(x,z,sx*.038,1.707,.030,.008,.005)
    return v

assert bpy.context.scene.get('as1_operation_id')=='clay-r001-primary'
head=bpy.data.objects['ADA_Head_Continuous']
N=160;Z=140
for i in range(Z+1):
    z=1.563+(1.798-1.563)*i/Z;w=interp(head_rows,z,1);back=interp(head_rows,z,3)
    for j in range(N):
        a=2*pi*j/N;x=w*sin(a)
        y=face_y(x,z) if cos(a)>=0 else -.012+back*cos(a)
        head.data.vertices[i*N+j].co=(x,y,z)
head.data.update()
for sign,label in [(-1,'L'),(1,'R')]:
    cx=sign*.038;cz=1.687
    vs=[];segments=64
    for k in range(7):
        r=k/6
        for j in range(segments):
            t=2*pi*j/segments
            dx=.023*r*cos(t);dz=(.009 if sin(t)>0 else .0065)*r*sin(t)+sign*.09*dx
            y=.072+.007*(1-r*r)
            vs.append((cx+dx,y,cz+dz))
    fs=[(k*segments+j,k*segments+(j+1)%segments,(k+1)*segments+(j+1)%segments,(k+1)*segments+j) for k in range(6) for j in range(segments)]
    mesh('ADA_Eye_Aperture_'+label,vs,fs)
    vs=[]
    for k in range(5):
        u=k/4;r=1+.42*u
        for j in range(segments):
            t=2*pi*j/segments;dx=.023*r*cos(t);dz=(.009 if sin(t)>0 else .0065)*r*sin(t)+sign*.09*dx
            x=cx+dx;z=cz+dz
            yy=(1-u)*.072+u*face_y(x,z)+.002*sin(pi*u)
            vs.append((x,yy,z))
    fs=[(k*segments+j,k*segments+(j+1)%segments,(k+1)*segments+(j+1)%segments,(k+1)*segments+j) for k in range(4) for j in range(segments)]
    mesh('ADA_Lid_Transition_'+label,vs,fs)
    pts=[]
    for j in range(65):
        t=2*pi*j/64;dx=.023*cos(t);dz=(.009 if sin(t)>0 else .0065)*sin(t)+sign*.09*dx
        pts.append((cx+dx,.0722,cz+dz))
    tube('ADA_Lid_Rim_'+label,pts,.0014)
    pts=[(cx+.006*cos(2*pi*j/48),.0785,cz+.006*sin(2*pi*j/48)) for j in range(49)]
    tube('ADA_Iris_Incision_'+label,pts,.00055)
    pts=[];rs=[]
    for j in range(25):
        t=j/24;x=sign*(.017+.047*t);z=1.704+.008*sin(pi*t)-.005*t
        pts.append((x,face_y(x,z)+.0025,z));rs.append(.001+ .003*(sin(pi*t)**.6))
    tube('ADA_Brow_Form_'+label,pts,rs,sides=8)
    vs=[]
    for k in range(9):
        r=k/8
        for j in range(64):
            t=2*pi*j/64
            y=-.014+.014*r*cos(t)
            z=1.669+.025*r*sin(t)
            x=sign*(.081+.017*sin(pi*r*.78)+.002*cos(t))
            vs.append((x,y,z))
    fs=[(k*64+j,k*64+(j+1)%64,(k+1)*64+(j+1)%64,(k+1)*64+j) for k in range(8) for j in range(64)]
    ear=mesh('ADA_Ear_Pinna_'+label,vs,fs);shell(ear,.003,0)
    pts=[]
    for j in range(49):
        t=2*pi*j/48
        pts.append((sign*(.094+.002*cos(t)),-.014+.013*cos(t),1.669+.024*sin(t)))
    tube('ADA_Ear_Helix_'+label,pts,.0027)
bpy.ops.object.select_all(action='DESELECT')
view((.7,2,1.69),(0,0,1.665),.46)
bpy.context.scene['as1_operation_id']='clay-r001-face'
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print('Original face cage refined; paired lid transitions, closed lip relief and ear anatomy created.')


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
    v+=gauss(x,z,0,1.677,.013,.034,.020)
    v+=gauss(x,z,0,1.652,.015,.010,.023)
    v+=gauss(x,z,.014,1.644,.009,.007,.013)+gauss(x,z,-.014,1.644,.009,.007,.013)
    v+=gauss(x,z,0,1.620,.032,.022,.009)
    cup=.002*exp(-((abs(x)-.007)/.005)**2)
    v+=gauss(x,z,0,1.613+cup,.024,.003,.006)+gauss(x,z,0,1.604,.022,.004,.007)
    v-=gauss(x,z,0,1.608+.0015*(x/.024)**2,.024,.0012,.003)
    v+=gauss(x,z,0,1.584,.032,.011,.004)
    for sx in [-1,1]:
        v-=gauss(x,z,sx*.038,1.687,.025,.011,.010)
        v+=gauss(x,z,sx*.047,1.663,.029,.014,.005)
        v+=gauss(x,z,sx*.038,1.707,.030,.008,.005)
    return v

assert bpy.context.scene.get('as1_operation_id')=='clay-r001-face'
head=bpy.data.objects['ADA_Head_Continuous'];N=160;Z=140
for i in range(Z+1):
    z=1.563+.235*i/Z;w=interp(head_rows,z,1);back=interp(head_rows,z,3)
    for j in range(N):
        a=2*pi*j/N;x=w*sin(a);y=face_y(x,z) if cos(a)>=0 else -.012+back*cos(a)
        head.data.vertices[i*N+j].co=(x,y,z)
for sign,label in [(-1,'L'),(1,'R')]:
    cx=sign*.038;cz=1.687
    eye=bpy.data.objects['ADA_Eye_Aperture_'+label]
    for v in eye.data.vertices:
        x,y,z=v.co;r2=((x-cx)/.023)**2+((z-cz-sign*.09*(x-cx))/(.009 if z-cz-sign*.09*(x-cx)>0 else .0065))**2
        v.co.y=face_y(x,z)+.0018+.006*max(0,1-r2)
    lid=bpy.data.objects['ADA_Lid_Transition_'+label]
    for v in lid.data.vertices:
        u=(v.index//64)/4
        x,y,z=v.co;v.co.y=face_y(x,z)+.0018*(1-u)+.0015*sin(pi*u)
    rim=bpy.data.objects['ADA_Lid_Rim_'+label]
    for v in rim.data.vertices:
        x,y,z=v.co;v.co.y=face_y(x,z)+.002+(y-.0722)*.65
    iris=bpy.data.objects['ADA_Iris_Incision_'+label]
    for v in iris.data.vertices:
        x,y,z=v.co;v.co.y=face_y(x,z)+.0018+.006*(1-((x-cx)/.023)**2-((z-cz)/.009)**2)+.0003
    brow=bpy.data.objects['ADA_Brow_Form_'+label]
    for v in brow.data.vertices:
        x,y,z=v.co;v.co.y=face_y(x,z)+.001+(y-face_y(x,z)-.0025)*.4
bpy.context.scene['as1_operation_id']='clay-r001-lid-fit'
bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print('Lid and eye patches now conform to continuous face curvature; nose projection and cheek inflation reduced.')


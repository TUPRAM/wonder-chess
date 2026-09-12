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

assert bpy.context.scene.get('as1_operation_id')=='clay-r001-hair'
# Paired front/back shells preserve sternum ridge and deliberate upper arm cutouts.
rows=[(1.192,.122,.086),(1.217,.125,.091),(1.30,.146,.112),(1.382,.171,.120),(1.44,.137,.096),(1.479,.078,.074)]
for side,label in [(1,'Breastplate'),(-1,'Backplate')]:
    vs=[];NX=16
    for i,(z,width,dep) in enumerate(rows):
        for j in range(NX+1):
            u=-1+2*j/NX;x=width*u
            yy=-.021+side*(dep*(1-.37*abs(u)**1.35)+(.009*(1-abs(u)) if side==1 else 0))
            zz=z
            if i==0:zz-=.012*(1-abs(u))
            if i==3:zz-=.017*(1-abs(u))
            if i==5:zz+=.01*abs(u)
            vs.append((x,yy,zz))
    fs=[(i*(NX+1)+j,i*(NX+1)+j+1,(i+1)*(NX+1)+j+1,(i+1)*(NX+1)+j) for i in range(len(rows)-1) for j in range(NX)]
    o=mesh('ADA_'+label,vs,fs,'STUDY_ARMOR',False);shell(o,.005,.0017)
    o['construction']='Original longitudinal shell cage; sternum plane; separate front/back; intentional neck/arm/waist openings'
# Padded collar has hollow inner wall and a lower front opening.
vs=[];N=96
for k in range(4):
    for j in range(N):
        a=2*pi*j/N
        outer=k in (0,1);upper=k in (1,2)
        w=.082 if outer else .069;d=.066 if outer else .054
        z=(1.564 if upper else 1.492)-.012*max(0,cos(a))+.004*sin(a)
        vs.append((w*sin(a),-.019+d*cos(a),z))
fs=[(k*N+j,k*N+(j+1)%N,((k+1)%4)*N+(j+1)%N,((k+1)%4)*N+j) for k in range(4) for j in range(N)]
collar=mesh('ADA_Padded_Collar',vs,fs,'STUDY_COSTUME');bev=collar.modifiers.new('Rounded padded borders','BEVEL');bev.width=.003;bev.segments=3
pts=[]
for j in range(97):
    a=2*pi*j/96;pts.append((.081*sin(a),-.019+.065*cos(a),1.564-.012*max(0,cos(a))+.004*sin(a)))
tube('ADA_Collar_Upper_Piping',pts,.0028,'STUDY_COSTUME')
# One upper-arm sleeve; other side intentionally stays open for the study.
sleeve=loft('ADA_Study_Sleeve_R',[(1.225,.043,.047,-.02),(1.28,.054,.057,-.02),(1.37,.063,.065,-.02),(1.422,.053,.055,-.02)],'STUDY_COSTUME')
for v in sleeve.data.vertices:
    v.co.x+=.203+(1.42-v.co.z)*.28
# Shoulder plates travel from collar-side high point over the outer deltoid.
for k,(x0,x1,z0,z1,dep) in enumerate([(.120,.276,1.496,1.398,.115),(.188,.301,1.434,1.341,.119),(.221,.305,1.364,1.302,.100)]):
    vs=[];U=10;V=18
    for i in range(U+1):
        u=i/U;x=x0+(x1-x0)*u
        for j in range(V+1):
            a=-pi/2+pi*j/V
            yy=-.023+dep*sin(a)
            zz=z0+(z1-z0)*u+.020*sin(pi*u)-.055*(abs(sin(a))**1.7)
            xx=x-.021*(abs(sin(a))**1.7)
            vs.append((xx,yy,zz))
    fs=[(i*(V+1)+j,i*(V+1)+j+1,(i+1)*(V+1)+j+1,(i+1)*(V+1)+j) for i in range(U) for j in range(V)]
    o=mesh('ADA_Shoulder_R_Plate_'+str(k+1),vs,fs,'STUDY_ARMOR');shell(o,.005,.002)
    o['construction']='Three-part shoulder study; separate finite shell, articulation gap preserved'
    pts=[vs[U*(V+1)+j] for j in range(V+1)]
    tube('ADA_Shoulder_R_Rolled_Edge_'+str(k+1),pts,.0028,'STUDY_ARMOR')
# Original upper two fastener attachment locations, without tertiary engraving.
for sx in [-1,1]:
    points=[(sx*.092,.053,1.479),(sx*.12,.057,1.451),(sx*.123,.058,1.421)]
    tube('ADA_Upper_Attachment_'+('R' if sx>0 else 'L'),points,[.009,.009,.006],'STUDY_ARMOR',8)
bpy.ops.object.select_all(action='DESELECT')
view((.8,2,1.68),(0,0,1.50),.91)
bpy.context.scene['as1_operation_id']='clay-r001-assembly'
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print('Hollow padded collar, sternum shell, separate backplate, sleeve and three finite shoulder shells authored.')


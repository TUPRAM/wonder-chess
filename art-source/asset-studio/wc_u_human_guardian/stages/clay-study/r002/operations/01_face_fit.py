import bpy
import math
import json
import bmesh
from mathutils import Vector
from math import sin, cos, pi, sqrt, exp
assert bpy.data.filepath.replace('\\','/').endswith('/live/ada_clay_study_r002.blend')
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

head_rows=[(1.563,.009,.025,.035),(1.575,.040,.065,.045),(1.591,.060,.068,.059),(1.615,.071,.070,.073),(1.646,.083,.073,.086),(1.672,.084,.074,.091),(1.693,.080,.070,.096),(1.720,.080,.075,.095),(1.747,.075,.070,.089),(1.770,.062,.056,.075),(1.788,.036,.035,.045),(1.798,.002,.002,.002)]
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
        v-=gauss(x,z,sx*.038,1.687,.026,.014,.008)
        v+=gauss(x,z,sx*.047,1.663,.029,.014,.005)
        v+=gauss(x,z,sx*.038,1.707,.030,.008,.005)
    return v

assert bpy.context.scene.get('as1_operation_id')=='clay-r002-initialize'
vs=[];N=160;Z=140
for i in range(Z+1):
    z=1.563+.235*i/Z;w=interp(head_rows,z,1);back=interp(head_rows,z,3)
    for j in range(N):
        a=2*pi*j/N;x=w*sin(a);y=face_y(x,z) if cos(a)>=0 else -.012+back*cos(a);vs.append((x,y,z))
fs=[(i*N+j,i*N+(j+1)%N,(i+1)*N+(j+1)%N,(i+1)*N+j) for i in range(Z) for j in range(N)]
fs.extend([tuple(range(N-1,-1,-1)),tuple(Z*N+j for j in range(N))])
m=bpy.data.meshes.new('ADA_Head_Fitted_Almond_Cage');m.from_pydata(vs,[],fs);m.update()
bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
cut=[]
for f in bm.faces:
    p=f.calc_center_median()
    if p.y>0:
        for s in (-1,1):
            dx=p.x-s*.038;dz=p.z-1.687-s*.08*dx
            if (dx/.032)**2+(dz/.019)**2<1:cut.append(f);break
bmesh.ops.delete(bm,geom=cut,context='FACES')
loose=[v for v in bm.verts if not v.link_faces]
if loose:bmesh.ops.delete(bm,geom=loose,context='VERTS')
boundary={e for e in bm.edges if e.is_boundary};loops=[]
while boundary:
    e=next(iter(boundary));start=e.verts[0];cur=e.verts[1];loop=[start];boundary.remove(e)
    while cur!=start:
        loop.append(cur);candidates=[q for q in cur.link_edges if q in boundary];assert len(candidates)==1
        e=candidates[0];boundary.remove(e);cur=e.other_vert(cur)
    loops.append(loop)
def opening(sign,t):
    dx=.0228*cos(t)
    dz=(.012 if sin(t)>0 else .009)*sin(t)*abs(sin(t))+sign*.08*dx
    x=sign*.038+dx;z=1.687+dz
    return Vector((x,face_y(x,z)+.0012,z))
for loop in loops:
    sign=1 if sum(v.co.x for v in loop)>0 else -1
    original=[v.co.copy() for v in loop];inner=[]
    for p in original:
        dx=p.x-sign*.038;dz=p.z-1.687-sign*.08*dx
        inner.append(opening(sign,math.atan2(dz/.019,dx/.032)))
    prev=loop
    for u in (.2,.4,.6,.8,1):
        curr=[]
        for p,q in zip(original,inner):
            v=p.lerp(q,u);v.y=face_y(v.x,v.z)+.0012*u+.0014*sin(pi*u)
            curr.append(bm.verts.new(v))
        for j in range(len(curr)):
            j1=(j+1)%len(curr);bm.faces.new((prev[j],prev[j1],curr[j1],curr[j]))
        prev=curr
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.normal_update()
bad=sum(not e.is_contiguous for e in bm.edges if len(e.link_faces)==2);assert bad==0
bm.to_mesh(m);bm.free();head=bpy.data.objects['ADA_Head_Continuous'];head.data=m
for p in m.polygons:p.use_smooth=True
for sign,label in [(-1,'L'),(1,'R')]:
    old=bpy.data.objects['ADA_Eye_Aperture_'+label];old.hide_set(True);old.hide_render=True
    cx=sign*.038;cz=1.687
    pts=[(cx,face_y(cx,cz)+.0038,cz)];S=96;R=12
    for k in range(1,R+1):
        r=k/R
        for j in range(S):
            p=opening(sign,2*pi*j/S)
            x=cx+(p.x-cx)*r;z=cz+(p.z-cz)*r
            y=face_y(x,z)+.001+.004*(1-r*r)
            ir=sqrt(((x-cx)/.0065)**2+((z-cz)/.0065)**2)
            y-=.0006*exp(-((ir-1)/.16)**2)+.0015*exp(-(ir/.38)**4)
            pts.append((x,y,z))
    faces=[(0,1+j,1+(j+1)%S) for j in range(S)]
    faces.extend((1+k*S+j,1+k*S+(j+1)%S,1+(k+1)*S+(j+1)%S,1+(k+1)*S+j) for k in range(R-1) for j in range(S))
    eye=mesh('ADA_Fitted_Eye_'+label,pts,faces)
    eye['construction']='Almond opening fitted to orbital surface; shallow iris/pupil relief is geometry for clay review'
    # Thin angular eyebrow surface rests directly on a supporting brow plane.
    pts=[]
    for j in range(25):
        u=j/24;x=sign*(.015+.050*u)
        z=1.706+.010*sin(pi*u*.90)-.004*u
        thick=.0042*(1-.78*u)
        for dz in (-thick/2,thick/2):
            pts.append((x,face_y(x,z+dz)+.0009,z+dz))
    faces=[(2*j,2*j+1,2*j+3,2*j+2) for j in range(24)]
    brow=mesh('ADA_Fitted_Brow_'+label,pts,faces);shell(brow,.0008,.0003)
bpy.context.scene['as1_operation_id']='clay-r002-face-fit'
view((.7,2,1.69),(0,0,1.665),.46)
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
bpy.context.scene.camera=bpy.data.objects['CAM_face']
bpy.context.scene.render.filepath='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/clay-study/r002/captures/face_after_fit.png'
bpy.ops.render.render(write_still=True)
print(json.dumps({'method':'fitted almond aperture; outer orbital cage positions preserved; broader jaw','inconsistent_winding':bad}))


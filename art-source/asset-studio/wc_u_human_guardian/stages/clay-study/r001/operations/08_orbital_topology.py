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

assert bpy.context.scene.get('as1_operation_id')=='clay-r001-construction-refine'
bpy.ops.wm.save_as_mainfile(filepath='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/clay-study/r001/attempt01.blend',copy=True)
head=bpy.data.objects['ADA_Head_Continuous'];bm=bmesh.new();bm.from_mesh(head.data)
cut=[]
for f in bm.faces:
    p=f.calc_center_median()
    if p.y<=0:continue
    for s in (-1,1):
        dx=p.x-s*.038;dz=p.z-1.687-s*.09*dx
        if (dx/.030)**2+(dz/.014)**2 < 1:cut.append(f);break
bmesh.ops.delete(bm,geom=cut,context='FACES')
isolated=[v for v in bm.verts if not v.link_faces]
if isolated:bmesh.ops.delete(bm,geom=isolated,context='VERTS')
boundary={v for e in bm.edges if e.is_boundary for v in e.verts}
components=[]
while boundary:
    start=next(iter(boundary));seen={start};todo=[start]
    while todo:
        v=todo.pop()
        for e in v.link_edges:
            if e.is_boundary:
                w=e.other_vert(v)
                if w not in seen:seen.add(w);todo.append(w)
    boundary-=seen;components.append(list(seen))
assert len(components)==2, 'Expected two actual orbital openings'
def eye_point(sign,t,r):
    dx=.0225*r*cos(t);dz=(.0095 if sin(t)>0 else .0075)*r*sin(t)+sign*.09*dx
    x=sign*.038+dx;z=1.687+dz
    y=.056-sign*.35*dx+.008*sqrt(max(0,1-(dx/.029)**2-((dz-sign*.09*dx)/.024)**2))
    return Vector((x,y,z))
for component in components:
    sign=1 if sum(v.co.x for v in component)>0 else -1
    def angle(v):
        dx=v.co.x-sign*.038;dz=v.co.z-1.687-sign*.09*dx
        return math.atan2(dz/.014,dx/.030)
    component.sort(key=angle)
    angles=[angle(v) for v in component]
    for v,t in zip(component,angles):
        p=eye_point(sign,t,1.38);v.co=(p.x,face_y(p.x,p.z),p.z)
    previous=component
    for r in (1.22,1.10,1.0,.98):
        current=[]
        for t in angles:
            p=eye_point(sign,t,r)
            mix=min(1,max(0,(1.38-r)/.38))
            surface=face_y(p.x,p.z)
            p.y=surface*(1-mix)+p.y*mix+.0018*sin(pi*mix)
            if r==.98:p.y-=.0012
            current.append(bm.verts.new(p))
        for j in range(len(current)):
            j1=(j+1)%len(current);bm.faces.new((previous[j],previous[j1],current[j1],current[j]))
        previous=current
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(head.data);bm.free();head.data.update()
for p in head.data.polygons:p.use_smooth=True
for sign,label in [(-1,'L'),(1,'R')]:
    for base in ['ADA_Lid_Transition_','ADA_Lid_Rim_','ADA_Iris_Incision_','ADA_Brow_Form_']:
        o=bpy.data.objects[base+label];o.hide_set(True);o.hide_render=True
    eye=bpy.data.objects['ADA_Eye_Aperture_'+label]
    for v in eye.data.vertices:
        j=v.index%64;k=v.index//64;t=2*pi*j/64;r=k/6
        p=eye_point(sign,t,r);p.y-=.0012;v.co=p
    eye['construction']='Convex visible globe aperture behind eyelids bridged into the head mesh'
# Broad integrated brow planes and jaw emphasis, without detached eyebrow tubes.
for v in head.data.vertices:
    x,y,z=v.co
    if y>0:
        add=0
        for s in (-1,1):
            add+=gauss(x,z,s*.039,1.708,.028,.006,.003)
        v.co.y+=add
head['construction']='Original continuous cage with two cut orbital openings and four bridged eyelid loops per opening'
bpy.context.scene['as1_operation_id']='clay-r001-orbital-topology'
view((.7,2,1.69),(0,0,1.665),.46)
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print(json.dumps({'orbital_openings':len(components),'head_vertices':len(head.data.vertices),'method_change':'actual orbital holes and bridged lid topology; separate loops hidden'}))


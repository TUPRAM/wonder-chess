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

assert bpy.context.scene.get('as1_operation_id')=='clay-r001-orbital-topology'
# Rebuild the full hair volume as one continuous swept scalp surface.
old=bpy.data.objects['ADA_Hair_Sculpt_Surface'];old.hide_set(True);old.hide_render=True
vs=[];N=192;R=100
for i in range(R+1):
    u=i/R
    for j in range(N):
        a=2*pi*j/N
        phi=a+.62*(1-u)**1.4
        f=max(0,cos(phi));back=max(0,-cos(phi))
        end=1.84-.57*f+.18*back+.04*sin(3*phi)
        t=.003+(end-.003)*u
        # Nine broad flowing masses are part of the surface rather than strips laid on it.
        phase=9*a+1.3*sin(pi*u)+.5*sin(a)
        bump=(.002+.010*(.5+.5*cos(phase))**1.5)*sin(t)**.8
        rx=.097+bump+.005*max(0,-sin(phi))
        dep=(.089 if cos(phi)>0 else .107)+bump
        x=rx*sin(t)*sin(phi)+.010*cos(t)**2*(1-u)
        y=-.021+dep*sin(t)*cos(phi)
        z=1.686+(.131+bump*.35)*cos(t)
        vs.append((x,y,z))
fs=[(i*N+j,i*N+(j+1)%N,(i+1)*N+(j+1)%N,(i+1)*N+j) for i in range(R) for j in range(N)]
fs.append(tuple(range(N-1,-1,-1)))
hair=mesh('ADA_Hair_Continuous_Sweep',vs,fs,'STUDY_HAIR');shell(hair,.008,0)
hair['construction']='Continuous asymmetric sculpt mesh with nine broad swept volumes and scalloped hairline; replaces ribbon assembly'
# Compact, fuller braid at upper back, retaining three editable strands.
for o in collection('STUDY_HAIR').objects:
    if o.name.startswith('ADA_Braid_'):
        for v in o.data.vertices:
            v.co.z=1.656+(v.co.z-1.656)*.72
            v.co.x*=1.25
# Compact cupped shoulder shells with front/back skirts and overlapping roots.
for o in list(collection('STUDY_ARMOR').objects):
    if o.name.startswith('ADA_Shoulder_R'):
        o.hide_set(True);o.hide_render=True
for k,(x0,x1,z0,drop,dep) in enumerate([(.128,.273,1.515,.084,.109),(.207,.290,1.468,.071,.110),(.249,.302,1.414,.055,.099)]):
    vs=[];U=16;V=28
    for i in range(U+1):
        u=i/U;x=x0+(x1-x0)*u
        for j in range(V+1):
            a=-pi/2+pi*j/V
            y=-.022+dep*sin(a)
            z=z0-drop*(u*u if k==0 else u)+(.018*sin(pi*u) if k==0 else .007*sin(pi*u))-.040*abs(sin(a))**1.5
            vs.append((x-.009*abs(sin(a)),y,z))
    fs=[(i*(V+1)+j,i*(V+1)+j+1,(i+1)*(V+1)+j+1,(i+1)*(V+1)+j) for i in range(U) for j in range(V)]
    for edge in (0,V):
        lower=[]
        for i in range(U+1):
            p=Vector(vs[i*(V+1)+edge]);p.z-=.030*(.5+.5*sin(pi*i/U));p.y+=(-.006 if edge==0 else .006)
            lower.append(len(vs));vs.append(tuple(p))
        fs.extend((i*(V+1)+edge,(i+1)*(V+1)+edge,lower[i+1],lower[i]) for i in range(U))
    o=mesh('ADA_Cupped_Shoulder_R_'+str(k+1),vs,fs,'STUDY_ARMOR');shell(o,.0045,.002)
    o['construction']='Cupped surface with side skirts; roots nested below previous plate; three-piece representative shoulder'
# Recess the globe and inner lid, then relax stretched outer orbital quads.
head=bpy.data.objects['ADA_Head_Continuous']
bm=bmesh.new();bm.from_mesh(head.data)
for v in bm.verts:
    x,y,z=v.co
    if y>0:
        for s in (-1,1):
            dx=x-s*.038;dz=z-1.687-s*.09*dx
            r=sqrt((dx/.0225)**2+(dz/(.0095 if dz>0 else .0075))**2)
            if .9<r<1.4 and 1.66<z<1.708:
                v.co.y-=.008*max(0,min(1,(1.4-r)/.4))
outer=[v for v in bm.verts if v.co.y>0 and 1.666<v.co.z<1.709 and .005<abs(v.co.x)<.073 and not v.is_boundary]
for i in range(5):
    bmesh.ops.smooth_vert(bm,verts=outer,factor=.35,use_axis_x=True,use_axis_y=True,use_axis_z=True)
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(head.data);bm.free()
for label in ('L','R'):
    o=bpy.data.objects['ADA_Eye_Aperture_'+label]
    for v in o.data.vertices:v.co.y-=.008
view((.8,2,1.68),(0,0,1.50),.91)
bpy.context.scene['as1_operation_id']='clay-r001-method-rebuild'
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
for name in ['front','profile','back','face','three_quarter']:
    bpy.context.scene.camera=bpy.data.objects['CAM_'+name]
    bpy.context.scene.render.filepath='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/clay-study/r001/captures/'+name+'_r002.png'
    bpy.ops.render.render(write_still=True)
bpy.context.scene.camera=bpy.data.objects['CAM_three_quarter']
print('Changed-method candidate captured in five fixed views: continuous hair sweep, compact braid, actual orbital openings, cupped overlapping shoulder.')


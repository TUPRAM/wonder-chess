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

assert bpy.context.scene.get('as1_operation_id')=='clay-r002-face-fit'
for o in collection('STUDY_HAIR').objects:
    if o.name.startswith('ADA_Swept_Lock_'):o.hide_set(True);o.hide_render=True
def path_samples(points,samples=80):
    result=[]
    for i in range(samples):
        q=(len(points)-1)*i/(samples-1);k=min(len(points)-2,int(q));t=q-k
        a=Vector(points[max(0,k-1)]);b=Vector(points[k]);c=Vector(points[k+1]);d=Vector(points[min(len(points)-1,k+2)])
        result.append(.5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t))
    return result
paths=[
[(-.080,.026,1.690),(-.083,.063,1.723),(-.041,.091,1.749),(.001,.080,1.779),(.014,.023,1.813),(-.020,-.068,1.775)],
[(.083,.028,1.691),(.086,.059,1.720),(.061,.088,1.743),(.030,.080,1.769),(.018,.026,1.813),(.049,-.074,1.776)],
[(-.093,-.025,1.679),(-.100,.018,1.710),(-.077,.047,1.757),(-.045,.018,1.796),(-.053,-.064,1.77),(-.043,-.113,1.681)],
[(.097,-.019,1.680),(.100,.011,1.718),(.084,.029,1.758),(.058,-.013,1.801),(.077,-.073,1.753),(.044,-.120,1.671)],
[(-.095,-.039,1.713),(-.084,-.012,1.772),(-.050,-.040,1.810),(-.05,-.095,1.753),(-.065,-.11,1.697),(-.011,-.135,1.650)],
[(.008,-.006,1.820),(.047,-.043,1.802),(.070,-.089,1.752),(.053,-.12,1.705),(.011,-.136,1.650)],
[(-.039,-.048,1.802),(-.029,-.101,1.765),(-.025,-.132,1.716),(.015,-.141,1.681),(.011,-.142,1.647)],
[(.022,-.063,1.798),(.041,-.108,1.76),(.025,-.137,1.725),(-.009,-.14,1.680),(-.009,-.143,1.647)]]
for group,points in enumerate(paths):
    ps=path_samples(points);count=3 if group<2 else 2
    for strand in range(count):
        offset=(strand-(count-1)/2)*.014
        vs=[];S=16
        for i,p in enumerate(ps):
            u=i/(len(ps)-1);t=(ps[min(len(ps)-1,i+1)]-ps[max(0,i-1)]).normalized()
            normal=(p-Vector((0,-.02,1.69))).normalized();side=t.cross(normal).normalized();normal=side.cross(t).normalized()
            center=p+side*(offset*(.6+.4*sin(pi*u)))+normal*(.002*sin(3*pi*u+strand))
            r=.0007+.013*(sin(pi*u)**.50)
            for j in range(S):
                a=2*pi*j/S;v=center+side*r*cos(a)+normal*r*.88*sin(a)
                vs.append(tuple(v))
        fs=[(i*S+j,i*S+(j+1)%S,(i+1)*S+(j+1)%S,(i+1)*S+j) for i in range(len(ps)-1) for j in range(S)]
        fs.extend([tuple(range(S-1,-1,-1)),tuple((len(ps)-1)*S+j for j in range(S))])
        o=mesh('ADA_Overlapping_Lock_%02d_%d'%(group,strand),vs,fs,'STUDY_HAIR')
        o['construction']='Solid tapered major hair clump with depth, sweep and offset overlap; no hair cards or texture'
view((.7,2,1.69),(0,0,1.665),.47)
bpy.context.scene['as1_operation_id']='clay-r002-overlap-hair'
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
bpy.context.scene.camera=bpy.data.objects['CAM_face']
bpy.context.scene.render.filepath='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/clay-study/r002/captures/hair_after_overlap.png'
bpy.ops.render.render(write_still=True)
print('18 smaller solid overlapping tapered locks replace eight broad flattened bands.')


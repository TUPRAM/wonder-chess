import bpy
import math
import json
import bmesh
from mathutils import Vector
from math import sin, cos, pi, sqrt, exp
assert bpy.data.filepath.replace('\\','/').endswith('/live/ada_clay_study_r003.blend')
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


from mathutils.bvhtree import BVHTree
assert bpy.context.scene.get('as1_operation_id')=='clay-r003-spatial-lid-blend'
scalp=bpy.data.objects['ADA_Hair_Foundation']
bvh=BVHTree.FromObject(scalp,bpy.context.evaluated_depsgraph_get())
for o in collection('STUDY_HAIR').objects:
    if o.name.startswith('ADA_Overlapping_Lock_') or o.name.startswith('ADA_Temporal_Sweep_'):
        o.hide_render=True;o.hide_set(True)
def samples(points,n=80):
    ps=[]
    for i in range(n):
        v=(len(points)-1)*i/(n-1);k=min(len(points)-2,int(v));t=v-k
        a=Vector(points[max(0,k-1)]);b=Vector(points[k]);c=Vector(points[k+1]);d=Vector(points[min(len(points)-1,k+2)])
        ps.append(.5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t))
    return ps
def supported_mass(name,points,width,depth,phase):
    guides=samples(points);centers=[bvh.find_nearest(p)[0] for p in guides]
    vs=[];C=24;N=len(guides)
    for layer in (0,1):
        for i,p in enumerate(centers):
            u=i/(N-1);normal=bvh.find_nearest(p)[1]
            if normal.dot(p-Vector((0,-.025,1.69)))<0:normal=-normal
            tangent=(centers[min(N-1,i+1)]-centers[max(0,i-1)]).normalized()
            side=tangent.cross(normal).normalized()
            breadth=.0015+width*sin(pi*u)**.55*(1+.12*sin(3*pi*u+phase))
            for j in range(C+1):
                v=-1+2*j/C
                q=p+side*breadth*v
                support,n,face,d=bvh.find_nearest(q)
                if n.dot(support-Vector((0,-.025,1.69)))<0:n=-n
                bulge=depth*(max(0,1-v*v)**.72)*(.12+.88*sin(pi*u)**.5)
                # Ends and margins overlap their actual scalp support.
                height=(-.0018 if layer else -.001+bulge)
                vs.append(tuple(support+n*height))
    fs=[];M=N*(C+1)
    for layer in (0,1):
        off=layer*M
        for i in range(N-1):
            for j in range(C):
                f=(off+i*(C+1)+j,off+(i+1)*(C+1)+j,off+(i+1)*(C+1)+j+1,off+i*(C+1)+j+1)
                fs.append(f if layer==0 else tuple(reversed(f)))
    perimeter=list(range(C+1))+[i*(C+1)+C for i in range(1,N)]+[(N-1)*(C+1)+j for j in range(C-1,-1,-1)]+[i*(C+1) for i in range(N-2,0,-1)]
    for j,a in enumerate(perimeter):
        b=perimeter[(j+1)%len(perimeter)];fs.append((a,b,b+M,a+M))
    o=mesh(name,vs,fs,'STUDY_HAIR')
    o['construction']='Broad closed scalp-supported mass; each surface sample projected onto actual scalp BVH; no free tube path'
    return o
points=[(.026,.035,1.804),(-.022,.052,1.789),(-.067,.045,1.763),(-.095,.015,1.719),(-.095,-.054,1.697),(-.033,-.127,1.665)]
supported_mass('ADA_Scalp_Supported_Sweep_01',points,.027,.012,.4)
bpy.context.scene['as1_operation_id']='clay-r003-supported-hair-proof'
view((.8,2,1.73),(0,0,1.70),.5)
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
for name in ['face','profile','back']:
    bpy.context.scene.camera=bpy.data.objects['CAM_'+name]
    bpy.context.scene.render.filepath='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/clay-study/r003/captures/'+name+'_supported_mass.png'
    bpy.ops.render.render(write_still=True)
print('One broad scalp-supported solid mass created; old tubular locks retained hidden.')


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


assert bpy.context.scene.get('as1_operation_id')=='clay-r003-supported-hair-proof'
root='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian'
bpy.ops.wm.save_as_mainfile(filepath=root+'/stages/clay-study/r003/failed_region_proof.blend',copy=True)
head=bpy.data.objects['ADA_Head_Continuous']
failed=head.copy();failed.data=head.data.copy();failed.name='ADA_Head_r003_Failed_Proof'
collection('STUDY_ORGANIC').objects.link(failed);failed.hide_render=True;failed.hide_set(True)
head.data=bpy.data.objects['ADA_Head_r002_Preserved'].data.copy()
for label in ['L','R']:
    for prefix in ['ADA_Spherical_Ocular_','ADA_Shaped_Brow_']:
        o=bpy.data.objects[prefix+label];o.hide_render=True;o.hide_set(True)
    for prefix in ['ADA_Fitted_Eye_','ADA_Fitted_Brow_']:
        o=bpy.data.objects[prefix+label];o.hide_render=False;o.hide_set(False)
for o in collection('STUDY_HAIR').objects:
    if o.name.startswith('ADA_Scalp_Supported_Sweep_'):
        o.hide_render=True;o.hide_set(True)
    if o.name.startswith('ADA_Overlapping_Lock_') or o.name.startswith('ADA_Temporal_Sweep_'):
        o.hide_render=False;o.hide_set(False)
scene=bpy.context.scene
scene['as1_operation_id']='clay-r003-restored-best-r002'
scene['as1_study_status']='REVISE: method limit; r003 proof failed; better r002 face/hair restored; no likeness approval'
scene['as1_feedback']='Pram: Mostly face and hair. Actual focused attempts retained; no forms approval.'
view((.8,2,1.68),(0,0,1.50),.91)
for o in bpy.context.selected_objects:o.select_set(False)
for name in ['front','profile','back','face','three_quarter']:
    scene.camera=bpy.data.objects['CAM_'+name]
    scene.render.filepath=root+'/stages/clay-study/r003/captures/'+name+'_restored.png'
    bpy.ops.render.render(write_still=True)
scene.camera=bpy.data.objects['CAM_three_quarter']
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
bpy.ops.wm.save_as_mainfile(filepath=root+'/stages/clay-study/r003/ada_clay_checkpoint.blend',copy=True)
print(json.dumps({'live':bpy.data.filepath,'state':'Better r002 face and hair restored; failed r003 method preserved separately','approval':'references only; no forms approval'}))


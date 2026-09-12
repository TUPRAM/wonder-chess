import bpy,json
from mathutils import Vector,Matrix
s=bpy.context.scene
r=bpy.data.objects['BW1_Temporary_Pose_Rig']
dg=bpy.context.evaluated_depsgraph_get()
re=r.evaluated_get(dg)
def h(n):return re.matrix_world@re.pose.bones[n].head
O=h('wrist.R'); M=h('finger3-1.R')
Y=(M-O).normalized()
raw=h('finger2-1.R')-h('finger5-1.R')
X=(raw-Y*raw.dot(Y)).normalized()
Z=X.cross(Y).normalized()
g=bpy.data.objects['BW1_Glove_Pair_SourceFit']
for o in s.objects:
    if o.type=='MESH':
        o['BW2_prior_hide_render']=o.hide_render
        o['BW2_prior_hide_view']=o.hide_get()
        o.hide_render=o!=g
        o.hide_set(o!=g)
camdata=bpy.data.cameras.new('BW2_calibration_palm')
cam=bpy.data.objects.new('BW2_calibration_palm',camdata)
s.collection.objects.link(cam)
target=O+Y*.083
cam.location=target+Z*.45
cam.rotation_euler=Matrix((X,Y,Z)).transposed().to_quaternion().to_euler()
camdata.type='ORTHO';camdata.ortho_scale=.235
s.camera=cam;s.render.resolution_x=1000;s.render.resolution_y=1000
s.render.image_settings.file_format='PNG';s.cycles.samples=24
s.render.filepath='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW2/r001/captures/calibration_first_side.png'
bpy.ops.render.render(write_still=True)
for a in bpy.context.screen.areas:
    if a.type=='VIEW_3D':
        a.spaces.active.region_3d.view_perspective='CAMERA'
        a.spaces.active.region_3d.view_camera_zoom=8
        a.spaces.active.overlay.show_overlays=False
ge=g.evaluated_get(dg)
verts=[{'index':v.index,'world':list(ge.matrix_world@v.co),'normal':list((ge.matrix_world.to_3x3().inverted().transposed()@v.normal).normalized())} for v in ge.data.vertices if (ge.matrix_world@v.co-O).length<.22]
def near_key(v):
    return (Vector(v['world'])-(O+Y*.055+Z*.014)).length
near=sorted(verts,key=near_key)[:5]
print(json.dumps({'O':list(O),'X':list(X),'Y':list(Y),'Z_provisional':list(Z),'near_provisional_palm':near,'evaluated_vertices':len(ge.data.vertices)}))

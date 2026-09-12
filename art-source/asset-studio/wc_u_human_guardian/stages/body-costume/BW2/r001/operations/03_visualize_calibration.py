import bpy,json,math
from mathutils import Vector,Matrix
s=bpy.context.scene;r=bpy.data.objects['BW1_Temporary_Pose_Rig'];g=bpy.data.objects['BW1_Glove_Pair_SourceFit']
dg=bpy.context.evaluated_depsgraph_get();re=r.evaluated_get(dg);ge=g.evaluated_get(dg)
def h(n):return re.matrix_world@re.pose.bones[n].head
O=h('wrist.R');Y=(h('finger3-1.R')-O).normalized();raw=h('finger2-1.R')-h('finger5-1.R');X=(raw-Y*raw.dot(Y)).normalized();Z=X.cross(Y).normalized()
F=Matrix((X,Y,Z)).transposed().to_4x4();F.translation=O
palm=ge.matrix_world@ge.data.vertices[2137].co
landmarks={'wrist':list(O),'middle_mcp':list(h('finger3-1.R')),'index_mcp':list(h('finger2-1.R')),'little_mcp':list(h('finger5-1.R')),'middle_tip':list(re.matrix_world@re.pose.bones['finger3-3.R'].tail),'palmar_point':list(palm)}
col=bpy.data.collections['BW2_CONTACT_STUDY']
def into(o):
    for c in list(o.users_collection):c.objects.unlink(o)
    col.objects.link(o)
def mat(name,color):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Roughness'].default_value=.7
    return m
mats=[mat('BW2_axis_X_transverse',(.65,.07,.04)),mat('BW2_axis_Y_distal',(.08,.65,.12)),mat('BW2_axis_Z_palmar',(.04,.2,.8))]
for label,v,ma in zip(['X_transverse_INDEX','Y_distal_FINGERS','Z_palmar_PALM'],[X,Y,Z],mats):
    bpy.ops.mesh.primitive_cylinder_add(vertices=12,radius=.0012,depth=.047,location=O+v*.0235)
    o=bpy.context.object;o.name='BW2_axis_'+label;o.rotation_euler=v.to_track_quat('Z','Y').to_euler();o.data.materials.append(ma);into(o)
    bpy.ops.mesh.primitive_cone_add(vertices=12,radius1=.003,radius2=0,depth=.008,location=O+v*.051)
    o=bpy.context.object;o.name='BW2_tip_'+label;o.rotation_euler=v.to_track_quat('Z','Y').to_euler();o.data.materials.append(ma);into(o)
    data=bpy.data.curves.new('BW2_label_'+label,'FONT');data.body=label;data.size=.004
    o=bpy.data.objects.new('BW2_label_'+label,data);col.objects.link(o);o.location=O+v*.058;o.rotation_euler=F.to_euler();o.data.materials.append(ma)
bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=6,radius=.002,location=palm)
o=bpy.context.object;o.name='BW2_PALM_surface_marker_eval2137';o.data.materials.append(mats[2]);into(o)
for o in s.objects:
    if o.type=='LIGHT':o['BW2_prior_hide_render']=o.hide_render;o.hide_render=True
target=O+Y*.085
for name,location,power,size in [('key',target+Z*.26-X*.17+Y*.13,8,.22),('fill',target+Z*.2+X*.2,4,.25),('rim',target-Z*.22+X*.08,5,.2)]:
    data=bpy.data.lights.new('BW2_light_'+name,'AREA');data.energy=power;data.shape='DISK';data.size=size
    o=bpy.data.objects.new('BW2_light_'+name,data);col.objects.link(o);o.location=location;o.rotation_euler=(target-location).to_track_quat('-Z','Y').to_euler()
cams=[]
for name,view_direction,up in [('palm',Z,Y),('back',-Z,Y),('side',-X,Y),('axial',X,Y),('oblique',(Z+X*.7+Y*.25).normalized(),Y)]:
    data=bpy.data.cameras.new('BW2_cam_'+name);data.type='ORTHO';data.ortho_scale=.24
    o=bpy.data.objects.new('BW2_cam_'+name,data);col.objects.link(o);o.location=target+view_direction*.5
    zz=view_direction;xx=up.cross(zz).normalized();yy=zz.cross(xx)
    o.rotation_euler=Matrix((xx,yy,zz)).transposed().to_euler();cams.append(o)
s.camera=bpy.data.objects['BW2_cam_palm'];s.render.filepath='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW2/r001/captures/frame_axes_palm.png';bpy.ops.render.render(write_still=True)
s.camera=bpy.data.objects['BW2_cam_side'];s.render.filepath='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW2/r001/captures/frame_axes_side.png';bpy.ops.render.render(write_still=True)
s.camera=bpy.data.objects['BW2_cam_palm']
s['BW2_frame_world']=json.dumps([list(row) for row in F])
s['BW2_landmarks_open_m']=json.dumps(landmarks)
s['BW2_hand_frame_in_posebone']=json.dumps([list(row) for row in (re.matrix_world@re.pose.bones['wrist.R'].matrix).inverted()@F])
bpy.ops.wm.save_as_mainfile(filepath='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW2/r001/ada_bw2_grip_work.blend')
print(json.dumps({'landmarks_world_m':landmarks,'frame_world':[list(row) for row in F],'tip_dot_distal':(Vector(landmarks['middle_tip'])-h('finger3-1.R')).normalized().dot(Y),'palmar_side_m':Z.dot(palm-(O+h('finger3-1.R'))*.5),'determinant':F.to_3x3().determinant(),'evaluated_level':1,'evaluated_vertices':len(ge.data.vertices),'images':['frame_axes_palm.png','frame_axes_side.png']}))

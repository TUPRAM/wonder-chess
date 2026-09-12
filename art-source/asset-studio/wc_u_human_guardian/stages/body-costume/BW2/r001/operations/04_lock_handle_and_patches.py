import bpy,json,math
from mathutils import Matrix,Vector
s=bpy.context.scene;r=bpy.data.objects['BW1_Temporary_Pose_Rig'];g=bpy.data.objects['BW1_Glove_Pair_SourceFit'];F=Matrix(json.loads(s['BW2_frame_world']));Fi=F.inverted()
dg=bpy.context.evaluated_depsgraph_get();re=r.evaluated_get(dg);ge=g.evaluated_get(dg)
X=F.col[0].xyz;Y=F.col[1].xyz;Z=F.col[2].xyz
patches={}
for digit in range(1,6):
    pb=re.pose.bones['finger'+str(digit)+'-3.R'];h=re.matrix_world@pb.head;t=re.matrix_world@pb.tail;d=(t-h).normalized();L=(t-h).length
    padnormal=(Z-d*Z.dot(d)).normalized()
    width=d.cross(padnormal).normalized()
    ids=[]
    for v in ge.data.vertices:
        p=ge.matrix_world@v.co;rel=p-h;a=rel.dot(d)/L
        if .3<a<.75 and abs(rel.dot(width))<.004 and rel.dot(padnormal)>.002 and rel.length<.036:
            n=(ge.matrix_world.to_3x3().inverted().transposed()@v.normal).normalized()
            if n.dot(padnormal)>.6:ids.append(v.index)
    patches[str(digit)]={'indices':ids,'selection':'distal phalanx palmar pad, longitudinal30-75%, width+-4mm, open normal dot >0.6','bone':pb.name,'sample_count':len(ids)}
assert all(len(p['indices'])>=3 for p in patches.values())
s['BW2_contact_patches_open']=json.dumps(patches)
s['BW2_patch_eval_level']=1;s['BW2_patch_eval_count']=len(ge.data.vertices)
raw=(Fi@(re.matrix_world@re.pose.bones['finger2-1.R'].head))-(Fi@(re.matrix_world@re.pose.bones['finger5-1.R'].head))
axis=Vector((raw.x,raw.y,0)).normalized();perp=Vector((-axis.y,axis.x,0))
center=Vector((0,.096,0));radius=.014;span=.109
cz=0
for v in ge.data.vertices:
    q=Fi@(ge.matrix_world@v.co);delta=q-center;ax=delta.dot(axis);side=delta.dot(perp)
    if abs(ax)<span*.5 and abs(side)<radius:
        candidate=q.z+math.sqrt(max(0,radius*radius-side*side))
        if candidate>cz:cz=candidate
center.z=cz+.0005
holder=bpy.data.objects.new('BW2_FixedHandFrame_R',None);bpy.data.collections['BW2_CONTACT_STUDY'].objects.link(holder)
holder.empty_display_type='ARROWS';holder.empty_display_size=.03
holder.parent=r;holder.parent_type='BONE';holder.parent_bone='wrist.R'
P=r.matrix_world@r.pose.bones['wrist.R'].matrix@Matrix.Translation((0,r.data.bones['wrist.R'].length,0))
holder.matrix_parent_inverse=P.inverted();holder.matrix_basis=F
bpy.context.view_layer.update()
bpy.ops.mesh.primitive_cylinder_add(vertices=96,radius=radius,depth=span)
handle=bpy.context.object;handle.name='BW2_Locked_Handle_28mm'
for c in list(handle.users_collection):c.objects.unlink(handle)
bpy.data.collections['BW2_CONTACT_STUDY'].objects.link(handle)
handle.parent=holder;handle.matrix_parent_inverse=Matrix.Identity(4)
handle.location=center;handle.rotation_euler=axis.to_track_quat('Z','Y').to_euler()
ma=bpy.data.materials.new('BW2_handle_diagnostic_grey');ma.diffuse_color=(.23,.23,.23,1);ma.use_nodes=True;ma.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.23,.23,.23,1);handle.data.materials.append(ma)
for p in handle.data.polygons:p.use_smooth=len(p.vertices)==4
for o in bpy.data.collections['BW2_CONTACT_STUDY'].objects:
    if o.name.startswith(('BW2_axis_','BW2_tip_','BW2_label_','BW2_PALM_')):o.hide_render=True;o.hide_set(True)
bpy.context.view_layer.update()
record={'calibration_pose':'OPEN at frame1, no action','frame_world':[list(x) for x in F],'frame_relative_to_wrist':json.loads(s['BW2_hand_frame_in_posebone']),'handle_center_hand_m':list(center),'handle_axis_hand':list(axis),'radius_m':radius,'endpoint_span_m':span,'cap_margin_m':.002,'usable_length_m':.105,'fitting_rule':'one open-palm tangent placement: max exposed surface plus14mm circular section and0.5mm clearance, transverse along MCP row; locked before curl','holder_world_error':max(abs(holder.matrix_world[i][j]-F[i][j]) for i in range(4) for j in range(4)),'patches':patches}
s['BW2_hand_contract']=json.dumps(record)
for nm in ['palm','side','oblique']:
    s.camera=bpy.data.objects['BW2_cam_'+nm];s.render.filepath='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW2/r001/captures/locked_handle_open_'+nm+'.png';bpy.ops.render.render(write_still=True)
s.camera=bpy.data.objects['BW2_cam_oblique']
bpy.ops.wm.save_as_mainfile(filepath='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW2/r001/ada_bw2_grip_work.blend')
bpy.ops.wm.save_as_mainfile(filepath='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW2/r001/bw2_calibrated_open_handle.blend',copy=True)
print(json.dumps(record))


import bpy,math,json
s=bpy.data.scenes['BW1_BODY_COSTUME'];rig=bpy.data.objects['BW1_Temporary_Pose_Rig']
assert not rig.animation_data or not rig.animation_data.action
s.frame_start=1;s.frame_end=169;s.render.fps=24
arm=json.loads(s['BW1_arm_pose_spec']);leg=json.loads(s['BW1_leg_pose_spec'])
keys=[(1,'A_pose',{}),(13,'ankle_flex',leg['ankle_dorsiflex']),(25,'foot_roll',leg['foot_roll']),(37,'A_pose',{}),(49,'range_step',leg['move_range_step']),(61,'A_pose',{}),(73,'elbow',arm['elbow_bend']),(85,'shoulder',arm['shoulder_raise']),(97,'wrist',arm['wrist_bend']),(109,'A_pose',{}),(121,'knee',leg['bent_knee']),(133,'A_pose',{}),(145,'grounded_kneel',leg['kneel']),(157,'grounded_kneel',leg['kneel']),(169,'A_pose',{})]
for frame,label,pose in keys:
    s.frame_set(frame)
    for p in rig.pose.bones:p.rotation_mode='XYZ';p.rotation_euler=(0,0,0);p.location=(0,0,0)
    for bone,angles in pose.items():
        if bone in rig.pose.bones:rig.pose.bones[bone].rotation_euler=[math.radians(a) for a in angles]
    if label=='grounded_kneel':
        from mathutils import Vector
        p=rig.pose.bones['root'];basis=rig.matrix_world.to_3x3()@p.bone.matrix_local.to_3x3();p.location=basis.inverted()@Vector((0,0,s['BW1_kneel_root_world_offset_z']))
    for p in rig.pose.bones:
        p.keyframe_insert('rotation_euler',frame=frame,group=p.name)
        if p.name=='root':p.keyframe_insert('location',frame=frame,group=p.name)
    marker=s.timeline_markers.new('BW1_'+label,frame=frame)
rig.animation_data.action.name='BW1_DIAGNOSTIC_RANGE_ART_REVISE';rig.animation_data.action.use_fake_user=True
s['BW1_motion_scope']='7.04-second range diagnostic. Not retargeted game Move, not approved animation; static hands show unresolved contact.'
s.frame_set(1);s.camera=bpy.data.objects['BW1_Camera_three_quarter']
for area in bpy.context.screen.areas:
    if area.type=='VIEW_3D':
        area.spaces.active.region_3d.view_perspective='CAMERA'
        area.spaces.active.overlay.show_overlays=False
# Workbench provides a reproducible fast clay motion capture.
s.render.engine='BLENDER_WORKBENCH'
s.display.shading.light='STUDIO';s.display.shading.studiolight_rotate_z=.4
s.display.shading.color_type='SINGLE';s.display.shading.single_color=(.55,.55,.55)
s.display.shading.show_shadows=True;s.display.shading.show_cavity=True
s.display.shading.cavity_type='BOTH';s.display.shading.background_type='WORLD'
s.render.resolution_x=680;s.render.resolution_y=880;s.render.resolution_percentage=100
s.render.image_settings.file_format='FFMPEG';s.render.ffmpeg.format='MPEG4';s.render.ffmpeg.codec='H264';s.render.ffmpeg.constant_rate_factor='MEDIUM'
s.render.filepath='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW1/r001/captures/BW1_motion_diagnostic_ART_REVISE.mp4'
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print(json.dumps({'action':rig.animation_data.action.name,'frames':s.frame_end,'fps':s.render.fps,'engine':s.render.engine}))

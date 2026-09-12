import bpy,json,math
from mathutils import Vector,Matrix
s=bpy.context.scene
r=bpy.data.objects['BW1_Temporary_Pose_Rig']
holder=bpy.data.objects['BW2_FixedHandFrame_R']
assert r.animation_data.action is None
pose=json.loads(s['BW2_retained_grip_pose'])
armnames=['wrist.R','lowerarm01.R','upperarm01.R']
owned=list(pose)+armnames
action=bpy.data.actions.new('BW2_RIGHT_GRIP_CARRY_DIAGNOSTIC')
r.animation_data.action=action
action.use_fake_user=True
keys=[
(1,0,{}),(25,1,{}),(37,1,{}),
(49,1,{'wrist.R':[20,0,0]}),
(61,1,{'wrist.R':[0,20,0]}),
(73,1,{}),(85,1,{'lowerarm01.R':[75,0,0]}),
(97,1,{'upperarm01.R':[20,0,-35],'lowerarm01.R':[55,0,0]}),
(109,1,{'upperarm01.R':[20,0,-35],'lowerarm01.R':[55,0,0]}),
(121,1,{'upperarm01.R':[-15,0,-15],'lowerarm01.R':[75,0,0],'wrist.R':[-10,0,0]}),
(133,1,{}),(145,1,{})]
for frame,fraction,arm in keys:
    s.frame_set(frame)
    for nm in owned:
        b=r.pose.bones[nm];b.rotation_mode='XYZ'
        b.rotation_euler=tuple(v*fraction for v in pose[nm]) if nm in pose else tuple(math.radians(v) for v in arm.get(nm,[0,0,0]))
        b.keyframe_insert(data_path='rotation_euler',frame=frame,group=nm)
for layer in action.layers:
    for strip in layer.strips:
        for bag in strip.channelbags:
            for curve in bag.fcurves:
                for k in curve.keyframe_points:k.interpolation='LINEAR'
s.frame_start=1;s.frame_end=145;s.render.fps=24;s.render.fps_base=1
s.frame_set(37);bpy.context.view_layer.update()
coll=bpy.data.collections['BW2_CONTACT_STUDY']
base=bpy.data.objects['BW2_cam_oblique']
cam=base.copy();cam.data=base.data.copy();cam.name='BW2_cam_carry_close';coll.objects.link(cam)
offset=cam.location-holder.matrix_world.translation
for frame in range(1,146):
    s.frame_set(frame);bpy.context.view_layer.update()
    cam.location=holder.matrix_world.translation+offset
    cam.keyframe_insert(data_path='location',frame=frame)
s['BW2_carry_spec']=json.dumps({'action':action.name,'keys':keys,'held_frames':[25,145],'fps':24,'frame_count':145,'camera_policy':'fixed rotation with translation-only tracking of wrist holder','scope':'AUTHORING diagnostic wrist rotation, elbow bend, arm raise and guard sweep; not retargeted game Move/Attack','old_action_preserved':'BW1_DIAGNOSTIC_RANGE_ART_REVISE'})
s.frame_set(37);s.camera=base;bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW2/r001/ada_bw2_grip_work.blend')
bpy.ops.wm.save_as_mainfile(filepath='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW2/r001/grip_carry_diagnostic_input.blend',copy=True)
print(json.dumps({'action':action.name,'frames':145,'held_frames':[25,145],'source':bpy.data.filepath}))


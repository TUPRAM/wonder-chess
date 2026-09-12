import bpy,math,json
from mathutils import Vector
s=bpy.data.scenes['BW1_BODY_COSTUME'];rig=bpy.data.objects['BW1_Temporary_Pose_Rig']
relaxed=json.loads("{\"finger1-1.R\":[0.05,0,0],\"finger1-2.R\":[0.12,0,0],\"finger1-3.R\":[0.08,0,0],\"finger2-1.R\":[0.12,0,0],\"finger2-2.R\":[0.25,0,0],\"finger2-3.R\":[0.15,0,0],\"finger3-1.R\":[0.12,0,0],\"finger3-2.R\":[0.25,0,0],\"finger3-3.R\":[0.15,0,0],\"finger4-1.R\":[0.12,0,0],\"finger4-2.R\":[0.25,0,0],\"finger4-3.R\":[0.15,0,0],\"finger5-1.R\":[0.12,0,0],\"finger5-2.R\":[0.25,0,0],\"finger5-3.R\":[0.15,0,0],\"finger1-1.L\":[0.05,0,0],\"finger1-2.L\":[0.12,0,0],\"finger1-3.L\":[0.08,0,0],\"finger2-1.L\":[0.12,0,0],\"finger2-2.L\":[0.25,0,0],\"finger2-3.L\":[0.15,0,0],\"finger3-1.L\":[0.12,0,0],\"finger3-2.L\":[0.25,0,0],\"finger3-3.L\":[0.15,0,0],\"finger4-1.L\":[0.12,0,0],\"finger4-2.L\":[0.25,0,0],\"finger4-3.L\":[0.15,0,0],\"finger5-1.L\":[0.12,0,0],\"finger5-2.L\":[0.25,0,0],\"finger5-3.L\":[0.15,0,0]}")
poses={'open':{},'relaxed':{},'elbow_bend':{'lowerarm01.R':[75,0,0]},'shoulder_raise':{'upperarm01.R':[20,0,-35],'lowerarm01.R':[55,0,0]},'wrist_bend':{'lowerarm01.R':[50,0,0],'wrist.R':[20,0,0]}}
s['BW1_arm_pose_spec']=json.dumps(poses)
s.camera=bpy.data.objects['BW1_Camera_arm_proof'];s.render.resolution_x=1000;s.render.resolution_y=900
for name,vals in poses.items():
    for p in rig.pose.bones:p.rotation_mode='XYZ';p.rotation_euler=(0,0,0);p.location=(0,0,0)
    if name!='open':
        for bone,angles in relaxed.items():rig.pose.bones[bone].rotation_euler=angles
    for bone,angles in vals.items():rig.pose.bones[bone].rotation_euler=[math.radians(a) for a in angles]
    bpy.context.view_layer.update()
    s.render.filepath='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW1/r001/captures/arm_pose_'+name+'.png';bpy.ops.render.render(write_still=True)
for p in rig.pose.bones:p.rotation_euler=(0,0,0);p.location=(0,0,0)
# Ground the deep-knee probe from the actual left sole; do not assume FK keeps ground contact.
kneel=json.loads(s['BW1_leg_pose_spec'])['kneel']
for bone,angles in kneel.items():rig.pose.bones[bone].rotation_euler=[math.radians(a) for a in angles]
bpy.context.view_layer.update()
sole=bpy.data.objects['BW1_BootSole_L_Blockout'];ev=sole.evaluated_get(bpy.context.evaluated_depsgraph_get());low=min((ev.matrix_world@v.co).z for v in ev.data.vertices)
rootpb=rig.pose.bones['root'];frame=rig.matrix_world.to_3x3()@rootpb.bone.matrix_local.to_3x3()
rootpb.location=frame.inverted()@Vector((0,0,-.027-low));bpy.context.view_layer.update()
s['BW1_kneel_root_world_offset_z']=-.027-low
s.camera=bpy.data.objects['BW1_Camera_three_quarter'];s.render.resolution_x=850;s.render.resolution_y=1100;s.render.filepath='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW1/r001/captures/leg_kneel_grounded.png';bpy.ops.render.render(write_still=True)
print(json.dumps({'kneel_left_sole_ground_offset_z':-.027-low,'scope':'Diagnostic grounded kneel; cloth/armor failures visible'}))
for p in rig.pose.bones:p.rotation_euler=(0,0,0);p.location=(0,0,0)
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)

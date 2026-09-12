import bpy, math, json
from mathutils import Vector
s=bpy.data.scenes['BW1_BODY_COSTUME'];rig=bpy.data.objects['BW1_Temporary_Pose_Rig']
poses={
'planted':{},
'ankle_dorsiflex':{'foot.R':[-20,0,0]},
'foot_roll':{'foot.R':[25,0,0],'toe1-1.R':[-18,0,0]},
'bent_knee':{'upperleg01.R':[-35,0,0],'lowerleg01.R':[75,0,0],'foot.R':[-25,0,0]},
'kneel':{'upperleg01.R':[15,0,0],'lowerleg01.R':[120,0,0],'foot.R':[-30,0,0],'upperleg01.L':[-80,0,0],'lowerleg01.L':[95,0,0],'foot.L':[-15,0,0]},
'move_range_step':{'upperleg01.R':[-22,0,0],'lowerleg01.R':[19,0,0],'foot.R':[-19,0,0],'upperleg01.L':[22,0,0],'foot.L':[-22,0,0]}}
s['BW1_leg_pose_spec']=json.dumps(poses)
s.render.resolution_x=900;s.render.resolution_y=900
for name,vals in poses.items():
    for p in rig.pose.bones:p.rotation_mode='XYZ';p.rotation_euler=(0,0,0);p.location=(0,0,0)
    for bone,angles in vals.items():
        if bone in rig.pose.bones:rig.pose.bones[bone].rotation_euler=[math.radians(a) for a in angles]
    bpy.context.view_layer.update()
    s.camera=bpy.data.objects['BW1_Camera_leg_proof'] if name in ['planted','ankle_dorsiflex','foot_roll'] else bpy.data.objects['BW1_Camera_three_quarter']
    s.render.filepath='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW1/r001/captures/leg_pose_'+name+'.png'
    bpy.ops.render.render(write_still=True)
for p in rig.pose.bones:p.rotation_euler=(0,0,0);p.location=(0,0,0)
bpy.context.view_layer.update()
s.camera=bpy.data.objects['BW1_Camera_three_quarter'];s.render.resolution_x=850;s.render.resolution_y=1100
print(json.dumps({'executed_leg_poses':list(poses),'interpretation':'Range probes; kneel ungrounded diagnostic, not approved motion','existing_toe_bones':[p.name for p in rig.pose.bones if 'toe' in p.name]}))

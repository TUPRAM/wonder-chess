import bpy,json,math
from mathutils import Matrix
s=bpy.context.scene
assert s.name=='BW3_COLLISION_FIRST'
r=bpy.data.objects['BW3_Derived_Rig']
assert r.data!=bpy.data.objects['BW1_Temporary_Pose_Rig'].data
r.animation_data.action.use_fake_user=True
r.animation_data.action=None
for p in r.pose.bones:
    p.rotation_mode='XYZ';p.rotation_euler=(0,0,0);p.location=(0,0,0);p.scale=(1,1,1)
# Actual rig probes identified CMC -Z as clearance and +X as the transverse/palmar sweep.
# Distribute flexion to MCP/IP X; no distal Y/Z twist, scaling, or fixture change.
keys=[(1,[(0,0,0),(0,0,0),(0,0,0)]),(7,[(0,0,-10),(0,0,0),(0,0,0)]),(15,[(25,0,-10),(0,0,0),(0,0,0)]),(25,[(35,0,-5),(35,0,0),(35,0,0)]),(145,[(35,0,-5),(35,0,0),(35,0,0)])]
for f,angles in keys:
    for j,ang in enumerate(angles,1):
        p=r.pose.bones['finger1-'+str(j)+'.R']
        p.rotation_euler=[math.radians(v) for v in ang]
        p.keyframe_insert(data_path='rotation_euler',frame=f,group='BW3_thumb_route')
a=r.animation_data.action;a.name='BW3_A_ExternalThumb_Initial';a.use_fake_user=True
for layer in a.layers:
    for strip in layer.strips:
        for bag in strip.channelbags:
            for fc in bag.fcurves:
                for k in fc.keyframe_points:k.interpolation='LINEAR'
s['BW3_method_status']='INITIAL_CONSTRUCTION'
s['BW3_method']='Staged external thumb trajectory and proximal/distal flexion distribution; candidate pose controls only'
s['BW3_iteration']=0
s['BW3_thumb_keys_degrees']=json.dumps(keys)
s['BW3_method_hypothesis']='BW2 thumb tunnels through the cylinder before web crossing even with other digits OPEN; remove inward route and distal twist before contact fitting.'
s.frame_set(25);bpy.context.view_layer.update()
s.camera=bpy.data.objects['BW3_cam_oblique']
bpy.ops.wm.save_as_mainfile(filepath='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW3/r001/ada_bw3_grip_work.blend')
bpy.ops.wm.save_as_mainfile(filepath='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW3/r001/thumb_route_A_initial.blend',copy=True)
s.render.filepath='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW3/r001/captures/A_thumb_f25_oblique.png'
bpy.ops.render.render(write_still=True)
print('INITIAL external thumb construction saved and rendered; other fingers OPEN; no contact or acceptance claim.')


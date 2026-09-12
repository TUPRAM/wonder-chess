import bpy,json,math
s=bpy.context.scene;r=bpy.data.objects['BW3_Derived_Rig']
assert r.animation_data.action.name=='BW3_A_ExternalThumb_Initial'
r.animation_data.action.use_fake_user=True;r.animation_data.action=None
for p in r.pose.bones:
    p.rotation_euler=(0,0,0)
# Correction 1: keep the CMC clearance throughout the sweep.
# A's release from -10 to -5 Z brought distal surface into the cylinder while pads looked close.
keys=[(1,[(0,0,0),(0,0,0),(0,0,0)]),(7,[(0,0,-20),(0,0,0),(0,0,0)]),(15,[(25,0,-20),(0,0,0),(0,0,0)]),(25,[(35,0,-20),(35,0,0),(35,0,0)]),(145,[(35,0,-20),(35,0,0),(35,0,0)])]
for f,angles in keys:
    for j,ang in enumerate(angles,1):
        p=r.pose.bones['finger1-'+str(j)+'.R'];p.rotation_euler=[math.radians(v) for v in ang];p.keyframe_insert(data_path='rotation_euler',frame=f,group='BW3_thumb_route')
a=r.animation_data.action;a.name='BW3_B_ExternalThumb_Clearance';a.use_fake_user=True
for layer in a.layers:
    for strip in layer.strips:
        for bag in strip.channelbags:
            for fc in bag.fcurves:
                for k in fc.keyframe_points:k.interpolation='LINEAR'
s['BW3_method_status']='CORRECTION_1';s['BW3_iteration']=1;s['BW3_thumb_keys_degrees']=json.dumps(keys)
s['BW3_correction_1']='Maintain CMC wristward/palmar clearance during MCP/IP flexion; A had 13.31mm sampled endpoint cylinder penetration. No change to geometry, weights, fixture, or other fingers.'
s.frame_set(25);bpy.context.view_layer.update();s.camera=bpy.data.objects['BW3_cam_oblique']
bpy.ops.wm.save_as_mainfile(filepath='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW3/r001/ada_bw3_grip_work.blend')
bpy.ops.wm.save_as_mainfile(filepath='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW3/r001/thumb_route_B_clearance.blend',copy=True)
s.render.filepath='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW3/r001/captures/B_thumb_f25_oblique.png';bpy.ops.render.render(write_still=True)
print('Correction 1 saved; explicit thumb route only; awaiting collision and visual review.')


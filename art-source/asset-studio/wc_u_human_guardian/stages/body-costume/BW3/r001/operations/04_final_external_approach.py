import bpy,json,math
s=bpy.context.scene;r=bpy.data.objects['BW3_Derived_Rig']
assert r.animation_data.action.name=='BW3_B_ExternalThumb_Clearance'
r.animation_data.action.use_fake_user=True;r.animation_data.action=None
for p in r.pose.bones:p.rotation_euler=(0,0,0)
# Correction 2 and stop: use the verified proximal +Y clearance direction and limit late flexion.
# This is an external approach study; missing contact must remain visible and measured.
keys=[(1,[(0,0,0),(0,0,0),(0,0,0)]),(7,[(0,0,-20),(0,0,0),(0,0,0)]),(15,[(25,10,-20),(0,0,0),(0,0,0)]),(25,[(30,15,-20),(20,0,0),(20,0,0)]),(145,[(30,15,-20),(20,0,0),(20,0,0)])]
for f,angles in keys:
    for j,ang in enumerate(angles,1):
        p=r.pose.bones['finger1-'+str(j)+'.R'];p.rotation_euler=[math.radians(v) for v in ang];p.keyframe_insert(data_path='rotation_euler',frame=f,group='BW3_thumb_route')
a=r.animation_data.action;a.name='BW3_C_ExternalApproach_ART_REVISE';a.use_fake_user=True
# Preserve the BW2 carrying test on the independent rig, while other digits stay explicitly OPEN.
src=bpy.data.actions['BW3_OriginalRoute_Derived'];carry=[]
for layer in src.layers:
    for strip in layer.strips:
        for bag in strip.channelbags:
            for fc in bag.fcurves:
                for nm in ['wrist.R','lowerarm01.R','upperarm01.R']:
                    if fc.data_path=='pose.bones["'+nm+'"].rotation_euler':
                        for k in fc.keyframe_points:
                            carry.append((nm,fc.array_index,float(k.co.x),float(k.co.y)))
for nm,axis,f,val in carry:
    p=r.pose.bones[nm];p.rotation_euler[axis]=val;p.keyframe_insert(data_path='rotation_euler',index=axis,frame=f,group='BW3_retained_carry')
for layer in a.layers:
    for strip in layer.strips:
        for bag in strip.channelbags:
            for fc in bag.fcurves:
                for k in fc.keyframe_points:k.interpolation='LINEAR'
s['BW3_method_status']='CORRECTION_2_LIMIT_REACHED';s['BW3_iteration']=2;s['BW3_thumb_keys_degrees']=json.dumps(keys)
s['BW3_correction_2']='Reversible CMC +Y5 probe shifted thumb tip wristward5.55mm/palmar2.43mm; use modest proximal opposition-plane change and reduce late MCP/IP flexion. Dorsal thumb was first entering surface in B. No distal twist. Contact not forced.'
s['BW3_candidate_scope']='Thumb external-approach study and retained wrist/arm carrying motion, with digits2-5 OPEN. NOT a closed grip.'
s['BW3_carry_keys_copied']=len(carry)
s['BW3_human_approval']='NOT_ISSUED'
s.frame_set(25);bpy.context.view_layer.update();s.camera=bpy.data.objects['BW3_cam_oblique']
bpy.ops.wm.save_as_mainfile(filepath='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW3/r001/ada_bw3_grip_work.blend')
bpy.ops.wm.save_as_mainfile(filepath='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW3/r001/thumb_route_C_final_method_input.blend',copy=True)
s.render.filepath='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW3/r001/captures/C_thumb_f25_oblique.png';bpy.ops.render.render(write_still=True)
print('Final authorized method correction saved. Thumb route only; all other digits remain OPEN; copied carry keys',len(carry))


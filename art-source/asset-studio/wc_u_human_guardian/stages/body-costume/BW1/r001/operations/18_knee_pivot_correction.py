import bpy,math,json
s=bpy.data.scenes['BW1_BODY_COSTUME'];s.frame_set(1);rig=bpy.data.objects['BW1_Temporary_Pose_Rig']
cup=bpy.data.objects['BW1_KneeCup_R_ThighAttachment'];world=cup.matrix_world.copy()
pivot=bpy.data.objects.new('BW1_KneeCup_R_PosePivot',None);bpy.data.collections['BW1_RIG'].objects.link(pivot);pivot.empty_display_size=.025
con=pivot.constraints.new('COPY_LOCATION');con.name='Knee joint location';con.target=rig;con.subtarget='lowerleg01.R';con.head_tail=0
con=pivot.constraints.new('COPY_ROTATION');con.name='Shin orientation';con.target=rig;con.subtarget='lowerleg01.R'
con=pivot.constraints.new('COPY_ROTATION');con.name='Half thigh orientation';con.target=rig;con.subtarget='upperleg02.R';con.influence=.5
bpy.context.view_layer.update()
cup.parent=pivot;cup.parent_type='OBJECT';cup.matrix_world=world
for p in cup.data.polygons:p.use_smooth=True
cup['attachment_policy']='Temporary rigid cup pivot at knee with equal thigh/shin rotation interpolation. Authoring constraint requires explicit bake/runtime decision.'
pivot['status']='LOCAL_AUTHORING_ONLY_NO_CANONICAL_SKELETON_CHANGE'
s.camera=bpy.data.objects['BW1_Camera_leg_proof'];s.render.resolution_x=900;s.render.resolution_y=900
for frame,name in [(1,'stance'),(121,'bend')]:
 s.frame_set(frame);s.render.filepath='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW1/r001/captures/knee_pivot_'+name+'.png';bpy.ops.render.render(write_still=True)
s.frame_set(145);s.camera=bpy.data.objects['BW1_Camera_three_quarter'];s.render.resolution_x=850;s.render.resolution_y=1100;s.render.filepath='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW1/r001/captures/knee_pivot_kneel.png';bpy.ops.render.render(write_still=True)
s.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath);print('Knee cup corrective attempt1: rigid blended pivot tested at rest, bend and kneel')

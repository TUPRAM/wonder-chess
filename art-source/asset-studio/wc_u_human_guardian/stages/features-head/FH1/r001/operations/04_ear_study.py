assert bpy.data.scenes.get('FH1_EAR_STUDY') is None
scene,col=fh_scene('FH1_EAR_STUDY',(.089,-.016,1.674),.082)
data=build_ear();data['design_notes']='; '.join(data['design_notes'])
ear=fh_mesh('FH1_Ear_R_Control_Cage',data,col)
ear.modifiers[0].levels=1;ear.modifiers[0].render_levels=1
target=Vector((.089,-.016,1.674))
for label,offset in [('front',(.50,0,0)),('profile',(.05,.50,0)),('three_quarter',(.45,.24,.025)),('underside',(.36,-.32,.03))]:
    cam=bpy.data.objects[scene.name+'_'+label];cam.location=target+Vector(offset)
    cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
key=bpy.data.objects[scene.name+'_Key'];key.location=target+Vector((.30,.23,.24));key.rotation_euler=(target-key.location).to_track_quat('-Z','Y').to_euler()
fill=bpy.data.objects[scene.name+'_Fill'];fill.location=target+Vector((.24,-.26,.03));fill.rotation_euler=(target-fill.location).to_track_quat('-Z','Y').to_euler()
scene.camera=bpy.data.objects[scene.name+'_three_quarter']
bpy.context.view_layer.objects.active=ear;ear.select_set(True)
for a in bpy.context.screen.areas:
    if a.type=='VIEW_3D':a.spaces.active.region_3d.view_rotation=scene.camera.rotation_euler.to_quaternion()
scene['render_allowlist']=json.dumps([o.name for o in col.objects]);scene['status']='Original ear study, inferred hidden anatomy; no human approval'
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
for label in ['front','profile','three_quarter','underside']:
    scene.camera=bpy.data.objects[scene.name+'_'+label];scene.render.filepath=ROOT+'/captures/ear_initial_'+label+'.png'
    bpy.ops.render.render(write_still=True)
print('EAR_AUDIT '+json.dumps(audit_ear()))

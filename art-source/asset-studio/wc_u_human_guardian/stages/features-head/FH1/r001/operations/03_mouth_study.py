assert bpy.data.scenes.get('FH1_MOUTH_STUDY') is None
scene,col=fh_scene('FH1_MOUTH_STUDY',(0,.059,1.618),.092)
mouth=fh_mesh('FH1_Mouth_Control_Cage',build_mouth(),col)
bpy.context.view_layer.objects.active=mouth;mouth.select_set(True)
scene['render_allowlist']=json.dumps([o.name for o in col.objects])
scene['status']='Isolated original mouth with perioral cage; not human-approved'
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
for label in ['front','profile','three_quarter']:
    scene.camera=bpy.data.objects[scene.name+'_'+label];scene.render.filepath=ROOT+'/captures/mouth_initial_'+label+'.png'
    bpy.ops.render.render(write_still=True)
print('FH1_MOUTH_CREATED '+json.dumps({'vertices':len(mouth.data.vertices),'faces':len(mouth.data.polygons),'interface':len(build_mouth()['root_loop'])}))

scene=bpy.data.scenes['FH1_EAR_STUDY'];bpy.context.window.scene=scene
assert bpy.data.objects.get('FH1_Ear_R_Control_Cage_r002') is None
old=bpy.data.objects['FH1_Ear_R_Control_Cage'];old.hide_render=True;old.hide_set(True)
data=build_ear();data['design_notes']='; '.join(data['design_notes'])
ear=fh_mesh('FH1_Ear_R_Control_Cage_r002',data,scene.collection)
ear.modifiers[0].levels=1;ear.modifiers[0].render_levels=1
scene['render_allowlist']=json.dumps([o.name for o in scene.objects if not o.hide_render])
bpy.context.view_layer.objects.active=ear;ear.select_set(True)
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
for label in ['front','profile','three_quarter','underside']:
    scene.camera=bpy.data.objects[scene.name+'_'+label];scene.render.filepath=ROOT+'/captures/ear_r002_'+label+'.png';bpy.ops.render.render(write_still=True)
print('Ear correction pass 1 executed from original sparse cage; root exactly preserved.')

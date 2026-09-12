import bpy,json
root='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/method-recovery/MR1/r001'
sc=bpy.data.scenes['MR1_CONTEXT_HEAD_CANDIDATE'];bpy.context.window.scene=sc
bc=bpy.data.collections.new('MR1_CONTEXT_BASELINE_ALLOWLIST');base=bpy.data.scenes.new('MR1_CONTEXT_BASELINE_REVIEW');base.collection.children.link(bc)
names=[o.name for o in bpy.data.scenes['Scene'].objects if o.type=='MESH' and not o.hide_render]
for n in names:
    src=bpy.data.objects[n];o=src.copy();o.data=src.data.copy();o.name='MR1_CONTEXT_BASE_'+n;bc.objects.link(o);o.hide_render=False;o.hide_viewport=False;o.show_wire=False
for o in sc.objects:
    if o.type in {'CAMERA','LIGHT'}:bc.objects.link(o)
base.world=sc.world;base.render.engine='CYCLES';base.cycles.samples=16;base.cycles.use_denoising=True
base.render.resolution_x=1000;base.render.resolution_y=1000;base.render.resolution_percentage=100;base.render.image_settings.file_format='PNG';base.render.film_transparent=False
base.view_settings.view_transform='Standard';base.view_settings.look='None';base.view_settings.exposure=0;base.view_settings.gamma=1
base.view_layers[0].material_override=bpy.data.materials['MR1_Uniform_Clay'];base['mr1_render_allowlist']=json.dumps([o.name for o in base.objects if not o.hide_render])
for v in ['front','profile','three_quarter','opposite','rear','top']:
    bpy.context.window.scene=base;base.camera=bpy.data.objects['MR1_CONTEXT_'+v];base.render.filepath=root+'/captures/context_baseline_clay_'+v+'.png';bpy.ops.render.render(write_still=True)
bpy.context.window.scene=sc;sc.camera=bpy.data.objects['MR1_CONTEXT_three_quarter'];sc['mr1_status']='REVISE_CONTEXTUAL_INTEGRATION'
sc['mr1_local_face_method']='METHOD_PROOF_ACCEPTED';sc['mr1_local_hair_method']='METHOD_PROOF_ACCEPTED';sc['mr1_human_forms_approval']=False
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print(json.dumps({'baseline_visible_source_meshes':len(names),'all_original_hidden_experiments_excluded':True,'source_names':names}))

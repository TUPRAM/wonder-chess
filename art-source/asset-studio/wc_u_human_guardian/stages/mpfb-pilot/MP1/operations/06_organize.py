import bpy,json
s=bpy.context.scene;source=bpy.data.objects['MP1_MpfbFoundation_Source'];head=bpy.data.objects['MP1_Head_r002']
archive=bpy.data.scenes.new('MP1_ARCHIVED_TRIALS');auth=bpy.data.scenes.new('MP1_SOURCE_CONTROLS')
for ob in [bpy.data.objects['MP1_Head_r000'],bpy.data.objects['MP1_Head_r001']]:
    archive.collection.objects.link(ob)
    for coll in list(ob.users_collection):
        if coll!=archive.collection:coll.objects.unlink(ob)
auth.collection.objects.link(source)
for coll in list(source.users_collection):
    if coll!=auth.collection:coll.objects.unlink(source)
for ob in s.objects:
    if ob.type in {'CAMERA','LIGHT'}:ob.hide_set(True)
head['source_object']='MP1_MpfbFoundation_Source';head['source_method']='MPFB CC0 phenotype + native feature targets; derived editable head cage';head['approval']='ART_REVISE';head['model_version']='MP1 r002'
for coll in list(s.collection.children):
    if coll.name=='HP1_HEAD_POLISH_ALLOWLIST':coll.name='MP1_SAVED_CAMERAS_LIGHTS'
viewcoll=bpy.data.collections.new('MP1_HEAD_RENDER_ALLOWLIST');s.collection.children.link(viewcoll)
for ob in [head,bpy.data.objects['MP1_Eye_R'],bpy.data.objects['MP1_Eye_L']]:
    for coll in list(ob.users_collection):coll.objects.unlink(ob)
    viewcoll.objects.link(ob)
for ob in s.objects:ob.select_set(False)
head.select_set(True);bpy.context.view_layer.objects.active=head;s.camera=bpy.data.objects['HP1_HEAD_POLISH_three_quarter'];s.cycles.samples=48
print(json.dumps({'active_scene':s.name,'render_meshes':[o.name for o in s.objects if o.type=='MESH' and not o.hide_render],'source_vertices':len(source.data.vertices),'source_keys':len(source.data.shape_keys.key_blocks),'source_only_scene':auth.name},indent=2))
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)

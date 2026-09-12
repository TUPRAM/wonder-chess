import bpy,json
assert bpy.data.filepath.replace('\\','/').endswith('/mpfb-pilot/MP1/ada_mpfb_work.blend')
old=bpy.data.scenes['HP1_HEAD_POLISH']; s=old.copy(); s.name='MP1_ADA_HEAD'; bpy.context.window.scene=s
keep={o.name for o in old.objects if o.type in {'CAMERA','LIGHT'}}
for scene in list(bpy.data.scenes):
    if scene!=s: bpy.data.scenes.remove(scene)
for o in list(bpy.data.objects):
    if o.name not in keep: bpy.data.objects.remove(o,do_unlink=True)
for m in list(bpy.data.meshes):
    if m.users==0: bpy.data.meshes.remove(m)
for c in list(bpy.data.collections):
    if len(c.all_objects)==0: bpy.data.collections.remove(c)
s['mpfb_trial']='Fresh licensed MPFB foundation; no prior Ada geometry retained. Human approval pending.'
s.camera=bpy.data.objects['HP1_HEAD_POLISH_three_quarter']; s.cycles.samples=32; s.render.resolution_x=900; s.render.resolution_y=900
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print(json.dumps({'scene':s.name,'objects':list(s.objects.keys()),'mesh_datablocks':len(bpy.data.meshes),'install_operator':[(p.identifier,p.type) for p in bpy.ops.extensions.package_install_files.get_rna_type().properties]},indent=2))

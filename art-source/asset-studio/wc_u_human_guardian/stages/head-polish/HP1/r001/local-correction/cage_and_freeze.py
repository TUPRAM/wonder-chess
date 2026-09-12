import bpy,json
ROOT='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/head-polish/HP1/r001'
s=bpy.data.scenes['HP1_HEAD_POLISH'];h=bpy.data.objects['HP1_HEAD_POLISH_Head_r016']
assert bpy.data.scenes.get('HP1_LOCAL_CAGE_REVIEW') is None
assert bpy.data.filepath.replace('\\','/')==ROOT+'/ada_head_polish_work.blend'
cs=bpy.data.scenes.new('HP1_LOCAL_CAGE_REVIEW');cs.world=s.world;cs.render.engine='CYCLES';cs.cycles.samples=24;cs.cycles.use_denoising=True;cs.render.resolution_x=1200;cs.render.resolution_y=1200;cs.render.resolution_percentage=100;cs.render.image_settings.file_format='PNG';cs.view_settings.view_transform='Standard';cs.view_settings.look='None'
for src in s.objects:
    if src.type in ['CAMERA','LIGHT']:
        c=src.copy();c.data=src.data.copy();c.name=cs.name+src.name.replace(s.name,'');cs.collection.objects.link(c)
body=h.copy();body.data=h.data.copy();body.name='HP1_LOCAL_CAGE_REVIEW_Base_r016';cs.collection.objects.link(body)
for mod in body.modifiers:mod.show_render=False;mod.show_viewport=False
for p in body.data.polygons:p.use_smooth=False
wire=body.copy();wire.data=body.data.copy();wire.name='HP1_LOCAL_CAGE_REVIEW_ActualEdges_r016';cs.collection.objects.link(wire);wire.modifiers.clear()
wire.data.materials.clear();wire.data.materials.append(bpy.data.materials['HP1_Cage_Diagnostic_Ink'])
wf=wire.modifiers.new('Actual source cage edges','WIREFRAME');wf.thickness=.00016;wf.use_replace=True;wf.offset=1
cs['render_allowlist']=json.dumps([o.name for o in cs.objects]);bpy.context.window.scene=cs
for label in ['front','three_quarter']:
    cs.camera=bpy.data.objects[cs.name+'_'+label];cs.render.filepath=ROOT+'/local-correction/captures/r016_cage_'+label+'.png';bpy.ops.render.render(write_still=True)
bpy.context.window.scene=s
s['status']='HP1 local correction r016, two bounded attempts, REVISE. No mirroring or forms approval.'
s['render_allowlist']=json.dumps([o.name for o in s.objects if not o.hide_render])
s.camera=bpy.data.objects[s.name+'_primary_fit']
bpy.ops.object.select_all(action='DESELECT');h.select_set(True);bpy.context.view_layer.objects.active=h
for a in bpy.context.screen.areas:
    if a.type=='VIEW_3D':
        sp=a.spaces.active;sp.region_3d.view_rotation=s.camera.rotation_euler.to_quaternion();sp.region_3d.view_location=(0,.01,1.678);sp.region_3d.view_distance=.35;sp.region_3d.view_perspective='ORTHO'
bpy.ops.wm.save_as_mainfile(filepath=ROOT+'/ada_head_polish_work.blend')
bpy.ops.wm.save_as_mainfile(filepath=ROOT+'/ada_head_polish_checkpoint_r016.blend',copy=True)
print('LOCAL_CAGE_AND_FREEZE '+json.dumps({'work':bpy.data.filepath,'checkpoint':ROOT+'/ada_head_polish_checkpoint_r016.blend','active':h.name,'r014_unchanged_object':bpy.data.objects['HP1_HEAD_POLISH_Head_r014'].name,'hair_family_linked_to_active_scene':[o.name for o in s.objects if any(t in o.name.lower() for t in ['hair','braid','brow','lash'])]}))

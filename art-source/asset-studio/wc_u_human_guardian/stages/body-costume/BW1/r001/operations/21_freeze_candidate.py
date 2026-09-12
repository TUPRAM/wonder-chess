import bpy,json
s=bpy.data.scenes['BW1_BODY_COSTUME'];s.frame_set(1)
for scene in bpy.data.scenes:scene.use_fake_user=True
s['BW1_scope']='Independent BW1 body/costume experiment from preserved MP1 indexed source. Full game and MP1 source files protected.'
s['BW1_recipe_promotion']='NONE; independent replay and second-body fit deferred because local articulation proofs failed'
s['BW1_human_forms_approval']=False;s['BW1_candidate_status']='ART_REVISE'
s['BW1_modeling_stop']='Grip initial+2 corrections failed. Knee attachment initial+2 corrections failed; restored best thigh attachment. No propagation of local improvements.'
s.camera=bpy.data.objects['BW1_Camera_three_quarter']
s.render.engine='CYCLES';s.cycles.samples=24;s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG';s.render.resolution_x=850;s.render.resolution_y=1100
s.render.filepath='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW1/r001/captures/review_preview.png'
bpy.ops.wm.save_as_mainfile(filepath='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW1/r001/ada_body_costume_work.blend')
bpy.ops.wm.save_as_mainfile(filepath='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW1/r001/ada_body_costume_checkpoint_r001_ART_REVISE.blend',copy=True)
print(json.dumps({'file':bpy.data.filepath,'scenes':[x.name for x in bpy.data.scenes],'body_shape_keys':len(bpy.data.objects['BW1_IndexedBody'].data.shape_keys.key_blocks),'hair_family_in_active_scene':[o.name for o in s.objects if any(word in o.name.lower() for word in ['hair','brow','lash','braid'])],'mesh_allowlist':[o.name for o in s.objects if o.type=='MESH' and not o.hide_render]}))

import bpy,json
s=bpy.data.scenes['BW1_BODY_COSTUME'];s.frame_set(1)
m=bpy.data.objects['BW1_Leggings'].modifiers['Garment thickness'];assert m.type=='SOLIDIFY'
m.use_even_offset=False;m.thickness_clamp=0;m.use_thickness_angle_clamp=False
s['BW1_technical_revision']='r002: disable leggings Solidify even offset after reproducible frame129/159 miter spikes; no cage or weight edits'
s['BW1_motion_spike_fix']='2mm inward thickness retained. Even-offset correction caused extrusion spikes; exact minimal setting independently scanned all169frames.'
s.render.resolution_x=850;s.render.resolution_y=1100;s.render.engine='CYCLES';s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG'
s.camera=bpy.data.objects['BW1_Camera_three_quarter']
for frame,name in [(129,'129'),(159,'159')]:
 s.frame_set(frame);s.render.filepath='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW1/r001/captures/technical_r002_frame_'+name+'.png';bpy.ops.render.render(write_still=True)
s.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW1/r001/ada_body_costume_work.blend')
bpy.ops.wm.save_as_mainfile(filepath='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW1/r001/ada_body_costume_checkpoint_r002_ART_REVISE.blend',copy=True)
print('Technical r002 frozen; art status unchanged, old r001 and faulty motion preserved')

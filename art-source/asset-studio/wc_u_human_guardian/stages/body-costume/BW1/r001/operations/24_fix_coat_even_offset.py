import bpy
s=bpy.context.scene;s.frame_set(1)
m=bpy.data.objects['BW1_CoatUpper_Continuous'].modifiers['Padded garment thickness'];assert m.type=='SOLIDIFY';m.use_even_offset=False
s['BW1_technical_revision']='r003: leggings and coat Solidify even-offset singularities disabled after full-motion isolation; source cages/weights/action unchanged'
s['BW1_coat_temporal_fix']='6mm inward thickness retained; even-offset false reduced max adjacent-frame jump0.6588m to0.04885m over169frames in isolated test'
s.camera=bpy.data.objects['BW1_Camera_three_quarter'];s.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW1/r001/ada_body_costume_work.blend')
bpy.ops.wm.save_as_mainfile(filepath='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW1/r001/ada_body_costume_checkpoint_r003_ART_REVISE.blend',copy=True)
print('Technical r003 frozen; source geometry and action unchanged')

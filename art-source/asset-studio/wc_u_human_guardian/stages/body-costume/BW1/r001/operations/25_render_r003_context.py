import bpy,json
from mathutils import Vector
s=bpy.context.scene
original_camera=s.camera
original_path=s.render.filepath
key=bpy.data.objects["BW1_Key"]
key_location=key.location.copy()
key_rotation=key.rotation_euler.copy()
s.frame_set(1)
s.render.image_settings.file_format='PNG'
captures=[]
for suffix,camera in [('front','front'),('profile','profile'),('back','back'),('3q','three_quarter'),('other3q','other_three_quarter')]:
    s.camera=bpy.data.objects['BW1_Camera_'+camera]
    s.render.filepath='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW1/r001/captures/r003_context_'+suffix+'.png'
    bpy.ops.render.render(write_still=True)
    captures.append(s.render.filepath)
s.camera=bpy.data.objects['BW1_Camera_three_quarter']
key.location.x=-key.location.x
key.rotation_euler=(Vector((0,0,1))-key.location).to_track_quat('-Z','Y').to_euler()
s.render.filepath='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW1/r001/captures/r003_context_reversed_key.png'
bpy.ops.render.render(write_still=True)
captures.append(s.render.filepath)
key.location=key_location
key.rotation_euler=key_rotation
s.camera=original_camera
s.render.filepath=original_path
print(json.dumps({'technical_revision':'r003','captures':captures,'frame':s.frame_current,'restored_camera':s.camera.name}))


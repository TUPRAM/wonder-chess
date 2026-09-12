import bpy,json
from mathutils import Vector
ROOT='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/head-polish/HP1/r001/local-correction'
s=bpy.data.scenes['HP1_HEAD_POLISH'];bpy.context.window.scene=s
assert not bpy.data.objects['HP1_HEAD_POLISH_Head_r016'].hide_render
for label in ['front','profile','three_quarter','primary_fit']:
    s.camera=bpy.data.objects[s.name+'_'+label]
    s.render.resolution_x=840 if label=='primary_fit' else 900;s.render.resolution_y=788 if label=='primary_fit' else 900
    s.render.filepath=ROOT+'/captures/r016_'+label+'.png';bpy.ops.render.render(write_still=True)
s.render.resolution_x=900;s.render.resolution_y=900
key=bpy.data.objects[s.name+'_Key'];fill=bpy.data.objects[s.name+'_Fill'];km=key.matrix_world.copy();fm=fill.matrix_world.copy()
try:
    key.location.x=-key.location.x;fill.location.x=-fill.location.x
    target=Vector((0,-.008,1.680));key.rotation_euler=(target-key.location).to_track_quat('-Z','Y').to_euler();fill.rotation_euler=(target-fill.location).to_track_quat('-Z','Y').to_euler()
    s.camera=bpy.data.objects[s.name+'_three_quarter'];s.render.filepath=ROOT+'/captures/r016_reverse_key.png';bpy.ops.render.render(write_still=True)
finally:
    key.matrix_world=km;fill.matrix_world=fm
try:
    for side in ['R','L']:bpy.data.objects[s.name+'_Eye_'+side].hide_render=True
    s.camera=bpy.data.objects[s.name+'_front'];s.render.filepath=ROOT+'/captures/r016_openings.png';bpy.ops.render.render(write_still=True)
finally:
    for side in ['R','L']:bpy.data.objects[s.name+'_Eye_'+side].hide_render=False
s.camera=bpy.data.objects[s.name+'_primary_fit']
print('LOCAL r016 six actual captures written; baseline camera and light transforms retained.')

import bpy
from mathutils import Vector
s=bpy.context.scene;root='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/mpfb-pilot/MP1/captures/'
s.render.resolution_x=900;s.render.resolution_y=900;s.camera=bpy.data.objects['HP1_HEAD_POLISH_three_quarter'];key=bpy.data.objects['HP1_HEAD_POLISH_Key'];fill=bpy.data.objects['HP1_HEAD_POLISH_Fill'];km=key.matrix_world.copy();fm=fill.matrix_world.copy()
try:
    key.location.x=-key.location.x;fill.location.x=-fill.location.x;target=Vector((0,-.008,1.680));key.rotation_euler=(target-key.location).to_track_quat('-Z','Y').to_euler();fill.rotation_euler=(target-fill.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=root+'final_clay_reverse_key.png';bpy.ops.render.render(write_still=True)
finally:
    key.matrix_world=km;fill.matrix_world=fm
try:
    for side in ['R','L']:bpy.data.objects['MP1_Eye_'+side].hide_render=True
    s.camera=bpy.data.objects['HP1_HEAD_POLISH_front'];s.render.filepath=root+'final_openings_front.png';bpy.ops.render.render(write_still=True)
finally:
    for side in ['R','L']:bpy.data.objects['MP1_Eye_'+side].hide_render=False
for side in ['R','L']:
    e=bpy.data.objects['MP1_Eye_'+side];e.data.materials.clear();e.data.materials.append(bpy.data.materials['MP1_Diagnostic_Iris_Grayscale'])
s.camera=bpy.data.objects['HP1_HEAD_POLISH_three_quarter'];s.render.filepath=root+'final_gaze_three_quarter.png';bpy.ops.render.render(write_still=True)
s.camera=bpy.data.objects['HP1_HEAD_POLISH_primary_fit'];s.render.resolution_x=840;s.render.resolution_y=788;s.render.filepath=root+'final_gaze_primary_fit.png';bpy.ops.render.render(write_still=True)
s.camera=bpy.data.objects['HP1_HEAD_POLISH_three_quarter'];s.render.resolution_x=900;s.render.resolution_y=900

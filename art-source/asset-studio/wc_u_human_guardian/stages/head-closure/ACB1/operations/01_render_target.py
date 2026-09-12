import bpy,json
from mathutils import Vector
ROOT='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/head-closure/ACB1'
s=bpy.data.scenes['ACB1_HEAD'];bpy.context.window.scene=s
target=bpy.data.objects['ACB1_FORM_TARGET'];baseline=bpy.data.objects['ACB1_HEAD_BASELINE']
for role in ['baseline','target_initial']:
    target.hide_render=role=='baseline';baseline.hide_render=role!='baseline'
    for label in ['front','profile','three_quarter','other_three_quarter','primary_fit','underside']:
        s.camera=bpy.data.objects['ACB1_'+label];s.render.resolution_x=840 if label=='primary_fit' else 900;s.render.resolution_y=788 if label=='primary_fit' else 900
        s.render.filepath=ROOT+'/captures/'+role+'_'+label+'.png';bpy.ops.render.render(write_still=True)
    s.render.resolution_x=900;s.render.resolution_y=900
    key=bpy.data.objects['ACB1_Key'];fill=bpy.data.objects['ACB1_Fill'];km=key.matrix_world.copy();fm=fill.matrix_world.copy()
    try:
        key.location.x=-key.location.x;fill.location.x=-fill.location.x;t=Vector((0,-.008,1.680))
        key.rotation_euler=(t-key.location).to_track_quat('-Z','Y').to_euler();fill.rotation_euler=(t-fill.location).to_track_quat('-Z','Y').to_euler()
        s.camera=bpy.data.objects['ACB1_three_quarter'];s.render.filepath=ROOT+'/captures/'+role+'_reverse_key.png';bpy.ops.render.render(write_still=True)
    finally:key.matrix_world=km;fill.matrix_world=fm
    try:
        for side in ['R','L']:bpy.data.objects['ACB1_Eye_'+side].hide_render=True
        s.camera=bpy.data.objects['ACB1_front'];s.render.filepath=ROOT+'/captures/'+role+'_openings.png';bpy.ops.render.render(write_still=True)
    finally:
        for side in ['R','L']:bpy.data.objects['ACB1_Eye_'+side].hide_render=False
target.hide_render=False;baseline.hide_render=True;s.camera=bpy.data.objects['ACB1_primary_fit']
print('Rendered actual ACB1 baseline and initial sculpt target in matching saved camera/light profiles.')

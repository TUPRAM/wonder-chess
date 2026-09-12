import bpy,json
from mathutils import Matrix,Vector
s=bpy.context.scene;s.frame_set(37)
F=Matrix(json.loads(s['BW2_frame_world']));X=F.col[0].xyz;Y=F.col[1].xyz;Z=F.col[2].xyz;O=F.translation
target=O+Y*.085
view_direction=(-Z+.65*X+.15*Y).normalized()
cam=bpy.data.objects['BW2_cam_oblique'].copy();cam.data=cam.data.copy();cam.name='BW2_cam_thumb_side';bpy.data.collections['BW2_CONTACT_STUDY'].objects.link(cam)
cam.location=target+view_direction*.5
cam.rotation_euler=(-view_direction).to_track_quat('-Z','Y').to_euler()
right=Y.cross(view_direction).normalized();up=view_direction.cross(right).normalized()
cam.matrix_world=Matrix(((right.x,up.x,view_direction.x,cam.location.x),(right.y,up.y,view_direction.y,cam.location.y),(right.z,up.z,view_direction.z,cam.location.z),(0,0,0,1)))
s.camera=cam;s.render.filepath='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW2/r001/captures/integrated_thumb_side.png';bpy.ops.render.render(write_still=True)
h=bpy.data.objects['BW2_Locked_Handle_28mm'];h.hide_render=True
s.render.filepath='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW2/r001/captures/integrated_thumb_side_handle_hidden.png';bpy.ops.render.render(write_still=True)
s.camera=bpy.data.objects['BW2_cam_axial'];s.render.filepath='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW2/r001/captures/integrated_axial_handle_hidden.png';bpy.ops.render.render(write_still=True)
h.hide_render=False;s.camera=bpy.data.objects['BW2_cam_oblique']
print('Thumb and handle-hidden diagnostic rendered; handle restored')


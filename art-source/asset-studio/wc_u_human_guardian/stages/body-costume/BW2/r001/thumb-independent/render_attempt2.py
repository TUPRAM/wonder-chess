import bpy,json,math
from pathlib import Path
out=Path(__file__).parent;data=json.loads((out/'bounded_thumb_fit.json').read_text());s=bpy.context.scene;r=bpy.data.objects['BW1_Temporary_Pose_Rig'];p=data['attempts'][1]['best']['params_deg']
r.pose.bones['finger1-1.R'].rotation_euler=tuple(math.radians(v) for v in p[:3]);r.pose.bones['finger1-2.R'].rotation_euler=(math.radians(p[3]),0,0);r.pose.bones['finger1-3.R'].rotation_euler=(math.radians(p[4]),0,math.radians(p[5]));bpy.context.view_layer.update()
s.render.engine='BLENDER_WORKBENCH';s.display.shading.light='STUDIO';s.display.shading.color_type='MATERIAL';s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.display.shading.cavity_type='BOTH';s.render.resolution_x=900;s.render.resolution_y=900;s.render.resolution_percentage=100;s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG';s.render.film_transparent=False;s.view_settings.view_transform='Standard'
for view in ['palm','oblique','axial']:
    s.camera=bpy.data.objects['BW2_cam_'+view];s.render.filepath=str(out/('attempt2_'+view+'.png'));bpy.ops.render.render(write_still=True)

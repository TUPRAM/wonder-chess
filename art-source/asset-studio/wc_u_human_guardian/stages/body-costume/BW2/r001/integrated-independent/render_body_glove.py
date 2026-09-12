import bpy,json,hashlib
from pathlib import Path
out=Path(__file__).parent;source=out.parent/'grip_integrated_contact_r001.blend';s=bpy.context.scene;r=bpy.data.objects['BW1_Temporary_Pose_Rig'];glove=bpy.data.objects['BW1_Glove_Pair_SourceFit'];body=bpy.data.objects['BW1_IndexedBody'];handle=bpy.data.objects['BW2_Locked_Handle_28mm'];sha=hashlib.sha256(source.read_bytes()).hexdigest()
report={'source':str(source),'source_sha256':sha,'objects':{},'scene':s.name,'thumb_euler_radians':{f'finger1-{j}.R':list(r.pose.bones[f'finger1-{j}.R'].rotation_euler) for j in [1,2,3]}}
for ob in [body,glove]:report['objects'][ob.name]={'base_vertices':len(ob.data.vertices),'world_matrix':[list(row) for row in ob.matrix_world],'modifiers':[{'name':m.name,'type':m.type,'show_render':m.show_render,'show_viewport':m.show_viewport,'levels':getattr(m,'levels',None),'render_levels':getattr(m,'render_levels',None)} for m in ob.modifiers]}
for o in s.objects:
    if o.type=='MESH':o.hide_render=True
s.render.engine='BLENDER_WORKBENCH';s.display.shading.light='STUDIO';s.display.shading.color_type='SINGLE';s.display.shading.single_color=(.6,.6,.6);s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.display.shading.cavity_type='BOTH';s.render.resolution_x=1000;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG';s.render.film_transparent=False;s.view_settings.view_transform='Standard'
for label,ob in [('body',body),('glove',glove)]:
    body.hide_render=ob!=body;glove.hide_render=ob!=glove;handle.hide_render=True
    for view in ['palm','oblique','axial']:
        s.camera=bpy.data.objects['BW2_cam_'+view];s.render.filepath=str(out/(label+'_'+view+'.png'));bpy.ops.render.render(write_still=True)
    s.display.shading.show_cavity=False;s.camera=bpy.data.objects['BW2_cam_axial'];s.render.filepath=str(out/(label+'_axial_no_cavity.png'));bpy.ops.render.render(write_still=True);s.display.shading.show_cavity=True
report['source_sha256_after']=hashlib.sha256(source.read_bytes()).hexdigest();assert report['source_sha256_after']==sha;(out/'source_and_render_metadata.json').write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)

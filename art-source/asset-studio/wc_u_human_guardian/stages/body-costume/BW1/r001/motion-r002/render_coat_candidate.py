import bpy,json
from pathlib import Path
out=Path(__file__).parent;scene=bpy.data.scenes['BW1_BODY_COSTUME'];bpy.context.window.scene=scene
scene.camera=bpy.data.objects['BW1_Camera_three_quarter'];scene.render.engine='BLENDER_WORKBENCH'
scene.display.shading.light='STUDIO';scene.display.shading.color_type='SINGLE';scene.display.shading.single_color=(.55,.55,.55);scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True;scene.display.shading.cavity_type='BOTH';scene.display.shading.show_specular_highlight=True;scene.display.shading.background_type='WORLD';scene.world.color=(.09,.09,.09)
scene.render.resolution_x=680;scene.render.resolution_y=880;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGB';scene.render.image_settings.media_type='IMAGE';scene.render.film_transparent=False;scene.use_nodes=False
scene.view_settings.view_transform='Standard';scene.view_settings.exposure=0;scene.view_settings.gamma=1
next(m for m in bpy.data.objects['BW1_CoatUpper_Continuous'].modifiers if m.type=='SOLIDIFY').use_even_offset=False
scene.frame_set(67);bpy.context.view_layer.update()
scene.render.filepath=str(out/'frame067_coat_even_offset_false_UNSAVED.png');bpy.ops.render.render(write_still=True,scene=scene.name)
observations=[];dg=bpy.context.evaluated_depsgraph_get()
for obj in scene.objects:
    if obj.type!='MESH' or obj.hide_render:continue
    ev=obj.evaluated_get(dg);mesh=ev.to_mesh()
    extremes=[]
    for v in mesh.vertices:
        p=obj.matrix_world@v.co
        if abs(p.x)>1.4 or abs(p.y)>1.4 or p.z>2.2 or p.z<-.3:extremes.append(list(p))
    if extremes:observations.append({'object':obj.name,'extreme_vertices':len(extremes),'samples':extremes[:6]})
    ev.to_mesh_clear()
(out/'frame067_coat_even_offset_false_screen.json').write_text(json.dumps({'frame':67,'world_extent_screen':'abs(x)>1.4 or abs(y)>1.4 or z>2.2 or z<-0.3','observations':observations},indent=2))

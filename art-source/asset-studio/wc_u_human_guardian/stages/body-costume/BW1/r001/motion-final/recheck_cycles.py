import bpy,json
from pathlib import Path
out=Path(__file__).parent;scene=bpy.data.scenes['BW1_BODY_COSTUME'];bpy.context.window.scene=scene
scene.camera=bpy.data.objects['BW1_Camera_three_quarter'];scene.render.engine='CYCLES';scene.cycles.samples=8;scene.cycles.use_denoising=True
scene.render.resolution_x=680;scene.render.resolution_y=880;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.image_settings.media_type='IMAGE';scene.render.image_settings.color_mode='RGB';scene.use_nodes=False;scene.render.film_transparent=False
scene.frame_set(129);bpy.context.view_layer.update();scene.render.filepath=str(out/'frame129_cycles_8sample_recheck.png');bpy.ops.render.render(write_still=True,scene=scene.name)
report={'frame':129,'engine':'CYCLES','samples':8,'scene':scene.name,'camera':scene.camera.name,'failed_knee_objects':[{'name':o.name,'hide_render':o.hide_render,'hide_viewport':o.hide_viewport} for o in bpy.data.objects if 'KneeSurfaceAnchor' in o.name],'leggings_outlier_data':[]}
obj=bpy.data.objects['BW1_Leggings'];ev=obj.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh()
for v in mesh.vertices:
    p=obj.matrix_world@v.co
    if abs(p.x)>1.4 or abs(p.y)>1.4 or p.z>2.2 or p.z<-.3:report['leggings_outlier_data'].append({'evaluated_index':v.index,'world':list(p)})
report['leggings_modifiers']=[{'name':m.name,'type':m.type,'show_viewport':m.show_viewport,'show_render':m.show_render} for m in obj.modifiers];ev.to_mesh_clear()
(out/'frame129_cycles_geometry_screen.json').write_text(json.dumps(report,indent=2))

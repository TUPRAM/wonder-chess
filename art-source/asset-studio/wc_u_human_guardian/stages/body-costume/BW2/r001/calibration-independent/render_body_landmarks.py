import bpy,json
from pathlib import Path
from mathutils import Vector,Matrix
out=Path(__file__).parent
data=json.loads((out/'open_inspection.json').read_text())
scene=bpy.data.scenes['BW1_BODY_COSTUME'];bpy.context.window.scene=scene;scene.frame_set(1)
rig=bpy.data.objects['BW1_Temporary_Pose_Rig'];rig.animation_data.action=None
for p in rig.pose.bones:
    if 'finger' in p.name and p.name.endswith('.R'):p.matrix_basis=Matrix.Identity(4)
for o in scene.objects:o.hide_render=True
body=bpy.data.objects['BW1_IndexedBody'];body.hide_render=False
print('BODY',len(body.data.vertices),[(m.name,m.type,m.show_render,m.show_viewport) for m in body.modifiers],flush=True)
bpy.context.view_layer.update()
Y=Vector(data['provisional_joint_plane_frame']['Y_distal']);Z=Vector(data['provisional_joint_plane_frame']['Z_UNCLASSIFIED']);O=Vector(data['landmarks_world_BU']['wrist']);T=Vector(data['landmarks_world_BU']['middle_tip']);target=(O+T)*.5
scene.render.engine='BLENDER_WORKBENCH';scene.display.shading.light='STUDIO';scene.display.shading.color_type='SINGLE';scene.display.shading.single_color=(.63,.63,.63);scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True;scene.display.shading.cavity_type='BOTH'
scene.render.resolution_x=900;scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.image_settings.media_type='IMAGE';scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGB';scene.render.film_transparent=False;scene.view_settings.view_transform='Standard';scene.world.color=(.07,.07,.07);scene.use_nodes=False
camdata=bpy.data.cameras.new('BW2_TEMP_independent_body_camera');cam=bpy.data.objects.new('BW2_TEMP_independent_body_camera',camdata);scene.collection.objects.link(cam);camdata.type='ORTHO';camdata.ortho_scale=.25;scene.camera=cam
for label,axis in [('positive_Z',Z),('negative_Z',-Z)]:
    loc=target+axis*.6;viewz=axis.normalized();viewx=Y.cross(viewz).normalized();viewy=viewz.cross(viewx).normalized()
    cam.matrix_world=Matrix(((viewx.x,viewy.x,viewz.x,loc.x),(viewx.y,viewy.y,viewz.y,loc.y),(viewx.z,viewy.z,viewz.z,loc.z),(0,0,0,1)))
    scene.render.filepath=str(out/('body_'+label+'.png'));bpy.ops.render.render(write_still=True)

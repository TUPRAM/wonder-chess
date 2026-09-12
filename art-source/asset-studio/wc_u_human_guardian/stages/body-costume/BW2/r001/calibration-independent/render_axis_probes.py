import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
out=Path(__file__).parent;data=json.loads((out/'finger_axis_calibration.json').read_text())
source=Path(data['source']);assert hashlib.sha256(source.read_bytes()).hexdigest()==data['source_sha256']
scene=bpy.data.scenes['BW1_BODY_COSTUME'];bpy.context.window.scene=scene;scene.frame_set(1)
rig=bpy.data.objects['BW1_Temporary_Pose_Rig'];rig.animation_data.action=None
names=[p.name for p in rig.pose.bones if p.name.startswith('finger') and p.name.endswith('.R')]
for n in names:rig.pose.bones[n].matrix_basis=Matrix.Identity(4)
for o in scene.objects:o.hide_render=True
glove=bpy.data.objects['BW1_Glove_Pair_SourceFit'];glove.hide_render=False
F=Matrix(data['semantic_frame_world']);X=F.to_3x3().col[0];Y=F.to_3x3().col[1];Z=F.to_3x3().col[2]
O=F.translation;T=Vector(json.loads((out/'open_inspection.json').read_text())['landmarks_world_BU']['middle_tip']);target=(O+T)*.5
scene.render.engine='BLENDER_WORKBENCH';scene.display.shading.light='STUDIO';scene.display.shading.color_type='SINGLE';scene.display.shading.single_color=(.63,.63,.63);scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True;scene.display.shading.cavity_type='BOTH'
scene.render.resolution_x=900;scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.image_settings.media_type='IMAGE';scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGB';scene.render.film_transparent=False;scene.view_settings.view_transform='Standard';scene.world.color=(.07,.07,.07);scene.use_nodes=False
camdata=bpy.data.cameras.new('BW2_TEMP_axis_probe_camera');cam=bpy.data.objects.new('BW2_TEMP_axis_probe_camera',camdata);scene.collection.objects.link(cam);camdata.type='ORTHO';camdata.ortho_scale=.25;scene.camera=cam
views={'side':X,'palm':Z}
tests=[('middle_base_plusX5','finger3-1.R','X',5,'side'),('middle_base_minusX5','finger3-1.R','X',-5,'side'),('thumb_base_plusX5','finger1-1.R','X',5,'palm'),('thumb_base_minusZ5','finger1-1.R','Z',-5,'palm')]
metadata={'source':str(source),'source_sha256':data['source_sha256'],'only_rotation_probes_no_grip':True,'tests':[]}
for label,n,axis,deg,view in tests:
    p=rig.pose.bones[n];p.matrix_basis=Matrix.Rotation(math.radians(deg),4,axis);bpy.context.view_layer.update()
    viewz=views[view].normalized();viewx=Y.cross(viewz).normalized();viewy=viewz.cross(viewx).normalized();loc=target+viewz*.6
    cam.matrix_world=Matrix(((viewx.x,viewy.x,viewz.x,loc.x),(viewx.y,viewy.y,viewz.y,loc.y),(viewx.z,viewy.z,viewz.z,loc.z),(0,0,0,1)))
    scene.render.filepath=str(out/(label+'.png'));bpy.ops.render.render(write_still=True)
    metadata['tests'].append({'file':label+'.png','bone':n,'local_axis':axis,'degrees':deg,'view':view,'camera_matrix_world':[list(r) for r in cam.matrix_world]})
    p.matrix_basis=Matrix.Identity(4);bpy.context.view_layer.update()
metadata['source_sha256_after']=hashlib.sha256(source.read_bytes()).hexdigest();assert metadata['source_sha256_after']==data['source_sha256']
(out/'axis_probe_render_metadata.json').write_text(json.dumps(metadata,indent=2))

import bpy,json
from pathlib import Path
from mathutils import Vector, Matrix
out=Path(__file__).parent
scene=bpy.context.scene
rig=bpy.data.objects['BW1_Temporary_Pose_Rig']
record=json.loads((out/'poses_correction1.json').read_text())
scene.view_settings.exposure=0
scene.view_settings.gamma=1
scene.use_nodes=False
for name,energy in [('HAND_KEY',3),('HAND_FILL',1)]:bpy.data.objects[name].data.energy=energy
def apply(pose):
    for pb in rig.pose.bones:pb.matrix_basis=Matrix.Identity(4)
    for name,val in pose.items():rig.pose.bones[name].rotation_euler=val
    bpy.context.view_layer.update()
def render(name,side,pose,handle,back=False):
    apply(pose)
    for s in ('R','L'):bpy.data.objects['STUDY_FIXED_HANDLE_'+s].hide_render=not(handle and s==side)
    h=record['handles'][side];c=Vector(h['center_world']);axis=Vector(h['axis_world']);forward=Vector(h['forward_world']);palmar=Vector(h['palmar_world'])
    target=c-forward*.015;viewdir=(palmar*(-.95 if back else .95)-forward*.4+axis*.28).normalized()
    cam=scene.camera;cam.location=target+viewdir*.6;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
    bpy.data.objects['HAND_KEY'].location=target+viewdir*.30+axis*.20+forward*.16
    bpy.data.objects['HAND_FILL'].location=target+viewdir*.30-axis*.28
    for obj in [bpy.data.objects['HAND_KEY'],bpy.data.objects['HAND_FILL']]:obj.rotation_euler=(target-obj.location).to_track_quat('-Z','Y').to_euler()
    scene.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
render('open_R','R',{},False)
render('relaxed_R','R',record['poses']['relaxed'],False)
render('sword_grip_correction1','R',record['poses']['sword_grip'],True)
render('shield_grip_correction1','L',record['poses']['shield_grip'],True)
render('sword_grip_correction1_dorsal','R',record['poses']['sword_grip'],True,True)
apply({**record['poses']['sword_grip'],**record['poses']['shield_grip']})
bpy.ops.wm.save_as_mainfile(filepath=str(out/'hand_pose_correction1.blend'))

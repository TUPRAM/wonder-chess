"""Bounded Ada import trial; never saves or modifies canonical source/export files."""
import bpy,json,hashlib,sys
from pathlib import Path
from mathutils import Matrix
root=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).resolve().parent))
from author_alpha import export_fbx_raw as export_fbx
uid='wc_u_human_guardian';source=root/f'art-source/heroes/{uid}/{uid}.blend'
before=hashlib.sha256(source.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(source))
arm=bpy.data.objects['Armature'];mesh=bpy.data.objects['SK_'+uid];sc=bpy.context.scene
action=bpy.data.actions[f'AN_{uid}_Idle'];slot=action.slots[0]
arm.animation_data.action=None
for bone in arm.pose.bones:bone.location=(0,0,0);bone.rotation_euler=(0,0,0);bone.scale=(1,1,1)
scale=Matrix.Scale(100,4)
arm.data.transform(scale);mesh.data.transform(scale)
arm.scale=(1,1,1);mesh.scale=(1,1,1);sc.unit_settings.scale_length=.01
bpy.context.view_layer.update()
curves=0;keys=0
for layer in action.layers:
    for strip in layer.strips:
        for bag in strip.channelbags:
            for curve in bag.fcurves:
                if curve.data_path.endswith('location'):
                    curves+=1
                    for key in curve.keyframe_points:
                        key.co.y*=100;key.handle_left.y*=100;key.handle_right.y*=100;keys+=1
                    curve.update()
out=root/'exports/calibration/import-probe-normalized-cm';out.mkdir(parents=True,exist_ok=True)
export_fbx(out/'SK_Ada.fbx',[arm,mesh],False)
arm.animation_data.action=action;arm.animation_data.action_slot=slot
sc.frame_start=1;sc.frame_end=121;sc.frame_set(1);bpy.context.view_layer.update()
export_fbx(out/'AN_Ada_Idle.fbx',[arm],True)
after=hashlib.sha256(source.read_bytes()).hexdigest()
if before!=after:raise RuntimeError('Canonical source changed during read-only export trial')
report={'purpose':'bounded normalized-centimeter import trial, not production export acceptance',
        'blender_version':bpy.app.version_string,'source':str(source.relative_to(root)),'source_sha256':before,
        'canonical_source_unchanged':before==after,'source_units':'meters retained on disk','trial_scene_scale_length':sc.unit_settings.scale_length,
        'method':'Loaded source into an isolated Blender process; Armature.data.transform(Scale100) and Mesh.data.transform(Scale100); multiplied every Idle location FCurve value and both handle ordinates by 100; object scales remain 1; selected FBX export unchanged.',
        'converted_location_curves':curves,'converted_location_keys':keys,'armature_object_scale':list(arm.scale),
        'mesh_object_scale':list(mesh.scale),'root_pose_scale':list(arm.pose.bones['root'].scale),
        'root_rest_head_cm':list(arm.data.bones['root'].head_local),'root_rest_tail_cm':list(arm.data.bones['root'].tail_local),
        'mesh_dimensions_trial_cm':list(mesh.dimensions),
        'files':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.glob('*.fbx')}}
(out/'trial_manifest.json').write_text(json.dumps(report,indent=2)+'\n')
print('WC_NORMALIZED_CM_TRIAL_COMPLETE '+json.dumps(report),flush=True)

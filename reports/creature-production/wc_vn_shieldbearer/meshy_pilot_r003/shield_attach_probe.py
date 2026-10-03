import json, unreal
from pathlib import Path
ROOT = Path(unreal.Paths.project_dir()).resolve().parent
out = {}
try:
    mesh = unreal.load_asset("/Game/WonderChess/VNext/Heroes/Shieldbearer_r003/SK_Shieldbearer")
    poses = unreal.AnimPoseExtensions
    ref = poses.get_reference_pose(mesh.skeleton)
    bone = poses.get_ref_bone_pose(ref, "LeftForeArm", unreal.AnimPoseSpaces.WORLD)
    hand = poses.get_ref_bone_pose(ref, "LeftHand", unreal.AnimPoseSpaces.WORLD)
    out["forearm"] = {"t": [bone.translation.x, bone.translation.y, bone.translation.z], "scale": [bone.scale3d.x, bone.scale3d.y, bone.scale3d.z]}
    out["hand"] = [hand.translation.x, hand.translation.y, hand.translation.z]
    results = {}
    # Desired shield pose in mesh space: upright beside the left forearm, slightly in front of the body.
    for name, yaw in (("yaw0", 0.0), ("yaw180", 180.0)):
        desired = unreal.Transform(location=unreal.Vector(bone.translation.x + 14, bone.translation.y + 16, 92),
                                   rotation=unreal.Rotator(roll=0, pitch=0, yaw=yaw), scale=unreal.Vector(0.62, 0.62, 0.62))
        relative = unreal.MathLibrary.make_relative_transform(desired, bone)
        r = relative.rotation.rotator()
        results[name] = {"location": [round(relative.translation.x, 3), round(relative.translation.y, 3), round(relative.translation.z, 3)],
                         "rotation_pitch_yaw_roll": [round(r.pitch, 3), round(r.yaw, 3), round(r.roll, 3)],
                         "scale": round(relative.scale3d.x, 4)}
    out["relative"] = results
except Exception as error:
    import traceback
    out["error"] = traceback.format_exc()
(ROOT / "reports/creature-production/wc_vn_shieldbearer/meshy_pilot_r003/shield-attach-probe.json").write_text(json.dumps(out, indent=2))
unreal.SystemLibrary.quit_editor()

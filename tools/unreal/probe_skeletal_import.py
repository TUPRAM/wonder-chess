"""Isolated UE FBX unit/basis trials; never alters production hero assets."""
from pathlib import Path
import hashlib
import json
import os
import traceback
import unreal

ROOT = Path(unreal.Paths.project_dir()).resolve().parent
REPORT = ROOT / "reports/WC-330/import-probe"
REPORT.mkdir(parents=True, exist_ok=True)
UID = "wc_u_human_guardian"
SOURCE_NAME = os.environ.get("WC_PROBE_SOURCE_NAME", UID)
CLIPS = os.environ.get("WC_PROBE_CLIPS", "Idle").split(",")
if not CLIPS or any(clip not in ("Idle", "Move", "Attack", "Active", "Hit", "Defeat", "Victory") for clip in CLIPS):
    raise RuntimeError("Unknown requested animation clip")
SOURCE = Path(os.environ.get("WC_PROBE_SOURCE", str(ROOT / "exports/heroes" / UID))).resolve()
MOUNT = "/Game/WonderChess/Calibration/ImportTrials"
PRESETS = [
    dict(name="baseline", units=True, front=True, scene=True, yaw=180, preserve=False),
    dict(name="preserve", units=True, front=True, scene=True, yaw=180, preserve=True),
    dict(name="no_front", units=True, front=False, scene=True, yaw=180, preserve=False),
    dict(name="no_front_preserve", units=True, front=False, scene=True, yaw=180, preserve=True),
    dict(name="no_units", units=False, front=True, scene=True, yaw=180, preserve=False),
    dict(name="no_scene", units=True, front=False, scene=False, yaw=0, preserve=False),
    dict(name="no_front_yaw0", units=True, front=False, scene=True, yaw=0, preserve=False),
    dict(name="no_front_yaw90", units=True, front=False, scene=True, yaw=90, preserve=False),
    dict(name="no_front_yaw270", units=True, front=False, scene=True, yaw=270, preserve=False),
]
SELECTED = os.environ.get("WC_PROBE_PRESETS", "").split(",")
PREFIX = os.environ.get("WC_PROBE_PREFIX", "meters")
if not PREFIX.replace("_", "").isalnum():
    raise RuntimeError("Probe prefix must contain only letters, digits or underscores")
if SELECTED != [""]:
    PRESETS = [item for item in PRESETS if item["name"] in SELECTED]
if not PRESETS:
    raise RuntimeError("No named probe preset selected")


def transform(value):
    return {
        "translation": [value.translation.x, value.translation.y, value.translation.z],
        "scale": [value.scale3d.x, value.scale3d.y, value.scale3d.z],
        "quaternion": [value.rotation.x, value.rotation.y, value.rotation.z, value.rotation.w],
    }


def settings(preset, animation=False, skeleton=None):
    options = unreal.FbxImportUI()
    options.automated_import_should_detect_type = False
    options.import_materials = False
    options.import_textures = False
    options.create_physics_asset = False
    options.import_as_skeletal = True
    options.import_mesh = not animation
    options.import_animations = animation
    options.mesh_type_to_import = unreal.FBXImportType.FBXIT_ANIMATION if animation else unreal.FBXImportType.FBXIT_SKELETAL_MESH
    if skeleton:
        options.skeleton = skeleton
    for data in (options.skeletal_mesh_import_data, options.anim_sequence_import_data):
        data.convert_scene = preset["scene"]
        data.convert_scene_unit = preset["units"]
        data.force_front_x_axis = preset["front"]
        data.import_rotation = unreal.Rotator(pitch=0, yaw=preset["yaw"], roll=0)
        data.import_uniform_scale = 1.0
        data.import_translation = unreal.Vector(0, 0, 0)
    options.anim_sequence_import_data.set_editor_property("preserve_local_transform", preset["preserve"])
    return options


def import_file(filename, folder, name, options):
    if not folder.startswith(MOUNT + "/"):
        raise RuntimeError("Import destination escaped owned calibration namespace")
    task = unreal.AssetImportTask()
    task.filename = str(filename)
    task.destination_path = folder
    task.destination_name = name
    task.automated = True
    task.replace_existing = True
    task.save = True
    task.options = options
    task.factory = unreal.FbxFactory()
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    if not task.imported_object_paths:
        raise RuntimeError("No assets imported: " + str(filename))
    return [unreal.load_asset(path) for path in task.imported_object_paths]


def sample(mesh, sequence):
    poses = unreal.AnimPoseExtensions
    reference = poses.get_reference_pose(mesh.skeleton)
    result = {"reference_bones": [str(name) for name in poses.get_bone_names(reference)], "reference": {}}
    for bone in ("root", "pelvis", "head", "foot_l", "foot_r", "toe_l", "toe_r", "cast_origin"):
        result["reference"][bone] = {
            "local": transform(poses.get_ref_bone_pose(reference, bone, unreal.AnimPoseSpaces.LOCAL)),
            "world": transform(poses.get_ref_bone_pose(reference, bone, unreal.AnimPoseSpaces.WORLD)),
        }
    result["samples"] = []
    for kind in (unreal.AnimDataEvalType.SOURCE, unreal.AnimDataEvalType.RAW, unreal.AnimDataEvalType.COMPRESSED):
        for retarget in (False, True):
            options = unreal.AnimPoseEvaluationOptions()
            options.evaluation_type = kind
            options.should_retarget = retarget
            options.extract_root_motion = False
            options.incorporate_root_motion_into_pose = True
            options.optional_skeletal_mesh = mesh
            for fraction in (0.0, 0.25, 0.5, 0.75, 1.0):
                time = float(sequence.sequence_length) * fraction
                pose = poses.get_anim_pose_at_time(sequence, time, options)
                if not poses.is_valid(pose):
                    raise RuntimeError("Imported animation evaluated to invalid pose")
                entry = {"evaluation": str(kind), "retarget": retarget, "time": time, "bones": {}}
                for bone in ("root", "pelvis", "head", "foot_l", "foot_r", "toe_l", "toe_r", "cast_origin"):
                    entry["bones"][bone] = {
                        "local": transform(poses.get_bone_pose(pose, bone, unreal.AnimPoseSpaces.LOCAL)),
                        "world": transform(poses.get_bone_pose(pose, bone, unreal.AnimPoseSpaces.WORLD)),
                    }
                result["samples"].append(entry)
    return result


def main():
    unreal.SystemLibrary.execute_console_command(None, "Interchange.FeatureFlags.Import.FBX 0")
    unreal.SystemLibrary.execute_console_command(None, "Interchange.FeatureFlags.Import.Enable 0")
    (REPORT / "python-api.txt").write_text("\n\n".join(str(getattr(unreal.AnimPoseExtensions, name).__doc__) for name in ("get_reference_pose", "get_anim_pose_at_time", "get_bone_pose", "get_ref_bone_pose")), encoding="utf-8")
    report = {"engine": unreal.SystemLibrary.get_engine_version(), "source": str(SOURCE), "source_sha256": {}, "trials": [], "boundary": "Isolated imported assets and actual source/raw/compressed pose evaluations; visual acceptance remains separate."}
    for name in [f"SK_{SOURCE_NAME}.fbx"] + [f"AN_{SOURCE_NAME}_{clip}.fbx" for clip in CLIPS]:
        report["source_sha256"][name] = hashlib.sha256((SOURCE / name).read_bytes()).hexdigest()
    output = REPORT / (PREFIX + "-results.json")
    for preset in PRESETS:
        folder = MOUNT + "/" + PREFIX + "_" + preset["name"]
        entry = {"preset": preset, "folder": folder, "status": "STARTED"}
        report["trials"].append(entry)
        output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        try:
            imported = import_file(SOURCE / f"SK_{SOURCE_NAME}.fbx", folder, f"SK_{UID}", settings(preset))
            mesh = next(value for value in imported if isinstance(value, unreal.SkeletalMesh))
            if not mesh.skeleton:
                raise RuntimeError("Imported mesh lacks a skeleton")
            if not unreal.EditorAssetLibrary.save_loaded_asset(mesh.skeleton):
                raise RuntimeError("Could not save trial skeleton")
            bounds = mesh.get_bounds()
            entry.update(mesh=mesh.get_path_name(), skeleton=mesh.skeleton.get_path_name(),
                         bounds_origin_cm=[bounds.origin.x, bounds.origin.y, bounds.origin.z], bounds_extent_cm=[bounds.box_extent.x, bounds.box_extent.y, bounds.box_extent.z])
            entry["clips"] = []
            for clip in CLIPS:
                imported = import_file(SOURCE / f"AN_{SOURCE_NAME}_{clip}.fbx", folder, f"AN_{UID}_{clip}", settings(preset, True, mesh.skeleton))
                sequence = next(value for value in imported if isinstance(value, unreal.AnimSequence))
                samples = sample(mesh, sequence)
                entry["clips"].append(dict(name=clip, animation=sequence.get_path_name(), sequence_seconds=sequence.sequence_length, **samples))
                if clip == CLIPS[0]:
                    entry.update(animation=sequence.get_path_name(), sequence_seconds=sequence.sequence_length, **samples)
            entry["status"] = "SAMPLED"
            unreal.log("WC_IMPORT_PROBE_SAMPLED " + folder)
        except Exception as error:
            entry.update(status="ERROR", error=str(error), traceback=traceback.format_exc())
            unreal.log_warning("WC_IMPORT_PROBE_ERROR " + str(error))
        output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    unreal.log("WC_IMPORT_PROBE_REPORT " + str(output))
    if any(item["status"] != "SAMPLED" for item in report["trials"]):
        raise RuntimeError("One or more import trial probes could not finish")


if __name__ == "__main__":
    main()

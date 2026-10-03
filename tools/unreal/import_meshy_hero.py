"""Import one hero's Meshy models into an isolated candidate folder and report what Unreal created.

Runs inside the Unreal editor (-ExecutePythonScript). Reads WC_MESHY_IMPORT (a JSON job) from the environment.
The body comes from the rigged FBX; every clip is imported as animation only onto that one skeleton; items are
static meshes. Nothing outside the job's destination folder is touched; an existing destination is refused.
"""
import json
import os
import traceback
from pathlib import Path

import unreal

ROOT = Path(unreal.Paths.project_dir()).resolve().parent
TOOLS = unreal.AssetToolsHelpers.get_asset_tools()


def fbx_options(animation, skeleton=None):
    options = unreal.FbxImportUI()
    options.automated_import_should_detect_type = False
    options.import_as_skeletal = True
    options.import_mesh = not animation
    options.import_animations = animation
    options.import_materials = not animation
    options.import_textures = not animation
    options.create_physics_asset = False
    options.mesh_type_to_import = (unreal.FBXImportType.FBXIT_ANIMATION if animation
                                   else unreal.FBXImportType.FBXIT_SKELETAL_MESH)
    if skeleton:
        options.skeleton = skeleton
    for data in (options.skeletal_mesh_import_data, options.anim_sequence_import_data):
        data.convert_scene = True
        data.convert_scene_unit = True
    return options


def run(filename, folder, name=None, options=None):
    task = unreal.AssetImportTask()
    task.filename = str(ROOT / filename)
    task.destination_path = folder
    if name:
        task.destination_name = name
    task.automated = True
    task.save = True
    task.replace_existing = False
    if options:
        task.options = options
        task.factory = unreal.FbxFactory()
    TOOLS.import_asset_tasks([task])
    return [unreal.load_asset(path) for path in task.imported_object_paths]


def extent(asset):
    box = asset.get_bounds().box_extent
    return [round(value, 1) for value in (box.x, box.y, box.z)]


def vector(value):
    return [round(component, 1) for component in (value.x, value.y, value.z)]


def main():
    job = json.loads(Path(os.environ["WC_MESHY_IMPORT"]).read_text(encoding="utf-8"))
    report = {"destination": job["destination"], "status": "STARTED"}
    try:
        base, name = job["destination"], job["name"]
        if job.get("add_clips_only"):
            # Adds clips to an existing candidate; the body, skeleton and items are left as they are.
            mesh = unreal.load_asset(f"{base}/SK_{name}")
            if not isinstance(mesh, unreal.SkeletalMesh):
                raise RuntimeError("The candidate body to add clips to is missing")
        else:
            if unreal.EditorAssetLibrary.does_directory_exist(base):
                raise RuntimeError("Destination already exists; choose a new candidate folder")
            imported = run(job["body"], base, f"SK_{name}", fbx_options(False))
            mesh = next(asset for asset in imported if isinstance(asset, unreal.SkeletalMesh))
        poses = unreal.AnimPoseExtensions
        reference = poses.get_reference_pose(mesh.skeleton)
        bones = [str(bone) for bone in poses.get_bone_names(reference)]
        report["body"] = {"mesh": mesh.get_path_name(), "skeleton": mesh.skeleton.get_path_name(), "bones": len(bones),
                          "half_extent_cm": extent(mesh), "materials": [str(m.material_interface.get_path_name())
                                                                      for m in mesh.materials],
                          # Which way the rest pose faces and where its left side is, for placement on the board.
                          "rest_pose_cm": {bone: vector(poses.get_ref_bone_pose(
                              reference, bone, unreal.AnimPoseSpaces.WORLD).translation)
                              for bone in ("Head", "LeftHand", "RightHand", "LeftToeBase", "LeftFoot") if bone in bones}}
        # One file may hold several takes; Unreal names each sequence after the file and take.
        for label, filename in job["clips"].items():
            run(filename, f"{base}/Animations", f"A_{name}_{label}", fbx_options(True, mesh.skeleton))
        report["clips"] = {}
        for path in unreal.EditorAssetLibrary.list_assets(f"{base}/Animations", recursive=True):
            asset = unreal.EditorAssetLibrary.load_asset(path)
            if isinstance(asset, unreal.AnimSequence):
                report["clips"][path.split(".")[0]] = round(asset.get_play_length(), 3)
        if not report["clips"]:
            raise RuntimeError("No animation was imported")
        report["items"] = {}
        for item, filename in job.get("items", {}).items():
            for asset in run(filename, f"{base}/Items/{item}"):
                if isinstance(asset, unreal.StaticMesh):
                    report["items"][item] = {"asset": asset.get_path_name(), "half_extent_cm": extent(asset),
                                             "triangles": asset.get_num_triangles(0)}
        # An import task saves only its primary asset. The skeleton, materials, textures and the extra takes of
        # a multi-take file exist only in memory until the whole folder is saved.
        if not unreal.EditorAssetLibrary.save_directory(base, only_if_is_dirty=False, recursive=True):
            raise RuntimeError("Saving the candidate folder failed")
        report["assets"] = sorted(unreal.EditorAssetLibrary.list_assets(base, recursive=True))
        report["status"] = "IMPORTED"
    except Exception:
        report["status"] = "FAILED"
        report["error"] = traceback.format_exc()
    path = ROOT / job["report"]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    unreal.SystemLibrary.quit_editor()


main()

"""Import the courtyard Meshy models and the banner cut-out as candidates. Not approved art.

Each model becomes one static mesh at a fixed path, Props/<piece>/SM_<piece>, so the game can load it by name.
A piece whose destination folder already exists is skipped, never replaced.
"""
import json
import traceback
from pathlib import Path

import unreal

root = Path(unreal.Paths.project_dir()).resolve().parent
inputs = root / "art-source/asset-studio/wc_env_courtyard/inputs"
folder = "/Game/WonderChess/VNext/Environment/Courtyard_r001"
tools = unreal.AssetToolsHelpers.get_asset_tools()
library = unreal.MaterialEditingLibrary
report = {"folder": folder, "pieces": {}, "boundary": "Imported candidate art; no owner approval"}


def run(filename, destination, name=None):
    task = unreal.AssetImportTask()
    task.filename, task.destination_path = str(filename), destination
    if name:
        task.destination_name = name
    task.automated = task.save = True
    task.replace_existing = False
    tools.import_asset_tasks([task])
    return [unreal.load_asset(path) for path in task.imported_object_paths]


try:
    for piece in ("round_tower", "gatehouse", "brazier", "yard_props"):
        destination = f"{folder}/Props/{piece}"
        source = inputs / f"meshy/{piece}_r001/original/model_urls_glb.glb"
        if unreal.EditorAssetLibrary.does_directory_exist(destination):
            report["pieces"][piece] = "already imported; skipped"
            continue
        if not source.is_file():
            report["pieces"][piece] = "no downloaded model"
            continue
        run(source, destination)
        meshes = [unreal.EditorAssetLibrary.load_asset(path) for path in
                  unreal.EditorAssetLibrary.list_assets(destination, recursive=True)]
        meshes = [asset for asset in meshes if isinstance(asset, unreal.StaticMesh)]
        if len(meshes) != 1:
            raise RuntimeError(f"{piece}: expected one static mesh, found {len(meshes)}")
        target = f"{destination}/SM_{piece}"
        if meshes[0].get_path_name().split(".")[0] != target and not unreal.EditorAssetLibrary.rename_asset(
                meshes[0].get_path_name().split(".")[0], target):
            raise RuntimeError(f"{piece}: could not name the mesh")
        mesh = unreal.EditorAssetLibrary.load_asset(target)
        bounds = mesh.get_bounds()
        report["pieces"][piece] = {"mesh": target, "triangles": mesh.get_num_triangles(0),
                                   "origin_cm": [round(v, 1) for v in (bounds.origin.x, bounds.origin.y, bounds.origin.z)],
                                   "half_extent_cm": [round(v, 1) for v in (bounds.box_extent.x, bounds.box_extent.y, bounds.box_extent.z)]}
    if not unreal.EditorAssetLibrary.does_asset_exist(f"{folder}/T_Banner"):
        banner = run(inputs / "textures_r001/derived/wall_banner_cutout.png", folder, "T_Banner")[0]
        material = tools.create_asset("M_CourtyardCutout", folder, unreal.Material, unreal.MaterialFactoryNew())
        material.set_editor_property("blend_mode", unreal.BlendMode.BLEND_MASKED)
        material.set_editor_property("two_sided", True)
        sample = library.create_material_expression(material, unreal.MaterialExpressionTextureSampleParameter2D, -500, 0)
        sample.set_editor_property("parameter_name", "Texture")
        sample.set_editor_property("texture", banner)
        library.connect_material_property(sample, "RGB", unreal.MaterialProperty.MP_BASE_COLOR)
        library.connect_material_property(sample, "A", unreal.MaterialProperty.MP_OPACITY_MASK)
        rough = library.create_material_expression(material, unreal.MaterialExpressionConstant, -250, 300)
        rough.set_editor_property("r", 0.85)
        library.connect_material_property(rough, "", unreal.MaterialProperty.MP_ROUGHNESS)
        library.recompile_material(material)
        report["banner"] = "T_Banner and M_CourtyardCutout created"
    unreal.EditorAssetLibrary.save_directory(folder, only_if_is_dirty=False, recursive=True)
    report["status"] = "IMPORTED"
except Exception:
    report["status"] = "FAILED"
    report["error"] = traceback.format_exc()
path = root / "reports/vnext/environment/courtyard-props-r001.json"
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

"""Import handmade effect props as static meshes at /Game/WonderChess/VNext/Effects/Props/SM_<Name>.

Reads WC_EFFECT_PROPS (a JSON job: {"source": folder holding <Name>/<Name>.fbx, "names": [...], "report": path}).
A prop that already exists is replaced, so a rebuilt model can be re-imported. Candidate art, not approved.
"""
import json
import os
import traceback
from pathlib import Path

import unreal

root = Path(unreal.Paths.project_dir()).resolve().parent
job = json.loads(Path(os.environ["WC_EFFECT_PROPS"]).read_text(encoding="utf-8"))
folder = "/Game/WonderChess/VNext/Effects/Props"
report = {"folder": folder, "status": "STARTED", "props": {}}
try:
    for name in job["names"]:
        options = unreal.FbxImportUI()
        options.automated_import_should_detect_type = False
        options.import_as_skeletal = False
        options.import_mesh = True
        options.import_animations = False
        options.import_materials = True
        options.import_textures = True
        options.mesh_type_to_import = unreal.FBXImportType.FBXIT_STATIC_MESH
        options.static_mesh_import_data.combine_meshes = True
        options.static_mesh_import_data.convert_scene = True
        options.static_mesh_import_data.convert_scene_unit = True
        task = unreal.AssetImportTask()
        task.filename = str(root / job["source"] / name / f"{name}.fbx")
        task.destination_path = f"{folder}/{name}"
        task.destination_name = f"SM_{name}"
        task.automated = task.save = task.replace_existing = True
        task.options = options
        task.factory = unreal.FbxFactory()
        unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
        mesh = unreal.EditorAssetLibrary.load_asset(f"{folder}/{name}/SM_{name}")
        if not isinstance(mesh, unreal.StaticMesh):
            raise RuntimeError(f"{name} did not import as a static mesh")
        # Props are drawn many at a time as instances, which the imported material is not set up for. Give each one
        # its own small material: the baked colour, usable on instanced meshes, and self-lit for flashes.
        library = unreal.MaterialEditingLibrary
        texture = unreal.EditorAssetLibrary.load_asset(f"{folder}/{name}/T_{name}_Color")
        look_path = f"{folder}/{name}/M_{name}_Prop"
        if unreal.EditorAssetLibrary.does_asset_exist(look_path):
            look = unreal.EditorAssetLibrary.load_asset(look_path)
            library.delete_all_material_expressions(look)
        else:
            look = unreal.AssetToolsHelpers.get_asset_tools().create_asset(f"M_{name}_Prop", f"{folder}/{name}", unreal.Material, unreal.MaterialFactoryNew())
        look.set_editor_property("used_with_instanced_static_meshes", True)
        look.set_editor_property("two_sided", True)
        sample = library.create_material_expression(look, unreal.MaterialExpressionTextureSample, -500, 0)
        sample.set_editor_property("texture", texture)
        if name in job.get("glowing", []):
            look.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_UNLIT)
            bright = library.create_material_expression(look, unreal.MaterialExpressionMultiply, -250, 0)
            bright.set_editor_property("const_b", 4.0)
            library.connect_material_expressions(sample, "RGB", bright, "A")
            library.connect_material_property(bright, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
        else:
            library.connect_material_property(sample, "RGB", unreal.MaterialProperty.MP_BASE_COLOR)
            rough = library.create_material_expression(look, unreal.MaterialExpressionConstant, -250, 250)
            rough.set_editor_property("r", 0.75)
            library.connect_material_property(rough, "", unreal.MaterialProperty.MP_ROUGHNESS)
        library.recompile_material(look)
        mesh.set_material(0, look)
        bounds = mesh.get_bounds()
        report["props"][name] = {"mesh": f"{folder}/{name}/SM_{name}", "triangles": mesh.get_num_triangles(0),
                                 "half_extent_cm": [round(v, 1) for v in (bounds.box_extent.x, bounds.box_extent.y, bounds.box_extent.z)]}
    unreal.EditorAssetLibrary.save_directory(folder, only_if_is_dirty=False, recursive=True)
    report["status"] = "IMPORTED"
except Exception:
    report["status"] = "FAILED"
    report["error"] = traceback.format_exc()
path = root / job["report"]
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

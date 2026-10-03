"""Import the courtyard flat textures and create the two materials that show them. Candidate art; not approved."""
import json
from pathlib import Path
import unreal

root = Path(unreal.Paths.project_dir()).resolve().parent
source = root / "art-source/asset-studio/wc_env_courtyard/inputs/textures_r001"
folder = "/Game/WonderChess/VNext/Environment/Courtyard_r001"
files = {"T_Flagstone": source / "flagstone_tile.png", "T_BoardLight": source / "board_tile_light.png",
         "T_BoardDark": source / "board_tile_dark.png", "T_Sky": source / "sky_backdrop.png",
         "T_WallStone": source / "derived/wall_stone_tile.png"}
tasks = []
for name, path in files.items():
    if not path.is_file():
        raise RuntimeError(f"Missing texture source {path}")
    task = unreal.AssetImportTask()
    task.filename, task.destination_path, task.destination_name = str(path), folder, name
    task.automated = task.replace_existing = task.save = True
    tasks.append(task)
tools = unreal.AssetToolsHelpers.get_asset_tools()
tools.import_asset_tasks(tasks)
textures = {name: unreal.EditorAssetLibrary.load_asset(f"{folder}/{name}") for name in files}
if not all(textures.values()):
    raise RuntimeError("A courtyard texture did not import")
library = unreal.MaterialEditingLibrary


def material(name, unlit):
    path = f"{folder}/{name}"
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        return unreal.EditorAssetLibrary.load_asset(path)
    asset = tools.create_asset(name, folder, unreal.Material, unreal.MaterialFactoryNew())
    coordinate = library.create_material_expression(asset, unreal.MaterialExpressionTextureCoordinate, -900, 0)
    tiling = library.create_material_expression(asset, unreal.MaterialExpressionAppendVector, -900, 200)
    for index, parameter in enumerate(("TilingU", "TilingV")):
        scalar = library.create_material_expression(asset, unreal.MaterialExpressionScalarParameter, -1150, 150 + index * 120)
        scalar.set_editor_property("parameter_name", parameter)
        scalar.set_editor_property("default_value", 1.0)
        library.connect_material_expressions(scalar, "", tiling, "A" if index == 0 else "B")
    scaled = library.create_material_expression(asset, unreal.MaterialExpressionMultiply, -700, 0)
    library.connect_material_expressions(coordinate, "", scaled, "A")
    library.connect_material_expressions(tiling, "", scaled, "B")
    sample = library.create_material_expression(asset, unreal.MaterialExpressionTextureSampleParameter2D, -500, 0)
    sample.set_editor_property("parameter_name", "Texture")
    sample.set_editor_property("texture", textures["T_Flagstone"])
    library.connect_material_expressions(scaled, "", sample, "UVs")
    color = library.create_material_expression(asset, unreal.MaterialExpressionVectorParameter, -500, 300)
    color.set_editor_property("parameter_name", "Color")
    color.set_editor_property("default_value", unreal.LinearColor(1, 1, 1, 1))
    tinted = library.create_material_expression(asset, unreal.MaterialExpressionMultiply, -250, 100)
    library.connect_material_expressions(sample, "RGB", tinted, "A")
    library.connect_material_expressions(color, "", tinted, "B")
    if unlit:
        asset.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_UNLIT)
        library.connect_material_property(tinted, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    else:
        library.connect_material_property(tinted, "", unreal.MaterialProperty.MP_BASE_COLOR)
        rough = library.create_material_expression(asset, unreal.MaterialExpressionConstant, -250, 350)
        rough.set_editor_property("r", 0.9)
        library.connect_material_property(rough, "", unreal.MaterialProperty.MP_ROUGHNESS)
    library.recompile_material(asset)
    return asset


materials = [material("M_CourtyardStone", False), material("M_CourtyardSky", True)]
unreal.EditorAssetLibrary.save_directory(folder, only_if_is_dirty=False, recursive=True)
report = root / "reports/vnext/environment/courtyard-textures-r001.json"
report.parent.mkdir(parents=True, exist_ok=True)
report.write_text(json.dumps({"folder": folder, "textures": sorted(files), "materials": [m.get_name() for m in materials],
                              "engine": unreal.SystemLibrary.get_engine_version(),
                              "boundary": "Imported and saved candidate art; no owner approval, runtime look reviewed separately"}, indent=2))

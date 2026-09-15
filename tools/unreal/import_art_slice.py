"""Import the bounded ArtSliceR001 sources into owned Unreal assets; no canonical art is replaced."""
import hashlib
import json
from pathlib import Path
import unreal

root = Path(unreal.Paths.project_dir()).resolve().parent
source = root / "art-source/2d-slice/r001/sources"
report = root / "reports/vnext/milestones/2d-slice-20260913/import.json"
destination = "/Game/WonderChess/VNext/ArtSliceR001"
specs = [
    ("bellback_portrait.png", "T_BellbackPortrait", 1024, True),
    ("heavy_bloom.png", "T_HeavyBloom", 512, True),
    ("quiet_stone.png", "T_QuietStone", 1024, False),
]
rows = []
for filename, name, size, ui in specs:
    asset_path = destination + "/" + name
    if unreal.EditorAssetLibrary.does_asset_exist(asset_path):
        raise RuntimeError("Preserve existing candidate; inspect before another import: " + asset_path)
    if not (source / filename).is_file():
        raise RuntimeError("Missing source: " + filename)
for filename, name, size, ui in specs:
    task = unreal.AssetImportTask()
    task.set_editor_property("filename", str(source / filename))
    task.set_editor_property("destination_path", destination)
    task.set_editor_property("destination_name", name)
    task.set_editor_property("automated", True)
    task.set_editor_property("replace_existing", False)
    task.set_editor_property("save", False)
    task.set_editor_property("factory", unreal.TextureFactory())
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    texture = unreal.EditorAssetLibrary.load_asset(destination + "/" + name)
    if not isinstance(texture, unreal.Texture2D):
        raise RuntimeError("Texture import missing/wrong class: " + name)
    texture.set_editor_property("srgb", True)
    texture.set_editor_property("power_of_two_mode", unreal.TexturePowerOfTwoSetting.RESIZE_TO_SPECIFIC_RESOLUTION)
    texture.set_editor_property("resize_during_build_x", size)
    texture.set_editor_property("resize_during_build_y", size)
    texture.set_editor_property("max_texture_size", size)
    texture.set_editor_property("lod_group", unreal.TextureGroup.TEXTUREGROUP_UI if ui else unreal.TextureGroup.TEXTUREGROUP_WORLD)
    texture.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_EDITOR_ICON if ui else unreal.TextureCompressionSettings.TC_DEFAULT)
    texture.set_editor_property("mip_gen_settings", unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS if ui else unreal.TextureMipGenSettings.TMGS_SIMPLE_AVERAGE)
    texture.set_editor_property("never_stream", ui)
    if not unreal.EditorAssetLibrary.save_loaded_asset(texture):
        raise RuntimeError("Texture save failed: " + name)
    rows.append({"source": filename, "source_sha256": hashlib.sha256((source / filename).read_bytes()).hexdigest(),
                 "asset": texture.get_path_name(), "requested_build_size": size, "ui": ui,
                 "built_size": [texture.blueprint_get_size_x(), texture.blueprint_get_size_y()], "opaque": True})
material_path = destination + "/M_QuietStone"
if unreal.EditorAssetLibrary.does_asset_exist(material_path):
    raise RuntimeError("Preserve existing material candidate")
material = unreal.AssetToolsHelpers.get_asset_tools().create_asset("M_QuietStone", destination, unreal.Material, unreal.MaterialFactoryNew())
edit = unreal.MaterialEditingLibrary
sample = edit.create_material_expression(material, unreal.MaterialExpressionTextureSample, -550, 0)
sample.set_editor_property("texture", unreal.EditorAssetLibrary.load_asset(destination + "/T_QuietStone"))
color = edit.create_material_expression(material, unreal.MaterialExpressionVectorParameter, -550, 220)
color.set_editor_property("parameter_name", "Color")
color.set_editor_property("default_value", unreal.LinearColor(.50, .54, .49, 1))
multiply = edit.create_material_expression(material, unreal.MaterialExpressionMultiply, -250, 0)
assert edit.connect_material_expressions(sample, "RGB", multiply, "A")
assert edit.connect_material_expressions(color, "", multiply, "B")
assert edit.connect_material_property(multiply, "", unreal.MaterialProperty.MP_BASE_COLOR)
roughness = edit.create_material_expression(material, unreal.MaterialExpressionConstant, -220, 260)
roughness.set_editor_property("r", .94)
assert edit.connect_material_property(roughness, "", unreal.MaterialProperty.MP_ROUGHNESS)
specular = edit.create_material_expression(material, unreal.MaterialExpressionConstant, -220, 360)
specular.set_editor_property("r", .18)
assert edit.connect_material_property(specular, "", unreal.MaterialProperty.MP_SPECULAR)
edit.recompile_material(material)
assert unreal.EditorAssetLibrary.save_loaded_asset(material)
report.write_text(json.dumps({"engine": unreal.SystemLibrary.get_engine_version(), "textures": rows,
                             "material": material_path, "saved": True,
                             "boundary": "Source import and material save only; package and visual checks are separate."}, indent=2))
unreal.log("WC_ART_SLICE_IMPORT_SAVED")


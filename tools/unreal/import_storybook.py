"""Import Storybook r001 illustrations into a fresh owned candidate asset lane."""
import hashlib
import json
from pathlib import Path
import unreal

root = Path(unreal.Paths.project_dir()).resolve().parent
source = root / "art-source/2d-expansion/r001"
report = root / "reports/vnext/milestones/storybook-20260913/import.json"
destination = "/Game/WonderChess/VNext/ArtExpansionR001"
heroes = ("bellback", "cragstoat", "grandmother_root", "snapvine", "prism_organ", "reefglass")
relics = ("quick_wick", "long_lens", "broad_canopy", "close_focus", "tight_choir", "silk_trigger", "patient_lantern", "far_hourglass", "wide_hourglass", "narrow_metronome", "urgent_shard")
specs = [(f"portraits/{hero}.png", f"T_Portrait_{hero}", 1024, 1024) for hero in heroes if hero != "bellback"]
specs += [(f"abilities/{hero}.png", f"T_Ability_{hero}", 512, 512) for hero in heroes]
specs += [(f"relics/wc_vn_r_{relic}.png", f"T_Relic_{relic}", 512, 512) for relic in relics]
specs += [("environment/sanctuary_background.png", "T_SanctuaryBackground", 2048, 1280)]
for filename, name, width, height in specs:
    if unreal.EditorAssetLibrary.does_asset_exist(destination + "/" + name):
        raise RuntimeError("Preserve imported candidate; inspect before retry: " + name)
    if not (source / filename).is_file():
        raise RuntimeError("Missing source: " + filename)
if unreal.EditorAssetLibrary.does_asset_exist(destination + "/M_SanctuaryBackground"):
    raise RuntimeError("Preserve existing background material")
rows = []
for filename, name, width, height in specs:
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
        raise RuntimeError("Missing/wrong texture: " + name)
    texture.set_editor_property("srgb", True)
    texture.set_editor_property("power_of_two_mode", unreal.TexturePowerOfTwoSetting.RESIZE_TO_SPECIFIC_RESOLUTION)
    texture.set_editor_property("resize_during_build_x", width)
    texture.set_editor_property("resize_during_build_y", height)
    texture.set_editor_property("max_texture_size", max(width, height))
    texture.set_editor_property("lod_group", unreal.TextureGroup.TEXTUREGROUP_UI)
    texture.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_EDITOR_ICON)
    texture.set_editor_property("mip_gen_settings", unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS)
    texture.set_editor_property("never_stream", True)
    texture.set_editor_property("address_x", unreal.TextureAddress.TA_CLAMP)
    texture.set_editor_property("address_y", unreal.TextureAddress.TA_CLAMP)
    assert unreal.EditorAssetLibrary.save_loaded_asset(texture)
    rows.append({"source": filename, "source_sha256": hashlib.sha256((source / filename).read_bytes()).hexdigest(),
                 "asset": texture.get_path_name(), "requested_build_size": [width, height],
                 "source_import_observed_size": [texture.blueprint_get_size_x(), texture.blueprint_get_size_y()],
                 "opaque": True})
material = unreal.AssetToolsHelpers.get_asset_tools().create_asset("M_SanctuaryBackground", destination, unreal.Material, unreal.MaterialFactoryNew())
material.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_UNLIT)
material.set_editor_property("two_sided", True)
edit = unreal.MaterialEditingLibrary
sample = edit.create_material_expression(material, unreal.MaterialExpressionTextureSample, -350, 0)
sample.set_editor_property("texture", unreal.EditorAssetLibrary.load_asset(destination + "/T_SanctuaryBackground"))
assert edit.connect_material_property(sample, "RGB", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
edit.recompile_material(material)
assert unreal.EditorAssetLibrary.save_loaded_asset(material)
report.write_text(json.dumps({"engine": unreal.SystemLibrary.get_engine_version(), "textures": rows,
    "material": destination + "/M_SanctuaryBackground", "saved": True,
    "boundary": "Imported and saved only. Cooked dimensions, runtime rendering and owner acceptance are separate."}, indent=2))
unreal.log("WC_STORYBOOK_IMPORT_SAVED")

"""Import the race and class badges (art-source/ui/trait_icons_r001, drawn by tools/production/build_trait_icons.py)
as interface textures: no mip maps, no block compression. Re-running replaces them in place.

Run inside the editor: UnrealEditor.exe game/WonderChess.uproject -ExecutePythonScript=tools/unreal/import_trait_icons.py
"""
import json
from pathlib import Path

import unreal

root = Path(unreal.Paths.project_dir()).resolve().parent
source = root / "art-source/ui/trait_icons_r001"
folder = "/Game/WonderChess/VNext/UI/TraitIcons_r001"
files = [p for p in sorted(source.glob("*.png")) if p.stem != "preview"]
tasks = []
for path in files:
    task = unreal.AssetImportTask()
    task.filename, task.destination_path, task.destination_name = str(path), folder, "T_" + path.stem
    task.automated = task.replace_existing = task.save = True
    tasks.append(task)
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)
names = []
for path in files:
    texture = unreal.EditorAssetLibrary.load_asset(f"{folder}/T_{path.stem}")
    if not texture:
        raise RuntimeError(f"{path.name} did not import")
    texture.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_EDITOR_ICON)
    texture.set_editor_property("mip_gen_settings", unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS)
    texture.set_editor_property("lod_group", unreal.TextureGroup.TEXTUREGROUP_UI)
    texture.set_editor_property("never_stream", True)
    unreal.EditorAssetLibrary.save_loaded_asset(texture)
    names.append(texture.get_name())
report = root / "reports/vnext/environment/trait-icons-r001.json"
report.parent.mkdir(parents=True, exist_ok=True)
report.write_text(json.dumps({"folder": folder, "textures": names,
                              "boundary": "Generated candidate interface art in the owner-chosen direction; not approved in the game"}, indent=2))
unreal.SystemLibrary.quit_editor()

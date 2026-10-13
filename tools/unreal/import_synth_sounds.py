"""Import the synthesized sound set (art-source/audio/synth_r001) as sound waves; *_loop files are set to loop."""
import json
from pathlib import Path

import unreal

root = Path(unreal.Paths.project_dir()).resolve().parent
source = root / "art-source/audio/synth_r001"
folder = "/Game/WonderChess/VNext/Audio/Synth_r001"
tasks = []
for path in sorted(source.glob("*.wav")):
    task = unreal.AssetImportTask()
    task.filename, task.destination_path, task.destination_name = str(path), folder, "S_" + path.stem
    task.automated = task.replace_existing = task.save = True
    tasks.append(task)
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)
names = []
for path in sorted(source.glob("*.wav")):
    asset = unreal.EditorAssetLibrary.load_asset(f"{folder}/S_{path.stem}")
    if not asset:
        raise RuntimeError(f"{path.name} did not import")
    if path.stem.endswith("_loop"):
        asset.set_editor_property("looping", True)
    unreal.EditorAssetLibrary.save_loaded_asset(asset)
    names.append(asset.get_name())
report = root / "reports/vnext/environment/synth-sounds-r001.json"
report.parent.mkdir(parents=True, exist_ok=True)
report.write_text(json.dumps({"folder": folder, "sounds": names, "boundary": "Generated placeholder audio; not approved"}, indent=2))

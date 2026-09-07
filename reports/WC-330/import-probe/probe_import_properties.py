"""Verify installed editor-only FBX properties on transient objects only."""
from pathlib import Path
import json
import unreal

root = Path(unreal.Paths.project_dir()).resolve().parent
ui = unreal.FbxImportUI()
result = {"engine": unreal.SystemLibrary.get_engine_version(), "asset_mutations": False, "properties": []}
for obj, name, desired in (
    (ui.skeletal_mesh_import_data, "update_skeleton_reference_pose", True),
    (ui.anim_sequence_import_data, "preserve_local_transform", False),
):
    entry = {"class": obj.get_class().get_name(), "property": name}
    entry["before"] = obj.get_editor_property(name)
    obj.set_editor_property(name, desired)
    entry["after"] = obj.get_editor_property(name)
    entry["expected"] = desired
    entry["pass"] = entry["after"] == desired
    result["properties"].append(entry)
    if not entry["pass"]:
        raise RuntimeError("Property assignment did not round trip: " + name)
result["status"] = "PASS"
out = root / "reports/WC-330/import-probe/property-setter-results.json"
out.write_text(json.dumps(result, indent=2), encoding="utf-8")
unreal.log("WC_IMPORT_PROPERTY_PROBE " + json.dumps(result))

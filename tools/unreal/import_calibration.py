"""Measure the supplied FBX in the installed Unreal importer, never infer import scale."""
import json
from pathlib import Path
import unreal

root = Path(unreal.Paths.project_dir()).resolve().parent
unreal.SystemLibrary.execute_console_command(None, "Interchange.FeatureFlags.Import.FBX 0")
task = unreal.AssetImportTask()
task.filename = str(root / "exports/calibration/WC_Calibration.fbx")
task.destination_path = "/Game/WonderChess/Calibration"
task.automated = True
task.save = True
task.replace_existing = True
task.factory = unreal.FbxFactory()
options = unreal.FbxImportUI()
options.automated_import_should_detect_type = False
options.import_as_skeletal = False
options.mesh_type_to_import = unreal.FBXImportType.FBXIT_STATIC_MESH
options.import_materials = False
options.import_textures = False
options.static_mesh_import_data.combine_meshes = False
options.static_mesh_import_data.convert_scene = True
options.static_mesh_import_data.convert_scene_unit = True
options.static_mesh_import_data.force_front_x_axis = True
options.static_mesh_import_data.import_rotation = unreal.Rotator(pitch=0, yaw=180, roll=0)
task.options = options
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
records = []
for path in task.imported_object_paths:
    mesh = unreal.load_asset(path)
    if isinstance(mesh, unreal.StaticMesh):
        bounds = mesh.get_bounding_box()
        size = bounds.max - bounds.min
        records.append({"path": path, "dimensions_cm": [size.x, size.y, size.z], "min_cm": [bounds.min.x,bounds.min.y,bounds.min.z], "max_cm": [bounds.max.x,bounds.max.y,bounds.max.z]})
def dim(name):
    values = [r for r in records if name in r["path"]]
    if len(values) != 1:
        raise RuntimeError("Expected exactly one imported " + name)
    return values[0]["dimensions_cm"]
cube, tile, shaft = dim("Cube_1m"), dim("Tile_2m"), dim("ForwardY_Shaft")
shaft_record = next(r for r in records if "ForwardY_Shaft" in r["path"])
tip_record = next(r for r in records if "ForwardY_Tip" in r["path"])
checks = {"cube_100cm": all(abs(v-100)<.1 for v in cube), "tile_200cm": all(abs(v-200)<.1 for v in tile[:2]), "forward_axis_X": abs(shaft[0]-90)<.1, "forward_positive_X": sum(tip_record[k][0] for k in ("min_cm","max_cm")) > sum(shaft_record[k][0] for k in ("min_cm","max_cm"))}
cube_record = next(r for r in records if "Cube_1m" in r["path"])
checks['feet_zero_top_positive_Z'] = abs(cube_record['min_cm'][2])<.1 and abs(cube_record['max_cm'][2]-100)<.1
report = {"engine": unreal.SystemLibrary.get_engine_version(), "records": records, "checks": checks, "rig_animation_review": "NOT_RUN", "importer": "legacy FbxFactory; convert_scene and convert_scene_unit and force_front_x_axis enabled; import yaw 180 degrees applied once to the source basis"}
out = root / "reports/WC-330/calibration-unreal.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(report, indent=2)+"\n", encoding="utf-8")
if not all(checks.values()):
    raise RuntimeError("Calibration measurement failed: " + str(checks))
unreal.log("WC_CALIBRATION_MEASUREMENTS_PASS " + str(checks))

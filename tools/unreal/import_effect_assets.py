"""Import and measure the two authored centimeter projectile glyphs in UE."""
from pathlib import Path
import hashlib
import json
import os
import traceback
import unreal

ROOT = Path(unreal.Paths.project_dir()).resolve().parent
SOURCE = ROOT / "exports/effects"
FOLDER = "/Game/WonderChess/Effects"
REPORT_NAME = os.environ.get("WC_EFFECT_REPORT", "effect-import.json")
if Path(REPORT_NAME).name != REPORT_NAME or not REPORT_NAME.startswith("effect-import") or not REPORT_NAME.endswith(".json"):
    raise RuntimeError("Effect report must be an effect-import*.json filename")
REPORT = ROOT / "reports/WC-340" / REPORT_NAME
NAMES = ("SM_WC_ArrowGlyph", "SM_WC_BoltGlyph")
MATERIAL = "/Game/WonderChess/Materials/M_WC_Surface"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def measured_settings(data):
    for key, value in {
        "convert_scene": True,
        "convert_scene_unit": True,
        "force_front_x_axis": False,
        "import_rotation": unreal.Rotator(pitch=0, yaw=90, roll=0),
        "import_translation": unreal.Vector(0, 0, 0),
        "import_uniform_scale": 1.0,
        "combine_meshes": True,
        "auto_generate_collision": False,
        "generate_lightmap_u_vs": False,
        "build_nanite": False,
    }.items():
        data.set_editor_property(key, value)


def options():
    settings = unreal.FbxImportUI()
    settings.automated_import_should_detect_type = False
    settings.import_as_skeletal = False
    settings.import_mesh = True
    settings.import_animations = False
    settings.import_materials = False
    settings.import_textures = False
    settings.mesh_type_to_import = unreal.FBXImportType.FBXIT_STATIC_MESH
    measured_settings(settings.static_mesh_import_data)
    return settings


def vec(value):
    return [float(value.x), float(value.y), float(value.z)]


def main():
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    manifest_path = SOURCE / "projectile_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    source_records = {entry["mesh"]: entry for entry in manifest["records"]}
    result = {
        "engine": unreal.SystemLibrary.get_engine_version(),
        "status": "STARTED",
        "manifest_sha256": sha256(manifest_path),
        "material": MATERIAL,
        "preset": {"convert_scene": True, "convert_scene_unit": True,
                   "force_front_x_axis": False, "yaw_degrees": 90,
                   "uniform_scale": 1, "translation_cm": [0, 0, 0]},
        "records": [],
        "boundary": "Actual legacy static mesh import, saved assets and signed bounds; rendered flight and packaged use remain separate checks.",
    }
    REPORT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    try:
        unreal.SystemLibrary.execute_console_command(None, "Interchange.FeatureFlags.Import.FBX 0")
        unreal.SystemLibrary.execute_console_command(None, "Interchange.FeatureFlags.Import.Enable 0")
        material = unreal.load_asset(MATERIAL)
        if not isinstance(material, unreal.MaterialInterface):
            raise RuntimeError("Required existing surface material is missing")
        for name in NAMES:
            filename = SOURCE / (name + ".fbx")
            digest = sha256(filename)
            if digest != manifest["files"][filename.name]:
                raise RuntimeError("Source FBX does not match its authored manifest: " + name)
            source = source_records[name]
            destination = FOLDER + "/" + name
            if unreal.EditorAssetLibrary.does_asset_exist(destination):
                previous = unreal.load_asset(destination)
                if not isinstance(previous, unreal.StaticMesh):
                    raise RuntimeError("Existing destination is not a static mesh: " + destination)
                measured_settings(previous.get_editor_property("asset_import_data"))
            task = unreal.AssetImportTask()
            task.filename = str(filename)
            task.destination_path = FOLDER
            task.destination_name = name
            task.automated = True
            task.replace_existing = True
            task.replace_existing_settings = True
            task.save = True
            task.options = options()
            task.factory = unreal.FbxFactory()
            unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
            mesh = unreal.load_asset(destination)
            if not task.imported_object_paths or not isinstance(mesh, unreal.StaticMesh):
                raise RuntimeError("Expected static mesh was not imported: " + name)
            slots = mesh.get_editor_property("static_materials")
            if len(slots) != 1:
                raise RuntimeError("Glyph must have exactly one material slot: " + name)
            mesh.set_material(0, material)
            if not unreal.EditorAssetLibrary.save_loaded_asset(mesh):
                raise RuntimeError("Could not save imported glyph: " + name)
            box = mesh.get_bounding_box()
            lower, upper = vec(box.min), vec(box.max)
            dimensions = [upper[i] - lower[i] for i in range(3)]
            expected = [source["source_dimensions_m"][i] * 100 for i in (1, 0, 2)]
            tip = source["source_tip_m"][1] * 100
            tail = source["source_tail_m"][1] * 100
            checks = {
                "dimensions_match_cm": max(abs(a - b) for a, b in zip(dimensions, expected)) < 0.05,
                "long_axis_x": dimensions[0] > max(dimensions[1], dimensions[2]) * 3,
                "positive_x_tip_extent": abs(upper[0] - tip) < 0.05,
                "negative_x_tail_extent": abs(lower[0] - tail) < 0.05,
                "authored_triangle_count": mesh.get_num_triangles(0) == source["triangles"],
                "surface_material_assigned": mesh.get_material(0) == material,
            }
            asset_file = ROOT / "game/Content/WonderChess/Effects" / (name + ".uasset")
            result["records"].append({
                "mesh": destination,
                "source_sha256": digest,
                "uasset_sha256": sha256(asset_file),
                "min_cm": lower, "max_cm": upper,
                "dimensions_cm": dimensions, "expected_dimensions_cm": expected,
                "triangles": mesh.get_num_triangles(0),
                "checks": checks,
            })
            REPORT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
            if not all(checks.values()):
                raise RuntimeError("Imported glyph measurement failed: " + name)
            unreal.log("WC_EFFECT_IMPORTED " + name + " " + json.dumps(checks))
        result["status"] = "PASS"
        REPORT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        unreal.log("WC_EFFECT_IMPORT_PASS two saved glyphs; long axis and signed tip extents verified")
    except Exception:
        result["status"] = "FAIL"
        result["error"] = traceback.format_exc()
        REPORT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        raise


if __name__ == "__main__":
    main()

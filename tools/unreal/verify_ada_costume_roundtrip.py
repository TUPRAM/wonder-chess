"""Isolated same-asset Ada costume reimport, then a separate cold reference read.

Run only after the current performance/editor owner releases the editor lock.
WC_ADA_ROUNDTRIP_PHASE is import or cold; WC_ADA_ROUNDTRIP_RUN names a fresh run.
WC_ADA_ROUNDTRIP_MANIFEST names the art lane's source JSON. The import phase
creates only /Game/WonderChess/Verification/AdaRoundTrip/<run>/ assets. Cold
phase loads the saved map in another process and never saves any asset.
"""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import re
import runpy
import traceback


UID = "wc_u_human_guardian"
CLIPS = ("Idle", "Move", "Attack", "Active", "Hit", "Defeat", "Victory")
MOUNT_ROOT = "/Game/WonderChess/Verification/AdaRoundTrip"
REPORT_ROOT = Path("reports/WC-330/ada-costume-roundtrip")


def utc():
    return datetime.now(timezone.utc).isoformat()


def sha256(path):
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def scoped(root, path, allowed):
    path = Path(path)
    resolved = (root / path).resolve() if not path.is_absolute() else path.resolve()
    if not any(resolved.is_relative_to(folder.resolve()) for folder in allowed):
        raise ValueError("Path is outside the assigned roundtrip inputs: " + str(path))
    if not resolved.is_file():
        raise ValueError("Required roundtrip input is missing: " + str(resolved))
    return resolved


def differences(before, after):
    return {
        "modified": sorted(key for key in before.keys() & after.keys() if before[key] != after[key]),
        "deleted": sorted(before.keys() - after.keys()),
        "created": sorted(after.keys() - before.keys()),
    }


def protected_hashes(content):
    """Only this drill's isolated verification subtree is outside protection."""
    excluded = content / "WonderChess/Verification/AdaRoundTrip"
    output = {}
    for path in sorted(content.rglob("*")):
        if path.is_file():
            resolved = path.resolve()
            if not resolved.is_relative_to(content):
                raise ValueError("Content file resolves outside project: " + str(path))
            if not resolved.is_relative_to(excluded):
                output[path.relative_to(content).as_posix()] = sha256(path)
    return output


def object_path(value):
    return value.get_path_name() if value else None


def mesh_metrics(unreal, mesh):
    subsystem = unreal.get_editor_subsystem(unreal.SkeletalMeshEditorSubsystem)
    count = int(subsystem.get_num_verts(mesh, 0))
    lods = int(subsystem.get_lod_count(mesh))
    bounds = mesh.get_bounds()
    result = {
        "lod0_vertices": count,
        "lod_count": lods,
        "bounds_origin_cm": [float(bounds.origin.x), float(bounds.origin.y), float(bounds.origin.z)],
        "bounds_extent_cm": [float(bounds.box_extent.x), float(bounds.box_extent.y), float(bounds.box_extent.z)],
    }
    if count <= 0 or lods <= 0 or not all(math.isfinite(x) for x in result["bounds_extent_cm"]):
        raise RuntimeError("Imported mesh has invalid measured geometry")
    return result


def material_paths(mesh):
    return [object_path(slot.get_editor_property("material_interface"))
            for slot in mesh.get_editor_property("materials")]


def dirty_production_packages(unreal):
    return sorted(package.get_path_name()
                  for package in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()
                  if package.get_path_name().startswith("/Game/")
                  and not package.get_path_name().startswith(MOUNT_ROOT + "/"))


def load_production(unreal):
    folder = "/Game/WonderChess/Heroes/" + UID
    mesh = unreal.load_asset(folder + "/SK_" + UID)
    if not isinstance(mesh, unreal.SkeletalMesh):
        raise RuntimeError("The actual production Ada mesh is required")
    skeleton = mesh.get_editor_property("skeleton")
    if not isinstance(skeleton, unreal.Skeleton):
        raise RuntimeError("The existing saved production Skeleton is required")
    materials = material_paths(mesh)
    if not materials or any(value is None for value in materials):
        raise RuntimeError("Production material references must be complete")
    sequences = {}
    for clip in CLIPS:
        sequence = unreal.load_asset(folder + "/AN_" + UID + "_" + clip)
        if not isinstance(sequence, unreal.AnimSequence) or sequence.get_editor_property("skeleton") != skeleton:
            raise RuntimeError("Missing/incompatible production animation " + clip)
        sequences[clip] = sequence
    return mesh, skeleton, sequences, materials


def actor_snapshot(unreal, mesh, skeleton, sequences):
    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
    selected = {actor.get_actor_label(): actor for actor in actors
                if actor.get_actor_label().startswith("WC_RoundTrip_")}
    expected = {"WC_RoundTrip_" + clip for clip in CLIPS}
    if set(selected) != expected:
        raise RuntimeError("Saved verification map must contain exactly seven named clip actors")
    rows, references = [], []
    for clip in CLIPS:
        actor = selected["WC_RoundTrip_" + clip]
        if not isinstance(actor, unreal.SkeletalMeshActor):
            raise RuntimeError("Verification actor class changed: " + clip)
        component = actor.get_editor_property("skeletal_mesh_component")
        animation = component.get_editor_property("animation_data").get_editor_property("anim_to_play")
        if component.get_skeletal_mesh_asset() != mesh or animation != sequences[clip]:
            raise RuntimeError("Placed component lost its mesh or saved animation reference: " + clip)
        if animation.get_editor_property("skeleton") != skeleton:
            raise RuntimeError("Animation Skeleton reference changed: " + clip)
        rows.append({
            "clip": clip, "actor": actor.get_path_name(), "component": component.get_path_name(),
            "mesh": mesh.get_path_name(), "skeleton": skeleton.get_path_name(),
            "animation": animation.get_path_name(),
            "materials": [object_path(component.get_material(index))
                          for index in range(component.get_num_materials())],
            "location": [float(actor.get_actor_location().x), float(actor.get_actor_location().y),
                         float(actor.get_actor_location().z)],
        })
        references.append((actor, component, animation))
    return rows, references


def import_into_duplicate(unreal, helpers, source, folder, mesh, skeleton):
    """Do not call task(): its production path forces a Skeleton pose refresh."""
    options = helpers["fbx_settings"]("skeletal", skeleton)
    settings = options.get_editor_property("skeletal_mesh_import_data")
    existing = mesh.get_editor_property("asset_import_data")
    if existing is None or existing.get_outer() != mesh:
        raise RuntimeError("Duplicate import data is not owned by the isolated duplicate")
    for data in (settings, existing):
        for name, value in {
            "convert_scene": True, "convert_scene_unit": True,
            "force_front_x_axis": False,
            "import_rotation": unreal.Rotator(pitch=0, yaw=90, roll=0),
            "import_translation": unreal.Vector(0, 0, 0), "import_uniform_scale": 1.0,
            "update_skeleton_reference_pose": False, "use_t0_as_ref_pose": False,
        }.items():
            data.set_editor_property(name, value)
    job = unreal.AssetImportTask()
    for name, value in {
        "filename": str(source), "destination_path": folder, "destination_name": mesh.get_name(),
        "automated": True, "replace_existing": True, "replace_existing_settings": True,
        "save": False, "options": options, "factory": unreal.FbxFactory(),
    }.items():
        job.set_editor_property(name, value)
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([job])
    paths = list(job.get_editor_property("imported_object_paths"))
    if paths != [mesh.get_path_name()]:
        raise RuntimeError("Import returned another asset or extra objects: " + repr(paths))
    imported = unreal.load_asset(paths[0])
    if imported != mesh or imported.get_editor_property("skeleton") != skeleton:
        raise RuntimeError("Same-asset reimport changed mesh identity or Skeleton reference")
    saved_data = imported.get_editor_property("asset_import_data")
    if saved_data.get_editor_property("update_skeleton_reference_pose"):
        raise RuntimeError("Importer enabled the prohibited Skeleton reference update")
    return imported


def main():
    import unreal

    root = Path(unreal.Paths.project_dir()).resolve().parent
    content = (root / "game/Content").resolve()
    directory = root / REPORT_ROOT
    directory.mkdir(parents=True, exist_ok=True)
    run_id = os.environ.get("WC_ADA_ROUNDTRIP_RUN", "run_v1")
    if re.fullmatch(r"[a-z0-9][a-z0-9_-]{0,47}", run_id) is None:
        raise ValueError("Run ID must be a simple lowercase name")
    phase = os.environ.get("WC_ADA_ROUNDTRIP_PHASE", "import")
    if phase not in ("import", "cold"):
        raise ValueError("WC_ADA_ROUNDTRIP_PHASE must be import or cold")
    report_path = directory / (run_id + "-" + phase + ".json")
    if report_path.exists():
        raise RuntimeError("Preserve previous report; choose another run ID: " + str(report_path))
    folder = MOUNT_ROOT + "/" + run_id
    mesh_path = folder + "/SK_AdaRoundTrip"
    map_path = folder + "/L_AdaRoundTrip"
    mesh_file = content / (mesh_path[len("/Game/"):] + ".uasset")
    map_file = content / (map_path[len("/Game/"):] + ".umap")
    report = {
        "status": "STARTED", "phase": phase, "run_id": run_id, "started_utc": utc(),
        "process_id": os.getpid(), "engine": unreal.SystemLibrary.get_engine_version(),
        "script_sha256": sha256(Path(__file__)), "mesh": mesh_path, "map": map_path,
        "boundary": "Isolated uncooked verification duplicate/map. Production mesh, Skeleton, materials, seven clips and every other Content file are protected; no production asset save is requested.",
        "visual_acceptance": "NOT_RUN", "packaged_production_change": False,
    }
    before = None
    caught = None

    def persist():
        report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    persist()
    try:
        before = protected_hashes(content)
        report["protected_files_before"] = before
        production, skeleton, sequences, materials = load_production(unreal)
        dirty_before = dirty_production_packages(unreal)
        report["production_references"] = {
            "mesh": production.get_path_name(), "skeleton": skeleton.get_path_name(),
            "materials": materials, "animations": {clip: value.get_path_name() for clip, value in sequences.items()},
        }
        report["dirty_production_packages_before"] = dirty_before
        levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
        if phase == "import":
            raw_manifest = os.environ.get("WC_ADA_ROUNDTRIP_MANIFEST", str(REPORT_ROOT / "source-change-manifest.json"))
            manifest_path = scoped(root, raw_manifest, [directory])
            manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
            if manifest.get("unit_id") != UID or not manifest.get("change_description"):
                raise ValueError("Source manifest must name Ada and its authored costume change")
            if (manifest.get("status") != "BLENDER_EXECUTED_UNREAL_ROUNDTRIP_PENDING"
                    or manifest.get("production_files_preserved") is not True
                    or manifest.get("source_unchanged_original_vertices") is not True
                    or manifest.get("source_unchanged_original_weights_and_uvs") is not True
                    or manifest.get("clip_count_unchanged") != 7):
                raise ValueError("Actual Blender source/invariant checks must pass before Unreal import")
            source_paths = {}
            for key in ("baseline_fbx", "changed_fbx"):
                source = scoped(root, manifest[key], [directory, root / "exports/heroes" / UID])
                if source.suffix.lower() != ".fbx" or sha256(source) != manifest[key + "_sha256"]:
                    raise ValueError("Source FBX/hash does not match " + key)
                source_paths[key] = source
            if source_paths["baseline_fbx"] == source_paths["changed_fbx"] or manifest["baseline_fbx_sha256"] == manifest["changed_fbx_sha256"]:
                raise ValueError("The changed costume requires distinct source bytes")
            minimum = manifest.get("expected_min_vertex_count_increase", 1)
            if isinstance(minimum, bool) or not isinstance(minimum, int) or minimum < 1:
                raise ValueError("Expected minimum added vertex count must be a positive integer")
            if unreal.EditorAssetLibrary.does_asset_exist(mesh_path) or unreal.EditorAssetLibrary.does_asset_exist(map_path):
                raise RuntimeError("Never overwrite prior verification assets; choose a new run ID")
            report.update({"source_manifest": str(manifest_path), "source_manifest_sha256": sha256(manifest_path),
                           "source_inputs": manifest})
            helper_path = root / "tools/unreal/import_alpha_assets.py"
            report["import_helper_sha256"] = sha256(helper_path)
            helpers = runpy.run_path(str(helper_path), run_name="wc_roundtrip_helpers")
            duplicate = unreal.EditorAssetLibrary.duplicate_asset(production.get_path_name(), mesh_path)
            if not isinstance(duplicate, unreal.SkeletalMesh):
                raise RuntimeError("Could not duplicate production Ada into the isolated package")
            duplicate = import_into_duplicate(unreal, helpers, source_paths["baseline_fbx"], folder, duplicate, skeleton)
            if material_paths(duplicate) != materials:
                raise RuntimeError("Baseline import did not preserve original material references")
            if not unreal.EditorAssetLibrary.save_loaded_asset(duplicate):
                raise RuntimeError("Cannot save isolated baseline mesh")
            if not levels.new_level(map_path):
                raise RuntimeError("Cannot create isolated verification map")
            actor_system = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
            for index, clip in enumerate(CLIPS):
                actor = actor_system.spawn_actor_from_class(unreal.SkeletalMeshActor, unreal.Vector(index * 240, 0, 0))
                if actor is None:
                    raise RuntimeError("Could not place verification actor " + clip)
                actor.set_actor_label("WC_RoundTrip_" + clip)
                component = actor.get_editor_property("skeletal_mesh_component")
                component.set_skeletal_mesh_asset(duplicate)
                component.override_animation_data(sequences[clip], True, False, 0.0, 1.0)
            if not levels.save_current_level():
                raise RuntimeError("Cannot save verification actor references before reimport")
            prior_rows, prior_objects = actor_snapshot(unreal, duplicate, skeleton, sequences)
            prior_metrics = mesh_metrics(unreal, duplicate)
            prior_mesh_hash = sha256(mesh_file)
            report.update({"references_before": prior_rows, "geometry_before": prior_metrics,
                           "baseline_saved_mesh_sha256": prior_mesh_hash, "baseline_map_sha256": sha256(map_file)})
            persist()
            changed = import_into_duplicate(unreal, helpers, source_paths["changed_fbx"], folder, duplicate, skeleton)
            after_rows, after_objects = actor_snapshot(unreal, changed, skeleton, sequences)
            after_metrics = mesh_metrics(unreal, changed)
            if prior_rows != after_rows or prior_objects != after_objects:
                raise RuntimeError("Placed actor/component/material/animation references changed during reimport")
            if material_paths(changed) != materials:
                raise RuntimeError("Mesh material references changed during costume reimport")
            if after_metrics["lod_count"] != prior_metrics["lod_count"]:
                raise RuntimeError("Reimport changed the duplicate's LOD count")
            if after_metrics["lod0_vertices"] - prior_metrics["lod0_vertices"] < minimum:
                raise RuntimeError("The expected costume geometry addition was not measured in Unreal")
            if not unreal.EditorAssetLibrary.save_loaded_asset(changed) or not levels.save_current_level():
                raise RuntimeError("Could not save changed verification mesh/map")
            after_mesh_hash = sha256(mesh_file)
            if after_mesh_hash == prior_mesh_hash:
                raise RuntimeError("Same-path changed mesh file did not change")
            for key, source in source_paths.items():
                if sha256(source) != manifest[key + "_sha256"]:
                    raise RuntimeError("Art source changed during the isolated import")
            report.update({"references_after": after_rows, "geometry_after": after_metrics,
                           "same_objects_preserved": True, "changed_saved_mesh_sha256": after_mesh_hash,
                           "saved_map_sha256": sha256(map_file), "cold_reload": "PENDING_SEPARATE_PROCESS"})
        else:
            import_report_path = directory / (run_id + "-import.json")
            imported = json.loads(import_report_path.read_text(encoding="utf-8"))
            if imported.get("status") != "PASS_IMPORT_ONLY_COLD_PENDING" or imported["process_id"] == os.getpid():
                raise RuntimeError("Cold validation needs a successful import from another process")
            if imported["protected_files_after"] != before:
                raise RuntimeError("Production Content changed between import and cold validation")
            if sha256(mesh_file) != imported["changed_saved_mesh_sha256"] or sha256(map_file) != imported["saved_map_sha256"]:
                raise RuntimeError("Isolated mesh/map bytes changed before cold validation")
            if not levels.load_level(map_path):
                raise RuntimeError("Cannot cold-load the saved verification map")
            mesh = unreal.load_asset(mesh_path)
            rows, _ = actor_snapshot(unreal, mesh, skeleton, sequences)
            metrics = mesh_metrics(unreal, mesh)
            if rows != imported["references_after"] or metrics != imported["geometry_after"]:
                raise RuntimeError("Cold-loaded references or costume geometry differ from saved result")
            if mesh.get_editor_property("skeleton") != skeleton or material_paths(mesh) != materials:
                raise RuntimeError("Cold mesh lost original Skeleton/material references")
            report.update({"import_report": str(import_report_path), "import_report_sha256": sha256(import_report_path),
                           "references_cold": rows, "geometry_cold": metrics,
                           "saved_mesh_sha256": sha256(mesh_file), "saved_map_sha256": sha256(map_file),
                           "cold_reload": "PASS_SEPARATE_PROCESS", "no_asset_save_requested": True})
        dirty_after = dirty_production_packages(unreal)
        report["dirty_production_packages_after"] = dirty_after
        if set(dirty_after) - set(dirty_before):
            raise RuntimeError("Importer newly dirtied a protected production package")
    except Exception:
        caught = traceback.format_exc()
    finally:
        if before is not None:
            try:
                after = protected_hashes(content)
                changes = differences(before, after)
                report.update({"protected_files_after": after, "protected_differences": changes,
                               "protected_unchanged": not any(changes.values())})
                if any(changes.values()):
                    caught = (caught or "") + "\nProtected production Content changed: " + json.dumps(changes)
            except Exception:
                caught = (caught or "") + "\nProtected Content check failed:\n" + traceback.format_exc()
        report["status"] = "FAIL" if caught else ("PASS_IMPORT_ONLY_COLD_PENDING" if phase == "import" else "PASS_COLD_REFERENCES_PRODUCTION_UNCHANGED")
        report["ended_utc"] = utc()
        if caught:
            report["error"] = caught
        persist()
    if caught:
        unreal.log_error(caught)
        raise RuntimeError("Isolated Ada roundtrip failed: " + str(report_path))
    unreal.log("WC_ADA_ROUNDTRIP_" + phase.upper() + "_PASS " + str(report_path))


if __name__ == "__main__":
    main()

"""Import or cold-check Ada's isolated AQ1 candidate in Unreal Editor.

Required environment: WC_AQ1_EXPORT, WC_AQ1_SOURCE_BLEND, WC_AQ1_REVISION,
WC_AQ1_REPORT, WC_AQ1_NORMAL_GREEN (keep|flip). WC_AQ1_OPERATION defaults to
import; cold also requires WC_AQ1_PRIOR_REPORT and performs no asset saves.
All Content outside this one revision is
hashed before/after. This tool does not promote a candidate or certify its art.
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
MOUNT = "/Game/WonderChess/Candidates/AQ1"


def digest(path):
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def inside(path, base):
    resolved = Path(path).resolve()
    if not resolved.is_relative_to(base.resolve()):
        raise ValueError("Path escapes candidate ownership: " + str(path))
    return resolved


def preflight(root, environ):
    source_root = root / "art-source/heroes" / UID / "candidates/AQ1"
    source = inside(environ["WC_AQ1_SOURCE_BLEND"], source_root)
    if source.suffix != ".blend" or not source.is_file():
        raise ValueError("A saved AQ1 candidate .blend is required")
    export = inside(environ["WC_AQ1_EXPORT"], root)
    canonical_export = (root / "exports/heroes" / UID).resolve()
    if export == canonical_export:
        raise ValueError("Canonical exports are not candidate inputs")
    revision = environ["WC_AQ1_REVISION"]
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]{0,63}", revision):
        raise ValueError("Revision must be a simple asset-folder identifier")
    operation = environ.get("WC_AQ1_OPERATION", "import")
    if operation not in ("import", "cold"):
        raise ValueError("WC_AQ1_OPERATION must be import or cold")
    green = environ["WC_AQ1_NORMAL_GREEN"]
    if green not in ("keep", "flip"):
        raise ValueError("Declare normal green-channel interpretation as keep or flip")
    report = inside(environ["WC_AQ1_REPORT"], root / "reports")
    if report.suffix != ".json" or report.exists():
        raise ValueError("A fresh .json report path under reports is required")
    manifest_path = export / "export_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    if manifest.get("unit_id") != UID or manifest.get("source_sha256") != digest(source):
        raise ValueError("Candidate source identity/hash differs from export manifest")
    if set(manifest.get("clips", {})) != set(CLIPS) or manifest.get("fps") != 60:
        raise ValueError("Candidate must retain seven named clips authored at60fps")
    names = [f"SK_{UID}.fbx"] + [f"AN_{UID}_{clip}.fbx" for clip in CLIPS]
    names += [f"T_{UID}_{kind}.png" for kind in ("BaseColor", "ORM", "Normal")]
    hashes = manifest.get("files", {})
    for name in names:
        path = inside(export / name, export)
        if not path.is_file() or hashes.get(name) != digest(path):
            raise ValueError("Missing or changed frozen candidate export: " + name)
    if manifest.get("units_source_sha256") != digest(root / "data/units.json"):
        raise ValueError("Candidate manifest must identify the current canonical units data")
    return source, export, revision, operation, green, report, manifest, names


def protected_hashes(root, revision):
    content = (root / "game/Content").resolve()
    excluded = content / "WonderChess/Candidates/AQ1" / revision
    result = {}
    for path in sorted(content.rglob("*")):
        if path.is_file():
            resolved = inside(path, content)
            if not resolved.is_relative_to(excluded):
                result[path.relative_to(content).as_posix()] = digest(path)
    return result


def changed(before, after):
    return {
        "modified": sorted(key for key in before.keys() & after.keys() if before[key] != after[key]),
        "created": sorted(after.keys() - before.keys()),
        "deleted": sorted(before.keys() - after.keys()),
    }


def candidate_hashes(root, revision):
    directory = root / "game/Content/WonderChess/Candidates/AQ1" / revision
    return {path.relative_to(directory).as_posix(): digest(path)
            for path in sorted(directory.rglob("*")) if path.is_file()}


def owned(asset, folder):
    if asset is None or not asset.get_path_name().startswith(folder + "/"):
        raise RuntimeError("Asset reference escapes this AQ1 revision: " + str(asset))
    return asset


def save(unreal, asset, folder):
    owned(asset, folder)
    if not unreal.EditorAssetLibrary.save_loaded_asset(asset, only_if_is_dirty=False):
        raise RuntimeError("Could not save candidate asset: " + asset.get_path_name())


def candidate_material(unreal, helpers, export, folder, green):
    textures = {}
    for kind in ("BaseColor", "ORM", "Normal"):
        name = f"T_{UID}_{kind}"
        texture = helpers["task"](export / (name + ".png"), folder, name)[0]
        owned(texture, folder)
        texture.set_editor_property("srgb", kind == "BaseColor")
        if kind == "Normal":
            texture.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_NORMALMAP)
            texture.set_editor_property("flip_green_channel", green == "flip")
        else:
            texture.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_DEFAULT)
        save(unreal, texture, folder)
        textures[kind] = texture
    name = "M_AQ1_Ada"
    master = unreal.load_asset(folder + "/" + name)
    if master is None:
        master = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
            name, folder, unreal.Material, unreal.MaterialFactoryNew())
    owned(master, folder)
    editing = unreal.MaterialEditingLibrary
    # Refresh existing graphs after texture reimport as well as on first creation.
    # The slots below are the three parameter nodes authored by this importer.
    for index, (kind, prop, sampler) in enumerate((
        ("BaseColor", unreal.MaterialProperty.MP_BASE_COLOR, unreal.MaterialSamplerType.SAMPLERTYPE_COLOR),
        ("ORM", unreal.MaterialProperty.MP_ROUGHNESS, unreal.MaterialSamplerType.SAMPLERTYPE_LINEAR_COLOR),
        ("Normal", unreal.MaterialProperty.MP_NORMAL, unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL),
    )):
        sample = editing.get_material_property_input_node(master, prop)
        if sample is None:
            sample = editing.create_material_expression(master, unreal.MaterialExpressionTextureSampleParameter2D, -500, index * 250)
        elif not isinstance(sample, unreal.MaterialExpressionTextureSampleParameter2D):
            raise RuntimeError("Candidate material graph differs from its owned atlas graph: " + kind)
        sample.set_editor_property("parameter_name", kind)
        sample.set_editor_property("texture", textures[kind])
        sample.set_editor_property("sampler_type", sampler)
        sample.set_editor_property("const_coordinate", 0)
        connections = (("R", unreal.MaterialProperty.MP_AMBIENT_OCCLUSION),
                       ("G", unreal.MaterialProperty.MP_ROUGHNESS),
                       ("B", unreal.MaterialProperty.MP_METALLIC)) if kind == "ORM" else (("RGB", prop),)
        for channel, target in connections:
            if not editing.connect_material_property(sample, channel, target):
                raise RuntimeError("Could not connect candidate atlas material: " + kind)
    editing.set_material_usage(master, unreal.MaterialUsage.MATUSAGE_SKELETAL_MESH)
    editing.recompile_material(master)
    save(unreal, master, folder)
    name = "MI_" + UID
    material = unreal.load_asset(folder + "/" + name)
    if material is None:
        material = unreal.AssetToolsHelpers.get_asset_tools().create_asset(name, folder, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    owned(material, folder)
    unreal.MaterialEditingLibrary.set_material_instance_parent(material, master)
    for kind, texture in textures.items():
        unreal.MaterialEditingLibrary.set_material_instance_texture_parameter_value(material, kind, texture)
    editing.update_material_instance(material)
    save(unreal, material, folder)
    return material


def import_assets(unreal, root, export, folder, green, manifest):
    helpers = runpy.run_path(str(root / "tools/unreal/import_alpha_assets.py"), run_name="aq1_helpers")
    material = candidate_material(unreal, helpers, export, folder, green)
    mesh = unreal.load_asset(folder + "/SK_" + UID)
    prior_mesh = mesh
    skeleton = owned(mesh.skeleton, folder) if mesh else None
    prior_skeleton = skeleton
    options = helpers["fbx_settings"]("skeletal", skeleton)
    options.skeletal_mesh_import_data.set_editor_property("normal_import_method", unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS)
    options.skeletal_mesh_import_data.set_editor_property("normal_generation_method", unreal.FBXNormalGenerationMethod.MIKK_T_SPACE)
    options.skeletal_mesh_import_data.set_editor_property("use_t0_as_ref_pose", False)
    # Same-path reimport must use the declared current interpretation as well.
    if mesh:
        data = mesh.get_editor_property("asset_import_data")
        data.set_editor_property("normal_import_method", unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS)
        data.set_editor_property("normal_generation_method", unreal.FBXNormalGenerationMethod.MIKK_T_SPACE)
    imported = helpers["task"](export / f"SK_{UID}.fbx", folder, "SK_" + UID, options, unreal.FbxFactory())
    meshes = [asset for asset in imported if isinstance(asset, unreal.SkeletalMesh)]
    if len(meshes) != 1:
        raise RuntimeError("Expected one imported skeletal mesh")
    mesh = owned(meshes[0], folder)
    skeleton = owned(mesh.skeleton, folder)
    if prior_mesh and (mesh != prior_mesh or skeleton != prior_skeleton):
        raise RuntimeError("Same-path candidate reimport changed mesh/skeleton identity")
    # FBX reimport preserves section indexes and can append a renamed source slot.
    # Truncating Materials here leaves sections pointing past the array. Retain
    # imported slot names/indices and bind every existing slot to the one atlas.
    slots = list(mesh.get_editor_property("materials"))
    if not slots:
        raise RuntimeError("Imported candidate has no material slots")
    imported_slots = [str(slot.get_editor_property("material_slot_name")) for slot in slots]
    for slot in slots:
        slot.set_editor_property("material_interface", material)
    mesh.set_editor_property("materials", slots)
    save(unreal, mesh, folder)
    save(unreal, skeleton, folder)
    units = json.loads((root / "data/units.json").read_text(encoding="utf-8"))["units"]
    unit = next(value for value in units if value["id"] == UID)
    attack_plan = helpers["window_contract"]["attack_window_plan"](manifest["clips"]["Attack"], manifest["fps"], unit["stats"]["attack_windup_ms"])
    for clip in CLIPS:
        name = f"AN_{UID}_{clip}"
        imported = helpers["task"](export / (name + ".fbx"), folder, name, helpers["fbx_settings"]("animation", skeleton), unreal.FbxFactory())
        sequences = [asset for asset in imported if isinstance(asset, unreal.AnimSequence)]
        if len(sequences) != 1:
            raise RuntimeError("Expected one imported clip: " + clip)
        sequence = owned(sequences[0], folder)
        if sequence.get_editor_property("skeleton") != skeleton:
            raise RuntimeError("Candidate animation skeleton mismatch: " + clip)
        if clip == "Attack":
            helpers["install_attack_windows"](sequence, attack_plan)
        save(unreal, sequence, folder)
    return {"reimport": prior_mesh is not None, "retained_imported_material_slots": imported_slots,
            "same_mesh_identity": mesh == prior_mesh if prior_mesh else None,
            "same_skeleton_identity": skeleton == prior_skeleton if prior_skeleton else None}


def inspect_assets(unreal, folder, manifest):
    mesh = owned(unreal.load_asset(folder + "/SK_" + UID), folder)
    if not isinstance(mesh, unreal.SkeletalMesh):
        raise RuntimeError("Candidate skeletal mesh not found")
    skeleton = owned(mesh.skeleton, folder)
    subsystem = unreal.get_editor_subsystem(unreal.SkeletalMeshEditorSubsystem)
    bounds = mesh.get_bounds()
    extent = [float(bounds.box_extent.x), float(bounds.box_extent.y), float(bounds.box_extent.z)]
    if not all(math.isfinite(value) and value > 0 for value in extent):
        raise RuntimeError("Invalid imported bounds")
    poses = unreal.AnimPoseExtensions
    reference = poses.get_reference_pose(skeleton)
    bones = [str(name) for name in poses.get_bone_names(reference)]
    required = ("root", "head", "foot_l", "foot_r", "weapon_l", "weapon_r", "cast_origin", "head_ui")
    if any(name not in bones for name in required):
        raise RuntimeError("Candidate rig is missing a required bone/socket")
    result = {
        "mesh": mesh.get_path_name(), "skeleton": skeleton.get_path_name(), "bones": bones,
        "lod0_render_vertices": int(subsystem.get_num_verts(mesh, 0)),
        "lod_count": int(subsystem.get_lod_count(mesh)), "bounds_extent_cm": extent,
        "bounds_origin_cm": [float(bounds.origin.x), float(bounds.origin.y), float(bounds.origin.z)],
        "materials": [owned(slot.material_interface, folder).get_path_name() for slot in mesh.materials],
        "required_reference_bones": {}, "clips": [],
    }
    material = owned(unreal.load_asset(folder + "/MI_" + UID), folder)
    master = owned(unreal.load_asset(folder + "/M_AQ1_Ada"), folder)
    if material.get_editor_property("parent") != master:
        raise RuntimeError("Candidate atlas material has a different parent")
    slots = list(mesh.get_editor_property("materials"))
    result["material_slots"] = [{
        "index": index, "slot_name": str(slot.get_editor_property("material_slot_name")),
        "imported_slot_name": str(slot.get_editor_property("imported_material_slot_name")),
        "material": owned(slot.material_interface, folder).get_path_name(),
    } for index, slot in enumerate(slots)]
    result["lod_sections"] = []
    for lod in range(result["lod_count"]):
        count = int(subsystem.get_num_sections(mesh, lod))
        if count <= 0:
            raise RuntimeError("Candidate LOD has no rendered sections")
        for section in range(count):
            slot = int(subsystem.get_lod_material_slot(mesh, lod, section))
            if not 0 <= slot < len(slots):
                raise RuntimeError(f"LOD {lod} section {section} references invalid material slot {slot}/{len(slots)}")
            if slots[slot].material_interface != material:
                raise RuntimeError(f"LOD {lod} section {section} does not use the candidate atlas")
            result["lod_sections"].append({"lod": lod, "section": section, "material_slot": slot,
                                           "material": material.get_path_name()})
    editing = unreal.MaterialEditingLibrary
    result["atlas_material_graph"] = {"master": master.get_path_name(), "instance": material.get_path_name(),
        "skeletal_mesh_usage": bool(editing.has_material_usage(master, unreal.MaterialUsage.MATUSAGE_SKELETAL_MESH)),
        "parameters": {}}
    if not result["atlas_material_graph"]["skeletal_mesh_usage"]:
        raise RuntimeError("Candidate material lacks skeletal mesh shader usage")
    for kind, prop, sampler in (
        ("BaseColor", unreal.MaterialProperty.MP_BASE_COLOR, unreal.MaterialSamplerType.SAMPLERTYPE_COLOR),
        ("ORM", unreal.MaterialProperty.MP_ROUGHNESS, unreal.MaterialSamplerType.SAMPLERTYPE_LINEAR_COLOR),
        ("Normal", unreal.MaterialProperty.MP_NORMAL, unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL),
    ):
        texture = owned(unreal.load_asset(folder + f"/T_{UID}_{kind}"), folder)
        node = editing.get_material_property_input_node(master, prop)
        if not isinstance(node, unreal.MaterialExpressionTextureSampleParameter2D):
            raise RuntimeError("Missing candidate atlas input node: " + kind)
        if str(node.get_editor_property("parameter_name")) != kind or node.get_editor_property("texture") != texture:
            raise RuntimeError("Candidate atlas input refers to the wrong texture: " + kind)
        if node.get_editor_property("sampler_type") != sampler or int(node.get_editor_property("const_coordinate")) != 0:
            raise RuntimeError("Candidate atlas sampler/UV channel differs: " + kind)
        if editing.get_material_instance_texture_parameter_value(material, kind) != texture:
            raise RuntimeError("Candidate material instance texture override differs: " + kind)
        result["atlas_material_graph"]["parameters"][kind] = {
            "texture": texture.get_path_name(), "sampler": str(node.get_editor_property("sampler_type")),
            "uv_channel": int(node.get_editor_property("const_coordinate")),
            "output": str(editing.get_material_property_input_node_output_name(master, prop)),
        }
    data = mesh.get_editor_property("asset_import_data")
    result["saved_normal_import_method"] = str(data.get_editor_property("normal_import_method"))
    result["saved_normal_generation_method"] = str(data.get_editor_property("normal_generation_method"))
    result["textures"] = {}
    for kind in ("BaseColor", "ORM", "Normal"):
        texture = owned(unreal.load_asset(folder + f"/T_{UID}_{kind}"), folder)
        result["textures"][kind] = {
            "asset": texture.get_path_name(), "srgb": bool(texture.get_editor_property("srgb")),
            "compression": str(texture.get_editor_property("compression_settings")),
            "flip_green_channel": bool(texture.get_editor_property("flip_green_channel")),
        }
        if result["textures"][kind]["srgb"] != (kind == "BaseColor"):
            raise RuntimeError("Saved texture color-space interpretation differs from contract: " + kind)
    for name in required:
        value = poses.get_ref_bone_pose(reference, name, unreal.AnimPoseSpaces.WORLD)
        result["required_reference_bones"][name] = [float(value.translation.x), float(value.translation.y), float(value.translation.z)]
    # Detect the prior meter/centimeter failure instead of masking it with actor scale.
    if not 100 <= result["required_reference_bones"]["head"][2] <= 200:
        raise RuntimeError("Head height is outside the adult Ada centimeter range")
    if any(abs(value) > .001 for value in result["required_reference_bones"]["root"]):
        raise RuntimeError("Candidate root is not at the ground origin")
    for clip in CLIPS:
        sequence = owned(unreal.load_asset(folder + f"/AN_{UID}_{clip}"), folder)
        if not isinstance(sequence, unreal.AnimSequence) or sequence.get_editor_property("skeleton") != skeleton:
            raise RuntimeError("Missing or incompatible clip " + clip)
        duration = float(sequence.sequence_length)
        frames = manifest["clips"][clip]["frames"]
        expected = (frames[1] - frames[0]) / manifest["fps"]
        if abs(duration - expected) > 1 / manifest["fps"] + .00001:
            raise RuntimeError("Imported clip duration changed: " + clip)
        samples = []
        options = unreal.AnimPoseEvaluationOptions()
        options.evaluation_type = unreal.AnimDataEvalType.COMPRESSED
        options.should_retarget = False
        options.extract_root_motion = False
        options.optional_skeletal_mesh = mesh
        for fraction in (0, .25, .5, .75, 1):
            pose = poses.get_anim_pose_at_time(sequence, duration * fraction, options)
            if not poses.is_valid(pose):
                raise RuntimeError("Invalid evaluated candidate pose")
            sample = {"time": duration * fraction, "bones": {}}
            for name in required:
                value = poses.get_bone_pose(pose, name, unreal.AnimPoseSpaces.WORLD)
                sample["bones"][name] = [float(value.translation.x), float(value.translation.y), float(value.translation.z)]
            samples.append(sample)
        result["clips"].append({"clip": clip, "asset": sequence.get_path_name(), "duration_seconds": duration, "expected_duration_seconds": expected, "compressed_samples": samples})
    return result


def main():
    import unreal
    root = Path(unreal.Paths.project_dir()).resolve().parent
    source, export, revision, operation, green, output, manifest, names = preflight(root, os.environ)
    folder = MOUNT + "/" + revision
    output.parent.mkdir(parents=True, exist_ok=True)
    before = protected_hashes(root, revision)
    report = {
        "status": "STARTED", "started_utc": datetime.now(timezone.utc).isoformat(),
        "engine": unreal.SystemLibrary.get_engine_version(), "pid": os.getpid(),
        "operation": operation, "candidate_folder": folder, "source": str(source),
        "source_sha256": digest(source), "export_manifest_sha256": digest(export / "export_manifest.json"),
        "script_sha256": digest(Path(__file__)), "normal_green_channel": green,
        "normal_tangent_method": "Import FBX vertex normals; compute MikkTSpace tangents",
        "normal_orientation_visual_test": "PENDING_ASYMMETRIC_RENDER_COMPARISON",
        "lod_generation": "NOT_REQUESTED_BEFORE_LOD0_ART_APPROVAL",
        "continuous_animation_review": "NOT_PERFORMED_BY_POSE_SAMPLER",
        "crowded_game_capture": "NOT_PERFORMED_BY_IMPORTER", "art_acceptance": "PRAM_REVIEW_PENDING",
        "protected_files_before": before,
    }
    def persist():
        output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    persist()
    error = None
    try:
        if operation == "import":
            report.update(import_assets(unreal, root, export, folder, green, manifest))
        report["measurements"] = inspect_assets(unreal, folder, manifest)
        report["candidate_files"] = candidate_hashes(root, revision)
        if operation == "cold":
            prior_path = inside(os.environ["WC_AQ1_PRIOR_REPORT"], root / "reports")
            prior = json.loads(prior_path.read_text(encoding="utf-8"))
            if prior.get("status") != "PASS_IMPORT_STRUCTURE_VISUAL_REVIEW_PENDING" or prior["pid"] == os.getpid():
                raise RuntimeError("Cold verification needs a successful import from another editor process")
            for key in ("candidate_folder", "source_sha256", "export_manifest_sha256", "normal_green_channel", "candidate_files", "measurements"):
                if report[key] != prior[key]:
                    raise RuntimeError("Cold candidate differs from persisted import: " + key)
            report["cold_reference_validation"] = "PASS_SEPARATE_PROCESS_MATCH"
            report["prior_report_sha256"] = digest(prior_path)
        for name in names:
            if digest(export / name) != manifest["files"][name]:
                raise RuntimeError("Export changed during editor operation: " + name)
        if digest(source) != manifest["source_sha256"]:
            raise RuntimeError("Candidate source changed during editor operation")
    except Exception:
        error = traceback.format_exc()
    finally:
        after = protected_hashes(root, revision)
        differences = changed(before, after)
        report.update({"protected_files_after": after, "protected_differences": differences,
                       "protected_unchanged": not any(differences.values())})
        if any(differences.values()):
            error = (error or "") + "\nProtected Content changed: " + json.dumps(differences)
        report["status"] = "FAIL" if error else "PASS_" + operation.upper() + "_STRUCTURE_VISUAL_REVIEW_PENDING"
        report["ended_utc"] = datetime.now(timezone.utc).isoformat()
        if error:
            report["error"] = error
        persist()
    if error:
        unreal.log_error(error)
        raise RuntimeError("AQ1 candidate operation failed; inspect " + str(output))
    unreal.log("WC_AQ1_IMPORT " + report["status"] + " " + str(output))


if __name__ == "__main__":
    main()

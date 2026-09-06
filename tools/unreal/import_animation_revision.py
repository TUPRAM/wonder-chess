"""Reimport an explicit animation-only revision with protected Content hashes.

Run in Unreal's Python commandlet. WC_IMPORT_ANIMATION_LIST names a JSON array
of workspace-relative exports/heroes/<alpha-id>/AN_<alpha-id>_<clip>.fbx paths.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import math
import os
from pathlib import Path, PureWindowsPath
import runpy
import traceback


CLIPS = frozenset(("Idle", "Move", "Attack", "Active", "Hit", "Defeat", "Victory"))
PACKAGE_SUFFIXES = frozenset((".uasset", ".uexp", ".ubulk", ".uptnl"))


def utc():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_plan(root, list_path):
    """Validate all inputs before editor import helpers can mutate any asset."""
    root = root.resolve()
    list_path = (root / list_path).resolve()
    if not list_path.is_relative_to(root) or not list_path.is_file():
        raise ValueError("Animation list must be an existing file inside this workspace")
    entries = json.loads(list_path.read_text(encoding="utf-8-sig"))
    if not isinstance(entries, list) or not 1 <= len(entries) <= 84:
        raise ValueError("Animation list must be a nonempty JSON array of at most 84 paths")
    rules = json.loads((root / "data/rules.alpha.json").read_text(encoding="utf-8-sig"))
    alpha = rules["alpha_unit_ids"]
    if len(alpha) != 12 or len(set(alpha)) != 12:
        raise ValueError("Canonical profile must contain exactly twelve unique alpha IDs")
    plan, seen = [], set()
    for entry in entries:
        if not isinstance(entry, str) or not entry or entry != entry.strip():
            raise ValueError("Every animation source must be a nonempty path string")
        windows_path = PureWindowsPath(entry)
        parts = entry.replace("\\", "/").split("/")
        if windows_path.drive or windows_path.root or len(parts) != 4:
            raise ValueError("Source must be a direct workspace-relative hero export: " + entry)
        if parts[:2] != ["exports", "heroes"] or parts[2] not in alpha:
            raise ValueError("Source is outside the canonical alpha hero exports: " + entry)
        uid, filename = parts[2:]
        prefix = "AN_" + uid + "_"
        if not filename.startswith(prefix) or not filename.endswith(".fbx"):
            raise ValueError("Source must be a canonical animation FBX: " + entry)
        clip = filename[len(prefix):-4]
        if clip not in CLIPS:
            raise ValueError("Unknown required animation clip: " + entry)
        source = (root / "exports/heroes" / uid / filename).resolve()
        expected_parent = root / "exports/heroes" / uid
        if source.parent != expected_parent or not source.is_file():
            raise ValueError("Missing source or resolved source escapes its hero folder: " + entry)
        key = str(source).casefold()
        if key in seen:
            raise ValueError("Duplicate animation source: " + entry)
        seen.add(key)
        manifest_path = source.parent / "export_manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
        digest = sha256(source)
        if manifest.get("unit_id") != uid or manifest.get("files", {}).get(filename) != digest:
            raise ValueError("Source differs from the authored export manifest: " + entry)
        name = source.stem
        folder = "/Game/WonderChess/Heroes/" + uid
        plan.append({
            "source": source.relative_to(root).as_posix(),
            "source_sha256": digest,
            "manifest_sha256": sha256(manifest_path),
            "unit_id": uid,
            "clip": clip,
            "name": name,
            "folder": folder,
            "asset": folder + "/" + name,
            "package": "WonderChess/Heroes/" + uid + "/" + name,
        })
    return list_path, plan


def content_hashes(content, target_packages):
    protected, targets = {}, {}
    for path in sorted(content.rglob("*")):
        if not path.is_file():
            continue
        resolved = path.resolve()
        if not resolved.is_relative_to(content):
            raise ValueError("Content file resolves outside the project: " + str(path))
        relative = path.relative_to(content).as_posix()
        target = path.suffix.lower() in PACKAGE_SUFFIXES and any(
            relative.startswith(package + ".") for package in target_packages
        )
        (targets if target else protected)[relative] = sha256(path)
    return protected, targets


def differences(before, after):
    return {
        "modified": sorted(key for key in before.keys() & after.keys() if before[key] != after[key]),
        "deleted": sorted(before.keys() - after.keys()),
        "created": sorted(after.keys() - before.keys()),
    }


def main():
    import unreal

    root = Path(unreal.Paths.project_dir()).resolve().parent
    content = (root / "game/Content").resolve()
    report_path = root / "reports/WC-330/animation-revision-import.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    if report_path.exists():
        stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        previous = report_path.with_name("animation-revision-import-" + stamp + "-previous.json")
        previous.write_bytes(report_path.read_bytes())
    report = {
        "status": "STARTED", "started_utc": utc(),
        "engine": unreal.SystemLibrary.get_engine_version(),
        "process_id": os.getpid(),
        "script_sha256": sha256(Path(__file__)),
        "cold_reload_validation": "PENDING_SEPARATE_PROCESS",
        "visual_acceptance": "NOT_RUN",
        "boundary": "Listed existing AnimSequences only; saved file hashes and in-process references. No mesh, skeleton, LOD, material, texture or map save is requested.",
        "records": [], "transitions": [{"status": "STARTED", "utc": utc()}],
    }

    def save_report():
        report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    save_report()
    before, target_packages = None, set()
    caught = None
    try:
        raw_list = os.environ.get("WC_IMPORT_ANIMATION_LIST", "")
        if not raw_list:
            raise ValueError("WC_IMPORT_ANIMATION_LIST must name the approved JSON path array")
        list_path, plan = read_plan(root, Path(raw_list))
        report.update({"list_path": str(list_path), "list_sha256": sha256(list_path),
                       "requested_count": len(plan), "plan": plan})
        target_packages = {entry["package"] for entry in plan}
        before, prior_targets = content_hashes(content, target_packages)
        report.update({"protected_files_before": before, "target_files_before": prior_targets})
        save_report()

        # Validate every destination before task() updates saved import options.
        references = {}
        for entry in plan:
            expected = entry["asset"] + "." + entry["name"]
            sequence = unreal.load_asset(entry["asset"])
            mesh = unreal.load_asset(entry["folder"] + "/SK_" + entry["unit_id"])
            if not isinstance(sequence, unreal.AnimSequence) or sequence.get_path_name() != expected:
                raise RuntimeError("Required existing AnimSequence is missing/wrong: " + entry["asset"])
            if not isinstance(mesh, unreal.SkeletalMesh):
                raise RuntimeError("Required existing skeletal mesh is missing: " + entry["unit_id"])
            skeleton = sequence.get_editor_property("skeleton")
            if not isinstance(skeleton, unreal.Skeleton) or skeleton != mesh.get_editor_property("skeleton"):
                raise RuntimeError("Existing sequence/mesh skeleton references differ: " + entry["asset"])
            skeleton_package = skeleton.get_path_name().split(".", 1)[0]
            if not skeleton_package.startswith("/Game/"):
                raise RuntimeError("Skeleton must already be saved in this project: " + skeleton_package)
            skeleton_file = content / (skeleton_package[len("/Game/"):] + ".uasset")
            target_file = content / (entry["package"] + ".uasset")
            if not skeleton_file.is_file() or not target_file.is_file():
                raise RuntimeError("Sequence and skeleton must both exist on disk: " + entry["asset"])
            references[entry["asset"]] = (sequence, skeleton, float(sequence.sequence_length))

        helper_path = root / "tools/unreal/import_alpha_assets.py"
        report["import_helper_sha256"] = sha256(helper_path)
        helpers = runpy.run_path(str(helper_path), run_name="wc_animation_revision_helpers")
        for entry in plan:
            source = root / entry["source"]
            if sha256(source) != entry["source_sha256"]:
                raise RuntimeError("Source changed after preflight: " + entry["source"])
            previous_sequence, skeleton, previous_length = references[entry["asset"]]
            imported = helpers["task"](
                source, entry["folder"], entry["name"],
                helpers["fbx_settings"]("animation", skeleton), unreal.FbxFactory(),
            )
            expected = entry["asset"] + "." + entry["name"]
            if len(imported) != 1 or not isinstance(imported[0], unreal.AnimSequence):
                raise RuntimeError("Import must return only its one existing animation: " + entry["asset"])
            sequence = imported[0]
            if sequence.get_path_name() != expected or sequence != previous_sequence:
                raise RuntimeError("Import changed the existing animation identity/path: " + expected)
            if sequence.get_editor_property("skeleton") != skeleton:
                raise RuntimeError("Import changed the animation skeleton reference: " + expected)
            length = float(sequence.sequence_length)
            if not math.isfinite(length) or length <= 0:
                raise RuntimeError("Imported animation has invalid duration: " + expected)
            if not unreal.EditorAssetLibrary.save_loaded_asset(sequence):
                raise RuntimeError("Failed to persist listed animation: " + expected)
            report["records"].append({
                "source": entry["source"], "source_sha256": entry["source_sha256"],
                "asset": expected, "skeleton": skeleton.get_path_name(),
                "identity_preserved": True, "skeleton_reference_preserved": True,
                "previous_length_seconds": previous_length, "length_seconds": length,
                "saved_asset_sha256": sha256(content / (entry["package"] + ".uasset")),
            })
            save_report()
            unreal.log("WC_ANIMATION_REVISION_IMPORTED " + expected)
        for entry in plan:
            if sha256(root / entry["source"]) != entry["source_sha256"]:
                raise RuntimeError("Authored source changed during import: " + entry["source"])
    except Exception:
        caught = traceback.format_exc()
    finally:
        if before is not None:
            try:
                after, target_after = content_hashes(content, target_packages)
                changed = differences(before, after)
                report.update({"protected_files_after": after, "protected_differences": changed,
                               "protected_unchanged": not any(changed.values()),
                               "target_files_after": target_after})
                if any(changed.values()):
                    caught = (caught or "") + "\nProtected Content changed: " + json.dumps(changed)
            except Exception:
                caught = (caught or "") + "\nProtected hash verification failed:\n" + traceback.format_exc()
        report["status"] = "FAIL" if caught else "PASS_IMPORT_ONLY_COLD_PENDING"
        report["ended_utc"] = utc()
        report["transitions"].append({"status": report["status"], "utc": report["ended_utc"]})
        if caught:
            report["error"] = caught
        save_report()
    if caught:
        unreal.log_error(caught)
        raise RuntimeError("Animation revision import failed; inspect " + str(report_path))
    unreal.log("WC_ANIMATION_REVISION_IMPORT_PASS " + str(len(report["records"])) +
               " animations; protected Content hashes unchanged; cold validation pending")


if __name__ == "__main__":
    main()

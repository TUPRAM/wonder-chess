"""Snapshot canonical asset readiness without promoting files into artistic approval.

Pass explicit importer JSON reports with --import-report (repeatable). Cold-load
reports without source/export hashes remain unbound. --output is a new directory.
"""
from __future__ import annotations
import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOT_ASSESSED = "NOT_ASSESSED_BY_THIS_REPORT"


def scoped(path, base=ROOT):
    path = Path(path)
    resolved = (path if path.is_absolute() else ROOT / path).resolve()
    if not resolved.is_relative_to(base.resolve()):
        raise ValueError(f"Path outside authorized workspace area: {path}")
    return resolved


def sha(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def relative(path):
    return path.relative_to(ROOT).as_posix()


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def file_record(path):
    exists = path.is_file()
    return {"path": relative(path), "present": exists,
            "sha256": sha(path) if exists else None,
            "bytes": path.stat().st_size if exists else None}


def asset_file(folder, name):
    if not folder.startswith("/Game/"):
        raise ValueError("Only this project's /Game assets are supported")
    return scoped(ROOT / "game/Content" / folder.removeprefix("/Game/") / (name + ".uasset"))


def collect_imports(paths):
    records, evidence = [], []
    for raw in paths:
        path = scoped(raw, ROOT / "reports")
        value = read(path)
        if not isinstance(value, dict):
            raise ValueError(f"Expected explicit importer report object: {path}")
        evidence.append({**file_record(path), "engine": value.get("engine"), "passed": value.get("passed"),
                         "boundary": value.get("boundary"), "utc": value.get("utc")})
        for family in ("heroes", "neutrals"):
            for entry in value.get(family, []):
                if isinstance(entry, dict) and entry.get("id"):
                    records.append((path, value, entry))
    return records, evidence


def report_asset(definition, family, imports):
    uid = definition["id"]
    paths = definition["asset_paths"]
    source = file_record(scoped(paths["blender"]))
    export_dir = scoped(paths["mesh_fbx"]).parent
    manifest_path = export_dir / "export_manifest.json"
    manifest_info = file_record(manifest_path)
    manifest = read(manifest_path) if manifest_info["present"] else {}
    errors = []
    if manifest and manifest.get("unit_id") != uid:
        errors.append("Export manifest identity mismatch")
    source_status = "MISSING" if not source["present"] else "UNKNOWN_NO_MANIFEST_HASH"
    if source["present"] and manifest.get("source_sha256"):
        source_status = "PASS" if source["sha256"] == manifest["source_sha256"] else "FAIL"
    clips = definition["animation_contract"]["required_clips"]
    required = [f"SK_{uid}.fbx", f"SK_{uid}_LOD1.fbx", f"SK_{uid}_LOD2.fbx", "portrait.png"]
    required += [f"T_{uid}_{kind}.png" for kind in ("BaseColor", "Normal", "ORM")]
    required += [f"AN_{uid}_{clip}.fbx" for clip in clips]
    declared = manifest.get("files", {})
    if not isinstance(declared, dict):
        raise ValueError(f"Invalid manifest files mapping: {uid}")
    exports = {}
    for name in sorted(set(required) | set(declared)):
        path = scoped(export_dir / name, export_dir)
        item = file_record(path)
        expected = declared.get(name)
        item["manifest_sha256"] = expected
        item["hash_status"] = ("MISSING" if not item["present"] else "UNKNOWN_UNLISTED" if not expected
                               else "PASS" if item["sha256"] == expected else "FAIL")
        exports[name] = item
    export_status = ("MISSING_MANIFEST" if not manifest else
                     "PASS" if all(item["hash_status"] == "PASS" for item in exports.values()) and not errors else "INCOMPLETE_OR_MISMATCH")
    folder = paths["unreal_folder"]
    imported = {"mesh": file_record(asset_file(folder, f"SK_{uid}")),
                "skeleton": file_record(asset_file(folder, f"SK_{uid}_Skeleton")),
                "portrait": file_record(asset_file(folder, f"T_{uid}_Portrait")),
                "material_instance": file_record(asset_file(folder, f"MI_{uid}")),
                "textures": {kind: file_record(asset_file(folder, f"T_{uid}_{kind}")) for kind in ("BaseColor", "Normal", "ORM")}}
    candidates, bound = [], []
    for path, container, entry in imports:
        if entry["id"] != uid:
            continue
        report_manifest = entry.get("export_manifest_sha256", entry.get("manifest_sha256"))
        report_source = entry.get("source_sha256")
        status = "UNKNOWN_UNBOUND_REPORT"
        if report_source and report_manifest:
            status = "PASS_SOURCE_EXPORT_HASH_MATCH" if (report_source == source["sha256"] and report_manifest == manifest_info["sha256"]
                     and source_status == "PASS" and export_status == "PASS" and not errors) else "STALE_OR_MISMATCH"
        explicit_import = str(entry.get("status", "")).startswith("IMPORTED")
        if container.get("passed") is False and status != "UNKNOWN_UNBOUND_REPORT":
            status = "REPORT_OVERALL_FAILED"
        candidates.append({"report": relative(path), "binding": status, "source_revision": entry.get("source_revision"),
                           "declared_status": entry.get("status"), "report_passed": container.get("passed"),
                           "explicit_import_record": explicit_import})
        if status == "PASS_SOURCE_EXPORT_HASH_MATCH" and explicit_import:
            bound.append((path, entry))
    rows = []
    for clip in clips:
        export = exports[f"AN_{uid}_{clip}.fbx"]
        spec = manifest.get("clips", {}).get(clip, {})
        content = file_record(asset_file(folder, f"AN_{uid}_{clip}"))
        expected_path = folder + f"/AN_{uid}_{clip}"
        matching = []
        for path, entry in bound:
            for record in entry.get("clips", []):
                if (record.get("name") == clip and record.get("path", "").split(".")[0] == expected_path
                        and float(record.get("length", record.get("seconds", 0))) > 0):
                    matching.append(relative(path))
        rows.append({"family": family, "id": uid, "display_name": definition.get("display_name", definition.get("name")),
                     "clip": clip, "source_revision": manifest.get("source_revision"),
                     "animation_revision": manifest.get("animation_revision"), "source_hash_status": source_status,
                     "manifest_clip_present": bool(spec), "authored_frames": spec.get("frames"), "release_frame": spec.get("release_frame"),
                     "export_hash_status": export["hash_status"], "export_sha256": export["sha256"],
                     "content_file_present": content["present"], "content_sha256": content["sha256"], "content_path": content["path"],
                     "matching_import_reports": matching, "import_report_matches_current_source_export": bool(matching),
                     "current_content_binary_bound_to_import_report": "UNKNOWN_IMPORTER_REPORT_HAS_NO_BINARY_HASH",
                     "continuous_visual_approval": NOT_ASSESSED, "audio_approval": NOT_ASSESSED, "performance_approval": NOT_ASSESSED})
    record = {"id": uid, "family": family, "display_name": definition.get("display_name", definition.get("name")),
              "source": source, "source_hash_status": source_status, "manifest": manifest_info,
              "source_revision": manifest.get("source_revision"), "geometry_revision": manifest.get("geometry_source_revision"),
              "animation_revision": manifest.get("animation_revision"), "rig_family": manifest.get("rig_family"),
              "export_hash_status": export_status, "exports": exports, "imported_files": imported,
              "import_reports": candidates, "import_report_matches_current_source_export": bool(bound),
              "required_clips": clips, "errors": errors, "open_reviews_from_manifest": manifest.get("open_reviews", []),
              "finished_asset_approval": NOT_ASSESSED, "continuous_visual_approval": NOT_ASSESSED,
              "audio_approval": NOT_ASSESSED, "performance_approval": NOT_ASSESSED}
    return record, rows


def csv_write(path, rows):
    with path.open("x", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        for row in rows:
            writer.writerow({key: json.dumps(value) if isinstance(value, (list, dict)) else value for key, value in row.items()})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="New output directory inside reports")
    parser.add_argument("--import-report", type=Path, action="append", default=[], help="Explicit importer or cold-load JSON report; repeatable")
    args = parser.parse_args()
    output = scoped(args.output, ROOT / "reports")
    if output.exists():
        raise ValueError("Refusing to overwrite existing asset evidence; choose a new output directory")
    rules = read(ROOT / "data/rules.alpha.json")
    unit_by_id = {unit["id"]: unit for unit in read(ROOT / "data/units.json")["units"]}
    ids = rules["alpha_unit_ids"]
    if len(ids) != 24 or len(set(ids)) != 24:
        raise ValueError("Expected adopted 24 distinct canonical hero IDs")
    heroes = [unit_by_id[uid] for uid in ids]
    neutrals = read(ROOT / "data/neutrals.json")["creatures"]
    if len(neutrals) != 7 or len({item["id"] for item in neutrals}) != 7:
        raise ValueError("Expected seven canonical neutral definitions")
    imports, evidence = collect_imports(args.import_report)
    records, hero_rows, neutral_rows = [], [], []
    for family, definitions, rows in (("hero", heroes, hero_rows), ("neutral", neutrals, neutral_rows)):
        for definition in definitions:
            record, clips = report_asset(definition, family, imports)
            records.append(record)
            rows.extend(clips)
    if len(hero_rows) != 168:
        raise ValueError("Canonical hero animation contracts must produce exactly168 rows")
    totals = {"heroes": 24, "hero_clip_rows": len(hero_rows), "neutrals": 7, "neutral_clip_rows": len(neutral_rows),
              "hero_sources_present": sum(item["source"]["present"] for item in records if item["family"] == "hero"),
              "hero_export_hash_pass": sum(item["export_hash_status"] == "PASS" for item in records if item["family"] == "hero"),
              "hero_import_reports_match_current": sum(item["import_report_matches_current_source_export"] for item in records if item["family"] == "hero"),
              "hero_clips_present_in_content": sum(row["content_file_present"] for row in hero_rows),
              "neutral_export_hash_pass": sum(item["export_hash_status"] == "PASS" for item in records if item["family"] == "neutral"),
              "neutral_import_reports_match_current": sum(item["import_report_matches_current_source_export"] for item in records if item["family"] == "neutral")}
    value = {"status": "INVENTORY_EXECUTED_ACCEPTANCE_NOT_INFERRED", "utc": datetime.now(timezone.utc).isoformat(),
             "schema_version": rules["schema_version"], "balance_version": rules["balance_version"],
             "script_sha256": sha(Path(__file__)), "canonical_inputs": [file_record(ROOT / "data" / name) for name in ("rules.alpha.json", "units.json", "neutrals.json")],
             "totals": totals, "missing_hero_source_ids": [item["id"] for item in records if item["family"] == "hero" and not item["source"]["present"]],
             "import_evidence": evidence, "assets": records,
             "boundaries": ["Files are hashed from canonical source/export/Content paths only. Candidate and failed-run movie folders are never searched.",
                            "Importer source/export hash agreement does not bind current Unreal binary bytes unless an importer recorded their hashes.",
                            "Cold-load reports without source/export hashes are explicitly unbound. Presence alone does not prove a valid loaded asset.",
                            "All continuous visual, audio, frame-time and finished-art approvals remain unassessed by this inventory.",
                            "Run while asset lanes are frozen; this filesystem snapshot is not an atomic Unreal asset transaction."]}
    output.mkdir(parents=True, exist_ok=False)
    (output / "asset-readiness.json").write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    csv_write(output / "hero-clips-168.csv", hero_rows)
    csv_write(output / "neutral-clips.csv", neutral_rows)
    print(json.dumps({"output": str(output), **totals, "missing_hero_source_ids": value["missing_hero_source_ids"]}, indent=2))


if __name__ == "__main__":
    main()

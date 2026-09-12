"""Capture immutable package/source/data/art identity after an explicit successful UAT report.

Read-only inputs; the sole output is a newly created JSON file under reports.
Run after all owners freeze inputs. This records identity, never gameplay acceptance.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]


def utc(timestamp=None):
    value = datetime.now(timezone.utc) if timestamp is None else datetime.fromtimestamp(timestamp, timezone.utc)
    return value.isoformat()


def scoped(path, folder=ROOT):
    value = Path(path)
    value = (ROOT / value).resolve() if not value.is_absolute() else value.resolve()
    if not value.is_relative_to(folder.resolve()):
        raise ValueError(f"Path is outside the permitted folder {folder}: {value}")
    return value


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--package", required=True, help="Actual folder containing top-level WonderChess.exe")
    parser.add_argument("--package-report", required=True, help="Specific completed UAT JSON report")
    parser.add_argument("--configuration", choices=("Development", "Shipping"), default="Shipping")
    parser.add_argument("--profile", choices=("alpha_24", "wonder_vnext"), default="alpha_24")
    parser.add_argument("--output", required=True, help="New immutable JSON path under reports")
    parser.add_argument("--runtime-only", action="store_true", help="Early slice: capture runtime inputs; art-source acceptance and export checks remain separate")
    args = parser.parse_args()
    if args.profile == "wonder_vnext" and not args.runtime_only:
        parser.error("Successor art/export acceptance is separate; use --runtime-only for the laboratory")
    package = scoped(args.package, ROOT / "builds")
    report_path = scoped(args.package_report, ROOT / "reports")
    output = scoped(args.output, ROOT / "reports")
    if output.exists():
        raise ValueError("Refusing to overwrite existing provenance: " + str(output))
    report = read_json(report_path)
    if (report.get("exit_code") != 0 or report.get("configuration") != args.configuration
            or report.get("packaging_status") != "tool_returned_success_launch_not_verified"):
        raise ValueError("Specified package report is not successful for the requested configuration")
    completed = datetime.fromisoformat(report["utc"].replace("Z", "+00:00")).timestamp()
    log_path = scoped(report_path.parent / report["log_file"], report_path.parent)
    log_bytes = log_path.read_bytes()
    log_encoding = "utf-16" if log_bytes.startswith((b"\xff\xfe", b"\xfe\xff")) else "utf-8-sig"
    log = log_bytes.decode(log_encoding, errors="replace")
    normalized_log = log.replace("\\", "/").casefold()
    possible_archives = (package, package.parent) if package.name == "Windows" else (package,)
    if ("-archivedirectory=" not in normalized_log
            or not any(str(path).replace("\\", "/").casefold() in normalized_log for path in possible_archives)
            or "BUILD SUCCESSFUL" not in log or "ExitCode=0" not in log):
        raise ValueError("Successful package log does not identify this archive and completion")
    launcher = package / "WonderChess.exe"
    binary_name = "WonderChess-Win64-Shipping.exe" if args.configuration == "Shipping" else "WonderChess.exe"
    binary = package / "WonderChess/Binaries/Win64" / binary_name
    receipt_path = ROOT / "game/Binaries/Win64" / (Path(binary_name).stem + ".target")
    receipt = read_json(receipt_path)
    if receipt.get("Configuration") != args.configuration or receipt.get("TargetName") != "WonderChess":
        raise ValueError("Build receipt does not match WonderChess and requested configuration")
    if not launcher.is_file() or not binary.is_file():
        raise ValueError("Actual packaged launcher/game executable is absent")

    started = utc()
    records = {}
    stamps = {}
    directory_sets = {}

    def capture(path, group, built_input=False):
        path = scoped(path)
        if path in records:
            return records[path]
        before = path.stat()
        if built_input and before.st_mtime > completed + 1:
            raise ValueError(f"Build input modified after package completion: {path}")
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(4 * 1024 * 1024), b""):
                digest.update(chunk)
        after = path.stat()
        stamp = (after.st_size, after.st_mtime_ns)
        if stamp != (before.st_size, before.st_mtime_ns):
            raise ValueError(f"Input changed while hashing: {path}")
        stamps[path] = stamp
        records[path] = {"group": group, "path": str(path),
                         "workspace_relative_path": path.relative_to(ROOT).as_posix(),
                         "bytes": after.st_size, "modified_utc": utc(after.st_mtime),
                         "sha256": digest.hexdigest()}
        return records[path]

    def tree(directory, group, built_input=False, skip_saved=False):
        directory = scoped(directory)
        if not directory.is_dir():
            raise ValueError("Required source/content directory missing: " + str(directory))
        def members():
            return {path.resolve() for path in directory.rglob("*") if path.is_file()
                    and "__pycache__" not in path.parts
                    and not (skip_saved and "Saved" in path.relative_to(directory).parts)}
        paths = members()
        directory_sets[directory] = (paths, members)
        for path in sorted(paths):
            capture(path, group, built_input)

    capture(report_path, "packaging_evidence")
    capture(log_path, "packaging_evidence")
    capture(receipt_path, "build_receipt")
    capture(ROOT / "game/WonderChess.uproject", "project_descriptor", True)
    tree(ROOT / "game/Source", "game_source", True)
    tree(ROOT / "game/Config", "game_config", True)
    tree(ROOT / "game/Content/WonderChess/SourceData", "staged_source_data", True)
    tree(ROOT / "game/Content", "game_content", True)
    tree(ROOT / "data", "canonical_data")
    tree(ROOT / "generated", "generated_data")
    if not args.runtime_only:
        tree(ROOT / "tools", "authoring_and_build_tools")
    tree(package, "packaged_payload", skip_saved=True)
    capture(Path(__file__), "provenance_tool")
    source_binary = capture(ROOT / "game/Binaries/Win64" / binary_name, "built_executable", True)
    if source_binary["sha256"] != capture(binary, "packaged_payload")["sha256"]:
        raise ValueError("Packaged game binary differs from current build output")
    for path in sorted((ROOT / "game/Intermediate/Build/Win64/x64/WonderChess" / args.configuration).rglob("*.rsp")):
        capture(path, "compiler_response_file")

    stage_path = ROOT / "game/Content/WonderChess/SourceData/runtime_stage_manifest.json"
    stage = read_json(stage_path)
    active_comparisons = []
    active_digest = stage["catalog_digest"]
    if args.profile == "wonder_vnext":
        active_path = ROOT / "game/Content/WonderChess/VNextData/runtime_catalog.json"
        active = read_json(active_path)
        authored = capture(ROOT / "data/vnext/catalog.json", "canonical_data")
        generated = capture(ROOT / "data/vnext/generated/runtime_catalog.json", "generated_data")
        staged_active = capture(active_path, "staged_source_data", True)
        if (active.get("profile_id") != "wonder_vnext" or active.get("source_sha256") != authored["sha256"]
                or staged_active["sha256"] != generated["sha256"]):
            raise ValueError("Successor source/generated/staged identities differ")
        active_digest = active["source_sha256"]
        active_comparisons.append({"source": authored["path"], "source_sha256": active_digest,
                                   "generated": generated["path"], "staged": staged_active["path"],
                                   "runtime_sha256": staged_active["sha256"], "matches": True})
    alpha_ids = read_json(ROOT / "data/rules.alpha.json")["alpha_unit_ids"]
    if stage["alpha_unit_ids"] != alpha_ids or len(alpha_ids) != 24 or len(set(alpha_ids)) != 24:
        raise ValueError("Staged alpha roster does not match the twenty-four canonical IDs")
    comparisons = []
    for name, declared in sorted(stage["files"].items()):
        staged = capture(scoped(stage_path.parent / name, stage_path.parent), "staged_source_data")
        canonical = capture(scoped(declared["source"]), "canonical_or_generated_data")
        matches = declared["sha256"] == staged["sha256"] == canonical["sha256"]
        if not matches:
            raise ValueError("Canonical/generated/staged bytes differ: " + name)
        comparisons.append({"staged_relative_path": name, "source": declared["source"],
                            "declared_sha256": declared["sha256"], "matches": matches})

    art_comparisons = []
    neutral_comparisons = []
    if not args.runtime_only:
        for unit_id in stage["alpha_unit_ids"]:
            folder = scoped(ROOT / "exports/heroes" / unit_id, ROOT / "exports/heroes")
            manifest_path = folder / "export_manifest.json"
            manifest = read_json(manifest_path)
            if manifest["unit_id"] != unit_id:
                raise ValueError("Hero export identity mismatch: " + unit_id)
            capture(manifest_path, "hero_export_manifest")
            source = capture(ROOT / "art-source/heroes" / unit_id / (unit_id + ".blend"), "authored_hero_source")
            if source["sha256"] != manifest["source_sha256"]:
                raise ValueError("Hero source differs from export manifest: " + unit_id)
            current_units_hash = capture(ROOT / "data/units.json", "canonical_data")["sha256"]
            files = []
            for name, expected in sorted(manifest["files"].items()):
                row = capture(scoped(folder / name, folder), "authored_hero_export")
                if row["sha256"] != expected:
                    raise ValueError("Hero export differs from manifest: " + row["path"])
                files.append(name)
            art_comparisons.append({"unit_id": unit_id, "source_sha256": source["sha256"],
                                    "source_revision": manifest.get("source_revision"),
                                    "canonical_units_sha256_at_export": manifest.get("units_source_sha256"),
                                    "canonical_units_sha256_at_capture": current_units_hash,
                                    "canonical_snapshot_unchanged": current_units_hash == manifest.get("units_source_sha256"),
                                    "canonical_boundary": "Historical export provenance is retained across display-name and balance metadata changes. Current animation/timing/identity compatibility requires separate imported-asset tests.",
                                    "export_files": files, "matches": True})
        for neutral in read_json(ROOT / "data/neutrals.json")["creatures"]:
            unit_id = neutral["id"]
            folder = scoped(ROOT / "exports/neutrals" / unit_id, ROOT / "exports/neutrals")
            manifest_path = folder / "export_manifest.json"
            manifest = read_json(manifest_path)
            if manifest["unit_id"] != unit_id:
                raise ValueError("Neutral export identity mismatch: " + unit_id)
            capture(manifest_path, "neutral_export_manifest")
            source = capture(ROOT / "art-source/neutrals" / unit_id / (unit_id + ".blend"), "authored_neutral_source")
            if source["sha256"] != manifest["source_sha256"]:
                raise ValueError("Neutral source differs from export manifest: " + unit_id)
            for name, expected in sorted(manifest["files"].items()):
                row = capture(scoped(folder / name, folder), "authored_neutral_export")
                if row["sha256"] != expected:
                    raise ValueError("Neutral export differs from manifest: " + row["path"])
            neutral_comparisons.append({"unit_id": unit_id, "source_revision": manifest.get("source_revision"),
                                        "source_sha256": source["sha256"], "export_files": sorted(manifest["files"]),
                                        "canonical_neutrals_sha256_at_export": manifest.get("canonical_source_sha256"),
                                        "matches": True})
        lobby = read_json(ROOT / "exports/lobby/lobby_manifest.json")
        lobby_source = capture(scoped(lobby["source"], ROOT / "art-source/lobby"), "authored_lobby_source")
        if lobby_source["sha256"] != lobby["source_sha256"]:
            raise ValueError("Lobby source differs from export manifest")
        for name, expected in lobby["files"].items():
            row = capture(scoped(ROOT / "exports/lobby" / name, ROOT / "exports/lobby"), "authored_lobby_export")
            if row["sha256"] != expected:
                raise ValueError("Lobby export differs from manifest: " + name)
        for name in ("arena", "effects", "lobby"):
            tree(ROOT / "exports" / name, "authored_" + name + "_exports")
            for path in sorted((ROOT / "art-source" / name).glob("*.blend")):
                capture(path, "authored_" + name + "_source")
        tree(ROOT / "exports/audio", "authored_audio")
        capture(ROOT / "exports/audio/update_provenance.json", "audio_update_provenance")
        for path in (ROOT / "art-source/calibration/WC_Calibration.blend",
                     ROOT / "exports/calibration/WC_Calibration.fbx",
                     ROOT / "exports/calibration/WC_Calibration.export.json",
                     ROOT / "reports/WC-350/hero-audio.json"):
            capture(path, "calibration_or_audio_provenance")

    rows = sorted(records.values(), key=lambda item: item["workspace_relative_path"])
    formats = {ext: [row["workspace_relative_path"] for row in rows
                     if row["group"] == "packaged_payload" and Path(row["path"]).suffix.lower() == ext]
               for ext in (".exe", ".pak", ".utoc", ".ucas", ".dll")}
    if not all(formats[ext] for ext in (".exe", ".pak", ".utoc", ".ucas")):
        raise ValueError("Executable/Pak/IoStore payload set incomplete")
    groups = {}
    fingerprint = hashlib.sha256()
    for row in rows:
        group = groups.setdefault(row["group"], {"files": 0, "bytes": 0})
        group["files"] += 1
        group["bytes"] += row["bytes"]
        fingerprint.update((row["workspace_relative_path"] + "\0" + row["sha256"] + "\n").encode())
    for directory, (expected, members) in directory_sets.items():
        if members() != expected:
            raise ValueError("Input file set changed during capture: " + str(directory))
    for path, expected in stamps.items():
        now = path.stat()
        if (now.st_size, now.st_mtime_ns) != expected:
            raise ValueError("Input bytes/stamp changed during capture: " + str(path))
    revision = subprocess.run(["git", "rev-parse", "--verify", "HEAD"], cwd=ROOT, capture_output=True, text=True)
    result = {"schema": "wonder_chess_candidate_provenance_v2", "candidate": args.candidate,
              "capture_start_utc": started, "capture_end_utc": utc(),
              "status": "PACKAGING_TOOL_SUCCESS_PROVENANCE_CAPTURED_ACCEPTANCE_SEPARATE",
              "input_files_stable_during_capture": True, "package_report": report,
              "package_report_path": str(report_path), "package_root": str(package),
              "packaged_executable": str(launcher), "packaged_game_executable": str(binary),
              "packaged_game_matches_build_output": True, "configuration": args.configuration,
              "build_receipt": receipt, "git_head_at_capture": revision.stdout.strip() if revision.returncode == 0 else None,
              "git_boundary": "Commit contextual; actual per-file hashes include uncommitted files.",
              "acceptance_boundary": "Observed input identity and packaging success only. Launch, matches, network, frame times, audio and visual acceptance remain separate evidence.",
              "data_boundary": "Canonical and loose staged bytes match. Container hashes identify cooked payload; runtime catalog loading is a separate execution check.",
              "art_boundary": "Runtime-only early slice: source art/export comparisons NOT_RUN; missing heroes/neutrals are internal grayboxes, never completed art." if args.runtime_only else "Current authored source/export hashes checked; no implication of visual approval from hashing.",
              "excluded_package_paths": ["Runtime Saved directories"],
              "profile_id": args.profile, "catalog_digest": active_digest,
              "legacy_catalog_digest": stage["catalog_digest"], "active_source_comparisons": active_comparisons,
              "staged_source_comparisons": comparisons,
              "hero_export_comparisons": art_comparisons, "neutral_export_comparisons": neutral_comparisons, "groups": groups,
              "cooked_file_formats": formats, "manifested_file_set_sha256": fingerprint.hexdigest(), "files": rows}
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2)
        stream.write("\n")
    print(json.dumps({"output": str(output), "sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
                      "groups": groups, "input_files_stable_during_capture": True}, indent=2))


if __name__ == "__main__":
    main()

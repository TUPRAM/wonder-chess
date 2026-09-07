"""Capture once, only after successful candidate6 packaging; never alter inputs."""

from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import re
import subprocess

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "reports/WC-360/candidate6-provenance.json"
PACKAGE = ROOT / "builds/Windows-Alpha-Candidate6"
PACKAGE_REPORTS = ROOT / "reports/WC-360/package-candidate6"


def utc(timestamp=None):
    return datetime.now(timezone.utc).isoformat() if timestamp is None else datetime.fromtimestamp(timestamp, timezone.utc).isoformat()


def main():
    if OUTPUT.exists():
        raise SystemExit("Refusing to overwrite immutable candidate6 provenance")
    candidates = sorted(PACKAGE_REPORTS.glob("package-*.json"), key=lambda p: p.stat().st_mtime_ns)
    if not candidates:
        raise SystemExit("Package outcome JSON is absent; no provenance manifest written")
    report_path = candidates[-1]
    report = json.loads(report_path.read_text(encoding="utf-8-sig"))
    if report.get("exit_code") != 0 or report.get("packaging_status") != "tool_returned_success_launch_not_verified":
        raise SystemExit("Latest package report does not confirm tool success; no provenance manifest written")
    executable = PACKAGE / "WonderChess.exe"
    if not executable.is_file():
        raise SystemExit("Packaged executable absent despite report; no provenance manifest written")
    log_path = PACKAGE_REPORTS / report["log_file"]
    log = log_path.read_text(encoding="utf-8-sig", errors="replace")
    if "-archivedirectory=" not in log or str(PACKAGE) not in log:
        raise SystemExit("Package log does not identify the expected archive directory")
    if "BUILD SUCCESSFUL" not in log or "ExitCode=0" not in log:
        raise SystemExit("Package log lacks successful completion markers")
    started = utc()
    rows = []
    stamps = {}
    seen = set()

    def capture(path, group):
        path = path.resolve()
        if path in seen:
            return next(row for row in rows if row["path"] == str(path))
        seen.add(path)
        before = path.stat()
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(4 * 1024 * 1024), b""):
                digest.update(chunk)
        after = path.stat()
        if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
            raise RuntimeError(f"File changed while being hashed: {path}")
        stamps[path] = (after.st_size, after.st_mtime_ns)
        item = {"group": group, "path": str(path), "workspace_relative_path": path.relative_to(ROOT).as_posix(),
                "bytes": after.st_size, "modified_utc": utc(after.st_mtime), "sha256": digest.hexdigest()}
        rows.append(item)
        return item

    capture(report_path, "packaging_evidence")
    capture(log_path, "packaging_evidence")
    for directory, group in ((ROOT / "game/Source", "game_source"), (ROOT / "game/Config", "game_config"),
                             (ROOT / "game/Content/WonderChess/SourceData", "staged_source_data")):
        for path in sorted(directory.rglob("*")):
            if path.is_file():
                capture(path, group)
    for path in sorted((ROOT / "game/Content").rglob("*")):
        if path.is_file():
            capture(path, "game_content")
    capture(ROOT / "game/WonderChess.uproject", "project_descriptor")
    for path in sorted(PACKAGE.rglob("*")):
        if path.is_file() and "Saved" not in path.relative_to(PACKAGE).parts:
            capture(path, "packaged_payload")
    for path in sorted((ROOT / "game/Intermediate/Build").rglob("*.rsp")):
        if "WonderChess" in str(path.relative_to(ROOT)):
            capture(path, "compiler_response_file")
    stage_manifest_path = ROOT / "game/Content/WonderChess/SourceData/runtime_stage_manifest.json"
    stage_manifest = json.loads(stage_manifest_path.read_text(encoding="utf-8-sig"))
    comparisons = []
    for name, declared in sorted(stage_manifest["files"].items()):
        staged = capture(stage_manifest_path.parent / name, "staged_source_data")
        source = capture(ROOT / declared["source"], "canonical_or_generated_data")
        comparisons.append({"staged_relative_path": name, "canonical_or_generated_source": declared["source"],
                            "declared_sha256": declared["sha256"], "actual_staged_sha256": staged["sha256"],
                            "actual_source_sha256": source["sha256"],
                            "matches": declared["sha256"] == staged["sha256"] == source["sha256"]})
    revision = subprocess.run(["git", "rev-parse", "--verify", "HEAD"], cwd=ROOT, capture_output=True, text=True)
    git_head = revision.stdout.strip() if revision.returncode == 0 else None
    groups = {}
    for row in rows:
        group = groups.setdefault(row["group"], {"files": 0, "bytes": 0})
        group["files"] += 1
        group["bytes"] += row["bytes"]
    cooked_formats = {extension: [row["workspace_relative_path"] for row in rows
                                  if row["group"] == "packaged_payload" and Path(row["path"]).suffix.lower() == extension]
                      for extension in (".exe", ".pak", ".utoc", ".ucas", ".dll")}
    if not cooked_formats[".exe"] or not cooked_formats[".pak"] or not cooked_formats[".utoc"] or not cooked_formats[".ucas"]:
        raise SystemExit("Expected packaged executable/Pak/IoStore files incomplete; no provenance manifest written")
    if not all(item["matches"] for item in comparisons):
        raise SystemExit("Staged/canonical declared SHA256 mismatch; no provenance manifest written")
    for path, expected in stamps.items():
        stat = path.stat()
        if (stat.st_size, stat.st_mtime_ns) != expected:
            raise RuntimeError(f"Input changed during manifest capture: {path}")
    fingerprint = hashlib.sha256()
    for row in sorted(rows, key=lambda item: item["workspace_relative_path"]):
        fingerprint.update((row["workspace_relative_path"] + "\0" + row["sha256"] + "\n").encode("utf-8"))
    result = {"schema": "wonder_chess_candidate_provenance_v1", "candidate": "candidate6",
              "capture_start_utc": started, "capture_end_utc": utc(), "input_files_stable_during_capture": True,
              "status": "PACKAGING_TOOL_SUCCESS_PROVENANCE_CAPTURED_LAUNCH_UNVERIFIED",
              "package_report": report, "package_report_path": str(report_path.resolve()),
              "package_root": str(PACKAGE.resolve()), "packaged_executable": str(executable.resolve()),
              "configuration": report["configuration"], "git_head_at_capture": git_head,
              "git_boundary": "Commit is contextual; per-file hashes cover current source/config/data including uncommitted files.",
              "acceptance_boundary": "Package tool success and immutable observed file hashes. No launch, complete human match, network session, render performance or art/audio acceptance inferred.",
              "data_boundary": "SourceData is staged as UFS. Loose authoring-stage bytes are hashed and compared to canonical/generated files; cooked payload container hashes cover packaged UFS data. Actual runtime catalog/profile validation remains a separate launch check.",
              "excluded_package_paths": ["Any runtime Saved directory"],
              "catalog_digest": stage_manifest["catalog_digest"],
              "staged_source_comparisons": comparisons, "groups": groups, "cooked_file_formats": cooked_formats,
              "toolchain_lines_from_successful_log": [line for line in log.splitlines()
                                                     if "Using Visual Studio" in line or "Windows 10." in line
                                                     or "bundled DotNet SDK version" in line or "Result: Succeeded" in line],
              "manifested_file_set_sha256": fingerprint.hexdigest(), "files": sorted(rows, key=lambda item: item["workspace_relative_path"])}
    with OUTPUT.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2)
        stream.write("\n")
    print(json.dumps({"output": str(OUTPUT), "sha256": hashlib.sha256(OUTPUT.read_bytes()).hexdigest(),
                      "groups": groups, "input_files_stable_during_capture": True}, indent=2))


if __name__ == "__main__":
    main()

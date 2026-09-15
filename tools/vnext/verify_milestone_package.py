"""Capture or verify exact milestone package/source identity; never infer release acceptance."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import tempfile

SCHEMA = "wonder_chess.milestone_package.1"
RUNTIME = "WonderChess/Content/WonderChess/VNextData/runtime_catalog.json"
SOURCE_RUNTIME = "game/Content/WonderChess/VNextData/runtime_catalog.json"
GENERATED_RUNTIME = "data/vnext/generated/runtime_catalog.json"
HEADER = "game/Source/WonderChessRuntime/Public/VNext/WonderVNextCatalog.generated.h"
SOURCE_REQUIRED = (
    "data/vnext/catalog.json", GENERATED_RUNTIME, "data/vnext/generated/WonderVNextCatalog.h", HEADER,
    SOURCE_RUNTIME, "game/WonderChess.uproject", "tools/vnext/catalog.py", "tools/unreal/package_game.ps1",
)
IGNORED_RUNTIME = ("saved/", "wonderchess/saved/", "engine/saved/")
BOUNDARY = (
    "Exact file identity and membership, source/generated/staged runtime consistency, and embedded binary identity markers. "
    "Not bit-reproducible build proof, art/human acceptance, network acceptance, or clean-machine testing. "
    "A cold launch on the development computer is same-machine evidence only."
)


def checked_path(root: Path, relative: str) -> Path:
    if not isinstance(relative, str):
        raise ValueError("Manifest file path must be a string")
    value = PurePosixPath(relative)
    if not relative or "\\" in relative or ":" in relative or value.is_absolute() or ".." in value.parts or value.as_posix() != relative:
        raise ValueError("Invalid manifest relative path: " + relative)
    path = root / relative
    if not path.resolve().is_relative_to(root.resolve()):
        raise ValueError("Manifest path escapes its root: " + relative)
    return path


def ignored(relative: str) -> bool:
    return relative.casefold().startswith(IGNORED_RUNTIME)


def tree(root: Path, directory: Path, omit_runtime: bool = False) -> set[str]:
    if not directory.is_dir():
        raise ValueError("Missing required directory: " + str(directory))
    result = set()
    for path in directory.rglob("*"):
        relative = path.relative_to(root).as_posix()
        if omit_runtime and ignored(relative + ("/" if path.is_dir() else "")):
            continue
        attributes = getattr(path.lstat(), "st_file_attributes", 0)
        if path.is_symlink() or attributes & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0):
            raise ValueError("Links/reparse points cannot enter exact identity capture: " + relative)
        if path.is_file():
            checked_path(root, relative)
            result.add(relative)
    return result


def source_members(root: Path, actual_binary: str) -> set[str]:
    members = set(SOURCE_REQUIRED)
    members.update(tree(root, root / "game/Source"))
    members.update(tree(root, root / "game/Config"))
    art_slice = root / "game/Content/WonderChess/VNext/ArtSliceR001"
    if art_slice.is_dir():
        members.update(tree(root, art_slice))
        members.add("tools/unreal/import_art_slice.py")
    storybook = root / "game/Content/WonderChess/VNext/ArtExpansionR001"
    if storybook.is_dir():
        members.update(tree(root, storybook))
        members.add("tools/unreal/import_storybook.py")
    fonts = root / "game/Content/WonderChess/UIFonts"
    if fonts.is_dir():
        members.update(tree(root, fonts))
    for material in ("game/Content/WonderChess/Materials/M_WC_Surface.uasset", "game/Content/WonderChess/VNext/M_CombatCue.uasset"):
        if (root / material).is_file():
            members.add(material)
    if (root / "game/Content/WonderChess/SourceData").is_dir():
        members.update(tree(root, root / "game/Content/WonderChess/SourceData"))
    members.update(path.relative_to(root).as_posix() for path in (root / "data").glob("*.json"))
    members.add("game/Binaries/Win64/" + Path(actual_binary).name)
    return members


def inventory(root: Path, members: set[str]) -> list[dict]:
    rows = []
    seen = set()
    for relative in sorted(members):
        if relative.casefold() in seen:
            raise ValueError("Case-colliding file membership: " + relative)
        seen.add(relative.casefold())
        path = checked_path(root, relative)
        before = path.stat()
        if not path.is_file():
            raise ValueError("Required file is missing: " + relative)
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(4 * 1024 * 1024), b""):
                digest.update(chunk)
        after = path.stat()
        if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
            raise ValueError("File changed during hashing: " + relative)
        rows.append({"path": relative, "bytes": after.st_size, "sha256": digest.hexdigest()})
    return rows


def roles(package: Path, members: set[str]) -> dict:
    bootstrap = "WonderChess.exe"
    binaries = sorted(members.intersection({"WonderChess/Binaries/Win64/WonderChess.exe",
                                           "WonderChess/Binaries/Win64/WonderChess-Win64-Shipping.exe"}))
    paks = sorted(name for name in members if name.startswith("WonderChess/Content/Paks/") and
                  Path(name).suffix.casefold() in (".pak", ".utoc", ".ucas"))
    if bootstrap not in members or len(binaries) != 1 or not paks:
        raise ValueError("Package needs its bootstrap, exactly one actual game binary, and cooked containers")
    return {"bootstrap": bootstrap, "game_binary": binaries[0], "containers": paks}


def identity(source: Path, package: Path, package_roles: dict) -> dict:
    authored = (source / "data/vnext/catalog.json").read_bytes()
    runtime = (source / GENERATED_RUNTIME).read_bytes()
    generated_header = (source / "data/vnext/generated/WonderVNextCatalog.h").read_bytes()
    if (source / SOURCE_RUNTIME).read_bytes() != runtime or (source / HEADER).read_bytes() != generated_header:
        raise ValueError("Generated/staged runtime or native headers differ")
    runtime_json = json.loads(runtime)
    source_sha = hashlib.sha256(authored).hexdigest()
    runtime_sha1 = hashlib.sha1(runtime).hexdigest()
    if not isinstance(runtime_json, dict) or runtime_json.get("profile_id") != "wonder_vnext" or runtime_json.get("source_sha256") != source_sha:
        raise ValueError("Runtime catalogue has the wrong source/profile identity")
    for marker, value in (("SourceSha256", source_sha), ("RuntimeSha1", runtime_sha1)):
        if not re.search(rb"\b" + marker.encode() + rb'\s*=\s*"' + value.encode() + rb'"', generated_header):
            raise ValueError("Compiled header has the wrong " + marker)
    actual = checked_path(package, package_roles["game_binary"]).read_bytes()
    built = source / "game/Binaries/Win64" / Path(package_roles["game_binary"]).name
    if hashlib.sha256(actual).digest() != hashlib.sha256(built.read_bytes()).digest():
        raise ValueError("Packaged actual binary differs from the current compiled game binary")
    for value in (source_sha, runtime_sha1):
        if value.encode() not in actual and value.encode("utf-16-le") not in actual:
            raise ValueError("Actual game binary lacks the expected compiled catalogue identity marker")
    return {"profile_id": "wonder_vnext", "balance_version": runtime_json["balance_version"],
            "source_sha256": source_sha, "runtime_sha1": runtime_sha1, "runtime_sha256": hashlib.sha256(runtime).hexdigest()}


def packaged_runtime(package: Path, package_roles: dict, unreal_pak: Path | None) -> tuple[bytes, dict]:
    loose = package / RUNTIME
    pak_files = [name for name in package_roles["containers"] if Path(name).suffix.casefold() == ".pak"]
    if not pak_files and loose.is_file():
        return loose.read_bytes(), {"kind": "loose", "path": RUNTIME}
    if unreal_pak is None or not unreal_pak.is_file():
        raise ValueError("Runtime is packed; supply the verified installed UnrealPak executable for capture")
    matches = []
    with tempfile.TemporaryDirectory(prefix="wc-runtime-extract-") as temporary:
        for index, relative in enumerate(pak_files):
            destination = Path(temporary) / str(index)
            destination.mkdir()
            result = subprocess.run(
                [str(unreal_pak), str(package / relative), "-Extract", str(destination),
                 "-Filter=*WonderChess/VNextData/runtime_catalog.json", "-unattended"],
                capture_output=True, timeout=60,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
            if result.returncode:
                raise ValueError("UnrealPak extraction failed for " + relative + ": " + result.stdout.decode("utf-8", errors="replace")[-1200:])
            for path in destination.rglob("runtime_catalog.json"):
                if not path.resolve().is_relative_to(destination.resolve()):
                    raise ValueError("Extracted runtime path escaped its temporary directory")
                matches.append((path.read_bytes(), relative))
    if not matches and loose.is_file():
        return loose.read_bytes(), {"kind": "loose", "path": RUNTIME, "containers_checked": pak_files,
                                    "tool_sha256": hashlib.sha256(unreal_pak.read_bytes()).hexdigest()}
    if len(matches) != 1:
        raise ValueError("Expected exactly one runtime catalogue in cooked containers; found " + str(len(matches)))
    if loose.is_file() and loose.read_bytes() != matches[0][0]:
        raise ValueError("Loose and packed runtime catalogues differ; a sidecar cannot replace the packed identity")
    return matches[0][0], {"kind": "unreal_pak_extraction", "container": matches[0][1],
                           "tool_sha256": hashlib.sha256(unreal_pak.read_bytes()).hexdigest()}


def capture(source: Path, package: Path, unreal_pak: Path | None = None) -> dict:
    source, package = source.resolve(), package.resolve()
    package_names = tree(package, package, True)
    package_roles = roles(package, package_names)
    source_names = source_members(source, package_roles["game_binary"])
    source_rows, package_rows = inventory(source, source_names), inventory(package, package_names)
    catalogue = identity(source, package, package_roles)
    runtime, storage = packaged_runtime(package, package_roles, unreal_pak)
    if hashlib.sha256(runtime).hexdigest() != catalogue["runtime_sha256"]:
        raise ValueError("Packaged runtime catalogue differs from generated/staged/compiled identity")
    if (source_members(source, package_roles["game_binary"]) != source_names or tree(package, package, True) != package_names or
            inventory(source, source_names) != source_rows or inventory(package, package_names) != package_rows):
        raise ValueError("Inputs changed during capture")
    return {"schema": SCHEMA, "captured_utc": datetime.now(timezone.utc).isoformat(),
            "source_root": str(source), "package_root": str(package), "source_files": source_rows,
            "package_files": package_rows, "roles": package_roles, "catalogue": catalogue,
            "packaged_runtime": storage, "ignored_runtime_prefixes": list(IGNORED_RUNTIME),
            "inputs_stable_during_capture": True, "boundary": BOUNDARY}


def validate_rows(root: Path, rows: list, actual: set[str]) -> None:
    if not isinstance(rows, list) or not rows:
        raise ValueError("Missing file inventory")
    expected = set()
    folded = set()
    for row in rows:
        if not isinstance(row, dict) or set(row) != {"path", "bytes", "sha256"}:
            raise ValueError("Malformed file inventory row")
        checked_path(root, row["path"])
        if row["path"].casefold() in folded:
            raise ValueError("Duplicate manifest file")
        if type(row["bytes"]) is not int or row["bytes"] < 0 or not re.fullmatch("[0-9a-f]{64}", row["sha256"]):
            raise ValueError("Malformed file size/hash")
        expected.add(row["path"])
        folded.add(row["path"].casefold())
    if expected != actual:
        raise ValueError("File membership changed; missing=" + str(sorted(expected - actual)) + "; unexpected=" + str(sorted(actual - expected)))
    if sorted(rows, key=lambda row: row["path"]) != inventory(root, actual):
        raise ValueError("File bytes differ from captured manifest")


def verify(manifest: dict, source: Path | None = None, package: Path | None = None) -> dict:
    if not isinstance(manifest, dict) or manifest.get("schema") != SCHEMA or manifest.get("inputs_stable_during_capture") is not True:
        raise ValueError("Unrecognized or unstable package manifest")
    if manifest.get("ignored_runtime_prefixes") != list(IGNORED_RUNTIME):
        raise ValueError("Manifest cannot broaden runtime exclusions")
    source = (source or Path(manifest["source_root"])).resolve()
    package = (package or Path(manifest["package_root"])).resolve()
    actual_names = tree(package, package, True)
    actual_roles = roles(package, actual_names)
    if actual_roles != manifest["roles"]:
        raise ValueError("Package binary/container roles changed")
    validate_rows(source, manifest["source_files"], source_members(source, actual_roles["game_binary"]))
    validate_rows(package, manifest["package_files"], actual_names)
    if identity(source, package, actual_roles) != manifest["catalogue"]:
        raise ValueError("Catalogue identity differs from captured package")
    storage = manifest["packaged_runtime"]
    if not isinstance(storage, dict):
        raise ValueError("Invalid packaged runtime binding")
    if storage.get("kind") == "loose":
        if storage.get("path") != RUNTIME or hashlib.sha256((package / RUNTIME).read_bytes()).hexdigest() != manifest["catalogue"]["runtime_sha256"]:
            raise ValueError("Loose packaged runtime identity differs")
    elif storage.get("kind") != "unreal_pak_extraction" or storage.get("container") not in actual_roles["containers"]:
        raise ValueError("Invalid packaged runtime binding")
    return {"status": "PASS", "verified_utc": datetime.now(timezone.utc).isoformat(),
            "source_files": len(manifest["source_files"]), "package_files": len(manifest["package_files"]),
            "catalogue": manifest["catalogue"], "boundary": BOUNDARY}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("capture", "verify"))
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--source-root", type=Path)
    parser.add_argument("--package-root", type=Path)
    parser.add_argument("--unreal-pak", type=Path)
    args = parser.parse_args()
    try:
        if args.mode == "capture":
            if args.source_root is None or args.package_root is None:
                raise ValueError("Capture requires --source-root and --package-root")
            if args.manifest.exists() or args.manifest.resolve().is_relative_to(args.package_root.resolve()):
                raise ValueError("Use a fresh manifest path outside the package")
            destination, source = args.manifest.resolve(), args.source_root.resolve()
            if destination.is_relative_to(source):
                relative = destination.relative_to(source).as_posix().casefold()
                if (relative in {name.casefold() for name in SOURCE_REQUIRED} or relative.startswith(("game/source/", "game/config/", "game/content/wonderchess/sourcedata/")) or
                        (destination.parent == source / "data" and destination.suffix.casefold() == ".json")):
                    raise ValueError("Manifest destination would enter its own captured source inventory")
            result = capture(args.source_root, args.package_root, args.unreal_pak)
            args.manifest.parent.mkdir(parents=True, exist_ok=True)
            with args.manifest.open("x", encoding="utf-8") as handle:
                json.dump(result, handle, indent=2)
            print(json.dumps({"status": "CAPTURED", "manifest": str(args.manifest.resolve()),
                              "source_files": len(result["source_files"]), "package_files": len(result["package_files"]), "boundary": BOUNDARY}, indent=2))
        else:
            manifest = json.loads(args.manifest.read_text(encoding="utf-8-sig"))
            print(json.dumps(verify(manifest, args.source_root, args.package_root), indent=2))
        return 0
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as error:
        print(json.dumps({"status": "FAIL", "error": str(error)}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

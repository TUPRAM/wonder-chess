"""Create or check the local, relative-path SHA-256 inventory for a PC transfer."""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import sys

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "TRANSFER_MANIFEST.jsonl"


def sha256(path: Path) -> str:
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def checked_path(relative: str) -> Path:
    value = PurePosixPath(relative)
    if not relative or ":" in relative or "\\" in relative or value.is_absolute() or ".." in value.parts or value.as_posix() != relative:
        raise ValueError(f"Unsafe manifest path: {relative}")
    path = ROOT / relative
    if not path.resolve().is_relative_to(ROOT):
        raise ValueError(f"Path leaves the project: {relative}")
    return path


def files(manifest: Path):
    for parent, dirs, names in os.walk(ROOT):
        for name in dirs + names:
            path = Path(parent) / name
            if path.lstat().st_file_attributes & 0x400:
                raise ValueError(f"Review link/reparse point before transfer: {path}")
        for name in names:
            path = Path(parent) / name
            relative = path.relative_to(ROOT).as_posix()
            # Git status rewrites the index; Git operations append reflogs/locks.
            # Objects, refs, HEAD, configuration and all project payloads are covered.
            if path == manifest or relative == ".git/index" or relative.startswith(".git/logs/") or (relative.startswith(".git/") and relative.endswith(".lock")):
                continue
            yield path, relative


def create(manifest: Path):
    if manifest.exists():
        raise ValueError("Manifest already exists; preserve it or choose a new --manifest path.")
    jobs = list(files(manifest))

    def row(job):
        path, relative = job
        before = path.stat()
        digest = sha256(path)
        after = path.stat()
        if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
            raise ValueError(f"File changed during capture: {relative}")
        return {"path": relative, "bytes": after.st_size, "sha256": digest}

    total = 0
    rows_digest = hashlib.sha256()
    try:
        with manifest.open("x", encoding="utf-8", newline="\n") as handle:
            with ThreadPoolExecutor(max_workers=4) as pool:
                for count, item in enumerate(pool.map(row, jobs), 1):
                    line = json.dumps(item, ensure_ascii=True) + "\n"
                    handle.write(line)
                    rows_digest.update(line.encode("utf-8"))
                    total += item["bytes"]
                    if count % 5000 == 0:
                        print(f"Hashed {count}/{len(jobs)} files", flush=True)
            handle.write(json.dumps({"type": "complete", "files": len(jobs), "bytes": total,
                                     "rows_sha256": rows_digest.hexdigest()}) + "\n")
    except Exception:
        print("Capture failed; this manifest is incomplete. Preserve it as failure evidence and use a fresh path for a retry.", file=sys.stderr)
        raise
    print(json.dumps({"status": "CREATED", "files": len(jobs), "bytes": total, "manifest_sha256": sha256(manifest)}))


def verify(manifest: Path) -> int:
    lines = manifest.read_text(encoding="utf-8").splitlines(keepends=True)
    if not lines:
        raise ValueError("Empty manifest")
    summary = json.loads(lines[-1])
    if summary.get("type") != "complete" or summary.get("rows_sha256") != hashlib.sha256("".join(lines[:-1]).encode("utf-8")).hexdigest():
        raise ValueError("Incomplete or changed manifest")
    rows = [json.loads(line) for line in lines[:-1]]
    if summary.get("files") != len(rows) or summary.get("bytes") != sum(row["bytes"] for row in rows):
        raise ValueError("Manifest totals do not match")
    if not rows or len({r["path"].casefold() for r in rows}) != len(rows):
        raise ValueError("Empty manifest or duplicate paths")
    for row in rows:
        checked_path(row["path"])
        if type(row["bytes"]) is not int or row["bytes"] < 0 or len(row["sha256"]) != 64 or any(c not in "0123456789abcdef" for c in row["sha256"]):
            raise ValueError("Invalid size/hash in manifest")

    def check(row):
        path = checked_path(row["path"])
        try:
            if path.stat().st_size != row["bytes"] or sha256(path) != row["sha256"]:
                return {"path": row["path"], "error": "changed"}
        except OSError as error:
            return {"path": row["path"], "error": str(error)}
        return None

    failures = []
    with ThreadPoolExecutor(max_workers=4) as pool:
        for count, result in enumerate(pool.map(check, rows), 1):
            if result:
                failures.append(result)
                print(json.dumps(result), flush=True)
            if count % 5000 == 0:
                print(f"Checked {count}/{len(rows)} files", flush=True)
    print(json.dumps({"status": "FAIL" if failures else "PASS", "files": len(rows), "bytes": sum(r["bytes"] for r in rows), "failures": len(failures), "manifest_sha256": sha256(manifest)}))
    return bool(failures)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--create", action="store_true", help="Capture a fresh manifest after closing editors and builds")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    args = parser.parse_args()
    manifest = args.manifest.resolve()
    if args.create:
        create(manifest)
        return 0
    return verify(manifest)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        sys.exit(1)

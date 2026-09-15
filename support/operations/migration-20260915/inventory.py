"""One-time migration inventory: hash original payloads and verify their new paths."""
import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
ACTIVE = Path(r"C:\Users\iputu\AppData\Local\Packages\OpenAI.Codex_2p2nqsd0c76g0\LocalCache\Local\CodexWorktrees\wc\m7")
SOURCES = [
    ("historical", ROOT, "support/archives/previous-checkout-20260915"),
    ("active", ACTIVE, ""),
    ("project-support", Path(r"C:\Users\iputu\Documents\Project Support\Wonder Chess"), "support/external"),
    ("user-data", Path(r"C:\Users\iputu\AppData\Local\WonderChess"), "support/local-state/WonderChess"),
]


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def inventory():
    jobs = []
    for group, source, destination in SOURCES:
        for parent, dirs, files in os.walk(source):
            if Path(parent) == source:
                if group == "historical":
                    dirs[:] = [d for d in dirs if d not in {".git", "support"}]
                if group == "active":
                    files = [f for f in files if f != ".git"]
            for name in dirs + files:
                path = Path(parent) / name
                if path.lstat().st_file_attributes & 0x400:
                    raise RuntimeError(f"Review reparse point before migration: {path}")
            for name in files:
                path = Path(parent) / name
                relative = path.relative_to(source).as_posix()
                jobs.append((group, path, (Path(destination) / relative).as_posix()))
    downloads = Path(r"C:\Users\iputu\Downloads")
    for path in sorted(downloads.glob("Wonder_Chess_*.zip")):
        jobs.append(("downloads", path, "support/archives/downloads/" + path.name))

    def record(job):
        group, path, destination = job
        before = path.stat()
        sha = digest(path)
        after = path.stat()
        if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
            raise RuntimeError(f"Source changed during hashing: {path}")
        return dict(group=group, source=str(path), destination=destination,
                    bytes=after.st_size, mtime_ns=after.st_mtime_ns, sha256=sha)

    totals = {}
    started = time.monotonic()
    with (HERE / "before.jsonl").open("x", encoding="utf-8") as output:
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            for n, row in enumerate(pool.map(record, jobs), 1):
                output.write(json.dumps(row) + "\n")
                count = totals.setdefault(row["group"], {"files": 0, "bytes": 0})
                count["files"] += 1
                count["bytes"] += row["bytes"]
                if n % 5000 == 0:
                    print(f"Hashed {n}/{len(jobs)} files", flush=True)
    summary = dict(groups=totals, seconds=round(time.monotonic()-started, 2), manifest_sha256=digest(HERE / "before.jsonl"))
    (HERE / "before-summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary), flush=True)


def verify():
    rows = [json.loads(line) for line in (HERE / "before.jsonl").read_text().splitlines()]
    def check(row):
        path = ROOT / row["destination"]
        if not path.is_file():
            return {"path": row["destination"], "error": "missing"}
        if path.stat().st_size != row["bytes"] or digest(path) != row["sha256"]:
            return {"path": row["destination"], "error": "changed"}
        return None
    failures = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        for n, result in enumerate(pool.map(check, rows), 1):
            if result:
                failures.append(result)
            if n % 5000 == 0:
                print(f"Verified {n}/{len(rows)} files", flush=True)
    result = dict(files=len(rows), bytes=sum(r["bytes"] for r in rows), failures=failures, passed=not failures)
    (HERE / "move-verification.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result), flush=True)
    return 1 if failures else 0


if __name__ == "__main__":
    if sys.argv[1:] == ["inventory"]:
        inventory()
    elif sys.argv[1:] == ["verify"]:
        sys.exit(verify())
    else:
        raise SystemExit("Use inventory or verify")

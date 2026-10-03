"""Submit and collect one bounded Meshy API job. Never retries a charged call.

The API key is read from the owner's Windows-encrypted store written by `Set Meshy API Key.cmd`; it is never
printed, logged or written to a receipt. Each job lives in its own folder with a `job.json` describing it.

    meshy_job.py balance
    meshy_job.py submit <job-folder>      one POST; refuses if this job was ever submitted before
    meshy_job.py status <job-folder>
    meshy_job.py download <job-folder>    saves every model and texture the finished task offers
"""
from __future__ import annotations

import argparse
import base64
import ctypes
import ctypes.wintypes
import hashlib
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HOST = "https://api.meshy.ai"
KEY_FILE = Path(os.environ.get("LOCALAPPDATA", "")) / "WonderChess/credentials/meshy-api-key.dpapi"
ENDPOINTS = {"multi-image-to-3d": "/openapi/v1/multi-image-to-3d", "rigging": "/openapi/v1/rigging",
             "animations": "/openapi/v1/animations"}


class Blob(ctypes.Structure):
    _fields_ = [("size", ctypes.wintypes.DWORD), ("data", ctypes.POINTER(ctypes.c_char))]


def unprotect(hex_text):
    """Decode PowerShell's ConvertFrom-SecureString output (DPAPI blob of UTF-16 text) for this Windows user."""
    raw = bytes.fromhex(hex_text.strip())
    source = Blob(len(raw), ctypes.cast(ctypes.create_string_buffer(raw, len(raw)), ctypes.POINTER(ctypes.c_char)))
    target = Blob()
    if not ctypes.windll.crypt32.CryptUnprotectData(ctypes.byref(source), None, None, None, None, 0,
                                                    ctypes.byref(target)):
        raise SystemExit("The stored Meshy key cannot be read by this Windows user; run Set Meshy API Key.cmd again")
    try:
        return ctypes.string_at(target.data, target.size).decode("utf-16-le")
    finally:
        ctypes.windll.kernel32.LocalFree(target.data)


def api_key():
    if not KEY_FILE.exists():
        raise SystemExit("No Meshy API key is stored on this PC. Double-click 'Set Meshy API Key.cmd' in the "
                         "project folder, paste the key, then run this again.")
    return unprotect(KEY_FILE.read_text(encoding="ascii"))


def call(method, path, body=None):
    request = urllib.request.Request(HOST + path, method=method,
                                     data=None if body is None else json.dumps(body).encode("utf-8"),
                                     headers={"Authorization": "Bearer " + api_key(),
                                              "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=300) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        raise SystemExit(f"Meshy answered {error.code}: {error.read().decode('utf-8', 'replace')[:800]}")


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def save(folder, name, value):
    (folder / name).write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def load_job(folder):
    job = json.loads((folder / "job.json").read_text(encoding="utf-8"))
    if job["operation"] not in ENDPOINTS:
        raise SystemExit("Unknown operation in job.json")
    return job


def submit(folder):
    job = load_job(folder)
    marker = folder / "submission-started.txt"
    if marker.exists() or (folder / "task.json").exists():
        raise SystemExit("This job was already submitted. Check its status and the account before any new job; "
                         "a new attempt needs a new job folder.")
    body = dict(job["parameters"])
    inputs = []
    if job["operation"] == "multi-image-to-3d":
        body["image_urls"] = []
        for relative in job["images"]:
            raw = (ROOT / relative).read_bytes()
            inputs.append({"file": relative, "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)})
            body["image_urls"].append("data:image/png;base64," + base64.b64encode(raw).decode("ascii"))
    balance_before = call("GET", "/openapi/v1/balance").get("balance")
    if balance_before is not None and balance_before < job["credit_ceiling"]:
        raise SystemExit(f"Balance {balance_before} is below this job's ceiling of {job['credit_ceiling']} credits")
    # The marker stays after a timeout or failure so an uncertain charge is never repeated blindly.
    marker.write_text(f"{now()} one authorized submission; ceiling {job['credit_ceiling']} credits; no retry\n",
                      encoding="utf-8")
    response = call("POST", ENDPOINTS[job["operation"]], body)
    save(folder, "task.json", {"submitted_utc": now(), "task_id": response.get("result"), "response": response,
                               "balance_before": balance_before, "inputs": inputs})
    print("Submitted task", response.get("result"))


def status(folder):
    job = load_job(folder)
    task = json.loads((folder / "task.json").read_text(encoding="utf-8"))
    result = call("GET", f"{ENDPOINTS[job['operation']]}/{task['task_id']}")
    save(folder, "status.json", {"checked_utc": now(), "task": result})
    print(result.get("status"), result.get("progress"), (result.get("task_error") or {}).get("message", ""))
    return result


def download(folder):
    result = status(folder)
    if result.get("status") != "SUCCEEDED":
        raise SystemExit("The task has not succeeded; nothing downloaded")
    files = {}

    def collect(prefix, value):
        if isinstance(value, str) and value.startswith("http"):
            files[prefix] = value
        elif isinstance(value, dict):
            for key, item in value.items():
                collect(f"{prefix}_{key}" if prefix else key, item)
        elif isinstance(value, list):
            for index, item in enumerate(value):
                collect(f"{prefix}_{index}", item)

    for key in ("model_urls", "texture_urls", "result", "thumbnail_url"):
        collect(key, result.get(key))
    output = folder / "original"
    output.mkdir(exist_ok=True)
    manifest = {}
    for name, url in files.items():
        extension = Path(url.split("?")[0]).suffix or ".bin"
        target = output / (name + extension)
        if not target.exists():
            with urllib.request.urlopen(url, timeout=600) as response:
                target.write_bytes(response.read())
        manifest[target.name] = {"sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
                                 "bytes": target.stat().st_size}
    # Signed download links can carry credentials; keep hashes, not URLs.
    save(folder, "download.json", {"downloaded_utc": now(), "files": manifest,
                                   "balance_after": call("GET", "/openapi/v1/balance").get("balance")})
    redacted = json.loads((folder / "status.json").read_text(encoding="utf-8"))

    def redact(value):
        if isinstance(value, str) and value.startswith("http"):
            return value.split("?")[0] + "?<redacted>"
        if isinstance(value, dict):
            return {key: redact(item) for key, item in value.items()}
        if isinstance(value, list):
            return [redact(item) for item in value]
        return value

    save(folder, "status.json", redact(redacted))
    print(f"Saved {len(manifest)} files to {output.relative_to(ROOT)}")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=("balance", "submit", "status", "download"))
    parser.add_argument("folder", nargs="?", type=Path)
    args = parser.parse_args()
    if args.command == "balance":
        print("Balance:", call("GET", "/openapi/v1/balance").get("balance"))
        return
    if args.folder is None:
        raise SystemExit("A job folder is required")
    {"submit": submit, "status": status, "download": download}[args.command](args.folder.resolve())


if __name__ == "__main__":
    sys.exit(main())

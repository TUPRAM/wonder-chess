"""Read-only MCP verification against an explicit, already-open candidate."""
import argparse
import asyncio
import base64
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import tomllib


REQUIRED_TOOLS = (
    "get_addon_status", "execute_blender_code", "get_scene_info",
    "get_object_info", "get_viewport_screenshot",
)
INSPECT_CODE = (
    'import bpy\nimport json\n'
    'print(json.dumps({"file": bpy.data.filepath, "version": bpy.app.version_string, '
    '"dirty": bpy.data.is_dirty, "objects": [{"name": o.name, "type": o.type} '
    'for o in bpy.context.scene.objects]}))'
)


def checked_blend(path, root):
    resolved = Path(path).resolve(strict=True)
    if not resolved.is_relative_to(root.resolve()) or resolved.suffix.lower() != ".blend" or not resolved.is_file():
        raise ValueError("Expected blend must be an existing .blend file inside this repository")
    return resolved


def tool_text(result):
    return "\n".join(block["text"] for block in result.get("content", []) if block.get("type") == "text")


def require_success(result):
    message = tool_text(result).strip()
    if result.get("isError") or re.match(r"(?:error|failed|could not|unable|rejected by safe mode|traceback)\b", message, re.I):
        raise ValueError(message or "MCP returned isError without error text")
    if not result.get("content"):
        raise ValueError("MCP returned no content")


def json_result(result, prefix=""):
    require_success(result)
    message = tool_text(result).strip()
    if prefix:
        if not message.startswith(prefix):
            raise ValueError("Missing successful execution prefix: " + message)
        message = message[len(prefix):].strip()
    parsed = json.loads(message)
    if not isinstance(parsed, dict):
        raise ValueError("Expected a JSON object from MCP")
    if parsed.get("error") or parsed.get("status") == "error":
        raise ValueError(str(parsed.get("error") or parsed))
    return parsed


def assert_expected_scene(snapshot, expected):
    actual = snapshot.get("file")
    if not actual or Path(actual).resolve() != expected:
        raise ValueError(f"Wrong live Blender file: expected {expected}; actual {actual!r}")


def save_capture(result, folder):
    require_success(result)
    captures = [block for block in result["content"] if block.get("type") == "image"]
    if len(captures) != 1 or captures[0].get("mimeType") != "image/png":
        raise ValueError("Expected exactly one PNG viewport capture")
    block = captures[0]
    image_bytes = base64.b64decode(block["data"], validate=True)
    if not image_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
        raise ValueError("Viewport capture has no PNG signature")
    path = folder / "viewport.png"
    with path.open("xb") as output:
        output.write(image_bytes)
    block.pop("data")
    block["saved_path"] = str(path)
    block["sha256"] = hashlib.sha256(image_bytes).hexdigest()
    return path


async def verify_session(session, config, expected, folder, user_prompt, results):
    results["initialize"] = (await session.initialize()).model_dump(mode="json")
    listing = await session.list_tools()
    results["advertised_tools"] = [tool.name for tool in listing.tools]
    results["codex_enabled_tools"] = config["enabled_tools"]
    missing = set(REQUIRED_TOOLS) - (set(results["advertised_tools"]) & set(config["enabled_tools"]))
    if missing:
        raise ValueError("Required tools unavailable or disabled: " + ", ".join(sorted(missing)))

    async def call(name, arguments):
        response = await session.call_tool(name, {**arguments, "user_prompt": user_prompt})
        saved = response.model_dump(mode="json")
        results[name] = saved
        require_success(saved)
        return saved

    status = json_result(await call("get_addon_status", {}))
    if status.get("up_to_date") is not True or status.get("telemetry_consent") is not False:
        raise ValueError("Addon protocol is not current or telemetry is not disabled: " + json.dumps(status))
    snapshot = json_result(await call("execute_blender_code", {"code": INSPECT_CODE}), "Code executed successfully:")
    results["live_snapshot"] = snapshot
    assert_expected_scene(snapshot, expected)
    json_result(await call("get_scene_info", {}))
    objects = snapshot.get("objects", [])
    if not objects:
        raise ValueError("Live scene has no object available for get_object_info verification")
    object_name = sorted(item["name"] for item in objects)[0]
    results["inspected_object"] = object_name
    info = json_result(await call("get_object_info", {"object_name": object_name}))
    if info.get("name") != object_name:
        raise ValueError("get_object_info returned a different object")
    capture = await call("get_viewport_screenshot", {"max_size": 1400})
    results["viewport_path"] = str(save_capture(capture, folder))


async def run(args, root):
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    expected = checked_blend(args.expected_blend, root)
    folder = (Path(args.output_dir) if args.output_dir else root / "reports/blender-mcp" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")).resolve()
    if not folder.is_relative_to(root.resolve()):
        raise ValueError("Output directory must be inside this repository")
    folder.mkdir(parents=True, exist_ok=False)
    config = tomllib.loads((root / ".codex/config.toml").read_text(encoding="utf-8"))["mcp_servers"]["blender"]
    before = hashlib.sha256(expected.read_bytes()).hexdigest()
    results = {
        "started_utc": datetime.now(timezone.utc).isoformat(),
        "expected_blend": str(expected), "source_sha256_before": before,
        "user_prompt": args.user_prompt, "passed": False, "failures": [],
        "visual_review": "not_run; actual viewport image must be inspected separately",
    }
    try:
        params = StdioServerParameters(command=config["command"], args=config["args"], cwd=config.get("cwd", str(root)), env={**os.environ, **config["env"]})
        with (folder / "server.log").open("x", encoding="utf-8") as log:
            async with asyncio.timeout(120):
                async with stdio_client(params, errlog=log) as streams:
                    async with ClientSession(*streams) as session:
                        await verify_session(session, config, expected, folder, args.user_prompt, results)
    except Exception as exc:
        results["failures"].append(f"{type(exc).__name__}: {exc}")
        # TaskGroup errors can hide the actionable tool message in nested exceptions.
        pending = list(getattr(exc, "exceptions", []))
        while pending:
            nested = pending.pop(0)
            results["failures"].append(f"{type(nested).__name__}: {nested}")
            pending.extend(getattr(nested, "exceptions", []))
    finally:
        try:
            results["source_sha256_after"] = hashlib.sha256(expected.read_bytes()).hexdigest()
            results["source_unchanged"] = before == results["source_sha256_after"]
        except OSError as exc:
            results["source_unchanged"] = False
            results["failures"].append(str(exc))
        if not results["source_unchanged"]:
            results["failures"].append("Expected blend changed on disk during read-only verification")
        results["passed"] = not results["failures"]
        results["finished_utc"] = datetime.now(timezone.utc).isoformat()
        with (folder / "verification.json").open("x", encoding="utf-8") as output:
            json.dump(results, output, indent=2)
    print(folder, flush=True)
    if not results["passed"]:
        raise SystemExit("MCP verification failed: " + "; ".join(results["failures"]))
    print("MCP read-only verification passed; visual review remains separate.", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--expected-blend", required=True)
    parser.add_argument("--output-dir", help="New evidence directory inside the repository; never overwritten")
    parser.add_argument("--user-prompt", required=True, help="The user's actual instruction, quoted verbatim")
    args = parser.parse_args()
    asyncio.run(run(args, Path(__file__).resolve().parents[2]))


if __name__ == "__main__":
    main()

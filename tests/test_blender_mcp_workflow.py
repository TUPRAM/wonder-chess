"""Regression checks for visible candidate selection and fail-closed MCP evidence."""
import asyncio
import base64
import copy
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
from types import SimpleNamespace
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("verify_mcp", ROOT / "tools/blender/verify_mcp.py")
verify = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(verify)


def text_response(value):
    return {"isError": False, "content": [{"type": "text", "text": value}]}


class Response:
    def __init__(self, value):
        self.value = value

    def model_dump(self, **kwargs):
        return copy.deepcopy(self.value)


class FakeSession:
    def __init__(self, expected):
        self.calls = []
        self.responses = {
            "get_addon_status": text_response(json.dumps({"up_to_date": True, "telemetry_consent": False})),
            "execute_blender_code": text_response("Code executed successfully: " + json.dumps({
                "file": str(expected), "objects": [{"name": "Reference Front", "type": "EMPTY"}]})),
            "get_scene_info": text_response('{"object_count": 1}'),
            "get_object_info": text_response('{"name": "Reference Front", "type": "EMPTY"}'),
            "get_viewport_screenshot": {"isError": False, "content": [{
                "type": "image", "mimeType": "image/png",
                "data": base64.b64encode(b"\x89PNG\r\n\x1a\nfixture").decode()}]},
        }

    async def initialize(self):
        return Response({"protocolVersion": "fixture"})

    async def list_tools(self):
        return SimpleNamespace(tools=[SimpleNamespace(name=name) for name in verify.REQUIRED_TOOLS])

    async def call_tool(self, name, arguments):
        self.calls.append((name, arguments))
        return Response(self.responses[name])


class McpVerificationTests(unittest.TestCase):
    def test_all_tools_use_actual_scene_and_verbatim_prompt(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            expected = (folder / "new.blend").resolve()
            session = FakeSession(expected)
            results = {}
            prompt = "I want to see editing in real time\nKeep my words unchanged."
            asyncio.run(verify.verify_session(session, {"enabled_tools": list(verify.REQUIRED_TOOLS)}, expected, folder, prompt, results))
            self.assertEqual([name for name, _ in session.calls], list(verify.REQUIRED_TOOLS))
            self.assertTrue(all(args["user_prompt"] == prompt for _, args in session.calls))
            self.assertEqual(results["inspected_object"], "Reference Front")
            self.assertTrue((folder / "viewport.png").exists())
            self.assertNotIn("data", results["get_viewport_screenshot"]["content"][0])

    def test_wrong_open_file_stops_after_readback(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            session = FakeSession(folder / "old.blend")
            with self.assertRaisesRegex(ValueError, "Wrong live Blender file"):
                asyncio.run(verify.verify_session(session, {"enabled_tools": list(verify.REQUIRED_TOOLS)}, folder / "new.blend", folder, "test", {}))
            self.assertEqual([name for name, _ in session.calls], ["get_addon_status", "execute_blender_code"])

    def test_text_errors_fail_even_without_mcp_error_flag(self):
        for message in ("Error executing code: disconnected", "Failed to connect", "Could not find object", "Rejected by safe mode - line 1", "Unable to capture"):
            with self.subTest(message=message), self.assertRaises(ValueError) as caught:
                verify.require_success(text_response(message))
            self.assertIn(message, str(caught.exception))
        with self.assertRaisesRegex(ValueError, "bad scene"):
            verify.json_result(text_response('{"error": "bad scene"}'))

    def test_disabled_telemetry_and_tool_allowlist_required(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            session = FakeSession(folder / "new.blend")
            session.responses["get_addon_status"] = text_response('{"up_to_date":true,"telemetry_consent":true}')
            with self.assertRaisesRegex(ValueError, "telemetry"):
                asyncio.run(verify.verify_session(session, {"enabled_tools": list(verify.REQUIRED_TOOLS)}, folder / "new.blend", folder, "test", {}))
            self.assertEqual(len(session.calls), 1)
            session = FakeSession(folder / "new.blend")
            with self.assertRaisesRegex(ValueError, "unavailable or disabled"):
                asyncio.run(verify.verify_session(session, {"enabled_tools": []}, folder / "new.blend", folder, "test", {}))
            self.assertEqual(session.calls, [])

    def test_capture_never_overwrites_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            original = b"existing evidence"
            (folder / "viewport.png").write_bytes(original)
            response = FakeSession(folder / "new.blend").responses["get_viewport_screenshot"]
            with self.assertRaises(FileExistsError):
                verify.save_capture(response, folder)
            self.assertEqual((folder / "viewport.png").read_bytes(), original)
            response["content"][0]["data"] = base64.b64encode(b"not a png").decode()
            with self.assertRaisesRegex(ValueError, "PNG signature"):
                verify.save_capture(response, folder)

    def test_expected_blend_requires_owned_existing_file(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            repo = folder / "repo"
            repo.mkdir()
            candidate = repo / "new.blend"
            candidate.write_bytes(b"fixture")
            self.assertEqual(verify.checked_blend(candidate, repo), candidate.resolve())
            outsider = folder / "outside.blend"
            outsider.write_bytes(b"fixture")
            with self.assertRaises(ValueError):
                verify.checked_blend(outsider, repo)
            with self.assertRaises(ValueError):
                verify.checked_blend(repo, repo)


@unittest.skipUnless(shutil.which("powershell"), "Windows PowerShell is unavailable")
class VisibleLauncherTests(unittest.TestCase):
    def invoke(self, script, candidate, existing=False):
        def quoted(value):
            return "'" + str(value).replace("'", "''") + "'"
        process = "[pscustomobject]@{Id=123}" if existing else ""
        command = """
function Get-Process { [CmdletBinding()] param([string]$Name) PROCESS_VALUE }
function Start-Process {
    param($FilePath, $WindowStyle, $ArgumentList, $WorkingDirectory, $RedirectStandardOutput, $RedirectStandardError, [switch]$PassThru)
    [pscustomobject]@{window=$WindowStyle; arguments=$ArgumentList; cwd=$WorkingDirectory} | ConvertTo-Json -Compress
}
& SCRIPT_VALUE -BlendFile CANDIDATE_VALUE
""".replace("PROCESS_VALUE", process).replace("SCRIPT_VALUE", quoted(script)).replace("CANDIDATE_VALUE", quoted(candidate))
        return subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", command], capture_output=True, text=True)

    def test_visible_launch_validation_and_existing_session_refusal(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            repo = folder / "repo"
            script = repo / "tools/blender/Start-Mcp.ps1"
            script.parent.mkdir(parents=True)
            shutil.copyfile(ROOT / "tools/blender/Start-Mcp.ps1", script)
            candidate = repo / "art-source/asset-studio/hero/live/candidate.blend"
            candidate.parent.mkdir(parents=True)
            candidate.write_bytes(b"fixture")
            launched = self.invoke(script, candidate)
            self.assertEqual(launched.returncode, 0, launched.stderr)
            value = json.loads(launched.stdout)
            self.assertEqual(value["window"], "Normal")
            self.assertEqual(value["arguments"][:2], ["--factory-startup", "--disable-autoexec"])
            self.assertIn(str(candidate), value["arguments"][2])
            refused = self.invoke(script, candidate, existing=True)
            self.assertNotEqual(refused.returncode, 0)
            self.assertIn("already open", refused.stderr)
            outsider = folder / "outside.blend"
            outsider.write_bytes(b"fixture")
            refused = self.invoke(script, outsider)
            self.assertNotEqual(refused.returncode, 0)
            self.assertIn("inside this repository", refused.stderr)


if __name__ == "__main__":
    unittest.main()

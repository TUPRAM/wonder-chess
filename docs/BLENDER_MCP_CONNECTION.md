# Wonder Chess Blender MCP connection

Verified 2026-09-08 Singapore time. The supplied Blender MCP server connects to the actual Blender 5.1.1 process and Ada source scene. The Codex desktop tool list still needs a restart to load the new project configuration.

## Installed connection

- Project configuration: `.codex/config.toml`, server name `blender`. It is scoped to this trusted Wonder Chess workspace. The global Codex configuration was not changed.
- Supplied ZIP: `C:\Users\iputu\Downloads\blender-mcp-main (1).zip`, SHA-256 `a7576e30ee43bc379af2c6bab27749c48b8b1a1380068112910498e5d672f005`.
- Reviewed source and isolated Python environment: `C:\Users\iputu\Documents\Project Support\Wonder Chess\blender-mcp-1.9.1\blender-mcp-main`.
- Server package 1.9.1; bundled add-on declares 1.6; both agree on protocol 5. Python 3.11.8, MCP SDK 1.29.0, uv 0.11.28, Codex CLI 0.153.4.
- Add-on: `C:\Users\iputu\AppData\Roaming\Blender Foundation\Blender\5.1\scripts\addons\blender_mcp.py`. Byte-identical to the supplied bundled add-on.
- Transport: Codex stdio server connects to Blender's TCP listener on `127.0.0.1:9876`.
- Existing **Codex Blender Realtime MCP Bridge** (`blender_addon`, port 9877) was preserved and not started by this task. Its protocol is separate.

The server uses the supplied `uv.lock`. An offline install first failed because pinned dependencies were missing from cache; the subsequent install fetched Python dependencies from PyPI. No assets were downloaded.

The ZIP is missing `src/blender_mcp/config.py`, which its telemetry module imports. A local compatibility file was added containing `from types import SimpleNamespace` and `telemetry_config = SimpleNamespace(enabled=False)`. It contains no service credentials or upload configuration. Keep this local patch when recreating the runtime; no upstream server/add-on source was otherwise changed.

## Use now

1. Leave Blender open. Ada's existing source file is loaded; no `.blend` file was saved or modified.
2. Restart Codex and reopen this Wonder Chess workspace. Verify the `blender` server in MCP settings. The current conversation cannot hot-load a new native tool list merely by editing configuration.
3. Ask: **“Use Blender MCP to inspect the open Wonder Chess scene and take a viewport screenshot before editing.”**

Enabled tools: `get_addon_status`, `get_scene_info`, `get_object_info`, `get_viewport_screenshot`, `execute_blender_code`. Scene/object calls require `user_prompt`; the verifier passes the user's actual connection request.

Telemetry is disabled in both the server environment and saved Blender add-on preferences. Asset-service integrations are disabled. `BLENDER_MCP_SAFE_MODE=1` enables upstream AST validation for code tools; it permits Blender modeling, materials, rendering, saving and import/export, and rejects arbitrary OS/network/subprocess code. It is a code validator, not an OS sandbox. No firewall, global permission policy, or remote access settings were broadened.

## Reopen Blender later

From the Wonder Chess workspace in PowerShell:

```powershell
& '.\tools\blender\Start-Mcp.ps1'
```

The launcher opens the canonical Ada file, disables embedded-file script auto-execution, enables the installed add-on, turns off telemetry and optional asset services, and writes startup logs under `reports/blender-mcp`. It preserves an already open Blender session by refusing to launch another instance. It does not save the source file. An optional `-BlendFile` selects another existing source file.

If Blender is already open, use its **MCP for Blender** sidebar on port 9876. The upstream add-on normally auto-starts on activation; use **Start MCP Server** if it is stopped. Do not start the separate Codex MCP bridge as a substitute for this server.

Repeat the live check with the installed environment:

```powershell
& 'C:\Users\iputu\Documents\Project Support\Wonder Chess\blender-mcp-1.9.1\blender-mcp-main\.venv\Scripts\python.exe' '.\tools\blender\verify_mcp.py'
```

This creates a fresh evidence folder, performs real MCP initialize/list-tools/tool calls, and checks the Ada source hash before and after. Run it while the scene contains Ada; the object-detail check intentionally targets `SK_wc_u_human_guardian`.

## Evidence and limits

- `reports/blender-mcp/20260907T232817Z/verification.json`: five live tool checks passed; protocol matched; telemetry consent false; source unchanged. Scene: 12 objects, Ada meshes and all seven named animation actions.
- Same directory: `viewport.png`, `server.log`, `installation.json` with hashes and versions.
- Initial run `20260907T232735Z` retained: `get_scene_info` failed because the verifier omitted required `user_prompt`. The verifier was corrected, and the fresh run above passed.
- Viewport inspection proves access to the live scene; it is not character art approval or continuous animation review.
- Full game tests, packaging and LAN acceptance were not rerun for this connection-only task. Existing release evidence remains separate.
- Direct integration into the restarted Codex desktop tool list remains to be observed. The current task successfully verified the same configured server through an actual MCP stdio client.

## Recovery

The pre-install Blender preferences backup is at `C:\Users\iputu\Documents\Project Support\Wonder Chess\blender-mcp-1.9.1\pre-install\userpref.blend`. To disconnect normally, stop/disable **MCP for Blender** and set `enabled = false` in the project's `[mcp_servers.blender]` table, then restart Codex. Keep the older custom bridge and source assets intact. Do not restore old preferences over newer unrelated settings without reviewing the differences.

Configuration syntax follows [OpenAI's MCP documentation](https://learn.chatgpt.com/docs/extend/mcp?surface=cli), including project-scoped configuration, tool allowlists and stdio environment variables.

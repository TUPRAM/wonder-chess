# Wonder Chess Blender MCP connection

Installation first verified 2026-09-08 Singapore time; original evidence is retained below. The current AS1 live-editing check uses a separate new Ada candidate. Native Codex Blender MCP calls and visible Computer Use were exercised in this session; see `reports/AS1/live-mcp/` for current evidence.

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

For a fresh Git clone, the machine-specific `.codex/config.toml` is intentionally ignored. Copy `.codex/config.example.toml` to `.codex/config.toml` and set `command` to the Python executable in your installed Blender MCP environment. The example does not install the server or add-on. The absolute installation and launcher paths below describe the verified original workstation; adjust them for another PC.

1. Open an explicit writable candidate with the visible launcher below. Preserve sealed stage snapshots and existing character sources.
2. If Blender is already open, inspect its actual filename and MCP status before editing. Do not launch another instance over an existing session.
3. Ask: **“Use Blender MCP to inspect the open Wonder Chess scene and take a viewport screenshot before editing.”** If a new installation's native tools are absent, refresh/restart Codex and verify its project MCP settings; editing configuration alone does not prove tool access.

Enabled tools: `get_addon_status`, `get_scene_info`, `get_object_info`, `get_viewport_screenshot`, `execute_blender_code`. Scene/object calls require `user_prompt`; the verifier passes the user's actual connection request.

Telemetry is disabled in the server environment and in the active Blender add-on preferences. The visible launcher sets preferences in memory and disables their auto-save, preserving saved user defaults. Asset-service integrations are disabled. `BLENDER_MCP_SAFE_MODE=1` enables upstream AST validation for code tools; it permits Blender modeling, materials, rendering, saving and import/export, and rejects arbitrary OS/network/subprocess code. It is a code validator, not an OS sandbox. No firewall, global permission policy, or remote access settings were broadened.

## Reopen Blender later

From the Wonder Chess workspace in PowerShell:

```powershell
& '.\tools\blender\Start-Mcp.ps1' -BlendFile '.\art-source\asset-studio\wc_u_human_guardian\live\ada_live_mcp_r001.blend'
```

`-BlendFile` is required and must select an existing repository `.blend` without symbolic-link/junction traversal. The launcher opens it in a normal visible window with factory settings for this new process, disables embedded-file script auto-execution, enables the installed add-on, turns off telemetry and optional asset services, and writes startup logs under `reports/blender-mcp`. It preserves an already open Blender session by refusing to launch another instance. It does not save the blend or user preferences. The command above selects the AS1 live candidate, not a sealed approval snapshot.

If Blender is already open, use its **MCP for Blender** sidebar on port 9876. The upstream add-on normally auto-starts on activation; use **Start MCP Server** if it is stopped. Do not start the separate Codex MCP bridge as a substitute for this server.

Repeat the live check with the installed environment:

```powershell
& 'C:\Users\iputu\Documents\Project Support\Wonder Chess\blender-mcp-1.9.1\blender-mcp-main\.venv\Scripts\python.exe' '.\tools\blender\verify_mcp.py' --expected-blend '.\art-source\asset-studio\wc_u_human_guardian\live\ada_live_mcp_r001.blend' --user-prompt 'Paste the user instruction verbatim here'
```

This creates a fresh evidence folder, performs real MCP initialize/list-tools/all-five-tool calls, reads the actual open file and object inventory, and checks the selected candidate's on-disk hash before and after. The object-detail check selects an object actually present in that scene. A wrong file, disabled tool, stale protocol, telemetry consent, tool error text, missing PNG, or changed file fails verification. Optional `--output-dir` must be a new directory inside this repository; existing evidence is never overwritten. Inspect the saved viewport image separately for visual acceptance.

## Evidence and limits

- `reports/blender-mcp/20260907T232817Z/verification.json`: five live tool checks passed; protocol matched; telemetry consent false; source unchanged. Scene: 12 objects, Ada meshes and all seven named animation actions.
- Same directory: `viewport.png`, `server.log`, `installation.json` with hashes and versions.
- Initial run `20260907T232735Z` retained: `get_scene_info` failed because the verifier omitted required `user_prompt`. The verifier was corrected, and the fresh run above passed.
- Viewport inspection proves access to the live scene; it is not character art approval or continuous animation review.
- Full game tests, packaging and LAN acceptance were not rerun for this connection-only task. Existing release evidence remains separate.
- The original installation only verified an MCP stdio client. The later AS1 session exercised native Codex MCP tools and the visible Blender window; `reports/AS1/live-mcp/verification-before-restart/verification.json` records all five tools against the separate live candidate.

## Recovery

The pre-install Blender preferences backup is at `C:\Users\iputu\Documents\Project Support\Wonder Chess\blender-mcp-1.9.1\pre-install\userpref.blend`. To disconnect normally, stop/disable **MCP for Blender** and set `enabled = false` in the project's `[mcp_servers.blender]` table, then restart Codex. Keep the older custom bridge and source assets intact. Do not restore old preferences over newer unrelated settings without reviewing the differences.

Configuration syntax follows [OpenAI's MCP documentation](https://learn.chatgpt.com/docs/extend/mcp?surface=cli), including project-scoped configuration, tool allowlists and stdio environment variables.

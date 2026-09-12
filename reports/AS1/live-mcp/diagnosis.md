# Visible Blender MCP diagnosis

Read-only inspection on 2026-09-08, approximately 12:22-12:25 Asia/Singapore. No Blender process was started, stopped or mutated by this diagnostic lane. The earlier observations describe that inspection time, not subsequent root-lane work.

## Findings

- No `blender.exe` process and no TCP listener on port 9876 were present during the initial inspection. The configured MCP Python executable exists. The immediate connection failure is consistent with an absent GUI-side Blender server.
- `.codex/config.toml` enables five Blender tools against `127.0.0.1:9876`, with telemetry disabled and safe mode enabled. No configuration change is needed merely to restore the missing GUI endpoint.
- The installed add-on and bundled add-on are byte-identical: SHA256 `F43469C8518C7021E0060E32CFE52E3BEB126B0F62FBAE7293106642A3EBDA89`. Both declare protocol 5. The source package is the local `Project Support/Wonder Chess/blender-mcp-1.9.1/blender-mcp-main` installation.
- The add-on refuses background Blender because its command queue needs the GUI main thread. It uses an IPv4 socket with default host `localhost`; its register path automatically starts the listener when the scene auto-start setting is enabled. The configured client address is loopback.
- `tools/blender/Start-Mcp.ps1` currently starts Blender with `-WindowStyle Hidden` and, without `-BlendFile`, selects the old canonical Ada. That default is inappropriate for this request to see AS1 work in real time.
- `tools/blender/verify_mcp.py` hardcodes the old canonical Ada path and `SK_wc_u_human_guardian` object. It is unsuitable for the fresh AS1 reference scene without parameterization.
- `tools/blender/start_mcp.py` enables the reviewed add-on, disables telemetry consent and external asset integrations, and starts its server without saving the opened blend. It saves user preferences. Its direct `bpy.types.blendermcp_server.running` access assumes register created a server; an explicit existence check would handle scenes with auto-start disabled.
- Historical GUI evidence at `reports/blender-mcp/20260908T072720-blender.log` records a successful server on localhost:9876 followed by orderly addon unregister and Blender quit. It is not a current connection test. The last shutdown socket error occurs during teardown and is not evidence of a presently broken package.

## Minimal durable changes recommended

1. Require an explicit `.blend` path in the launcher, use a visible normal window for this user-authorized interactive workflow, retain refusal to interfere with an already-open Blender session, and launch with factory settings before the explicit candidate and reviewed bootstrap.
2. Open a writable, isolated live-session copy of the sealed AS1 reference scene. Never use or overwrite the old Ada or sealed reference snapshot for MCP smoke changes.
3. Parameterize verification with the expected live file. Read back the actual open file before any mutation, inspect an object that is actually present, check addon protocol/telemetry, capture the viewport, and check the original sealed source hash independently.
4. Preserve `BLENDER_MCP_SAFE_MODE=1`. It allows normal bpy modeling and file save/open, while rejecting execution escapes, process/network modules, timer persistence and embedded code operations. Bounded visible edits can be issued as sequential calls without weakening this control.
5. Verify one reversible marker creation/transformation/deletion through MCP in the visible session and inspect real captures. Leave artistic reference approval unchanged.

No official documentation lookup, editor execution, installed-package mutation, source-art mutation or MCP command was performed in this read-only lane. Root owns the live Blender session and all resulting execution evidence.

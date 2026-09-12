# Uploaded Blender MCP archive — source audit

**Archive:** `blender-mcp-main (1).zip`  
**SHA-256:** `a7576e30ee43bc379af2c6bab27749c48b8b1a1380068112910498e5d672f005`  
**Declared package version:** 1.9.1. This is the uploaded source, not proof of the user's running version or enabled configuration.

Only text was inspected. No addon, server, scripts or integrations were executed.

## Confirmed source behavior

| Topic | Source location | Finding |
|---|---|---|
| Version | `pyproject.toml:3` | Declares 1.9.1. |
| Viewport feedback | `src/blender_mcp/server.py:461–497` | Screenshot tool returns an MCP Image; signature defaults to max_size=1000, while its prose still says 800. |
| Image dimensions | `addon.py:1274–1355` | Addon default is 800, but passed parameters override it. Code downsizes when source dimensions exceed the cap; it does not promise new source detail by raising the cap. |
| Modeling access | `src/blender_mcp/server.py:557–588` | Code execution supports Blender operations, with small-step guidance and safe-mode validation when enabled. Nothing here establishes a low-poly modeling limitation. |
| Timeout | `src/blender_mcp/server.py:84,162` | Socket timeouts are set to 180 seconds. This is implementation behavior, not permission to assume timed-out edits never ran. |
| Optional providers | Server tool definitions and uploaded README | Optional asset/generation integrations exist. Configuration, budget, external terms, and quality were not verified. |
| Privacy | `TERMS_AND_CONDITIONS.md:15–38`; telemetry module | With consent, described data includes prompts, code, scene metadata, screenshots, trajectories and manual edit events. Section 2 also describes minimal usage data without consent. |
| Full telemetry controls | `src/blender_mcp/telemetry.py:103–117` | Reads disable environment variables including DISABLE_TELEMETRY and BLENDER_MCP_DISABLE_TELEMETRY. Verify actual process configuration/restart before relying on a setting. |

## Privacy wording discrepancy

Section 2 of the supplied terms says minimal anonymous usage records can still be sent without consent. Section 5 also contains a broader 'no data' opt-out statement. The implementation explicitly contains a no-consent minimal-usage path. This audit preserves that discrepancy rather than treating the broad wording as a full no-network guarantee. Review the environment-level disable behavior when confidentiality matters; no settings were modified here.

## Safe-mode boundary

The source's safe-mode rejection message permits appropriate Blender modeling/render/save/import/export operators but rejects several general file/process/execution mechanisms. Do not ask Codex to disable or circumvent it to run convenient file-evaluation snippets. Use allowed MCP operations, or separately authorized trusted local tools.

## Recommendations

Use the existing bridge for scene inspection, named-part edits and real image feedback. Use fixed-camera saved renders for review rather than relying only on viewport dimensions. On timeout inspect state before retrying. Keep one writer per Blender scene. Review telemetry and external-upload consent before processing unpublished character designs. Additional 3D-generation providers are optional concept routes, not a replacement for art approval, cleanup, UVs and rigging.

## File hashes of inspected archive sources

- `pyproject.toml`: `c1034c4904b8ba8cb51188843917c280bd1db9ce47f9de8a218ae2c9e685236e`
- `src/blender_mcp/server.py`: `cb42d7a4e69b7711c018a5d3c1ee2d6c90d2fb0a5a5d27e8571469f3f2a902dc`
- `addon.py`: `f43469c8518c7021e0060e32cfe52e3beb126b0f62fbae7293106642a3ebda89`
- `src/blender_mcp/telemetry.py`: `09c5bc161f85f11c1026741cfe3f0a9899926af5d3fc2f27bec1b57d987849d7`
- `src/blender_mcp/safe_mode.py`: `d3bc1f43f4707476e595efed111d514b3f81bf4358993b8accb18962c5c4bf35`
- `TERMS_AND_CONDITIONS.md`: `bf949d95a23387dbe064fdf1d9085dc8ae0837904b42a860d747c69774e7aeaa`

# Meshy workflow setup — 17 September 2026

## Executed connections

| Connection | Evidence | Result |
|---|---|---|
| Official Meshy MCP 0.5.1 | `mcp-verification.json` | Authentication, 24-tool discovery and balance passed. Project Codex config installed; application reload still required for new native tool discovery. |
| Blender Meshy 0.6.1 on Blender 5.2.1 | `bridge-install.json`, `bridge-start.json`, `bridge-verification.json` | Extension loaded; local HTTP status and actual GLB transfer, MCP scene inspection, save and FBX export passed. |
| Blender FBX → Unreal 5.8.2 | `unreal-transport.json`, `unreal-transport.log` | Isolated-project static mesh import passed. One-meter cube measured 100 cm on every axis. |
| Duplicate-submission safeguard | `retry-guard-test.json` | One POST attempt on simulated failure; read-only GET retains bounded retries. No network request in this test. |

The calibration is a locally authored cube. It does not prove Bellback likeness, animation, texture transport, game performance or art acceptance. Meshy's website Send to Blender UI has not been exercised. No direct Unreal Meshy plugin was installed; Unreal uses the verified Blender export route.

## Installations and repairs

- Downloaded official Blender ZIP 0.6.1 from `https://cdn.meshy.ai/meshy-for-blender/meshy-blender-plugin-v0.6.1.zip`. Found an existing matching extension during setup; verified source files against the ZIP and preserved it under `support/archives/meshy-before-loopback-20260917`.
- Patched only the extension server bind from all interfaces to `127.0.0.1:5324`. Original ZIP and extracted vendor sources remain under `support/external/meshy`.
- Installed pinned official npm package `@meshy-ai/meshy-mcp-server@0.5.1` using npm 12.0.2 and the existing Node 24.19.0. Downloaded npm's SHA-512 matched registry metadata. Dependency install used `--ignore-scripts`; `package-lock.json` preserves resolved package integrity.
- Patched `meshy-client.js` so only GET requests automatically retry. Original retained as `support/external/meshy/meshy-client.original.js`. This prevents an uncertain create response from triggering another paid generation.
- Key is DPAPI encrypted for the current Windows user outside the project. The launcher decrypts into its child-process environment without printing it. This does not make the key portable to a different Windows user/PC; use **Set Meshy API Key.cmd** again after transfer.
- Windows PowerShell launcher explicitly imports its own security module because the calling PowerShell 7 environment initially caused a module-path conflict. It trims the encrypted file's newline before decoding. The final real MCP verification passed.

## Bellback authorization and task

The owner approved the displayed regenerated isolated image: **“Use this image for one candidate”**, in response to the explicit 20-credit geometry-only proposal. Input provenance records the exact question and response. This approves the single upload/generation, not the resulting 3D forms.

Task: `01a0ae18-2c30-7635-9165-15db87ba0fbc`.

**Succeeded.** The original **112,061,588-byte GLB** is preserved. Actual consumption **20 credits**; balance changed from **3,118 to 3,098**. No second generation or texture/rigging operation was submitted.

Blender imported it, normalized total height to 2.2 m, corrected facing to +Y, saved an editable candidate and reopened it successfully. Clay views and an underside inspection were actually viewed. The 3,513,982-triangle model has useful organic forms but major bell/back/support construction defects. See the asset's `stages/forms/meshy_r001/REVIEW.md`; status **REVISE**, not forms acceptance.

Working source: `art-source/asset-studio/wc_vn_bellback/stages/forms/meshy_r001/Bellback_forms_oriented.blend`.

Input/task receipts: `art-source/asset-studio/wc_vn_bellback/inputs/meshy/r001/`.

Meshy 7, standard geometry, Ultra off, textures off, remesh off, GLB only. The original approved sheet remains untouched. The clean input is a regenerated view, not an exact crop; actual prompt and source/input hashes are recorded.

## Session handling and known limits

The owner's existing unsaved Blender session is preserved. Transport tests used a separately named test `.blend` and a separate MCP port 9877. The normal connection remains 9876. An early test attempted the wrong port; its failed receipt is retained as `bridge-verification-r2-failed.json`. The subsequent test passed with the dedicated port. No failed receipt is counted as acceptance.

**Open Bellback Meshy.cmd** is the reusable candidate launcher. Save and close existing Blender sessions before using it. It enables both reviewed bridges in the selected candidate session without saving factory preferences. Updating the on-disk extension does not reload code already loaded by the owner's existing Blender process; start a fresh session to get the loopback patch.

Human forms approval and all dependent production stages remain open. The new generation is an isolated candidate and does not replace the game's Bellback proxy or modify gameplay data.

At completion, the temporary test Blender process was identity-checked and closed; its ports 5324/9877 were released. The owner's existing Blender process and normal MCP port 9876 were left running. The convenience launcher and its Python source are installed and configuration-checked, but the combined interactive launch was not run because it intentionally refuses to replace an existing Blender session. Its component connections were executed independently as documented above.

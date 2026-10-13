# New PC repair and connection tests — 16 September 2026

## Outcome

**Blender control and Blender-to-Unreal asset exchange pass. File recovery and the game build environment remain incomplete.** No production art was resaved, no preserved package was overwritten, and the Wonder Chess project was not converted to Unreal 5.8.

## Completed

- Recovered **424 exact original files** from local manifest-matching copies, Git objects and hash-verified newline variants. Existing files and the Git index were preserved. See [recovery evidence](recovery/).
- Created a fresh project `.venv` with the declared authoring dependencies and local Blender MCP 1.9.1 package. `pip check` passes; [installed versions](python-packages.txt) are retained. This environment uses Codex's bundled Python 3.12.14 as its base and should be recreated if that runtime is removed or the project moves again.
- Repaired `.codex/config.toml` to use this user's root and new Python environment. Installed/enabled the retained addon in Blender 5.2.1. Previous config/preferences were backed up under [blender/](blender/). Telemetry is disabled; MCP safe mode is enabled; the live listener is **127.0.0.1:9876**.
- Updated `tools/blender/Start-Mcp.ps1` to accept `-BlenderExe`/`BLENDER_EXE` and discover installed Blender 5.2 or 5.1. Existing candidate path validation and refusal to replace an open session remain. The launcher parses successfully; its Windows PowerShell test is blocked by execution policy. This is an intentional post-recovery edit.
- Exercised the actual configured MCP process: initialize/protocol handshake, scene read, temporary object create/read/remove, object inspection, and viewport PNG delivery all pass. The image was viewed and shows the diagnostic cube. Read-only verification kept the `.blend` hash unchanged. [MCP verification](blender/live-verification/verification.json), [viewport](blender/live-verification/viewport.png), [write/read test](blender/mcp-check.json).
- Unreal **5.8.2** executed Python, imported Blender's one-metre FBX cube, saved the mesh, and reloaded it in a fresh process. Dimensions are approximately **100 × 100 × 100 cm**, with 12 triangles. All successful probe processes exited 0. [Unreal evidence](unreal/README.md).
- All four authoring checks pass: `validate_kit.py` (**400 checks**), `build_documents.py --check`, `compile_catalog.py --check`, and `tools/vnext/catalog.py --check`.

The live Blender diagnostic process is left available for connection testing. Its scene is the isolated `support/diagnostics/new-pc-20260916/blender/WC_ConnectionProbe.blend`; no production asset is open. The desktop task's already-loaded tool list did not gain a Blender namespace during this run. The saved configuration itself was tested end-to-end through an MCP client; reload the project/task connection to load it into Codex's normal tool list.

## Incomplete recovery

**285 original payloads remain unrecovered** (284 absent files and one regenerated cache that is not the original). Git integrity passes after recovery. Nine source/tool files still require the original complete folder or another backup:

- `tools/verify_transfer.py`
- `tools/unreal/create_combat_cue_material.py`
- `tools/unreal/import_art_slice.py`
- `tools/unreal/import_storybook.py`
- `tools/unreal/launch_milestones.ps1`
- `tools/vnext/analyze_mana_experiment.py`
- `tools/vnext/verify_milestone_package.py`
- `tests/runtime/run_vnext_balance_experiment.ps1`
- `tests/runtime/vnext_balance_experiment.cpp`

Historical support files and old bytecode caches also remain unrecovered. Newly generated caches are not recovered originals. No older script was substituted and no missing file was recreated under its original name. The root play shortcut still depends on the missing `launch_milestones.ps1`.

The original 78,029 present payload files passed the earlier full hash audit. This repair verifies restored originals against that manifest; it does not recertify intentional new configuration, reports, caches, or source changes as original transfer bytes.

## Tests and limitations

The latest discovery run attempted **221 tests: 219 passed, one failed, one import error**. [Complete log](python-tests-final.log).

- One import error is caused by missing `verify_milestone_package.py`; its full test module cannot execute.
- The launcher test invokes **Windows PowerShell**, whose execution policy is `Restricted`. It refuses to execute the test's temporary `.ps1`. This differs from the installed PowerShell 7 shell. No security policy was changed or bypassed to make the test pass.

These are not a passing full suite. The original nine source files, compiler and correct Unreal engine remain necessary for complete verification. The static-mesh probe does not certify skeletal animation, rendering, gameplay, packaging, performance or production art acceptance. The import's smoothing-group warning is documented in the Unreal report.

## Required user actions

1. Provide the path to the original complete Wonder Chess folder, transfer drive or backup so remaining missing files can be recovered by exact hash.
2. Right-click [Install Wonder Chess Build Tools.cmd](../../support/tools/installers/Install%20Wonder%20Chess%20Build%20Tools.cmd) → **Run as administrator**, approve Microsoft's prompt and let it finish. The downloaded official VS2022 bootstrapper has a valid Microsoft signature; its configuration selects MSVC 14.44 and Windows SDK 22621. [Installer provenance and instructions](build-tools/README.md).
3. In **Epic Games Launcher → Unreal Engine → Library → + Engine Versions**, select **5.7.4 if offered** and install it alongside 5.8. The dropdown was not accessible with the available browser-only UI tools; patch availability remains unverified. Wonder Chess still targets 5.7.
4. After installation, run the prepared [compiler/SDK verifier](../../support/diagnostics/new-pc-20260916/build-tools/Verify-BuildTools.ps1) and complete a 5.7 project build into a new candidate output. No compiler or SDK installation is claimed yet.

Automatic approval review rejected the agent's Microsoft installer command before execution with the reason **“blocked by policy.”** The Windows token is also non-administrator. The agent did not retry or bypass that rejection; administrator installation requires the user's action.

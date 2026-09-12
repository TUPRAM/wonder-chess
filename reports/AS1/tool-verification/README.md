# AS1 local tool verification

Date: 2026-09-08. Status: **PASS for the exercised Blender fixture operations**. Unreal installation metadata was verified read-only; Unreal execution is **NOT RUN** in this lane.

The delegated scope was to prove the three shipped Blender helpers against the installed Blender API, on a new owned fixture. All outputs remain inside `reports/AS1/tool-verification`. No current Ada source, user GUI scene, roster, game content, or shared implementation-state file was edited or loaded by this verification lane.

## Evidence and results

| Operation | Actual evidence | Result |
| --- | --- | --- |
| Installed Blender and CLI | `blender-version.txt`, `blender-help.txt` | Blender **5.1.1**, build `b70da489d7f4`; CLI options verified using installed `--help`. |
| Installed API inspection | `installed-bpy-api.json`, `create-fixture.log` | Actual `bpy` operator documentation and required RNA properties read in a new background process. |
| New editable fixture | `fixture.blend`, `create_fixture.py` | New weighted box, unskinned sphere, one-bone armature; no existing character source. |
| Dry run | `dry-run.json` | Command printed; requested audit output was not created. |
| Calibrated image setup | `final-reference-setup.log`, `final-fixture-with-references.blend`, `final-reference-audit.json` | Hash-checked 320 by 512 image loaded into a new reference collection and new candidate `.blend`; exit 0. |
| Wrong image hash rejection | `reference-reject.log` | Exit **23**, `Image hash mismatch`, rejected candidate does not exist. This negative check used the original runner; the Blender-side helper remained unchanged. |
| Geometry, weights and skeleton audit | `final-scene-audit.log`, `final-scene-audit.json` | Exit 0. Weighted box: 8 vertices, 12 triangles, zero unweighted/non-normalized vertices, one deform influence. Sphere: 266 vertices/528 triangles; unskinned fields remain null. Zero degenerate source triangles in both. |
| Fixed material review renders | `final-render-material.log`, `final-renders-material/` | Exit 0, front and three-quarter PNGs, actual captures inspected. |
| Fixed clay review renders | `final-render-clay.log`, `final-renders-clay/` | Exit 0, front and three-quarter PNGs, actual captures inspected. |
| Source preservation | `final-execution-results.json` | Both source and reference candidate hashes remain unchanged after audits/renders. |
| Installed Unreal | `unreal-build-version.json`, `unreal-binaries.json`, `unreal-read-only.json` | Unreal **5.7.4**, editor and commandlet binaries present; project targets 5.7 and enables the editor scripting plugins; installed Python plugin DLL present. |
| Unreal launch/import/reimport/package | `unreal-read-only.json` | **NOT RUN**. Metadata and binary presence do not verify an operational integration. |

The helper runner initially loaded saved Blender addons in its separate process: original logs contain `BlenderMCP` addon messages. The integration owner corrected `run_blender.py` to put `--factory-startup` before the explicit source while retaining `--disable-autoexec`. `verify_final_runner.py` reran all three helpers against fresh destinations after that change. All passed, and the five final helper logs contain no BlenderMCP addon messages. Original evidence remains preserved to distinguish the first run from the correction.

Final runner SHA-256: `04aca90bdbd9b370dacbb534a714bfcb1572d96f035ea3815975365081eba46e`.

Fixture source SHA-256: `63ed5d74faf051ffe331c8972f9dc2dfb4a44e7e3cc3825ef5aa85f28ca99ecb`.

Final reference candidate SHA-256: `66faadfdac8f9d53be925adebd1bd0c2f9e4d01261d547c4cd12191d5e1f7313`.

## Available operation mapping

The verified local path is Python `run_blender.py` to the installed Blender CLI, then one of `reference_setup`, `scene_audit`, or `render_review`, with explicit source and output locations. The runner defaults to a dry run, records the executed command, uses a bounded timeout, and gives helper exceptions a nonzero exit code.

The tool inventory exposes Blender MCP scene/object information, addon status, code execution and viewport screenshot operations. This lane did not invoke those operations or connect to an active editor. Their availability in the inventory does not establish a working connection; the orchestrator records its separate connection probe.

No Unreal MCP operation was exposed in the discovered tool inventory. Installed Unreal editor/commandlet binaries and existing project editor scripting configuration provide candidate local automation paths. No runtime importer or export profile was certified by this fixture test.

## Reproduction and limits

`run_verification.py` creates the original fixture and runs dry-run, positive import, negative hash, audit, and material/clay checks. `verify_final_runner.py` records the post-isolation-fix run. Both deliberately require new output locations. Do not rerun into the retained evidence paths; create a new owned evidence revision and adjust those fixture-only output paths first.

See `VISUAL_REVIEW.md` for observations on the actual captures. This smoke covers exercised local API paths and basic expected values. It does not provide exhaustive geometry validation, likeness judgment, topology quality, UV/bake quality, real character skinning, continuous motion, FBX export, Unreal integration, reimport, performance, packaged gameplay, or any Ada approval.

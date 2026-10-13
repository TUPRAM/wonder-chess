# Qualified tools and repeatable commands

**Local qualification: 21 September 2026, handbook 1.2.** Read the
[evidence packet](../../reports/pipeline-tools-20260921/README.md) for what actually
ran. Installed tools are not all MCP servers; use the integration mode below.

## 1. Installed applications and their jobs

| Tool | Actual integration | Qualification and limit |
|---|---|---|
| Krita 5.3.4 | Native UI and built-in Scripter; layered `.kra` and OpenRaster sources; PNG interchange | Two-layer fixture preserved exact pixels. Cragstoat executed native uniform scaling, padding and four-PNG/layered-sheet export; originals stayed unchanged. Headless export was not qualified. |
| UE 5.8.2 Modeling Mode / UV Editor / Geometry Scripting | Bundled editor plugins plus versioned Python recipes | Created high/low meshes, repacked UVs, computed tangents and baked a 256px normal map. This is tool qualification, not production bake quality. |
| UE skeleton editing / Sequencer / Control Rig | Bundled editor tools; editable Unreal sources | Added a bone to a private Bellback copy with a private skeleton; saved and reopened it. Sequencer creation/reopen passed; existing Bellback control studies remain separate evidence. |
| UE Data Validation | Explicit Python validator registration per process | Good fixtures passed; wrong scale, missing dependency/socket and broken binding were rejected. No automatic discovery assumption. |
| Unreal Insights | Local `.utrace` file analysis and CSV export | CPU trace analysis/export exercised. GPU/crowd/memory acceptance requires separate actual package measurements. |
| Audacity 4.0.0 | Native UI; `.aup4` editable sessions; PCM WAV exchange | Imported and saved a session, exported bit-identical 48kHz mono PCM. No script-pipe/MCP connection claimed for this version. |
| OBS 32.2.2 | Built-in Lua scripting; image-only qualification recording | Eight-second recording decoded and viewed; global audio was muted during capture and prior scene/mutes restored. No network or streaming setup required. |
| Git LFS 3.7.1 | Repository-local hooks/filters plus hydrated backups | Fresh local clone and object-store recovery preserved exact bytes. Remote storage, quota and upload were not tested. |
| MeshLab 2025.07 | Native UI diagnostic copies; OBJ exchange | Cube import/export preserved geometry, dimensions and UVs. Never treat this as a qualified rig or animation round trip. |

The Unreal features were already shipped with the installed engine. Setup enabled
the missing editor plugins in [WonderChess.uproject](../../game/WonderChess.uproject);
no separate marketplace download was needed. All newly enabled plugins are scoped
to the editor target. Validate a future packaged candidate for editor-only leakage.

Executable locations on this PC:

- Krita: `C:/Program Files/Krita (x64)/bin/krita.exe`
- Unreal: `C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/`
- Audacity: `C:/Program Files/Audacity 4/bin/Audacity4.exe`
- OBS: `C:/Program Files/obs-studio/bin/64bit/obs64.exe`
- MeshLab: the installed Windows Store MeshLab application; its versioned package
  path is machine-specific. Resolve it before launch rather than hard-coding it.
- Git/Git LFS: resolve with `Get-Command git` and `git lfs version`.

## 2. Source preflight

Run from the repository root. These commands are read-only except explicit seal
output. Replace examples with the exact candidate paths; never seal the entire
working repository, secret files, caches or another person's unrelated content.

```powershell
& .venv/Scripts/python.exe tools/production/asset_checks.py inspect support/tools/pipeline/fixtures/cube-centimeters.obj
& .venv/Scripts/python.exe tools/production/asset_checks.py preflight path/to/bundle path/to/filled-source-contract.json
& .venv/Scripts/python.exe tools/production/asset_checks.py seal path/to/bundle --output path/to/bundle-manifest.json
& .venv/Scripts/python.exe tools/production/asset_checks.py verify path/to/restored-bundle path/to/bundle-manifest.json
```

Fill [source-preflight.json](templates/source-preflight.json) with a nonempty
manifest and explicit numeric constraints. Source-contract paths are relative to
the specified bundle root; other candidate record paths are repository-relative.
An empty template, unknown limit, stale hash or LFS pointer cannot pass. OBJ has
no implicit centimeters; GLB bounds are local mesh coordinates. Apply/verify node
transforms and actual scale in Unreal. Compressed geometry needs a qualified decoder.

## 3. Unreal validation

Copy [unreal-contracts.json](templates/unreal-contracts.json), populate exact object
paths and requirements, then run:

```powershell
& tools/production/run_unreal_checks.ps1 -Contract path/to/contracts.json -Output reports/your-candidate/validation-r001.json
```

The wrapper launches the installed editor, registers our Python validator, verifies
the actual callback ran, checks the process/result and keeps the console log. It
refuses an empty contract and an existing result file. Choose a new evidence filename
for each attempt. It changes no execution policy. `-EngineRoot` supports an explicitly
qualified different installation. Paths passed to Unreal use forward slashes to
avoid Python interpreting Windows path escape sequences.

Declared checks currently cover class, static mesh dimensions, required bone/socket,
asset dependency, sequence binding and duration. Keep missing requirements visible:
skin influence distribution, full material graphs, LOD quality, cooked dependency
closure and actual runtime behavior still need their candidate-specific checks.

The deliberately failing qualification suite logs real Unreal errors and therefore
returns a nonzero process code. Its expected-error test report is separate from an
ordinary production run; never teach the wrapper to ignore all nonzero exits.

## 4. Four fixed views and reference comparison

[unreal_reference_studio.py](../../tools/production/unreal_reference_studio.py) reads
an explicit recipe and writes only a new diagnostic folder. It saves four named
orthographic cameras, one fixed reference pose, direct original-color materials and
lit/base-color captures. Original meshes and textures remain untouched. The unlit
material uses emissive only as a diagnostic display; it is not a runtime brightness fix.

The Cragstoat trial found that these materials also need explicit
`MATUSAGE_SKELETAL_MESH` before a real PIE/game capture. The studio builder now sets
that usage flag. A saved material or successful screenshot export alone did not
prove the correct shader rendered: Unreal substituted a gray default material in
the first actual-board test. Inspect colored skinned output and engine warnings;
see [trial evidence](../../reports/creature-production/wc_vn_cragstoat/production_r001/README.md).

Use [the local qualification recipe](../../reports/pipeline-tools-20260921/reference-studio-config-r2.json)
as a starting example, with new output and asset-folder names. Its neutral light
settings are a comparison candidate, not an approved board-lighting profile.
Check source forward direction before adapting yaw. The source Bellback faces +Y;
the example rotates it -90 degrees so the studio's forward becomes +X.

Launch a **fresh** editor with `-ExecutePythonScript` and the environment variable
`WC_REFERENCE_STUDIO_CONFIG` pointing to the recipe. Run captures with graphics
enabled; `-nullrhi` cannot prove rendered appearance. Preserve the emitted recipe,
camera transforms, source hashes and capture record. Review all four sides before
using any render as a new Meshy input. This operation grants no generation credits.

Krita holds labelled construction/reference layers. Generator exports omit labels,
dimensions, swatches and unrelated objects. Keep the original approved color image
visible during review; do not paint over its colors as an accidental preparation step.

For precise image preparation, use **Tools → Scripts → Scripter**, load the reviewed
candidate recipe, and run it. The owner selected this as the default preparation
route. The [executed Cragstoat example](../../art-source/asset-studio/wc_vn_cragstoat/stages/production_r001/recipes/krita_align_references.py)
uses native `Document.scaleImage` with Bicubic interpolation, separate working
documents, `.kra` saves and PNG export. Its
[receipt](../../art-source/asset-studio/wc_vn_cragstoat/inputs/references/four_view_r003/krita-alignment.json)
records actual version, transforms and hashes. Review partial outputs before retry;
never rerun over an existing accepted source. Successful export is not G2 acceptance.

## 5. Audio and continuous review capture

Audacity: import licensed/self-recorded source layers → edit nondestructively where
possible → save `.aup4` → export candidate WAV → inspect sample rate/channels/peak,
tails and loop joins → listen in Unreal. Close the saved project before a byte-level
backup so SQLite journal data is not stranded in an open session. Save sources and
processing notes separately from the exported wave.

OBS: use a candidate-specific scene, explicitly choose capture source/audio devices,
and verify no unrelated desktop/window appears. Never reuse the synthetic fixture
script as a hidden desktop recorder. The tested
[Lua fixture](../../tools/production/obs_fixture_test.lua) deliberately records only
our reference-board image. For creature motion, create a reviewed Unreal capture
scene and include the actual game mix only when needed. Check the recorded file,
not just a successful “start recording” event. Record performance without OBS first;
measure recording overhead separately.

The local authoring helper `imageio-ffmpeg==0.6.0` under
`support/tools/pipeline/python` decoded the OBS recording. It is an authoring
dependency, not a shipped game component or a claim about AI audio rights.

## 6. Trace analysis

For local trace analysis use:

```powershell
& tools/production/analyze_unreal_trace.ps1 -Trace path/to/capture.utrace -OutputDirectory reports/your-candidate/insights-r001
```

This saves the export command, Insights log, timer CSV and result. It refuses an
existing output directory and reports analysis errors. On this installed engine,
CPU timer export worked but both CPU-only and memory-light qualification traces
reported memory analysis errors. Memory profiling remains **unqualified**; do not
substitute the successful timer export for a valid allocation/memory report.
Use [the preserved results](../../reports/pipeline-tools-20260921/README.md#insights-analysis)
to recheck this on an engine update. No firewall permission is required for the
local-file workflow; leave Windows permission prompts for the user.

## 7. LFS and recovery

Future adds of `.uasset`, `.umap`, `.glb`, `.fbx`, `.kra`, `.aup4`, `.wav`, `.flac`,
`.mp4`, `.mkv` and `.utrace`
use [.gitattributes](../../.gitattributes). No old commits were rewritten or project
binaries staged by setup. Inspect `git check-attr filter -- <file>` before adding.

For a delivery, close/save authoring sessions, assemble explicit raw/editable/runtime
bundles, seal them, and preserve their actual bytes on independent storage. If using
LFS-object backup, include the required `.git/lfs/objects`, then test hydration in a
fresh checkout. `git lfs fsck` and a matching SHA-256 verify bytes; opening sources and
launching the game verify usability. A local fixture restore does not prove that the
whole project or a remote host is backed up.

## 8. Requalification triggers and sources

Repeat the affected fixtures after an engine/app upgrade, importer change, renderer
change, compression change or script/API change. Pin actual versions in each delivery.
Keep positive and deliberately bad fixtures. Review [engineering](ENGINEERING.md)
for pipeline stages and [acceptance](ACCEPTANCE.md) for the completion evidence.

- [Epic Modeling Mode](https://dev.epicgames.com/documentation/en-us/unreal-engine/modeling-mode-in-unreal-engine)
- [Epic Data Validation](https://dev.epicgames.com/documentation/unreal-engine/data-validation-in-unreal-engine)
- [OBS scripting](https://docs.obsproject.com/scripting)
- [Git LFS](https://git-lfs.com/)
- [Audacity scripting](https://manual.audacityteam.org/man/scripting.html) describes a
  scripting route; its existence does not prove compatibility with installed 4.0.
- [imageio-ffmpeg 0.6.0](https://pypi.org/project/imageio-ffmpeg/0.6.0/)

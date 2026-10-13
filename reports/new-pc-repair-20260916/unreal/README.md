# Unreal machine connection and Blender exchange test

Executed 16 September 2026 on this PC. **PASS for local Unreal editor Python control and Blender-to-Unreal static-mesh exchange.** This result is separate from compiling or accepting the Wonder Chess game.

## Executed results

| Check | Result | Evidence |
| --- | --- | --- |
| Unreal commandlet executes Python | PASS, exit 0, engine 5.8.2-56702186, embedded Python 3.11.8 | `python-probe.json`, `python-probe-2-exit.json` |
| Blender diagnostic FBX imports and saves | PASS, exit 0, one StaticMesh | `import-probe.json`, `import-probe-exit.json` |
| Expected metre cube preserves scale and placement | 100.000008 × 100.000008 × 100.0 cm; centre (0, 0, 50) cm | `import-probe.json` |
| Saved asset loads in a fresh Unreal process | PASS, exit 0; one LOD, 12 triangles | `reload-probe.json`, `reload-probe-exit.json` |

The FBX input SHA-256 is `441f7624a84646bb5bbf72e4a95746dde599fcb1d4cc6eb92ccde87211f3f151`. The generated `.uasset` is in `support/diagnostics/new-pc-20260916/unreal-smoke/Content/ConnectionProbe/`. The source Blender file and FBX remain in the adjacent `blender/` folder. JSON records identify the exact input and saved-output hashes.

## Method and limits

The disposable content-only project `support/diagnostics/new-pc-20260916/unreal-smoke/WCConnectionSmoke.uproject` enables PythonScriptPlugin and EditorScriptingUtilities. Every probe used the installed `C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor-Cmd.exe`, `-run=pythonscript`, unattended operation, and `-nullrhi`. Launch JSON files preserve complete arguments, timestamps and process IDs. Every engine process exited itself. Remote Python execution remains disabled.

This proves local command control and a real Blender FBX export → Unreal import → saved-asset reload, including basic geometric scale. It does not prove rendering, skeletal/animation exchange, all existing production assets, a persistent editor RPC bridge, a C++ build, gameplay, packaging or release acceptance. The actual `game/WonderChess.uproject` still targets 5.7 and was not opened or converted by this test. Its appropriate 5.7.4 engine/compiler validation is a separate setup task.

## Warnings and retained failed attempt

- The diagnostic FBX import produced one smoothing-group warning. Geometry imported successfully; this probe did not assess normal/shading quality. Production exports should include their intended smoothing settings and undergo visual review.
- The initial Python probe used Windows backslashes in `-script`. Unreal interpreted `\n` in the path as a newline and could not load that script. Its logs remain as `python-probe-*` (without `-2-`). The corrected launch uses forward slashes, executed successfully, and recorded process exit 0. No game content was touched by either attempt.
- Optional profiling DLLs are absent in startup logs; they did not prevent these probes. Import completed with 0 errors and 1 warning. Reload completed with 0 errors and 0 warnings.

## References

- [Epic: scripting the Unreal Editor using Python](https://dev.epicgames.com/documentation/unreal-engine/scripting-the-unreal-editor-using-python)
- [Epic Python sample: asset import tasks](https://github.com/EpicGames/PythonSamples/blob/main/scripts/ImportExport/Asset_Import_task.py)
- Installed 5.8.2 source: `Engine/Source/Editor/UnrealEd/Public/AssetImportTask.h`, `Engine/Source/Developer/AssetTools/Private/AssetTools.cpp`, and `Engine/Source/Runtime/Engine/Classes/Engine/StaticMesh.h` were inspected for the import and geometry APIs.

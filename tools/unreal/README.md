# Wonder Chess Unreal integration helpers

Resume `game/WonderChess.uproject`; do not bootstrap over the existing project. The installed toolchain executed during WC-U400–450 is Unreal 5.7.4 (CL 51494982), MSVC 14.44.35226 and Windows SDK 10.0.22621.0. Read `reports/implementation_state.json` and the release handoff for current asset and acceptance boundaries.

The canonical update uses all 24 stable hero IDs. Generate with `python tools/compile_catalog.py`, then stage with `python tools/unreal/sync_runtime_data.py`. This copies the canonical payload and reflected header into the existing Unreal project. Never edit cooked tables or balance independently.

## Build and import

Build `WonderChessEditor Win64 Development` through the installed engine's `Engine/Build/BatchFiles/Build.bat`, passing the absolute `.uproject` path, `-WaitMutex` and `-NoHotReloadFromIDE`. Only one owner may build/import shared Unreal binaries at a time. Close task-owned editor processes normally before rebuilding their loaded module.

`run_editor_task.py` dispatches the explicit `WC_EDITOR_TASK` environment value. Set `WC_EDITOR_REPORT_DIR` to a fresh directory under `reports/WC-U<task>/<UTC-run-id>/`, and launch the installed `UnrealEditor-Cmd.exe` with the project, `-unattended -nop4 -NullRHI -nosplash` and `-ExecutePythonScript=<absolute run_editor_task.py>`. Record the actual process status and inspect `<task-name>.json` (for example `import_alpha_assets.json`); a zero editor exit alone does not establish a successful Python import.

Prefer `invoke_editor_task.ps1 -Task import_alpha_assets -Editor <installed UnrealEditor-Cmd.exe> -ReportDirectory <fresh absolute reports path> -Hero <stable ID or PowerShell array>`. The wrapper normalizes the Python path to forward slashes, rejects reused evidence and unsupported selections, restores process environment values, and requires both exit 0 and a successful task report. This addresses an observed UE Python command-parser failure where backslashes became escapes and the editor exited 0 without running the import. Inspect the detailed `import-<ID>.json` or `import-selected.json` after wrapper success; cold reload and visual acceptance are separate checks. Audio is opt-in through `-IncludeAudio` or `-AudioOnly`.

- `import_data_tables` imports unit/ability tables and reads every reflected field back. UE 5.7.4 required the process-scoped `DataTableJSON.ExportUsingPropertyVisitor 0` workaround. The importer parses legacy nested struct text through the compiled reflected type and compares normalized values. Failed attempts remain in WC-U410 evidence.
- `import_alpha_assets` validates source/manifest hashes before importing. `WC_IMPORT_HERO=wc_u_human_guardian` selects one published hero; comma-separated IDs select a handed-off batch. Unknown IDs or missing exports fail. Existing skeletons are retained. `WC_IMPORT_AUDIO=1` adds authored WAVs; `WC_IMPORT_AUDIO_ONLY=1` selects only audio.
- `import_neutral_assets` imports the seven original neutral exports. Their rig contracts and optional active clips differ from hero requirements.
- `import_lobby_assets` imports the hash-bound original Brighthaven approach and six modules, checks centimeter bounds and three combined LODs, and preserves the shared surface material. `create_lobby_sky` authors its original unlit horizon/zenith gradient. Both require actual composition review after execution.

Imports use the measured legacy FBX route. Blender/Unreal units and orientations differ; validate imported bounds, LODs, bones, materials and clips after a fresh editor load.

Cold automation filters include `WonderChess.Data`, `WonderChess.Assets.ImportedAlphaContracts`, `WonderChess.Assets.ImportedNeutralContracts` and `WonderChess.Verification`. Combine filters with `+` in `Automation RunTests`, use `-TestExit="Automation Test Queue Empty"`, and export to a new `-ReportExportPath`. `-WCAssetOnly=<stable hero ID>` scopes the hero check. These validate data/transforms, not art or continuous motion approval.

## Package and inspect

`package_game.ps1` invokes installed UAT. Supply an absolute project path, a new archive destination, the installed `RunUAT.bat` via `-UatScript`, `-Configuration Shipping`, and a fresh `-LogDirectory`. Preserve prior archives. UAT success must be followed by executable/payload inspection and a real launch.

`capture_update_provenance.py` binds the completed UAT report, compiled receipt, source, canonical/staged data, content and package hashes to a new immutable JSON file. `--runtime-only` is for an explicitly partial slice; full capture also checks source/export and audio provenance. Historical export-time catalog hashes remain distinct from current data and numeric compatibility checks.

The actual early update archive is `builds/WonderChess-Update24-Early/Windows/WonderChess.exe`. Its record is under `reports/WC-U410/20260906T132749Z/early-package/`. It uses earlier 0.4.0 balance and incomplete art, so it is not the final candidate or current acceptance evidence.

Launch/audit wrappers live in `tests/runtime/`: `run_shipping_solo.ps1`, `run_packaged_regression.ps1`, `audit_packaged_restart.py`, `audit_update_regression.py` and `summarize_frame_evidence.py`. Read their parameters and use fresh output directories. Headless combat, rendered scripted interaction, manual play, continuous animation review, audio listening and two-physical-machine LAN are separate evidence gates.

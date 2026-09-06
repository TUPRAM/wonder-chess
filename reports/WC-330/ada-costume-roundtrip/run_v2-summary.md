# Ada costume reimport and placed-reference cold check

**PASS for the isolated source-to-Unreal same-asset roundtrip.** A real source costume addition was imported into the same duplicated skeletal mesh while preserving seven placed actors/components, their original animation references, the production Skeleton and material references. A separate Unreal process cold-loaded the saved map and verified the same references and geometry. All **296 protected production Content files** were byte-identical before, after and between both phases; no production package became newly dirty.

The verification assets are retained only under `/Game/WonderChess/Verification/AdaRoundTrip/run_v2/`: `SK_AdaRoundTrip` and `L_AdaRoundTrip`. The shipped production costume, production assets and existing package were not revised by this test. The current packaging configuration names the two production maps, uses `bCookAll=False`, and does not name this verification folder among always-cooked directories. This is editor reference-preservation evidence, not a claim that the isolated costume is cooked, visually approved or a new production hero revision.

| Observation | Actual result |
|---|---|
| Source change | Added a central gold breastplate medallion by duplicating an authored fastener; same material/UVs/skin weights. Actual Blender source vertices 2,517→2,557; triangles 4,760→4,836. Original vertices/UVs/weights, bounds, 27-bone rest hierarchy and seven actions unchanged. |
| Blender process | Exit 0; manifest `source-change-manifest.json`, SHA-256 `9d7cab1003ad46f70bfaef9425f0fef15991e2fb288c526de811b0e057d7c0ca`. Sixteen production source/export hashes independently checked before Unreal. |
| Unreal import | Process 42728, import assertions 08:06:39.400–08:06:45.042 UTC, process exit 0. `run_v2-import.json` status `PASS_IMPORT_ONLY_COLD_PENDING`. |
| Actual Unreal geometry | LOD0 render vertices **8,317→8,493 (+176)**; LOD count stays **3**. Render vertices include UE splits and are not Blender source vertex counts. Bounds origin/extents remain exactly equal. |
| Mesh identity | Same duplicated UObject/path before and after reimport. Saved mesh SHA changes from `e0d107ed8983b38d1fa70d18085bc4be861b07469eb623585a84468735a472ce` to `43ee47fc3ee9d9bca3b964e9610cb32d8ab1492175cead4c6d0f3951921920b3`. |
| Seven saved actors | Idle, Move, Attack, Active, Hit, Defeat and Victory actors retain object/component identities, mesh, material references, Skeleton, original AnimSequence and placed location. `OverrideAnimationData` records serialized animation references rather than transient playback state. |
| Map preservation | Before/after map SHA remains `4a640577d808ca6a7c228d070ff2cd085c10d0e7f8bed43aa3dda1c3d16261f1`; saved component references required no replacement. |
| Cold process | Separate process **45060**, assertions 08:07:24.462–08:07:25.989 UTC, exit **0**. `run_v2-cold.json` status `PASS_COLD_REFERENCES_PRODUCTION_UNCHANGED`; exact saved map/mesh hashes, seven reference records and measured geometry match. No asset save requested in cold phase. |
| Production protection | All 296 files protected, no modified/deleted/created production Content paths; empty dirty-production package lists before/after both phases. Only the isolated duplicate/map were saved. |

The importer reused the measured legacy skeletal FBX settings from `tools/unreal/import_alpha_assets.py`, but did not call its production `task()` path because that path forces a Skeleton reference-pose refresh. The drill explicitly disables reference-pose/T0 updates in both the duplicate-owned import data and new options, uses `AssetImportTask.save=False`, and saves only the duplicate and its isolated map.

The import commandlet's summary reports zero errors and zero warnings. Its complete log retains **two late shutdown CVar-priority warnings** about restoring the already-disabled Interchange flag; a blanket zero-warning claim for the entire log would be incorrect. The cold log has zero error/warning lines. Neither warning changed the checked production bytes or references.

The first attempt, `run_v1`, is preserved: exit -1 before the Python script loaded, because Windows backslashes in the Python command-line script path interpreted an escape. No script/asset operation ran. `run_v2` used forward-slash paths and passed. Both process records and full editor/console logs remain next to this summary.

For another complete drill, choose a fresh run ID and execute import followed by cold in separate editor processes. Do not overwrite the successful JSON records or copy them as though they were a new execution. The actual phase inputs were:

```text
WC_ADA_ROUNDTRIP_MANIFEST=C:/Users/iputu/Documents/Wonder Chess/reports/WC-330/ada-costume-roundtrip/source-change-manifest.json
WC_ADA_ROUNDTRIP_RUN=run_v2
WC_ADA_ROUNDTRIP_PHASE=import
# A separate editor process then used WC_ADA_ROUNDTRIP_PHASE=cold.
```

The commandlet was the installed `C:/Program Files/Epic Games/UE_5.7/Engine/Binaries/Win64/UnrealEditor-Cmd.exe`, project `C:/Users/iputu/Documents/Wonder Chess/game/WonderChess.uproject`, with `-run=pythonscript`, a forward-slash `-script=.../tools/unreal/verify_ada_costume_roundtrip.py`, `-unattended -nop4 -NullRHI -nosound` and a unique `-abslog` per phase. Both editor processes exited before the root lane resumed packaging.

No attractive-hero, continuous deformation, sound, frame-time or packaged-game claim is implied by this isolated reference/geometry test. Those checks retain their own evidence boundaries.

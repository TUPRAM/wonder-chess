# Isolated skeletal FBX calibration — 2026-09-06

The original meter-based exports produce a real animation scale mismatch in Unreal 5.7.4. The measured candidate uses a normalized centimeter export, then the legacy FBX importer with `convert_scene=True`, `convert_scene_unit=True`, `force_front_x_axis=False`, `import_rotation=(pitch=0,yaw=90,roll=0)`, `import_uniform_scale=1`, and `preserve_local_transform=False` for animation.

This conclusion comes from **15 executed mesh-plus-Idle import presets and 450 requested pose evaluations**, not from preset documentation alone. Each editor commandlet exited 0. The actual numerical comparison is in `comparison.json`; raw results, source FBX hashes and logs are retained beside this file. All trial assets live under `/Game/WonderChess/Calibration/ImportTrials/`. Production hero assets and their importer were not changed by this probe.

## Findings

- Original meter source, original importer: reference root scale approximately 100; animated root scale approximately 1. Reference head world Z is 154.700 cm, while the sampled animated head is 1.547 cm. The animated root also changes orientation by about 90 degrees.
- Enabling `preserve_local_transform` does not repair the scale mismatch. Disabling forced front-axis conversion fixes the orientation relationship but retains the scale mismatch for the meter source.
- Disabling unit conversion on the meter source produces consistently tiny assets: mesh height about 1.811 cm. It is not a valid size correction.
- The art lane's isolated normalized-centimeter export preserves the authored source file and converts geometry, armature rest translations and animation location keys consistently, with object scales remaining 1. This fixes the imported root scale and animated world height.
- On the normalized source, forced front-axis conversion still creates a reference-to-animation orientation jump. Disabling it produces matching reference and animated root transforms.
- With that option disabled, import yaw 0 points forward along negative Y, yaw 270 along negative X, and **yaw 90 along positive X**. In the yaw-90 trial, the reference toe-minus-foot vector is approximately `(21.839996, 0.000003, -8.190000)` cm, and the cast origin is approximately `(29.119995, -0.000010, 131.040002)` cm. Animated values agree at the initial Idle sample. Head world Z remains approximately 154.700 cm.

The selected trial folder is `/Game/WonderChess/Calibration/ImportTrials/forward_cm_no_front_yaw90`. The fixed root reference rotation represents the imported bone basis; its agreement with animation and the measured world-space forward direction matter. No actor or child scale compensation was used.

## Boundaries and next verification

The probe requests SOURCE, RAW and COMPRESSED modes through the installed `AnimPoseExtensions` API, with retargeting both enabled and disabled, at five times per clip. Python does not expose `IsCompressedDataValid` here, so a requested compressed mode is not a separate assertion that compressed data was valid rather than falling back. The updated C++ asset diagnostic records that distinction.

The initial 15 presets sampled Ada's Idle clip. A sixteenth actual import then used the measured preset with all seven normalized-copy clips (Idle, Move, Attack, Active, Hit, Defeat and Victory). This commandlet also exited 0 and evaluated 210 additional requested poses. Across all seven clips, reference-to-sampled root scale and translation deltas are zero; normalized quaternion rotation delta is at most 0.000003416 degrees. Mesh height is 181.089997 cm, with the measured reference forward direction along positive X. The complete report is `all7_cm-results.json`, numerical summary is `all7-comparison.json`, and actual trial assets are under `/Game/WonderChess/Calibration/ImportTrials/all7_cm_no_front_yaw90`.

The complete probe therefore executed 16 import presets and 660 requested pose evaluations. The updated C++ asset diagnostic and an actual rendered animation review remain separate checks. Correct bone transforms alone do not prove skinned-vertex deformation, feet contact, attractive art, release timing, retarget compatibility or packaged acceptance.

The normalized trial source manifest and exporter evidence are in `exports/calibration/import-probe-normalized-cm/trial_manifest.json` and the art lane's `reports/WC-330/normalized-cm-trial.log`. The original production source remained unchanged during the trial. Production conversion, skeleton/reimport handling, all-hero verification and packaging remain the root/art lanes' responsibility.

## Existing-asset reimport and installed property behavior

A transient-object-only Unreal commandlet verified both `set_editor_property("update_skeleton_reference_pose", True)` on `FbxSkeletalMeshImportData` and `set_editor_property("preserve_local_transform", False)` on `FbxAnimSequenceImportData`. Each value round-tripped through `get_editor_property`; the process exited 0 with 0 commandlet errors and 0 warnings. See `property-setter-results.json` and `property-setter-console.log`. This probe saved no assets. The skeleton-update field is editor-visible but is not declared BlueprintReadWrite, so direct Python attribute assignment is not the valid installed interface.

Cold production diagnostics subsequently showed that assigning only new task options does not update all stored legacy FBX settings during atomic reimport. Installed engine source explains this:

- `UnrealEd/Private/Factories/EditorFactories.cpp`, skeletal reimport: the override UI's skeletal import data is replaced with the existing mesh's import data before applying options. The existing asset's `update_skeleton_reference_pose` must therefore also be set.
- `UnrealEd/Private/SkeletalMeshEdit.cpp:154`, animation reimport: `CopyAnimationValues` copies animation options into existing import data. Its implementation in `Fbx/FbxAnimSequenceImportData.cpp:82` does not copy inherited import transform fields.
- `UnrealEd/Private/SkeletalMeshEdit.cpp:2059` builds the animation's additional transform from `DestSeq->AssetImportData`, including its stored rotation. A stale yaw survives a new task preset unless the existing data is corrected.
- `AssetImportTask.replace_existing_settings` exists, but the installed editor source usage found for that flag belongs to the sound importer, not the FBX atomic reimport branches above.

The resulting integration recommendation is to update the existing SK and AN assets' stored `asset_import_data` with the measured scene/unit/front/rotation/translation/scale preset before atomic reimport; set the respective skeleton-update and local-transform fields through `set_editor_property`; then save the imported asset and skeleton. The root lane owns execution and cold verification of that production migration. The fresh isolated trial result is not evidence that an existing production asset migrated correctly.

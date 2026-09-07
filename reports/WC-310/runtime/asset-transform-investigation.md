# Imported root transform investigation

The first actual asset automation result is **FAILED**, not a successful import gate. Its immutable source export is copied to `asset-automation-first-imported-assets.json`; the original automation log and index remain under `reports/WC-330/asset-automation-first*`. The engine process used an automation queue exit condition and exited with status 0 despite the recorded failed test. Acceptance must use the automation result, not that process code alone.

At that run, twelve mesh objects loaded, but only the six Human/Elf heroes had persisted skeleton dependencies. Those six supplied 42 animation references and 5,994 sampled bone transforms. The remaining Dwarf/Orc skeletons were missing on disk at that checkpoint; no animation/root result was inferred for them.

For all six loaded rigs, the mesh reference root translation was zero, its rotation was near zero, and its uniform scale was approximately 100. Every sampled clip had a root rotation approximately 1.570796 radians (90 degrees) and bone scales approximately 1. The measured root mismatch is therefore both a factor-of-100 scale difference and a 90-degree rotation difference. It is not a threshold-edge numerical rounding failure. The report includes the exact per-hero values.

The first test also found an empty material slot appended during LOD import. Root corrected the importer to assign the same hero material to every existing allowed slot after LOD import. Texture resource dimensions were zero under the headless renderer; these were not proof of absent imported source pixels. The revised test checks `FTextureSource::IsValid` and source dimensions while recording render dimensions separately. A source-dimension pass does not certify cooked texture residency.

The revised root contract compares sampled animation transforms with the actual mesh reference basis. Non-root reference bones retain unit scales. A root may retain a fixed, uniform positive FBX basis scale, but every sampled root must match the reference translation/rotation and every sampled bone scale must match its reference scale. A fixed meter-to-centimeter conversion alone is not enough to accept physical height, feet or forward direction; those remain measured scene checks. The observed 100-versus-1 and 0-versus-90 discrepancies still fail this corrected contract.

Diagnostic sampling now records mesh-reference and skeleton-reference root transforms, raw root samples, runtime root samples, absolute values and differences from the mesh reference. Installed Unreal 5.7 `UAnimSequence::GetBoneTransform` can fall back to raw data when called with `bUseRawData=false`; therefore the field is named `runtime_root`, not an unconditional claim of compressed sampling. Each clip separately records `IsCompressedDataValid()`.

The isolated test flags are:

```text
-WCAssetOnly=wc_u_human_guardian
-WCAssetFolder=/Game/WonderChess/Calibration/ImportTrials/normalized_cm_no_front
```

The folder must contain the original `SK_<id>`, `AN_<id>_<clip>` and `T_<id>_<kind>` basenames. `WCAssetFolder` requires `WCAssetOnly`. A single-hero selection expects one mesh, seven clip references and one declared family. A mesh-plus-Idle experiment still writes useful Idle transform diagnostics while correctly reporting the other clips/textures/LODs as missing; it cannot produce a full-asset pass.

The importer lane is testing normalized-centimeter export and FBX basis options in separate calibration folders. Its reported promising settings have not been promoted to asset acceptance here. The revised test is saved and frozen for a coordinated build and execution against the selected probe. No production binary asset was edited by the runtime lane.


Normalized production cold-load follow-up (2026-09-06T06:16:29.153Z): all12 meshes/84 clips load, with11988 sampled transforms. Exactly84 unique failed assertions remain, each root-reference rotation matching; every clip has approximately90.00001162 degrees delta, root translation0, maximum bone-scale delta4.18e-7. Human/Elf USkeleton reference scales remain100, whereas all mesh references and latter six skeletons are1. Stored animation assets existed even for the previous missing-skeleton heroes, so their failures do not demonstrate a fresh-import defect. The importer owner identified engine reimport paths that reuse existing AssetImportData and omit copied inherited transform fields; production options must be updated on stored import objects before reimport. This is a source-supported diagnosis, with actual correction still awaiting a new cold report. Preserved normalized report and summary are in this directory.

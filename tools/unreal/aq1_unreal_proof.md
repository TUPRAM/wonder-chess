# AQ1 isolated Unreal proof

These tools are authored integration candidates until their execution reports exist. They do not promote Ada, change canonical gameplay data, or certify artistic acceptance. Only the parent editor/content owner should run them.

## Import and cold verification

`aq1_import_candidate.py` consumes the existing export-manifest structure: Ada's stable ID, current canonical `units_source_sha256`, candidate `source_sha256`, `files` hashes, seven `clips` with frame ranges, and `fps:60`. Inputs must include the canonical basenames `SK_wc_u_human_guardian.fbx`, `AN_wc_u_human_guardian_<clip>.fbx`, and `T_wc_u_human_guardian_{BaseColor,ORM,Normal}.png`. Candidate `.blend` files must be under `art-source/heroes/wc_u_human_guardian/candidates/AQ1`.

Use the measured centimeter-copy FBX profile in `tools/blender/profiles/fbx_skeletal_cm_v1.json`. It multiplies mesh vertices, rest translations and animation translation curves by100 on temporary copies while setting export scene scale0.01; source remains meters. Skeletal import uses legacy FBX, convert-scene and convert-unit, no forced front axis, yaw90, scale1 and preserve-local-transform false. AQ1 explicitly imports vertex normals and computes MikkTSpace tangents, matching `use_tspace:false` in that profile.

Example, replacing the input locations with actual saved candidate exports:

```powershell
$env:WC_AQ1_SOURCE_BLEND='C:/Users/iputu/Documents/Wonder Chess/art-source/heroes/wc_u_human_guardian/candidates/AQ1/Ada_r01.blend'
$env:WC_AQ1_EXPORT='C:/Users/iputu/Documents/Wonder Chess/art-source/heroes/wc_u_human_guardian/candidates/AQ1/exports/r01'
$env:WC_AQ1_REVISION='Ada_r01'
$env:WC_AQ1_OPERATION='import'
$env:WC_AQ1_NORMAL_GREEN='flip'
$env:WC_AQ1_REPORT='C:/Users/iputu/Documents/Wonder Chess/reports/AQ1/import-r01.json'
& 'C:/Program Files/Epic Games/UE_5.7/Engine/Binaries/Win64/UnrealEditor-Cmd.exe' 'C:/Users/iputu/Documents/Wonder Chess/game/WonderChess.uproject' -run=pythonscript '-script=C:/Users/iputu/Documents/Wonder Chess/tools/unreal/aq1_import_candidate.py' -unattended -nosplash '-abslog=C:/Users/iputu/Documents/Wonder Chess/reports/AQ1/import-r01.log'
```

`flip` is the initial interpretation for a Blender +Y tangent normal map, not proof of correct appearance. Compare a known asymmetric raised/beveled normal test under matched lighting; use `keep` if that actual comparison requires it. Exactly one green-channel flip must occur. The importer leaves that visual gate pending.

Run cold verification in a new editor process with `WC_AQ1_OPERATION=cold`, `WC_AQ1_PRIOR_REPORT` naming the successful import JSON and a fresh `WC_AQ1_REPORT`. It compares loaded mesh/skeleton/material/clip references, pose samples, measured vertices/bounds and persisted package hashes with the earlier process. It never saves assets in cold mode. Reimport uses the same revision folder but changed, freshly hashed candidate exports and a new import report. It checks same mesh/skeleton object identities; retain matched images to establish that the intended visual change persisted.

The importer creates a candidate material and candidate skeleton, avoiding writes to shared production objects. This isolates revised proportions. Bone names alone do not certify compatible animation: compare the rest pose and all motion extrema. It imports no automatic LODs before the LOD0 art gate.

## Presentation override and actual game captures

The opt-in `-WCAQ1HeroRoot=/Game/WonderChess/Candidates/AQ1/Ada_r01` selects only Ada's mesh and seven clips in `WCBoardPresenter.cpp` and `WCFrontEndScene.cpp`. Other heroes, portraits, effects, audio and all combat/economy code retain their original paths and behavior. Invalid roots or missing candidate assets exit with an explicit `WC_AQ1_*` error. Without the flag, the original paths are used. Recompile the existing `WonderChessEditor Win64 Development` target before relying on the flag; the old binary cannot implement it.

After import and compilation, run from the repository:

```powershell
& './tools/unreal/aq1_launch_proof.ps1' -Mode GalleryMotion -Revision Ada_r01 -EvidenceDirectory 'C:/Users/iputu/Documents/Wonder Chess/reports/AQ1/gallery-r01'
& './tools/unreal/aq1_launch_proof.ps1' -Mode MatchCapture -Revision Ada_r01 -EvidenceDirectory 'C:/Users/iputu/Documents/Wonder Chess/reports/AQ1/match-r01' -ExitAfter 900
& './tools/unreal/aq1_launch_proof.ps1' -Mode MatchProfile -Revision Ada_r01 -EvidenceDirectory 'C:/Users/iputu/Documents/Wonder Chess/reports/AQ1/profile-r01' -ExitAfter 900
```

Use `-Baseline` with separate evidence directories for the production control. Match capture uses the existing scripted human-seat exercise and persistent bots at ordinary speed; it does not claim manual input. Gallery capture is the existing full-cycle20fps recorder, separate from frame-time profiling. Profile runs disable screenshot capture to avoid including screenshot stalls. Inspect actual logs, pixels and `visible_alive` counts; a900-second run is not automatically a crowded encounter containing Ada or a completed tournament. The current exercise buys/places legal roster contents and cannot guarantee a particular shop or battle. Retain the source seed/transition evidence and confirm the target hero in the observed encounter.

Normal board framing is the existing orthographic camera at `(2450,0,2800)`, rotation `(-50,180,0)`, width4300cm. `-WCArtReview` uses a closer width2300cm and replaces the visible roster with posed review units; it is not an actual fight and must not be substituted for MatchCapture.

These commands run the current Unreal game with uncooked editor content; they are real engine/game captures, not packaged evidence. Candidate content needs an explicit cook directory if a separate AQ1 proof package is made. Do not change production cook/default asset references merely to collect the candidate experiment.

## Checks

`python tools/unreal/aq1_test_import_preflight.py` exercises rejection of canonical paths, directory traversal, changed assets/source, stale canonical stats provenance, missing clips, implicit normal interpretation, overwritten evidence and unprotected sibling candidates. These are ordinary-Python guard tests, not editor execution. The parent must compile the two presentation source files and run both flagged/unflagged actual startup. Run an invalid-root startup and require the named error/exit2. Inspect gallery `engine-motion.json` for all seven candidate animation paths, then compare before/after ordinary-speed frame CSVs on the same named hardware. Continuous visual review, normal orientation, crowded gameplay, source/reimport appearance and Pram acceptance remain separate gates.

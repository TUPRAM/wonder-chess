# BW2 — scoped acceptance, runtime decisions and reusable recipes

## 1. One successful subsystem per run

Default first scope: the anatomical-right sword grip. A correctly calibrated but visually failed pose remains failed. A successful right grip can justify the left shield adaptation; it does not automatically approve shoulder armor, moving cloth or the complete hero.

An initial method plus two unsuccessful meaningful corrections triggers method review for that lane. Keep progress on other independent lanes possible. Do not restart the game, reopen facial likeness, or build a new framework to avoid a modeling failure.

Routine code mistakes and wrong coordinate metadata must be diagnosed explicitly. They are not evidence that the anatomical method itself has been tested correctly. After fixing them, rerun the short calibration before more posing. Record the real work and avoid resetting the artistic stop rule indefinitely by renaming the same failed method.

## 2. Proposed acceptance matrix — all new work starts NOT_RUN

| ID | Scope | Required evidence |
|---|---|---|
| F01 | Hand frame | Correct open-hand labels, world/metric conversion, proper determinant, visible distal/palmar directions, transformed-rig consistency |
| F02 | Axes | Reversible local bend-sign checks; original pose restored |
| G01 | Right grip | Actual glove-surface contact patches, opposing thumb, no significant penetration, consistent palm/back/side/axial views |
| G02 | Carrying | Closed-hold sequence, fixed hand-local weapon relation, guard/pommel clearance, actual source-bound movie |
| G03 | Left grip | Independent left calibration and shield/forearm clearance; no mirrored-sign assumption |
| A01 | Arm assembly | Sleeve continuity/ease with armor hidden; rigid plate overlap and bracer construction in required motion |
| C01 | Panels | Split retained; body does not pass visibly through required-motion panels; tested intermediate poses |
| K01 | Knee/greave | Useful coverage and overlap across declared motion; no popping/shelf/detached rigid shell |
| B01 | Boot | Improved sole retained, coherent seam/heel junction and ankle behavior |
| V01 | Style | Required component matches reference construction at full-body/gallery/gameplay views |
| T01 | Temporal | Original 169-frame probe preserved; candidate scanned; old Solidify spikes do not recur |
| P01 | Preservation | Uploaded protected hashes unchanged; candidate opens with its actual intended scene/data |
| R01 | Runtime path | Each new corrective/control has a declared, separately tested export representation |
| RP1 | Replay | Successful scoped construction replayed from frozen inputs without unrecorded manual fixes |
| RP2 | Second body | Same recipe fits one compatible changed body; changed inputs/output and failures recorded |

Numbers in the grip guide are starting screens; visual failure is not canceled by a numeric pass. Do not automate human approval or average one failed category into several passing tests.

## 3. Preserve known corrections

On the affected copied BW1 modifiers, maintain:

- `BW1_CoatUpper_Continuous`: `use_even_offset=False`, thickness 0.006 m, offset -1.
- `BW1_Leggings`: `use_even_offset=False`, thickness 0.002 m, offset -1.

These are the reported retained settings, not a claim that every future garment should use them. An alternate topology/thickness workflow needs its own all-frame evaluation. Blender documents limitations to Solidify's even-thickness approximation. [S4]

The provided source skin/costume data and body keys must not be unintentionally altered by applying modifiers. Corrected clothing candidates may have deliberately changed geometry; document this separately from source preservation.

## 4. Do not confuse authoring and runtime skeletons

The BW1 report identifies a temporary 163-bone MPFB rig versus a 27-bone game rig. This handoff does not assert compatibility, change the shared skeleton or authorize a replacement.

For every moving component record its candidate owner/control, rest frame, affected vertices, and proposed export path:

| Method | Candidate use | Before runtime acceptance |
|---|---|---|
| Fixed hand grip | Fingers posed on authoring rig; derived output may bake a fixed grip relative to a hand | Verify rest-space conversion, wrist seam, hand-bone weighting and all actual animations; cannot claim opening fingers when none exist |
| Expanded finger/panel/knee joints | Better authoring articulation | Separate export-rig version, retarget/mapping and performance approval; no silent merge into shared skeleton |
| Pose corrective shape | Garment or joint correction | Export compatible morph data, explicitly reproduce driving behavior in Unreal and test intermediate/combined states |
| Blender constraints | Convenient local armor/tool control | Bake supported animation or implement a verified equivalent; arbitrary constraints are not assumed transferred |
| Cloth simulation | Optional later secondary motion | Implement/test in the selected runtime solution; a Blender cache is not a shipping cloth solver |

Morph targets are supported in Unreal's FBX pipeline, but that fact alone does not recreate Blender's driver logic. [S5] Use the installed compatible exporter/importer and a real import test. Animation transfer has its own documented FBX workflow. [S6]

A useful local proof may remain AUTHORING_ONLY. If its runtime path is unresolved, finish/report the local result but do not promote it as the all-character production recipe.

## 5. Proof before recipe promotion

After a part works, record only the information needed to reproduce it: source IDs/hashes/license, installed versions, rest/candidate matrices, meaningful dimensions, selected landmarks, actual control axes, fitting parameters, operations, poses, and review outcomes.

Replay on an independent duplicate with no hidden selection/UI/manual edits. Then fit one compatible body variation. A second body should test the recipe, not silently alter its code for that single target. Log any limits instead of calling the method universal.

Do not start model training from the failed BW1 poses as successful exemplars. Keep failures as rejected cases with reasons. The coordinate-frame bug is useful regression data once the corrected workflow actually passes in Blender.

## 6. Evidence economy

During local fitting use a few relevant closeups and short cheap viewport motion. After retaining a candidate, capture final neutral/reversed-light and continuous evidence, scan the full relevant range, and save/reopen once.

Do not run full gameplay suites, re-render the entire roster, or produce a report for every vertex adjustment. Run only checks affected by the change. Reuse the existing AS1 tooling where it works.

The supplied 680×880 movie can demonstrate large panel/intersection defects. It cannot measure sub-millimetre grip contact. Use actual evaluated geometry plus closeups for that evidence.

## 7. Final report format

- Candidate file/scene/object and exact parent baseline.
- Scope changed; protected sources and retained old failures.
- Actual images/movie, poses and numerical observations.
- One sentence per visible improvement; no unsupported likeness percentage.
- Top remaining defects, with next independent task.
- Runtime-path state and replay state, explicitly NOT_RUN where absent.
- Human approval remains unrecorded unless actually supplied by Pram.

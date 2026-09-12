# AQ1 candidate compatibility review

Read-only review of current Git diff, fresh file hashes and executed Blender/Unreal reports. This lane did not run Blender, Unreal, GPU work, or another game process. The current audit snapshot is recorded in `review.json`; later material or source changes require new hashes and evidence.

## Preserved interfaces

- Current HEAD remains `9623fd82f98ff80a90985b9f552d8851ccece30f`, the cited audit commit. All **7/7 baseline hash entries** still match: canonical Ada `.blend`, saved before-copy, approved reference image, `units.json`, `rules.alpha.json`, `traits.json`, and `asset_manifest.json`. Ada's canonical identity, role, skill and numeric data therefore remain byte-for-byte preserved in the checked source.
- The only tracked C++ changes are `WCBoardPresenter.cpp` and `WCFrontEndScene.cpp`. Review of their diff finds optional `-WCAQ1HeroRoot=/Game/WonderChess/Candidates/AQ1/<revision>` loading for Ada's mesh and animations. Canonical portraits remain loaded from the usual folder. No combat, economy, source definitions, animation clocks, or release timing is changed. The third tracked diff is the pre-existing Blender bridge log. The exact inspected C++ diff is retained as `presentation_source_diff.patch`.
- Loaded-baseline and baked-export reports have identical rest-skeleton and source-action invariants: rest `f68ec623265e008026f982875d973907580e600d2e7a215980e2c4bf6cb6c73e`; actions `d3022161e3068284babb6f598ca2b136cbc4bc17e5e092552531b940098c4ad7`; seven action identifiers, unit scale 1m, 60fps. Source curve equality does not imply compressed animation bytes equal old assets: export copies can bake evaluated support-hand constraints.

## Candidate chain

- Editable forms: `art-source/heroes/wc_u_human_guardian/candidates/AQ1/ada_forms_r08.blend`, SHA-256 `823cc10c1f1c4bfe81c92928a60e8dfb5e56d53ae46421ddbeb932af0b2829bb`.
- Baked export source: `art-source/heroes/wc_u_human_guardian/candidates/AQ1/ada_baked_r06.blend`, SHA-256 `b284de03f89e1506048eb7e62427dafde9f90eb0eb2ef5141089ff6ef91f0c37`.
- Export set: `art-source/heroes/wc_u_human_guardian/candidates/AQ1/exports/r06/`. **11/11** current FBX/texture hashes match `baked_r06/export.json`; the report manifest hash matches the imported manifest hash.
- Candidate Unreal folder: `/Game/WonderChess/Candidates/AQ1/Ada_r01`. **14/14** candidate binary hashes currently match `import-r01.json`. No canonical replacement is inferred.
- The importer recorded **604 protected content files unchanged** before/after its operation. This review checked that record and freshly hashed the seven AQ1 baseline entries and fourteen candidate binaries; it did not independently rehash all 604 historical protected files.

## Imported measurements

The actual Unreal 5.7.4 import report records 27 bones; `root`, `head`, both feet, both weapon bones, `cast_origin` and `head_ui` are present. Root reference position is zero. Head reference Z is **154.700 cm** and head-UI Z **186.550 cm**. Bounds origin is `[8.2621, 8.2938, 92.2812]` cm, extent `[29.7101, 78.5704, 91.0812]` cm: mesh Z span **1.200–183.362 cm**, height **182.162 cm**. These are import-space measurements, not crowded-fight camera acceptance.

LOD0 has **22,803 render vertices**. The export has **24,280 triangles**, **one material**, and **1024px textures**. Render vertex count differs from source topology because render splits exist. Only LOD0 is imported; two lower LODs are pending. The 15k target is exceeded: the up-to-25k comparison experiment still needs Pram's exception/character acceptance before promotion. Counts alone do not justify it.

| Clip | Imported seconds | Expected seconds |
|---|---:|---:|
| Idle | 2.0 | 2.0 |
| Move | 1.0 | 1.0 |
| Attack | 0.649999976 | 0.65 |
| Active | 0.600000024 | 0.60 |
| Hit | 0.400000006 | 0.40 |
| Defeat | 1.0 | 1.0 |
| Victory | 1.5 | 1.5 |

All seven durations match within floating-point tolerance. The importer sampled five compressed poses per clip; that is not a full visual animation review. The separate `review_engine_motion_r01` review covers all 150 actual captured gallery frames but remains frame-sequence inspection.

Saved import settings are FBX normals plus MikkTSpace tangents. BaseColor uses sRGB; ORM and Normal do not; Normal compression and green-channel flip are recorded. These settings are confirmed in executed import metadata. Final normal orientation and material appearance require visual proof; the r01 gallery visibly looks washed out, and the owner is diagnosing it.

## Pending / not established by this record

Pram's reference character approval; finished form/material approval; the 24,280-triangle exception; lower LODs and candidate portrait; final corrected material/normal/tangent appearance; deliberate source edit and reimport with mesh/skeleton/placed references preserved; complete continuous playback and audio review; normal-board and crowded-fight candidate review; isolated baseline/candidate performance comparison; candidate packaged launch and complete match/elimination/spectating/restart.

The reviewed import is an **initial import**, with `reimport=false` and identity-comparison fields null. Do not label it reimport proof. Existing baseline performance work and subsequent candidate work belong to their own reports. No numeric art score or final asset approval is issued here.

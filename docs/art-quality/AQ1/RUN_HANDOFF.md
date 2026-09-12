# AQ1 Ada candidate — executed review handoff

This run continues commit `9623fd82f98ff80a90985b9f552d8851ccece30f` in the existing Wonder Chess repository. The selected direction is Pram's attached Ada reference sheet. That explicit selection replaces the pack's generic three-concept choice; it does not approve the resulting 3D character.

**Current result: a materially improved, animated Blender/Unreal candidate with open art defects. It is not a finished match for the reference, a promoted production hero, or a new packaged release.** The source was rebuilt through named editable parts and inspected renders. Its method is scripted, manually directed mesh authoring and refinement, not a freehand sculpt or a generated image presented as editor evidence.

## Open the actual candidate

The editable major-form source is `art-source/heroes/wc_u_human_guardian/candidates/AQ1/ada_forms_r08.blend`. The current baked/export source is `ada_baked_r07.blend` in the same directory. Open either with the installed Blender 5.1.1; preserve it and save the next revision under a fresh candidate name. Textures, normalized FBX mesh and all seven animation exports are in `exports/r07/`; `export_manifest.json` binds their bytes to the baked source.

The candidate has been imported to `/Game/WonderChess/Candidates/AQ1/Ada_r01`. Preview it in the actual compiled Unreal game using PowerShell:

```powershell
& 'C:\Program Files\Epic Games\UE_5.7\Engine\Binaries\Win64\UnrealEditor.exe' `
  'C:\Users\iputu\Documents\Wonder Chess\game\WonderChess.uproject' `
  -game -windowed -ResX=1920 -ResY=1080 `
  -WCAQ1HeroRoot=/Game/WonderChess/Candidates/AQ1/Ada_r01
```

Choose the hero gallery and Ada to inspect the model/clips, or start the existing Solo session. This launches the uncooked Editor target. No new standalone AQ1 executable was packaged. Omitting `-WCAQ1HeroRoot` uses the original production Ada. The existing roster, statistics, skills, economy and tournament implementation are retained.

## What actually changed

- A new continuous head/neck/nose surface replaces the coarse old head. Swept dark hair and braid volumes replace the short blockout cap. Facial expression and eyelid/hair construction still need substantial refinement.
- Chest/back armor now wraps the torso; shoulders have modeled curvature; boots, knees, forearms, coat and tabard use shaped surfaces and named ownership. Armor still reads too much like smooth caps and tubes, with insufficient layering compared with the selected sheet.
- The shield is convex with a peaked kite outline, rim, raised sun crest and rear straps. The sword has a ridge, taper, guard and downward idle stance. Palm/thumb/finger geometry is connected, though repetitive finger bands, wrist transitions and equipment contact remain visible weaknesses.
- Actual Cycles selected-to-active bakes produce base color, tangent normal, AO, roughness and metalness. One 1K atlas material uses BaseColor sRGB, Normal linear, and ORM linear (`R=AO`, `G=roughness`, `B=metalness`). Source detail includes restrained bevels and selective procedural quilting; it is not a sculpted high-detail finish.
- The 16-bit sRGB base-color PNG caused a real Unreal interpretation mismatch. An 8-bit source revision retains the intended encoded colors. Reimport then exposed material-slot remapping and an unrefreshed material graph; both were repaired and checked in fresh engine captures and a separate cold process.
- Early gallery frames showed transient low-detail shading. The review fixture now waits for actual referenced textures to stream/compile before its six settling frames. It retains the authored 20 Hz review timeline and changes no combat timing.

## Measurements and limits

| Property | Loaded/recorded result |
|---|---|
| Canonical baseline mesh | 9,068 triangles; 4,787 vertices |
| Candidate LOD0 export | 24,280 triangles |
| Unreal render vertices | 22,803 |
| Rig | 27 bones; preserved source rest/action invariants |
| Import calibration | 182.162 cm mesh height; head reference Z154.700 cm; root at origin |
| Materials | One actual LOD0 section and one atlas instance; two retained FBX slot names point to that same instance |
| Texture resolution | 1024×1024 |
| UV sampling | 41.42% occupied pixel centers, zero sampled overlaps/out-of-bounds triangles; 14 zero-area UV triangles and 2,710 subpixel triangles remain limitations |
| Clips | Idle 2s, Move 1s, Attack 0.65s, Active 0.6s, Hit 0.4s, Defeat 1s, Victory 1.5s |

The ordinary 15k triangle ceiling remains unchanged. This is the AQ1 up-to-25k comparison experiment, not an accepted shipping exception. Lower LODs wait for Pram's LOD0 approval under the art contract. No blanket decimation or global generator rerun was used to meet the comparison limit.

## Evidence to inspect

All paths below are relative to `reports/AQ1/20260908/`.

| Evidence | Actual boundary |
|---|---|
| `comparison/material_before_after.png`, `comparison/clay_before_after.png` | Matched real Blender renders, placed beside each other with labels; no character pixels generated or retouched |
| `before_relinked/`, `after_matched_r07/` | Front/side/back/three-quarter, clay/material, face/grip, board and 96px views |
| `live_snapshot.json`; repo path `reports/blender-mcp/20260908T004353Z/viewport.png` | Actual safe MCP save-copy and real Blender viewport screenshot |
| `review_blender_motion_r06/REVIEW.md` | 436 source frames measured; all 154 rendered frames/neighbors inspected |
| `engine_candidate_motion_r04/engine-motion.json` | Actual 150-frame, seven-clip Unreal capture with texture readiness recorded |
| `review_engine_motion_r04/REVIEW.md` | All 150 final engine frames inspected; startup shading corrected, geometry defects retained |
| `videos_before/`, `videos_candidate_r04/` | Actual 20fps MP4s encoded from the recorded frame sequences, with decoder readback; human continuous audiovisual approval remains pending |
| `engine_candidate_match_r01/`, `review_candidate_match/` | Actual normal-board/crowded capture with Ada and her shield effect; scripted seat input, timed exit and one retained snapshot-write gap |
| `reimport-r03.json`, `cold-r03.json` | Same-path reimport, same mesh/skeleton identities, persisted references and protected Content unchanged |
| `normal_probe_unreal_r06/orientation-review.json` | Actual asymmetric physical-control comparison supports exactly one green-channel flip |
| `color_encoding_probe_r02/color-encoding-results.json` | Actual bake/save/shader-reload regression passes for known navy and linear ORM samples |
| `review.json`, `reference_review/`, `compatibility_final/` | Filled review, specific visual gaps and current byte/compatibility checks; no numeric art approval |

The engine captures are automated inspection of the existing game. They do not establish manual 1H7B completion, a new 100-tournament regression, two physical LAN machines, or release acceptance. Source and gameplay data hashes remain unchanged from the retained baseline.

The candidate combat capture exited with code 0 after its requested 600-second process limit, in round 15 combat, with settlements 1–14 and `complete=false`. It produced 1,206 valid snapshots and 62 screenshots. There are 69 sampled states with Ada visible in an encounter containing at least 12 living units, and 76 states with eight unfinished neutral encounters across rounds 1, 2, 3, 5, 10 and 15. A single logged snapshot-write failure corresponds to a 1.010247-second gap during round 12; all retained JSON rows parse and timestamps remain monotonic. A read-only review had opened the mutable log during capture, so contention is possible but not established. Performance was not measured in this screenshot run.

## Actual performance comparison

The separate normal-speed runs used the Ryzen 7 6800H, RTX 3060 Laptop GPU, approximately 16 GB RAM, NVIDIA 580.88, D3D11, 1920×1080 at 100% resolution, VSync off and a 60 FPS cap. Seed 828301 and recorded settings match. No Blender renderer, video encoder or competing Unreal/build process ran during the candidate profile. There are 20,547 baseline and 20,583 candidate samples, covering 345.181 and 346.087 seconds of summed frame intervals after warmup. Both end in round 10 preparation; neither completes a tournament.

| Measurement | Original Ada | AQ1 candidate |
|---|---:|---:|
| Overall frame p95 | 16.693 ms | 16.679 ms |
| Overall GPU p95 | 21.444 ms | 21.801 ms |
| Twelve-visible combat frame p99 | 21.166 ms | 20.922 ms |
| Eight live neutral encounters frame p99 | 24.121 ms | 29.589 ms |
| Largest frame interval | 100.018 ms | 235.061 ms |

The candidate's 235.061 ms hitch occurs during round 4 combat with 10 visible living units. It is an unresolved measurement, not proof that Ada caused it. The candidate has 28 intervals over 50 ms versus 19 in the baseline. One capped run per version cannot isolate mesh cost or establish performance acceptance. Thread/GPU counters are asynchronous and must not be added as though they describe one frame. The eight-neutral subset is eight active simulations, with one observed board rendered.

Both profiles have zero recorded frame-counter gaps and no evidence-write failures. Both also retain the same existing `MID_M_WC_Surface_5` instanced-static-mesh material-usage/fallback warning; this has not been established as Ada's material. See `reports/AQ1/20260908/performance_review/PERFORMANCE.md`, `PAIRED_OBSERVATIONS.md` and `performance.json` for complete distributions, settings, hashes and limits. The higher geometry budget is not approved by these measurements.

## Checks and unresolved work

Fresh baseline: 400 spec/data checks, 147 Python tests, document check and generated catalog check passed. The candidate importer preflight has 11 passing tests. Two real Unreal Editor builds succeeded, including the texture-readiness fixture. Import/cold-load, seven-clip capture, color regression and the asymmetric normal comparison executed successfully within the boundaries above.

Retained failures include copied-source relative-texture renders, earlier bake/UV/budget attempts, invalid/stale/black normal-probe captures, the initial wrong color-test oracle, washed-out and gray Unreal material captures, and an invalid-root process-exit assertion. The invalid path was refused and Unreal logged requested exit status 2, but graceful startup returned 0; the launch wrapper now also checks named candidate-load errors. The original bridge log's trailing whitespace is preserved as evidence, so a whole-tree whitespace check reports it; scoped source checks pass.

The material/readiness fixes do not resolve the open art problems: schematic face/hair, insufficient armor/cloth construction, uneven shield highlights, repetitive grip, ivory/tabard intersection during Move, exposed waist crescent during Hit, stiff Defeat panels/light seam artifacts, and full frontal face occlusion during part of Active. Continuous human playback/audio review, LODs, final portrait and Pram's reference approval remain pending. There is no enabled native desktop/video playback inspection tool in this session; consecutive rendered frames and encoded videos were used, without claiming a real-time audiovisual review.

## Preserve and resume

Canonical Ada SHA-256: `54f04b8f28fd819eb22b7a4f6c8051484c6466513e6cd43d419c835b67d950b3`. Its exact disk copy is `before_canonical.blend`; the actual open-scene snapshot is `before_live_scene.blend`. The selected sheet is retained as `approved_reference.png`. Candidate source SHA-256: `cd6bb6ddb3a54aaa15be3112a804caf0820f9ad1162b7cb8ee345f646bef8a67`. The current data, rules, traits and asset manifest hashes are recorded in `baseline_hashes.json` and checked again in the preservation and final compatibility records.

Continue from editable `ada_forms_r08.blend`, using named semantic parts and a fresh source revision. Address the face/expression/hair and armor/tailoring gap in actual clay renders before adding ornaments. Fix the named cloth/contact defects at their recorded extreme frames. Rebake/export the isolated copy and repeat the seven-clip, material, calibration, candidate-only reimport and normal-board inspections after a real geometry change. Do not run old topology-count surgery, `author_alpha.py --all`, reset the live scene, change balance, or promote this candidate without Pram's art approval. No commit or push was performed in this assignment.

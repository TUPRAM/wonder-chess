# BW6 bracer and cuff local review — 2026-09-11

Status: **local review candidates; no human approval; Ada remains ART_REVISE overall.** These parts are fitted to the unchanged BW5 MPFB forearm, padded sleeve and source glove. They have not yet been checked against the separately reconstructed BW6 fixed hand or final torso assembly.

The retained right bracer has a new, editable dorsal steel surface with a deliberate axial crest, a continuous leather lining/cuff, and two closure straps. The broad shell follows `lowerarm02.R` rigidly. Only the cuff’s wrist transition blends the existing local forearm/wrist influences. The glove and bare-hand geometry were not changed. A separately fitted left counterpart uses actual `.L` bones and independently tested motion.

## Native deliverables

| Side | Editable work | Frozen checkpoint |
|---|---|---|
| Right | `ada_bw6_bracer_work.blend` | `ada_bw6_bracer_checkpoint_r002_REVIEW_CANDIDATE.blend` |
| Left | `left/ada_bw6_left_bracer_work.blend` | `left/ada_bw6_left_bracer_checkpoint_r001_REVIEW_CANDIDATE.blend` |

The right checkpoint/work SHA-256 is `734dd39808cd5efa906c823d644e69b31b5ef69aeddf1d2bf380b392e54b2042`. The left checkpoint SHA-256 is `40d16931f2ee9a4f7f2f45a29a592aa75420de76eefec7c0fef3b462ef40aff1`. Both files were saved and reopened; owned mesh positions, faces and weights match the pre-save records. See `records/verification.json` and `left/records/verification.json`.

## Construction and bounded revisions

The source is the frozen BW5 r003 armor file, SHA-256 `e1acb1cb3e11be218b7a0f381921e8da7e81a46a87a4f68f35151e28ab657899`. The bracer scene contains independent copies of the body, glove, coat, rig data and action. Source geometry, original shape keys, reference files and the game were preserved.

The fitting frame is expressed in world metres. Anatomical right is positive world X. Its wrist is approximately `(0.486376, 0.112333, 1.112247)` and elbow `(0.361061, -0.042104, 1.248911)`. The proximal axis comes from these actual landmarks; dorsal orientation uses the previously verified nail/palm classification. The construction record contains layer-specific radial measurements at ten forearm sections, rather than assuming a circular bare forearm. The steel spans roughly 26–186 mm proximal to the wrist and uses a 2.4 mm outward wall. The leather lining uses a 1.2 mm wall. These are candidate construction choices, not dimensions recovered from the painting. The retained padded-coat and leggings settings were not reset.

1. **Initial construction:** purpose-built steel shell, volar leather panel, separate cuff, straps and rims. It cleared the body and sleeve in the five initial authoring samples, but the cuff met the glove incorrectly and separate leather/rim overlaps produced crossings.
2. **Correction 1:** replaced the crossing cuff/panel arrangement with one continuous, welded-seam leather lining; rejected the intersecting separate rims; shaped a stronger central steel crest. This cleared all 97 authoring frames. Extra wrist stress probes still exposed failure in the simple cuff-weight ramp.
3. **Correction 2:** replaced that arbitrary ramp using locally constrained radial correspondence to the actual unchanged glove/body’s evaluated rest surfaces. Only weights were transferred; no evaluated posed vertices were pasted into rest geometry. This cleared the tested wrist probes. This is the final right geometry/deformation revision for the bounded assignment.

The left counterpart reflects only the four new surfaces and reverses winding. Its actual wrist, elbow and MCP landmarks were recorded. Seventy-seven source fingernail vertices establish the dorsal sign independently. Its test action maps the right posed/rest **world-space deltas** through reflection onto each actual left rest bone, then bakes those transforms into an independent action. It does not copy right Euler signs. The maximum reconstructed integer-pose matrix error was approximately `4.77e-7`.

## Executed checks

| Check | Right | Left |
|---|---|---|
| New parts, raw and evaluated self-crossing screen | 0 confirmed pairs | 0 confirmed pairs |
| All 97 integer authoring frames, each part against unchanged body, coat and glove | 0 confirmed pairs | 0 confirmed pairs in independently mapped left action |
| Intersections between the four new parts across those frames | 0 confirmed pairs | 0 confirmed pairs |
| Additional wrist-local X/Z rotations of ±15° and ±25° | All eight sampled probes clear | All eight sampled probes clear |
| Editable mesh/weight save and reopen | Verified | Verified |
| Actual seven canonical game clips and Unreal | Unrun | Unrun |

The intersection screen confirms nonadjacent, noncoplanar transverse triangle crossings. Zero detected pairs does not prove mathematical continuous collision freedom, tangency/coplanar correctness, containment, useful contact, or good appearance. The stress angles are explicit local diagnostic inputs, not a claimed anatomical or runtime range. `a_clearance_weights` fields inherited from the shared query refer to Shrinkwrap diagnostics and are not cuff skinning weights; these bracer parts use no Shrinkwrap modifier.

The complete records are `records/r002_all97_surface_checks.json`, `records/r002_wrist_stress_probes.json`, `left/records/left_initial_all97_surface_checks.json`, and `left/records/left_initial_wrist_stress_probes.json`. Frozen files preserve the same mesh/weight records as the measured sources; capture manifests record the later frozen hashes.

## Actual visual evidence and remaining defects

`captures/BW5_vs_BW6_right_bracer_comparison.png` places actual BW5 and BW6 dorsal clay renders side by side. The source renders use the same saved camera; the AS1 sheet helper resizes panels for display but applies no image registration or geometric warping. Other right images include dorsal, volar, side, axial, reversed clay, actual cage, and a +25° wrist test. Left images include separately calibrated dorsal, volar, axial, three-quarter, moved-arm and wrist-test views. These images were inspected.

The source-bound right movie is `motion/r002/BW6_BRACER_97_AUTHORING_FRAMES_NOT_GAME_CLIPS.mp4`: 97 actual rendered frames at 24 fps, with a tracked closeup and a fixed context view. `motion/r002/source_record.json` binds its source hash, cameras and action. Representative temporal images were inspected; a complete human continuous-motion approval has not occurred. Left movement is retained in its native action and sampled pose captures; no separate left movie was produced.

The steel is more deliberately constructed than the old open bracer. The leather underside and wrist connection read as distinct layers. Remaining visible issues:

- The cuff flares at its lateral corners. It can look like a protruding lip rather than tailored leather.
- The wrist lap becomes a dark, open-looking seam in the stress pose. The zero-crossing result does not establish attractive or complete visual enclosure there.
- The two straps have useful placement but still need a final fastening design if this local construction is adopted.
- The finish is a diagnostic preview. The silhouette, collar relationship and material character require review within the complete Ada assembly.
- Some isolated images have deliberately cropped context boundaries above the elbow. Those jagged display cuts are temporary unsaved masks, not newly modeled garment boundaries. Full context views also expose pre-existing body/coat study defects outside this forearm assignment.

## Controlled integration

`append_bracers.py` provides `append_bracers(target_rig, target_scene)`. It appends only the eight owned surfaces, checks both frozen hashes, rejects existing owned names and incompatible world bind matrices, and redirects their armature modifiers to the explicitly supplied target rig. It does not save the target file or apply either diagnostic action. It was executed against an isolated rig copy: all eight mesh/weight signatures matched the frozen sources, and the target action signature remained unchanged. See `records/append_helper_verification.json` and `append_replay_check.blend`.

After appending to the combined candidate, recheck the current padded sleeve, new fixed glove, equipment and wrist lap through that candidate’s motion. The source rig still has the MPFB authoring hierarchy; this is not compatibility with the game’s 27-bone skeleton. No canonical rest pose, sockets, animations, Unreal assets or game data were replaced. No human approval or reusable-recipe promotion is recorded. A left adaptation on the same body is not a second-body generalization test.

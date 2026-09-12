# BW5 anatomical-right shoulder study — ART_REVISE

This is a rejected local study, separate from the BW5 torso candidate. It removes the sampled coat and inter-lame crossings but introduces self-folds in the evaluated cap and lowest-lame edge. The lowered pose also exposes inadequate cap suspension. Do not replace the retained BW4 contextual shoulder with this as an accepted component or extend it to the other side.

## Executed construction

- Preserved the BW4 frozen armor and all non-owned meshes, original shape keys, body, coat, sleeves, torso, rig/action and master files. Six anatomical-right shoulder shell/return objects were the exclusive editable scope.
- Located the cap failure on the proximal broad surface, including medial/front/rear transitions; the cap lower rim was clear. The lowest lame's first failure was its distal anterior corner and return, not its entire width.
- Replaced the narrow proximal cap patch with an open saddle-shaped crown and an intentional front/rear cutaway, retaining the original distal cap overlap and rigid `upperarm01.R` attachment.
- Recut only the lowest lame's distal anterior route, up to 26 mm along the upper-arm axis. The rear extent and transverse radius were retained.
- Gave the first/second lame a controlled nested interface: first-lame lower edge grows outward by at most 6 mm, lowest-lame upper underlap moves inward by 8 mm. The first-lame cap interface remains fixed.
- Rebuilt the lowest-lame returned edge as two rows sharing its boundary. The old separate terminal trim remains present but hidden and explicitly labeled `SUPERSEDED_FAILED_GEOMETRY_RETAINED`; this is a replacement surface, not an accepted hidden crossing.
- Reconstructed two intermediate cap rows after their original replacement doubled back. This reduced cap self-crossing but did not solve the final shell.

## Results and limits

| Observation | Retained diagnostic result |
|---|---|
| Raw cage vs final padded coat, all 97 original frames | 0 confirmed transverse pairs on five active shoulder pieces |
| Evaluated shoulder vs final padded coat, all 97 frames | 0 confirmed transverse pairs |
| All ten active shoulder-part pair combinations, all 97 frames | 0 confirmed transverse pairs |
| Thirteen additional quarter/half-frame coat queries | 0 confirmed transverse pairs |
| Separately posed arm lowered 32 degrees around world Y | 0 confirmed transverse coat pairs; visual suspension still fails |
| Cap self-query | Raw cage 0; evaluated shell **135 confirmed nonadjacent transverse pairs** |
| Lowest-lame self-query | Raw cage 0; evaluated shell **111 confirmed nonadjacent transverse pairs** |
| Other three active pieces, self-query | Raw and evaluated 0 |
| BW4 shoulder baseline self-queries | All six original pieces 0 raw and evaluated; the new folds are a regression |

Self-query is at frame1 because each complete part follows one rigid owner and preserves its internal geometry across this authoring action. Raw cage is not the final surface: the cap still has two crossings under subdivision alone, 40 after Solidify, and 135 after bevel. The lowest lame is clear under subdivision alone, then has 32 crossings after Solidify and 111 with bevel. Modifier-isolation results are in `records/ordered_patch_modifier_diagnosis.json`; final retained modifiers were not silently disabled to claim a clear mesh.

The queries confirm noncoplanar transverse triangle intersections after BVH candidate generation. Topologically shared-vertex triangles are excluded only from the self-query. Coplanar overlap, tangencies, containment and mathematically continuous-time collision freedom are not certified. Counts are repeated triangle observations, not independent anatomical defects.

## Actual image and motion review

Fresh BW4 and BW5 captures use the same saved cameras and image dimensions. `captures/BW4_vs_BW5_SHOULDER_ART_REVISE.png` compares rest, rear and the same temporary lowered pose. The last comparison is a diagnostic posture, not a measured reproduction of the painted reference. Its temporary action unassignment was restored by reopening the unchanged candidate before saving.

Actual raw-cage, Cycles clay, reversed-key and lowered front/rear views were opened and inspected. The cap is now too much like a tall outer arm plate. In the lowered pose it drops with the upper arm and leaves a large uncovered area between the cap and torso bridge. This cannot be passed merely because the coat is no longer crossed.

The 97-frame source-bound, 24 fps, 800 × 800 movie was rendered and reopened through Blender's native sequencer. All 97 encoded frames were decoded successfully. All frames were visually examined in five chronological sheets at 320-pixel tiles, with native-size stills for local shape review. This is frame-by-frame temporal review, not a claim of continuous-time collision proof or actual canonical seven-clip gameplay review. Existing BW4 torso/collar, left armor, open hand and unfinished bracer are context in this movie.

## Attempt accounting and intervention

One initial construction cleared the sampled coat screen but failed self and inter-lame geometry. The overlap correction improved the inter-lame screen; the continuous return correction removed a separate trim seam but retained evaluated self-folds. One focused ordered-row follow-up removed raw cap foldback and reduced evaluated cap crossings from 382 to 135. The affected method is now parked; no new nearly equivalent variants are authorized by this report.

The next useful intervention is **a redesigned proximal cap surface and suspension together**, checked first in the lowered posture and then raised: an attachment on a candidate clavicle/shoulder support or explicit rigid articulation must keep coverage near the shoulder while the arm moves beneath it. This is a candidate-only proposal, not a shared rig change. Build its medial aperture with nonfolding surface correspondence, then prove subdivision and physical thickness before adding a bevel. Rebuild the lowest-lame terminal edge with sufficient curvature radius for the chosen wall thickness; its current narrow returned section cannot carry the inherited modifier stack cleanly. Do not fix these failures through more whole-cap offsets, sleeve shrinkage or decorative trim.

`operations/apply_bw5_shoulder.py` and `records/final_owned_geometry.json` reproduce the executed rejected geometry on an independent diagnostic copy. A same-source serialization replay matched all mesh coordinates, faces and weights; it is **not** a promoted modeling recipe or second-body fit. The primary torso/waist/collar lane remains independent of this failure.

No human approval, opposite-side extension, canonical asset replacement, runtime bind conversion, seven game clips, Unreal import/reimport or packaged test was performed for this shoulder.

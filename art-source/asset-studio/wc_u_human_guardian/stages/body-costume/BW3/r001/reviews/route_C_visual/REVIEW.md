# BW3 route C independent visual review

Status: **ART_REVISE — partial thumb approach, not a grip.** Other fingers remain OPEN throughout this evidence. The two corrective attempts have been used; this packet records the retained result and does not authorize more modelling or human approval.

The changed thumb route makes the glove's outer thumb mass less severely hooked than the verified BW2 isolated-thumb baseline. It does not solve the underlying first web or put the thumb pad around the fixture. This is a posture improvement with a failed contact/construction outcome, not a rebuilt hand or approved grip.

## Observed image findings

1. **The thumb does not enclose the fixture.** The side and axial fixture views separate the cylinder from the thumb's contact face clearly. Palm projection makes the tip appear close to the cylinder, but the other views show why that projection cannot establish contact. The fingers are deliberately open. The movie keeps this limitation visible.
2. **The underlying body web remains sharply compressed.** The actual posed BODY base cage shows a thin triangular fold at the palm/thumb transition, with adjacent faces narrowing into the same corner. Its evaluated smooth counterpart still has a thin seam at that location. The smoother glove covers much of the defect; it must not substitute for a body-surface pass. Small dark body exposures beside the glove web are visible in the body-dark/glove-light diagnostic.
3. **Glove volume is improved but not yet anatomically convincing at the transition.** The old BW2 image has a narrow bent thumb and a deep longitudinal slit beside its base. Route C has a broader, more continuous outer mass and avoids that exact hooked silhouette. It now sweeps across the lower palm with a compressed upper junction and a full, rounded base. Since the thumb pose differs, this comparison is not evidence that the same posture was repaired by a topology or weight change.

Reversed lighting preserves the reading of the fixture separation and web junction. The dorsal view is useful context but largely hides these failures; it is not an acceptance view. No extra smoothing or image repair was applied to these rendered surfaces.

## Numerical evidence, separately attributed

The native audit in `../route_C/route_C_results.json` is a separate executed geometry test, not an inference from the images. It reports no detected self-crossings or fixture entry in the raw/evaluated glove across its 145 integer-frame checks and sampled onset refinements. This partial result does not establish grasp contact.

At frame 145 the evaluated glove's designated thumb-pad samples are 27.59–31.63 mm from the cylinder; their mean normal dot toward the cylinder is -0.91177, and the contact-band fraction is zero. The underlying body first crosses at sampled frame 13.75 in the raw cage (previous clear sample 13.5) and frame 19 in the evaluated surface (previous clear sample 18.75). The frame-145 body contains 9 raw crossing pairs and 14 evaluated crossing pairs. These specific tests confirm why the better outer glove silhouette cannot pass the local proof. They are bounded collision queries, not a guarantee against every possible contact defect.

## Actual evidence viewed

All following stills were personally opened and inspected at native image resolution in this review. Stills are source frame 25.

- `C_fixture_palm.png`, `C_fixture_side.png`, `C_fixture_axial.png`, `C_fixture_back.png`: original saved cameras, original Cycles settings and lights, glove plus fixed diagnostic cylinder.
- `C_glove_hidden_oblique.png`, `C_glove_hidden_axial.png`, `C_body_hidden_oblique.png`, `C_body_hidden_axial.png`: evaluated surfaces isolated with the fixture hidden.
- `C_body_dark_glove_light_both.png`: both surfaces, temporary dark-gray body/light-gray glove material identifiers; this is a diagnostic, not a material pass.
- `C_glove_reversed_key.png`: key/fill transforms swapped temporarily, each original light energy preserved; source unchanged.
- `C_actual_posed_base_cage_oblique.png`, `C_actual_posed_base_cage_axial.png`: actual 2,294-vertex glove authoring cage deformed by its saved armature, subdivision disabled, wire overlay. These are not wires drawn over the evaluated smooth topology.
- `C_actual_BODY_posed_base_cage_oblique.png`, `C_actual_BODY_posed_base_cage_axial.png`: actual 19,158-vertex indexed body's posed authoring cage, existing masks/armature retained and subdivision disabled.
- `C_first_web_closeup_body_cage.png`, `C_first_web_closeup_body_evaluated.png`: new explicitly diagnostic close camera, original oblique orientation, tighter .115 orthographic scale. These closeups are not baseline-comparison cameras.
- `C_matched_BW2_isolated_thumb_oblique.png` and `../onset/isolated_verified_glove_frame25_oblique.png`: same saved BW2 oblique camera, .285 orthographic scale, 900×1000, matching Workbench studio/gray/shadow/cavity recipe. Other digits are open in both; thumb poses differ. The rejected earlier non-isolated baseline is not used.
- `comparison_verified_BW2_thumb_vs_C_final_labels.png`: AS1 downsample-only comparison with external labels. Original rendered panels are not warped or repaired; no image-registration score is claimed.

## Complete motion review

`BW3_C_thumb_approach_OTHER_FINGERS_OPEN_NOT_A_GRIP.mp4` contains every frame 1–145 at 24 fps and 800×800, about 6.04 seconds. Its visible banner states **THUMB APPROACH STUDY / OTHER FINGERS OPEN / NOT A GRIP**. Frame 1–25 shows the authored thumb approach; 26–145 retains that thumb pose during the copied wrist/arm carry channels. The fixture remains the saved fixed-hand-frame cylinder, not an adapted sword.

Every native frame was inspected in five consecutive contact sheets, with no skipped integer frame: 001–030, 031–060, 061–090, 091–120, and 121–145. The final sheets in `contact-sheets-final/` use the same source pixels with shorter, legible labels. Full-size frames 15, 25, and 97 were also inspected. The sequence shows progressive thumb movement and subsequent wrist/arm movement without an obvious pose pop or cropped hand. The outer glove movie cannot reveal the hidden body's internal crossing and does not validate grip pressure, game timing, or a closed-hand animation.

A fresh native Blender VSE process decoded **all 145 encoded movie frames** to `decoded-verification/`. Encoded frames 1 and 121 were personally opened to check image content and the visible banner. This was ordered frame-by-frame visual review plus full encoded-stream decoding; it is not a claim of live, real-time player observation. See `motion_metadata.json`, `video_verification.json`, and `contact_sheet_manifest_final.json` for exact camera matrices, source/frame/movie hashes and encoding evidence.

## Source binding and limits

All C renders read `thumb_route_C_final_method_input.blend`, SHA256 `2dad0803a3e8bfd1974b3bf86dbf5377cd462807f02fb9e76f45463205ba2a1d`, action `BW3_C_ExternalApproach_ART_REVISE`. Each background process kept source hashes unchanged and never saved a `.blend`. The BW2 comparison source also remained at SHA256 `d64d5900317541710d5ef29939d12559e5ecef31777a7e9261158cbccb7a41cf`.

The separately executed native reopen record `../../records/reopen_and_preservation.json` binds C's exact candidate core data/action/modifiers and ten posed geometry samples to the final frozen file, SHA256 `d195b2870e7974665efd3ae03dd3ac88dc5ba2b8a7dbfcc76accbf8b4de3ac60`, and work file `cf15051c9d31885b1c6c4cd2d97de70716f87dbe0e4d3cc667f24a00413d664c`. The record reports all 560 protected-file checks unchanged and preservation of the 69 master meshes. This binding was read here; the independent reviewer did not rewrite or resave either final file.

The movie SHA256 is `587e738750da2212fd1a3c87b3be18de9e4515017c68f5e1c457136054bd1df0`. Still-specific source, camera, light, pose and hash records are in `stills_metadata.json`, `body_cage_metadata.json`, and `fixture_views_metadata.json`.

Recommendation: park C at **ART_REVISE**. Retain the independently testable thumb-route experiment and its evidence, not a promoted glove/grip recipe. A subsequent explicitly bounded intervention should reconstruct the underlying first-web deformation and establish real thumb-pad opposition before closing the remaining fingers. No full grip, actual sword adaptation, second-body replay, runtime export, Unreal motion, or human approval was completed by this review.

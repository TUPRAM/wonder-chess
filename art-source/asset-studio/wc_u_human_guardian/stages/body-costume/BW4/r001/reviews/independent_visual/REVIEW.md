# BW4 independent visual review

Reviewer: Codex independent visual-review agent. This is an agent assessment, not human approval.

**Latest result: fixed hand ART_REVISE; chest/back/right-shoulder assembly ART_REVISE.** Both methods produced visible improvements and reached their initial-plus-two-corrections boundary. Remaining confirmed crossings prevent local acceptance. No third geometry correction is requested by this review.

## Reference basis

Read BW4 `docs/04_ARMOR_PLAYBOOK.md` and `docs/05_ACCEPTANCE_AND_DELIVERY.md`. Visually inspected the package's native `Ada_torso_costume_crop.png` and `Ada_arm_equipment_crop.png`. The target has one broad, controlled breastplate with a restrained center ridge, waist taper, a separate padded collar/underlayer, and low broad shoulder caps with subordinate plate boundaries. Historical museum designs are not substituted for Ada's design.

The old BW1 `captures/armor_blockout_r000.png` was inspected only as historical context. It is not the frozen-r003 matched baseline.

## Initial valid armor construction

Actual files inspected under `armor/captures/`: `initial_valid_front.png`, `initial_valid_three_quarter.png`, `initial_valid_back.png`. The earlier files lacking `valid` were not used; the writer reported an initial candidate-parenting setup error there.

Status: **ART_REVISE**.

Observed improvements:

- The new anatomical-right cap and two subordinate lames have explicit rim boundaries and a more intentional top-to-side transition than the old broad smooth cap.
- The front and back shells form identifiable continuous armor parts, and the side fastening has a visible design intention.

Blocking observations:

- The front plate has extensive irregular surface islands near the upper chest and both side transitions. These read as overlap or interpenetration, rather than designed armor planes. Exact cause requires isolated-shell and underlayer inspection; this review does not claim a mesh collision audit.
- The three-quarter view has a deep, empty-looking lateral opening below the armpit and above the side strap. A strap alone does not establish undergarment enclosure.
- Irregular pointed silhouettes appear at the retained upper collar/shoulder context in the back and front views. Their source ownership must be distinguished from new armor before changing anything.
- The plate still reads tall and vertically oriented compared with Ada's compact, broad chest armor. This is a lower-priority shape issue until shell/underlayer assembly is coherent.

Recommended first correction: isolate the new shell and the retained underlayer, confirm the render allowlist and actual clearance, then correct the assembly fit. Do not add decoration or broad smoothing to conceal these artifacts. Request new matched assembled views, one isolated-shell view, and one sleeve-only view before extending the design.

Not yet reviewed: candidate control cage, underside thickness, saved-camera r003 comparison, actual seven-clip motion, transitions, reversed lighting, fixed hand, wrist/bracer, save/reopen equivalence, Unreal. None of these checks is implied by the three still renders.

## Initial fixed-hand construction

Inspected actual `captures/initial_palm.png`, `initial_oblique.png`, `initial_handle_hidden.png`, `initial_cage.png`, `initial_side.png`, `initial_underside.png`, `initial_axial.png`, and `initial_dorsal.png`. Also inspected the preceding open-palm/oblique/side source captures and the package's native glove-style crop.

Status: **ART_REVISE**. The fixed shape is not a valid production grip yet.

- The handle-hidden and actual cage views expose long triangular sheets between finger bases and palm. These are surface construction failures, not a material or subdivision requirement.
- The underside shows the thumb web folded into a blade-like sheet with a narrow transition into the palm. The opposing thumb lacks coherent supporting thenar volume.
- The dorsal knuckle ridge has scalloped pointed rises rather than four broad knuckle masses with deliberate intervening valleys.
- The fingers have distinguishable curved silhouettes, but their roots do not yet form believable connected anatomy. Contact statistics cannot override that failure.
- `initial_side.png` is almost completely obscured by the sword guard/blade. It does not establish the hand's side profile. Request a same-camera sword-hidden view and a separately labeled selected-hilt-only view.

Recommended first correction: replace the failed short base-to-palm transitions with feature-aligned bridge topology, preserving digit spacing and building a broad rounded thumb/palm transition. Do not merely increase smoothing or widen one selected crease. Retain the initial geometry and views as the unsuccessful initial construction; this recommendation does not reset the bounded correction counter.

No source-animation, wrist-interface, clearance, collision, engine, or user-approval pass is issued by this static review.

## Armor corrective revision 1

Inspected actual `armor/captures/rev1_front.png`, `rev1_three_quarter.png`, `rev1_profile.png`, `rev1_raise.png`, `rev1_reach.png`, and `rev1_sleeve_only_raise.png`.

The revised front surface is meaningfully cleaner: most broad irregular overlap islands are gone. The side returns now give the lateral torso an enclosed assembly rather than the initial deep void. These are specific visible improvements, not an armor acceptance pass.

Status remains **ART_REVISE**:

- The upper breastplate stands far forward of the chest in profile. Shoulder straps stop behind its upper endpoints, so its attachment is visibly incomplete.
- The lower front rim overlaps the belt buckle and reads apron-long relative to the approved compact plate-above-belt hierarchy.
- The broad smooth chest remains inflated rather than showing Ada's restrained angular center-plane transition.
- The new right cap retains an irregular inner-boundary surface patch in front/three-quarter views.
- The sleeve-only raised pose shows continuous torso/underarm coverage from this angle, but a very broad flared cuff opening around the forearm. One view cannot establish full underarm or cuff clearance through motion.

Recommended final corrective revision: fix top shell/strap attachment without uniformly moving the shell farther from the body, refine the lower edge above the belt, establish the restrained center plane, and inspect the cap's residual inner-boundary artifact. Keep unresolved sleeve/cuff fit explicit. The two posed stills are local diagnostics, not seven-clip playback evidence.

## Fixed-hand corrective revision 1

Inspected actual `captures/correction1_palm.png`, `correction1_dorsal.png`, `correction1_oblique_hidden.png`, `correction1_side_hidden.png`, `correction1_underside_hidden.png`, and `correction1_axial.png`.

The four finger-to-palm roots are meaningfully improved. The triangular sawtooth sheets are absent in these images, and the dorsal knuckles now meet the palm through broad continuous transitions. Preserve this improvement.

Status remains **ART_REVISE** because the thumb has a major local construction failure. The sword-hidden side view exposes two knife-shaped descending flaps and a narrow palm junction. The underside shows a severe twist/kink near the thumb MCP region instead of one rounded thumb/thenar volume. The root's reported cross-section roll reversal is consistent with the appearance; this visual review has not independently inspected vertex ordering.

Recommended final corrective revision: maintain consistently ordered and oriented thumb cross-sections through the local transition, rebuilding the longitudinal connection and rounded base while preserving the improved finger/palm construction. Check the raw cage before subdivision. Removal of the fold alone does not establish hand/handle clearance or plausible thumb volume.

## Fixed-hand final corrective revision 2

Inspected actual `captures/correction2_palm.png`, `correction2_dorsal.png`, `correction2_oblique_hidden.png`, `correction2_side_hidden.png`, `correction2_underside_hidden.png`, `correction2_axial.png`, and `correction2_cage.png`.

The thumb/palm silhouette is substantially more coherent. The blade-like hanging flaps are absent, the thenar region has a continuous rounded external volume, and the four improved finger roots are retained. A small sharp notch remains on the distal/thumb contact area. These views justify testing the geometry; they do not establish nonintersection.

The independent geometry worker's executed `reviews/hand_geometry/REVIEW.md` and `correction2_summary.json` were read. Its source is `ada_fixed_hand_correction2.blend`, SHA-256 `2dd8ddbd0fcd2183a26319a185cca81be39a64b7b1e76f4eb8176b5b05123244`. This visual reviewer did not independently rerun that audit.

The audit reports 64 raw / 141 evaluated confirmed nonadjacent self-crossing triangle pairs, 301 / 527 handle-crossing pairs, and 25 / 30 guard-crossing pairs. The worst sampled evaluated handle penetration is 11.814 mm at candidate vertex 709, associated with the middle proximal/metacarpal transition rather than a distal contact pad. The reported raw self-crossings predominantly affect reconstructed web/thumb and palm-base/thumb relationships. These are serious geometry failures despite a smoother outer silhouette.

Final status: **ART_REVISE**. Stop the bounded hand method. A future narrow intervention must reconstruct the connected palm/base/thumb volume around the locked selected hilt, keeping the metacarpal transition outside the equipment and preventing local web crossings before refining pad contact. Do not propagate this failed candidate into cuff fitting or seven-clip acceptance. No animated-grasp success is claimed.

## Armor final corrective revision 2

Authoritative writer-identified source: `armor/ada_armor_checkpoint_FINAL_ART_REVISE.blend`, SHA-256 `95b508f7550f5752a41f6b9706a324038dc4ffbbb888e70d29dbb788e7528dcc`.

Inspected the final `armor/captures/review_final_*` images: front, three-quarter, profile, back, rear-three-quarter, reversed key, shoulder and shoulder-reversed closeups, shell-only front and back, actual cage, raise and reach, sleeve-only rest/raise/reach, and full-body context. Inspected `matched_r003_front.png`, `matched_r003_three_quarter.png`, `matched_r003_profile.png`, and `matched_r003_back.png` as the actual frozen-r003 comparison. The unprefixed `final_*` files are preserved intermediate second-correction captures and are not the final authority.

Specific retained improvements against r003:

- The breastplate has a continuous designed front surface, defined neckline/waist rims, and a center plane that reads under reversed light; r003's broad block-like horizontal bands are gone.
- Side returns make the front/back relationship visible, and the backplate is closer to the torso than r003's widely separated rear slab.
- The lower front edge now clears the buckle rather than overlapping it.
- Shoulder bridges reach the plate endpoints, and the new right cap/two lames have readable layered edges in rest, raised, and reaching stills.

Remaining defects:

- The right cap's medial coat intersection produces a visibly irregular, disappearing boundary. This persists in the diagnostic closeup.
- The backplate's upper region crosses the retained coat. The back and rear-quarter images show unresolved overlapping contour relationships.
- The breastplate remains conspicuously forward-projecting in profile. Longer straps connect it, but do not themselves resolve its heavy silhouette or fit.
- The raised lower edge reveals dark gaps immediately above the belt. The waist/underlayer transition remains unfinished.
- The sleeve remains broad and poorly tailored at its wrist opening. Raised/reaching stills expose a large cuff void around the forearm. The retained bracer is incomplete; no cuff/bracer success is claimed.
- Retained neck/head context has a visible jagged neck boundary and is outside this armor correction. It is not hidden or treated as approved.

Read the writer's executed `armor/verification.json` and `armor/records/all97_authoring_frame_surfaces.json`. Across 97 integer frames of the local MPFB diagnostic, the reported maximum confirmed coat-crossing pair counts are: backplate 84 (first frame 1), right cap 372 (first frame 1), and lower lame 2 95 (first frame 20). Front plate and lame 1 have zero detected transverse pairs in that specific query. Tangency, coplanar overlap, containment, and all other pairings are not certified by those zeros. This visual reviewer did not independently rerun that query.

Final status: **ART_REVISE**. Retain the designed front surface, returns, and layered-plate approach as improved candidate construction. The next separate scoped task should fit the upper back and medial shoulder to a coherent sleeve envelope through the required movement, and resolve the waist/underlayer transition. The geometry method has reached its two-correction limit. The 97-frame local diagnostic is not a review of the actual seven game actions, and no engine or human approval is issued.

## Final presentation and motion evidence

Inspected the labeled `armor/captures/BW1_r003_vs_BW4_FINAL_ART_REVISE.png` comparison and the stronger-contrast actual cage view `review_final_actual_cage_black_edges.png`. The comparison preserves the source/candidate distinction and makes the improved front plane, rims, side enclosure, and remaining profile-fit limitation visible.

Inspected `armor/motion/decoded_motion_review_9_samples.png`, representing frames 1, 13, 20, 25, 37, 49, 61, 73, and 97 of `BW4_ARMOR_AUTHORING_DIAGNOSTIC_NOT_GAME_CLIPS.mp4`. The samples show the same local raised/reaching arm sequence and persistent unfinished cuff/shoulder relationships. This reviewer inspected nine temporal samples, not continuous playback of every frame. The writer's all-97-frame decode and geometric query are distinct executed checks; neither is an independent continuous visual-motion pass by this reviewer.

Inspected the hand's `final_selected_hilt_only_axial.png`, `final_selected_hilt_only_palm.png`, `final_selected_hilt_only_side.png`, `final_uniform_clay_key.png`, and `final_uniform_clay_reversed_key.png`. The hilt-only side view resolves the earlier guard-obscured evidence problem and shows the handle against the palm/finger envelope. Opposite lighting does not remove the confirmed local fit failures. The earlier neutral-gray diagnostics retain more surface detail than the bright uniform-clay view and should remain in the review packet.

No source file was edited by this reviewer. Only review notes and inspected-file hash records under `reviews/independent_visual/` were written.

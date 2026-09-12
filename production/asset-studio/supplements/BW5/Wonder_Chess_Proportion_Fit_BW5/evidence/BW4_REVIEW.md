# Ada BW4 — fixed hand and upper armor: ART_REVISE

Executed new editable closed-glove geometry and an independent chest/back/right-shoulder assembly. Both reached the BW4 limit of one initial construction and two substantive corrections. Both retain major geometric defects and remain **ART_REVISE**. This delivery does not complete the requested production hand, wrist/bracer integration, armor acceptance, or Ada.

## Equipment decision and preserved contract

The current canonical source was freshly opened read-only: 27 bones, no digit bones, and all seven authored actions retain hand/equipment relationships across 865 half-frame samples. This supports choosing a fixed representation. It does not validate the new glove or its new sword orientation in those animations.

The original sword has an octagonal 77.314 × 77.314 mm handle section across corners, 209.300 mm total length and 164.900 mm exposed below the guard. There is no separate pommel. After seeing the executed comparison, the user explicitly selected **“Use the narrower handle proposal”**: 30 × 26 mm section, 110 mm exposed length, original upper overlap retained (154.4 mm total). The blade and guard geometry remain unchanged. That selection applies to the isolated BW4 candidate; it is not forms approval or canonical promotion.

`equipment_fit.json` records the selection. The local hand study uses one rigid placement of that selected sword across the palm. The old sword offset nearly follows the game hand's proximal axis; a conventional transverse grip needs a different candidate-only attachment. Conversion and review on the existing game rig are NOT_RUN because local construction fails. Shared sockets, skeleton, actions and canonical equipment remain unchanged.

## What geometry changed

The hand starts from the clean open CC0 `toigo_gloves_short` adaptation, extracted as an independent 1,147-vertex editing reference. It does not bake the failed BW2/BW3 pose. The new closed derivative adapts the original finger sections, replaces local thumb/web faces and builds a connected palm/base transition. The first correction removes sawtooth finger-root sheets; the second maintains continuous thumb cross-section orientation and restores a broader thenar connection. The retained cage has 1,185 vertices and 1,191 faces, with no live finger rig. These counts describe editability, not quality.

The armor file builds new breastplate/backplate cages, shaped edge returns, side connections and one right shoulder cap with two lames. A separate coat copy receives local right shoulder/underarm allowance. The front plate's center plane, neckline and waist are clearer, and its side connections are more explicit. No new cuff/bracer was built: that work depends on a credible hand fit. The old cuff/bracer, head, opposite shoulder and lower costume in armor context views remain unfinished context.

The hand-mass study used the supplied Ada crop and the public [Proko hand-muscle lesson](https://www.proko.com/course-lesson/how-to-draw-hands-muscle-anatomy-of-the-hand/) to distinguish thumb-base volume from the web. Those references informed the construction; they did not establish that this implementation succeeded.

## Measured and visible failures

| Final local query | Raw cage | Evaluated surface |
|---|---:|---:|
| Confirmed glove self-crossing triangle pairs | 64 | 141 |
| Glove / selected actual handle crossing pairs | 301 | 527 |
| Glove / unchanged guard crossing pairs | 25 | 30 |
| Glove / blade crossing pairs | 0 | 0 |
| Worst sampled handle penetration | 11.560 mm | 11.814 mm |

The largest handle intrusion is at the middle proximal/metacarpal transition, not a distal pad. Candidate vertex 709 lies near (1.723, 85.465, 31.719) mm in the metric hand frame. The free base transition moved through the handle while the distal finger sections surrounded it. Most raw self-crossings involve the reconstructed web and thumb; an example is triangles 200/1675 near (27.425, 69.631, 30.828) mm. The smoother exterior therefore does not establish a valid closed glove. All five declared pad groups retained their source membership; the middle pad still has no samples within the inherited contact band.

The independent armor test evaluated every integer frame of a 97-frame MPFB authoring diagnostic. The front plate and first lame have zero detected transverse crossings against the coat in those samples. The upper backplate reaches 84 pairs, the right cap 372, and the second lame 95 (first detected at frame 20). The profile also remains too far forward, and the waist exposes unfinished underlayer gaps. These prevent assembly acceptance.

Pair counts are reproducible observations, not numbers of distinct defects. The reused tests distinguish transverse intersections from BVH candidates, but do not certify coplanar contact, all containment cases or mathematically continuous collision freedom. See `reviews/hand_geometry/REVIEW.md`, `armor/REVIEW.md`, and `reviews/independent_visual/REVIEW.md` for exact cases and independent pixel review.

## Delivered evidence and limits

- Editable hand: `ada_fixed_hand_work.blend`; frozen: `ada_fixed_hand_checkpoint_ART_REVISE.blend`.
- Editable armor: `armor/ada_armor_work.blend`; frozen: `armor/ada_armor_checkpoint_FINAL_ART_REVISE.blend`.
- Matched hand comparison: `captures/BW4_fixed_hand_initial_vs_final_ART_REVISE.png`. Actual cages, selected-hilt-only views, sword-hidden views and neutral-gray diagnostics are retained. The authoritative balanced Cycles light pair ends in `_key_review.png`; earlier brighter lighting attempts remain explicitly diagnostic history.
- Matched armor comparison: `armor/captures/BW1_r003_vs_BW4_FINAL_ART_REVISE.png`; use `review_final_*` for final armor stills. Earlier `final_*` files are intermediate history, not the frozen final.
- Hand movie: `motion/BW4_fixed_hand_LOCAL_TURNTABLE_ART_REVISE.mp4`, 96 frames, 24 FPS, 800 × 800. This is a camera turntable of the static failed hand; guard/blade are hidden and labeled. All 96 encoded frames were decoded; 12 temporal samples and closeups were inspected.
- Armor movie: `armor/motion/BW4_ARMOR_AUTHORING_DIAGNOSTIC_NOT_GAME_CLIPS.mp4`, 97 frames, 24 FPS, 800 × 800. All frames were rendered, geometrically sampled and decoded; nine temporal samples and pose stills were visually inspected. This is not continuous visual review of every frame or a canonical seven-clip test.

Both files were reopened in fresh Blender processes. Hand raw/evaluated geometry, groups, modifiers, transforms and selected sword match the audited correction exactly. Armor signatures match its frozen final. All 28 intake hashes and 62 inherited protection hashes match (77 unique paths). Armor also preserves 55 original BW1 mesh records and independently owns 38 duplicated context meshes and its temporary rig/action. The retained garment settings are the source's positive 6 mm/2 mm thickness with offset −1 and even-offset disabled; the original right sole is unchanged.

Blender MCP was unavailable at preflight. Installed Blender 5.1.1 background processes executed the work and renders. No desktop screen control was used. No new assets, neural training, purchases, private uploads, engine upgrades, canonical replacements or gameplay tests were performed.

## Stop and exact next intervention

Do not continue this hand's displacement/interpolation method with another coefficient or angle pass. Retain the useful distal finger shapes and selected hilt, but replace the middle/base and thumb/web transition against an explicitly constructed closed form that stays outside the actual handle. Keep a separate palm volume and distribute new web loops around the thumb base; confirm the raw cage before subdivision and pad fitting. The exact failed regions above define a narrow local mesh intervention.

For armor, retain the improved breastplate and side returns. Reconstruct the cap's medial/rear edge and the backplate's upper armhole against the padded shoulder in rest and raised poses, then recut the lowest lame at its measured sleeve crossing. Torso profile and waist underlayer enclosure need their own focused correction. Do not globally inflate shells to hide the intersections.

Wrist/bind conversion, new cuff/bracer, candidate seven game clips and transitions, Unreal import/reimport, packaged-game review, materials/baking, second-body replay and recipe promotion remain NOT_RUN. No human approval was issued, and BW3 remains ART_REVISE research. The next scope is a specific local mesh intervention, not another unrestricted polish loop.

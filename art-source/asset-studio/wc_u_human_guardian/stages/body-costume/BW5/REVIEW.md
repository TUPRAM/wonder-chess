# BW5 — armor proportion and fit / ART_REVISE

Executed in Blender 5.1.1 on independent candidates. The torso is shorter and less deep than BW4, and its final neckline topology repair removes the detected self-folds. **A coherent fitted upper-torso assembly was not achieved.** The torso, separate shoulder study and separate fixed hand all remain **ART_REVISE**. No human approval, canonical replacement, completed-Ada claim or reusable-recipe promotion is issued.

## Retained editable sources

| Lane | Work file | Frozen checkpoint | Outcome |
|---|---|---|---|
| Primary torso | [Armor work](<C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW5/armor/ada_bw5_armor_work.blend>) | [Armor r003](<C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW5/armor/ada_bw5_armor_checkpoint_r003_ART_REVISE.blend>) | Proportion improvement; fit and enclosure fail |
| Separate shoulder | [Shoulder work](<C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW5/shoulder/ada_bw5_shoulder_work.blend>) | [Shoulder checkpoint](<C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW5/shoulder/ada_bw5_shoulder_checkpoint_ART_REVISE.blend>) | External clearance improves; evaluated self-folds and suspension fail |
| Separate fixed hand | [Hand work](<C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW5/hand/ada_bw5_hand_work.blend>) | [Hand checkpoint](<C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW5/hand/ada_bw5_hand_checkpoint_ART_REVISE.blend>) | Retained correction 1 clears tested crossings; form and contact fail |

All were saved and reopened. The primary r003 source SHA-256 is `e1acb1cb3e11be218b7a0f381921e8da7e81a46a87a4f68f35151e28ab657899`. Earlier BW5 checkpoints and failed attempts remain available. The shoulder and hand studies were **not merged** into the primary torso. Its old BW4 collar, shoulders, head, hands, bracers and lower costume are explicitly unresolved context.

## Primary torso: actual changes and comparison

Direct section editing replaced the front control surface with deliberate lateral columns, shortened its occupancy above the belt and reduced its forward projection. The back was fitted separately, including its upper armhole setbacks and rising central hem; the front retains a shallow downward center. A connected navy waist envelope was constructed from evaluated garment sections. Body proportions, padding geometry and the rear tabard split were preserved.

The initial construction and two substantive corrective passes are retained. A final integrity-only repair in r003 reordered two interior neckline rows on the front and back and their side returns. Their previous reversed order folded the surfaces. This repair kept the selected opening boundary, height, width, hem and chest profile; it was not another likeness pass or permission to continue equivalent variants.

New collar attempts failed through coat conflicts, excessive flare and poor opening construction. They remain hidden as rejected experiments. The BW4 collar was restored as context, without claiming improvement.

| Same historical front-camera measure | BW4 | BW5 r003 | Approximate handoff reference |
|---|---:|---:|---:|
| Center plate height / selected plate width | 0.731 | 0.614 | 0.60 |
| Evaluated outer collar span / plate width | 0.500 | 0.500 | 0.65 |
| Center waist-underlayer exposure / plate height | 0.006 | 0.194 | 0.14 |

Plate width was not enlarged to improve a ratio. These measured model endpoints are consistent between the two Blender revisions, but differ from the handoff's manually selected painted pixels. They are review guides, not precise recovered 3D dimensions or a likeness score. The waist exposure now exceeds the approximate reference relationship.

At the center chest section, coat-to-inner-plate axial separation fell from about **68.1 to 24.7 mm**; at upper chest it is now **14.7 mm**. However, an upper anterior section at X=125 mm, Z=1470 mm still has approximately **95.1 mm separation**. The profile shows an open wedge between the plate, padding and shoulder bridge. A clear intersection query cannot compensate for this floating fit. The chest has also become too flat across its width and lacks Ada's decisive central plane transition.

- [Matched BW4 / r003 clay comparison](<C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW5/armor/captures/BW4_vs_BW5_r003_TORSO_ART_REVISE.png>)
- [Measured body, coat and shell sections](<C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW5/analysis/BW4_vs_BW5_r003_torso_sections.png>)
- [Separate reference-pose comparison](<C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW5/analysis/BW5_r003_body_anchored_reference_comparison.png>)
- [r003 numerical summary](<C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW5/analysis/R003_FINAL_FIT_SUMMARY.json>) and [fit addendum](<C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW5/analysis/R003_FIT_ADDENDUM.md>)
- [Reference registration and uncertainty](<C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW5/analysis/r003_registration_body_anchors.json>)

The reference comparison uses an independent lowered-arm context, separate orthographic cameras and one uniform scale/translation using inferred clavicle and waist proxies. Hidden landmarks have explicit uncertainty. Plate corners were not used to register away the mismatch. This is an approximate reference-like pose, not an exact projection match.

## Geometry, motion and remaining major defects

The final r003 raw and evaluated self-query found **zero confirmed nonadjacent transverse pairs on all 19 owned visible parts at frame 1**. The original authoring action's six numeric curves match BW4 exactly. Full arm-motion queries were rerun against the frozen r003 source for all **97 integer frames**, plus eight quarter-frame samples near selected critical transitions.

| Final r003 relationship | All-97 authoring-frame result |
|---|---|
| Main front plate vs evaluated coat / body | 0 confirmed transverse pairs |
| Main backplate vs evaluated coat / body | 0 confirmed transverse pairs |
| Navy enclosure vs coat | Fails from frame 1; maximum 76 pairs |
| Navy enclosure vs belt | Fails from frame 1; maximum 384 pairs |
| Thorax side walls vs coat | Fails from frame 1; maxima 244 / 270 pairs |
| Shoulder bridges vs coat | Fails from frame 1; maxima 154 / 166 pairs |

Pair counts describe repeated triangle observations, not independent defect counts. Queries screen noncoplanar transverse intersections; coplanar overlap, tangency, containment and continuous-time collision freedom are not certified. The hidden rejected collar also appears in historical/audit records; its results are not evidence for the restored visible collar.

The original 97-frame action is an arm diagnostic. Two additional static tests on the independent reference rig exposed further failures: a 10-degree forward bend and 15-degree torso twist make the backplate, side walls and waist envelope cross the coat. These tests do not establish a supported anatomical range or substitute for game animations.

The retained torso's major defects are:

1. **Upper plate fit and shape:** approximately 95 mm local anterior separation, open bridge/rim wedge, and a broad flat chest without the intended ridge and planar transitions.
2. **Collar and garment opening:** unchanged undersized collar relationship, ragged underlying neck opening and unfinished collar-to-plate construction. The replacement collar was rejected.
3. **Waist and sides:** excessive center exposure, coat/belt intersections, and side closures that do not form a coherent fitted enclosure.
4. **Torso movement:** static bend/twist reveals rear and side conflicts even though the main plates clear the original arm action.
5. **Shoulder context:** the primary file retains the unsuccessful BW4 shoulder. The separate BW5 study is also rejected, as described below.

Evidence: [all-97 queries](<C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW5/armor/records/r003_all97_crossings.json>), [critical subframes](<C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW5/armor/records/r003_critical_subframes.json>), [bending diagnostics](<C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW5/armor/records/r003_supplementary_bending.json>), [self-integrity and action checks](<C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW5/armor/records/surface_integrity_r003.json>), [save/reopen verification](<C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW5/armor/verification_r003.json>).

Actual captures include [control cage](<C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW5/armor/captures/r003_retained_actual_control_cage.png>), [reversed key](<C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW5/armor/captures/r003_retained_reversed_key.png>), [waist color-ID diagnostic, not final textures](<C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW5/armor/captures/r003_retained_waist_color_ID_NOT_TEXTURED.png>), [bending profile](<C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW5/armor/captures/r003_diagnostic_forward_bend_right.png>), and labeled rest/critical-pose front, side, back and three-quarter images.

The [97-frame torso movie](<C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW5/armor/motion/r003/BW5_ARMOR_AUTHORING_DIAGNOSTIC_NOT_GAME_CLIPS.mp4>) is 800 × 800 at 24 fps, bound to the frozen r003 file. Its SHA-256 is `8e73188d467da5f9dff9b6ca2f3e319a2e309a081113cc426a3fcbd472d85e22`. All 97 encoded frames were reopened and decoded. Frame-by-frame visual inspection uses chronological sheets and native stills; it is not a claim of real-time playback or continuous collision proof. [Independent visual review](<C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW5/reviews/independent_hand_torso_visual_REVIEW.md>) records the reviewed source and limitations.

## Separate shoulder and fixed hand

**Shoulder:** new cap cutaways and a reconstructed lowest-lame corner clear sampled coat and inter-plate crossings over all 97 frames and 13 extra samples. Yet the evaluated cap retains **135 self-crossing pairs** and the lowest lame **111**; BW4 had no detected self-crossings in those parts. The cap drops with the upper arm in the lowered pose, exposing inadequate proximal coverage. This is a structural regression and attachment failure, not a successful moving shoulder. See [shoulder review](<C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW5/shoulder/REVIEW.md>) and [matched captures](<C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW5/shoulder/captures/BW4_vs_BW5_SHOULDER_ART_REVISE.png>). Do not propagate it to the other side.

**Hand:** invalid palm/root/web faces were replaced around an explicit outside hilt channel. Retained correction 1 has zero tested raw/evaluated transverse self, hilt, guard and blade crossings, with the exact original 20-vertex wrist boundary retained. The selected **30 × 26 mm / 110 mm exposed hilt**, unchanged blade and guard remain locked. No new equipment decision or whole-hand scaling was introduced.

The glove still reads as repeated rounded finger rings, a flat creased palm and a hooked thumb with inadequate thenar support. All five predeclared pad groups have **0 of 27 evaluated samples** in the −0.5 to +1.0 mm contact band; median gaps range from **3.529 to 6.649 mm**. Correction 2 improved some contact but introduced palm/web seams and self-crossings, so it was rejected. See [hand review](<C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW5/hand/HAND_REVIEW.md>), [matched images](<C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW5/hand/captures/BW4_vs_BW5_HAND_ART_REVISE.png>), and [actual grip sections](<C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW5/hand/captures/BW5_HAND_ACTUAL_SECTIONS.png>). Its 48-frame movie is explicitly a static camera orbit, not carrying or game-animation evidence.

## Preservation and acceptance boundary

All **169 predeclared protected files** match their intake hashes, including earlier candidates and listed source assets. The primary reopen check preserves **93 original/context mesh and shape-key records**, historical camera matrices and authoring action values. Coat thickness remains +6 mm, leggings +2 mm, both offset −1 with even-offset disabled. Head/hair, approved references, source MPFB topology/keys, sole and canonical game data were preserved. [Preservation record](<C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW5/records/preservation_after.json>) and [delivery verification](<C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW5/verification.json>) record the actual checks.

New candidate game-bind conversion, the seven actual game clips and transitions, Unreal import/reimport, packaged tests, new cuff/bracer integration and a second compatible-body fit remain **NOT_RUN**. Local fit/construction did not earn those dependent gates. No unrelated game test suite, neural training, downloads or new modeling toolkit replaced the asset work. Background Blender and direct rendered-image inspection kept desktop interaction to a minimum.

## Precise next intervention

The bounded methods are parked. Retain the improved plate occupancy and useful lower/chest section clearances, then **reconstruct the upper plate/neckline and its side closure against a jointly designed padded collar interface**, using front, profile and lowered-arm views before adding detail. The local upper wedge requires a new surface/attachment relationship; another uniform scale, broad smoothing or outward offset will not resolve it. Do not silently shrink the body or padding to make that surface fit.

For the shoulder, redesign the proximal cap surface and suspension together so a supported cap stays near the shoulder while the arm moves beneath it. Prove wall thickness without folds before restoring its bevel. For the separate hand, retain the empty hilt channel and exact wrist interface but replace the palm/thenar and proximal knuckle construction against an anatomical sculpt/control-surface target; do not keep tightening repeated ring profiles. These are specific follow-on interventions, not claims that BW5 has passed.

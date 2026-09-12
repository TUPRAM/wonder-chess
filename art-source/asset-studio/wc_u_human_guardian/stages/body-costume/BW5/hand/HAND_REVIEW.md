# BW5 fixed-hand lane — ART_REVISE

The new outside-channel construction removes the confirmed hilt/guard and self crossings found in BW4, but it is **not yet a convincing fixed game grip**. Retain **correction 1** as the editable candidate. The second corrective construction was rejected because it introduced palm/web seams and self crossings. The bounded assignment stops here; armor work is independent.

## Delivered source

- `ada_bw5_hand_work.blend`: retained correction 1 with review status and anatomically declared contact groups.
- `ada_bw5_hand_checkpoint_ART_REVISE.blend`: frozen retained candidate.
- `ada_bw5_hand_initial.blend`: initial new palm/root/web construction, retained as a failed attempt.
- `ada_bw5_hand_correction1.blend`: useful outside-channel construction before final review metadata.
- `ada_bw5_hand_correction2.blend`: rejected final construction; preserved with its actual images and queries.

The working/frozen files were reopened in a fresh Blender 5.1.1 process. Their mesh/transform hashes match. The visible cage has **1,026 vertices and 1,114 faces**; subdivision level 1 evaluates to 4,279 vertices and 8,516 triangles. These counts describe editability and evidence scope, not artistic quality.

## Executed method and bounded outcome

1. **Initial construction:** removed the BW4 palm, proximal roots and web. Retained four distal pieces only after a declared 28-degree section cut; built new flattened proximal sections, a connected palm and a separate rounded thumb branch around the fixed hilt. The source distal inner surfaces still entered the hilt. The new branch also had incorrect loop correspondence. Raw/evaluated self crossings: **16/65**. Hilt crossings: **233/396**. Guard crossings: **18/16**. Worst evaluated sampled hilt penetration: **4.517 mm**.
2. **Correction 1 — retained:** replaced the unusable distal inner surfaces as well as the roots with articulated flattened control sections. Corrected the branch's explicit cyclic loop correspondence and the wrist bridge correspondence. A broad, connected palm and new thumb/web replaced the old harmonic displacement field. The actual octagonal grip remains outside the mesh in the tested sections and surface queries. This materially improves the previous channel defect, but the rendered fingers still look too similar and the palm/thenar forms are not successful.
3. **Correction 2 — rejected:** attempted varied proximal proportions, a fuller thenar area, a wider rebuilt thumb-root opening and closer opposing pad placement. The new palm/web transition produced **12 raw / 28 evaluated self crossings** and **30 boundary edges**, rather than the intended wrist-only 20. Real cage and clay images expose the seams. A smaller contact gap cannot outweigh those regressions. No further modeling revision was performed.

This was an actual topology and rest-surface change, not an animated thumb search or another displacement-coefficient pass. No whole-hand scaling, hilt repositioning, added subdivision or Boolean cavity was used. The initial and both substantive corrections remain inspectable.

## Retained geometry screen

The read-only query reuses the existing BW2/BW4 BVH candidate stage followed by confirmed nonadjacent segment/triangle intersections. It tests the **actual selected hilt, unchanged guard and blade**, including triangle interiors through bidirectional edge/face tests. Obstacles hidden in selected images remain in the complete query.

| Screen on retained correction 1 | Raw cage | Evaluated surface |
|---|---:|---:|
| Confirmed nonadjacent transverse self pairs | 0 | 0 |
| Actual hilt transverse pairs | 0 | 0 |
| Actual guard transverse pairs | 0 | 0 |
| Actual blade transverse pairs | 0 | 0 |
| Sampled vertices inside hilt | 0 | 0 |
| Triangles with all vertices inside hilt | 0 | 0 |
| Minimum sampled hilt clearance | 1.371 mm | 1.890 mm |

The cage has one intentional **20-edge wrist boundary**, no other nonmanifold edges, no loose vertices and no zero-area faces in the tested thresholds. All 20 original source wrist positions match exactly. The source geometry hidden for comparison uses an independent mesh data block.

**Limits:** the legacy query excludes shared-vertex self pairs and does not classify coplanar overlap or tangency. Vertex distances are samples, not an exact deepest-volume solver. These results are a clear transverse-intersection screen, not a mathematical collision-free certificate or an artistic pass.

## Distributed contact still fails

The retained construction's anatomical pad groups were declared by construction station and profile sector **before scoring**, without selecting nearest vertices after the result. Each raw group contains 10 vertices. Each evaluated group contains 27 vertices using inherited weight greater than 0.999. The source correspondence and exact points are recorded in `records/retained_pad_mapping_before_scoring.json` and `records/retained_geometry.json`.

| Evaluated pad | Minimum gap | Median gap | Maximum gap | Samples in −0.5 to +1.0 mm band |
|---|---:|---:|---:|---:|
| Index | 6.060 mm | 6.649 mm | 7.581 mm | 0 / 27 |
| Middle | 5.705 mm | 6.400 mm | 7.306 mm | 0 / 27 |
| Ring | 6.060 mm | 6.649 mm | 7.581 mm | 0 / 27 |
| Little | 3.843 mm | 4.644 mm | 6.329 mm | 0 / 27 |
| Thumb | 1.890 mm | 3.529 mm | 5.949 mm | 0 / 27 |

The loose channel is also visible in axial images and actual sections. The hand therefore does not establish credible persistent contact or force closure. No fixed-grip acceptance is issued.

## Equipment, handedness and preservation

The selected **30 × 26 mm octagonal hilt**, **110 mm exposed span**, **154.4 mm total span**, original guard and blade remain exactly equal to BW4 in raw vertices, faces and object transforms. No additional registration change was made. No pommel is assumed. In the retained frame, the guard is toward **+X**, the index and thumb are at that end, and the little finger is toward −X. `BW5_HAND_DIGIT_REGISTRATION.png` labels those actual projected construction locations with the guard visible.

The BW4 frozen source still hashes to `f85003358791c8346f4432a0fbdfc797047abca19ca9dc33c9d66428b411ffa3`. Its historical palm, dorsal, side, underside, oblique and axial camera matrices are unchanged in the new candidate. The original MPFB source, original shape keys, previous experiments, head/hair, garment/sole, canonical sword and game skeleton/actions were not edited by this lane. The rendered derivative contains a glove exterior; it does not claim repaired bare-hand anatomy, and no master body faces were deleted.

## Real review evidence

- `captures/BW4_vs_BW5_HAND_ART_REVISE.png`: freshly rendered BW4 versus retained BW5 in the same palm, oblique and axial cameras.
- `captures/BW5_HAND_ACTUAL_SECTIONS.png`: evaluated glove and actual hilt triangle-plane intersections at X = +27, +3, −19 and −39 mm. These sections show the outside route and remaining loose channel.
- `captures/retained_actual_cage_{palm,oblique,side,underside}.png`: actual raw source edges, subdivision disabled for the diagnostic.
- `captures/retained_uniform_clay_key.png` and `retained_uniform_clay_reversed_key.png`: same geometry/material/camera/exposure, reversed area key.
- `captures/retained_full_*.png`, `retained_hilt_only_*.png`, and `retained_equipment_hidden_*.png`: whole equipment and isolated construction views labeled by purpose.
- `captures/BW5_HAND_REJECTED_CORRECTION2.png`: actual failed final surface and cage, retained without concealment.
- `motion/BW5_HAND_ART_REVISE_STATIC_INSPECTION_NOT_GAME_CLIPS.mp4`: 48-frame, 24-fps, 800 × 800 **static-shape camera turntable**. The encoded MP4 was reopened and all 48 frames decoded in Blender; eight temporal samples were visually inspected. This is not hand animation, wrist integration, carrying verification or seven-action evidence.

The reviewer inspected the retained palm, oblique, axial, actual cage, evaluated section, reversed-light view, labeled registration and eight decoded movie samples. The visual defects remain visible across these views. Tool execution has not been substituted for visual review.

## Exact remaining defects and next intervention

1. **Proximal/finger form:** four separated digits remain too regular in profile, spacing and repeated rounded silhouettes. The intended joint planes do not read as a convincing knuckle rhythm.
2. **Palm:** the longitudinal panel topology fans into the roots and wrist with stretched diagonal/parallel creases. The axial view exposes an overly thin, flat palm profile.
3. **Thenar/thumb support:** the thumb reads as a hook attached to a narrow side transition rather than a strong rounded thenar mass with a convincing opposing pad. The retained surface clears the query but lacks the required anatomy.
4. **Contact:** every declared pad group remains outside the comparison contact band; long-finger median gaps are roughly 4.6–6.6 mm.
5. **Wrist:** the exact opening is preserved, but the new palm-to-wrist flow and cuff/forearm connection are not visually accepted or integrated.

**Recommendation:** keep the verified empty-channel envelope, selected equipment frame and exact wrist interface. Replace the palm/thenar and proximal knuckle control surface with a small anatomically shaped local sculpt/control-cage intervention. Use the actual hilt as a keep-out reference while placing independent palm, metacarpal and thumb-base volumes; then reconstruct the visible contact surfaces against that target. Do not keep shrinking this ring-based construction or tightening all five digits by a common coefficient. The rejected second correction specifically shows why a wider branch and fuller panel alone do not resolve surface correspondence.

**Not run:** source-to-game bind conversion, cuff/bracer integration, seven canonical candidate animations/transitions, Unreal import/reimport, packaged checks, independent recipe replay and second-body fitting. Those gates stay unrun because local construction/contact has not become credible. No human approval, recipe promotion, canonical replacement or completed-Ada claim is made.

# BW2 anatomical-right grip review

**ART_REVISE — calibrated contact construction executed; a convincing sword grip has not been established.**

This is the bounded right-hand assignment from BW2. The open-hand frame and finger directions were corrected, a fixed handle was fitted, individual fingers and the opposing thumb were posed, and the evaluated surfaces were inspected. The retained candidate improves the middle/ring wrap, but the thumb reaches its contact partly through self-intersecting hand geometry. Neither pad-distance screens nor a stable attachment override that failure. No human approval was issued.

## Editable source and scope

- Working file: [ada_bw2_grip_work.blend](ada_bw2_grip_work.blend).
- Frozen result: [ada_bw2_grip_checkpoint_r001_ART_REVISE.blend](ada_bw2_grip_checkpoint_r001_ART_REVISE.blend), SHA256 `d64d5900317541710d5ef29939d12559e5ecef31777a7e9261158cbccb7a41cf`.
- Active scene: `BW2_RIGHT_GRIP`; retained closed inspection pose at frame 37.
- Parent: BW1 frozen r003, SHA256 `03829ab406d6bd5e6a1c5f86e045e9f2edc720b05e620e70017667c59be8b3f8`. Initial live work file was preserved separately; this candidate was saved to the BW2 directory.
- Owned work: right finger pose, one wrist-parented semantic frame and cylindrical fixture, a separate BW2 carrying action, cameras/lighting/diagnostics. The original glove mesh, weights, body, rest skeleton, shape keys, costume, armor and equipment geometry were not remodeled. Glove viewport subdivision was changed from 0 to 1 to measure the same level used by render subdivision 1.
- The original `BW1_DIAGNOSTIC_RANGE_ART_REVISE` action is retained separately; the candidate uses `BW2_RIGHT_GRIP_CARRY_DIAGNOSTIC`. No canonical game skeleton or game source was changed in this assignment.

## What was demonstrated

The wrist, finger-base landmarks, fingertip direction and actual palm surface were expressed in metric world space. The rig has a positive uniform world scale of 1.143804065 and approximately 180-degree Z rotation; those transforms were included exactly once. The frame determinant is +1, its distal direction points toward the fingers, and palmward was checked against actual pad/thenar and dorsal/nail images. The largest calibration round-trip error was about 0.000133 mm. See [calibration review](calibration-independent/REVIEW.md).

All 15 right finger joints received reversible local X/Y/Z probes of plus/minus 5 degrees, 90 probes total. The evaluated glove restored exactly after each probe. Index through little finger curl palmward on local +X. The thumb requires separate opposition and pad-orientation controls; small-angle calibration does not establish safe combined ranges.

The fixture is an intentional diagnostic fitting decision, not a recovered Ada measurement: **28 mm diameter, 109 mm total span, 105 mm usable span after 2 mm end margins**. Its hand-space center is (0, 0.096000001, 0.039601333) m; its long axis is (0.970016062, 0.243040547, 0). It was fitted once against the open palm and then locked. The single parent chain is right wrist -> semantic hand frame -> handle. No per-finger or per-frame handle adjustment, whole-hand scaling, bone stretching or double-driving constraint was used.

The middle/ring corrections combined proximal orientation and flexion so the pads wrapped down the cylinder instead of perching above it. The thumb acquired opposing measured radial contact. However, the latter construction was rejected as a complete grip because it intersects the hand.

## Contact observations — numerical screens only

The contact regions were declared on the open evaluated glove before closure, using the distal phalanx palmar pad, 30–75% along its length, a +/-4 mm width band, and palm-normal screening. Their vertex IDs were not reselected after fitting. Evaluated glove topology remained 9,130 vertices; the right connected component has 4,565. The supplied BW2 calculator was executed on actual world-space pad points and the measured handle endpoints.

Across all **121 held frames (25–145)**:

| Digit | Minimum samples in -0.5 to +1.0 mm band | Gap range across held frames | Largest per-frame p95 gap |
|---|---:|---:|---:|
| Thumb | 9/9 | -0.376 to +0.879 mm | 0.829 mm |
| Index | 6/7 | -0.350 to +1.613 mm | 1.251 mm |
| Middle | 8/9 | -0.342 to +1.281 mm | 1.081 mm |
| Ring | 7/9 | -0.492 to +1.490 mm | 1.319 mm |
| Little | 10/12 | -0.251 to +1.330 mm | 1.302 mm |

All declared patches remained within the usable axial span. These fractions satisfy the proposed sampled band screen; they do not prove force closure, anatomy or nonintersection. The retained thumb/middle radial-direction dot product was approximately -0.830, an opposing direction measure rather than artistic acceptance.

An independent triangle-interior query at the retained pose checked 9,088 right-glove triangles against the ideal capped cylinder. Maximum depth was bounded at 0.491920–0.491974 mm; no queried triangle exceeded 0.5 mm. The actual 96-sided fixture is represented by its circumradius in these calculations; its face radius differs by approximately 0.0075 mm. This is not a continuous-time exact polygon collision certification.

Full details: [all-frame contact and attachment records](reviews/carry_contact_measurements.json), [triangle and self-intersection audit](integrated-independent/integrated_geometry_audit.json), and [frozen scene contract](records/frozen_scene_contract.json). The [static-to-final geometry binding](reviews/static_geometry_to_final_binding.json) confirms exact equality of evaluated glove/body vertices, topology and world matrices between the collision-audited pose and delivered frame 37; maximum vertex difference was zero.

## Why the grip remains rejected

1. **Inter-finger and thumb/web self-intersection is major.** The retained glove has 375 confirmed nonadjacent transverse triangle-crossing pairs: 167 middle/ring, 88 palm/thumb, 58 middle/thumb, 52 index/thumb, and 10 within digits. The underlying MPFB body also has confirmed crossings (567 pairs). These are pair counts, not 375 or 567 independent defects. The visible long knife-like fold into the palm is supported by geometry evidence, and the handle-hidden views do not rescue the anatomy. Improved pad wrap was achieved without sufficient clearance between neighboring fingers.
2. **The thumb pad is not convincingly presented as an external opposing surface.** A small distance to the cylinder is possible even when the route to that position tunnels into the hand.
3. **Middle/ring web pinching and angular finger transitions remain.** The improved distal wrap does not establish that the entire finger/web deformation is sound.
4. **The strongest thumb fit reaches a tested search bound:** distal local-Z is -20 degrees. Its safe anatomical range was not validated. A second retained thumb candidate also folded the web and reached the opposite Z bound. Neither was promoted.
5. **A deformation-mode switch was insufficient.** Unsaved preserve-volume/dual-quaternion diagnostic variants retained the fold and self-crossings in both body and glove. The glove still had 368 crossing pairs, and its maximum handle penetration worsened to 0.720444–0.720497 mm. Existing thumb/metacarpal weights already blend across 143 selected glove base vertices; this is not a 143-vertex direct wrist-weight mask. The unsmoothed cage itself has 201 crossings. The original live modifier remains unchanged. A blanket glove-weight transfer or normalization is not supported as a fix for this pose.

The initial calibrated construction and bounded contact corrections are retained as distinct attempts. Middle/ring enclosure improved, but further thumb pose search was stopped after the two retained thumb corrections failed the complete visual/surface test. Numerical cap-only contact discovered during fitting was rejected explicitly; it was not counted as a valid grip.

## Carrying boundary

A separate 145-frame, 24 fps authoring diagnostic opens/closes the hand, then holds the same finger pose while testing wrist rotation, elbow bend, arm raise and a short guard sweep. Frames 1–24 are approach/closure, not persistent-contact frames. This is not a retarget of the game's Move or Attack.

The maximum measured handle drift relative to the wrist during the held range was **0.000305 mm and 0.000006391 degrees**; the semantic holder drift was 0.000265 mm and 0.000005964 degrees. This demonstrates a stable fixture attachment in the sampled source action. It does not pass the complete carrying gate: the hand self-intersects, the real sword was not fitted, and guard/pommel clearance was not tested.

The [source-bound movie](motion-carry-final/ada_bw2_fixed_handle_ART_REVISE.mp4) and 145 native frames are diagnostic evidence of this retained ART_REVISE state, not an approved sword grip. The movie was rendered from the final frozen checkpoint at 800 x 800, 24 fps, with a fixed-orientation camera tracking wrist translation only and 0.32 m orthographic scale. Its SHA256 is `acce52246f19720f0bc6b7f28c54dd94eb3f4016931ff1bab751c2ca29c21eb0`. A fresh native Blender process decoded all 145 movie frames successfully. Root inspected all 145 native frames in five unskipped sheets and frames 14, 25, 93 and 121 at native size. The hand and fixture remain within the recorded view; the web fold develops during closure and persists through the held sequence. Live Blender timeline playback was also operated and observed through computer use. None of those observations removes the confirmed self-intersection defect.

## Evidence to inspect

- Initial versus retained BW2 closeups: `captures/grip_initial_*.png` and `captures/grip_integrated_*.png`, with matched cameras and clay.
- Reversed key: [retained reversed-light view](captures/grip_retained_reversed_light.png).
- Handle hidden: [axial opening and web](captures/integrated_axial_handle_hidden.png).
- Actual posed base cage: [axial](captures/actual_posed_cage_axial.png), [back](captures/actual_posed_cage_back.png). These use the real original control mesh with armature deformation and subdivision disabled, plus a wire overlay; they are not generated construction diagrams.
- Body/glove and linear/dual-quaternion comparisons: `integrated-independent/`.
- [Independent visual review](reviews/independent_grip_review.md).
- [BW2 initial versus retained correction sheet](captures/comparison_BW2_initial_vs_retained.png).
- [BW1 r003 versus BW2 contextual comparison](baseline-r003/comparison_BW1_r003_vs_BW2.png). The top row is r003's original OPEN frame 1 with its original handle, not its failed closed-grip experiment. The bottom row is the retained BW2 closed pose. Camera and light settings match; hand poses and handle dimensions intentionally differ and are labeled.
- [Frozen reopen/preservation audit](reviews/final_frozen_audit.json), [work-file audit](reviews/final_work_audit.json), and [measurement-source equivalence](reviews/final_source_chain_and_equivalence.json): both files reopened, all 16 required preservation checks passed on each, all 62 incoming hashes were unchanged, all 61 original mesh source records matched r003, and the original 492 animation curves remained exact. All 12 source-chain checks passed. These are technical preservation results, not art acceptance.

## Recommended next intervention

Keep the corrected world-space frame, fixed fixture, predeclared pads, indexed body master and the useful finger-wrap candidate. Start a **local thumb-base/opposition and web-deformation study on an independent derived hand copy**, with the handle hidden while proving the external thumb path. Establish a collision-free thumb sweep and thenar/web volume before optimizing handle contact. Compare body and glove together; the defect is already present beneath the glove. Exact inspection seeds and their verified body correspondence are in [the local weight/geometry diagnosis](integrated-independent/REVIEW.md); they are not yet a validated correction mask.

Any local reweighting, rest-space correction or pose corrective must preserve the established pad regions and be evaluated through the entire opening-to-hold sequence. Resolve middle/ring neighbor clearance as a separate local relationship before restoring their full contact pose. Include hand self-collision in the acceptance check before pad-distance optimization, so contact cannot be achieved by tunneling. Do not repeat another unconstrained whole-hand angle search or turn up subdivision.

No real sword adaptation, shield calibration, shoulder/cloth/knee/boot work, runtime import, independent recipe replay, second-body fit, model training or human approval was performed. The local result is **AUTHORING_ONLY**. A possible future runtime route is a fixed posed grip baked into a derived hand mesh; its rest-space conversion, wrist seam, hand weighting and actual game animations still need separate proof. The shared 27-bone game skeleton remains unchanged.

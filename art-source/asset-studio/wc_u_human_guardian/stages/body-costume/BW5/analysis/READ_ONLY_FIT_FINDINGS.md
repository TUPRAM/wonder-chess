# BW5 read-only fit findings

The frozen BW4 armor has room for a substantially closer central chest and back profile without changing Ada's body or padded coat. The upper-back lateral region is already tight. A section-specific fit and an armhole recut are appropriate; a uniform shell offset is not.

No source or candidate Blender file was saved by this analysis lane. Blender 5.1.1 evaluated immutable inputs in background processes. This is analysis, not forms approval or runtime acceptance.

## Frozen BW4 measured clearance

`bw4_sections_and_conflicts.json` retains actual evaluated triangle/plane intersections and all anterior/posterior ray hits. `BW4_evaluated_torso_sections.png` draws those measured intersections; it is a plotted section diagram, not a Blender beauty render. The body is gray, final padded coat orange, front plate blue, back plate magenta. The thin inner and outer shell surfaces are both present.

The chosen reference stations are world Z=1.1400, 1.2225, 1.3050, 1.3875 and 1.4700 m. They are explicit provisional analysis planes, not recovered dimensions from the artwork. Real rig landmarks are included: clavicle heads Z=1.461896 m, clavicle/shoulder junction Z=1.483331 m, spine03 head/tail Z=1.098645/1.201888 m, neck01 base Z=1.539533 m. `Bone.head_local` and `tail_local`, transformed by the armature world matrix, are used for these rest landmarks.

All 97 native authoring frames were additionally sampled after transforming the evaluated coat into the same-time moving `spine01` plate frame. Minimum sampled axial gaps, in millimeters:

| Station | Front center | Front X=100 mm | Back center | Back X=100 mm |
|---|---:|---:|---:|---:|
| Lower ribs | 68.85 | 35.30 | 77.86 | 43.31 |
| Chest | 68.14 | 37.05 | 75.93 | 37.07 |
| Upper chest | 58.70 | 28.95 | 51.64 | 11.10 |

At upper chest X=150 mm the back gap falls to 2.71 mm. This makes a central profile reduction feasible while requiring the lateral upper back to be handled separately. The values are directional gaps, not normal distances and not collision certification. Missing rays remain missing. The full relative-motion samples are in `bw4_motion_section_envelope.json`.

`bw4_section_extents.json` separates central connected section components from the arms where possible. At the shoulder where components join, the reported width includes the connected shoulder and is not called a hidden torso circumference.

## Specific BW4 conflict regions

`bw4_conflict_local_regions.json` re-executes the existing segment/triangle query at each first/worst pair. All crossing means are transformed back through the rigid owner to the undeformed plate frame.

- Backplate: first frame 1, 82 pairs; worst frame 29, 84. Cage neighborhoods 64, 75, 76 and 87 are implicated. The region spans about X=150–197 mm, Y=−151 to −118 mm, Z=1357–1451 mm. It includes the upper lateral armhole surface rather than just a decorative rim.
- Cap: first frame 1, 316 pairs; worst frame 54, 372. Both rear and anterior medial ends cross. In the local shoulder frame the region spans distal U=−65 to +36 mm, anterior=−103 to +110 mm. The first four logged examples alone underdescribe the affected region.
- Lowest lame: first frame 20, 32 pairs, nearest cage vertices 48/49; worst frame 28, 95, nearest 38/39/48. These are the distal anterior corner, U=198–209 mm, anterior=55–76 mm. A local corner/length recut is more directly supported than raising the whole shell radius.

Counts are triangle-pair observations, not defect counts. Coplanar overlap, tangency, containment and continuous-time freedom are not established.

## Initial BW5 torso review

Inspected the actual `initial_front.png`, `initial_profile.png`, and `initial_back.png` produced by the armor lane. Shorter center occupancy, reduced front projection and the rising rear hem are visible improvements. They do not clear the following construction failures:

- The initial waist radial casts pick up the distant arms and form large horizontal lobes. Use the connected torso surface, with reviewed ray direction and component selection.
- The front plate crosses the padded coat after interpolation even though its control vertices were bounded outside the coat. Chest Z=1.305 m has inner gaps +19.96 mm at the center, +4.46 mm at X=100 mm, −2.74 mm at X=125 mm, and −15.45 mm at X=150 mm. Add purposeful lateral surface support and recut the transition rather than restoring all the old center projection.
- At frame 1 the front shell has 1,733 confirmed transverse pairs against the coat; neckline return 144; left/right side returns 130/136. The back shell and back side returns have none in that frame. The new collar has 1,084, and the malformed waist has 1,316. This is a frame-1 diagnosis, not the required complete revised motion audit.
- The widened collar still reads as a tall straight sleeve around the neck in these initial renders. A flared, shaped opening and a controlled neck/shoulder relationship need review. The preserved jagged neck context is separately visible.

The initial semantic-cage projected ratios are H/W=0.6141, C/W=0.6648 and U/H=0.1941 under the unchanged BW4 front camera. These are already closer to the approximate reference ratios, yet the construction still fails. `initial_fit_diagnosis.json` contains source hash, exact sampled endpoints and counts. Collar C uses the evaluated maximal exterior span rather than the reference's manually selected upper rim. These conventions must not be silently equated.

The supplied art hides the actual natural waist and base of neck. A future body-based registration must label those landmarks as approximate/occluded proxies or use visible body anchors. The handoff contains plate/collar/belt endpoints, not validated naked-body landmarks. Do not label an armor-corner alignment as independent body registration.

## Correction 1 diagnosis

The revised support columns reduce the frame-1 front query from 1,733 to 1,221 pairs, neck return 144 to 62, and side returns 130/136 to 74/80. The back remains clear in that single-frame pair query. These are improvements in the measured pair count, not a fit pass.

The remaining front failure has two specific causes, recorded in `correction1_interpolation_diagnosis.json`:

1. A ray-miss control falls abruptly behind its neighbor: row-4 control 90 is `(0.14925, 0.14373, 1.298)` m, 17 mm ahead of the coat. Control 91 is `(0.16915, 0.09252, 1.298)` m where the ray misses the torso. That is a 51 mm depth falloff in only 20 mm horizontal distance. At X=150 mm, Z=1300 mm the final outer surface retreats 11.84 mm relative to the raw cage intersection.
2. Some connecting raw faces already intersect the coat. At X=140 mm, Z=1200 mm, the raw gap is −7.85 mm and the final outer gap is −7.98 mm. At X=120 mm, Z=1445 mm, raw gap is −2.10 mm. This cannot be blamed only on subdivision. The outside route must remain supported between rows as well as columns.

The waist's remote-arm lobes are removed, but 424 frame-1 transverse coat pairs remain. The correction-1 collar expands over connected shoulder volume and has 2,384 frame-1 coat pairs. Its full exterior width is no longer a valid proxy for the intended upper collar opening. Subsequent ratio records distinguish full evaluated collar C/W from the actual top-opening cage C_top/W.

`coat_neck_boundary.json` identifies the real, ordered, 38-vertex open neck boundary in the unchanged derived coat: X=±120.851 mm, Y=−143.972 to +8.668 mm, Z=1505.005–1539.741 mm. The vertical serrations are part of the source boundary. The source is preserved; any new collar connection must account for this actual opening rather than collecting the entire shoulder with radial rays.

`torso_frame_verification.json` establishes a positive-handed orthonormal anatomical frame from the actual clavicle and spine landmarks. Its determinant is 1 within floating precision, and its anterior direction agrees with source +Y. The existing measured horizontal sections intentionally retain the historical world-Z convention; they are not mislabeled as perpendicular to the slightly tilted anatomical centerline.

## Correction 2: retained plate improvement and unresolved construction

Inspected the actual correction-2 front, profile and back renders. The broad visible chest interference patches are gone; the plate is shorter and closer in central profile. The back retains the rising hem and the smaller upper armhole corner. The fitted navy band has replaced the initial arm-spanning lobes.

At frame 1, the queried front/back plates and their queried neck/side returns have zero confirmed transverse pairs against the final coat. The navy band still has 76 pairs, concentrated around X=−150 to +143 mm, Y=82–110 mm, Z=1119–1214 mm. The rejected collar still has 46, plus visible folds and torn-looking transitions inherited from the old jagged neck boundary. These counts do not include all object pairs or certify containment. The armor owner performs the separate complete 97-frame audit.

Central front inner gaps improve from 68.85/68.14/58.70 mm at lower ribs/chest/upper chest to 28.80/24.69/14.88 mm. Back center gaps become 53.40/27.20/10.12 mm. The actual section comparison is `BW4_vs_BW5_retained_torso_sections.png`; all underlying intersections are retained in `correction2_sections_and_conflicts.json`.

Two major visual fit problems remain despite those improvements:

- The front section is now almost flat across its width. The outer lateral support has become broad, and the upper anterior edge floats above the coat. A ray at X=125 mm, Z=1470 mm measures a 94.97 mm axial gap. The profile render shows open space beneath the shoulder bridge and upper neckline. The next intervention needs a controlled edge/neckline route and side return, not a return to the old forward center projection or another global smoothing pass.
- The attempted neck-boundary collar folds and does not produce the reference's tall, fitted collar. The armor owner has elected to retain the unchanged BW4 collar as explicitly unfinished context and preserve these failed collar versions separately. Therefore the improved C/W of the failed collar must not be reported as a retained assembly improvement.

The retained plate semantic H/W is 0.6142 and U/H is 0.1939 under the unchanged camera. The active collar must be measured after the context restoration. This remains **ART_REVISE**. The source-bound frame-1 diagnosis establishes local observations only; no human approval, actual seven-clip result, Unreal acceptance or replay is implied.

## Retained frozen source and reference comparison

Reopened `armor/ada_bw5_armor_checkpoint_ART_REVISE.blend` in two fresh read-only Blender processes and measured it directly. `retained_fit_diagnosis.json` and `retained_sections_and_conflicts.json` bind their results to its actual hash. `FINAL_FIT_SUMMARY.json` is the compact final numerical record. The unchanged restored collar has top-opening C/W=0.4428 (full evaluated silhouette C/W=0.4997), so no collar-proportion improvement is claimed.

`BW5_body_anchored_reference_comparison.png` compares the actual separately posed front render with the supplied artwork through a single uniform image scale and translation. The inference-marked artwork proxies are clavicle midpoint `(255,214)` with vertical allowance ±12 px and natural waist `(255,350)` with ±8 px. Both are occluded by costume; the rectangles make that uncertainty visible. The source points are actual projected rig landmarks, not plate corners. `registration_body_anchors.json` records the scene, source hash, camera matrix, pose frame, image hashes, transforms, crop, interpolation and uncertainty interval.

The comparison supports a closer plate height/width relationship, but the source still lacks the reference's strong controlled chest-plane change and full collar relationship. Covered anatomical proxies cannot establish exact silhouette likeness. The restored shoulders and collar are explicitly labeled old unresolved context. The candidate remains a partially improved, reviewable **ART_REVISE** source.

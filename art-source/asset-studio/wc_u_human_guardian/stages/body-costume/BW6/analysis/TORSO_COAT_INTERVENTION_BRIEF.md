BW6 torso / padded-coat intervention brief — read-only, ART_REVISE

The garment needs a local construction rebuild. The new rest-pose failures are not explained by the inherited sleeve problem, and the remaining outer-surface crossings cannot be repaired by changing Solidify settings alone. No smoothing, wrapping, cage correction, or replacement candidate was made in this review.

Exact source: C:\Users\iputu\Documents\Wonder Chess\art-source\asset-studio\wc_u_human_guardian\stages\body-costume\BW6\armor\ada_bw6_upper_combined_r001.blend
SHA256 before and after inspection: c8e689365a113c3b40728cf3a551492d61615541e45c6912cc94401bd4b8e9b9
The actual root scene objects were inspected directly. Current and inherited coat objects have identity world transforms to numerical tolerance and share BW4_Armor_Independent_Rig. The body retains its proper MPFB transform. No coat copy was substituted or given the body's world matrix.

What fails, and where

| Region | Direct observation | Specific next intervention |
|---|---|---|
| Collar inner wall / neck saddle | Rest: 75 self-crossing triangle pairs;71 inner/inner and 4 outer/inner. World envelope x -125 to125mm, y -131 to60mm, z1444-1563mm. The cutaway exposes deep inward folds at both collar sides and rear base. | Retain the exterior as a reference target, remove the defective collar-ring / neck-saddle transition on a new derivative, and lay out a compact deliberately spaced control boundary with explicit front, side and rear landmarks. Reconstruct the inner wall and seam return against that surface before sewing it back into the coat. Do not inherit the present sliver spacing or extrude another four rings from it. |
| Front surface beneath plate | Rest: 39 self pairs, including 6 outer/outer ; 10 raw-cage crossings in this region. Main clusters are the high central transition around z1431mm and side/lower-rib seams near x +/-153mm, z1276-1280mm. Associated controls include1871,1041, 471,1870,1764. | Replace those crossing strips with intentional face flow between sternum/upper-chest and side-waist sections. Preserve the fitted torso proportions; remove the local surface reversal before adding an inner wall. A rectangular smoothing region or another depth coefficient does not resolve the crossed connection. |
| Axilla / side transition | Rest: 10 inner/inner self pairs near x +/-153mm, z1277-1280mm; raw-cage failures already exist. Right armhole body crossings also occur near x164-167mm, z1345-1353mm. | Rebuild the seam/underarm junction as a volume with a deliberate sleeve-cap boundary. Keep the successful metal placement available as context, not as a way to hide the pinched cloth. |
| Body versus wall | Rest: 566 full-garment/body pairs but 40 when the wall is disabled. Nearest control-region localization:195 neck/saddle, 200 lower-front/waist, 124 side/back-waist, 47 right axilla. Lower-front contacts cover z1066-1223mm; side/back contacts z1147-1279mm. | After repairing the outer topology, fit explicit inner and outer sections to the actual BW6_BodyFit_Candidate. Restore local seam/lining space in these regions rather than shrinking the entire body or broadening every plate. The wall must be evaluated as part of the fit. |
| Posed sleeve / elbow | Current garment has 339 sleeve self pairs at sampled frame 20 and 332 at 49. The earlier hidden BW4 coat already has 232 total self pairs at 20 and 226 at 49. Matched isolated renders show the same diagonal elbow fold and distorted sleeve opening in both, while BW6 adds shoulder/neck rippling. | Reconstruct one elbow and sleeve-cap region with enough cloth volume and joint-oriented face flow, then author local joint weights against the actual forearm motion. Keep collar and sleeve ownership separate. Test the sleeve without armor before refitting the bracer. |

Why the collar method fails

The actual final top boundary has 92 edges, with lengths from 0.122 to 55.825 mm (median 4.810 mm). Twenty-eight edges are shorter than the 1.5 mm seam-wall setting. The operation in armor/operations/22_cut_and_sew_neckline.py preserves a highly uneven bisected aperture and uses a very small angular minimum while extruding the collar rings. The observed crowding and sharp saddle turns are consistent with the offset-wall folds; edge length alone is not a universal failure criterion. The actual cutaway is the stronger visual evidence.

The existing wall comparison supports changing construction: simple_clamped records 124 self pairs, while complex_constraints increases them to 455. The earlier recut file has 292 rest self pairs; it is a different saved candidate and must not be quoted as the current combined result. Current combined rest outer-only geometry still has 6 self pairs. No wall mode clears that outer defect.

Introduced versus inherited

The hidden original BW4 coat has 0 rest self pairs in this same scene/rig, while the new coat has 124. The collar, front and axilla rest failures were therefore introduced by the BW6 construction path. The original coat already collapses during elbow bending; that is an inherited deformation failure. For rest-space sleeve controls at absolute x >= 225 mm, 353 original vertices are position-identical and retain identical bone weights. Another 257 sleeve controls were inserted or changed, principally by the global section cuts. New non-skeletal thickness groups were excluded from the bone-weight comparison. Thus the sleeve was neither rebuilt as a tailored articulated garment nor literally left topologically unchanged.

The original-coat/body totals are not treated as a pristine historical body-fit baseline: they are queried against the current independently adjusted body. All numbers are sampled nonadjacent transverse triangle pairs, not counts of separate anatomical defects. Coplanar overlap, tangency, containment, and unsampled time are not established by this screen.

Actual evidence viewed

The two source combined rest renders (clay and color layout), plus all six new native Blender diagnostic images were inspected. Paths relative to this analysis folder:

- torso_failure_captures/rest_control_cage_region_map.png — actual posed control cage; red collar, orange front-underplate, purple axilla mark faces adjacent to nearest failed controls. This local association is not exact evaluated-face correspondence.
- torso_failure_captures/collar_inner_wall_cutaway.png — actual evaluated collar with the front half and lower garment removed only in a temporary render snapshot; red points identify binned confirmed self intersections.
- torso_failure_captures/current_sleeve_20.png and inherited_sleeve_20.png — matched camera and source pose.
- torso_failure_captures/current_sleeve_49.png and inherited_sleeve_49.png — matched camera and source pose.

All captures are bound to the unchanged source in torso_failure_capture_sources.json. Exact region points, nearest cage indices, bone weights, modifier observations and finite queries are in torso_failure_localization.json. Collar spacing is recorded in neck_cage_spacing.json.

Recommended bounded handoff

Use the current outer silhouette and source measurements as targets, then replace the collar/neck-saddle and the two failing front/side transition clusters on a separate garment derivative. Prove both outer surface and inner wall at rest first. Rebuild one sleeve elbow/cap region independently, preserving the master and canonical rig. Compare frames 1, 20, 49, 73 in the same views and then recheck the full motion. A changed garment invalidates dependent clearance evidence for its bracer and shoulder interface; keep the accepted shape improvements but refresh those checks. This brief does not authorize another whole-garment smoothing/wrap variant or claim art approval.

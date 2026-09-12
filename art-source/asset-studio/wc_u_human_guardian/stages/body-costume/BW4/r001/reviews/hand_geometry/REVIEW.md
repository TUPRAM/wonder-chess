# BW4 fixed-hand geometry review

**ART_REVISE. The second correction reduces several crossings, but the glove still crosses itself, the selected handle, and the guard. This bounded hand method should stop before cuff or runtime work depends on a credible grip. Independent armor work remains available.**

This review opened `ada_fixed_hand_correction1.blend` and `ada_fixed_hand_correction2.blend` in separate read-only Blender 5.1.1 background processes. Neither source was saved. File hashes before and after match in each result JSON. Queries use world metres from the actual glove and selected sword meshes. The handle was included in every query regardless of diagnostic visibility.

| Geometry query | Correction 1 raw / evaluated | Correction 2 raw / evaluated |
|---|---:|---:|
| Confirmed nonadjacent self-crossing triangle pairs | 116 / 183 | 64 / 141 |
| Glove / actual handle transverse triangle pairs | 303 / 540 | 301 / 527 |
| Glove / guard transverse triangle pairs | 51 / 83 | 25 / 30 |
| Glove / blade transverse triangle pairs | 0 / 0 | 0 / 0 |
| Worst sampled handle penetration | 11.979 / 11.467 mm | 11.560 / 11.814 mm |

The source has no separate pommel. The handle's capped end is part of its actual mesh query. Triangle pair counts are reproducible query results, not numbers of distinct artistic defects.

## Confirmed failure locations

The raw final cage's 64 crossing pairs classify approximately from original source weights and newly inserted web vertices:

| Approximate regions | Pairs | Example raw triangles | Intersection point in hand-frame mm |
|---|---:|---|---|
| Reconstructed web / thumb | 43 | 200 / 1675 | (27.425, 69.631, 30.828) |
| Palm/base transition / thumb | 12 | 907 / 2013 | (21.971, 71.153, 30.234) |
| Thumb / thumb | 5 | 905 / 1666 | (43.819, 68.114, 39.510) |
| Reconstructed web / reconstructed web | 3 | 1638 / 1645 | (46.435, 51.775, 51.767) |
| Ring / ring | 1 | 1275 / 1732 | (-27.746, 94.685, 26.182) |

These are transverse crossings, not coplanar contacts. The minimum acute triangle-plane angle is 23.165 degrees for the raw pairs and 15.177 degrees for evaluated pairs. All 64 raw pairs have an intersection span above 0.01 mm; 137 of 141 evaluated pairs do. Raw intersection spans range from 0.066 to 5.612 mm. The full exact vertices, triangle coordinates, intersection points, and spans are retained in the JSON files.

The worst handle penetration is at candidate vertex 709, corresponding to original full-glove vertex 1856. In the open source it is at `(-1.454, 102.707, 26.392)` mm, with `finger3-1.R=0.472817` and `metacarpal2.R=0.341992`, plus smaller neighboring base influences. This is the **middle proximal finger / metacarpal transition**, not a distal contact pad. Its final evaluated point `(1.723, 85.465, 31.719)` mm is 11.814 mm inside the selected handle. There are 951 evaluated vertices inside the handle, including 874 deeper than 0.5 mm.

The observed shape and operation together support a specific failure explanation: the free palm/base transition is allowed to move through the fixed handle while the distal finger sections are placed around it. The thumb/web reconnection also remains locally folded through itself. Better distal pad measurements cannot clear either failure.

## Contact-region correspondence and results

All five raw contact groups exactly retain the vertex IDs predeclared from the clean open source. The groups were not replaced with whichever points happened to be closest after fitting. Evaluated queries use only the inherited group core with weight above 0.999, so their IDs and counts are explicitly different from the raw cage. This is evidence of preserved declared membership, not a blanket claim that every new topology vertex has a reviewed anatomical label.

| Final evaluated pad region | Samples | Min / median / max signed distance to actual handle, mm | Samples within −0.5 to +1.0 mm |
|---|---:|---|---:|
| Thumb | 49 | −0.463 / 4.312 / 17.294 | 8 |
| Index | 42 | −0.765 / 3.884 / 8.815 | 5 |
| Middle | 41 | 2.085 / 4.827 / 8.844 | 0 |
| Ring | 47 | 0.598 / 4.148 / 8.596 | 4 |
| Little | 87 | −0.529 / 3.229 / 6.234 | 17 |

These contact screens do not override the confirmed crossings. No local grip pass is issued.

## Method and practical limits

The audit reuses BW2's existing `segment_triangle` and `self_audit` functions. BVH overlap supplies candidate triangle pairs; both triangles' edges are tested against the other triangle interior. Shared-vertex self pairs are excluded. Parallel/coplanar determinant cases are rejected by this transverse test, and coplanar/tangential overlap remains unclassified. The final result also confirms crossing spans and plane angles to separate material crossings from tiny numerical contacts.

Actual selected handle, guard, and blade triangles are queried; no ideal-cylinder proxy substitutes for the final target. Signed glove-vertex distances are measured against the closed convex actual handle. Fully contained glove triangles are recorded separately. The deepest triangle-interior penetration has not been solved exactly; the reported maximum is explicitly the worst sampled vertex depth. The glove's open wrist also prevents a general closed-volume containment certificate.

Files: `correction1_geometry.json`, `correction1_summary.json`, `correction2_geometry.json`, `correction2_summary.json`, and `correction2_failure_regions.json`. `audit_fixed_geometry.py` and `classify_final.py` record the executed read-only queries. No asset edit, additional modeling revision, hand/cuff pass, engine run, or human approval was performed by this review.

The next hand intervention should replace the failing connected palm/thumb/base surface against a collision-aware closed form, preserving the selected hilt. It must keep the metacarpal transition outside the handle and establish a rounded, noncrossing web before pad fitting. This is a precise local mesh intervention after the bounded method, not permission for a third equivalent correction pass or another angle search.

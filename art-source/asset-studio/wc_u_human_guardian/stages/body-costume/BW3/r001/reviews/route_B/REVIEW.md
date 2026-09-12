# BW3 route B — read-only audit

**ART_REVISE.** Route B delays the old inward failure but does not establish a valid thumb approach. The body web crosses during the base sweep; later, the dorsal side of the distal thumb penetrates the fixture while its declared palmar pads remain outside.

Frozen input `thumb_route_B_clearance.blend`, SHA256 `d6ea683f2224a06a63786bc0c3349c3acd22e71e568e48ec2ddcfd21704d3556`, unchanged after inspection. Scene `BW3_COLLISION_FIRST`; derived rig/body/glove only. Blender 5.1.1 background, no source save, pose override, optimization, weight or surface edit. Other digits were asserted OPEN on the evaluated rig at each sample.

| Surface | First self-crossing | First palm/thumb crossing | First handle triangle entry | First >0.5 mm handle penetration |
|---|---:|---:|---:|---:|
| Evaluated glove | 23.0 (within thumb) | 23.5 | 20.5 | 20.5 |
| Raw posed glove | 22.0 | 22.0 | 20.0 | 20.0 |
| Evaluated body | 19.0 | 19.0 | 20.5 | 21.0 |
| Raw posed body skin | 15.0 | 15.0 | 20.5 | 20.5 |

Each onset's preceding half-frame was sampled clear for that category. At frame 15 the source control state is CMC `[25,0,-20]` degrees, with MCP/IP still zero: the body web failure therefore precedes late thumb flexion. Its first raw pair is triangles 6360/6487, vertices `[3640,3630,3637]` and `[3642,3819,3211]`, at hand-space `(0.031110,0.070860,0.028652)` m. The first evaluated-body pair at frame 19 is triangles 17040/17547 near `(0.028303,0.070761,0.026354)` m.

The first evaluated-glove handle entry is triangle 12568, vertices `[1645,3856,8429]`, at frame 20.5. These are the back/side of the distal thumb, not its frozen palmar pad. At OPEN their normal dots against the mean declared-pad normal are −0.8673, −0.8833, −0.6931; longitudinal fractions are about 0.41–0.57 of the distal phalanx. They carry approximately 84–95% `finger1-3.R` weight. Exact open/posed normals, coordinates and groups are in `first_surface_ownership.json`.

At frame 145 the evaluated glove has 25 confirmed crossing pairs (17 palm/thumb, 8 within thumb), and minimum signed-cylinder vertex distance −13.25077 mm. The raw glove has 17 pairs and −13.19234 mm; evaluated body 27 pairs and −12.37722 mm; raw body 17 pairs and −12.22771 mm. These signed distances are vertex measurements; triangle-interior queries separately confirm penetration beyond 0.5 mm, rather than claiming those vertex values are the exact maximum triangle penetration.

The nine original thumb-pad samples at the endpoint remain +4.175…+10.372 mm outside the ideal cylinder, with **0/9** in the original contact band, although all remain within the usable axial span. The most deeply penetrating endpoint glove vertex 6156 is 100% `finger1-3.R`, approximately 90% along the distal phalanx, with OPEN normal dot −0.7330 to the pad normal. Better pad proximity alone would not resolve that dorsal-side tunnel.

This supports treating base-sweep web behavior and pad orientation/whole-thumb clearance as separate requirements. A final correction must address the early web fold as well as the later dorsal surface entry. A glove-only web blend or additional curl is not demonstrated sufficient here. No alternate angles or correction were searched in this audit.

Coverage: 113 surface-state samples: all 25 integer approach frames on each of four surfaces, adaptive half-frame onset samples, and endpoint 145 on each surface. This is not an all-frame carrying audit or whole-grip proof. The handle's actual source dimensions were checked against the contract; hand coordinates follow the posed wrist frame. Source body raw queries explicitly exclude helper geometry using the body skin group.

`route_B_results.json` contains exact samples/onsets and `first_surface_ownership.json` the surface diagnosis. Existing BW2 transverse-triangle and cylinder-interior routines were reused. Shared-vertex adjacency is excluded; tangency/coplanar contact and containment are not certified. Dominant weight labels approximate anatomy. The cylinder is an ideal circular proxy; its 96-sided display differs by up to about 0.0075 mm. No new image review is claimed by this numeric audit; root owns the matching live/render review.

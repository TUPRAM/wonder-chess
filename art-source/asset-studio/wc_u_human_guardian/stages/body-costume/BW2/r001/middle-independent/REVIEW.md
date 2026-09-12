# Independent middle-finger fit

The fixed 28 mm circular handle and all nine predeclared middle-pad indices were preserved. Only middle-finger X flexion and at most ±10° root local-Z abduction were varied. No `.blend`, glove geometry, weights, bone lengths, other fingers, or handle placement was changed.

Source: `bw2_calibrated_open_handle.blend`, SHA256 `983311ca1c50a44779982b455ca17c2d3db346950a90d59c82b177f9aaeed3f4`.

The initial pose X=[15.2,59.4,56.8]° reproduced gaps 1.266–7.297 mm with a full-right-hand minimum vertex SDF of −0.366920 mm. The touching region was the distal tip at roughly 79–91% along the distal phalanx, outside the frozen patch's 30–75% region; central pad samples around 45–51% remained farthest away. Simply adding curl would deepen tip penetration.

The best bounded candidate rolls more of the distal pad onto the cylinder:

| Pose bone | Local XYZ Euler degrees |
|---|---|
| `finger3-1.R` | 35.7667622094, 0, 10.0 |
| `finger3-2.R` | 43.5668738907, 0, 0 |
| `finger3-3.R` | 54.3330539618, 0, 0 |

Eight of nine original samples lie within −0.5 to +1.0 mm; all nine lie within the declared usable axial span. Gaps range −0.302334 to +1.262137 mm; median 0.150653 mm, p95 1.094923 mm. Evaluated sample 1351 remains the outlier at 1.262137 mm. The root's +10° abduction reaches the explicitly imposed bound; it was not increased.

Two deterministic bounded fits used 639 actual evaluated-mesh observations in total. The second start produced 7/9 contact and a weaker score, so the first was retained. `bounded_fit.json` preserves both results and the parameter trace. The evaluated mesh has 9130 vertices at the frozen level 1 arrangement; no pad indices were changed.

Actual matched palm, side and oblique before/after renders were produced. Initial side and all three best views were inspected. The candidate visibly changes fingertip-first contact into broader distal-pad contact. This is one middle-finger study, not a complete grasp or human approval.

`triangle_interior_audit.json` adds a full evaluated triangle test against the locked ideal capped cylinder: triangles are clipped to inward-offset axial slabs and their projected radial minima tested, followed by penetration-depth bisection. Across 9088 right-hand triangles, no candidate triangle penetrates more than 0.5 mm. The deepest candidate surface penetration lies between 0.3376846 and0.3377381 mm, compared with 0.3668976–0.3669510 mm initially. The 96-sided rendered proxy differs from the ideal cylinder by at most 0.0075 mm radially. This does not test glove self-intersection or the eventual combined finger/thumb pose.

Recommendation: apply these exact middle-only controls in the live candidate, then independently evaluate the combined hand. Retain the one sample above 1 mm and the root-abduction bound as explicit limits. No skin or fixture correction is justified by this local result alone.

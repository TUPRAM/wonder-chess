# BW3 final route C — ART_REVISE

**Route C removes the glove's detected tunneling but does not produce an opposing grip.** Its thumb pads remain far outside and face away from the handle. The underlying body web still self-crosses and intersects the glove. The initial route and two corrective iterations have reached the declared limit; retain this partial approach study at ART_REVISE and stop further pose fitting in this assignment.

Frozen input: `thumb_route_C_final_method_input.blend`, SHA256 `2dad0803a3e8bfd1974b3bf86dbf5377cd462807f02fb9e76f45463205ba2a1d`. Scene `BW3_COLLISION_FIRST`; action `BW3_C_ExternalApproach_ART_REVISE`; objects `BW3_Derived_Rig`, `BW3_Derived_Body`, `BW3_Derived_Glove`, `BW3_Locked_Handle_28mm`. Hash remained unchanged. This was a read-only Blender 5.1.1 background audit with no live MCP, source saves, pose search, weight changes or surface reconstruction.

## Full sampled route result

All 145 integer frames were evaluated on raw/evaluated glove and body, plus matching quarterframe samples at **13.25, 13.50, 13.75, 18.25, 18.50, 18.75** on every surface: **604 unique surface-state evaluations**. A separate actual glove/body intersurface query covered all 145 integer frames. Raw body queries use the skin group, excluding helpers. Other fingers remain OPEN throughout; this is not a whole-hand wrap or sword-grip proof.

| Surface | Confirmed self-crossings | Handle triangle penetration | First self-crossing |
|---|---|---|---|
| Evaluated glove | None in tested states | None in tested states | None detected |
| Raw posed glove | None in tested states | None in tested states | None detected |
| Evaluated body | Up to 14 pairs | None in tested states | **19.00**, clear at 18.75 |
| Raw posed body skin | Up to 9 pairs | None in tested states | **13.75**, clear at 13.50 |

The first raw-body crossing is palm/thumb triangles **6361/6486**, vertices `[3630,3627,3637]` and `[3642,3640,3211]`, near hand-space `(0.030154,0.067619,0.031397)` m. The first evaluated-body pair is **17040/17547**, near `(0.027224,0.069125,0.028508)` m. At frame 145 the evaluated body has 9 palm/thumb, 4 within-thumb and 1 palm/palm crossing pairs; raw body has 9 within-thumb pairs. These pair counts describe triangulated intersections, not separate visible defects or quality scores.

The closest evaluated-glove vertex stays approximately **0.4888–0.4893 mm outside** the ideal cylinder; raw glove approximately **0.3765–0.3770 mm outside**. These are whole-hand closest-point values, not thumb-pad contact. Triangle-interior checks also find no fixture entry in the sampled C states.

## Contact and orientation remain unsatisfied

Across all 121 held frames 25–145, the nine original thumb pads remain **27.591–31.635 mm outside** the cylinder, with **0/9** in the original −0.5…+1.0 mm band. All remain within the 105 mm usable axial span. Their mean normal dot **toward** the cylinder is approximately **−0.91177**, so they face substantially away from it. This is a separated thumb posture, not successful opposition.

The original evaluated glove correspondence remained 9,130 vertices; raw glove 2,294; evaluated body 36,579; indexed raw body 19,158. Evaluated polygon-index identities and vertex-group index/name tables were checked through every sample. The frozen pad indices were retained, not reselected after seeing the result.

## Body/glove fit is a separate failed check

Actual cross-object triangle tests find **131–170 transverse glove/body crossing pairs per integer frame**. Frame 1 OPEN already contains 137: 125 in a diagnostic wrist/cuff band (hand-space Y below 25 mm), plus 12 at the middle fingertip (approximately Y 189 mm). At frames 25 and 145 there are 163: **127 wrist-band, 24 new palm/thenar, and 12 middle-tip** pairs.

The new thenar/palm crossings lie near `(0.0358,0.0817,0.0128)` m. Thus glove-only self-clearance conceals an underlying-body/garment relationship that still fails. At the endpoint, 42 pairs touch exact open-glove boundary vertices; those are separately labeled. Neither that boundary label nor the broader wrist band automatically exempts an intersection. The 25 mm and 125 mm bands are diagnostic locations, not new acceptance tolerances.

No evaluated hand triangles had area below `1e-14 m²`; no nonfinite vertices were found. These structural screens do not negate the confirmed body fold. Containment/enclosure is **not certified**: the cuff is open, the body self-crosses, and the transverse test does not classify coplanar overlap or tangency. Cross-object intersection records are distinct from same-surface counts.

## What changed across A, B and C

The table compares the same endpoint 145. A/B were checked across approach frames 1–25 and endpoint 145; only C received the full 145-frame audit here.

| Route | Role | Evaluated-glove self-crossing pairs at endpoint | Minimum signed-cylinder vertex distance | Frozen thumb-pad gap range |
|---|---|---:|---:|---:|
| A | Initial external route | 51 | −13.312 mm | +0.289…+5.122 mm |
| B | First correction: retain base clearance | 25 | −13.251 mm | +4.175…+10.372 mm |
| C | Final correction: proximal orientation and reduced flexion | 0 | +0.489 mm | +27.592…+31.635 mm |

A/B brought pad samples closer while the dorsal distal thumb still passed through the cylinder. B's first entering triangle was independently identified as the back/side of the distal thumb from its OPEN normals and weights. C removes that passage by changing orientation and reducing closure, but loses contact and leaves a body-web failure. This demonstrates a useful clearance change, not successful completion of the original grip objective.

The next separately scoped intervention should address the body thenar/web deformation and anatomically useful thumb-pad orientation together, with consistent glove fitting. The current evidence does not establish whether localized weights, a rest-surface change, or a pose corrective is sufficient. Inspect the exact early body crossing under modest base motion before choosing that method; do not continue with another unconstrained curl/contact search or hide the body defect beneath the glove. No fourth route was constructed by this audit.

## Coordinates, preservation and limitations

The metric frame was recomputed from the evaluated moving wrist on every sample. The actual fixture was checked against that frame: maximum endpoint drift **0.000489 mm**, center drift **0.000483 mm**, axis drift **0.00001532°**. World scale remained uniformly **1.1438040733**; maximum pose-scale error and non-thumb OPEN basis error were both zero. This is attachment/coordinate evidence, not grip acceptance.

The triangle query uses the actual evaluated hand triangles and an ideal capped cylinder. Its 96-sided displayed mesh differs radially by up to approximately 0.0075 mm. Deterministic evaluated topology and group identities are recorded. Shared-vertex adjacency is excluded from same-surface crossing tests, but never used to exempt pairs across different objects. Dominant deform-group labels approximate anatomical ownership.

Integer and adaptive subframe sampling is not continuous collision certification. The intersurface fit query was integer-frame only. Tiny-area observations concern evaluated hand triangles; they do not establish raw-cage manifold/deformation suitability. Root owns the matched image review; this independent report establishes numerical/geometric observations and does not self-issue human approval. No real sword, guard/pommel proof, full hand closure, canonical skeleton change, runtime/export proof, recipe replay or training promotion is claimed.

Evidence: `SUMMARY.json`, `route_C_results.json`, `glove_body_fit_results.json`, `audit_route_C.py`, `audit_glove_body_fit.py`, and `refine_all_surfaces.py`. A/B comparison sources remain under `reviews/route_A/` and `reviews/route_B/`. The audit binds to the immutable input hash above; a later final `.blend` needs root's explicit geometry/action/matrix equivalence binding before inheriting these observations.

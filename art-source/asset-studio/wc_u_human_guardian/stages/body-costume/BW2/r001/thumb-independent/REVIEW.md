# Independent thumb fit — contact improved, ART_REVISE

The retained candidate brings all nine existing thumb-pad samples onto the usable side of the fixed cylinder while preserving opposite-side contact relative to the middle finger. **A pronounced thumb-base/web fold remains visible.** This is a stronger contact construction, not a finished or approved hand. No third pose-search attempt was made after the two bounded attempts.

Source: `grip_correction1_input.blend`, SHA256 `71abf0c027695c17ff68544f305b49afc3c351b8f1bd7adfc2f641f1c2bc4b36`. The input was opened only in background Blender 5.1.1 with factory startup and automatic script execution disabled. No `.blend` was saved and no live MCP operation was performed.

## Fixed scope

The source's handle remained fixed at 14 mm radius, 109 mm endpoint span and 105 mm usable length, with 2 mm exclusion at each cap. All original nine thumb pad indices were retained at the same 9130-vertex evaluated level. Bone lengths, glove geometry, weights, all non-thumb pose bases and the source contract were preserved. The fixed-handle world matrix was checked after fitting.

Only six existing controls were varied: thumb-base XYZ, middle-thumb X and distal-thumb X/Z. The inherited authoring bounds were base X [−15,80], Y [−85,85], Z [−70,40]; middle X [0,85]; distal X [0,80], Z [−20,20], in degrees. These are limited authoring guardrails, not measured biomechanical ranges. No bone scales or additional axes were introduced.

## Initial diagnosis

The initial source already had almost opposite mean contact directions: thumb/middle radial dot −0.996564. Every thumb pad was within the usable axial span, at 29.67–43.86 mm from the cylinder center, versus a 52.5 mm limit. The defect was primarily uneven pad orientation and contact breadth, not missing opposition or current cap exclusion.

The initial selected-pad gaps were −0.388540 to +7.190529 mm, with only 3/9 in the declared −0.5 to +1.0 mm band. Importantly, a triangle-interior check found three triangles deeper than 0.5 mm: maximum depth 0.543831–0.543884 mm. The initial vertex screen alone missed that surface penetration.

## Retained controls

Use XYZ Euler mode, degrees below; all unspecified components are zero.

| Bone | X | Y | Z |
|---|---:|---:|---:|
| `finger1-1.R` | 16.2978596481 | −34.2462146524 | 12.5913969633 |
| `finger1-2.R` | 44.0221539544 | 0 | 0 |
| `finger1-3.R` | 32.0725571646 | 0 | −20.0 |

The distal Z control reaches the existing −20° bound. It was not expanded. The resulting thumb-base and distal-joint shape need visible anatomical review.

| Observation | Retained candidate |
|---|---:|
| Original selected-pad samples in −0.5 to +1.0 mm band | 9 / 9 |
| Minimum / maximum selected gap | −0.375777 / +0.878450 mm |
| Median / p95 gap | +0.287081 / +0.828789 mm |
| Absolute axial coordinate range | 9.479–23.964 mm |
| Usable halfspan | 52.5 mm |
| Thumb/middle mean radial direction dot | −0.829928 |
| Whole-right-hand minimum evaluated vertex SDF | −0.375777 mm |
| Evaluated right-hand triangles screened | 9088 |
| Triangles deeper than 0.5 mm | 0 |
| Maximum triangle-interior penetration depth | 0.433975–0.434029 mm |

The maximum triangle depth is now in another contact region rather than the initially failing thumb triangle. Exact per-pad gaps/axial coordinates are in `bounded_thumb_fit.json`. `triangle_interior_audit.json` records clipping of evaluated triangles to inward-offset cylinder slabs and radial polygon tests, with bisection bounding penetration over edges and interiors. The rendering's 96-sided proxy differs from the ideal circular metric by at most 0.0075 mm radially. The printed narrow interval is the algorithm's bound; it does not imply submicron authoring accuracy.

Two bounded search attempts used 1123 evaluated observations in total. The alternative start reached 8/9 contact, gaps −0.327117 to +1.278708 mm, with distal Z at +20°. It retained a visible web fold and had weaker contact, so the first candidate was retained. The second candidate's full triangle-depth test was not separately executed and is not represented as passed.

## Actual image review and remaining defects

Matched initial and retained palm, side, oblique and axial renders were produced. The initial axial view, all four retained views and all three alternative-candidate views were inspected. The opposite contact is visible in the axial arrangement and broader pad seating is consistent with the numeric observations.

The retained candidate also exposes a long sharp fold/pinch from the thumb base into the palm/web area, especially in the axial and palm views. The glove has Armature and Subdivision modifiers, not a Solidify modifier, so this is not the prior coat/leggings thickness-offset failure. Its deformation/fit must be addressed separately; actual self-intersection and the exact weight/topology cause have not been proved by these cylinder tests. No glove self-collision pass is claimed.

Both retained candidates meet contact better by rolling the pad, but neither resolves that visible web deformation. The inherited ±20° distal side-control bounds are reached and should not be treated as anatomically validated. Other fingers shown are the immutable input poses; the root task is modifying them independently, so the combined final hand needs a fresh all-pad and triangle review.

Recommendation: retain the first candidate's explicit thumb controls as **contact-improved ART_REVISE**. Review or correct the copied glove's thumb-base/web deformation before calling the grip convincing. Do not make another unrestricted thumb-angle search, move the cylinder, redefine pads or relax the contact tolerances to claim completion. No human approval, full-grip acceptance, recipe promotion, animation or Unreal evidence is issued here.

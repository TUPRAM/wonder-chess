# BW2 package and contact mathematics review

Verified 2026-09-09. Scope: read supplied source, verify the extracted package manifest, and execute only its 30 numerical tests. No Blender/MCP, downloads, game tests, source changes, CLI example rerun, or actual Ada contact measurements were performed in this review.

## Executed result

- All **31/31** manifest entries match declared byte counts and SHA-256 hashes. No unlisted package files exist apart from the manifest itself.
- Manifest SHA-256: `8d6a41370ffd30aea27ec4cf1084f71c7464a745122bf6ed85de6c5423b22710`.
- `tools/contact_math.py` SHA-256: `df6467f1f4beb341f8e2e1c515c9287af98685866eaa38fb789b76101c0f017d`.
- Read both the helper and supplied test module before execution. They use the standard library, perform no network/editor calls, and the test module only exercises synthetic numeric functions. The helper CLI can create a result directory/file but was not invoked here.
- Ran `python -B -m unittest discover -s tests -v` from `production/asset-studio/supplements/BW2`, using Python 3.11.8. **30 tests passed**, exit 0, reported test time 0.004 seconds.
- All manifest-listed files remain unchanged after testing. `-B` disabled bytecode writes.
- Full local observations: `bw2_package_math_verification.json`; complete test output: `bw2_numerical_tests.txt`. Earlier package preparation reports remain source-reported evidence, not additional checks executed here.

The math implementation supports its stated narrow purpose: a landmark-derived proper rigid hand frame and sampled distance screens against an ideal closed circular cylinder. These results do not establish that Ada's actual landmarks, units, grip, weights, surfaces, motion, or visual quality are correct.

## Exact input contract

### Landmark API

`hand_frame(*, wrist, middle_mcp, index_mcp, little_mcp, middle_tip, palmar_point)`

All six arguments are required, each a length-three finite numeric sequence in **world-space metres**, measured in the same verified neutral **open** hand pose. Boolean coordinate components are rejected.

| Argument | Required meaning |
| --- | --- |
| `wrist` | Wrist landmark and resulting frame origin |
| `middle_mcp` | Middle finger-base joint; wrist-to-joint direction becomes +Y distal |
| `index_mcp` | Index finger-base joint |
| `little_mcp` | Little finger-base joint; index-minus-little establishes transverse direction before orthogonalization |
| `middle_tip` | Open middle fingertip, used to reject a backwards/distorted distal interpretation |
| `palmar_point` | Identified palm-side **surface** point offset from the joint plane, used to select palmar +Z |

The helper requires dot(+Y, normalized middle-base-to-tip) >= 0.25; transverse magnitude relative to index-to-little span >= 0.2; and absolute palmar directional projection >= 0.1. These are disambiguation screens, not checks of anatomically correct labels or pose. Ambiguous/degenerate directions reject rather than guess.

Output is `HandFrame(origin_m, x_transverse, y_distal, z_palmar, x_points_toward_index)`. Its 4x4 `matrix_rows()` representation has axes in **columns**, translation in column 3, and column-vector multiplication. X and Z flip together when required; +Y remains distal and determinant remains +1. Left/right anatomical X sign may differ. `to_world` and `to_local` operate on metre-space points.

`relative_transform(parent_world, child_world)` returns `inverse(parent_world) @ child_world`. `apply_point`, `inverse_rigid`, `multiply`, and `validate_rigid` expect finite 4x4 proper rigid transforms; their rotation columns must be orthonormal and determinant +1 within default tolerance 1e-7. Scale, reflection, and shear reject. These functions do not implement Blender parent-inverse, constraints, bone inheritance, or nonuniform scale handling.

### Contact API

`cylinder_sample(point, start, end, radius_m)` takes one world-metre point and two distinct world-metre cylinder-axis endpoints, plus a finite positive radius in metres. It returns:

- `signed_distance_m`: exact signed distance to the **closed finite** ideal circular cylinder, negative inside;
- `side_gap_m`: radial distance minus radius, regardless of axial position;
- `axial_m`, `length_m`, and `within_axial_span`.

`screen_patch(points, start, end, radius_m, gap_m=0.001, penetration_m=0.0005, min_fraction=0.5, end_margin_m=0.002)` expects a nonempty iterable of predeclared localized **evaluated glove surface** samples, all in the same world-metre frame as the cylinder.

Its exact default pass logic is:

1. Every sample lies between 2 mm and length-minus-2 mm along the cylinder axis.
2. No sampled radial gap is less than -0.5 mm.
3. At least 50% of samples lie within the inclusive radial gap interval [-0.5, +1.0] mm.

It reports min/median/p95/max radial gaps, contact fraction, maximum sampled penetration, and axial validity. P95 uses linear interpolation between sorted samples. `PASS_SAMPLED_NUMERIC_SCREEN` always retains `visual_approval: false`.

### CLI JSON schema actually consumed

The following is a **type description**, not measured Ada input:

```text
{
  "coordinate_space": "WORLD_METERS",              // required exact string
  "pose_kind": "OPEN_CALIBRATION",                 // required exact string
  "example_only": false,                          // optional; defaults true
  "landmarks": {                                  // exactly the six API names
    "wrist": [number, number, number],
    "middle_mcp": [number, number, number],
    "index_mcp": [number, number, number],
    "little_mcp": [number, number, number],
    "middle_tip": [number, number, number],
    "palmar_point": [number, number, number]
  },
  "cylinder": {                                   // optional
    "start_m": [number, number, number],
    "end_m": [number, number, number],
    "radius_m": positive_number
  },
  "contact_patches": {                            // optional, arbitrary names
    "declared_pad_name": [[number, number, number], ...]
  }
}
```

Invocation is `python -B tools/contact_math.py INPUT.json --output NEW_OUTPUT.json`. Output creation uses exclusive mode and refuses an existing file. No such CLI invocation was run during this review.

Important mismatches with the incomplete hand template: `handle_dimensions_m` is provenance, not the CLI's `cylinder` field. `source_blend_sha256`, rig/scene names, frame, units, landmark provenance, probe results, and other extra top-level fields are not verified or copied into its output. Extra entries inside `landmarks` cause unexpected-keyword failure. A missing `cylinder` silently skips contact screens even if `contact_patches` exists; a supplied cylinder without patches yields an empty screen dictionary. There is no required-digit list. The CLI exposes **no tolerance overrides**; use the function API and separately record any declared tolerance decision.

## Adapter requirements and remaining limitations

1. **Use actual evaluated coordinates and explicit source binding.** The helper trusts declarations. Record source file/hash, scene, rig/mesh names, evaluation frame, modifier state, measured metre conversion, and the exact landmark/sample correspondence. Convert evaluated pose-bone endpoints with the evaluated rig's `matrix_world` once; do not multiply endpoints by the pose matrix again. Evaluated mesh points use their own evaluated object transform. This review did not extract any points or verify these conversions in Blender.
2. **Keep calibration separate from grip evaluation.** Build the frame once from open landmarks and store it relative to the evaluated hand bone. Propagate that stored transform during motion. Closed grip patches come from their own evaluated frames. The CLI labels the whole input `OPEN_CALIBRATION` and does not enforce common or separate timestamps, so retain explicit calibration/contact provenance or call the functions through a source-bound adapter. Do not remeasure a distal frame from curled tips.
3. **Validate sampling, not only the pass string.** The function does not require a minimum sample count, distinct points, area weighting, minimum covered pad area, all required digits, or a palm patch. Duplicate/one-point samples can pass. It does not check that thumb and fingers occupy opposing sides or form an enclosure. Predeclare all pad patches and preserve their mapping across evaluated frames.
4. **A half-contact pass can hide large gaps.** The remaining fraction can have arbitrarily large positive gaps; p95/max are reported but are not pass thresholds. Review the full per-patch distribution and visible pad extent. Every supplied sample still must satisfy the axial range and penetration limit. Document tolerances rather than loosen them to relabel a failed fit.
5. **Samples are not collision coverage.** Triangle interiors, edges, unselected glove regions, finger-to-finger intersections, handle/guard/pommel collisions, and continuous motion are outside the function. It does not measure force closure, pressure, friction, or believable glove compression. Those require separate geometry and visual evidence.
6. **Cylinder geometry must match the fixture.** The radial test is valid for a straight circular handle with the measured radius. Nonuniform scale, elliptical/irregular grips, taper, and actual sword details require the real evaluated handle geometry. Even for a circular fixture, side-gap alone does not reject cap contact; retain the axial check. At default 2 mm margins, a 105 mm endpoint span has 101 mm usable axial span. If the chosen 105 mm value means usable length, record endpoints/margins consistently rather than silently treating the two meanings as equal.
7. **Motion and runtime remain separate.** The helper does not solve finger rotations, verify flexion axes, maintain phalange lengths, calculate prop drift, inspect closed-phase frames, or test Blender/game skeleton compatibility. Validate the fixed hand-relative handle transform and each closed/held frame through the owned Blender proof. Existing 169-frame BW1 action is protected by the task; no action was touched here.

The provided tests cover synthetic frame orientation/handedness/covariance, rigid inversion and relative transforms, basic invalid transforms/landmarks, finite-cylinder distances, and selected patch failures. They do not cover a Blender adapter or actual Ada inputs, and the 30-test suite does not execute the CLI overwrite behavior. No stronger acceptance is inferred.

**Recommendation:** use the unmodified helper as a numerical reference behind a small, source-bound Blender adapter. First verify the open-hand axis markers and real surface correspondence, then measure the fixed-cylinder grasp and inspect the whole moving assembly. No new toolkit, external source, or replacement modeling system is needed for this math review.

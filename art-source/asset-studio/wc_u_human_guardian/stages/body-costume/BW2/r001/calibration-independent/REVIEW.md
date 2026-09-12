# BW2 independent anatomical-right hand calibration

Status: **executed coordinate and small-angle calibration; no grip constructed or approved**. Frozen BW1 r003 was opened in background Blender 5.1.1 with factory startup and automatic script execution disabled. All scripts, logs, numeric observations and diagnostic renders stay in this folder. No `.blend` was saved and no live MCP call was made.

Source SHA256 before/after: `03829ab406d6bd5e6a1c5f86e045e9f2edc720b05e620e70017667c59be8b3f8`.

The calibration starts at saved frame 1, temporarily detaches the existing action and sets only the right finger basis matrices to identity. The wrist/arm chain remains at frame 1. Bone endpoints use evaluated pose data transformed exactly once by the evaluated rig world matrix; glove points use the evaluated glove world matrix. The stored original transforms/action are restored after the numeric probes; rendering takes place only in an unsaved process.

## Confirmed landmarks and palm side

Scene units are METRIC, scale_length 1.0, metres. Blender units are metres here; there is no Unreal centimetre conversion.

| Landmark | World X, Y, Z in metres |
|---|---|
| Wrist — `wrist.R` head | 0.486376435, 0.112332664, 1.112247467 |
| Middle MCP — `finger3-1.R` head | 0.532154262, 0.189413235, 1.054875612 |
| Index MCP — `finger2-1.R` head | 0.515469253, 0.208899572, 1.065429330 |
| Little MCP — `finger5-1.R` head | 0.541745067, 0.150959089, 1.039523125 |
| Middle bone tip — `finger3-3.R` tail | 0.542452335, 0.241414711, 0.979093909 |
| Actual glove palm surface ray hit | 0.492402732, 0.149853900, 1.068737507 |

The palm marker is on `BW1_Glove_Pair_SourceFit` evaluated face 1992, found by a ray through the wrist/middle-MCP midpoint. It is **22.4753 mm off the joint plane** on positive Z. The opposite surface is 14.7431 mm on negative Z. These are evaluated face identifiers, not original body indices.

The sign was verified by actual body-only images: `body_positive_Z.png` shows finger-pad creases and the thenar/palmar region; `body_negative_Z.png` clearly shows the fingernails and dorsal tendons. The glove-only paired renders agree. Thus positive Z is palmward and no X/Z flip is required. The BW1 old handle-frame inference was not used to choose this sign.

Semantic world axes:

| Axis | Direction |
|---|---|
| X — toward the index side | −0.502100229, 0.688099265, 0.523846030 |
| Y — wrist toward middle MCP | 0.430098504, 0.724198580, −0.539028406 |
| Z — palmward | −0.750273705, −0.045340884, −0.659570813 |

The frame determinant is +1; axes are orthonormal within float precision. Middle-MCP-to-tip direction dot +Y is 0.8967836. The largest tested world→local→world point round-trip error is 1.333e−7 m.

## Transform precaution

The rig and glove both contain a **uniform positive world scale of 1.143804065**, an approximately 180° Z rotation and Y translation −0.07 m. Their 3×3 determinant is 1.496424794, not 1. This is not a negative mirror, and no Ctrl+A or source transform change was performed.

`finger_axis_calibration.json` stores the unit semantic world frame and its **full affine** transform relative to the evaluated wrist bone. That relative matrix contains inverse scale, as it must to cancel the existing wrist world scale on multiplication. Do not normalize the relative matrix and then blindly multiply it by a still-scaled wrist world matrix. Either preserve the full affine multiplication, or derive and consistently use a unit rigid wrist frame after explicitly separating the verified uniform scale. Keep handle radius/length in metric world units.

## Reversible local joint probes

Each of 15 actual right finger bones was tested independently about local X, Y and Z, at +5° and −5°: **90 probes total**. No broad curl optimization occurred. Each probe started from the same open basis, and restored the exact open basis before the next probe. The maximum evaluated glove vertex restoration error over all probes was **0.0 m**. No constraints were present on these finger pose bones.

Controls were assigned as `pb.matrix_basis = open_basis @ Matrix.Rotation(radians(angle), 4, local_axis)`. This is a local joint rotation, not a common world-axis push. Full rest/pose/world matrices, zero bases and normalized world direction of each local joint axis are retained in the JSON files.

For index, middle, ring and little fingers, **local +X** is the strongest tested palmward curl direction at every joint. The table reports displacement of a fixed distal glove pad patch for a +5° test at the named joint, with other joints open:

| Digit / actual prefix | Joint 1 palmward mm | Joint 2 palmward mm | Joint 3 palmward mm |
|---|---:|---:|---:|
| Index — `finger2-*.R` | 5.304 | 3.104 | 1.371 |
| Middle — `finger3-*.R` | 6.304 | 3.473 | 1.259 |
| Ring — `finger4-*.R` | 5.796 | 3.255 | 1.262 |
| Little — `finger5-*.R` | 3.986 | 2.217 | 1.037 |

`middle_base_plusX5.png` and `middle_base_minusX5.png` were rendered and inspected in the same side camera. They show the small palmward bend versus extension, consistent with the numeric displacement.

The thumb is different. Its three bones are `finger1-1.R` (parent wrist), `finger1-2.R`, and `finger1-3.R`:

| Thumb test | Observed distal glove-pad response |
|---|---|
| Base +X 5° | Moves across toward middle-MCP region: −7.295 mm hand-X, +3.431 mm hand-Y, +1.927 mm palm-Z; reduces distance to middle MCP by 4.226 mm |
| Base −Z 5° | Primarily lifts palmward: +5.527 mm palm-Z, but retreats −5.957 mm hand-Y and increases distance to middle MCP by 3.940 mm |
| Middle +X 5° | +1.323 mm palm-Z; reduces distance to middle MCP by 3.053 mm |
| Distal +X 5° | +0.484 mm palm-Z; reduces distance to middle MCP by 1.402 mm |
| Middle / distal −Z 5° | Stronger pure palm-normal lifts, +4.037 / +1.456 mm, while retreating from the finger-base region |
| Local Y | Primarily axial orientation/twist; distal bone tip stays fixed for its local-Y probe while the glove pad moves around it |

`thumb_base_plusX5.png` and `thumb_base_minusZ5.png` were rendered and inspected with the same palm camera. Base +X moves the thumb across; −Z alone mainly shifts/lifts it. **Largest palm-normal displacement is not the same as successful thumb opposition.** A future grip will need anatomical thumb-base positioning, flexion and pad orientation together. These small probes do not prescribe a universal thumb pose.

Only the ±5° neighborhood was tested. No broader safe working range, combined-angle behavior, contact, collision clearance, or grip quality is claimed.

## Surface correspondence and limitations

Before probing, small localized patches were selected by palm-side rays into the actual evaluated glove near each distal phalanx. The fixed evaluated vertex IDs are recorded per digit. Each patch has three samples with a 3.42–6.91 mm maximum radius from its ray hit. Evaluated topology stayed constant at 2294 vertices throughout the probes. This is adequate to measure motion direction; these sparse diagnostic patches are **not** accepted BW2 handle-contact patches and do not prove pad compression or triangle clearance.

Recommended next action: the live task can use the independently confirmed frame and local +X finger direction for its visual calibration. Choose and lock the dimensioned handle only after that visual inspection, then fit one digit and the thumb with the actual glove surface. The right-hand calibration says nothing about the left hand; do not mirror its signs or transforms without an independent check.

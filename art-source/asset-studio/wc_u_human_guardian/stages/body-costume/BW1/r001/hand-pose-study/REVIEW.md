# BW1 independent hand-pose study

Status: **ART_REVISE — stopped after initial construction and two unsuccessful bounded corrections.** No human approval, grip acceptance, or reusable pose recipe is issued.

The child Blender process used the immutable `../bw1_hand_pose_input.blend` with `--factory-startup --disable-autoexec --background`. All scripts, renders, JSON and child `.blend` outputs stayed inside this directory. No MCP/live editor calls, body/glove vertex edits, topology changes, weight edits, or canonical skeleton changes were made.

## Useful result

`open_R.png` and `relaxed_R.png` show the actual coherent glove in an open pose and mild relaxation. The relaxed pose rotates the four non-thumb digits by approximately 6.9, 14.3 and 8.6 degrees around their local X axes, and the thumb segments by approximately 2.9, 6.9 and 4.6 degrees. These are useful diagnostics, not an approved grip.

`poses.json` records exact XYZ Euler radians per named finger bone. The empty `open` pose means reset the hand/finger basis to identity relative to the saved rest pose. Do not reset unrelated arm bones when importing a hand pose into an arm articulation test.

## Rejected grip outcome

The right sword and left shield trials retain the requested 32 mm x 130 mm and 30 mm x 120 mm cylinder dimensions. One setup correction moved each center by 13 mm along the inferred finger-forward direction and 11 mm along the inferred palmar direction; axis and dimensions did not change. Each final handle remained fixed while that grip was fitted and rendered. Original and corrected centers, axes, world matrices and wrist-relative matrices remain in the record for diagnosis.

The actual final palmar and dorsal images show four fingers curled below/behind the handle rather than around it. The thumb intersects the cylinder while other digits lack contact. Severe knuckle/web cavities appear under the large angles. The dorsal view can appear more plausible than the palmar view; it must not be used alone to claim a working grip.

Actual Blender control-vertex screening (not a complete surface-intersection test) found:

| Digit | Sword: minimum radial clearance | Shield: minimum radial clearance |
|---|---:|---:|
| Thumb | -5.405 mm | -5.478 mm |
| Index | +6.081 mm | +6.865 mm |
| Middle | +8.296 mm | +9.124 mm |
| Ring | +4.659 mm | +5.480 mm |
| Little | +12.752 mm | +13.717 mm |

Each thumb had five sampled vertices more than 1 mm inside the cylinder. None of the sampled non-thumb digit vertices was within 2 mm of the cylindrical side. These values corroborate the image failure; they are not a proof about every subdivided triangle or all contacts.

## Exact method failure and next intervention

Final inspection exposed a coordinate-frame error in the construction code. It transformed `Bone.y_axis` and `Bone.z_axis` as though they were the armature-space rest axes. In this file, `Bone.y_axis` does not agree with the armature-space `tail_local - head_local`. For the right index proximal bone, the transformed property was `(0.121, -0.957, 0.262)` while the actual world endpoint direction was `(0.132, 0.776, -0.617)`. The latter agrees with column 1 of `Bone.matrix_local`. The resulting inferred finger-forward vector points toward the wrist, so the handle placement and fitting objective were built in an invalid anatomical frame.

This is an error in this study's frame construction, not evidence that the source hand or bundled rig cannot make a grip. The final `forward_world`, `palmar_world`, center and wrist-relative handle fit must therefore be treated as **rejected diagnostic data, not a reusable equipment attachment**. `frame_diagnosis.json` contains the exact observed comparisons.

The next intervention should construct hand axes from explicit world-space MCP/tip endpoints and `matrix_local` columns, verify the sign against the visible palmar surface and a small actual finger curl, and only then establish a fixed cylinder and solve contacts. Use actual posed glove surfaces in the acceptance check. No third correction was made in this bounded assignment.

At the owning agent's subsequent request, `corrected_handle_frame_UNTESTED.json` computes that corrected frame read-only from the immutable source. Its forward vector agrees with the actual MCP-to-tip direction (dot 0.9981), and its palmar vector agrees with the positive local-X curl direction from matrix-local axes (dot 0.9785). It includes proposed centers, world matrices and wrist-relative matrices for equipment blockout. No cylinder was moved or constructed from this corrected record, and no grip was refitted. The proposed placement remains untested; it must not be confused with an accepted attachment or pose.

## Evidence

- `open_R.png`, `relaxed_R.png`: inspected useful mild-motion diagnostics.
- `sword_grip_initial.png`, `shield_grip_initial.png`, `sword_grip_initial_dorsal.png`: inspected initial grip failure.
- `sword_grip_correction1.png`, `shield_grip_correction1.png`: inspected first correction failure.
- `sword_grip_final.png`, `shield_grip_final.png`, `sword_grip_final_dorsal.png`: inspected second/final correction failure.
- `poses.json`: exact rejected grip and useful diagnostic pose records, dimensions and frame caveat.
- `contact_observations.json`: actual evaluated control-vertex screening.
- `frame_diagnosis.json`: actual bone-property vs matrix-local/endpoints comparison.
- `corrected_handle_frame_UNTESTED.json`: subsequently requested read-only corrected geometric frame; no executed grip or attachment fit.
- `hand_pose_study_ART_REVISE.blend`: editable child scene retaining rejected final poses and fixed cylinders for inspection.

The original overexposed review captures were regenerated with lower child-scene lights before visual judgment. That lighting correction did not change poses or geometry. The child files were reopened through separate Blender processes during rendering and audit.

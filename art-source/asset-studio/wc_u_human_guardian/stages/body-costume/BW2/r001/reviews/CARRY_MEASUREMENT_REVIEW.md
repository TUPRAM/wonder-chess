# BW2 fixed-handle carry measurement — ART_REVISE

The fixed fixture is stable through the measured authoring motion, and the five declared distal-pad patches satisfy the supplied sampled-cylinder screen. **This is not G02 success.** The independently reported thumb/web self-intersections remain a blocking defect; no real sword adaptation or art approval follows from these contact numbers.

## Actual executed measurements

Opened immutable `grip_carry_diagnostic_input.blend` in fresh background Blender 5.1.1 with automatic script execution disabled. Source SHA-256: `4103457fe00a2b1ebe5477d3d8e633e0985f4b0fef8ea16cc820b51c04e4f224`.

Evaluated all **145 frames** at 24 FPS. Frames **25–145** are the **121 held frames** subject to contact requirements; frames 1–24 remain explicitly labeled open-to-close. Executed the unmodified BW2 `contact_math.py` functions on actual evaluated world-metre glove points and endpoints/radius derived from the actual evaluated handle.

The original five stored pad-index sets remain unchanged. Their evaluated vertex topology was checked at every frame. The full **4,565-vertex right-glove connected component**, identified from those pad indices, was also screened against the finite cylinder. This includes the glove/cuff component; it does not claim measurement of underlying body skin.

| Pad | Held screens passed | Minimum gap mm | Highest median mm | Highest p95 mm | Maximum gap mm | Minimum fraction in −0.5/+1 mm band |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Thumb | 121/121 | −0.376085 | 0.287580 | 0.829220 | 0.878830 | 100.00% |
| Index | 121/121 | −0.349778 | −0.095327 | 1.250900 | 1.612773 | 85.71% |
| Middle | 121/121 | −0.341758 | 0.118531 | 1.081182 | 1.280714 | 88.89% |
| Ring | 121/121 | −0.492322 | 0.391988 | 1.319329 | 1.489842 | 77.78% |
| Little | 121/121 | −0.251163 | 0.043851 | 1.301728 | 1.330444 | 83.33% |

Every declared pad sample remains within the usable axial span in every held frame. The measured handle has approximately 28 mm diameter, 109 mm endpoint span, and 2 mm exclusion margins, giving 105 mm usable length.

The worst sampled penetration over the full right-glove vertex component is **0.492322 mm**. This is close to the provisional 0.5 mm threshold and does not establish a safety margin over triangle interiors or unsampled continuous time. Four pads contain some samples beyond +1 mm; the helper permits them because it requires only half the patch to be in-band. The full distribution is retained rather than converting the pass into a claim of perfect surface contact.

## Fixed-transform stability

Relative to the evaluated wrist at held frame 25:

| Object | Maximum translation drift | Maximum orientation drift |
| --- | ---: | ---: |
| Holder | 0.000265423 mm | 0.000005964 degrees |
| Handle | 0.000304987 mm | 0.000006391 degrees |

These changes are at floating-point noise scale. The audit retains full affine wrist-relative matrices and verified wrist uniform scale; it does not send scaled bone transforms into the helper's rigid-only API. Polar rotation isolates orientation for the drift report without changing any geometry or pose. Every held frame has its own transforms and measurements in `carry_contact_measurements.json`.

## Separate geometric failure

`../integrated-independent/integrated_geometry_audit.json` reports **375 confirmed nonadjacent transverse glove-triangle crossing pairs** in the retained linear-skinning pose. That is separate work on the integrated input, not a self-collision test executed by this contact script. Its stated boundary excludes shared-vertex pairs and does not classify coplanar overlap or tangential contacts. The visible thumb/web folding remains consistent with the need to stop the current pose search.

The sampled handle-distance result cannot override that self-intersection failure. Full triangle/collision details, the rejected DQ variant, and the corrective recommendation belong to the integrated geometry review and root REVIEW.

The later `static_geometry_to_final_binding.json` directly closes source attribution: static integrated input `9509750f833cec0c8cac90cd866215a732baed67571d1d444c7b718f441f877d` at frame 1 and final frozen `d64d5900317541710d5ef29939d12559e5ecef31777a7e9261158cbccb7a41cf` at held frame 37 have **exactly equal evaluated glove (9,130 vertices) and underlying-body (36,579 vertices) arrays, indexed topology, and world matrices**. Maximum local/world vertex difference is **0.0** for both. Both source hashes remained unchanged. No triangle query was repeated; this comparison binds the already reported static failure to the delivered held pose.

## Final source binding and native movie

Final frozen `ada_bw2_grip_checkpoint_r001_ART_REVISE.blend` SHA-256:
`d64d5900317541710d5ef29939d12559e5ecef31777a7e9261158cbccb7a41cf`.

Working file SHA-256:
`5c639f70facb63f5cc16f5a6ee57917606968e31170a41366c9f4a588d47750c`.

Fresh independent reopens passed all **16 required preservation checks** for each save. All **61 original mesh records**, including retained MP1 sources, match BW1 r003 exactly for audited source coordinates/topology/UVs/weights/keys; original **492 action curves** remain exact. The only original modifier change is the authorized glove viewport subdivision 0→1, matching render level 1. Coat 6 mm and leggings 2 mm inward thickness, both with even-offset disabled, remain preserved.

`final_source_chain_and_equivalence.json` verifies that measurement input and final frozen file retain the same original/new mesh arrays, actions, saved rig pose, handle/holder transforms and hierarchy, modifier changes, and stored hand contract. Work/frozen inspected data match; their native bytes differ. Source-bound evidence is not invalidated by substituting an unverified later pose.

The movie `../motion-carry-final/ada_bw2_fixed_handle_ART_REVISE.mp4` was rendered directly from the **final frozen file**, using Workbench clay, **800×800**, **145 frames at 24 FPS**, and the translation-only `BW2_cam_carry_close` camera at **0.32 m orthographic scale**. Native VSE encoded H264 and then a separate fresh Blender process reopened and actually decoded **all 145 frames** to PNG. Encoded duration is 6.041667 seconds; action sample time span is 6 seconds. Movie SHA-256: `acce52246f19720f0bc6b7f28c54dd94eb3f4016931ff1bab751c2ca29c21eb0`.

Exact settings and every camera matrix are retained in `../motion-carry-final/metadata.json`, with the studio-light name/rotation clarified in `render_settings_verified.json`. `video_verification.json` records the complete decode. Five contact sheets contain all native frames without skipping: **30/30/30/30/25**, with per-frame hashes in `contact_sheet_manifest.json`.

This agent viewed native frames **1, 25, 93, and 121**: the complete hand/fixture fits those frames, and thumb/web distortion remains visible. Root performs the full sheet review; no full visual-review claim is inferred from rendering or decoding.

All **62 incoming protected files** matched their original hashes before/after measurement and again during the final saved-file audits. No `.blend` was saved or edited by these audit/render processes, and no live MCP, gameplay change, Unreal import, or approval operation was performed.

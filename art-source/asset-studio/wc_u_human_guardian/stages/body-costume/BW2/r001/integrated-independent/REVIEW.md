# BW2 integrated right-hand audit — ART_REVISE

The retained fixed pose improves measured contact with the fixture, but it is not a usable grip. The thumb tunnels into the hand/fingers, and the middle/ring web intersects. A glove-only weight blend is not demonstrated to repair this pose. Stop the grip assignment; do not promote the recipe or describe equipment carrying as successful grip evidence.

Input: `BW2/r001/grip_integrated_contact_r001.blend`.

SHA256 before and after all read-only diagnostics: `9509750f833cec0c8cac90cd866215a732baed67571d1d444c7b718f441f877d`.

Executed in Blender 5.1.1 background with factory startup and auto-execution disabled. No source save, live MCP, pose search, weight edit, topology edit, or equipment change occurred. The only deformation variation was an unsaved Armature Preserve Volume diagnostic, restored in memory. Render visibility/cameras were changed only in the background process.

## Fixed-fixture and triangle results

The original radius 14 mm, span 109 mm, usable span 105 mm, original semantic frame, and predeclared level-1 evaluated sample indices were retained. Both glove tests evaluated 9,130 vertices and all 9,088 anatomical-right hand triangles.

| Diagnostic | Linear skinning, retained source | Preserve Volume / DQ, unsaved test |
|---|---:|---:|
| Deepest ideal-cylinder triangle penetration | 0.491920–0.491974 mm | 0.720444–0.720497 mm |
| Triangles penetrating more than 0.5 mm | 0 | 19 |
| Confirmed nonadjacent glove triangle crossings | 375 pairs | 368 pairs |
| Confirmed nonadjacent body triangle crossings | 567 pairs | 569 pairs |

The retained linear geometry is only about 0.008 mm inside the declared 0.5 mm penetration limit. This is a narrow numerical result, not safety margin or artistic acceptance. DQ fails that limit and does not visually restore the web.

The retained worst cylinder triangle is evaluated triangle 11610, vertices `[4381, 1451, 4393]`, at hand-space point approximately `(-0.022821, 0.097367, 0.051231)` metres. The DQ worst triangle is 11612, vertices `[8309, 4393, 1493]`.

| Frozen pad set | Retained samples in −0.5…+1 mm band and usable axial span | Retained gap range | DQ samples in band |
|---|---:|---:|---:|
| Thumb | 9 / 9 | −0.376…+0.878 mm | 9 / 9 |
| Index | 6 / 7 | −0.349…+1.612 mm | 5 / 7 |
| Middle | 8 / 9 | −0.341…+1.281 mm | 8 / 9 |
| Ring | 7 / 9 | −0.492…+1.490 mm | 6 / 9 |
| Little | 10 / 12 | −0.251…+1.330 mm | 10 / 12 |

All retained pad axial coordinates remain within the fixed usable span. Those pad statistics do not detect interpenetration between digits and palm.

## Visible defects and intersection ownership

Actual saved-camera palm, axial, oblique, and added back diagnostic renders were inspected with the handle hidden. Both bare MPFB body and glove show the same long sharp fold from the thumb base into the palm. It persists with cavity shading disabled. The thumb is substantially occluded by/tunneled through neighboring hand surfaces. The back view also shows pinching between middle and ring. DQ preserves those visible failures.

The 375 retained glove crossing pairs, classified approximately by the dominant existing deform groups on each triangle, are:

| Regions | Crossing triangle pairs |
|---|---:|
| Middle / ring | 167 |
| Palm or metacarpal region / thumb | 88 |
| Middle / thumb | 58 |
| Index / thumb | 52 |
| Within thumb | 6 |
| Within index | 2 |
| Within ring | 2 |

These are intersecting triangle-pair counts, not 375 distinct artistic defects. Classification by deform weights is an ownership aid, not an anatomical segmentation guarantee. Intersection coordinates and exact evaluated triangle IDs are retained in `web_weight_diagnosis.json`.

Disabling subdivision without changing the pose also produces 201 confirmed transverse crossing pairs in the glove base cage, involving 201 base vertices. The body's unsmoothed skin cage produces 325 pairs involving 326 source vertices. Thus this is not a subdivision-only or Workbench-only artifact.

## Existing weight construction and exact intervention seeds

The thumb/metacarpal transition already contains blended weights: 143 selected glove base vertices and 94 body source vertices have both `finger1-1.R` and non-finger right-hand support. This broad selection includes the metacarpals; it must not be interpreted as 143 vertices weighted directly to `wrist.R`, or as a proposed edit mask.

Sharp changes exist across neighboring edges. The largest selected glove edge changes total thumb-family weight by 0.526396 across vertices 1924–2190. Another changes by 0.485128 across 1948–1949. The corresponding body also has steep transitions, including a 0.617900 change across source vertices 3645–3646.

| Glove base vertex | `finger1-1.R` | `finger1-2.R` | `metacarpal1.R` | Other group | Actual MHCLO body correspondence |
|---|---:|---:|---:|---|---|
| 1924 | 0.059117 | 0.746224 | 0.194659 | — | 3179, 3637, 3638 |
| 2190 | 0.079589 | 0.199356 | 0.721055 | — | 3820, 3179, 3236 |
| 1948 | 0.638045 | 0.106343 | 0.237597 | `metacarpal2.R` 0.018015 | 3646, 3645, 3203 |
| 1949 | 0.101827 | 0.157434 | 0.712720 | `metacarpal2.R` 0.028020 | 3822, 3204, 3210 |

Glove vertices 1924, 2190, and 1949 also belong to confirmed raw-cage intersections. These are precise inspection seeds, not a sufficient correction boundary. `web_weight_diagnosis.json` records the complete selected and crossing base-index lists, exact weights, posed hand-space coordinates, and body correspondence coefficients.

The glove is a native imported MHCLO asset; it does **not** have the helper garments' single `mpfb_source_index` attribute. Its 2,294 correspondence rows were read from the retained MHCLO, and the source OBJ's indexed face sets were checked against the live glove base topology. Do not equate a glove vertex number with a body vertex number. MHCLO fitting coefficients and skeletal weights are distinct data.

All nine frozen thumb pad samples have existing evaluated support only from `finger1-2.R` and `finger1-3.R`, ranging from 0…0.280831 and 0.719169…1 respectively. Their exact weights are recorded. This does not establish an exact base-vertex subdivision support exclusion mask, nor prove that a new web edit would preserve those evaluated positions.

## Recommendation

Retain the corrected coordinate frame, observed joint signs, fixed fixture, sample contract, and rejected pose as useful evidence. Park grip at **ART_REVISE**.

The next distinct intervention should rebuild the thumb opposition and web deformation together on an isolated body/glove copy, using a collision-free intermediate pose and the actual metacarpal/CMC structure. Establish a nonintersecting thumb-base and web volume before demanding distal-pad contact; then solve middle/ring separation with whole-hand collision checks included. Review the source body as well as the glove. Any skinning correction should have an explicit local base-vertex scope and preserve the original source and pad contract; any changed rig behavior stays local to this authoring proof.

A copied-glove local blend could be investigated in that future intervention, but these results do not support applying it as a sufficient repair while freezing the current pose. It would leave underlying-body defects and independent thumb/finger and middle/ring intersections unresolved. DQ was tested and rejected. No third thumb search, new sword construction, or recipe promotion was performed here.

## Evidence and limits

- `integrated_geometry_audit.json`: fixed-pad and capped-cylinder triangle queries; linear/DQ self-intersections.
- `web_weight_diagnosis.json`: exact raw and evaluated crossing records, ownership classes, base groups and verified MHCLO source mappings.
- `source_and_render_metadata.json`, `dq_render_metadata.json`: source hash, matrices, modifiers, cameras and diagnostic boundary.
- `glove_palm.png`, `glove_oblique.png`, `glove_axial_no_cavity.png`, `glove_linear_back.png`: retained visible failure.
- `body_palm.png`, `body_axial_no_cavity.png`, `body_linear_back.png`: same underlying-body failure.
- `glove_dq_palm.png`, `glove_dq_axial.png`, `glove_dq_back.png`, and corresponding body DQ images: rejected Preserve Volume comparison.

Triangle crossing tests exclude shared-vertex topology neighbors and confirm nonadjacent transverse edge/triangle crossings. Coplanar overlap and tangential contact are not classified. Cylinder queries use an ideal capped cylinder; the 96-sided display fixture differs radially by at most about 0.0075 mm. Numerical interval precision is a computational bound, not physical accuracy. Only this frozen pose was audited here; no animation-wide, Unreal, gameplay, or human-approval result is claimed.

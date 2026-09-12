# BW1 body foundation: immutable snapshot audit

Reviewed 2026-09-09 through isolated, read-only background Blender 5.1.1 processes with automatic scripts disabled. Snapshot: `bw1_body_audit_input.blend`; SHA256 **`5aac61d7b6666c3b898f8dd6da274cba0822fa5ab5ef2d3e61da310f8a9aaf68`**. It was hashed again after measurement and remained unchanged. No live Blender/MCP calls or source saves were performed by this audit.

This is structural/rest-state evidence. It does not issue art, deformation or runtime approval. Root authoring continued independently after this snapshot; successor fixes are distinguished below.

## Foundation and head preservation

- `BW1_IndexedBody` retains **19,158 vertices**, independent mesh `BW1_IndexedBody_Mesh` and independent key datablock `Key.001`. The retained master uses `base` / `Key`.
- Candidate and retained master have byte-exact base vertex coordinates and identical indexed edge/face lists. Vertex correspondence was preserved.
- All **38 original shape keys** retain exact coordinate arrays and unchanged values. Six added native body targets bring the candidate to **44 keys**: shoulder-distance increase 0.12; torso V-shape increase 0.08; right/left upper-arm shoulder muscle increase 0.12 each; right/left hand scale increase 0.03 each.
- `BW1_Context_Head_ART_REVISE` retains all **4,271 local vertex coordinates and face indices exactly** from `MP1_Head_r002`; both diagnostic eyes likewise retain exact local coordinates/topology. Each has independent mesh data.
- Each source scene was explicitly evaluated before comparing world matrices. Context head world coordinates differ from original by at most **0.0000002862 m**; eyes by less than **0.0000000600 m**, consistent with floating-point parenting transforms. The head has not been reshaped by this body study.
- New glove/boot body Delete masks are disabled in viewport and render. The full indexed body remains present; the deliberate display mask exposes only the below-neck body while retaining the contextual head. The neck interface is not thereby accepted or welded.

The snapshot reopened with `BW1_BODY_COSTUME`, `MP1_ADA_HEAD`, `MP1_ARCHIVED_TRIALS` and `MP1_SOURCE_CONTROLS` retained. The temporary local rig contains **163 bones** and is explicitly labeled incompatible with current runtime export until separately reviewed.

## Rest-state measurements

Measurements use the current mixed shape keys **before armature deformation**, transformed through the body's actual world matrix into metres. Joints use actual `bone.head_local`, `bone.tail_local` and `rig.matrix_world @ bone.matrix_local`. No assumption about `Bone.y_axis` was used. Left and right values match to floating-point precision unless stated otherwise.

| Quantity | Actual value | Definition |
|---|---:|---|
| Complete MPFB source skin height | **1.82000024 m** | Feet to full source scalp, skin vertices only; source head is retained but display-masked |
| Assembled contextual head + feet height | **1.79924476 m** | Retained MP1 head cage top to body skin ground; excludes hair, soles, equipment and subdivision |
| A-pose overall skin X extent | **1.12405946 m** | Includes spread arms/hands; not shoulder breadth |
| Shoulder joint-centre span | **0.36369270 m** | Right upperarm01 head to left upperarm01 head |
| Hip joint-centre span | **0.21636708 m** | Right upperleg01 head to left upperleg01 head |
| Upper-arm joint length | **0.26567006 m** | Shoulder to elbow |
| Forearm joint length | **0.24131201 m** | Elbow to wrist |
| Shoulder-to-wrist chain | **0.50698207 m** | Sum of the two joint lengths |
| Palm MCP span | **0.06869242 m** | Index-to-pinky knuckle joint centres; excludes thumb and soft margins |
| Palm skin diagnostic width | **0.06495970 m** | Skin-edge plane 60% from wrist to middle MCP, perpendicular to palm length; thumb-heavy edges excluded |
| Upper-leg joint length | **0.42581898 m** | Hip to knee |
| Lower-leg joint length | **0.43366718 m** | Knee to ankle |
| Hip-to-ankle chain | **0.85948616 m** | Sum of the two joint lengths |
| Foot skin length | **0.24060278 m** | Horizontal projection along ankle-to-second-toe-tip direction |
| Foot skin width | **0.10178572 m** | Horizontal projection perpendicular to that foot direction |

The chosen **1.82 m** is an artistic/source-scale decision recorded in the scene. It does not mean the assembled contextual head is 1.82 m tall. The old scene `body_landmarks_initial` JSON predates native fitting; current measurements above use the actual fitted rig endpoints rather than treating that initial cache as current.

Right-side world joint centres in metres (`+X` anatomical right, `+Y` forward):

| Joint | X | Y | Z |
|---|---:|---:|---:|
| Shoulder | 0.18184635 | −0.04636158 | 1.44498372 |
| Elbow | 0.36106092 | −0.04210385 | 1.24891078 |
| Wrist | 0.48637643 | 0.11233269 | 1.11224747 |
| Hip | 0.10818354 | −0.05011099 | 0.93183768 |
| Knee | 0.15342824 | −0.01559750 | 0.50983822 |
| Ankle | 0.18816832 | −0.03621603 | 0.07805675 |

Torso measurements are repeatable diagnostic plane sections, not dimensions recovered from the painted reference. Actual skin mesh edges were intersected with horizontal planes; arm-weighted endpoints were excluded:

| Section | Chosen world height | Width | Front/back depth |
|---|---:|---:|---:|
| Ribcage diagnostic | 1.2740 m (70% height) | 0.28537119 m | 0.19992688 m |
| Waist diagnostic | 1.1102 m (61% height) | 0.30010184 m | 0.18830722 m |
| Pelvis diagnostic | 0.9828 m (54% height) | 0.36148911 m | 0.24091128 m |

The sampled rib/pelvis width ratio is **0.78943**. It describes these chosen planes, not an approved anatomical standard or Ada likeness score. The full measured matrices, bounds, exact selection definitions and native settings are retained in `body_measurements.json`.

## Correspondence and weights

| Mesh | Snapshot observation |
|---|---|
| `BW1_CoatUpper_Continuous` | 1,131 vertices; `mpfb_source_index` has 1,131 unique valid indices, range 15,556–17,975. Every deformation-group weight exactly matches the named source vertex. No unweighted vertices; maximum raw weight-sum error 0.000000154; at most seven influences. |
| `BW1_Glove_Pair_SourceFit` | 2,294 vertices; no point source-index attribute, provenance instead comes from retained MHCLO correspondence. No unweighted or opposite-hand-weighted vertices. Maximum raw sum error 0.00146631; at most eight influences. |
| `BW1_Boot_Pair_SourceFit` | 2,084 vertices; MHCLO provenance rather than point source-index attribute. No unweighted or opposite-foot-weighted vertices. **Maximum raw sum 1.10102108**, minimum 0.99876289; at most eight influences. |
| `BW1_Leggings` | 965 snapshot vertices; source-index entries are unique/valid and source weights match within 0.000000119. However, the extracted object contains unintended wrist components described below. |

A bounded glove screen tested **652 distal finger vertices** near the middle/tip phalanx interiors. No vertex had more than 0.1 foreign-digit influence under that proximity heuristic. This does not prove all finger weights are correct; palms, webs, thumb contact and every required grip still need posed image review. Small left/right crossing in coat/leggings torso regions was recorded, not automatically classified as an error.

### Concrete extraction defect found

The snapshot leggings contain three disconnected components:

- Correct **945-vertex** lower-body component, zero arm/hand weights.
- **10-vertex right wrist remnant** at X 0.452–0.525 m, Z 1.068–1.112 m, fully weighted to forearm/wrist/hand.
- Corresponding **10-vertex left wrist remnant**.

These source weights match their source indices. The defect is region extraction admitting cuff geometry, not erroneous source-to-garment weight transfer. Correct it on the derived leggings by semantic/component selection. Do not remove or reorder indexed body vertices. Snapshot indices and bounds are in the JSON; do not blindly reuse old indices after successor geometry changes.

### Root-reported successor fix, outside this snapshot

The main author reports operation `operations/16_normalize_and_render_motion.py` normalized only skeletal groups on 125 glove and 347 boot vertices. Its recorded comparison at frame 13 reported evaluated-coordinate change **0 for the glove** and approximately **2.235e−8 local units for the boot**; Blender already normalizes effective deformation. This is a numerical cleanup, not claimed artistic improvement.

Operation file SHA256 when inspected: `24f036cd7a4d2d9e72b58cb8db58c31f328ceac3878c81fa22a2b82010fcc184`. This audit did not load the live successor or independently repeat that operation. Root's final save/reopen audit must establish its final normalized state and confirm the cuff-remnant fix. The immutable JSON intentionally retains the pre-normalization observations.

## Acceptance boundary

Source/key preservation and named-source correspondence are supported by executed evidence. This report does not establish visual costume acceptance, collision-free grips, boot articulation, actual-game motion coverage, final head/neck integration, runtime skeleton compatibility, or a reusable recipe. The detailed arm/leg images and motion review remain separate evidence.

Artifacts: `body_measurements.json`, `body_snapshot_inventory.json`, `measure_body_foundation.py`, `inspect_body_foundation.py`, `body_measurement_run.log`. All writes are local evidence; original MP1 and body snapshot files were not saved or altered.

## Final saved successor verification

The final frozen candidate and working file were subsequently reopened in **two independent fresh background Blender processes**. Their detailed results are in `final_reopen_frozen.json`, `final_reopen_work.json` and the combined `final_reopen_audit.json`.

The original source preservation and contextual head checks still pass. The saved leggings now have **945 vertices in one connected component**, 945 valid unique source indices and **zero arm/hand-weighted vertices**. The two cuff remnants identified above are removed from the derived garment. Final glove/boot maximum weight-sum errors are respectively **0.000006082** and **0.000009977**, within the recorded 0.00001 tolerance; neither is claimed numerically exact one.

Both files retain all four scenes with fake users, 49 visible/renderable mesh objects, finite raw/evaluated mesh coordinates and the local diagnostic action at frames 1–169, 24 FPS. Six discarded study meshes remain hidden in the active scene. These are technical persistence checks; failed grip/knee visual proofs, the unjoined neck, runtime compatibility and recipe reuse remain open at **ART_REVISE**.

Final frozen SHA256: `7e71cdf5b737779d84231866e5559cd2950bbf4a65b13430658d957370bbc443`. Working-file SHA256 at final audit: `3d5f98684e0aa193b1d19f67da1174b065b2d1310b3190f4c8d71e9456163a86`. Neither file was saved by the audit processes.

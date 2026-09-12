# 04 — Technical art contract for the AQ1 candidate

## Four different resolutions

Do not conflate:

| Layer | What must be decided |
|---|---|
| Source geometry | Detail and control needed to author appealing shapes |
| Runtime mesh | Silhouette, deformation, vertex/material cost at the game camera |
| Texture data | Actual painted/baked content and its UV allocation |
| Review image | Camera framing, pixel size, lighting, sampling, and display |

A larger render does not change topology. Subdivision does not invent design. A bigger color atlas does not invent texture detail. A high triangle count can still preserve poor proportions.

## Source and game meshes

Separate the editable source from the export copy. Use controlled subdivisions or multiresolution/sculpt refinement for organic surfaces when appropriate. Use modeled curvature, support topology, and limited bevels for armor and weapons. Bevel widths follow object scale and intended material, not a universal default.

Do not add Catmull-Clark to the entire joined character without inspecting topology. It can round off intended planes and damage details. Smooth shading changes surface-normal interpolation; it does not change the outline. Both operations require intentional surface boundaries.

For the final mesh, allocate topology to visible contours and deforming joints. Separate rigid overlapping armor is acceptable when it is intentional and does not intersect badly; 'one watertight object' is not a universal character requirement. Organic body surfaces and cloth transitions need coherent construction.

Voxel remeshing can fuse parts for sculpting but is not an automatic final animation topology solution. Review/retopologize where deformation requires it. A blanket decimation ratio is not a substitute for checking elbows, fingers, face, shield rim, and weapon edge.

## Budget experiment, not a new universal cap

The inspected Ada data uses a 15,000-triangle LOD0 ceiling and 1K default textures. First attempt the new design within that envelope by reallocating geometry. There is no minimum triangle count and no reward for filling the allowance.

If the approved design visibly benefits from an exception, prepare one **up-to-25,000-triangle LOD0 comparison candidate** with the original as a control. This is an unprofiled experiment, not blanket permission to raise every character's budget. Update the relevant art configuration and validation only after explicit acceptance. Do not silently disable a failing test.

The authoring source may be denser than the shipped mesh. A 2K texture-authoring candidate is reasonable for evaluating face/costume detail, but compare 1K and 2K at actual gameplay and inspection distance before choosing a shipping resolution. Do not upscale existing swatches and call that a material upgrade.

Retain one or two materials where practical. Do not multiply draw calls for every costume fragment. Profile actual render vertices, skinning, material complexity, transparency, texture memory, and busy-fight frame times; triangles alone do not predict cost.

## Semantic surface ownership

Preserve separately named editable parts such as:

`body_base`, `head_surface`, `hair_braid`, `coat_body`, `tabard_front`, `armor_chest`, `armor_pauldron_l`, `armor_pauldron_r`, `bracer_r`, `hand_grip_r`, `shield_shell`, `shield_crest`, `shield_straps`, `sword_blade`, `sword_guard`, `sword_grip`.

These names are proposed candidate conventions, not instructions to blindly rename the live runtime. The export may join approved parts while retaining a mapping in a manifest.

Do not select parts using a required vertex count, arbitrary component index, or color-atlas position. Existing scripts that do so need candidate-specific replacement or a clear unsupported-revision failure. Do not run old mesh surgery on new topology.

## Materials and UVs

Use purposeful UV islands and texel allocation for the parts that need unique information. Shared, mirrored, or palette-based areas remain valid when the intended result supports them; unique unwraps are not a goal by themselves.

For the reference candidate, visibly demonstrate:

- Face/hair color structure consistent with the approved identity.
- Brushed steel separated from cloth, leather, skin, and restrained gold.
- A few broad cloth folds and selectively represented quilting.
- Controlled shield/weapon edge treatment rather than noisy wear everywhere.
- Actual baked normal information where it adds useful surface detail.

Bake from suitable source geometry with an inspected cage or projection settings. Document normal orientation and tangent basis. Base color must not contain a dramatic studio cast shadow that fights in-engine lighting. AO and other baked cues should be restrained.

Base color uses the appropriate color texture interpretation. Normal and packed data maps use non-color treatment in Blender and matching Unreal settings. Keep channel packing explicit. A map named `Normal` is not automatically a correctly interpreted tangent normal.

The current source describes tangent +Y normals. For Unreal, verify orientation with a known asymmetric raised/beveled test and the actual material/import configuration; do not flip a channel twice or assume the label alone guarantees compatibility.

## Rig and animation compatibility

Record rest transforms, bone hierarchy/names, root, sockets, scale, clip names, and current action data before editing. Skin the candidate deliberately. Weight transfer is a starting point, not proof of a good result.

Retain the existing seven animation semantics and gameplay timing unless an explicit presentation change is approved. Do not move attack/shield resolution into animation notifies. Cosmetic polish must not alter simulation outcomes.

Review every clip continuously, then inspect extrema: elbow flexion, shoulder elevation, wrist grip, shield lift, knee bend, torso twist, defeat pose. Verify the face remains visible where required. Finger-by-finger rigging is optional, not a requirement for a convincing fixed weapon grip.

If a new silhouette requires changed rest proportions, make a new rig candidate and retarget/review all affected clips. Do not claim compatibility solely because bone names match. Never globally overwrite a shared skeleton to solve one hero.

## Export and Unreal acceptance

Preserve the existing measured unit/axis calibration until a fresh test justifies changing it. Export candidate assets separately. Bake/triangulate the export copy consistently with the normal-map workflow while retaining editable source topology.

Choose and record the Unreal normal/tangent import method. Unreal distinguishes computing normals from importing normals and importing both normals and tangents; these paths can visibly change the result. Match the chosen path to the exported data and validate an asymmetric normal test.

Do not overwrite a working production asset at first import. Place the candidate in a temporary content location, preserve the existing skeleton where valid, and verify scale, facing, material assignments, bounds, socket positions, animations, and selection/collision behavior.

Capture actual game-camera footage, not only the skeletal-mesh viewer. Show one crowded encounter, allied/enemy readability, and each skill effect. Check that the current simulation still runs independently of animation/presentation visibility.

Build LODs after LOD0 approval. Keep important outlines and deformation support. Compare transitions at actual distances; the previous 50% and 25% ratios may remain starting points but are not acceptance criteria.

Finally make one small source revision, re-export, reimport, and verify stable references and appearance. Promote only when both human art approval and technical checks pass. Keep a rollback package and mark old candidates as superseded, not deleted.

## Technical references

See `SOURCE_INDEX.json` entries T1–T5. These support tool behavior, not the subjective art direction or proposed performance budgets. Inspect installed-version APIs before writing scripts.

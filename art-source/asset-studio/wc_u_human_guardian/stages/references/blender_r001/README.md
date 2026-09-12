# Ada AS1 r001: reference-only Blender scene

Created and executed in Blender 5.1.1 on 2026-09-08 from a new factory-startup source. No existing Ada geometry, rig, materials, textures, animation, or `.blend` was loaded or appended.

Open `ada_reference_scene_r001.blend` for the final reference-only candidate. It contains **nine EMPTY objects**: four packed image references and five coordinate/height markers. There are **zero mesh, armature, camera, or light objects**. All reference images are non-rendering and locked against selection/transform changes. References display on their front sides, so an opposite reference does not overlay the front-facing image. The saved viewport is orthographic and looks from +Y toward the origin; this viewport setting does not certify the generated artwork as orthographic.

The untouched original empty scene is `ada_reference_empty_source_r001.blend`. The AS1 helper's raw imported result is `ada_reference_import_candidate_r001.blend`. The final locked and packed result is saved separately. The execution report confirms that the earlier source files remained unchanged.

## Pixel calibration

Source: `../ada_construction_r002.png`, native **1658 by 949** pixels. Native crops were produced by AS1 `image_review.py`; `native-crops/crops.json` records source and output hashes with `resampled: false`.

| View | Source crop `[left, top, right, bottom]` | Native crop size | Crown source y | Sole source y | Chosen centerline source x |
| --- | --- | --- | --- | --- | --- |
| Front | `[45, 45, 460, 850]` | 415 x 805 | 69 | 833 | 255 |
| Anatomical left | `[545, 45, 755, 850]` | 210 x 805 | 69 | 825 | 650 |
| Back | `[835, 45, 1240, 850]` | 405 x 805 | 68 | 827 | 1035 |
| Anatomical right | `[1300, 45, 1525, 850]` | 225 x 805 | 69 | 826 | 1404 |

Crown and sole rows are measured dark-outline extents in the body-only horizontal bands, using at least three pixels with all RGB channels below 110 per row, then visually inspected against the actual source image. The painted and antialiased silhouettes leave approximately three pixels of landmark uncertainty. The side centerline is a construction interpretation, not an anatomical measurement recovered from the image.

Each complete crop uses a single uniform scale: `meters_per_pixel = 1.82 / (sole_y - crown_y)`. Image planes preserve the native image aspect ratio. No region is stretched, perspective-corrected, or independently resized. Matrices map the selected sole to world Z=0 and crown to Z=1.82 m. The actual saved Blender transforms were checked numerically, with sub-micrometer floating-point tolerances, in `saved_scene_audit_r001.json`.

The display-size formula uses Blender's installed `get_ref_object_space_coord` implementation at `C:/Program Files/Blender Foundation/Blender 5.1/5.1/scripts/startup/bl_operators/image_as_planes.py`, lines 237-258, inspected during this task. That code normalizes each image dimension by the larger pixel dimension, matching `display_size_m = max(width, height) * meters_per_pixel` used here.

## Coordinates and limits

The source is meters, **+Y forward**, **+Z up**, **anatomical right +X**, and **anatomical left -X**. The front image is viewed from +Y, rear from -Y, left side from -X, and right side from +X. This makes the left profile face screen-left and the right profile face screen-right without mirroring the source pixels. Reference planes sit 0.75 m from the central construction axes, with the same chosen ground and crown heights.

These are proposed generated construction references. They do not establish exact projections or human approval. The r002 rear panel lacks the intended center split; its image is used for candidate placement and hem-length reference. The original back reference and written construction decisions control the proposed split. That conflict is explicitly stored on every image object and in scene metadata.

No modeling has started in this scene. Reference approval, modeled forms, topology, materials, rigging, animation, Unreal import, reimport, and release remain separate downstream work.

Execution evidence: `../../../reports/reference_scene_execution_r001.json`. Local observations: `saved_scene_audit_r001.json` and `as1_reference_audit_r001.json`. Commands and logs remain beside this README. Treat the three `.blend` files, native crops, calibration, and executed reports as immutable evidence for this revision.

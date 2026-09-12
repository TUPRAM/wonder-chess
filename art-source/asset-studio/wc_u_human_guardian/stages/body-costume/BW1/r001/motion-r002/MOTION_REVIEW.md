# BW1 technical r002 motion evidence — ART_REVISE

Rendered from frozen `ada_body_costume_checkpoint_r002_ART_REVISE.blend`, SHA256 `9e15e8446afbb6f60725e3d2d72026df07f707271b007e5f31c2919f565f30ef`. The input was not saved or modified by media/audit processes.

All 169 actual PNG frames were retained and inspected through 11 labeled 4×4 contact sheets; frame 67 was additionally inspected at native resolution against the unsaved coat modifier diagnostic. The existing `BW1_DIAGNOSTIC_RANGE_ART_REVISE` action was rendered from the saved `BW1_Camera_three_quarter`, at 24 FPS, 680×880, Workbench single clay 0.55, shadows and cavity. This is a Blender authoring diagnostic sequence. It is not game playback, an exported clip, a walking animation, or human approval. The media was encoded and independently reopened with native Blender VSE; all 169 frames, 24 FPS and dimensions were verified. Continuous native-player playback was not used as the visual review method.

`ada_bw1_articulation_r002_review.mp4`: 369143 bytes, SHA256 `cdfae69ca214145ad138c3e7abeacea5b97f76a0651da57dd8c1d64f1b70563d`. Complete render provenance is in `metadata.json`; PNG hashes and contact-sheet coverage are in `contact_sheet_manifest.json`.

## Result and remaining defects

- The leggings singular spikes formerly visible at frames 129 and 159 are absent. Their first technical correction is present in the frozen r002 source.
- A second narrow Solidify spike remains in the upper coat during arm motion. It is especially clear behind the right shoulder at frame 67 (2.750 s), also visible around frame 70 and 96. r002 remains faulty evidence and is preserved rather than overwritten.
- Both hands remain open beside the equipment handles throughout; a convincing sword or shield grip has not been demonstrated.
- The raised thigh passes through the hanging garment/front panel during the leg ranges, approximately frames 41–58 (1.667–2.375 s) and 113–130 (4.667–5.375 s).
- The kneeling range, approximately 139–163 (5.750–6.750 s), exposes large thigh/garment intersections and unfinished knee/greave transitions. The tabard does not yet respond adequately to the lifted thigh.
- The head is contextual ART_REVISE geometry; the head/neck/collar interface remains unfinished. Armor and costume retain blockout forms. This sequence does not establish finished local arm or leg proofs.

## Second technical diagnosis, unsaved

The read-only audit screened 45 active clothing/equipment meshes across all 169 frames. The r002 source had zero extreme-world-bounds events. Temporal screening flagged coat vertices moving as much as 0.6588035 m between adjacent frames; expected rapid sword-tip and boot movement also exceeded the conservative 0.12 m flag threshold and is separately interpretable in the JSON. Bounds screening does not test cloth collisions or prove an acceptable surface.

`BW1_CoatUpper_Continuous` has Solidify `Padded garment thickness`, thickness 0.006 m, with `use_even_offset=True`. In an unsaved background candidate, changing only `use_even_offset=False` reduced the coat's maximum adjacent-frame vertex displacement to 0.0488512 m, with zero bounds/temporal flags over all 169 frames. Actual matched frame 67 images confirm the long narrow shoulder spike disappears while the pose remains. See `coat_even_offset_false_temporal_audit.json`, `frame067_coat_even_offset_false_UNSAVED.png` and its script/log. No source file was written by this diagnosis.

Recommendation: use a new source checkpoint containing the separately verified coat property correction for final recording, retain r001/r002 failure evidence, and continue to report the grip, cloth and construction defects as ART_REVISE. No recipe or human approval is issued.

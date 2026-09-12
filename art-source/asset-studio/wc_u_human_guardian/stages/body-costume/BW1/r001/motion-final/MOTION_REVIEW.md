# BW1 frozen-checkpoint motion evidence

Status: **ART_REVISE.** Media generation and reopening passed; the displayed asset does not pass articulation or grip acceptance.

Source: `../ada_body_costume_checkpoint_r001_ART_REVISE.blend`, SHA256 `7e71cdf5b737779d84231866e5559cd2950bbf4a65b13430658d957370bbc443`. Hash was checked before rendering and after completion. The source was never saved or modified by this task.

The actual saved action `BW1_DIAGNOSTIC_RANGE_ART_REVISE` on `BW1_Temporary_Pose_Rig` was rendered from `BW1_BODY_COSTUME` through `BW1_Camera_three_quarter`. Frames 1–169, 24 fps, 680×880, duration 7.041667 seconds. This is a Blender authoring diagnostic sequence, not normal-speed gameplay, the game walking clip, imported animation, or engine evidence.

## Media and technical verification

- `ada_bw1_articulation_review.mp4`: actual 169-frame PNG sequence encoded through Blender 5.1.1's native VSE as H.264/MPEG4, no audio.
- `frames/frame_0001.png` through `frames/frame_0169.png`: all actual source frames retained.
- `contact-sheets/`: eleven labeled 4×4 sheets cover every frame. Pixels are uniformly downsampled from 680×880 to 255×330; labels sit outside each image. No image warping, retouching or generated substitutes.
- `metadata.json`: camera matrix, action, source hash, render configuration, time range and execution timestamps.
- `video_verification.json`: a fresh factory-startup Blender process reopened the encoded movie and confirmed 169 frames, 24 fps and 680×880 dimensions.
- `contact_sheet_manifest.json`: exact sheet coverage and SHA256 for every PNG.

Workbench used single clay color (0.55, 0.55, 0.55), shadows and cavity shading. The source's saved camera was preserved. No action, bone, topology, weight or canonical game changes were made. No new software was installed.

MP4 SHA256: `b2ea401642be9b6aaccf84b0eabaaa1b7cfae25cb7a8f759b747fa0632f3fffd`; 369,965 bytes.

## Actual visual review

All 169 frames were inspected through the eleven sheets. Frames 49, 81, 129 and 145 were also inspected at native image size. This is frame-complete visual inspection of the rendered sequence; no claim is made that a game animation bank or in-engine transition set was reviewed.

| Observation | Frames and approximate clip time | Consequence |
|---|---|---|
| Both hands remain open while sword and shield handles move with their attachments. | Throughout; clear at 1, 49 and 81 | The clip cannot establish a functioning equipment grip. |
| Raised thigh visibly emerges through the front cloth panel. | Approximately 41–58, 1.667–2.375 s; recurs 114–130, 4.708–5.375 s | Major garment clearance/deformation failure. |
| Deep bend/kneel exposes the thigh through the unmoving coat/tabard envelope and leaves rigid protection transitions visibly unfinished. | Approximately 139–160, 5.750–6.625 s; frame145 native inspection | Full kneeling costume assembly remains unapproved. |
| Long extruded-looking spike projects from hip level far to screen right. | Frame129, 5.333 s | Major reproducible geometry/modifier defect; independent checks below. |
| Brief thin stray lines appear near the upper body/equipment silhouette. | Frames66 and 159, 2.708 s and 6.583 s | Additional anomalous frames retained; their exact object/cause was not independently localized here. |
| Contextual head/neck join remains visibly unfinished. | Throughout | Preserved contextual head is not evidence of accepted final integration. |

The arm bends and foot/leg pose changes are visibly executed, so this recording is stronger evidence than static setup claims. Those movements also expose the failures above. No overall motion-quality or pose-clearance pass is issued.

## Independent frame129 checks

`frame129_fresh_process_recheck.png` reproduces the spike in a new Workbench process. `frame129_cycles_8sample_recheck.png` reproduces it in Cycles using the same camera at eight samples. Thus it is not merely Workbench temporal render history.

Both evaluated-geometry screens identify one `BW1_Leggings` vertex, evaluated index 4638, at world position `(-1.2326323, 3.9150538, 0.2187704)`, far outside the character. The object's stack is Armature, Subdivision and Solidify; this task did not isolate which operation creates the outlier. The hidden failed `BW1_KneeSurfaceAnchor_R` has `hide_render=true` and is not the identified outlier source.

The raw movie and every original sequence frame remain intact. The diagnostic stills supplement them; they do not silently replace or conceal failed frames. Recommended next action: isolate the leggings stack at frame129 and the transient line frames, then correct the source in a separately authorized candidate. Preserve the current frozen source and ART_REVISE record.

## Subsequent read-only modifier isolation

At the owning agent's request, the frame129 leggings stack was evaluated stage by stage without saving a `.blend`. Raw mesh, Armature-only and Armature+Subdivision have no extreme vertex. Adding Solidify produces the outlier. The original Solidify settings are thickness 0.002 m, inward offset -1, `use_even_offset=true`, `thickness_clamp=0.0`, `solidify_mode=EXTRUDE`.

Four configurations were then screened at every frame 1–169. This screening used actual evaluated mesh vertices with explicit world-space limits: abs(X)>1.4 m, abs(Y)>1.4 m, Z>2.2 m, Z<-0.3 m, or non-finite coordinates.

| Temporary configuration | Frames with extreme vertices |
|---|---|
| Original even offset | 129, 159 |
| Only `use_even_offset=false` | None across all 169 frames |
| Even offset retained; `thickness_clamp=0.5` | 129, 159 |
| Same clamp plus `use_thickness_angle_clamp=true` | 129, 159 |

`leggings_modifier_isolation.json` contains all frame measurements and exact settings. Setting only `use_even_offset=false` is the verified minimal technical correction candidate; thickness and inward offset remain unchanged. It avoids the unstable even-thickness amplification at the deformed fold. This is a cause inference supported by modifier isolation, not a general proof that every fold is well constructed.

The unsaved corrected stills `frame129_even_offset_false_UNSAVED.png` and `frame159_even_offset_false_UNSAVED.png` were rendered and visually inspected. Both remove the large spike/stray-line defect while retaining the displayed pose and normal leggings envelope. Cloth penetration and open equipment grips remain. No corrected full movie or corrected source save was produced by this subtask; the raw frozen-source movie remains unaltered evidence of its failures.

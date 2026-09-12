# BW1 technical r003 motion evidence — ART_REVISE

The final recording is `ada_bw1_articulation_r003_review.mp4`, rendered from frozen `ada_body_costume_checkpoint_r003_ART_REVISE.blend`. It records the existing Blender articulation diagnostic and preserves the remaining art defects visibly. No human approval, successful grip, finished body/costume, Unreal animation compatibility, or gameplay outcome is implied.

## Source and media provenance

| Field | Executed result |
|---|---|
| Source SHA256 before and after rendering/audit | `03829ab406d6bd5e6a1c5f86e045e9f2edc720b05e620e70017667c59be8b3f8` |
| Saved scene | `BW1_BODY_COSTUME` |
| Saved camera | `BW1_Camera_three_quarter`; unchanged orthographic framing |
| Existing action | `BW1_DIAGNOSTIC_RANGE_ART_REVISE` on `BW1_Temporary_Pose_Rig` |
| Frame range | 1–169 inclusive, 24 FPS; 7.041667 seconds |
| Actual image sequence | 169 PNGs retained at 680×880 |
| Render | Blender 5.1.1 Workbench, single clay 0.55, studio lighting, shadows, cavity BOTH |
| Encoding | Native Blender VSE, VIDEO media type, H264/MPEG4, no audio |
| MP4 verification | Fresh factory-startup Blender process reopened 169 frames at 24 FPS and 680×880 |
| MP4 size | 368718 bytes |
| MP4 SHA256 | `3d5c96ee9007ec21bbd2e533a2e8ad6433e46ce02e5b19230fad4b0439a84172` |
| Visual review | Every frame inspected through all 11 labeled 4×4 contact sheets, plus native-resolution frames 67, 129 and 159 |

The review method was actual frame inspection, not a claim of continuous native-player playback. Contact sheets downsample uniformly and add labels outside the images. PNGs were not warped, repainted or replaced. `metadata.json` records camera transform, source hash and UTC execution times. `contact_sheet_manifest.json` retains frame hashes and coverage. `video_verification.json` records fresh-process MP4 verification. No `.blend` save or live MCP operation was performed by this media task. Previous raw `motion-final/` and `motion-r002/` evidence remains intact.

## Technical corrections demonstrated

The r003 source contains the parent-applied `use_even_offset=False` correction on Solidify for both `BW1_Leggings` (0.002 m thickness) and `BW1_CoatUpper_Continuous` (0.006 m thickness). The remaining thickness and pose construction were preserved.

- The large leggings spike at frame 129 and narrow spike at frame 159 seen in r001 are absent in the r003 images.
- The upper-coat spike behind the right shoulder at frame 67 and the corresponding thin artifacts during arm movement are absent in the r003 images.
- Both effects were diagnosed in separately preserved prior evidence through modifier isolation and unsaved candidates. These are technical stability corrections, not an additional art revision or proof of collision-free thickness.

The evaluated screening covered **45 active clothing/equipment meshes over all 169 frames**. It returned **zero nonfinite/extreme-world-bounds events**. The screen tests `abs(X)>1.4 m`, `abs(Y)>1.4 m`, `Z>2.2 m`, `Z<−0.3 m`, or nonfinite values. Seventeen conservative temporal flags remain for vertices moving more than 0.12 m between adjacent frames: sword tip during the arm range, and boot/sole/strap during entry to and return from kneeling. These follow visible articulated movement; no new singular spike was identified in the inspected images. The maximum flagged step is 0.1400661 m on the right sole at frame 165.

The coat maximum adjacent-frame evaluated vertex movement is 0.0488512 m; leggings is 0.0854775 m. Both have no temporal flags. Exact per-object observations are in `clothing_temporal_audit.json`, which also binds the before/after source hash. These tests do not detect all intersections, establish suitable ground contact, or approve mesh quality.

## Remaining defects, with visible times

| Defect | Evidence in this recording | Status |
|---|---|---|
| Sword and shield grips do not close around handles | Both hands remain open beside equipment throughout, especially clear at frame 67 (2.750 s) and 159 (6.583 s) | Major; grip proof failed |
| Thigh passes through hanging garment/front panels | Approximately frames 41–58 (1.667–2.375 s), and 113–130 (4.667–5.375 s); frame 129 native image clearly exposes the thigh | Major; cloth movement proof failed |
| Kneeling reveals unresolved garment clearance and knee/greave relationships | Approximately frames 139–163 (5.750–6.750 s), largest held bend around 145–157 (6.000–6.500 s) | Major; leg assembly not approved |
| Head/neck/collar interface is unfinished | Jagged contextual head attachment visible through the sequence | Context only; head remains ART_REVISE |
| Costume and armor retain coarse construction | Breastplate panels, belt fit, shoulder transitions and greave openings remain visibly at study/blockout quality | Further art work required |
| Ground contact and motion usefulness are unproven | This is an articulated test sequence without an actual game stage. The right sole reaches world Z −0.1233 m at frame 165; no calibrated-ground contact pass is claimed | Not accepted as locomotion or a kneeling game clip |

The sequence demonstrates that the candidate can be evaluated and rendered through its temporary rig while exposing failures. It does not establish a convincing final sleeve/pauldron/glove/grip assembly or leg/boot/greave assembly. The separate stopped grip-study record remains authoritative for its rejected attempts.

Recommendation: hand off this stable r003 recording for honest development review with **ART_REVISE** maintained. The next bounded art work should resolve the failed equipment grips and hanging-cloth clearance with explicit contact/deformation construction. Do not promote a reusable recipe, rig/export acceptance, or human approval from this diagnostic movie.

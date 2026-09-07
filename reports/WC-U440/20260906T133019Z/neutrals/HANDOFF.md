# Seven neutral Blender sources and export handoff

Status: **AUTHORED, BLENDER EXECUTED, EXPORTED. UNREAL AND CONTINUOUS VISUAL ACCEPTANCE OPEN.** Ownership of source/exports is released to the root integration owner. No finished-art claim is made from stills or structural checks.

The actual Blender executable was `C:/Program Files/Blender Foundation/Blender 5.1/blender.exe`, version 5.1.1, build b70da489d7f4. The authoring script is `tools/blender/author_neutrals.py`. It uses the existing mesh/material/export helpers read-only, with original creature geometry, individual mechanical rigs and motion. No external asset downloads or copied reference assets were used.

| ID | Current revision | LOD0 triangles | Bones | Clips |
|---|---:|---:|---:|---:|
| wc_n_sprout | 2 | 1056 | 9 | 5 |
| wc_n_thorn | 3 | 2068 | 12 | 5 |
| wc_n_wisp | 2 | 1820 | 9 | 6 |
| wc_n_stoneback | 3 | 1860 | 11 | 6 |
| wc_n_prowler | 2 | 2160 | 11 | 6 |
| wc_n_sentinel | 2 | 2004 | 9 | 6 |
| wc_n_warden | 2 | 1304 | 12 | 6 |

Sources: `art-source/neutrals/<id>/<id>.blend`. Exports: `exports/neutrals/<id>/`. Each contains a base skeletal FBX, LOD1/LOD2 FBXs, one 1024px BaseColor/Normal/ORM set, 640px portrait, required clip FBXs and `export_manifest.json` with source/export hashes, bone list, clip endpoints and release frames. Normal textures are explicitly flat tangent normals; geometry supplies bevels. Palette UVs deliberately reuse small atlas swatches; they are not painted unique unwraps.

All rigs have `root`, `body`, `head`, `cast_origin`, `head_ui` and creature-specific limbs/props. The meshes are source meters, +Y forward, +Z up with applied transforms; exported through `fbx_skeletal_cm_v1.json`. Use separate neutral skeleton assets. The prior measured centimeter/facing profile is retained, but these new rigs still require actual Unreal scale/facing/contact verification. Gameplay uses the one-cell proxy; exported meshes make no physical-ragdoll assumption.

Required clips are Idle/Move/Attack/Hit/Defeat, with Active on Wisp/Stoneback/Prowler/Sentinel/Warden. All are 60fps, no root translation or scale animation. Attack/Active release frames derive from canonical cast/windup timing. The runtime moves Prowler during Bound; its clip crouches/recoveries without baked translation. Defeat is a contained lowering pose and needs the game's non-graphic dissolution.

## Executed checks and retained evidence

- Main revision-2 authoring process: this folder's `author-all.log`, exit 0. Thorn and Stoneback revision-3 corrections: `reports/WC-U440/20260906T133400Z/neutrals`, both exit 0. Each manifest's `review_path` is authoritative for the current version.
- All seven `structural.json` reports pass: one material and UV layer, single root, no unweighted vertices, excess influences or unnormalized weights.
- All seven `motion-invariants.json` reports pass. Every frame of every required clip was evaluated for root translation, scale invariance and floor penetration.
- `recording-validation.json`: **40 actual MP4s**, **2437 frames**, **60fps**, **384x384**, **40.6167 seconds total**; Blender movie readback and source/export hash checks pass. This is metadata validation, not an auditory, continuous visual, or performance result.
- `pose-samples.log`: 200 actual rendered sparse poses. Seven labelled `wc_n_*_pose_sheet.png` sheets were inspected, along with all seven Cycles portraits. The contact sheet is `neutral_portrait_contact_sheet.png`.
- Corrected observed issues: Thorn detached-looking roots and connector face occlusion; cropped Stoneback portrait; paper-thin shell panels; missing visible Sentinel bell suspension. The sampled poses show contained movement and distinct launcher, shell-lift, bell-swing, feline crouch, crown/panel and lantern motions without gross silhouette collapse.
- The first movie-output run failed on Blender 5.1's media type change. The failing log is retained in `reports/WC-U440/20260906T132352Z/neutrals/author-all.log`. Local RNA inspection established that `image_settings.media_type='VIDEO'` is required before `file_format='FFMPEG'`; successful runs use that API.

## Remaining work and limits

1. Import each new skeleton/mesh/LOD/clip/texture/portrait into Unreal, verify measured scale/facing and one-cell selection proxy, then inspect both team orientations in the board camera.
2. Review all 40 clips continuously at normal speed. Current model-visible tools expose still images, not a continuous video stream; the real MP4s are retained for that review. Sparse poses do not close this gate.
3. Verify contact and release/impact timing with actual basic attacks, optional skills, dash movement, shields, stun and defeat dissolution. Idle/move/defeat motion is restrained and may need stronger readability after game-camera review.
4. Integrate neutral effects/audio and listen to the complete mix. No audio asset or listening claim belongs to this authoring handoff.
5. Inspect LOD silhouettes, materials and portrait recognition at the actual UI sizes. All source constructions are deliberately faceted candidates; final visual quality remains open.
6. Measure frame times on named hardware after Blender rendering has stopped. These authoring runs are not performance evidence.

To regenerate intentionally, preserve evidence and use a fresh report directory:

```powershell
& 'C:/Program Files/Blender Foundation/Blender 5.1/blender.exe' --background --factory-startup --python-exit-code 1 --python tools/blender/author_neutrals.py -- --creature all --revision 4 --report-dir reports/WC-U440/<fresh-UTC>/neutrals
```

The revision-2 and revision-3 author scripts were snapshotted in their report folders. Current neutral source/export ownership is frozen for root import; do not run regeneration concurrently with that import.

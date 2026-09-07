# Sora Dragonkin pilot — source/export handoff

Sora revision 3 is frozen for parent-owned Unreal import. This is authored and executed Blender source with actual FBX/movie readback; it does not certify finished art, continuous motion approval or playable packaged content.

- Source: `art-source/heroes/wc_u_dragonkin_guardian/wc_u_dragonkin_guardian.blend`.
- Source SHA256: `595788dd19cf4d35b53565189a31c147ebb5c6e0b390838ee6e32fbf3bc3439a`.
- Export manifest: `exports/heroes/wc_u_dragonkin_guardian/export_manifest.json`.
- Manifest SHA256: `071ad17af86682d707b404f441a6068331b48afdffd8ebc9d7bef17947cc48a1`.
- Actual Blender 5.1.1, four render threads; one own Blender process at a time.
- Separate rig `WC_humanoid_draconic_v1`, 27 established bone names and sockets, separately measured draconic neck/head/shoulders. Actual rest matrices, head/tail coordinates and hierarchy are in `sora/rig-calibration.json`. Same names do not establish compatibility.
- Meter source, +Y forward, +Z up; FBX exported through frozen independent-centimeter-copy profile. No source/actor scale workaround claimed.
- LOD0/1/2: 8474 / 4234 / 2095 triangles; one material, one UV layer. Three 1024-pixel texture maps, one model-derived 640-pixel portrait, three mesh FBXs and seven animation FBXs. Fourteen exact output hashes are in HANDOFF.json and the export manifest.

## Changes and actual inspection

Built an integrated 216-vertex skull/muzzle surface, fitted concentric eye/iris/pupil/glint layers and lids/brows to that actual surface, short swept horns, compact neck crest and throat scales. Broad pale ceremonial armor, royal-blue panels, articulated arm armor with soft visible joints, an engraved oval beacon shield and short blunt fluted mace retain the authored identity. Feet are plantigrade; no wings, tail, copied human head, hidden inventory or stat gear.

The first source exposed sharply folded arm armor. Revision 2 separates rigid upper-arm/forearm sections and smooth joints; revision 3 also curves the horns and lowers the undersleeve below the closed pauldron top. Actual front, side, back, face, three-quarter and gameplay-angle views were inspected. All 21 start/release-or-middle/end poses were inspected via actual renders; their hash-bound montages are `sora/actual-pose-grid-1.png` and `-2.png`. Two actual 96-pixel silhouettes were inspected. Sparse samples do not prove normal-speed continuous quality, all inter-frame clearances or crowded-board readability.

## Executed verification

Production exit 0 and independent verifier exit 0. `sora-readback/fbx-video-validation.json` binds the unchanged saved source and every export. All three mesh FBXs were actually reimported with matching dimensions, triangles, bones, materials, UVs and weighted vertices. All seven animation FBXs were actually reimported using explicit `anim_offset=0.0`; their frame ranges match source.

All 439 authored frames were evaluated for deformed geometry, root and bone scale. Hand and foot IK clamp are zero in every clip. Lowest source geometry stays approximately +2.08 mm above the floor; root translation and scale error are zero. Seven actual MP4 files read back at 384×384 and 60 FPS: 439 total frames, 7.316667 seconds including each clip endpoint. Video metadata verification is not continuous visual approval.

| Clip | Inclusive source frames | Release frame |
|---|---:|---:|
| Idle | 1–121 | — |
| Move | 1–61 | — |
| Attack | 1–40 | 16 (250 ms) |
| Active | 1–40 | 22 (350 ms) |
| Hit | 1–25 | — |
| Defeat | 1–61 | — |
| Victory | 1–91 | — |

The source's previous negative-X active tilt faced the shield downward. The actual r2 fixture failed with outward-normal Z = -0.529919. The corrected r3 source passes at +0.406737; the check reads the actual deformed weapon bone at release. Exact rest skeleton and all six unaffected action curves remain unchanged; only Active changed. This fixes presentation without changing canonical timing or rules.

## Retained failures and boundaries

- Revision 1 and 2 source/export inputs remain under the next revision's `before-source` and `before-exports`, with their original reports at `20260906T164907Z` and `20260906T165204Z`.
- The first semantic audit used Blender's default Python-error behavior, which returned process 0 despite the recorded AssertionError. It is a failed semantic audit, not a pass. The fresh repeated fixture explicitly used `--python-exit-code 2`, retained exit 2 and wrote `sora-negative-semantic-fixture/semantic-check.json`. Final production and verification explicitly use that fail-closed switch.
- LOD generation logged duplicate-face diagnostics, then removed 2 / 22 invalid triangles before final export. Actual clean FBX readbacks match final counts. Those diagnostics are preserved; no failed artifact was relabeled.
- Parent-owned Unreal family calibration, cold load, actual gallery/board footage, material/skeleton/animation/actor reference preservation through a deliberate costume reimport, continuous seven-clip art review, neighbor overlaps, LOD silhouettes, effects/audio synchronization and frame-time measurement remain open.
- Sora's muzzle is intentionally subtle head-on but projects clearly in the actual side view. Elbow/cuff transitions and broad armor shapes still merit close continuous and game-camera review; no finished-hero claim is made.

No shared rig/material, frozen preparation helper, canonical data, existing hero or Unreal binary was modified in this lane. Varek, Iri and Oren production remain gated until the parent releases them after Sora's engine pilot.

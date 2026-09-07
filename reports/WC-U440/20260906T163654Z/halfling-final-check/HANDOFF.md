# Finn, Nella and Milo source/export handoff

All three selected heroes are frozen for root-owned Unreal integration. Source authoring, execution, hash checks, actual FBX import readback, and sparse visual inspection are complete at the scopes below. This handoff does not approve finished art or replace engine import, continuous motion, gameplay-camera, audio or performance gates.

| Hero | Revision | LOD0 / LOD1 / LOD2 triangles | Actual source/video frames | Actual video seconds |
|---|---:|---|---:|---:|
| Finn | 5 | 6996 / 3498 / 1744 | 439 | 7.3166667 |
| Nella | 4 | 6748 / 3373 / 1668 | 430 | 7.1666667 |
| Milo | 2 | 8400 / 4200 / 2083 | 442 | 7.3666667 |

All use the frozen 27-bone `WC_humanoid_small_v1` family, one material, one UV layer, 1024-square BaseColor/Normal/ORM textures, a 640-square model-derived portrait, and seven separately exported animation FBXs. All 42 export files match their manifests. Sources remain in metres; the established exporter produces independent centimetre copies. Actual mesh-FBX readback confirms dimensions, triangles, bones, material, UV and weights. All 21 animation-FBX files were imported with explicit `anim_offset=0.0`, and their recorded frame ranges match the saved actions.

Source and readback locations:

- **Finn** `wc_u_halfling_ranger`: source `C:\Users\iputu\Documents\Wonder Chess\art-source\heroes\wc_u_halfling_ranger\wc_u_halfling_ranger.blend` (SHA256 `3cdc9c6c637a4eef1d0fcb9afead810d4be308364e3a1117278160058be79b7f`); export manifest `C:\Users\iputu\Documents\Wonder Chess\exports\heroes\wc_u_halfling_ranger\export_manifest.json` (SHA256 `5ff9dfcd6e4d23a30f76c93733be479adbdb2bc0cc58f99dd4ab2e750d61343a`). Readback: `C:\Users\iputu\Documents\Wonder Chess\reports\WC-U440\20260906T163654Z\halfling-final-check\finn-readback\fbx-video-validation.json`.

- **Nella** `wc_u_halfling_rogue`: source `C:\Users\iputu\Documents\Wonder Chess\art-source\heroes\wc_u_halfling_rogue\wc_u_halfling_rogue.blend` (SHA256 `668ae6c0eb57949364a7ac4c5cdf752d4aa20112b3ffe3301ddcb2914f1c9802`); export manifest `C:\Users\iputu\Documents\Wonder Chess\exports\heroes\wc_u_halfling_rogue\export_manifest.json` (SHA256 `7f89d2b7e07ee494d05033b51db345223c10a1d0c065b5f88f020b95e5da6315`). Readback: `C:\Users\iputu\Documents\Wonder Chess\reports\WC-U440\20260906T163654Z\halfling-final-check\nella-readback\fbx-video-validation.json`.

- **Milo** `wc_u_halfling_mage`: source `C:\Users\iputu\Documents\Wonder Chess\art-source\heroes\wc_u_halfling_mage\wc_u_halfling_mage.blend` (SHA256 `b64ad1262cb15bcb5bde668a4767df6a5cea5111b797c31ae6129a80ba562faf`); export manifest `C:\Users\iputu\Documents\Wonder Chess\exports\heroes\wc_u_halfling_mage\export_manifest.json` (SHA256 `09aa0467d406f759c924cfa09d518858a5f4c0cf5a04f7f0627c19faff71caf7`). Readback: `C:\Users\iputu\Documents\Wonder Chess\reports\WC-U440\20260906T162841Z\halfling-face-fit\milo-readback\fbx-video-validation.json`.

## Authored differences and fixes

Finn has a narrow adult face, sandy curls, upturned folded brim, blue vest/cream sleeves, short triangular river cape and side quiver. The bow is held upright; its string endpoints follow the bow hand and its nock follows the drawing hand. Dulling Shot uses a raised, careful aim within the authored cast timing. His initial vest/trouser gap and pointed shoulder cloth were found in actual renders and corrected before the final source freeze.

Nella has fitted green-brown eyes, one solid swept tuft, a plum jacket and asymmetric starred lapel, teal waist/diagonal cape cord, a diamond cape, and paired broad painted fan batons. The active performs an off-hand lead and forward gesture; it does not teleport. A first-pass Move target exceeded leg reach by 2.7406 mm and correctly failed production. The in-place pelvis was lowered 5.5 mm; final all-frame IK checks show no clamp. Thin obsolete hair strands visible in revision 3 were removed in revision 4.

Milo has fitted gray eyes, a small mustache and wavy hair, round blue raincoat with separate front panels, a high pale collar, thick spiral wand and a fixed rear decorative umbrella disk. His active uses the authored small stir/flick; the model does not imply an added shield, flight or persistent cloud effect. Equipment remains visual only.

The final facial refinements preserve exact previous seven-action curves, rest skeletons, non-head vertex positions, swatches and skin weights. Each verifier records these signatures. No canonical hero statistics, ability timing, shared rig, Pippa source, Unreal binary, or equipment-inventory logic was changed by this lane.

## Actual inspection and remaining gates

The 21 actual 384-square 60 fps MP4 files have 1,311 frames reported by actual movie readback and total 21.85 seconds including inclusive source endpoints. Every authored frame was executed through the deformed-mesh/root/scale/floor checks. I inspected 63 actual start/release-or-mid/end pose renders, 18 model views, and six actual 96-pixel black-on-white silhouettes. These are sparse visual inspections, not continuous normal-speed motion approval.

Finnâ€™s broad brim and upright bow are visible front-on; his bow and face foreshorten at the high game angle. Nellaâ€™s paired broad baton ends and swept tuft separate her silhouette; the side-on and off-hand anticipation still need normal-speed crowded-board review. Miloâ€™s spiral and collar show clearly front-on but the focus foreshortens at the high angle. Readability beside large allied shields/staves, exact hand/weapon/costume collision, all LOD silhouettes, engine animation transitions, effect/audio synchronization and final attractive-art acceptance remain open.

An early silhouette staging pass accidentally left the presentation ground visible, producing unusable ground-filled images. Those images remain under the earlier Finn/Nella readbacks; they are not visual acceptance. The final verifier hides that ground and requires substantial separated dark and light pixel populations. The final Finn readback in this directory and the final Nella/Milo readbacks contain the corrected captures. No original source file was altered during verification.

Retained earlier candidates/failures: `reports/WC-U440/20260906T161802Z/halflings` (Finn1), `161953Z/halflings` (Finn2), `162137Z/halflings` (Finn3 and failed Nella1), `162318Z/halflings` (Finn4/Nella2/Milo1), and `162841Z/halfling-face-fit` (Finn5/Nella3/Milo2). Fresh later authoring directories contain full before-source and before-exports copies. No failed record was overwritten or relabeled.

## Resume in Unreal

Root owns all `.uasset`/map imports. Import only the frozen manifest-bound Finn5, Nella4 and Milo2 exports, run cold asset validation, inspect actual gallery and board cameras, then run the motion capture/encoding and full packaged-match gates. Keep this source/export handoff separate from any later engine verification result. The parent has already received each per-hero freeze message.

The new Unreal motion encoder is separately documented in `reports/WC-U450/20260906T161426Z/pippa-encoder-repaired/HANDOFF.md`: 14 focused tests and actual seven-clip Pippa viewport encoding passed; original 151 PNGs are hash-preserved. That encoder pass is not continuous visual approval.

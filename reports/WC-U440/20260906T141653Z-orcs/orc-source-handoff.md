# Orc source and measured export handoff

Executed in Blender 5.1.1 on 2026-09-06. The three owned production source/export directories are frozen for the root's Unreal reimport. No Dwarf, shared rig/material/map, canonical data or Unreal asset was modified in this art lane. Detailed versions, source/manifest hashes, actual measured counts and open checks are in `orc-source-handoff.json` beside this file.

| Hero | Stable ID | Source / geometry / animation revision | LOD0 / LOD1 / LOD2 triangles | All authored frames evaluated and verified in MP4 |
| --- | --- | --- | --- | --- |
| Rok | wc_u_orc_warrior | 7 / 7 / 6 | 5462 / 2731 / 1364 | 439 |
| Zura | wc_u_orc_mage | 7 / 7 / 6 | 6884 / 3441 / 1720 | 457 |
| Kesh | wc_u_orc_rogue | 7 / 7 / 7 | 3798 / 1899 / 948 | 430 |

Rok now has a curved ochre mantle, red stitched edging and hip sash, brown padded torso, cloth trousers, a distinct open balance hand and a more compact broad axe. Zura has curved cloud shoulder cloth, separated three-part braids, tapered split coat, a smaller sky stone and wider fork negative space. Kesh has shorter rounded blades, tan sash, a route patch and pale hair tie, cloth trousers, and a scarf clear of his chin. All preserve their original family skeleton, stable mesh/action IDs, source-separated body/costume/equipment, materials and UV atlas. Faces, shoulder caps and grips were refined independently of their gameplay definitions.

Actual Cycles front/side/back/three-quarter views were inspected for each. Chosen review directories:

- `rok-candidate02/workbench-review`
- `zura-candidate02/workbench-fitted`
- `kesh-contact03/workbench-review`

Each contains seven real `continuous_<Clip>.mp4` files rendered at every authored frame at 60fps, selected pose PNGs, `pose-index.png`, `motion-invariants.json`, `normal-speed-evidence.json`, `published-verification.json` and the original/refined hashes. MP4 video-track stts/stsz/mdhd sample counts, timing, codec and hashes were read from actual output: 21 videos and 1326 inclusive-endpoint source frames total. Selected poses across all seven clips were visually inspected. This does not claim continuous visual acceptance. Material stills are Cycles; Workbench videos prove the actual textured geometry sequence and require continuous Unreal review.

Kesh's first all-frame Move check failed at -0.0042306688m. `fix_orc_move_contact.py` sampled all existing poses before modifying keys, added at most 0.0062306688m to the pelvis support position, and preserved the root transform, rig and six other action hashes. The corrected all-frame minimum is 0.0019999743m. The failed candidate and report remain intact. Zura's first portrait and Victory video cropped the raised staff; the fitted review projects every deformed vertex at every authored frame, and the corrected portrait uses actual posed bounds. All earlier images/videos remain available.

Three fresh Blender process checks exited 0 after production promotion. Each verified 14 exported files, retained rig/action invariants, source/manifest hashes, EXPORT and LOD_SOURCE skin/scale/UV/material structures, and post-save sampled motion. The stronger full-frame checks were run on the exact candidates whose invariant hashes were confirmed after promotion. Export used the existing measured `fbx_skeletal_cm_v1.json` profile: three mesh/LOD FBXs, seven animation FBXs, three retained textures and one model-derived portrait per hero.

Important metadata limitation: generic `verify_refined_hero.py` reads an older hand-contact-only `changed_clips` field and prints an empty `modified_clips` list for Kesh. The actual source invariants, `refinement.animation_changes`, `export-result.animations_modified_by_refinement` and final hero manifest correctly identify only Move as changed and set animation_revision=7. The consolidated JSON uses those correct fields. The shared verifier was not edited in this lane.

Not yet verified in this handoff: Unreal revision7 import/reimport, cold engine asset/clip tests, current in-engine continuous clip playback, source-to-engine appearance, FX/audio timing, LOD silhouette/crowd occlusion, packaged runtime/performance and final art acceptance. The assets remain faceted alpha refinements and are not certified finished heroes by a script exit code.

Fresh verification commands, from the workspace root (do not rerun into these same retained evidence files):

```powershell
& 'C:\Program Files\Blender Foundation\Blender 5.1\blender.exe' --background --threads 4 --python-exit-code 1 --python tools/blender/verify_refined_hero.py -- --unit wc_u_orc_warrior --output reports/WC-U440/20260906T141653Z-orcs/rok-candidate02/workbench-review
& 'C:\Program Files\Blender Foundation\Blender 5.1\blender.exe' --background --threads 4 --python-exit-code 1 --python tools/blender/verify_refined_hero.py -- --unit wc_u_orc_mage --output reports/WC-U440/20260906T141653Z-orcs/zura-candidate02/workbench-fitted
& 'C:\Program Files\Blender Foundation\Blender 5.1\blender.exe' --background --threads 4 --python-exit-code 1 --python tools/blender/verify_refined_hero.py -- --unit wc_u_orc_rogue --output reports/WC-U440/20260906T141653Z-orcs/kesh-contact03/workbench-review
```

For a fresh rerun, copy only required immutable inputs into a new timestamped evidence directory before invoking the verifier. The next integration step belongs to the root's serialized Unreal import lane. Upcoming Sora/Dragonkin production is not started; Sora's full dossier has been read and source production awaits the root's family-sequence release.

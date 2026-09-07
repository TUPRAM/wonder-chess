# Art execution evidence

The art lane owns the authored Blender scripts, original `.blend` sources, and hero/arena exports. Unreal import and game presentation are performed by the integration lane. These are separate acceptance boundaries.

Actual tools: Blender 5.1.1, build `b70da489d7f4`, invoked through `C:/Program Files/Blender Foundation/Blender 5.1/blender.exe`, with `--background --factory-startup --python-exit-code 1`. Factory startup applies only to these new isolated processes. No user scene or other project's files were read or reset.

## Executed reference checkpoint

- `tools/blender/create_calibration_scene.py`: executed successfully. Measured source cube is 1 m on each axis; tile is 2 m by 2 m by 0.2 m. The named forward arrow is authored along positive Y. The probe has an actual keyed one-second skeletal action.
- `tools/blender/export_collection.py`: actual FBX export succeeded with the explicitly acknowledged candidate profile. This alone does not calibrate the engine.
- Ada revision 1: model, palette textures, seven FBX clips, editable source and actual portrait/front/side/back/clip-pose renders produced. Supplied inspector passes: 4,504 evaluated triangles, 27 deforming bones, one material, UVs, normalized weights, no unweighted visible vertices, and one ground-origin `root`.
- Actual render review caught excessive eye volume and too-light authored texture colors. Clip-pose review caught a shield orientation defect and wrong pelvis-local translation for kneeling. These are implementation defects, not accepted animation.
- The first Unreal measurement had correct dimensions but negative facing. The integrator's first correction made the forward sign positive but inverted Z, exposed by cube bounds `[-100, 0]` cm rather than `[0, 100]` cm. Full signed basis calibration is required before acceptance.

## Courtyard checkpoint

Thirteen original modules have executed exports: tile, alternate tile, edge, corner, low wall, bench plinth, flagpole, banner, lantern, planter, stair, distant blue-roofed facade and foundation. Source is `art-source/arena/WC_SevenLanternCourtyard.blend`; FBXs and one shared texture atlas are in `exports/arena/`.

Actual 1920x1080, 1280x720 and three-quarter renders are in `reports/WC-330/arena/`. Render inspection fixed a wrong foliage swatch and iterated the camera. The current camera is a candidate requiring the actual game HUD and a crowded encounter; Blender framing does not establish in-engine safe areas.

## Roster execution and corrections

All twelve canonical alpha IDs received original modeled sources, separate FBX mesh and animation exports, three 1024-pixel texture maps, two reduced meshes, and model-rendered portraits. The source manifest retains each full canonical art brief; no expansion hero was substituted for an alpha obligation. These are authored asset candidates, not twelve accepted finished heroes.

Revision 2 froze the 27-bone family rest poses after correcting arm roll. Revision 3 replaced protruding eye spheres with inset eye surfaces and replaced the first hair lobes with a continuous shaped hair cap. It also corrected foot counter-rotation and crouch support height. Actual deformed-mesh sampling caught a Sylas Active penetration before the correction. Each source uses its authored height and a family-specific shoulder/leg layout rather than uniform scaling of one mesh.

Revision 4 narrowed the Elf bodies, refined woven hair braids and costume hems, extended Zura's triangular coat panels, corrected Rowan's bronze bracket and spectacles, moved shoulder armor with the clavicles, and introduced baked reachable support-hand poses for the two hammers, crossbow, bow and harp. The first Dagna support-hand attempt visibly overextended the arm; the actual portrait was rejected and the grip was brought closer to the body. A subsequent batch stopped when the hammer Attack requested 12.8 cm beyond natural reach. The corrected swing keeps both hands closer to the torso and is re-executed through the same check. Failed attempts and their logs remain preserved.

The support-hand solver does not change the rest skeleton or stretch the bones. It bakes Euler poses at 50 ms intervals and preserves Euler continuity. Reach clamping is reported per clip; exceeding 2.5 cm fails the export run. This is a geometric contact check, not a claim of pleasing continuous animation. The sole check samples the actual skinned mesh every three frames at 60 FPS, with floor penetration limited to 2.5 cm and supported height to 4.5 cm. It separately checks fixed root translation and unit pose scale.

Revision 5 was executed for Liora, Elin and Tessa only. Liora now holds the bow clear of her torso at rest, draws its string through the existing `weapon_l` bone, and crouches into the Active slide. Elin's harp has a lower string support and a broader chord/raised victory gesture. Tessa has the prescribed single wide forehead lens. Elin's first raised-harp gesture exceeded natural arm reach by 8.64 cm; lowering the hold and moving the plucking hand corrected the failed check before export acceptance. All three include fresh portraits, key poses and sampled deformation reports; all twelve source/rest/export parity checks pass.

The first Unreal all-hero import created twelve skeletal meshes, eighty-four sequences and twenty-four lower LODs. A fresh-process integration test subsequently found that generated skeleton packages had not been persisted; the integration lane corrected explicit skeleton saving and is reimporting. The earlier successful object-creation report alone was not a valid cold-load acceptance. Consult the integration lane's current reports for the actual package state.

## Visual evidence and limits

`reports/WC-330/roster/twelve_hero_portraits.png` and `84_key_pose_contact_sheet.png` contain actual Blender renders. Each hero also has front, side, back, seven key poses and a 96-pixel portrait preview. The initial thirty-six small-scale LOD renders are assembled into `lod_comparison_1.png` and `lod_comparison_2.png`. The reduced meshes retain the main weapon and costume silhouettes in these reviewed stills, while small eyes, hair and thin string details simplify substantially. Runtime LOD switching and all animated LOD deformations remain a separate check.

The actual twelve-model board renders use the authored camera and courtyard. They establish source-space scale and spacing; they do not establish game HUD safe areas, presentation in Unreal, real combat motion or performance. The live game camera and effects may require further framing and art adjustments.

The present models are deliberately faceted tabletop candidates. They still need an art acceptance pass for attractive faces, joint creases, cloth/plate differentiation, full authored gesture fidelity and gameplay-camera readability. In particular, sharply bent sleeves can form pronounced creases; small facial features and string work can disappear at the lower LODs. Do not present these candidates as finished heroes merely because their exports and structural checks pass.

## Evidence interpretation

The authoring meshes use tailored connected cross-section lofts, explicit facial features and hair, beveled costume/equipment polygons, proportion-specific skeletal families and normalized skinning. Original procedural authoring does not by itself establish final art quality. Close-up renders do not replace gameplay-camera inspection. Single release-pose renders do not establish continuous motion quality or all 84 animation combinations.

The texture convention is base color in sRGB, flat tangent-space normal data (the bevels are geometric), and linear ORM with red occlusion, green roughness, blue metallic. No external assets, paid services, downloaded character models or third-party animation clips were used.

Installed behavior was checked against official Blender references: [Blender 5.1 Python API changes](https://developer.blender.org/docs/release_notes/5.1/python_api/), [slotted action migration](https://developer.blender.org/docs/release_notes/4.4/upgrading/slotted_actions/), and [Blender export operators](https://docs.blender.org/api/main/bpy.ops.export_scene.html). Actual installed operator execution remains the compatibility evidence.

The static calibration measurements pass in `reports/WC-330/calibration-unreal.json`: 100 cm cube, 200 cm tile, forward axis X, positive X facing, and feet at zero with positive Z above. That static import uses named `yaw=180`, scene/unit conversion and force-front-X. It did **not** prove skeletal animation compatibility. A later actual Unreal pose evaluation found a root-scale mismatch (reference 100 versus animation 1) and a 90-degree animation basis jump. The corresponding meter FBXs are superseded for hero imports.

The production skeletal profile is now `tools/blender/profiles/fbx_skeletal_cm_v1.json`. The exporter creates temporary independent object, mesh, armature and action copies; it multiplies vertices, rest-bone translations and animation location keys/handles by 100, keeps object scale one, and exports with a 0.01-m scene unit. Original meter-valued `.blend` files, mesh vertices and rest transforms remain unchanged. The measured Unreal settings are scene/unit conversion enabled, **force-front-X disabled**, **named yaw 90**, preserve-local-transform disabled, uniform scale one. These settings are specific to the normalized skeletal exports; do not apply them blindly to the separate static arena profile.

`reports/WC-330/normalized-roster-export.json` records the actual reexport of twelve main meshes, twenty-four lower LOD meshes and eighty-four clips. `export-integrity.json` verified all 168 required hero files and source hashes with no mismatches. The separate seven-clip Ada trial in `import-probe/all7-comparison.json` passed 210 actual Unreal pose evaluations with zero root scale/translation delta and a maximum root rotation delta of approximately 0.000003416 degrees. It measured +X forward and 181.09 cm total mesh height. Full cooked-roster appearance and deformation remain separate acceptance requirements.

Unreal acceptance of the latest source revision, continuous motion review, effects/audio, human matches, network play and package performance are not certified by this art report. The source/data parity and actual export bytes can be reproduced with `python tools/blender/verify_art_exports.py`. `tools/blender/verify_rest_skeletons.py` reads the current and preceding saved Blender sources to compare rest matrices and hierarchy. Neither script establishes visual approval.

The final source review batch refreshed the three revision-5 heroes' LOD, black silhouette and support-motion views, then reassembled and inspected the 36-LOD and 45-support-pose grids. The updated bow draw and harp chord are visible in the sampled poses; angular deep elbow creases and simplified hand contacts remain art risks. All launched review workers exited successfully. Hero and arena source/export files remain frozen for integration.

Two original ranged glyphs were modeled and exported for Liora and Tessa. The first Unreal import correctly measured 64/76 triangles, 76/62 cm lengths and positive-X direction but reported four tangent/binormal warnings caused by missing UVs. The glyph-only revision 2 adds independent planar face UV islands, preserves dimensions and triangle counts, and validates all 140 UV triangles with positive area. Actual Blender author/export/render execution exited zero; `reports/WC-340/projectile-glyphs-uv-fix.log` and the revised `exports/effects/projectile_manifest.json` record the result. The prior manifest remains in `reports/WC-340/projectile-manifest-before-uv-fix.json`. Corrected Unreal reimport is pending in the integration lane at this record.

## Revision 6: response to actual Unreal pose review

The actual engine frames exposed weak Hit and Defeat signals and restrained caster/ranger gestures. A bounded animation-only revision was authorized and executed. Ada and Rowan were isolated first; their stronger recoil and deep, planted crouch were rendered and inspected before expanding the trial roster. Rowan's first raised-orb Victory crossed his face and was corrected to an outward raised hand. Subsequent source tests rejected unreachable bow/harp/hammer grips during the crouch transition and corrected them without stretching the rig. Zura's long coat prevented the same deep crouch as the shorter costumes; a shallower supported crouch and horizontal staff preserve her coat while clearly lowering the pose.

Exactly 36 production animation FBXs changed: Hit and Defeat for all twelve heroes, plus Active and Victory for the six priest/mage/ranger heroes. The other 132 required export files remain byte-identical. All sources are revision 6, with existing geometry, UVs, weights and rest matrices preserved. The alpha unit data, durations and authored release timing were not changed. No game Content file was edited by the art lane.

`reports/WC-330/animation-refinement-production.json` contains the exact root-relative import list, per-file hashes and per-source evidence. The final export integrity and twelve saved-source rest comparisons passed. The revised clips received 1,830 complete-mesh frame evaluations at 60 FPS; minimum vertex Z was +0.011878 m and maximum Defeat ankle displacement was 0.000005589 m. A preliminary final aggregate still showed 7.6 mm coat penetration for Zura; this was preserved in `animation-refinement-production-before-coat-clearance.json`, then removed with a two-degree crouch adjustment. The final whole-mesh criterion is no vertex below -0.0001 m, rather than the earlier 25 mm numerical tolerance. Current nested per-hero motion reports and failed/corrected logs are retained.

Production execution intentionally reused reviewed isolated-trial previews and did not rerender all beauty views. The next actual Unreal revision-6 frame set and crowded game views must establish whether the original engine-side readability findings are resolved. Intentional faceting and low triangle count alone are not visual defects; review the authored features, silhouette, appeal, grip contact, deformation and camera readability. Art source/export files are held stable pending that review.

The glyph UV correction has now passed actual Unreal reimport: `reports/WC-340/effect-import-uv2.json` and the integration review record commandlet exit 0 at 14:39:05, with 0 import errors and 0 import warnings. Both meshes retain their measured signed bounds, triangle counts and material assignment. The original warning-bearing import reports are preserved; runtime flight remains a separate presentation check.

## Revision-6 actual Unreal visual follow-up

The integration owner captured a new 21-frame review in UE 5.7.4 game mode on 2026-09-06, 15:01:39–15:02:08 local time. The art lane opened and inspected all21, covering all84 hero/clip combinations at20/52/88 percent. `unreal-visual-review-revision6.md` records per-clip and per-hero observations. Durable copies are `unreal-art-review-revision6/`; `unreal-visual-review-revision6-evidence.json` records21 actual image hashes and verifies36 revised export hashes still match their import records.

The lowered terminal crouch, stronger Hit recoil and revised caster/ranger celebrations are visible in-engine. No gross skinning failure, scale/basis jump, missing hero or detached weapon is visible, and the previous directional-light warning is gone. This closes the old sampled Defeat ambiguity and warning, and passes the bounded sampled pose checkpoint. Angular elbow/sleeve polish, small grip detail, exact skill cue readability and the final crowded gameplay camera remain distinct limits. No geometry, source action, export or game Content was edited during this review; no new gameplay, network or performance result is claimed.

## Candidate-6 packaged720p network visual checkpoint

Inspected eight actual combat images (host/client rounds5,8,10,12) from the candidate-6 Windows package. Archived unchanged originals and observed session snapshots under `packaged-candidate6-network720/`; report and hashes are `packaged-candidate6-network720-review.md` and `packaged-candidate6-network720-review-evidence.json`. Normal combat board/header/shop framing is clear at720p, including twelve-unit encounters; eleven distinct living hero definitions were observed, while Zura remains a targeted crowd gap. The readiness matrix now records that partial packaged720p coverage.

Observed P2: host round12 elimination panel at roughly y449–511 hides part of a living foreground unit. Root was notified with the exact screenshot. The projected-bounds snapshots have345 successful, in-safe-rectangle component-box evaluations, but those geometric checks do not detect this overlay occlusion. Simulation ran5x; normal animation timing, current1080p crowd, complete skills and performance are not certified. Report-only review; no source, export, game Content or package changed.

## Shipping spectator correction verified in actual pixels

Opened five actual Shipping720p combat screenshots from failed-network-startup process42484, rounds10–14. Four post-elimination images show the notice entirely in the inactive shop area and the correct SCOUTING bot header. `shipping-spectator-fix-review.md` and `shipping-spectator-fix-review-evidence.json` preserve exact images/session/launch hashes under `shipping-spectator-fix/`. Prior P2 overlap is visually closed. Run was actually network_mode0 solo,5x,stoppedround14 incomplete; no network/fullmatch/timing claim. Native primary/secondary raster percentages100/100. Zura still not observed living on-board. Reports only; art held unchanged.

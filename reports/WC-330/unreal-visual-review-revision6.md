# Revision 6 — actual Unreal hero and animation review

All 21 fresh Unreal 1920×1080 screenshots were opened and visually inspected after the capture process closed. They were captured on 2026-09-06 from 15:01:39 through 15:02:08 local time, using UE 5.7.4 and the candidate-6 pre-recap-fix Editor DLL in game mode. The durable unchanged screenshots are in `unreal-art-review-revision6/`; `unreal-visual-review-revision6-evidence.json` records every SHA-256, capture time, clip and sampled position. It also verifies that all 36 revised animation FBXs still match the actual import records. No art source, export or Unreal asset was changed during this review.

**The revised sampled poses pass the bounded Unreal deformation/readability checkpoint.** All twelve heroes render with coherent scale, orientation, family proportions, costume materials and attached equipment. The former standing-bow Defeat shape has been replaced by a clearly lowered non-combat crouch. Hit recoil and the six caster/ranger Victory poses are more distinguishable. The orange directional-light warning is absent from every new frame. No missing hero, T-pose, exploded skinning, hundredfold shrink, basis jump, detached weapon or obvious gross stretch is visible in these samples.

The cast has a coherent original faceted tabletop style. The warm/cool costume groupings, deliberately different equipment contours, varied hair/headgear and four proportion families give the twelve characters identifiable visual roles. This is authored modeled costume and equipment, with recognizable high-fantasy silhouettes; faceting alone is not a defect or grounds to call the models mannequins. The broad forms are appealing and readable in this orderly view. The final crowded gameplay view and complete skill presentation remain required before accepting all twelve as finished playable heroes.

## Coverage and interpretation

The layout is fixed: far row, left to right, Dagna, Rok, Zura, Kesh; middle row Elin, Sylas, Borin, Tessa; near row Ada, Mira, Rowan, Liora. Each animation is shown at 20%, 52% and 88% of its individual duration. All 84 hero/clip combinations were examined at all three positions: 252 visible sampled instances, not 252 independent gameplay tests. The camera is the isolated asset-review camera, not the newly changed full-board HUD camera. Three still frames do not establish continuous playback, exact release timing or effects/audio alignment.

| Clip | Frames | Actual visible result |
|---|---|---|
| Idle | 00–02 | Stable stances, family heights and equipment silhouettes. Primary colors remain separate from the limestone. Most fine facial features are occluded by the steep angle. |
| Move | 03–05 | Alternating support, bent knees and arm/equipment movement appear without gross distortion. Fixed-position sampling does not verify foot sliding while the runtime translates actors. |
| Attack | 06–08 | Ada's shield/sword movement, the hammer changes, rogue arm movement and ranged hand positioning remain coherent. Small bowstring, plucking and crossbow contact are not confidently resolvable in these full-frame images. |
| Active | 09–11 | Ada's shield action, rogue forward stances and Liora's slide stance are visibly different. Mira's staff crosses forward, Rowan gathers the orb hand, Elin opens the harp gesture, and Tessa changes her brace. These smaller gestures remain restrained at this distance; the full skill cue must supply the action's gameplay meaning. |
| Hit | 12–14 | All four families open the chest, pull the shoulders back and expose more of the face than Idle. Ada's shield follows the recoil without separating. Comparison with the archived candidate-4 frame 13 confirms the stronger torso/arm silhouette. |
| Defeat | 15–17 | Bodies descend into bent-knee crouches, heads bow and equipment lowers. At 88%, Ada's shield and the dwarf hammers are below the face, the casters' implements are lowered, and the rogues' blades sit beside their knees. Zura is shallower to preserve coat clearance but still reads as inactive. This resolves the old near-standing bow in the sampled terminal state. |
| Victory | 18–20 | Mira, Rowan and Zura raise equipment to one side with the face clear. Liora's fist lifts independently of the bow. Elin raises the harp and Tessa lifts her supported crossbow. The six revised gestures separate better from their ordinary guard. The ordinary guardian/warrior/rogue celebrations remain restrained but recognizable. |

## Per-hero observations

Every row below includes all seven clips and all three sampled positions; the observations highlight distinguishing details and remaining camera limits rather than claiming unseen detail fidelity.

| Hero | Dossier features visible at this angle | Revision-6 pose observation |
|---|---|---|
| Ada Brightshield | Navy kite shield, bright single crest, ivory armor and broad shoulders | Recoil and deep crouch are clear; lowered shield stays connected to the hand and clears the face. |
| Mira Dawnwell | Coral mantle, circular staff head and tied-up auburn hair | Staff moves across the body in Active and to the side in Victory; terminal staff head lowers near the feet. The open circle remains discernible when it faces the camera. |
| Rowan Emberwick | Indigo/amber costume and small framed golden orb | The outward raised orb arm leaves the face clear in Victory; the terminal orb is lowered. Fine spectacles/frame detail is too small to judge here. |
| Liora Leafstep | Green slim silhouette, pale fan-like hair and crescent bow | Controlled bent-knee action stance, separate raised-fist celebration and lowered terminal bow are distinct. String-to-finger precision remains a close-view check. |
| Elin Moonsong | Silver head/hair mass, long ears, ivory sleeve ends and open harp outline | Harp support remains attached during the broader chord and raised celebration; terminal harp lies lower across the knees. Individual strings and braid segments are unresolved. |
| Sylas Duskrun | Dusk-blue asymmetrical shoulder shape and paired small blades | Forward action stance and compact terminal crouch differ clearly. Daggers remain near the hands in every sampled pose. |
| Borin Stonebell | Short stocky slate silhouette, open helmet/beard mass and bell-shaped hammer | Hammer is supported in normal clips, then flattened below the face in the deep crouch. Individual beard strands are obscured by the top-down view. |
| Tessa Brassbolt | Mustard jacket, copper hair and horizontal crossbow | Active and Victory keep the weapon close and supported; the terminal pose is lower and compact. The forehead lens and detailed stock/hand interfaces require closer views. |
| Dagna Anvilheart | Red shoulder/coat mass and wide hammer bar | Recoil is visible in the upper body; terminal hammer lowers across the lap without obscuring the head. The short body retains its distinct proportions. |
| Rok Sunward | Broad ochre body, dark topknot, green face and broad axe | Chest recoil and deep crouch read clearly; the axe ends beside the foot region without detaching. |
| Zura Stormcall | Broad blue coat, pale collar, braided head mass and forked staff | Shallower terminal crouch keeps the coat intact and lowers the staff. Victory raises the fork to the side and ends in an extended staff sweep; check that sweep against neighbors in the crowd view. |
| Kesh Quickwind | Broad turquoise diagonal costume, scarf and small blades | Open forward action stance contrasts with compact lowered terminal posture; hand/weapon attachment remains coherent. |

## Remaining concrete limits and minor polish

- **Fine anatomy and grip polish:** Angular elbow/sleeve transitions remain apparent in the crouch and raised-arm shapes, especially the slim figures. They do not produce gross broken joints in the inspected frames. Simplified hand anatomy and dense torso/equipment overlap prevent a precise no-intersection claim for all two-handed grips. These are minor polish limitations at this view, with source close-ups retained for further work.
- **Small action silhouettes:** Elin and Tessa's Attack/Active changes are modest compared with Ada's shield action and the rogues' forward stance. Their gestures now differ, but these stills alone cannot confirm a clear harp chord, shot release or heal cue during an encounter. Review the runtime projectile/effect/audio combination at actual timing before closing skill-readability acceptance.
- **Fine features at distance:** Eyes, strings, goggles and individual braids often disappear at this scale. The primary silhouettes and materials carry identity successfully in the review layout, as the production brief prioritizes. The crowded full-board view must verify that small heroes and similar family members remain distinguishable after UI, facing and team indicators are added.
- **Extended equipment during celebration:** Zura and Mira's late Victory staff extends sideways. It remains attached and visually intentional here; this widely spaced layout cannot determine neighbor overlap. This is a crowd check, not an observed collision defect.

No subjective numeric quality score is assigned. The earlier blanket concern about faceted anatomy does not constitute a separate failing criterion: the actual remaining concerns are the specific creases, pixel coverage and unreviewed gameplay combinations listed above. The new source geometry was not changed by this revision.

## Closed findings and remaining gate

The sampled terminal Defeat ambiguity and the on-screen light-priority warning are closed by actual new Unreal images. Weak recoil and caster/ranger celebration have visibly improved enough to pass this isolated pose checkpoint. All 84 combinations retain coherent deformation and equipment attachment at the sampled positions.

WC-330 final acceptance still requires every hero in the real crowded gameplay camera, current packaged rendering, complete skill effects with their actual rule timing, and the integration lane's material/rig/performance review. Continuous playback, moving-foot contact, LOD transitions, 1080p/720p crowded opposing teams, nearby duplicate dwarfs, audio and complete matches are not certified by this report. The next unblocked art check is to inspect the integration lane's current crowded gameplay captures; production source and exports remain held stable for packaging.

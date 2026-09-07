# Actual Unreal sampled animation review

Reviewed 2026-09-06, after the final `pose-20.png` capture at 14:31:14 local time. All 21 original 1920×1080 engine screenshots in `game/Saved/WonderChessEvidence/ArtReview/` were opened and inspected. Source meshes, animation exports and arena files were held unchanged during this review.

Before the revision-6 capture reused the game screenshot directory, the integration owner preserved this original batch in `reports/WC-330/unreal-art-review-candidate4/`, including `hashes.json`. That archive is the durable image location for this historical review.

**Result: the current roster renders coherently in Unreal; final art acceptance remains open.** No obvious exploded skinning, hundredfold animation shrink, sideways basis jump, missing character, detached floating weapon or gross stretch was visible in these samples. This is a bounded visual finding and does not extend the separate numerical pose tests into an artistic pass.

The camera shows the following stable layout, left to right: far row Dagna, Rok, Zura, Kesh; middle row Elin, Sylas, Borin, Tessa; near row Ada, Mira, Rowan, Liora. All twelve appear in each screenshot. The presenter samples each animation at 20%, 52% and 88% of its individual duration. Thus this review covers 84 hero/clip combinations at three positions, or 252 visible sampled instances. Those are coverage counts, not independent gameplay tests, exact ability-release samples or continuous playback.

| Clip | Actual screenshots | Visible observation |
|---|---|---|
| Idle | `pose-00.png`–`pose-02.png` | Stable planted silhouettes, family height differences and recognizable primary equipment. Faces are largely hidden by this steep angle. |
| Move | `pose-03.png`–`pose-05.png` | Alternating leg support is visible; equipment remains with its holder. This fixed-position review cannot prove absence of sliding during runtime translation. |
| Attack | `pose-06.png`–`pose-08.png` | Ada's shield/sword shift and both hammer changes are visible. Liora's hands move into the draw region. Small bowstring, finger contact and exact release cannot be resolved confidently at this camera. |
| Active | `pose-09.png`–`pose-11.png` | Ada's shield lift, Sylas/Kesh's low forward stance and Liora's crouch are distinct. Elin's harp hand motion and Tessa's firing brace are much subtler. |
| Hit | `pose-12.png`–`pose-14.png` | Small head/torso recoil is visible, but the silhouettes remain very close to Idle. Hit recognition needs stronger animation or a verified complementary presentation cue. |
| Defeat | `pose-15.png`–`pose-17.png` | All bodies settle into a lowered forward bow. At 88% they remain standing on both feet, so the silhouette reads more like a bow than a decisive defeat. |
| Victory | `pose-18.png`–`pose-20.png` | Weapon/arm and harp gestures appear, including Liora's fist movement. Several caster/ranger poses remain close to their ordinary guard at this distance. |

## Visible defects and remaining decisions

1. **Motion-state readability needs improvement.** Hit is weak across the roster (`pose-12`–`14`). Mira, Rowan, Elin and Tessa's attack/cast/victory differences are restrained (`pose-06`–`11`, `18`–`20`). The full runtime effect/audio combination may help, but it was absent from this isolated review and cannot be credited here. Defeat should receive a more decisive authored collapse, kneel or lowered equipment shape appropriate to each dossier (`pose-17`).
2. **The steep view suppresses fine character features.** Most faces read as small dark areas beneath hair or headgear. Tessa's single lens, Liora's string and Elin's string/plucking work do not remain clearly readable. The broad class equipment and costume color masses remain distinct. Assess this again in the actual HUD camera before changing authored character scale.
3. **Precise two-handed contact remains unresolved.** Borin and Dagna's hammer grips, Tessa's crossbow grip, Liora's draw and Elin's strings remain near the expected hand region without obvious floating equipment. Torso/equipment occlusion and low pixel coverage prevent a precise no-intersection claim. Source close-ups already show angular sleeve creases; these engine views do not erase that known defect.
4. **The faceted anatomy and flat costume blocks are still apparent.** The roster is coherent as an internal tabletop candidate, but these captures do not establish twelve attractive finished heroes or full dossier detail fidelity. No subjective numerical score is assigned.
5. **The captures contain the actual orange directional-light priority warning.** The integration owner reports a source fix for the next build; no corrected screenshot was part of this batch. Retain these originals as failed-warning evidence and verify the next capture is clear.

This review is an actual Unreal, pre-package still-frame checkpoint. It does not verify animated LOD transitions, continuous cloth/joint motion, crowded opposing teams with effects, projectile timing, audio, complete tournament play, packaged rendering or frame times. The source crowd render and these orderly twelve-character samples also do not establish the final arena/HUD composition. The source/export hold remains intact pending the integration lane's next bounded revision request.

## Subsequent source revision

The integration owner authorized revision 6 in response to these observations. Thirty-six animation sequences were refined and validated in Blender, with source pose previews inspected before the production update. `animation-refinement-production.json` records the exact changed files and source checks. Hit/Defeat and caster/ranger motion concerns are addressed in source but remain open for the next actual Unreal review; the original screenshots and observations above are preserved as historical evidence. Intentional faceting itself is not a failing criterion: the next review must judge coherent authored forms, recognizable features and readable, well-behaved poses at the real camera.

# Prompt for Codex — finish and fix the whole hero roster

Written 3 October 2026 after the first runs and the first five Meshy builds. It replaces the stop rules of `CODEX_PROMPT.md`: no attempt limit, and no hero may end the run with a missing view. Paste everything in the block into Codex, opened in this repository root. It can be pasted again; finished sets are skipped.

```text
You are finishing the 2D reference images for the whole Wonder Chess hero roster (40 heroes) with your image generation tool (GPT Image). Do it in one run, hero after hero, without waiting for me between heroes. The images are uploaded to Meshy as Main / Left / Back / Right inputs to build 3D models that are then rigged and animated, so the four views of one set must show exactly the same thing.

GOAL OF THIS RUN — NOT NEGOTIABLE
At the end, every one of the 40 heroes has all four views (main, left, back, right) of its full set, and every hero with a held, strapped, standing or floating item also has a four-view body set and a four-view set for each item. No view may be left missing.

READ FIRST, IN THIS ORDER
1. production/hero-art/VISUAL_STANDARD.md — the look, the three kinds of set, the four views, the consistency checks.
2. production/hero-art/HERO_LOOKS.md — what every hero looks like and which sets it needs.
3. production/hero-art/BRIEFS.md — per hero: the folder and the ready prompt for every image. Use these prompts; append corrections when a retry needs them.
4. production/hero-art/RUN_LOG.md — what earlier runs did and why views failed.
Where this prompt disagrees with those files or with production/hero-art/CODEX_PROMPT.md, this prompt wins.

STYLE ANCHOR
art-source/asset-studio/wc_vn_shieldbearer/inputs/references/four_view_r004/with_shield/main.png
Give it to the image tool as the style reference for every hero's first image. Copy its rendering style, realism, lighting, framing and background only, never its design.

CHANGED RULES FOR THIS RUN
1. No attempt limit. Keep regenerating a view until it passes. Earlier runs stopped after three attempts; do not stop.
2. Never leave a view missing. If a view still has a defect after eight attempts, save the best attempt as the view anyway, list the exact defect in provenance.json and the run log, and move on. A slightly imperfect view is useful; a missing view is not.
3. Background: a plain light-grey studio background is enough. A faint gradient or slight unevenness is NOT a defect. Do not reject or retry an image for its background unless it contains scenery, a floor line, a cast shadow or text.
4. Proportions: the "about 5.5 heads tall" figure is a guide. Accept 5 to 6.5 heads if the hero reads clearly and matches its race. Earlier runs rejected good fronts for being closer to 7 heads; add "stocky, large head, short legs, game-character proportions" to the prompt and accept the closest result.
5. Small differences in material shade between views (for example brass versus iron on a small fitting) are recorded as a note, not a reason to reject.
What still IS a reason to regenerate: a different design, outfit or item between views; a part missing or added; the wrong hand holding an item; a side view that is turned three-quarter instead of true profile; left and right views that are mirror copies; anything cropped; a different scale or baseline between views.

LESSONS FROM THE FIRST 3D BUILDS — APPLY TO EVERY BODY AND ITEM SET
The 3D tool fuses anything that touches. A weapon drawn in a hand, or standing on the ground against a leg, becomes part of the body and cannot be swung. So:
A. body/ sets (the hero without items) are what gets rigged. Draw them in a clear A-pose:
   - both arms straight, angled about 35 degrees away from the body, not touching the torso, cloak, kilt, cape or anything else;
   - both hands EMPTY and open, palms facing the thighs, all five fingers visible, straight and slightly spread with clear gaps between them, thumb clearly separate and pointing forward. No fists, no curled fingers, no mitten hands. (Heroes that have claws, paws, stubs or elemental arms instead of hands keep those, held clear of the body the same way.)
   - legs shoulder-width apart with a visible gap between them, feet flat, standing upright, head level, looking straight ahead;
   - cloaks, capes, beards, braids and long hair hang straight and do not cover the arms or hands;
   - nothing held, strapped, standing beside, or floating near the hero. No item anywhere in the image.
   The back view shows the backs of the hands with the same arm angle; the side views show the near arm in front of the torso outline with the hand still open.
B. items/<name>/ sets show the item completely alone: no hand, no arm, no strap attached to a body, no ground.
   - Draw the whole item, including the part of a handle or shaft that a hand covered in the full view.
   - Weapons and tools stand upright and centred with the grip end at the BOTTOM and the working end at the top (club head, hammer head, blade tip, staff top, scythe blade, bow upper limb). A hook hangs with its handle at the top.
   - Keep handles straight and plain enough to hold: a clear grip section at least one hand-width long.
   - Shields show the painted face in main and the strap side in back. Summons and standing objects (cannon, drum, rock wall, cage) stand on their own base.
   - Left and right are true profiles; back is the true rear. For a flat symmetrical item the two side views may look alike, but generate each one, never mirror.
C. full/ sets (the hero with items, shown on the catalogue site) keep the brief's pose. An item that the brief says stands on the ground may do so in the full set only.

WHERE EVERYTHING GOES
art-source/asset-studio/<hero_id>/inputs/references/four_view_r001/
  full/main.png  left.png  back.png  right.png
  body/main.png  left.png  back.png  right.png
  items/<name>/main.png  left.png  back.png  right.png
  provenance.json, review/full_views.png, review/all_views.png, rejected/
PNG, square, at least 1024x1024, one pixel size per hero. Do not crop, mirror, upscale or repaint generated pixels afterwards.
Never overwrite or delete an existing saved view. If an existing saved view is wrong and must be replaced, save the new set in four_view_r002 with the same layout and say so in the run log.

DO NOT REDO — ALREADY BUILT IN 3D
- wc_vn_shieldbearer: finished (four_view_r004). Do not touch its folder.
- wc_vn_earthbreaker and wc_vn_tide_caller: full sets are finished and modelled. Do not regenerate them. Neither has a body or item set to make.
The designs of wc_vn_boar_rusher, wc_vn_hookjaw and wc_vn_hammerer in four_view_r001/full are accepted. Do not change those designs.

STEP 1 — FIX THE THREE WEAPON HEROES FIRST
Their four_view_r002/rejected/ folders hold good candidates that were rejected only for the background, which is no longer a defect. Use them as image references and complete the sets under four_view_r001/:
- wc_vn_boar_rusher: body/ — four candidates exist; regenerate them only as needed to meet rule A (open hands with separated fingers, arms clear of the fur cape). items/bone_club/ — front candidate exists; make left, back and right, grip end at the bottom.
- wc_vn_hookjaw: body/ — front candidate exists; make left, back and right with the same A-pose, open clawed hands, cloak hanging clear of the arms. items/chain_hook/ — front and left candidates exist; redo left as a true profile, make back and right.
- wc_vn_hammerer: body/ — front, left and back candidates exist; make right and fix the back so the hands match the front. items/war_hammer/ — front candidate exists but is drawn head-down: redraw the set with the grip end at the bottom and the head at the top, whole shaft visible.
You may copy a candidate unchanged into its final place if it already meets the rules; record that in provenance.json.

STEP 2 — FINISH EVERY FULL SET (all 40 heroes end with four full views)
Go through BRIEFS.md sections 02 to 40 in order. For each hero look at its folder first: skip a full set that already has four views; finish a partial one using its existing main.png as the image reference; start a missing one from its brief with the style anchor as the style reference.
State when this prompt was written:
- Full set complete: shieldbearer, boar_rusher, hookjaw, tide_caller, hammerer, earthbreaker, bearguard, bomber, ember_wisp.
- Front attempted but not accepted (best attempts are in rejected/ — start from them under the changed rules 3 and 4): grove_druid, prism_scholar, soul_jailer, chapel_healer.
- Not started: blood_drummer, siege_master, longbow_scout, moonblade, treant_caller, ironwall, rifleman, forge_king, jinxer, dartblower, bonechanter, foxclaw, wolf_caller, owl_seer, hellblade, shadow_fiend, pit_lord, bone_archer, curse_weaver, stitcher, necromancer, stone_shaper, storm_spirit, scaleguard, dawn_oracle, flame_regent, void_wyrm.
For each hero: generate main, look at it, check it against HERO_LOOKS.md; generate left, back and right each from its own prompt with this hero's main.png as the image reference; view the four side by side; regenerate what fails. Save review/full_views.png (main, left, right, back in one labelled row) and provenance.json.

STEP 3 — BODY AND ITEM SETS for every hero whose HERO_LOOKS.md entry lists them
Heroes with items (make body/ and every items/<name>/ set):
boar_rusher (bone_club), grove_druid (grove_staff), hookjaw (chain_hook), prism_scholar (prism_crystal), soul_jailer (soul_cage), chapel_healer (lantern_staff), siege_master (field_cannon, ramrod), longbow_scout (longbow), moonblade (crescent_blade), treant_caller (treant_summon), hammerer (war_hammer), ironwall (bolted_shield), rifleman (long_rifle), bomber (round_bomb), jinxer (bone_rattle), dartblower (blowpipe), blood_drummer (war_drum, drumstick), bonechanter (skull_staff), foxclaw (hand_claw), wolf_caller (hunting_horn, wolf_summon), owl_seer (crooked_staff, hex_critter), hellblade (flame_greatsword), pit_lord (fire_whip), bone_archer (rib_bow), curse_weaver (curse_doll, curse_needle), stitcher (giant_needle), necromancer (scythe, skeleton_summon), stone_shaper (rock_wall), dawn_oracle (sun_disc), flame_regent (flame_sceptre).
If HERO_LOOKS.md lists an item not named here, make it too; HERO_LOOKS.md is the authority for the list.
Make body/main.png by editing full/main.png: remove every item and put the hero in the rule-A pose. Then make body left, back and right from body/main.png. Make each item set from its prompts with full/main.png as the image reference so design, colours and materials match. For a pair of identical items (two blades, two shields, two drumsticks, two claws) one item set is enough.
Check body/ beside full/ (same design, nothing but the items and the pose changed) and each item's four views together. Save review/all_views.png with one labelled row per set and update provenance.json.

AFTER EVERY FIVE HEROES
Run:  .venv/Scripts/python.exe tools/vnext/sync_hero_art.py
Fix any FAIL line before continuing. Append one line per hero per step to production/hero-art/RUN_LOG.md: hero id, step, files saved, attempts, any defect still visible.

IF YOU RUN OUT OF QUOTA, TIME OR CONTEXT
Stop at the end of the current set, run the sync tool, update the run log, and tell me the last finished hero and the next one. I will paste this prompt again and you continue from the run log. Running out is the only acceptable reason for an unfinished roster.

AT THE END
1. Run the sync tool, then:  .venv/Scripts/python.exe -m unittest discover -s tests
   (test_blender_mcp_workflow already fails on this PC because PowerShell scripts are disabled; report it, do not fix it.)
2. Report one table with a row per hero: full views saved (must be 4), body views saved, item sets saved, total attempts, and every defect still visible. Then list any view you saved under rule 2 despite a defect. Show me every review sheet. Report only what you generated and looked at.

RULES
- Do not edit data/vnext/catalog.json, production/hero-art/hero_art.json, HERO_LOOKS.md, BRIEFS.md, VISUAL_STANDARD.md, any game source, or anything under game/, tools/ or art-source/asset-studio/*/inputs/meshy.
- Do not mark anything approved or accepted. I review every image myself.
- No Meshy upload, no 3D generation, no paid service other than the image generation asked for here, no deployment or site publishing, no git commit or push.
- Leave unrelated uncommitted changes alone; another session may be running Unreal.
```

## Notes for the owner

- Roughly 150 full-view images, 120 body images and about 150 item images remain, before retries.
- The open-hand rule (separated fingers, thumb apart) is there so later bodies can get real finger joints instead of the current "mitten" grip.
- Boar Rusher, Hookjaw and Hammerer are already in the game, built from the earlier candidates. When their new body and weapon sets exist, they can be rebuilt for better hands; that costs about 80 Meshy credits per hero.
- Item names in step 3 come from `hero_art.json` as of today. If you change a hero's items there, rerun `tools/vnext/build_hero_art_briefs.py` before pasting.

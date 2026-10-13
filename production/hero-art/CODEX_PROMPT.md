# Prompt for Codex — hero reference images

One prompt for the whole roster. Paste everything in the block below into Codex, opened in this repository root. It can be pasted again at any time: finished heroes are skipped and the run continues where it stopped.

```text
You are producing the 2D reference images for the Wonder Chess hero roster with your image generation tool (GPT Image). Do the whole roster in this one run, hero after hero, without waiting for me between heroes. The images are later uploaded to Meshy as its Main / Left / Back / Right inputs, so the four views of one subject must show exactly the same design.

STYLE ANCHOR
The owner has chosen the style. The anchor image is:
art-source/asset-studio/wc_vn_shieldbearer/inputs/references/four_view_r004/with_shield/main.png
Open it and look at it before you start. Give it to the image tool as a style reference for every hero's first image so the roster looks like one game. Copy its rendering style, level of realism and detail, lighting, framing and background only. Never copy the Shieldbearer's armour, colours, sun emblem or body shape onto another hero.

READ FIRST, IN THIS ORDER
1. AGENTS.md — the section "Owner roster rework — 2026-10-03".
2. production/hero-art/VISUAL_STANDARD.md — the look, the three kinds of set, the pose, the four views and the consistency checks. Follow it exactly.
3. production/hero-art/HERO_LOOKS.md — what every hero looks like, the shared look of each race, and the list of sets and image counts per hero.
4. production/hero-art/BRIEFS.md — per hero: the folder and the ready prompt for every single image. Use these prompts as written; you may append a short correction when a retry needs one.

WHERE EVERYTHING GOES
For each hero, the folder is art-source/asset-studio/<hero_id>/inputs/references/four_view_r001/ and inside it:
  full/main.png  full/left.png  full/back.png  full/right.png      the complete hero with items
  body/main.png  body/left.png  body/back.png  body/right.png      the same hero without items
  items/<name>/main.png  left.png  back.png  right.png             one item or summon alone
  provenance.json                                                  see "Records"
  review/full_views.png and review/all_views.png                   review sheets
  rejected/                                                        failed attempts you kept
The exact paths are in BRIEFS.md. PNG, square, at least 1024x1024, the same pixel size for every image of one hero. Keep the generated pixels unchanged; do not crop, mirror, upscale or repaint them afterwards.

WHAT IS ALREADY DONE (resume rule)
Before each hero, look at its folder.
- If full/ already has all four views, pass 1 is done for that hero: skip it. The same applies to a body/ or items/<name>/ folder in pass 2.
- If a set has one to three views, finish it: keep the existing files and generate only the missing views, using the existing main.png as the image reference.
- Never overwrite or delete an existing image. Shieldbearer (four_view_r004) is finished: do not touch anything under art-source/asset-studio/wc_vn_shieldbearer.

PASS 1 — the four full views of all 39 remaining heroes (156 images)
Go through the heroes in the order of BRIEFS.md, sections 02 to 40. For each hero:
1. Generate full/main.png from its prompt with the style anchor as the style reference. Look at the result yourself. Check it against HERO_LOOKS.md (every listed part present, nothing added, right hand and left hand correct — left and right are the hero's own, so an item in the hero's right hand is on the viewer's left) and against the anchor (same realism, materials, light, background; not cartoon or toy). Regenerate until it passes, up to three attempts.
2. Generate full/left.png, full/back.png and full/right.png, each from its own prompt with this hero's full/main.png as the image reference, so design, colours, proportions, pose and scale stay identical. The left view faces the left edge of the image; the right view faces the right edge. Generate each side separately; never mirror one to make the other, because the two sides of most heroes differ. Use the "Seen from behind" sentence in the prompt for the back view instead of inventing the back.
3. View all four images side by side and run the six consistency checks in VISUAL_STANDARD.md. Regenerate any view that fails, up to three attempts per file.
4. If a file still fails after three attempts, move the best attempt to rejected/ with the defect in its file name, write the defect in the run log, leave that view missing, and go on to the next hero. Do not save a failed image as a view.
5. Save the four files, write provenance.json, and save review/full_views.png: the four views in one row in the order main, left, right, back, each labelled.
6. After every five heroes, run:  .venv/Scripts/python.exe tools/vnext/sync_hero_art.py
   It validates the files and writes 768 px copies of the full views to web/catalogue/art/<hero_id>/ for the catalogue site. "PENDING" lines for body and item sets are expected during pass 1. Fix any "FAIL" line before continuing.

PASS 2 — body and item sets (264 images), only after pass 1 has been attempted for every hero
Same hero order. Skip heroes whose HERO_LOOKS.md entry lists only "full". For each remaining hero whose full/ set is complete:
1. body/: make each view by editing the matching full/ view (body/main.png from full/main.png, and so on): remove only the held, strapped, standing or floating items named in the brief and reveal the hand, arm and body behind them, empty and relaxed. Everything worn stays exactly the same, at the same position and scale. If the brief's separate items are not in the full image at all and the hands are already empty (for example a summon), copy the four full views into body/ unchanged and record them as copies.
2. items/<name>/: generate the four views of each item or summon alone from its prompts, with full/main.png as the image reference so it has the same design, colours and materials. Main shows its front face, back its rear or inner side.
3. Check body/ beside full/ view by view, and each item set's four views together. Same three-attempt limit and the same handling of failures as pass 1.
4. Update provenance.json and save review/all_views.png: one labelled row per set (full, body, each item).

RECORDS
- provenance.json per hero: hero_id, date, the image model you used (write null for anything the tool does not tell you — do not invent values), and for every file: the exact prompt, the image references used, the number of attempts, and whether it is a generation, an edit or a copy. Add "owner_review": "open".
- Run log: production/hero-art/RUN_LOG.md. Append one line per hero per pass as you finish it: hero id, pass, files saved, attempts, any defect you can still see. This is what you read first when the prompt is pasted again.

WHEN YOU MUST STOP EARLY
If you run out of image quota, time or context, stop at the end of the current hero — never in the middle of a set if you can avoid it — run the sync tool, update the run log, and tell me the last finished hero. I will paste this prompt again to continue.

AT THE END
1. Run:  .venv/Scripts/python.exe tools/vnext/sync_hero_art.py
2. Run:  .venv/Scripts/python.exe -m unittest discover -s tests
   One Blender launcher test (test_blender_mcp_workflow) already fails on this PC because PowerShell script execution is disabled. Report it; do not fix it or change the policy.
3. Report in a table, per hero: sets saved, images saved, total attempts, and every defect still visible. List separately the heroes with a missing or rejected view. Be exact: report only what you actually generated and actually looked at.

RULES
- Do not edit data/vnext/catalog.json, production/hero-art/hero_art.json, HERO_LOOKS.md, BRIEFS.md, VISUAL_STANDARD.md or any game source. If a brief contradicts itself or cannot be drawn as written, skip that hero, note why in the run log and the report, and continue with the next.
- Do not mark anything approved or accepted anywhere. Owner review stays "open"; I review every image myself. Passing your own checks is not approval.
- No Meshy upload, no 3D generation, no paid service other than the image generation I asked for here, no deployment or site publishing, no git commit or push.
- Leave unrelated uncommitted changes alone.
```

## Notes for the owner

- The run is 420 images: 156 in pass 1 (what the catalogue site shows) and 264 in pass 2 (bodies, items and summons for Meshy). [HERO_LOOKS.md](HERO_LOOKS.md) lists the count per hero.
- To review the looks before the body and item sets are made, delete the "PASS 2" block before pasting; paste the full prompt later to add them.
- To redo one hero after review, change its description in `hero_art.json`, run `tools/vnext/build_hero_art_briefs.py`, and ask Codex for that hero in a new `four_view_r002` folder. Earlier sets are kept.
- After a run, `tools/vnext/publish_site.py` pushes the new images to the public catalogue site.

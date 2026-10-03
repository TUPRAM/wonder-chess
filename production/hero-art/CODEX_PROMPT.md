# Prompt for Codex — hero reference images

Paste everything in the block below into Codex, opened in this repository root. Change the hero list on the last line when you want a different batch.

```text
You are producing 2D reference images for Wonder Chess heroes with your image generation tool (GPT Image). These images are later uploaded to Meshy as its Main / Left / Back / Right inputs, so the four views of one hero must show exactly the same design.

Read first, in this order:
1. AGENTS.md — the section "Owner roster rework — 2026-10-03".
2. production/hero-art/VISUAL_STANDARD.md — the style and view rules. Follow them exactly.
3. production/hero-art/BRIEFS.md — one section per hero with its folder, colours, design description, a ready prompt for each view, and its accessory list.

For each hero in the batch, in order:
1. Generate main.png from the hero's "main.png" prompt. Look at the result. If it breaks the visual standard (too much detail or texture, extra parts, wrong colours, cropped, text, scenery), regenerate before continuing.
2. Generate left.png, back.png and right.png using main.png as the image reference together with that view's prompt, so the design, colours, proportions and pose stay identical. The left view faces the left edge of the image; the right view faces the right edge. Never mirror one side view to make the other.
3. Generate each accessory listed for the hero, using main.png as the style reference, one item per image.
4. Run the five consistency checks in VISUAL_STANDARD.md by actually viewing all four images side by side. Regenerate any view that fails. If two attempts at the same view still fail, stop that hero, keep the best attempt in a "rejected" subfolder, and report the defect instead of saving it as a view.
5. Save the files as PNG, square, at least 1024x1024, all four views the same size, exactly here:
   art-source/asset-studio/<hero_id>/inputs/references/four_view_r002/main.png
   art-source/asset-studio/<hero_id>/inputs/references/four_view_r002/left.png
   art-source/asset-studio/<hero_id>/inputs/references/four_view_r002/back.png
   art-source/asset-studio/<hero_id>/inputs/references/four_view_r002/right.png
   art-source/asset-studio/<hero_id>/inputs/references/four_view_r002/accessories/<name>.png
6. In the same folder write provenance.json with: hero_id, date, the image model you used, the exact prompt used for every file, which file was used as the image reference, and the number of attempts per file. Do not invent values you do not know.

After the batch:
1. Run:  .venv/Scripts/python.exe tools/vnext/sync_hero_art.py
   It validates the files, writes 768 px copies to web/catalogue/art/<hero_id>/, updates production/hero-art/status.json and regenerates web/catalogue/data/catalogue.json. Fix anything it reports and run it again.
2. Run:  .venv/Scripts/python.exe -m unittest discover -s tests
3. Report, per hero: the files saved, attempts used, and any remaining visible defect. Show me the four views of each hero.

Rules:
- Do not edit data/vnext/catalog.json, production/hero-art/hero_art.json, BRIEFS.md or any game source. If a brief is unclear or wrong, stop and tell me.
- Do not overwrite an existing four_view_r002 set. If one exists, stop and ask; a redo goes in four_view_r003.
- Do not mark anything approved. In status.json the owner review stays "open"; I review the images myself.
- No Meshy upload, no 3D generation, no paid service other than the image generation I asked for, no deployment, no git push.
- Leave unrelated uncommitted changes alone.

This is the second attempt at the style. The first attempt (visual standard version 1, folder four_view_r001) was judged too cartoonish and toy-like; do not use any r001 image as a reference. Follow version 2 of the visual standard: a stylized hand-painted fantasy hero with believable materials.

Batch: wc_vn_shieldbearer only. Stop after this one hero so I can review the style before you continue.
```

## Later batches

After the Shieldbearer set is accepted, replace the last line. Suggested order — the heroes already in the game first:

1. `wc_vn_boar_rusher, wc_vn_grove_druid, wc_vn_hookjaw, wc_vn_prism_scholar, wc_vn_tide_caller, wc_vn_soul_jailer`
2. `wc_vn_chapel_healer, wc_vn_hammerer, wc_vn_earthbreaker, wc_vn_bearguard, wc_vn_bomber, wc_vn_ember_wisp, wc_vn_blood_drummer`
3. The remaining 26 planned heroes, six or seven at a time, in the order of `BRIEFS.md`.

For later batches add this line to the prompt: "Use art-source/asset-studio/wc_vn_shieldbearer/inputs/references/four_view_r002/main.png as an additional style reference for every hero, so the whole roster shares one look."

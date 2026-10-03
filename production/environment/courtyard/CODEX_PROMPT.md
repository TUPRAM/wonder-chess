# Prompt for Codex — courtyard reference images

Paste everything in the block below into Codex, opened in this repository root.

```text
You are producing 2D reference images and flat textures for the Wonder Chess board environment, a stone castle courtyard, with your image generation tool (GPT Image). The 3D pieces are later uploaded to Meshy as Main / Left / Back / Right inputs, so the four views of one piece must show exactly the same object.

Read first:
1. production/environment/courtyard/BRIEFS.md — the style, every piece, its folder and its requirements. Follow it exactly.
2. production/hero-art/VISUAL_STANDARD.md — only the sections on the four views and the camera, which apply here too.

Style reference image for everything you generate, so the environment matches the heroes:
art-source/asset-studio/wc_vn_shieldbearer/inputs/references/four_view_r004/with_shield/main.png
Copy its rendering style, realism and lighting only. Never put a character in an environment image.

3D pieces, in this order: wall_section, round_tower, gatehouse, wall_banner, brazier, yard_props. For each one:
1. Generate main.png (front view) from the brief. Look at it. If it breaks the brief, regenerate before continuing.
2. Generate left.png, back.png and right.png using main.png as the image reference, so shape, proportions, materials and colours stay identical. Never mirror one side view to make the other.
3. View the four images side by side and check: same object, same scale, same baseline, plain light-grey background, nothing cropped, no text, no character. For wall_section and gatehouse also check that the left and right ends are flat cut faces of the same height and thickness. Regenerate any view that fails. After three failed attempts at one view, keep the best attempt in a "rejected" subfolder, stop that piece and report the defect.
4. Save as PNG, square, at least 1024x1024, all four the same size, at:
   art-source/asset-studio/wc_env_courtyard/inputs/references/<piece>_r001/main.png  (and left.png, back.png, right.png)
5. Save a review sheet of the four views at <piece>_r001/review/all_views.png and a provenance.json with the date, the image model, the exact prompt for every file, which file was used as the image reference, and the attempts per file. Do not invent values you do not know.

Flat images, saved to art-source/asset-studio/wc_env_courtyard/inputs/textures_r001/ :
flagstone_tile.png, board_tile_light.png, board_tile_dark.png, sky_backdrop.png — each exactly as its row in BRIEFS.md describes. For flagstone_tile.png, check the seams by viewing a 2x2 tiling of the image and regenerate if a seam shows. Save that 2x2 check as review/flagstone_tiling_check.png. Write one provenance.json for the folder.

When finished, report per piece: files saved, attempts used and any remaining visible defect, and show me every review sheet.

Rules:
- Do not edit any game source, data/vnext/catalog.json, or anything under production/hero-art or art-source/asset-studio/wc_vn_*.
- Do not overwrite an existing set; a redo goes in <piece>_r002.
- Do not mark anything approved. I review the images myself.
- No Meshy upload, no 3D generation, no paid service other than the image generation I asked for, no deployment, no git commit or push.
- Another chat may be running Unreal or editing hero art. Leave unrelated uncommitted changes alone.
```

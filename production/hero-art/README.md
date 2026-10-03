# Hero art — reference images

How the 2D reference images for the race/class roster are described, generated, stored and shown. The owner chose GPT Image (run by Codex) for the references and four views per hero so that Meshy receives a consistent Main / Left / Back / Right set.

| File | Purpose |
|---|---|
| [VISUAL_STANDARD.md](VISUAL_STANDARD.md) | The simple, readable look and the four-view rules every image follows |
| [hero_art.json](hero_art.json) | Art description per hero: proportions, three colours, features, hands, accessories. Edit here |
| [BRIEFS.md](BRIEFS.md) | Generated: per hero, the folder, file names and a ready prompt for each view |
| [CODEX_PROMPT.md](CODEX_PROMPT.md) | The prompt to paste into Codex |
| `status.json` | Written by the sync tool: which heroes have a complete set, file hashes, owner review state |

## Where images live

```text
art-source/asset-studio/<hero_id>/inputs/references/four_view_r002/
  main.png  left.png  back.png  right.png      original generated views (kept unchanged)
  accessories/<name>.png                       weapon, held item or summon, one per image
  provenance.json                              model, prompts, reference image, attempts
web/catalogue/art/<hero_id>/
  main.png  left.png  back.png  right.png      768 px copies for the catalogue site (made by the tool)
```

`<hero_id>` is the catalogue ID, for example `wc_vn_shieldbearer`. A redo is a new folder, `four_view_r003`; earlier sets are kept.

## Commands

```powershell
& .venv/Scripts/python.exe tools/vnext/build_hero_art_briefs.py      # after editing hero_art.json or the catalogue
& .venv/Scripts/python.exe tools/vnext/sync_hero_art.py --check      # report only
& .venv/Scripts/python.exe tools/vnext/sync_hero_art.py              # publish web copies, update status and site data
```

## Status and limits

- The sync tool checks file facts only (PNG, square, size, all four present). It cannot judge likeness or consistency; that is a human review.
- `owner_review` starts as `open` and returns to `open` whenever an image changes. Only the owner sets it to accepted.
- These images are references. A set being saved does not start Meshy generation or any spending.
- The live site at https://wonder-chess.vercel.app shows the images only after it is redeployed.

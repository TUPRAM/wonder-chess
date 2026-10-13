# Hero art — reference images

How the 2D reference images for the race/class roster are described, generated, stored and shown. The owner generates them with GPT Image through Codex, four views per subject, so that Meshy receives a consistent Main / Left / Back / Right set.

| File | Purpose |
|---|---|
| [VISUAL_STANDARD.md](VISUAL_STANDARD.md) | The owner-chosen look (anchored on Shieldbearer r004), the three kinds of set and the view rules |
| [hero_art.json](hero_art.json) | Art description per hero and per race: proportions, colours, features, hands, back, items. Edit here |
| [HERO_LOOKS.md](HERO_LOOKS.md) | Generated: the readable description of every hero's look, and the image count |
| [BRIEFS.md](BRIEFS.md) | Generated: per hero, the folder, file names and a ready prompt for every image |
| [CODEX_PROMPT.md](CODEX_PROMPT.md) | The single prompt to paste into Codex for the whole roster; it can be pasted again to continue |
| `RUN_LOG.md` | Written by Codex: one line per hero per pass |
| `status.json` | Written by the sync tool: which heroes have a complete set, file hashes, owner review state |

## Where images live

```text
art-source/asset-studio/<hero_id>/inputs/references/four_view_r001/
  full/   main.png left.png back.png right.png     complete hero with items (shown on the site)
  body/   main.png left.png back.png right.png     same hero without items (Meshy body and rig)
  items/<name>/  main.png left.png back.png right.png   one item alone (separate Meshy model)
  provenance.json                                   model, prompts, reference images, attempts
  review/full_views.png, review/all_views.png       review sheets
art-source/asset-studio/<hero_id>/inputs/meshy/<job>/   Meshy job definition, receipts and downloads
web/catalogue/art/<hero_id>/                        transparent WebP copies of full/ for the site: 768 px and a 384 px -thumb (made by the tool)
```

`<hero_id>` is the catalogue ID, for example `wc_vn_boar_rusher`. Shieldbearer's accepted-direction set is `four_view_r004` with the older subfolder names `with_shield/`, `without_shield/` and `shield_only/`; `hero_art.json` records that mapping. A redo is a new folder (`four_view_r002`); earlier sets are kept.

## Commands

```powershell
& .venv/Scripts/python.exe tools/vnext/build_hero_art_briefs.py      # after editing hero_art.json or the catalogue
& .venv/Scripts/python.exe tools/vnext/sync_hero_art.py --check      # report only
& .venv/Scripts/python.exe tools/vnext/sync_hero_art.py              # publish web copies, update status and site data
& .venv/Scripts/python.exe tools/vnext/publish_site.py               # push the site to the `site` branch for Vercel
& .venv/Scripts/python.exe tools/production/meshy_job.py balance     # Meshy: balance, submit, status, download
```

## Status and limits

- The sync tool checks file facts only (PNG, square, size, all views present). It cannot judge likeness or consistency; that is a human review.
- A hero is published to the site as soon as its four `full/` views exist; missing `body/` and `items/` sets are listed as pending in `status.json`.
- `owner_review` starts as `open` and returns to `open` whenever an image changes. Only the owner sets it to accepted.
- Saving a reference set does not start Meshy generation or any spending. Each Meshy job needs the owner's go-ahead and a credit ceiling, recorded in its `job.json`.
- The Meshy API key is stored encrypted outside the project by `Store Meshy API Key.cmd`.

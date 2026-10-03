# Stone castle courtyard — asset briefs

**Version 1 — 3 October 2026.** The owner chose a stone castle courtyard for the board environment and asked for these briefs. Nothing here is generated or approved yet.

The courtyard currently in the game is a blockout made of plain boxes and cylinders (`AWCVNextLab::BuildCourtyard`). These assets replace those shapes one for one, so each brief gives the size the blockout uses.

## Style

Same look as the heroes: painterly semi-realistic fantasy, worn believable materials, limited palette. The style anchor is the Shieldbearer:

`art-source/asset-studio/wc_vn_shieldbearer/inputs/references/four_view_r004/with_shield/main.png`

- **Stone:** warm grey limestone blocks, large and clearly cut, with worn edges, a few chips and darker mortar lines. Slight moss low down. No tiny cracks or noisy texture.
- **Accent colours:** deep royal blue `#24468F` cloth and aged brass `#B8923A`, matching the Shieldbearer.
- **Roofs and wood:** dark slate-red roof tiles `#6B2F28`, dark oak beams.
- **Mood:** late-afternoon sun, calm, a lived-in castle. Not ruined, not gothic-horror, not cartoon.
- The environment must stay quieter than the heroes: lower contrast and less saturated than the characters standing in front of it.

## Reference images (for Codex with GPT Image)

Every 3D piece gets four views, the same as hero items: `main.png` (front), `left.png`, `back.png`, `right.png`. One piece alone, centred, whole piece in frame, straight-on orthographic-style camera, even soft light, plain light-grey background `#E6E6E6`, no ground shadow, no scenery, no characters, no text. PNG, square, 1024×1024 or larger.

Folder for each piece: `art-source/asset-studio/wc_env_courtyard/inputs/references/<piece>_r001/`

| Piece | Folder name | What it is | Size in game | Key requirements |
|---|---|---|---|---|
| Wall section | `wall_section` | One straight length of curtain wall with battlements | 5.2 m long, 9 m tall, 2.6 m thick | **Must tile:** the left and right ends are flat, identical cut faces so sections join into a long wall. A stone plinth along the base, a walkway and five merlons on top. No door or window. |
| Round tower | `round_tower` | A corner tower | 6.4 m wide, 12 m tall plus roof | Round stone drum, a ring of battlements, a conical slate roof with a small brass finial. Two arrow slits. Looks the same from all four sides apart from the slits. |
| Gatehouse | `gatehouse` | The gate in the far wall | 8.4 m wide, 10 m tall | A block that stands proud of the wall, a tall round arch with a closed iron portcullis, a blue banner with a brass sun above the arch, battlements on top. Left and right ends are flat cut faces so wall sections join it. |
| Banner | `wall_banner` | A long cloth banner on a brass rod | 1.9 m wide, 4.6 m tall | Deep blue cloth, brass sun emblem, brass trim along the forked bottom edge, a plain brass rod at the top. Hangs flat; back is plain blue. |
| Brazier | `brazier` | A standing fire bowl | 1.1 m wide, 2 m tall | Dark iron tripod stand, wide iron bowl with glowing coals and a small flame. The glow is the only bright element. |
| Yard props | `yard_props` | One group for dressing the yard edges | Fits a 3 m square | Two barrels, one crate, a wooden weapon rack with two spears and a round shield, standing together on nothing. Oak and iron, a little blue cloth. |

## Flat images (for Codex with GPT Image; not sent to Meshy)

Folder: `art-source/asset-studio/wc_env_courtyard/inputs/textures_r001/`

| File | What it is | Requirements |
|---|---|---|
| `flagstone_tile.png` | Yard paving seen straight down | **Seamless on all four edges.** Large irregular rectangular flagstones, warm grey, dark mortar, a little moss in a few joints. Even light, no shadows, no perspective. 2048×2048. |
| `board_tile_light.png` | One light board square seen straight down | A single square stone slab filling the image edge to edge, pale warm limestone, smooth-worn, faint chisel marks. Even light. 1024×1024. |
| `board_tile_dark.png` | One dark board square seen straight down | The same slab in dark slate grey. Must read clearly darker than the light square. 1024×1024. |
| `sky_backdrop.png` | The sky behind the walls | A wide late-afternoon sky: soft blue fading to warm near the horizon, a few calm clouds, distant hills and one far tower on the horizon line. No sun disc, nothing in the lower third but haze. 2048×1024. |

## Meshy plan (not started; needs the owner's go-ahead and a credit ceiling)

Each 3D piece: one multi-image job from its four views on `meshy-7.1`, PBR textures at 4K, triangles. No rigging; these are static.

| Piece | Target triangles | Credits |
|---|---|---|
| Wall section | 6,000 | 30 |
| Round tower | 8,000 | 30 |
| Gatehouse | 10,000 | 30 |
| Banner | 1,500 | 30 |
| Brazier | 2,500 | 30 |
| Yard props | 6,000 | 30 |
| **Total** | | **180** |

The wall section is the risk: generated models rarely tile cleanly. If its ends do not join, the fallback is to keep the simple wall shape already in the game and apply a generated stone texture to it.

## Review

The owner reviews each image set before any Meshy job, and each model in the game before it replaces a blockout shape. Nothing here approves itself.

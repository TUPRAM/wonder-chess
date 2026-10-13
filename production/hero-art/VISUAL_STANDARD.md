# Wonder Chess hero visual standard

**Version 3 — 3 October 2026.** The owner chose the Shieldbearer `four_view_r004` set as the direction ("I like this direction more"). That set is the **style anchor** for the whole roster:

`art-source/asset-studio/wc_vn_shieldbearer/inputs/references/four_view_r004/with_shield/main.png`

Earlier versions are superseded: version 1 (flat toy look) was rejected as too cartoonish, and version 2 (stylized hand-painted) was replaced by the more realistic r004 look.

## The look

- **Painterly semi-realistic fantasy**, rendered like a clean 3D character turnaround.
- **Realistic heroic proportions:** a medium humanoid is about 5.5 heads tall; goblins and dwarves about 4.5; large heroes 6 to 7. Each brief gives the value.
- **Believable worn materials:** steel plate with rivets, dents and scratches; chainmail; stitched leather; weathered cloth with trim; bone, fur, scales where the hero has them.
- **Limited dominant palette:** the brief's three colours dominate, with neutral metal, leather and skin tones beside them.
- **Strong silhouette:** one signature feature (helmet, horns, weapon, tail) carries the identity. Only the parts listed in the brief.
- **Not** cartoon, chibi or toy. No text, no logos, no glow except where the brief names one.

## Three kinds of set

Every set is four views: `main.png`, `left.png`, `back.png`, `right.png`.

| Subfolder | Shows | Used for |
|---|---|---|
| `full/` | The complete hero with every held, strapped or floating item | The catalogue site and overall review |
| `body/` | The same hero with empty hands and no item | Meshy body model and rig |
| `items/<name>/` | One item alone (weapon, shield, summon) | A separate Meshy model attached in Unreal |

A hero with no separate item needs only `full/`. Shieldbearer's existing r004 set uses the older names `with_shield/`, `without_shield/` and `shield_only/`.

## Pose and camera (identical within a set)

- Standing straight in a relaxed **A-pose**: arms slightly away from the body, legs slightly apart, looking straight ahead.
- Held items stay in the stated hand and position, never covering the body or face.
- Whole subject in frame with margin on every side; nothing cropped. Same baseline and same scale in every view.
- Straight-on orthographic-style camera, even soft studio light, plain light-grey background `#E6E6E6`. No ground shadow, scenery, effects, motion blur or depth of field.

## The four views

| File | Camera | The subject faces |
|---|---|---|
| `main.png` | Front | The viewer |
| `left.png` | Looking at the subject's own left side | The viewer's **left** edge of the image |
| `back.png` | Rear | Away from the viewer |
| `right.png` | Looking at the subject's own right side | The viewer's **right** edge of the image |

Left and right are the hero's own. An item in the hero's right hand appears on the viewer's left in `main.png`. Never mirror one side view to make the other.

## Consistency checks before a set is saved

1. Same part inventory in all four views; nothing appears, disappears, changes hand or changes position.
2. `body/` matches `full/` exactly apart from the removed items.
3. Same colours, materials, proportions, pose, scale and baseline.
4. Side views face the correct edge.
5. Plain background, no text, nothing cropped.
6. Side by side with the Shieldbearer anchor, the hero looks like it belongs to the same game.

A set that fails any check is regenerated, not saved.

## Format

PNG, square, 1024×1024 or larger, the same size for every view of one hero.

This standard does not approve any image; the owner reviews each set.

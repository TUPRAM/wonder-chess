# Wonder Chess hero visual standard

**Version 2 — 3 October 2026.** Version 1 asked for a toy-like, flat, three-colour look. The first Shieldbearer attempt came out as a vinyl toy, and the owner judged it too cartoonish and not like a fantasy-world hero. Version 2 keeps the readability goal and restores the fantasy.

The target is a **stylized hand-painted fantasy hero**, the kind seen in auto-battlers and stylized fantasy strategy games: clear at board size, but a believable warrior, mage or monster with real equipment.

## What changed from version 1

| | Version 1 (rejected) | Version 2 |
|---|---|---|
| Proportions | About 3 heads tall, huge head | Heroic: medium heroes about 4 heads tall; goblins and dwarves about 3.5; large heroes up to 5. Each brief gives the value |
| Surfaces | Flat colour, no texture, matte | Hand-painted materials: worn metal with edge highlights, stitched leather, heavy cloth with broad folds |
| Detail | None | Medium-sized detail only: plate edges, rivets, straps, trim, a few dents or scratches |
| Colour | Exactly three flat colours | Three dominant colours from the brief, plus neutral leather, metal and skin tones; clear light-and-dark contrast |
| Tone | Toy, calm face | Grounded fantasy; serious or characterful expression |

## What stays

- **Readable silhouette:** recognisable as a solid black shape. One signature feature (helmet, horns, weapon, tail) carries the identity. Shoulders, hands and weapon are slightly exaggerated.
- **No micro detail:** no noisy texture, engraving, fabric weave, fur strands or scale-by-scale rendering. If a detail would vanish at board size, leave it out.
- **Only the parts in the brief.** No extra pouches, spikes or jewellery.
- **Not photorealistic**, no text, no logos, no glow except where the brief names one.

## Pose and camera (identical in all four views)

- Neutral **A-pose**: standing straight, arms about 35° away from the body, legs slightly apart, looking straight ahead.
- Held items stay in the stated hand and position, never covering the body or face.
- Full body in frame with margin on every side; nothing cropped. Feet (or hover base) on the same baseline in every view. Same scale in every view.
- Straight-on camera at chest height with very little perspective.
- Even, soft light. Plain flat light-grey background `#E6E6E6`. No ground shadow shapes, scenery, effects, particles, motion blur or depth of field.

## The four views

| File | Camera | The hero faces |
|---|---|---|
| `main.png` | Front | The viewer |
| `left.png` | Looking at the hero's own left side | The viewer's **left** edge of the image |
| `back.png` | Rear | Away from the viewer |
| `right.png` | Looking at the hero's own right side | The viewer's **right** edge of the image |

Left and right are the hero's own left and right. An item in the hero's right hand appears on the viewer's left in `main.png`, is nearest the camera in `right.png`, and is mostly hidden behind the body in `left.png`. Never mirror one side view to make the other.

## Consistency checks before a set is saved

1. Same part inventory in all four views; nothing appears, disappears, changes hand or changes position.
2. Same colours, materials and proportions.
3. Same pose, scale and baseline.
4. Side views face the correct edge.
5. Plain background, no text, nothing cropped.

A set that fails any check is regenerated, not saved.

## Format and folders

- PNG, square, 1024×1024 or larger, the same size for all four views of one hero.
- Version 2 images are saved in `four_view_r002`. The `four_view_r001` folders hold version 1 attempts and are kept unchanged.
- Accessory images use the same style, background and lighting, one item per image, centred.

This standard does not approve any image; the owner reviews each set.

# Eighty-four hero/clip review matrix

Current review: revision-6 sources and animation exports, actual Unreal 5.7.4 game-mode captures from 2026-09-06 at 15:01–15:02 local time. Each cell marked **R** means the hero and clip were visibly reviewed at 20%, 52% and 88% of that clip in the actual new engine screenshots. At those positions, the model was present with coherent scale, orientation, skinning and attached equipment. This is a bounded sampled pose pass, not continuous playback, precise hand intersection, gameplay timing or final hero acceptance.

The durable original screenshots are in `unreal-art-review-revision6/`. `unreal-visual-review-revision6-evidence.json` records their hashes and verifies that the 36 revised source animation files still match the actual import records. Detailed per-clip/per-hero observations and remaining limits are in `unreal-visual-review-revision6.md`. Earlier failed-readability evidence remains in `unreal-art-review-candidate4/` and `unreal-visual-review.md`.

| Canonical hero | Idle | Move | Attack | Active | Hit | Defeat | Victory |
|---|---|---|---|---|---|---|---|
| wc_u_human_guardian — Ada Brightshield | R | R | R | R | R | R | R |
| wc_u_human_priest — Mira Dawnwell | R | R | R | R | R | R | R |
| wc_u_human_mage — Rowan Emberwick | R | R | R | R | R | R | R |
| wc_u_elf_ranger — Liora Leafstep | R | R | R | R | R | R | R |
| wc_u_elf_priest — Elin Moonsong | R | R | R | R | R | R | R |
| wc_u_elf_rogue — Sylas Duskrun | R | R | R | R | R | R | R |
| wc_u_dwarf_guardian — Borin Stonebell | R | R | R | R | R | R | R |
| wc_u_dwarf_ranger — Tessa Brassbolt | R | R | R | R | R | R | R |
| wc_u_dwarf_warrior — Dagna Anvilheart | R | R | R | R | R | R | R |
| wc_u_orc_warrior — Rok Sunward | R | R | R | R | R | R | R |
| wc_u_orc_mage — Zura Stormcall | R | R | R | R | R | R | R |
| wc_u_orc_rogue — Kesh Quickwind | R | R | R | R | R | R | R |

| Clip | Actual frame indices | Review emphasis |
|---|---|---|
| Idle | 00, 01, 02 | Planted silhouette, family scale, material grouping |
| Move | 03, 04, 05 | Alternating support, coherent limbs and held equipment |
| Attack | 06, 07, 08 | Weapon/hand movement, no gross deformation or detached equipment |
| Active | 09, 10, 11 | Distinct shield/forward/ranged/caster stances and equipment paths |
| Hit | 12, 13, 14 | Broader torso/shoulder recoil than the earlier capture |
| Defeat | 15, 16, 17 | Supported terminal crouch with lowered equipment; Zura's shallower coat-safe variant |
| Victory | 18, 19, 20 | Equipment raised away from faces and stronger caster/ranger gestures |

All 84 cells were reviewed. The three samples produce 252 visible hero/pose instances, not 252 independent tests. The source revision also passed full-mesh floor checks on every frame of the 36 changed clips and the existing seven-clip numerical motion audit; numerical coverage is separately documented in `animation-refinement-production.json`.

This matrix closes the requirement to examine each imported hero/clip pair at this checkpoint. Final acceptance stays open for current crowded 1080p/720p gameplay, continuous moving-foot/LOD behavior, actual skill release cues and packaged rendering. Angular elbow creases and small contact detail remain minor polish limits; intentional faceting alone is not a failing criterion. `hero-readiness-matrix.json` keeps these stage distinctions explicit.

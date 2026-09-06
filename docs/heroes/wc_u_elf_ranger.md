# Liora Leafstep — The Canopy Scout

**Elf · Ranger · Ranged damage · ALPHA**

Stable identity: `wc_u_elf_ranger`. Cost: **1 gold**. Rarity label: **Common**, separate from star level. Status: designed, not modeled or implemented by this kit. All combat values are provisional prototype inputs.

## Character and world

Liora mapped the canopy paths above Thistlewood’s old trade road. She believes visitors protect a forest better when they understand it, so she guides traders rather than turning them away. Elin persuaded her to enter the trials, where she studies how to keep a ranged ally safe without simply hiding it in a corner.

Home region: `thistlewood`. Affiliation: `greenward_circle`. Neither supplies a hidden third synergy. Proper names are original proposed fiction, not trademark-clearance claims.

## Appearance and art direction

Authored standing height: **1.88 m**, excluding raised equipment. Rig family: `humanoid_slender`. One logical tile at every star. All characters are adults, fully clothed and presented as non-graphic heroic fantasy.

### Silhouette and proportions

A light forward-leaning profile, long crescent bow and three short leaflike cloak panels. The cloak stops above the knees, revealing long, narrow leg shapes.

### Face, hair and expression

Golden-brown skin, gray-green eyes, swept-back pointed ears and pale brown hair tied into a short fan. Her gaze is alert rather than severe.

### Costume construction

Moss fabric over fitted leather shoulder protection, a single pale scarf and flexible boots. The bow-side shoulder stays clear; no oversized pauldron blocks the draw.

### Color palette

Moss #647A4B; pale mint #B7CBB0; chestnut #765641; warm linen #DACCAB.

### Equipment and magical focus

A stylized crescent bow with broad flattened limbs and a slim back quiver. The bowstring is simplified geometry that can be hidden at distant LODs.

### Three low-resolution identifiers

Crescent bow, three separated cloak panels, and sideways archery stance.

### Materials and surface detail

Matte woven cloth, satin-finished wood and leathery boots. Leaf motifs are broad seam shapes, not transparency cutouts.

### Back and side-view constraints

Quiver sits diagonally and avoids the shoulder draw arc. Cloak panels spread enough to read as three shapes without requiring cloth bones beyond a small secondary chain.

## Combat statistics — without traits or temporary effects

| Property | One star | Two stars | Three stars |
|---|---:|---:|---:|
| Health | 670 | 1,206 | 2,170.8 |
| Basic attack damage | 60 | 108 | 194.4 |
| Attack delivery | ranged | ranged | ranged |
| Basic damage type | physical | physical | physical |
| Nominal attacks/second | 0.85 | 0.85 | 0.85 |
| Effective attacks/second at 20 Hz | 0.8333 | 0.8333 | 0.8333 |
| Range in tiles | 4 | 4 | 4 |
| Physical armor | 10 | 10 | 10 |
| Magic resistance | 10 | 10 | 10 |
| Movement tiles/second | 1.15 | 1.15 | 1.15 |

Nominal basic-attack DPS at one star: **51.00**, before mitigation, movement, stuns, skills, targeting downtime or timing quantization. Basic windup: 300 ms; ordinary projectile travel: 150 ms. No hidden critical hits, evasion, lifesteal or mana.

## One active skill

### Leafstep

**Player tooltip:** Dashes away from her target while keeping it in range.

**Indonesian draft:** Melakukan dash menjauh dari sasaran sambil tetap dalam jangkauan serang.

| Contract field | Value |
|---|---|
| Stable ability ID | `wc_a_elf_ranger` |
| Effect / target selector | `dash` / `retreat_from_current_enemy` |
| One / two / three star magnitude | Not applicable / Not applicable / Not applicable |
| Damage type | Not damaging |
| First-cast delay / cooldown | 2 s / 7.5 s |
| Windup / recovery | 0.2 s / 0.15 s |
| Effect duration | 0 s |
| Skill reach / area radius | 4 / 0 tiles |
| Can include self | False |
| Max dash distance | 2 tiles |
| Projectile travel | 0 ms |
| Affected stat | Not applicable |

Cooldown starts at successful cast commitment. An interrupted committed cast keeps its cooldown; an unavailable target leaves the ability ready and allows ordinary behavior. Area centers and area recipients are captured at release. Targeted projectiles keep their target ID but never retarget a defeated unit. Dash landing is reserved at commitment and validated before movement. See the rules contract for same-tick ordering, shield replacement and refresh semantics.

Health and basic damage use 1.00/1.80/3.24 star multipliers. Only explicitly authored skill magnitudes vary with stars; stun duration, range, radius, dash distance, cooldown and model footprint do not grow. A status-only skill may deliberately have identical behavior across stars; its owner still gains health and basic damage.

## Positioning and counterplay

**Preferred formation.** Backline with at least one free retreat tile; avoid filling every adjacent rear cell.

**Useful partners.** Ada or Borin gives Liora room to reposition; Tessa completes Ranger.

**Counterplay.** A fully crowded backline can deny landing cells, and pursuing Rogues can force repeated relocation.

**Practical weakness.** The skill deals no damage and fails to commit when no useful legal landing exists.

**Difference from the nearest alternative.** Tessa provides burst damage; Liora trades that burst for positional resilience.

**Character-specific acceptance test.** Test blocked board edges, equal-distance destinations, two dash reservations and target loss before release.

## Animation, effects and sound

Idle scans in short head turns. Movement uses light lateral steps. Basics draw, pause visibly at release, and recover. Leafstep crouches briefly then slides through a controlled airborne step to the reserved cell.

**Skill effect:** A short mint leaf trail follows the dash and fades within half a second. No invisibility, shield or damage accompanies the dash.

**Sound:** A soft bow snap and a brief brushlike dash sweep. Keep leaf rustle short and non-looping.

Author at 60 FPS, as in-place animations with no locomotion-driven root translation. Required clips: Idle, Move, Attack, Active, Hit, Defeat, Victory. The active release marker is frame 12 relative to animation start. Basic release marker is frame 18. These are presentation alignment points, not sources of authoritative damage. Idle begins as a 2-second loop; movement as a 1-second cycle; hit as 0.4 seconds; defeat as 1 second; victory as 1.5 seconds. Adjust clip lengths during animation review without altering gameplay timing.

A defeat uses a brief stagger, kneel or magical dissolve with no injury detail. Stars use UI pips, a subtle trim accent and a brief upgrade flourish; do not produce three separate bodies or enlarge the collision footprint.

## Blender construction and Unreal handoff

Start from the `humanoid_slender` base or a validated compatible family. Block silhouette before bevels; separate body, costume and equipment into named source collections. Build equipment as decorative fantasy game props, not real functional objects. Author model-space Z up and a consistent forward orientation, then prove conversion with the calibration fixture. Materials use one or two runtime slots and a shared atlas where it preserves identity.

Targets to profile: at most 15,000 LOD0 triangles, 1024-pixel default maps, up to 60 deforming bones and 4 influences per vertex. Lower-detail targets begin near 50% and 25% triangles. These are budgets, not measured performance.

Sockets: `weapon_r`, `weapon_l`, `cast_origin`, `head_ui`. Inspect shoulder, elbow, hip and knee extremes. Use separate rig proportions where needed; matching bone names is not proof of animation compatibility. Selection uses a stable unit proxy, not detailed prop collision. Team affiliation uses base rings/icons in addition to color, never a complete costume recolor.

**Specific production risk:** Foot sliding during the dash is acceptable only within the deliberate magical slide, not normal walking. Reserved tile and displayed landing must agree.

Required source/export locations:

- blender: `art-source/heroes/wc_u_elf_ranger/wc_u_elf_ranger.blend`

- mesh_fbx: `exports/heroes/wc_u_elf_ranger/SK_wc_u_elf_ranger.fbx`

- unreal_folder: `/Game/WonderChess/Heroes/wc_u_elf_ranger`

- portrait: `exports/heroes/wc_u_elf_ranger/portrait.png`

Create separate animation exports and texture maps, a model-derived portrait, front/side/back/three-quarter views, a gameplay-camera screenshot, and an actual Unreal animation capture. Log source/export hashes, skeleton revision, tool versions and import preset. Deliberately change one costume detail, re-export and verify existing material, skeleton, animation and actor references survive.

## Model-sheet generation brief

Original Wonder Chess high-fantasy character production sheet for Liora Leafstep, The Canopy Scout. Elf Ranger, adult character, height 1.88 m. Front, true side, back and three-quarter views at matching scale, neutral A-pose plus one action pose. A light forward-leaning profile, long crescent bow and three short leaflike cloak panels. The cloak stops above the knees, revealing long, narrow leg shapes. Golden-brown skin, gray-green eyes, swept-back pointed ears and pale brown hair tied into a short fan. Her gaze is alert rather than severe. Moss fabric over fitted leather shoulder protection, a single pale scarf and flexible boots. The bow-side shoulder stays clear; no oversized pauldron blocks the draw. A stylized crescent bow with broad flattened limbs and a slim back quiver. The bowstring is simplified geometry that can be hidden at distant LODs. Palette: Moss #647A4B; pale mint #B7CBB0; chestnut #765641; warm linen #DACCAB. Flat neutral background, orthographic construction views, equipment inset, readable seams, non-graphic stylized fantasy. No copied franchise designs, text baked into textures, cinematic fog, invented extra limbs or altered gear between views. These are concept directions, not generated images.

## Approval gates

Silhouette passes at 96-pixel preview; costume agrees across all views; all seven clips reviewed; no required missing textures; no unexplained import scale compensation; effect matches declared reach and damage type; portrait agrees with the modeled hero; crowded-board test passes; source revision/reimport is demonstrated. A Python exit code alone does not approve the art.

Canonical source: `data/units.json`. Regenerate this dossier with `python tools/build_documents.py` after data edits. Do not hand-edit a stat table and leave the JSON unchanged.

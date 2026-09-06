# Milo Mistwhistle — The Weather Tinkerer

**Halfling · Mage · Spell damage · EXPANSION**

Stable identity: `wc_u_halfling_mage`. Cost: **2 gold**. Rarity label: **Uncommon**, separate from star level. Status: designed, not modeled or implemented by this kit. All combat values are provisional prototype inputs.

## Character and world

Milo makes harmless weather displays for Willowrun’s festivals and became fascinated by why the real winds were changing. Zura answered his questions more patiently than he expected. He enters the trials to turn those lessons into a small dependable spell, while insisting that practical magic can still be delightful.

Home region: `willowrun`. Affiliation: `wayfarer_fellowship`. Neither supplies a hidden third synergy. Proper names are original proposed fiction, not trademark-clearance claims.

## Appearance and art direction

Authored standing height: **1.14 m**, excluding raised equipment. Rig family: `humanoid_small`. One logical tile at every star. All characters are adults, fully clothed and presented as non-graphic heroic fantasy.

### Silhouette and proportions

A round short travel coat, large upturned collar and a thick spiral-topped wand. A small rigid umbrella disk folded against the back adds a distinctive rounded shape.

### Face, hair and expression

Warm tan skin, gray eyes, a small dark mustache and wavy brown hair. Clearly adult proportions and expression; no oversized infant features.

### Costume construction

Sky-blue raincoat, cream collar, copper belt buckle and dark boots. Sleeves are wide but stop at the wrists for clean hand animation.

### Color palette

Sky blue #77AFC2; cream #EAE0C7; copper #B78258; slate #566477.

### Equipment and magical focus

A thick spiral fantasy wand and a collapsed decorative umbrella disk. The disk is not a shield or movement device.

### Three low-resolution identifiers

Spiral wand, upturned pale collar and round coat silhouette.

### Materials and surface detail

Waxed cloth, painted wood and dull copper; use a small bounded emissive spiral rather than transparent mist clothing.

### Back and side-view constraints

Umbrella disk is locked to a short bracket, clear of the head. The coat separates into two broad lower panels.

## Combat statistics — without traits or temporary effects

| Property | One star | Two stars | Three stars |
|---|---:|---:|---:|
| Health | 570 | 1,026 | 1,846.8 |
| Basic attack damage | 42 | 75.6 | 136.08 |
| Attack delivery | ranged | ranged | ranged |
| Basic damage type | magic | magic | magic |
| Nominal attacks/second | 0.80 | 0.80 | 0.80 |
| Effective attacks/second at 20 Hz | 0.8000 | 0.8000 | 0.8000 |
| Range in tiles | 3 | 3 | 3 |
| Physical armor | 8 | 8 | 8 |
| Magic resistance | 20 | 20 | 20 |
| Movement tiles/second | 1.15 | 1.15 | 1.15 |

Nominal basic-attack DPS at one star: **33.60**, before mitigation, movement, stuns, skills, targeting downtime or timing quantization. Basic windup: 300 ms; ordinary projectile travel: 150 ms. No hidden critical hits, evasion, lifesteal or mana.

## One active skill

### Mist Pop

**Player tooltip:** Bursts magic around the target’s captured location.

**Indonesian draft:** Memberikan kerusakan sihir kepada musuh di area sasaran.

| Contract field | Value |
|---|---|
| Stable ability ID | `wc_a_halfling_mage` |
| Effect / target selector | `damage` / `current_enemy_area` |
| One / two / three star magnitude | 135 / 243 / 437 |
| Damage type | magic |
| First-cast delay / cooldown | 3 s / 7 s |
| Windup / recovery | 0.35 s / 0.3 s |
| Effect duration | 0 s |
| Skill reach / area radius | 4 / 1 tiles |
| Can include self | False |
| Max dash distance | 0 tiles |
| Projectile travel | 200 ms |
| Affected stat | Not applicable |

Cooldown starts at successful cast commitment. An interrupted committed cast keeps its cooldown; an unavailable target leaves the ability ready and allows ordinary behavior. Area centers and area recipients are captured at release. Targeted projectiles keep their target ID but never retarget a defeated unit. Dash landing is reserved at commitment and validated before movement. See the rules contract for same-tick ordering, shield replacement and refresh semantics.

Health and basic damage use 1.00/1.80/3.24 star multipliers. Only explicitly authored skill magnitudes vary with stars; stun duration, range, radius, dash distance, cooldown and model footprint do not grow. A status-only skill may deliberately have identical behavior across stars; its owner still gains health and basic damage.

## Positioning and counterplay

**Preferred formation.** Middle-back row with enough protection to cast repeatedly.

**Useful partners.** Rowan enables Mage; Finn or Pippa supplies Halfling mobility.

**Counterplay.** Spread formations reduce area value, while a single durable target exposes his low burst.

**Practical weakness.** Fragile and unable to provide any control or protection.

**Difference from the nearest alternative.** Rowan’s burst is stronger and slower; Milo supplies lower-cost repeated small areas.

**Character-specific acceptance test.** Mist Pop is a single damage event and never produces hidden ticking cloud damage.

## Animation, effects and sound

Idle balances the wand with a curious head tilt. Basics send a small pale mote. The active makes one circular stir and flicks a cloudlet toward the captured target area.

**Skill effect:** A small blue-white cloud pops low to the board and vanishes. It does not blind, obscure the camera, slow movement or persist.

**Sound:** A soft rising whistle followed by a light magical pop, without a continuous wind loop.

Author at 60 FPS, as in-place animations with no locomotion-driven root translation. Required clips: Idle, Move, Attack, Active, Hit, Defeat, Victory. The active release marker is frame 21 relative to animation start. Basic release marker is frame 18. These are presentation alignment points, not sources of authoritative damage. Idle begins as a 2-second loop; movement as a 1-second cycle; hit as 0.4 seconds; defeat as 1 second; victory as 1.5 seconds. Adjust clip lengths during animation review without altering gameplay timing.

A defeat uses a brief stagger, kneel or magical dissolve with no injury detail. Stars use UI pips, a subtle trim accent and a brief upgrade flourish; do not produce three separate bodies or enlarge the collision footprint.

## Blender construction and Unreal handoff

Start from the `humanoid_small` base or a validated compatible family. Block silhouette before bevels; separate body, costume and equipment into named source collections. Build equipment as decorative fantasy game props, not real functional objects. Author model-space Z up and a consistent forward orientation, then prove conversion with the calibration fixture. Materials use one or two runtime slots and a shared atlas where it preserves identity.

Targets to profile: at most 15,000 LOD0 triangles, 1024-pixel default maps, up to 60 deforming bones and 4 influences per vertex. Lower-detail targets begin near 50% and 25% triangles. These are budgets, not measured performance.

Sockets: `weapon_r`, `weapon_l`, `cast_origin`, `head_ui`. Inspect shoulder, elbow, hip and knee extremes. Use separate rig proportions where needed; matching bone names is not proof of animation compatibility. Selection uses a stable unit proxy, not detailed prop collision. Team affiliation uses base rings/icons in addition to color, never a complete costume recolor.

**Specific production risk:** Cloud effects can obscure units. Keep opacity low, lifetime short and the gameplay ring more readable than the vapor.

Required source/export locations:

- blender: `art-source/heroes/wc_u_halfling_mage/wc_u_halfling_mage.blend`

- mesh_fbx: `exports/heroes/wc_u_halfling_mage/SK_wc_u_halfling_mage.fbx`

- unreal_folder: `/Game/WonderChess/Heroes/wc_u_halfling_mage`

- portrait: `exports/heroes/wc_u_halfling_mage/portrait.png`

Create separate animation exports and texture maps, a model-derived portrait, front/side/back/three-quarter views, a gameplay-camera screenshot, and an actual Unreal animation capture. Log source/export hashes, skeleton revision, tool versions and import preset. Deliberately change one costume detail, re-export and verify existing material, skeleton, animation and actor references survive.

## Model-sheet generation brief

Original Wonder Chess high-fantasy character production sheet for Milo Mistwhistle, The Weather Tinkerer. Halfling Mage, adult character, height 1.14 m. Front, true side, back and three-quarter views at matching scale, neutral A-pose plus one action pose. A round short travel coat, large upturned collar and a thick spiral-topped wand. A small rigid umbrella disk folded against the back adds a distinctive rounded shape. Warm tan skin, gray eyes, a small dark mustache and wavy brown hair. Clearly adult proportions and expression; no oversized infant features. Sky-blue raincoat, cream collar, copper belt buckle and dark boots. Sleeves are wide but stop at the wrists for clean hand animation. A thick spiral fantasy wand and a collapsed decorative umbrella disk. The disk is not a shield or movement device. Palette: Sky blue #77AFC2; cream #EAE0C7; copper #B78258; slate #566477. Flat neutral background, orthographic construction views, equipment inset, readable seams, non-graphic stylized fantasy. No copied franchise designs, text baked into textures, cinematic fog, invented extra limbs or altered gear between views. These are concept directions, not generated images.

## Approval gates

Silhouette passes at 96-pixel preview; costume agrees across all views; all seven clips reviewed; no required missing textures; no unexplained import scale compensation; effect matches declared reach and damage type; portrait agrees with the modeled hero; crowded-board test passes; source revision/reimport is demonstrated. A Python exit code alone does not approve the art.

Canonical source: `data/units.json`. Regenerate this dossier with `python tools/build_documents.py` after data edits. Do not hand-edit a stat table and leave the JSON unchanged.

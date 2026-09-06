# Orla Hearthglow — The Hallkeeper

**Dwarf · Priest · Support · ALPHA**

Stable identity: `wc_u_dwarf_priest`. Cost: **2 gold**. Rarity label: **Uncommon**, separate from star level. Production and verification status is recorded separately in reports/implementation_state.json; this generated dossier does not certify an asset or build. All combat values are provisional prototype inputs.

Quick display name: **Orla**. Informational roles: Healer. Role tags provide no additional synergy.

## Character and world

Orla keeps Stoneveil’s common hall welcoming to miners, craftspeople and travelers alike. She and Mira exchange practical notes, with Orla insisting that a good chair and a warm meal are often as important as a clever spell. In the trials she practices keeping a close-knit team standing without asking anyone to become invulnerable.

Home region: `stoneveil`. Affiliation: `hearthwright_union`. Neither supplies a hidden third synergy. Proper names are original proposed fiction, not trademark-clearance claims.

## Appearance and art direction

Authored standing height: **1.3 m**, excluding raised equipment. Rig family: `humanoid_stocky`. One logical tile at every star. All characters are adults, fully clothed and presented as non-graphic heroic fantasy.

### Silhouette and proportions

A broad rounded coat, low lantern held at the chest and a soft arch-shaped head covering. Her gentle oval outline contrasts with Borin’s rectangular armor.

### Face, hair and expression

Warm dark skin, lively brown eyes and silver hair arranged in two thick side braids. Her smile is restrained and dependable.

### Costume construction

Rust-red wool coat over cream cloth, a wide woven apron panel, short gloves and practical boots. The head covering is a padded travel hood, not a rigid helmet.

### Color palette

Rust #AC6653; oatmeal #DCCEAF; forest #586B57; warm brass #BDA061.

### Equipment and magical focus

A squat octagonal lantern carried on a short handle and a small folded cloth pouch. The lantern’s heavy silhouette stays visible even when unlit.

### Three low-resolution identifiers

Low octagonal lantern, rounded hood and broad warm-colored coat.

### Materials and surface detail

Thick wool, stitched canvas, dull brass and frosted-looking opaque lantern panes with emissive color. Avoid glass refraction.

### Back and side-view constraints

A broad stitched hearth emblem and two large coat folds create readable planes. The hood must not stretch unnaturally during looking down.

## Combat statistics — without traits or temporary effects

| Property | One star | Two stars | Three stars |
|---|---:|---:|---:|
| Health | 820 | 1,476 | 2,656.8 |
| Basic attack damage | 36 | 64.8 | 116.64 |
| Attack delivery | ranged | ranged | ranged |
| Basic damage type | magic | magic | magic |
| Nominal attacks/second | 0.70 | 0.70 | 0.70 |
| Effective attacks/second at 20 Hz | 0.6897 | 0.6897 | 0.6897 |
| Range in tiles | 2 | 2 | 2 |
| Physical armor | 20 | 20 | 20 |
| Magic resistance | 25 | 25 | 25 |
| Movement tiles/second | 0.95 | 0.95 | 0.95 |

Nominal basic-attack DPS at one star: **25.20**, before mitigation, movement, stuns, skills, targeting downtime or timing quantization. Basic windup: 300 ms; ordinary projectile travel: 150 ms. No hidden critical hits, evasion, lifesteal or mana.

## One active skill

### Hearth Glow

**Player tooltip:** Heals herself and adjacent allies.

**Indonesian draft:** Memulihkan kesehatan diri sendiri dan sekutu di petak bersebelahan.

| Contract field | Value |
|---|---|
| Stable ability ID | `wc_a_dwarf_priest` |
| Effect / target selector | `heal` / `adjacent_allies` |
| One / two / three star magnitude | heal: 125 / 225 / 405 |
| Damage type | Not damaging |
| First-cast delay / cooldown | 3 s / 8 s |
| Windup / recovery | 0.35 s / 0.3 s |
| Effect duration | 0.0 s |
| Skill reach / area radius | 1 / 1 tiles |
| Can include self | True |
| Max dash distance | 0 tiles |
| Projectile travel | 0 ms |
| Affected stat | Not applicable |

Cooldown starts at successful cast commitment. An interrupted committed cast keeps its cooldown; an unavailable target leaves the ability ready and allows ordinary behavior. Area centers and area recipients are captured at release. Targeted projectiles keep their target ID but never retarget a defeated unit. Dash landing is reserved at commitment and validated before movement. See the rules contract for same-tick ordering, shield replacement and refresh semantics.

Health and basic damage use 1.00/1.80/3.24 star multipliers. Only explicitly authored skill magnitudes vary with stars; stun duration, range, radius, dash distance, cooldown and model footprint do not grow. A status-only skill may deliberately have identical behavior across stars; its owner still gains health and basic damage.

## Positioning and counterplay

**Preferred formation.** Second row among durable allies rather than alone at maximum range.

**Useful partners.** Borin and Dagna can stay close enough to receive the pulse; Mira enables Priest.

**Counterplay.** Area magic punishes the group formation required for efficient healing.

**Practical weakness.** Short heal reach and modest damage; allies outside the release snapshot receive nothing.

**Difference from the nearest alternative.** Mira can heal a distant single ally; Orla repairs a nearby group.

**Character-specific acceptance test.** Self is counted exactly once, each adjacent ally is healed once, and full-health targets do not inflate effective healing.

## Animation, effects and sound

Idle lifts the lantern slightly as if checking a path. Basics release a small light mote. The active opens the free arm and raises the lantern, then settles into the same stance.

**Skill effect:** A low amber ring washes over adjacent allies once; small rising squares suggest warmth. No lasting zone, regeneration or shield.

**Sound:** A warm bell cluster with a soft wooden resonance, distinct from Mira’s higher single-target cue.

Author at 60 FPS, as in-place animations with no locomotion-driven root translation. Required clips: Idle, Move, Attack, Active, Hit, Defeat, Victory. The active release marker is frame 21 relative to animation start. Basic release marker is frame 18. These are presentation alignment points, not sources of authoritative damage. Idle begins as a 2-second loop; movement as a 1-second cycle; hit as 0.4 seconds; defeat as 1 second; victory as 1.5 seconds. Adjust clip lengths during animation review without altering gameplay timing.

A defeat uses a brief stagger, kneel or magical dissolve with no injury detail. Stars use UI pips, a subtle trim accent and a brief upgrade flourish; do not produce three separate bodies or enlarge the collision footprint.

## Blender construction and Unreal handoff

Start from the `humanoid_stocky` base or a validated compatible family. Block silhouette before bevels; separate body, costume and equipment into named source collections. Build equipment as decorative fantasy game props, not real functional objects. Author model-space Z up and a consistent forward orientation, then prove conversion with the calibration fixture. Materials use one or two runtime slots and a shared atlas where it preserves identity.

Targets to profile: at most 15,000 LOD0 triangles, 1024-pixel default maps, up to 60 deforming bones and 4 influences per vertex. Lower-detail targets begin near 50% and 25% triangles. These are budgets, not measured performance.

Sockets: `weapon_r`, `weapon_l`, `cast_origin`, `head_ui`. Inspect shoulder, elbow, hip and knee extremes. Use separate rig proportions where needed; matching bone names is not proof of animation compatibility. Selection uses a stable unit proxy, not detailed prop collision. Team affiliation uses base rings/icons in addition to color, never a complete costume recolor.

**Specific production risk:** Group-heal effects can look like a persistent aura. Make the one-shot pulse clear and cap repeated target sounds.

Required source/export locations:

- blender: `art-source/heroes/wc_u_dwarf_priest/wc_u_dwarf_priest.blend`

- mesh_fbx: `exports/heroes/wc_u_dwarf_priest/SK_wc_u_dwarf_priest.fbx`

- unreal_folder: `/Game/WonderChess/Heroes/wc_u_dwarf_priest`

- portrait: `exports/heroes/wc_u_dwarf_priest/portrait.png`

Create separate animation exports and texture maps, a model-derived portrait, front/side/back/three-quarter views, a gameplay-camera screenshot, and an actual Unreal animation capture. Log source/export hashes, skeleton revision, tool versions and import preset. Deliberately change one costume detail, re-export and verify existing material, skeleton, animation and actor references survive.

## Model-sheet generation brief

Original Wonder Chess high-fantasy character production sheet for Orla Hearthglow, The Hallkeeper. Dwarf Priest, adult character, height 1.3 m. Front, true side, back and three-quarter views at matching scale, neutral A-pose plus one action pose. A broad rounded coat, low lantern held at the chest and a soft arch-shaped head covering. Her gentle oval outline contrasts with Borin’s rectangular armor. Warm dark skin, lively brown eyes and silver hair arranged in two thick side braids. Her smile is restrained and dependable. Rust-red wool coat over cream cloth, a wide woven apron panel, short gloves and practical boots. The head covering is a padded travel hood, not a rigid helmet. A squat octagonal lantern carried on a short handle and a small folded cloth pouch. The lantern’s heavy silhouette stays visible even when unlit. Palette: Rust #AC6653; oatmeal #DCCEAF; forest #586B57; warm brass #BDA061. Flat neutral background, orthographic construction views, equipment inset, readable seams, non-graphic stylized fantasy. No copied franchise designs, text baked into textures, cinematic fog, invented extra limbs or altered gear between views. These are concept directions, not generated images.

## Approval gates

Silhouette passes at 96-pixel preview; costume agrees across all views; all seven clips reviewed; no required missing textures; no unexplained import scale compensation; effect matches declared reach and damage type; portrait agrees with the modeled hero; crowded-board test passes; source revision/reimport is demonstrated. A Python exit code alone does not approve the art.

Canonical source: `data/units.json`. Regenerate this dossier with `python tools/build_documents.py` after data edits. Do not hand-edit a stat table and leave the JSON unchanged.

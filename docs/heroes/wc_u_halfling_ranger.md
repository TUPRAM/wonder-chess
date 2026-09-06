# Finn Thistlearrow — The River Lookout

**Halfling · Ranger · Ranged damage · EXPANSION**

Stable identity: `wc_u_halfling_ranger`. Cost: **1 gold**. Rarity label: **Common**, separate from star level. Status: designed, not modeled or implemented by this kit. All combat values are provisional prototype inputs.

## Character and world

Finn watches Willowrun’s river crossings and records changes in water levels for travelers. He is quieter than Pippa but just as determined to keep routes open. The trials give him a way to practice slowing a dangerous opponent’s attacks while the rest of his team carries out a plan.

Home region: `willowrun`. Affiliation: `wayfarer_fellowship`. Neither supplies a hidden third synergy. Proper names are original proposed fiction, not trademark-clearance claims.

## Appearance and art direction

Authored standing height: **1.08 m**, excluding raised equipment. Rig family: `humanoid_small`. One logical tile at every star. All characters are adults, fully clothed and presented as non-graphic heroic fantasy.

### Silhouette and proportions

A small narrow body beneath a broad folded brim and a long simple bow carried upright. A narrow shoulder cape makes a triangular rear profile.

### Face, hair and expression

Tan skin, dark eyes, sandy curls and a thoughtful expression. The hat brim tilts upward enough not to hide his eyes.

### Costume construction

River-blue vest over cream sleeves, moss trousers, a short cape and simple boots. One broad belt pouch breaks the symmetrical torso.

### Color palette

River blue #58899C; cream #E4DABC; moss #6F8158; warm brown #866243.

### Equipment and magical focus

A slim fantasy bow and a compact quiver worn at the side. Keep the active projectile visibly magical instead of suggesting a real substance.

### Three low-resolution identifiers

Folded brim, upright long bow and blue triangular shoulder cape.

### Materials and surface detail

Matte cloth, oiled wood and simple leather. No thin transparent feathers on arrows at gameplay distance.

### Back and side-view constraints

The cape ends above the waist and leaves the side quiver visible; a stitched river line supplies one large motif.

## Combat statistics — without traits or temporary effects

| Property | One star | Two stars | Three stars |
|---|---:|---:|---:|
| Health | 590 | 1,062 | 1,911.6 |
| Basic attack damage | 49 | 88.2 | 158.76 |
| Attack delivery | ranged | ranged | ranged |
| Basic damage type | physical | physical | physical |
| Nominal attacks/second | 1.00 | 1.00 | 1.00 |
| Effective attacks/second at 20 Hz | 1.0000 | 1.0000 | 1.0000 |
| Range in tiles | 4 | 4 | 4 |
| Physical armor | 8 | 8 | 8 |
| Magic resistance | 10 | 10 | 10 |
| Movement tiles/second | 1.25 | 1.25 | 1.25 |

Nominal basic-attack DPS at one star: **49.00**, before mitigation, movement, stuns, skills, targeting downtime or timing quantization. Basic windup: 300 ms; ordinary projectile travel: 150 ms. No hidden critical hits, evasion, lifesteal or mana.

## One active skill

### Dulling Shot

**Player tooltip:** Reduces the current target’s attack speed for three seconds.

**Indonesian draft:** Mengurangi kecepatan serang sasaran untuk sementara.

| Contract field | Value |
|---|---|
| Stable ability ID | `wc_a_halfling_ranger` |
| Effect / target selector | `stat_modifier` / `current_enemy` |
| One / two / three star magnitude | -20% / -25% / -30% |
| Damage type | Not damaging |
| First-cast delay / cooldown | 2.5 s / 8 s |
| Windup / recovery | 0.3 s / 0.3 s |
| Effect duration | 3 s |
| Skill reach / area radius | 4 / 0 tiles |
| Can include self | False |
| Max dash distance | 0 tiles |
| Projectile travel | 150 ms |
| Affected stat | attack_rate |

Cooldown starts at successful cast commitment. An interrupted committed cast keeps its cooldown; an unavailable target leaves the ability ready and allows ordinary behavior. Area centers and area recipients are captured at release. Targeted projectiles keep their target ID but never retarget a defeated unit. Dash landing is reserved at commitment and validated before movement. See the rules contract for same-tick ordering, shield replacement and refresh semantics.

Health and basic damage use 1.00/1.80/3.24 star multipliers. Only explicitly authored skill magnitudes vary with stars; stun duration, range, radius, dash distance, cooldown and model footprint do not grow. A status-only skill may deliberately have identical behavior across stars; its owner still gains health and basic damage.

## Positioning and counterplay

**Preferred formation.** Protected backline where he can keep shooting the most threatening current opponent.

**Useful partners.** Tessa or Liora enables Ranger; Pippa provides a matching-race frontline.

**Counterplay.** Ability-focused casters are less affected because Dulling Shot does not alter active cooldowns.

**Practical weakness.** Low health and no burst active; the debuff has limited value against already slow attackers.

**Difference from the nearest alternative.** Tessa adds a damage burst; Finn reduces an enemy’s basic-attack output.

**Character-specific acceptance test.** Negative speed modifiers use the strongest-key refresh policy, cannot reduce speed below the clamp, and never slow cooldowns.

## Animation, effects and sound

Idle checks the distance under the hat brim. Basics use quick controlled bow draws. The active pauses longer, aims carefully and releases one blue mote-tipped fantasy arrow.

**Skill effect:** Blue chevrons descend briefly over the target to indicate reduced attack tempo. No movement slow, poison or damage-over-time trail.

**Sound:** A clear bow snap followed by a soft descending two-note magical cue.

Author at 60 FPS, as in-place animations with no locomotion-driven root translation. Required clips: Idle, Move, Attack, Active, Hit, Defeat, Victory. The active release marker is frame 18 relative to animation start. Basic release marker is frame 18. These are presentation alignment points, not sources of authoritative damage. Idle begins as a 2-second loop; movement as a 1-second cycle; hit as 0.4 seconds; defeat as 1 second; victory as 1.5 seconds. Adjust clip lengths during animation review without altering gameplay timing.

A defeat uses a brief stagger, kneel or magical dissolve with no injury detail. Stars use UI pips, a subtle trim accent and a brief upgrade flourish; do not produce three separate bodies or enlarge the collision footprint.

## Blender construction and Unreal handoff

Start from the `humanoid_small` base or a validated compatible family. Block silhouette before bevels; separate body, costume and equipment into named source collections. Build equipment as decorative fantasy game props, not real functional objects. Author model-space Z up and a consistent forward orientation, then prove conversion with the calibration fixture. Materials use one or two runtime slots and a shared atlas where it preserves identity.

Targets to profile: at most 15,000 LOD0 triangles, 1024-pixel default maps, up to 60 deforming bones and 4 influences per vertex. Lower-detail targets begin near 50% and 25% triangles. These are budgets, not measured performance.

Sockets: `weapon_r`, `weapon_l`, `cast_origin`, `head_ui`. Inspect shoulder, elbow, hip and knee extremes. Use separate rig proportions where needed; matching bone names is not proof of animation compatibility. Selection uses a stable unit proxy, not detailed prop collision. Team affiliation uses base rings/icons in addition to color, never a complete costume recolor.

**Specific production risk:** The debuff must remain distinguishable from stun. Do not show immobilizing chains or stop the target’s movement animation.

Required source/export locations:

- blender: `art-source/heroes/wc_u_halfling_ranger/wc_u_halfling_ranger.blend`

- mesh_fbx: `exports/heroes/wc_u_halfling_ranger/SK_wc_u_halfling_ranger.fbx`

- unreal_folder: `/Game/WonderChess/Heroes/wc_u_halfling_ranger`

- portrait: `exports/heroes/wc_u_halfling_ranger/portrait.png`

Create separate animation exports and texture maps, a model-derived portrait, front/side/back/three-quarter views, a gameplay-camera screenshot, and an actual Unreal animation capture. Log source/export hashes, skeleton revision, tool versions and import preset. Deliberately change one costume detail, re-export and verify existing material, skeleton, animation and actor references survive.

## Model-sheet generation brief

Original Wonder Chess high-fantasy character production sheet for Finn Thistlearrow, The River Lookout. Halfling Ranger, adult character, height 1.08 m. Front, true side, back and three-quarter views at matching scale, neutral A-pose plus one action pose. A small narrow body beneath a broad folded brim and a long simple bow carried upright. A narrow shoulder cape makes a triangular rear profile. Tan skin, dark eyes, sandy curls and a thoughtful expression. The hat brim tilts upward enough not to hide his eyes. River-blue vest over cream sleeves, moss trousers, a short cape and simple boots. One broad belt pouch breaks the symmetrical torso. A slim fantasy bow and a compact quiver worn at the side. Keep the active projectile visibly magical instead of suggesting a real substance. Palette: River blue #58899C; cream #E4DABC; moss #6F8158; warm brown #866243. Flat neutral background, orthographic construction views, equipment inset, readable seams, non-graphic stylized fantasy. No copied franchise designs, text baked into textures, cinematic fog, invented extra limbs or altered gear between views. These are concept directions, not generated images.

## Approval gates

Silhouette passes at 96-pixel preview; costume agrees across all views; all seven clips reviewed; no required missing textures; no unexplained import scale compensation; effect matches declared reach and damage type; portrait agrees with the modeled hero; crowded-board test passes; source revision/reimport is demonstrated. A Python exit code alone does not approve the art.

Canonical source: `data/units.json`. Regenerate this dossier with `python tools/build_documents.py` after data edits. Do not hand-edit a stat table and leave the JSON unchanged.

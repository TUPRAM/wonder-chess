# Varek Prismshot — The Glasswing Archer

**Dragonkin · Ranger · Ranged damage · EXPANSION**

Stable identity: `wc_u_dragonkin_ranger`. Cost: **2 gold**. Rarity label: **Uncommon**, separate from star level. Status: designed, not modeled or implemented by this kit. All combat values are provisional prototype inputs.

## Character and world

Varek crafts signal mirrors for Cindercrest’s mountain paths and developed an archer’s patience while aligning them. Tessa’s mechanical accuracy fascinates him, and their friendly demonstrations draw crowds in Brighthaven. He joins the trials to show that magical ranged combat can be precise rather than spectacularly noisy.

Home region: `cindercrest`. Affiliation: `skyward_conclave`. Neither supplies a hidden third synergy. Proper names are original proposed fiction, not trademark-clearance claims.

## Appearance and art direction

Authored standing height: **1.98 m**, excluding raised equipment. Rig family: `humanoid_draconic`. One logical tile at every star. All characters are adults, fully clothed and presented as non-graphic heroic fantasy.

### Silhouette and proportions

A long narrow torso with a broad prismatic bow and two short outward horn fins. A split short cloak creates a forked shape without actual wings.

### Face, hair and expression

Blue-gray scales, pale gold eyes and a short angular muzzle. Horn fins are blunt and clearly part of the head rather than a wearable crown.

### Costume construction

Dark blue fitted ranger coat, ivory shoulder panels, silver belt and practical boots. The cloak ends at the hips.

### Color palette

Blue gray #7996AC; deep blue #3F567A; ivory #E6DFC9; prism cyan #8BC9CA.

### Equipment and magical focus

A stylized bow with broad translucent-looking but opaque shaded crystal facets. Keep its central grip readable and its mechanics decorative.

### Three low-resolution identifiers

Prismatic horizontal bow, short horn fins and forked cloak.

### Materials and surface detail

Opaque faceted crystal shader, matte scale surface and soft cloth. Refraction is not required for the crystal look.

### Back and side-view constraints

Cloak panels suggest folded wings in outline only; no hidden wing rig or flight ability. A flat quiver sits between them.

## Combat statistics — without traits or temporary effects

| Property | One star | Two stars | Three stars |
|---|---:|---:|---:|
| Health | 720 | 1,296 | 2,332.8 |
| Basic attack damage | 56 | 100.8 | 181.44 |
| Attack delivery | ranged | ranged | ranged |
| Basic damage type | magic | magic | magic |
| Nominal attacks/second | 0.85 | 0.85 | 0.85 |
| Effective attacks/second at 20 Hz | 0.8333 | 0.8333 | 0.8333 |
| Range in tiles | 4 | 4 | 4 |
| Physical armor | 12 | 12 | 12 |
| Magic resistance | 25 | 25 | 25 |
| Movement tiles/second | 1.05 | 1.05 | 1.05 |

Nominal basic-attack DPS at one star: **47.60**, before mitigation, movement, stuns, skills, targeting downtime or timing quantization. Basic windup: 300 ms; ordinary projectile travel: 150 ms. No hidden critical hits, evasion, lifesteal or mana.

## One active skill

### Prism Shot

**Player tooltip:** Fires a stronger magic shot at the current target.

**Indonesian draft:** Memberikan kerusakan sihir kepada sasaran saat ini.

| Contract field | Value |
|---|---|
| Stable ability ID | `wc_a_dragonkin_ranger` |
| Effect / target selector | `damage` / `current_enemy` |
| One / two / three star magnitude | 160 / 288 / 518 |
| Damage type | magic |
| First-cast delay / cooldown | 3 s / 7.5 s |
| Windup / recovery | 0.35 s / 0.3 s |
| Effect duration | 0 s |
| Skill reach / area radius | 4 / 0 tiles |
| Can include self | False |
| Max dash distance | 0 tiles |
| Projectile travel | 150 ms |
| Affected stat | Not applicable |

Cooldown starts at successful cast commitment. An interrupted committed cast keeps its cooldown; an unavailable target leaves the ability ready and allows ordinary behavior. Area centers and area recipients are captured at release. Targeted projectiles keep their target ID but never retarget a defeated unit. Dash landing is reserved at commitment and validated before movement. See the rules contract for same-tick ordering, shield replacement and refresh semantics.

Health and basic damage use 1.00/1.80/3.24 star multipliers. Only explicitly authored skill magnitudes vary with stars; stun duration, range, radius, dash distance, cooldown and model footprint do not grow. A status-only skill may deliberately have identical behavior across stars; its owner still gains health and basic damage.

## Positioning and counterplay

**Preferred formation.** Protected backline against opponents leaning heavily on physical armor.

**Useful partners.** Tessa or Liora activates Ranger; Oren activates Dragonkin.

**Counterplay.** High magic resistance reduces both his basics and his active; Rogues threaten his unprotected flank.

**Practical weakness.** No mobility and no area damage; cannot bypass resistance.

**Difference from the nearest alternative.** Tessa deals physical damage, while Varek’s basic and active shots deal magic damage.

**Character-specific acceptance test.** Ranger boosts his magic basic attacks but not Prism Shot; mitigation selects resistance rather than armor.

## Animation, effects and sound

Idle holds the bow low. Basics release pale magic arrows. The active rotates the bow slightly to align its facets, then fires one clear beamlike projectile with finite travel time.

**Skill effect:** One narrow cyan projectile and compact prismatic target sparkle. It does not pierce, chain or deal true damage.

**Sound:** A crystalline bow note and a short clean impact, mixed below large area spells.

Author at 60 FPS, as in-place animations with no locomotion-driven root translation. Required clips: Idle, Move, Attack, Active, Hit, Defeat, Victory. The active release marker is frame 21 relative to animation start. Basic release marker is frame 18. These are presentation alignment points, not sources of authoritative damage. Idle begins as a 2-second loop; movement as a 1-second cycle; hit as 0.4 seconds; defeat as 1 second; victory as 1.5 seconds. Adjust clip lengths during animation review without altering gameplay timing.

A defeat uses a brief stagger, kneel or magical dissolve with no injury detail. Stars use UI pips, a subtle trim accent and a brief upgrade flourish; do not produce three separate bodies or enlarge the collision footprint.

## Blender construction and Unreal handoff

Start from the `humanoid_draconic` base or a validated compatible family. Block silhouette before bevels; separate body, costume and equipment into named source collections. Build equipment as decorative fantasy game props, not real functional objects. Author model-space Z up and a consistent forward orientation, then prove conversion with the calibration fixture. Materials use one or two runtime slots and a shared atlas where it preserves identity.

Targets to profile: at most 15,000 LOD0 triangles, 1024-pixel default maps, up to 60 deforming bones and 4 influences per vertex. Lower-detail targets begin near 50% and 25% triangles. These are budgets, not measured performance.

Sockets: `weapon_r`, `weapon_l`, `cast_origin`, `head_ui`. Inspect shoulder, elbow, hip and knee extremes. Use separate rig proportions where needed; matching bone names is not proof of animation compatibility. Selection uses a stable unit proxy, not detailed prop collision. Team affiliation uses base rings/icons in addition to color, never a complete costume recolor.

**Specific production risk:** Crystal materials can become too bright against snowlike backgrounds. Keep dark facet planes and verify readability without bloom.

Required source/export locations:

- blender: `art-source/heroes/wc_u_dragonkin_ranger/wc_u_dragonkin_ranger.blend`

- mesh_fbx: `exports/heroes/wc_u_dragonkin_ranger/SK_wc_u_dragonkin_ranger.fbx`

- unreal_folder: `/Game/WonderChess/Heroes/wc_u_dragonkin_ranger`

- portrait: `exports/heroes/wc_u_dragonkin_ranger/portrait.png`

Create separate animation exports and texture maps, a model-derived portrait, front/side/back/three-quarter views, a gameplay-camera screenshot, and an actual Unreal animation capture. Log source/export hashes, skeleton revision, tool versions and import preset. Deliberately change one costume detail, re-export and verify existing material, skeleton, animation and actor references survive.

## Model-sheet generation brief

Original Wonder Chess high-fantasy character production sheet for Varek Prismshot, The Glasswing Archer. Dragonkin Ranger, adult character, height 1.98 m. Front, true side, back and three-quarter views at matching scale, neutral A-pose plus one action pose. A long narrow torso with a broad prismatic bow and two short outward horn fins. A split short cloak creates a forked shape without actual wings. Blue-gray scales, pale gold eyes and a short angular muzzle. Horn fins are blunt and clearly part of the head rather than a wearable crown. Dark blue fitted ranger coat, ivory shoulder panels, silver belt and practical boots. The cloak ends at the hips. A stylized bow with broad translucent-looking but opaque shaded crystal facets. Keep its central grip readable and its mechanics decorative. Palette: Blue gray #7996AC; deep blue #3F567A; ivory #E6DFC9; prism cyan #8BC9CA. Flat neutral background, orthographic construction views, equipment inset, readable seams, non-graphic stylized fantasy. No copied franchise designs, text baked into textures, cinematic fog, invented extra limbs or altered gear between views. These are concept directions, not generated images.

## Approval gates

Silhouette passes at 96-pixel preview; costume agrees across all views; all seven clips reviewed; no required missing textures; no unexplained import scale compensation; effect matches declared reach and damage type; portrait agrees with the modeled hero; crowded-board test passes; source revision/reimport is demonstrated. A Python exit code alone does not approve the art.

Canonical source: `data/units.json`. Regenerate this dossier with `python tools/build_documents.py` after data edits. Do not hand-edit a stat table and leave the JSON unchanged.

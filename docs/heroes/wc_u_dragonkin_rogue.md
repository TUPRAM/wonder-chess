# Iri Cinderstep — The Quiet Spark

**Dragonkin · Rogue · Disruption · EXPANSION**

Stable identity: `wc_u_dragonkin_rogue`. Cost: **3 gold**. Rarity label: **Rare**, separate from star level. Status: designed, not modeled or implemented by this kit. All combat values are provisional prototype inputs.

## Character and world

Iri repairs small ward stones along Cindercrest’s footpaths, work that rewards precision more than force. She initially found the public trials overwhelming, but Sora encouraged her to bring a quiet skill to a noisy event. Her friendship with Nella rests on a shared belief that one well-timed action can be more useful than a grand entrance.

Home region: `cindercrest`. Affiliation: `skyward_conclave`. Neither supplies a hidden third synergy. Proper names are original proposed fiction, not trademark-clearance claims.

## Appearance and art direction

Authored standing height: **1.89 m**, excluding raised equipment. Rig family: `humanoid_draconic`. One logical tile at every star. All characters are adults, fully clothed and presented as non-graphic heroic fantasy.

### Silhouette and proportions

A slim low stance with a short swept neck crest, one long diagonal sash and paired broad crescent fantasy blades. The outline stays compact rather than spiky.

### Face, hair and expression

Muted copper scales, dark violet eyes and a short soft-edged muzzle. Two small backward horns sit close to the skull.

### Costume construction

Charcoal traveling jacket with coral lining, short layered hip panels and light boots. Leave elbow and knee shapes visible for agile poses.

### Color palette

Copper #AF7C60; charcoal #454552; coral #CB7B6B; muted violet #837B9E.

### Equipment and magical focus

Paired fantasy crescent blades with small pale inset gems. The true-damage fantasy comes from a brief magical effect, not realistic cutting detail.

### Three low-resolution identifiers

Close neck crest, coral diagonal sash and paired crescents.

### Materials and surface detail

Matte scales, soft cloth and restrained metal. Keep gem glow off except during the active.

### Back and side-view constraints

The sash crosses a flat back panel; no tail or wings. Neck crest must clear the shoulder blades during crouches.

## Combat statistics — without traits or temporary effects

| Property | One star | Two stars | Three stars |
|---|---:|---:|---:|
| Health | 730 | 1,314 | 2,365.2 |
| Basic attack damage | 65 | 117 | 210.6 |
| Attack delivery | melee | melee | melee |
| Basic damage type | physical | physical | physical |
| Nominal attacks/second | 1.05 | 1.05 | 1.05 |
| Effective attacks/second at 20 Hz | 1.0000 | 1.0000 | 1.0000 |
| Range in tiles | 1 | 1 | 1 |
| Physical armor | 15 | 15 | 15 |
| Magic resistance | 20 | 20 | 20 |
| Movement tiles/second | 1.25 | 1.25 | 1.25 |

Nominal basic-attack DPS at one star: **68.25**, before mitigation, movement, stuns, skills, targeting downtime or timing quantization. Basic windup: 250 ms; ordinary projectile travel: 0 ms. No hidden critical hits, evasion, lifesteal or mana.

## One active skill

### Prism Cut

**Player tooltip:** Deals a small true-damage hit to the current target.

**Indonesian draft:** Memberikan kerusakan murni kepada sasaran saat ini.

| Contract field | Value |
|---|---|
| Stable ability ID | `wc_a_dragonkin_rogue` |
| Effect / target selector | `damage` / `current_enemy` |
| One / two / three star magnitude | 100 / 180 / 324 |
| Damage type | true |
| First-cast delay / cooldown | 2.5 s / 8 s |
| Windup / recovery | 0.25 s / 0.3 s |
| Effect duration | 0 s |
| Skill reach / area radius | 1 / 0 tiles |
| Can include self | False |
| Max dash distance | 0 tiles |
| Projectile travel | 0 ms |
| Affected stat | Not applicable |

Cooldown starts at successful cast commitment. An interrupted committed cast keeps its cooldown; an unavailable target leaves the ability ready and allows ordinary behavior. Area centers and area recipients are captured at release. Targeted projectiles keep their target ID but never retarget a defeated unit. Dash landing is reserved at commitment and validated before movement. See the rules contract for same-tick ordering, shield replacement and refresh semantics.

Health and basic damage use 1.00/1.80/3.24 star multipliers. Only explicitly authored skill magnitudes vary with stars; stun duration, range, radius, dash distance, cooldown and model footprint do not grow. A status-only skill may deliberately have identical behavior across stars; its owner still gains health and basic damage.

## Positioning and counterplay

**Preferred formation.** Flank where she can reach a valuable durable target without taking the initial focus.

**Useful partners.** Sylas or Kesh enables Rogue; Sora provides protection and Dragonkin.

**Counterplay.** Shields still absorb Prism Cut, and her low health makes focused attacks effective.

**Practical weakness.** No dash and no area attack; true damage is small and does not bypass shields.

**Difference from the nearest alternative.** Other Rogues reposition or stun; Iri offers a narrow anti-defense damage tool only in the expansion.

**Character-specific acceptance test.** True damage bypasses armor/resistance, still applies permitted source bonuses once and is absorbed by shields first.

## Animation, effects and sound

Idle is still and balanced. Basics are compact alternating attacks. Prism Cut draws one crescent inward, pauses for a readable glint and releases a short deliberate gesture.

**Skill effect:** A thin white-violet impact mark and the ordinary damage number with a distinct true-damage icon. No injury detail, teleport or invulnerability.

**Sound:** A clean bright note with a soft impact tick; avoid harsh scraping sounds.

Author at 60 FPS, as in-place animations with no locomotion-driven root translation. Required clips: Idle, Move, Attack, Active, Hit, Defeat, Victory. The active release marker is frame 15 relative to animation start. Basic release marker is frame 15. These are presentation alignment points, not sources of authoritative damage. Idle begins as a 2-second loop; movement as a 1-second cycle; hit as 0.4 seconds; defeat as 1 second; victory as 1.5 seconds. Adjust clip lengths during animation review without altering gameplay timing.

A defeat uses a brief stagger, kneel or magical dissolve with no injury detail. Stars use UI pips, a subtle trim accent and a brief upgrade flourish; do not produce three separate bodies or enlarge the collision footprint.

## Blender construction and Unreal handoff

Start from the `humanoid_draconic` base or a validated compatible family. Block silhouette before bevels; separate body, costume and equipment into named source collections. Build equipment as decorative fantasy game props, not real functional objects. Author model-space Z up and a consistent forward orientation, then prove conversion with the calibration fixture. Materials use one or two runtime slots and a shared atlas where it preserves identity.

Targets to profile: at most 15,000 LOD0 triangles, 1024-pixel default maps, up to 60 deforming bones and 4 influences per vertex. Lower-detail targets begin near 50% and 25% triangles. These are budgets, not measured performance.

Sockets: `weapon_r`, `weapon_l`, `cast_origin`, `head_ui`. Inspect shoulder, elbow, hip and knee extremes. Use separate rig proportions where needed; matching bone names is not proof of animation compatibility. Selection uses a stable unit proxy, not detailed prop collision. Team affiliation uses base rings/icons in addition to color, never a complete costume recolor.

**Specific production risk:** True damage can erase defensive choices if overtuned. Its magnitude is deliberately lower than same-tier physical or magic skills and belongs only to expansion.

Required source/export locations:

- blender: `art-source/heroes/wc_u_dragonkin_rogue/wc_u_dragonkin_rogue.blend`

- mesh_fbx: `exports/heroes/wc_u_dragonkin_rogue/SK_wc_u_dragonkin_rogue.fbx`

- unreal_folder: `/Game/WonderChess/Heroes/wc_u_dragonkin_rogue`

- portrait: `exports/heroes/wc_u_dragonkin_rogue/portrait.png`

Create separate animation exports and texture maps, a model-derived portrait, front/side/back/three-quarter views, a gameplay-camera screenshot, and an actual Unreal animation capture. Log source/export hashes, skeleton revision, tool versions and import preset. Deliberately change one costume detail, re-export and verify existing material, skeleton, animation and actor references survive.

## Model-sheet generation brief

Original Wonder Chess high-fantasy character production sheet for Iri Cinderstep, The Quiet Spark. Dragonkin Rogue, adult character, height 1.89 m. Front, true side, back and three-quarter views at matching scale, neutral A-pose plus one action pose. A slim low stance with a short swept neck crest, one long diagonal sash and paired broad crescent fantasy blades. The outline stays compact rather than spiky. Muted copper scales, dark violet eyes and a short soft-edged muzzle. Two small backward horns sit close to the skull. Charcoal traveling jacket with coral lining, short layered hip panels and light boots. Leave elbow and knee shapes visible for agile poses. Paired fantasy crescent blades with small pale inset gems. The true-damage fantasy comes from a brief magical effect, not realistic cutting detail. Palette: Copper #AF7C60; charcoal #454552; coral #CB7B6B; muted violet #837B9E. Flat neutral background, orthographic construction views, equipment inset, readable seams, non-graphic stylized fantasy. No copied franchise designs, text baked into textures, cinematic fog, invented extra limbs or altered gear between views. These are concept directions, not generated images.

## Approval gates

Silhouette passes at 96-pixel preview; costume agrees across all views; all seven clips reviewed; no required missing textures; no unexplained import scale compensation; effect matches declared reach and damage type; portrait agrees with the modeled hero; crowded-board test passes; source revision/reimport is demonstrated. A Python exit code alone does not approve the art.

Canonical source: `data/units.json`. Regenerate this dossier with `python tools/build_documents.py` after data edits. Do not hand-edit a stat table and leave the JSON unchanged.

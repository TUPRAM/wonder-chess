# Elin Moonsong — The Grove Cantor

**Elf · Priest · Support · ALPHA**

Stable identity: `wc_u_elf_priest`. Cost: **2 gold**. Rarity label: **Uncommon**, separate from star level. Production and verification status is recorded separately in reports/implementation_state.json; this generated dossier does not certify an asset or build. All combat values are provisional prototype inputs.

Quick display name: **Elin**. Informational roles: Support. Role tags provide no additional synergy.

## Character and world

Elin directs music at Thistlewood’s seasonal gatherings, where songs help visiting communities learn each other’s histories. When travel became dangerous, she adapted those rhythms into marching exercises. She joins Liora in the trials to prove that cooperation can be felt in a formation as clearly as it can be heard in a chorus.

Home region: `thistlewood`. Affiliation: `greenward_circle`. Neither supplies a hidden third synergy. Proper names are original proposed fiction, not trademark-clearance claims.

## Appearance and art direction

Authored standing height: **1.85 m**, excluding raised equipment. Rig family: `humanoid_slender`. One logical tile at every star. All characters are adults, fully clothed and presented as non-graphic heroic fantasy.

### Silhouette and proportions

An upright pear-shaped silhouette with an open half-moon harp framing one shoulder. Layered petal-shaped sleeves form large, separated planes rather than many small leaves.

### Face, hair and expression

Deep umber skin, pale blue eyes and silver hair in a compact crown braid. Pointed ears remain visible on both sides of the harp.

### Costume construction

Blue-green tunic with ivory sleeve ends, a short overlapping overskirt and practical fitted boots. Silver trim follows one large curved line across the torso.

### Color palette

Deep teal #337A80; moon ivory #E3E8DD; blue-gray #6E86A0; silver #B6C7C9.

### Equipment and magical focus

A compact crescent harp held close to the torso, with only a few thick stylized strings. A small charm at the waist marks her order without introducing a resource.

### Three low-resolution identifiers

Open crescent harp, crown braid, and layered pale sleeve ends.

### Materials and surface detail

Smooth cloth with sparse brocade normals, brushed silver and a faint cool glow on the harp rim. Do not use constantly glowing eyes.

### Back and side-view constraints

Short robe panels leave the legs visible; a braided cord forms a clean circle high on the back. The harp must not clip through the spine during turning.

## Combat statistics — without traits or temporary effects

| Property | One star | Two stars | Three stars |
|---|---:|---:|---:|
| Health | 700 | 1,260 | 2,268 |
| Basic attack damage | 35 | 63 | 113.4 |
| Attack delivery | ranged | ranged | ranged |
| Basic damage type | magic | magic | magic |
| Nominal attacks/second | 0.80 | 0.80 | 0.80 |
| Effective attacks/second at 20 Hz | 0.8000 | 0.8000 | 0.8000 |
| Range in tiles | 3 | 3 | 3 |
| Physical armor | 10 | 10 | 10 |
| Magic resistance | 25 | 25 | 25 |
| Movement tiles/second | 1.05 | 1.05 | 1.05 |

Nominal basic-attack DPS at one star: **28.00**, before mitigation, movement, stuns, skills, targeting downtime or timing quantization. Basic windup: 300 ms; ordinary projectile travel: 150 ms. No hidden critical hits, evasion, lifesteal or mana.

## One active skill

### Quick Song

**Player tooltip:** Temporarily increases nearby allies’ attack speed.

**Indonesian draft:** Meningkatkan kecepatan serang diri sendiri dan sekutu bersebelahan untuk sementara.

| Contract field | Value |
|---|---|
| Stable ability ID | `wc_a_elf_priest` |
| Effect / target selector | `stat_modifier` / `adjacent_allies` |
| One / two / three star magnitude | stat_modifier: 20% / 25% / 30% |
| Damage type | Not damaging |
| First-cast delay / cooldown | 2.5 s / 9 s |
| Windup / recovery | 0.35 s / 0.3 s |
| Effect duration | 3.0 s |
| Skill reach / area radius | 1 / 1 tiles |
| Can include self | True |
| Max dash distance | 0 tiles |
| Projectile travel | 0 ms |
| Affected stat | attack_rate |

Cooldown starts at successful cast commitment. An interrupted committed cast keeps its cooldown; an unavailable target leaves the ability ready and allows ordinary behavior. Area centers and area recipients are captured at release. Targeted projectiles keep their target ID but never retarget a defeated unit. Dash landing is reserved at commitment and validated before movement. See the rules contract for same-tick ordering, shield replacement and refresh semantics.

Health and basic damage use 1.00/1.80/3.24 star multipliers. Only explicitly authored skill magnitudes vary with stars; stun duration, range, radius, dash distance, cooldown and model footprint do not grow. A status-only skill may deliberately have identical behavior across stars; its owner still gains health and basic damage.

## Positioning and counterplay

**Preferred formation.** One row behind clustered attackers so several allies occupy the eight neighboring cells.

**Useful partners.** Tessa and Liora use the attack-rate bonus effectively; Mira activates Priest support potency.

**Counterplay.** Area spells punish the grouping that makes the song efficient.

**Practical weakness.** She does not heal, and moving away after release does not grant the buff to newly adjacent units.

**Difference from the nearest alternative.** Mira restores health; Elin improves ordinary attack tempo without shortening active cooldowns.

**Character-specific acceptance test.** Priest must strengthen the positive attack-rate buff as well as healing/shields; equal-key casts must not stack indefinitely.

## Animation, effects and sound

Idle shifts a hand over the harp. Basic attacks pluck a single note. The active plants both feet and plays a broad chord, opening the elbows so the cast silhouette differs from an attack.

**Skill effect:** A low teal ring outlines affected adjacent cells, then small wing-shaped chevrons appear briefly over recipients. No continuous aura tick; recipients are snapshotted at release.

**Sound:** One clear string note for basics and a restrained three-note chord for the skill. Separate the buff sound from Mira’s healing bell.

Author at 60 FPS, as in-place animations with no locomotion-driven root translation. Required clips: Idle, Move, Attack, Active, Hit, Defeat, Victory. The active release marker is frame 21 relative to animation start. Basic release marker is frame 18. These are presentation alignment points, not sources of authoritative damage. Idle begins as a 2-second loop; movement as a 1-second cycle; hit as 0.4 seconds; defeat as 1 second; victory as 1.5 seconds. Adjust clip lengths during animation review without altering gameplay timing.

A defeat uses a brief stagger, kneel or magical dissolve with no injury detail. Stars use UI pips, a subtle trim accent and a brief upgrade flourish; do not produce three separate bodies or enlarge the collision footprint.

## Blender construction and Unreal handoff

Start from the `humanoid_slender` base or a validated compatible family. Block silhouette before bevels; separate body, costume and equipment into named source collections. Build equipment as decorative fantasy game props, not real functional objects. Author model-space Z up and a consistent forward orientation, then prove conversion with the calibration fixture. Materials use one or two runtime slots and a shared atlas where it preserves identity.

Targets to profile: at most 15,000 LOD0 triangles, 1024-pixel default maps, up to 60 deforming bones and 4 influences per vertex. Lower-detail targets begin near 50% and 25% triangles. These are budgets, not measured performance.

Sockets: `weapon_r`, `weapon_l`, `cast_origin`, `head_ui`. Inspect shoulder, elbow, hip and knee extremes. Use separate rig proportions where needed; matching bone names is not proof of animation compatibility. Selection uses a stable unit proxy, not detailed prop collision. Team affiliation uses base rings/icons in addition to color, never a complete costume recolor.

**Specific production risk:** String geometry and hands can shimmer or intersect. Simplify the finger action and let the chord’s full-body gesture carry readability.

Required source/export locations:

- blender: `art-source/heroes/wc_u_elf_priest/wc_u_elf_priest.blend`

- mesh_fbx: `exports/heroes/wc_u_elf_priest/SK_wc_u_elf_priest.fbx`

- unreal_folder: `/Game/WonderChess/Heroes/wc_u_elf_priest`

- portrait: `exports/heroes/wc_u_elf_priest/portrait.png`

Create separate animation exports and texture maps, a model-derived portrait, front/side/back/three-quarter views, a gameplay-camera screenshot, and an actual Unreal animation capture. Log source/export hashes, skeleton revision, tool versions and import preset. Deliberately change one costume detail, re-export and verify existing material, skeleton, animation and actor references survive.

## Model-sheet generation brief

Original Wonder Chess high-fantasy character production sheet for Elin Moonsong, The Grove Cantor. Elf Priest, adult character, height 1.85 m. Front, true side, back and three-quarter views at matching scale, neutral A-pose plus one action pose. An upright pear-shaped silhouette with an open half-moon harp framing one shoulder. Layered petal-shaped sleeves form large, separated planes rather than many small leaves. Deep umber skin, pale blue eyes and silver hair in a compact crown braid. Pointed ears remain visible on both sides of the harp. Blue-green tunic with ivory sleeve ends, a short overlapping overskirt and practical fitted boots. Silver trim follows one large curved line across the torso. A compact crescent harp held close to the torso, with only a few thick stylized strings. A small charm at the waist marks her order without introducing a resource. Palette: Deep teal #337A80; moon ivory #E3E8DD; blue-gray #6E86A0; silver #B6C7C9. Flat neutral background, orthographic construction views, equipment inset, readable seams, non-graphic stylized fantasy. No copied franchise designs, text baked into textures, cinematic fog, invented extra limbs or altered gear between views. These are concept directions, not generated images.

## Approval gates

Silhouette passes at 96-pixel preview; costume agrees across all views; all seven clips reviewed; no required missing textures; no unexplained import scale compensation; effect matches declared reach and damage type; portrait agrees with the modeled hero; crowded-board test passes; source revision/reimport is demonstrated. A Python exit code alone does not approve the art.

Canonical source: `data/units.json`. Regenerate this dossier with `python tools/build_documents.py` after data edits. Do not hand-edit a stat table and leave the JSON unchanged.

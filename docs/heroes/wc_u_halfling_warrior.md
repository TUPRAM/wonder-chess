# Pippa Oakstride — The Orchard Defender

**Halfling · Warrior · Melee damage · ALPHA**

Stable identity: `wc_u_halfling_warrior`. Cost: **1 gold**. Rarity label: **Common**, separate from star level. Production and verification status is recorded separately in reports/implementation_state.json; this generated dossier does not certify an asset or build. All combat values are provisional prototype inputs.

Quick display name: **Pippa**. Informational roles: Melee. Role tags provide no additional synergy.

## Character and world

Pippa organizes Willowrun’s orchard crews and can settle an argument about harvest shares before it becomes a feud. She entered the trials after helping Tala guide a stranded caravan home. Her confidence comes from preparation and practical teamwork, not from pretending that being small makes every danger harmless.

Home region: `willowrun`. Affiliation: `wayfarer_fellowship`. Neither supplies a hidden third synergy. Proper names are original proposed fiction, not trademark-clearance claims.

## Appearance and art direction

Authored standing height: **1.12 m**, excluding raised equipment. Rig family: `humanoid_small`. One logical tile at every star. All characters are adults, fully clothed and presented as non-graphic heroic fantasy.

### Silhouette and proportions

A small broad stance with a large round wooden buckler and an upright leaf-shaped fantasy club. An oversized short scarf forms a clear horizontal at the neck.

### Face, hair and expression

Light brown skin, freckled cheeks, bright hazel eyes and dense chestnut curls. Keep the face friendly and visibly adult.

### Costume construction

Apple-green quilted jacket, ochre trousers, a red neck scarf and broad walking boots. Outfit proportions emphasize capable mobility, not toy-like baby features.

### Color palette

Apple green #7A985A; ochre #BE9A59; berry red #A85251; walnut #73553B.

### Equipment and magical focus

Round orchard-mark buckler and short stylized wooden club reinforced with decorative bronze bands. Both are exaggerated fantasy props.

### Three low-resolution identifiers

Circular buckler, large red scarf and wide planted stance.

### Materials and surface detail

Quilted cloth, matte wood and dull bronze. Paint the orchard emblem in one readable silhouette.

### Back and side-view constraints

A square travel patch on the jacket and scarf ends over one shoulder keep the rear identifiable.

## Combat statistics — without traits or temporary effects

| Property | One star | Two stars | Three stars |
|---|---:|---:|---:|
| Health | 760 | 1,368 | 2,462.4 |
| Basic attack damage | 54 | 97.2 | 174.96 |
| Attack delivery | melee | melee | melee |
| Basic damage type | physical | physical | physical |
| Nominal attacks/second | 0.95 | 0.95 | 0.95 |
| Effective attacks/second at 20 Hz | 0.9091 | 0.9091 | 0.9091 |
| Range in tiles | 1 | 1 | 1 |
| Physical armor | 20 | 20 | 20 |
| Magic resistance | 10 | 10 | 10 |
| Movement tiles/second | 1.20 | 1.20 | 1.20 |

Nominal basic-attack DPS at one star: **51.30**, before mitigation, movement, stuns, skills, targeting downtime or timing quantization. Basic windup: 350 ms; ordinary projectile travel: 0 ms. No hidden critical hits, evasion, lifesteal or mana.

## One active skill

### Stout Heart

**Player tooltip:** Gains a temporary personal shield.

**Indonesian draft:** Memberikan perisai sementara kepada diri sendiri.

| Contract field | Value |
|---|---|
| Stable ability ID | `wc_a_halfling_warrior` |
| Effect / target selector | `shield` / `self` |
| One / two / three star magnitude | shield: 150 / 270 / 486 |
| Damage type | Not damaging |
| First-cast delay / cooldown | 2 s / 7.5 s |
| Windup / recovery | 0.25 s / 0.3 s |
| Effect duration | 2.5 s |
| Skill reach / area radius | 0 / 0 tiles |
| Can include self | True |
| Max dash distance | 0 tiles |
| Projectile travel | 0 ms |
| Affected stat | Not applicable |

Cooldown starts at successful cast commitment. An interrupted committed cast keeps its cooldown; an unavailable target leaves the ability ready and allows ordinary behavior. Area centers and area recipients are captured at release. Targeted projectiles keep their target ID but never retarget a defeated unit. Dash landing is reserved at commitment and validated before movement. See the rules contract for same-tick ordering, shield replacement and refresh semantics.

Health and basic damage use 1.00/1.80/3.24 star multipliers. Only explicitly authored skill magnitudes vary with stars; stun duration, range, radius, dash distance, cooldown and model footprint do not grow. A status-only skill may deliberately have identical behavior across stars; its owner still gains health and basic damage.

## Positioning and counterplay

**Preferred formation.** Beside a sturdier frontline ally where she can attack without taking every hit.

**Useful partners.** Finn or Nella supplies Halfling movement; Cass provides Warrior damage.

**Counterplay.** Sustained magic and crowd control can overcome her modest health after the shield ends.

**Practical weakness.** Short reach, no area effect, and less durability than a dedicated Guardian.

**Difference from the nearest alternative.** Ada is a defensive anchor; Pippa is a faster Warrior with a smaller survival window.

**Character-specific acceptance test.** Shield has a fixed 2500 ms duration at every star and a correctly scaled visual shell.

## Animation, effects and sound

Idle is grounded rather than constantly bouncing. Walk uses quick full-foot steps. Basics are short determined swings. Stout Heart lifts the buckler with a compact upward hop that returns to the same logical cell.

**Skill effect:** A small green-gold shield outline that matches her scale. No taunt or healing accompanies it.

**Sound:** A light wooden knock and short warm chime; avoid childish squeaks.

Author at 60 FPS, as in-place animations with no locomotion-driven root translation. Required clips: Idle, Move, Attack, Active, Hit, Defeat, Victory. The active release marker is frame 15 relative to animation start. Basic release marker is frame 21. These are presentation alignment points, not sources of authoritative damage. Idle begins as a 2-second loop; movement as a 1-second cycle; hit as 0.4 seconds; defeat as 1 second; victory as 1.5 seconds. Adjust clip lengths during animation review without altering gameplay timing.

A defeat uses a brief stagger, kneel or magical dissolve with no injury detail. Stars use UI pips, a subtle trim accent and a brief upgrade flourish; do not produce three separate bodies or enlarge the collision footprint.

## Blender construction and Unreal handoff

Start from the `humanoid_small` base or a validated compatible family. Block silhouette before bevels; separate body, costume and equipment into named source collections. Build equipment as decorative fantasy game props, not real functional objects. Author model-space Z up and a consistent forward orientation, then prove conversion with the calibration fixture. Materials use one or two runtime slots and a shared atlas where it preserves identity.

Targets to profile: at most 15,000 LOD0 triangles, 1024-pixel default maps, up to 60 deforming bones and 4 influences per vertex. Lower-detail targets begin near 50% and 25% triangles. These are budgets, not measured performance.

Sockets: `weapon_r`, `weapon_l`, `cast_origin`, `head_ui`. Inspect shoulder, elbow, hip and knee extremes. Use separate rig proportions where needed; matching bone names is not proof of animation compatibility. Selection uses a stable unit proxy, not detailed prop collision. Team affiliation uses base rings/icons in addition to color, never a complete costume recolor.

**Specific production risk:** Small units can disappear behind tall allies. Test camera spacing and health-bar anchors without enlarging her logical footprint.

Required source/export locations:

- blender: `art-source/heroes/wc_u_halfling_warrior/wc_u_halfling_warrior.blend`

- mesh_fbx: `exports/heroes/wc_u_halfling_warrior/SK_wc_u_halfling_warrior.fbx`

- unreal_folder: `/Game/WonderChess/Heroes/wc_u_halfling_warrior`

- portrait: `exports/heroes/wc_u_halfling_warrior/portrait.png`

Create separate animation exports and texture maps, a model-derived portrait, front/side/back/three-quarter views, a gameplay-camera screenshot, and an actual Unreal animation capture. Log source/export hashes, skeleton revision, tool versions and import preset. Deliberately change one costume detail, re-export and verify existing material, skeleton, animation and actor references survive.

## Model-sheet generation brief

Original Wonder Chess high-fantasy character production sheet for Pippa Oakstride, The Orchard Defender. Halfling Warrior, adult character, height 1.12 m. Front, true side, back and three-quarter views at matching scale, neutral A-pose plus one action pose. A small broad stance with a large round wooden buckler and an upright leaf-shaped fantasy club. An oversized short scarf forms a clear horizontal at the neck. Light brown skin, freckled cheeks, bright hazel eyes and dense chestnut curls. Keep the face friendly and visibly adult. Apple-green quilted jacket, ochre trousers, a red neck scarf and broad walking boots. Outfit proportions emphasize capable mobility, not toy-like baby features. Round orchard-mark buckler and short stylized wooden club reinforced with decorative bronze bands. Both are exaggerated fantasy props. Palette: Apple green #7A985A; ochre #BE9A59; berry red #A85251; walnut #73553B. Flat neutral background, orthographic construction views, equipment inset, readable seams, non-graphic stylized fantasy. No copied franchise designs, text baked into textures, cinematic fog, invented extra limbs or altered gear between views. These are concept directions, not generated images.

## Approval gates

Silhouette passes at 96-pixel preview; costume agrees across all views; all seven clips reviewed; no required missing textures; no unexplained import scale compensation; effect matches declared reach and damage type; portrait agrees with the modeled hero; crowded-board test passes; source revision/reimport is demonstrated. A Python exit code alone does not approve the art.

Canonical source: `data/units.json`. Regenerate this dossier with `python tools/build_documents.py` after data edits. Do not hand-edit a stat table and leave the JSON unchanged.

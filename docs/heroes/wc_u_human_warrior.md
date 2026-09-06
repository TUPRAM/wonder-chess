# Cass Vale — The Banner Captain

**Human · Warrior · Melee damage · ALPHA**

Stable identity: `wc_u_human_warrior`. Cost: **2 gold**. Rarity label: **Uncommon**, separate from star level. Production and verification status is recorded separately in reports/implementation_state.json; this generated dossier does not certify an asset or build. All combat values are provisional prototype inputs.

Quick display name: **Cass**. Informational roles: Melee. Role tags provide no additional synergy.

## Character and world

Cass trains Brighthaven’s volunteer patrols and remembers every recruit’s name. Ada taught him that a captain who rushes ahead can leave a stronger team behind. He enters the trials to practice decisive attacks within a formation, carrying a banner sewn by the same market families whose roads his patrols protect.

Home region: `brighthaven`. Affiliation: `dawn_compact`. Neither supplies a hidden third synergy. Proper names are original proposed fiction, not trademark-clearance claims.

## Appearance and art direction

Authored standing height: **1.86 m**, excluding raised equipment. Rig family: `humanoid_standard`. One logical tile at every star. All characters are adults, fully clothed and presented as non-graphic heroic fantasy.

### Silhouette and proportions

A tall upright figure with one squared shoulder plate and a long, broad fantasy blade held diagonally downward. A short rectangular back-banner creates a distinctive vertical behind the head.

### Face, hair and expression

Medium-brown skin, close-cropped dark hair, brown eyes and a composed, focused expression. A pale eyebrow streak is a natural hair accent rather than an injury story.

### Costume construction

Deep red fitted coat under partial silver plate, broad belt, cream trousers and knee boots. The asymmetric armor leaves a clear leading and trailing side.

### Color palette

Crimson #A4464D; cream #E3D7BA; silver #A6B5BF; midnight #344155.

### Equipment and magical focus

Broad two-handed fantasy blade and a short banner fixed to a rigid back bracket. The banner is cosmetic; no area buff or faction system is implied.

### Three low-resolution identifiers

Single large shoulder plate, upright back-banner and long diagonal blade.

### Materials and surface detail

Matte cloth and brushed steel with sparse clean edge highlights. Bake banner folds or use two accessory bones; no cloth solver.

### Back and side-view constraints

A rigid banner bracket attaches visibly to the harness, leaving shoulder motion clear. The cloth stops above the hips.

## Combat statistics — without traits or temporary effects

| Property | One star | Two stars | Three stars |
|---|---:|---:|---:|
| Health | 980 | 1,764 | 3,175.2 |
| Basic attack damage | 72 | 129.6 | 233.28 |
| Attack delivery | melee | melee | melee |
| Basic damage type | physical | physical | physical |
| Nominal attacks/second | 0.80 | 0.80 | 0.80 |
| Effective attacks/second at 20 Hz | 0.8000 | 0.8000 | 0.8000 |
| Range in tiles | 1 | 1 | 1 |
| Physical armor | 25 | 25 | 25 |
| Magic resistance | 15 | 15 | 15 |
| Movement tiles/second | 1.05 | 1.05 | 1.05 |

Nominal basic-attack DPS at one star: **57.60**, before mitigation, movement, stuns, skills, targeting downtime or timing quantization. Basic windup: 350 ms; ordinary projectile travel: 0 ms. No hidden critical hits, evasion, lifesteal or mana.

## One active skill

### Firm Strike

**Player tooltip:** Delivers a stronger physical hit to the current target.

**Indonesian draft:** Memberikan kerusakan fisik kepada sasaran saat ini.

| Contract field | Value |
|---|---|
| Stable ability ID | `wc_a_human_warrior` |
| Effect / target selector | `damage` / `current_enemy` |
| One / two / three star magnitude | damage: 180 / 324 / 583 |
| Damage type | physical |
| First-cast delay / cooldown | 3 s / 7.5 s |
| Windup / recovery | 0.35 s / 0.3 s |
| Effect duration | 0.0 s |
| Skill reach / area radius | 1 / 0 tiles |
| Can include self | False |
| Max dash distance | 0 tiles |
| Projectile travel | 0 ms |
| Affected stat | Not applicable |

Cooldown starts at successful cast commitment. An interrupted committed cast keeps its cooldown; an unavailable target leaves the ability ready and allows ordinary behavior. Area centers and area recipients are captured at release. Targeted projectiles keep their target ID but never retarget a defeated unit. Dash landing is reserved at commitment and validated before movement. See the rules contract for same-tick ordering, shield replacement and refresh semantics.

Health and basic damage use 1.00/1.80/3.24 star multipliers. Only explicitly authored skill magnitudes vary with stars; stun duration, range, radius, dash distance, cooldown and model footprint do not grow. A status-only skill may deliberately have identical behavior across stars; its owner still gains health and basic damage.

## Positioning and counterplay

**Preferred formation.** Frontline second contact, beside a Guardian rather than alone at the center.

**Useful partners.** Rok or Dagna enables Warrior while Ada can provide the Human bonus.

**Counterplay.** High armor and shields reduce the single large physical hit; stuns can cancel its windup.

**Practical weakness.** No area effect or self-protection; he needs access to a useful current target.

**Difference from the nearest alternative.** Dagna spreads damage; Cass concentrates it on one enemy.

**Character-specific acceptance test.** Ensure the active is an ability packet, not a basic attack repeated with all basic-only bonuses.

## Animation, effects and sound

Idle keeps the blade low and feet apart. Basics are short two-handed cuts. The active pulls the blade inward and delivers one measured forward strike; the banner follows slightly after the torso.

**Skill effect:** A single narrow warm-white trail and compact impact spark. No splash damage, armor break or knockback.

**Sound:** One firm cloth movement and a clean resonant hit; no shouted voice requirement.

Author at 60 FPS, as in-place animations with no locomotion-driven root translation. Required clips: Idle, Move, Attack, Active, Hit, Defeat, Victory. The active release marker is frame 21 relative to animation start. Basic release marker is frame 21. These are presentation alignment points, not sources of authoritative damage. Idle begins as a 2-second loop; movement as a 1-second cycle; hit as 0.4 seconds; defeat as 1 second; victory as 1.5 seconds. Adjust clip lengths during animation review without altering gameplay timing.

A defeat uses a brief stagger, kneel or magical dissolve with no injury detail. Stars use UI pips, a subtle trim accent and a brief upgrade flourish; do not produce three separate bodies or enlarge the collision footprint.

## Blender construction and Unreal handoff

Start from the `humanoid_standard` base or a validated compatible family. Block silhouette before bevels; separate body, costume and equipment into named source collections. Build equipment as decorative fantasy game props, not real functional objects. Author model-space Z up and a consistent forward orientation, then prove conversion with the calibration fixture. Materials use one or two runtime slots and a shared atlas where it preserves identity.

Targets to profile: at most 15,000 LOD0 triangles, 1024-pixel default maps, up to 60 deforming bones and 4 influences per vertex. Lower-detail targets begin near 50% and 25% triangles. These are budgets, not measured performance.

Sockets: `weapon_r`, `weapon_l`, `cast_origin`, `head_ui`. Inspect shoulder, elbow, hip and knee extremes. Use separate rig proportions where needed; matching bone names is not proof of animation compatibility. Selection uses a stable unit proxy, not detailed prop collision. Team affiliation uses base rings/icons in addition to color, never a complete costume recolor.

**Specific production risk:** Banner silhouette must not overlap health bars or obscure the next row. Validate that a two-handed pose works with the shared standard rig.

Required source/export locations:

- blender: `art-source/heroes/wc_u_human_warrior/wc_u_human_warrior.blend`

- mesh_fbx: `exports/heroes/wc_u_human_warrior/SK_wc_u_human_warrior.fbx`

- unreal_folder: `/Game/WonderChess/Heroes/wc_u_human_warrior`

- portrait: `exports/heroes/wc_u_human_warrior/portrait.png`

Create separate animation exports and texture maps, a model-derived portrait, front/side/back/three-quarter views, a gameplay-camera screenshot, and an actual Unreal animation capture. Log source/export hashes, skeleton revision, tool versions and import preset. Deliberately change one costume detail, re-export and verify existing material, skeleton, animation and actor references survive.

## Model-sheet generation brief

Original Wonder Chess high-fantasy character production sheet for Cass Vale, The Banner Captain. Human Warrior, adult character, height 1.86 m. Front, true side, back and three-quarter views at matching scale, neutral A-pose plus one action pose. A tall upright figure with one squared shoulder plate and a long, broad fantasy blade held diagonally downward. A short rectangular back-banner creates a distinctive vertical behind the head. Medium-brown skin, close-cropped dark hair, brown eyes and a composed, focused expression. A pale eyebrow streak is a natural hair accent rather than an injury story. Deep red fitted coat under partial silver plate, broad belt, cream trousers and knee boots. The asymmetric armor leaves a clear leading and trailing side. Broad two-handed fantasy blade and a short banner fixed to a rigid back bracket. The banner is cosmetic; no area buff or faction system is implied. Palette: Crimson #A4464D; cream #E3D7BA; silver #A6B5BF; midnight #344155. Flat neutral background, orthographic construction views, equipment inset, readable seams, non-graphic stylized fantasy. No copied franchise designs, text baked into textures, cinematic fog, invented extra limbs or altered gear between views. These are concept directions, not generated images.

## Approval gates

Silhouette passes at 96-pixel preview; costume agrees across all views; all seven clips reviewed; no required missing textures; no unexplained import scale compensation; effect matches declared reach and damage type; portrait agrees with the modeled hero; crowded-board test passes; source revision/reimport is demonstrated. A Python exit code alone does not approve the art.

Canonical source: `data/units.json`. Regenerate this dossier with `python tools/build_documents.py` after data edits. Do not hand-edit a stat table and leave the JSON unchanged.

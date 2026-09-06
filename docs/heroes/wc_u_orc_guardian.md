# Tala Ironroot — The Caravan Wall

**Orc · Guardian · Defender · EXPANSION**

Stable identity: `wc_u_orc_guardian`. Cost: **2 gold**. Rarity label: **Uncommon**, separate from star level. Status: designed, not modeled or implemented by this kit. All combat values are provisional prototype inputs.

## Character and world

Tala leads caravan defenses across Stormstep and knows that travelers rarely fit a perfect formation. She joins the trials to make protection adaptable without turning it into a promise that nobody can be hurt. Rok respects her steady judgment, while Kesh keeps returning to ask whether his latest shortcut counts as a sensible route.

Home region: `stormstep`. Affiliation: `highland_watch`. Neither supplies a hidden third synergy. Proper names are original proposed fiction, not trademark-clearance claims.

## Appearance and art direction

Authored standing height: **2.0 m**, excluding raised equipment. Rig family: `humanoid_broad`. One logical tile at every star. All characters are adults, fully clothed and presented as non-graphic heroic fantasy.

### Silhouette and proportions

A wide arch formed by two high shoulder guards and a tall rectangular shield with a rounded top. The lower body remains a stable trapezoid.

### Face, hair and expression

Deep moss-green skin, warm brown eyes, small tusks and tightly braided dark hair. Her expression is attentive rather than aggressive.

### Costume construction

Layered leather-and-bronze armor, a pale ochre shoulder wrap, a blue woven sash and thick boots. Broad woven patterns identify her caravan community.

### Color palette

Bronze #AC8658; ochre #D1B576; deep blue #405E78; moss #60765A.

### Equipment and magical focus

A broad fantasy tower shield and a short ceremonial mace. The shield carries a simple interlocking-road emblem with no dense carving.

### Three low-resolution identifiers

Rounded tower shield, arched shoulders and a bold blue waist sash.

### Materials and surface detail

Worn bronze, thick cloth and matte hide. Shield wear is painted as soft color variation rather than deep damage.

### Back and side-view constraints

A flat travel pack sits beneath the shoulder line. Keep its volume low enough not to collide with the shield when turning.

## Combat statistics — without traits or temporary effects

| Property | One star | Two stars | Three stars |
|---|---:|---:|---:|
| Health | 1,120 | 2,016 | 3,628.8 |
| Basic attack damage | 45 | 81 | 145.8 |
| Attack delivery | melee | melee | melee |
| Basic damage type | physical | physical | physical |
| Nominal attacks/second | 0.65 | 0.65 | 0.65 |
| Effective attacks/second at 20 Hz | 0.6452 | 0.6452 | 0.6452 |
| Range in tiles | 1 | 1 | 1 |
| Physical armor | 30 | 30 | 30 |
| Magic resistance | 20 | 20 | 20 |
| Movement tiles/second | 0.90 | 0.90 | 0.90 |

Nominal basic-attack DPS at one star: **29.25**, before mitigation, movement, stuns, skills, targeting downtime or timing quantization. Basic windup: 250 ms; ordinary projectile travel: 0 ms. No hidden critical hits, evasion, lifesteal or mana.

## One active skill

### Shared Guard

**Player tooltip:** Shields herself and adjacent allies for three seconds.

**Indonesian draft:** Memberikan perisai sementara kepada diri sendiri dan sekutu bersebelahan.

| Contract field | Value |
|---|---|
| Stable ability ID | `wc_a_orc_guardian` |
| Effect / target selector | `shield` / `adjacent_allies` |
| One / two / three star magnitude | 140 / 252 / 454 |
| Damage type | Not damaging |
| First-cast delay / cooldown | 2.5 s / 9.5 s |
| Windup / recovery | 0.35 s / 0.3 s |
| Effect duration | 3 s |
| Skill reach / area radius | 1 / 1 tiles |
| Can include self | True |
| Max dash distance | 0 tiles |
| Projectile travel | 0 ms |
| Affected stat | Not applicable |

Cooldown starts at successful cast commitment. An interrupted committed cast keeps its cooldown; an unavailable target leaves the ability ready and allows ordinary behavior. Area centers and area recipients are captured at release. Targeted projectiles keep their target ID but never retarget a defeated unit. Dash landing is reserved at commitment and validated before movement. See the rules contract for same-tick ordering, shield replacement and refresh semantics.

Health and basic damage use 1.00/1.80/3.24 star multipliers. Only explicitly authored skill magnitudes vary with stars; stun duration, range, radius, dash distance, cooldown and model footprint do not grow. A status-only skill may deliberately have identical behavior across stars; its owner still gains health and basic damage.

## Positioning and counterplay

**Preferred formation.** Frontline with at least one adjacent ally at cast time.

**Useful partners.** Dagna or Rok benefits from nearby protection; Orla can sustain the same cluster.

**Counterplay.** Spread ranged attacks and area magic both pressure different weaknesses of her grouped team.

**Practical weakness.** Lower shield amount per recipient than a dedicated self-shield; no control skill.

**Difference from the nearest alternative.** Ada shields only herself for a larger amount; Tala distributes a smaller shield to a nearby formation.

**Character-specific acceptance test.** Shield power is source-derived once, self is not duplicated, and leaving the radius after release does not remove the granted shield.

## Animation, effects and sound

Idle angles the shield protectively toward adjacent allies. Basics use a short mace arc. Shared Guard plants the shield and extends the free hand outward, clearly signaling a group effect.

**Skill effect:** Several short amber shield outlines appear on eligible recipients; a brief ground ring shows reach. No continuous aura follows her afterward.

**Sound:** One low shield chime and quiet recipient ticks, mixed as a single event rather than many full-volume sounds.

Author at 60 FPS, as in-place animations with no locomotion-driven root translation. Required clips: Idle, Move, Attack, Active, Hit, Defeat, Victory. The active release marker is frame 21 relative to animation start. Basic release marker is frame 15. These are presentation alignment points, not sources of authoritative damage. Idle begins as a 2-second loop; movement as a 1-second cycle; hit as 0.4 seconds; defeat as 1 second; victory as 1.5 seconds. Adjust clip lengths during animation review without altering gameplay timing.

A defeat uses a brief stagger, kneel or magical dissolve with no injury detail. Stars use UI pips, a subtle trim accent and a brief upgrade flourish; do not produce three separate bodies or enlarge the collision footprint.

## Blender construction and Unreal handoff

Start from the `humanoid_broad` base or a validated compatible family. Block silhouette before bevels; separate body, costume and equipment into named source collections. Build equipment as decorative fantasy game props, not real functional objects. Author model-space Z up and a consistent forward orientation, then prove conversion with the calibration fixture. Materials use one or two runtime slots and a shared atlas where it preserves identity.

Targets to profile: at most 15,000 LOD0 triangles, 1024-pixel default maps, up to 60 deforming bones and 4 influences per vertex. Lower-detail targets begin near 50% and 25% triangles. These are budgets, not measured performance.

Sockets: `weapon_r`, `weapon_l`, `cast_origin`, `head_ui`. Inspect shoulder, elbow, hip and knee extremes. Use separate rig proportions where needed; matching bone names is not proof of animation compatibility. Selection uses a stable unit proxy, not detailed prop collision. Team affiliation uses base rings/icons in addition to color, never a complete costume recolor.

**Specific production risk:** Large shield and shoulders may occlude neighboring supports. Use a lowered idle pose and test the camera from both encounter orientations.

Required source/export locations:

- blender: `art-source/heroes/wc_u_orc_guardian/wc_u_orc_guardian.blend`

- mesh_fbx: `exports/heroes/wc_u_orc_guardian/SK_wc_u_orc_guardian.fbx`

- unreal_folder: `/Game/WonderChess/Heroes/wc_u_orc_guardian`

- portrait: `exports/heroes/wc_u_orc_guardian/portrait.png`

Create separate animation exports and texture maps, a model-derived portrait, front/side/back/three-quarter views, a gameplay-camera screenshot, and an actual Unreal animation capture. Log source/export hashes, skeleton revision, tool versions and import preset. Deliberately change one costume detail, re-export and verify existing material, skeleton, animation and actor references survive.

## Model-sheet generation brief

Original Wonder Chess high-fantasy character production sheet for Tala Ironroot, The Caravan Wall. Orc Guardian, adult character, height 2.0 m. Front, true side, back and three-quarter views at matching scale, neutral A-pose plus one action pose. A wide arch formed by two high shoulder guards and a tall rectangular shield with a rounded top. The lower body remains a stable trapezoid. Deep moss-green skin, warm brown eyes, small tusks and tightly braided dark hair. Her expression is attentive rather than aggressive. Layered leather-and-bronze armor, a pale ochre shoulder wrap, a blue woven sash and thick boots. Broad woven patterns identify her caravan community. A broad fantasy tower shield and a short ceremonial mace. The shield carries a simple interlocking-road emblem with no dense carving. Palette: Bronze #AC8658; ochre #D1B576; deep blue #405E78; moss #60765A. Flat neutral background, orthographic construction views, equipment inset, readable seams, non-graphic stylized fantasy. No copied franchise designs, text baked into textures, cinematic fog, invented extra limbs or altered gear between views. These are concept directions, not generated images.

## Approval gates

Silhouette passes at 96-pixel preview; costume agrees across all views; all seven clips reviewed; no required missing textures; no unexplained import scale compensation; effect matches declared reach and damage type; portrait agrees with the modeled hero; crowded-board test passes; source revision/reimport is demonstrated. A Python exit code alone does not approve the art.

Canonical source: `data/units.json`. Regenerate this dossier with `python tools/build_documents.py` after data edits. Do not hand-edit a stat table and leave the JSON unchanged.

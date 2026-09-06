# Zura Stormcall — The Sky Listener

**Orc · Mage · Spell damage · ALPHA**

Stable identity: `wc_u_orc_mage`. Cost: **3 gold**. Rarity label: **Rare**, separate from star level. Production and verification status is recorded separately in reports/implementation_state.json; this generated dossier does not certify an asset or build. All combat values are provisional prototype inputs.

Quick display name: **Zura**. Informational roles: Caster. Role tags provide no additional synergy.

## Character and world

Zura learned to read mountain winds so that Stormstep’s villages could prepare before storms arrived. She now studies disturbances around the distant breach, comparing notes with Rowan instead of accepting easy omens. In the trials she teaches captains to notice where enemies gather and to commit carefully when a spell cannot change direction once released.

Home region: `stormstep`. Affiliation: `highland_watch`. Neither supplies a hidden third synergy. Proper names are original proposed fiction, not trademark-clearance claims.

## Appearance and art direction

Authored standing height: **1.97 m**, excluding raised equipment. Rig family: `humanoid_broad`. One logical tile at every star. All characters are adults, fully clothed and presented as non-graphic heroic fantasy.

### Silhouette and proportions

A tall stable stance beneath two broad crescent shoulder cloths, with a forked staff held outward. Her costume forms layered triangles rather than a conventional pointed wizard hat.

### Face, hair and expression

Sage-green skin, silver-gray eyes, modest tusks and dark hair braided into three thick sections. A calm upward gaze suggests listening to the weather.

### Costume construction

Storm-blue layered coat, pale wool collar, russet belt and wrapped boots. Fabric panels end above the ankles and open around the knees for movement.

### Color palette

Storm blue #4A638D; cloud gray #CBD3DA; russet #A7664D; silver #A9B8C4.

### Equipment and magical focus

A tall wooden staff with an open fork framing a small floating sky stone. No hanging chains that require physical simulation.

### Three low-resolution identifiers

Open forked staff, cloud collar and three thick braids.

### Materials and surface detail

Wool, painted wood, oxidized silver and restrained cyan glow. Keep the sky stone’s bloom local.

### Back and side-view constraints

Two long triangular coat panels split around the legs, with a broad stitched cloud arc high on the back.

## Combat statistics — without traits or temporary effects

| Property | One star | Two stars | Three stars |
|---|---:|---:|---:|
| Health | 750 | 1,350 | 2,430 |
| Basic attack damage | 50 | 90 | 162 |
| Attack delivery | ranged | ranged | ranged |
| Basic damage type | magic | magic | magic |
| Nominal attacks/second | 0.75 | 0.75 | 0.75 |
| Effective attacks/second at 20 Hz | 0.7407 | 0.7407 | 0.7407 |
| Range in tiles | 3 | 3 | 3 |
| Physical armor | 12 | 12 | 12 |
| Magic resistance | 25 | 25 | 25 |
| Movement tiles/second | 1.00 | 1.00 | 1.00 |

Nominal basic-attack DPS at one star: **37.50**, before mitigation, movement, stuns, skills, targeting downtime or timing quantization. Basic windup: 300 ms; ordinary projectile travel: 150 ms. No hidden critical hits, evasion, lifesteal or mana.

## One active skill

### Storm Ring

**Player tooltip:** Strikes enemies around a captured enemy location with magic.

**Indonesian draft:** Memberikan kerusakan sihir kepada musuh di area sasaran.

| Contract field | Value |
|---|---|
| Stable ability ID | `wc_a_orc_mage` |
| Effect / target selector | `damage` / `current_enemy_area` |
| One / two / three star magnitude | damage: 190 / 342 / 616 |
| Damage type | magic |
| First-cast delay / cooldown | 4 s / 10 s |
| Windup / recovery | 0.6 s / 0.3 s |
| Effect duration | 0.0 s |
| Skill reach / area radius | 4 / 2 tiles |
| Can include self | False |
| Max dash distance | 0 tiles |
| Projectile travel | 300 ms |
| Affected stat | Not applicable |

Cooldown starts at successful cast commitment. An interrupted committed cast keeps its cooldown; an unavailable target leaves the ability ready and allows ordinary behavior. Area centers and area recipients are captured at release. Targeted projectiles keep their target ID but never retarget a defeated unit. Dash landing is reserved at commitment and validated before movement. See the rules contract for same-tick ordering, shield replacement and refresh semantics.

Health and basic damage use 1.00/1.80/3.24 star multipliers. Only explicitly authored skill magnitudes vary with stars; stun duration, range, radius, dash distance, cooldown and model footprint do not grow. A status-only skill may deliberately have identical behavior across stars; its owner still gains health and basic damage.

## Positioning and counterplay

**Preferred formation.** Protected backline with a frontline lasting long enough for the first cast.

**Useful partners.** Rowan completes Mage; Rok activates Orc; Borin can briefly keep targets close.

**Counterplay.** Spread out or force movement after the capture; Rogues can interrupt the long windup.

**Practical weakness.** High cost, slow active cadence and no control effect despite the storm imagery.

**Difference from the nearest alternative.** Rowan casts sooner with a smaller area; Zura risks a longer commitment for broader coverage.

**Character-specific acceptance test.** The storm captures center at release, not at impact; verify every affected unit receives exactly one magic packet.

## Animation, effects and sound

Idle makes a small palm-up listening gesture. Basics release small storm motes. The active raises the staff slowly, draws a visible circular path, then plants it as the captured area resolves.

**Skill effect:** A thin blue circle previews the captured radius during travel, followed by several short vertical magic streaks. The ability is one damage pulse, not damage over time or stun.

**Sound:** Low rising wind followed by a short soft thunder chord, capped to avoid overwhelming every other cue.

Author at 60 FPS, as in-place animations with no locomotion-driven root translation. Required clips: Idle, Move, Attack, Active, Hit, Defeat, Victory. The active release marker is frame 36 relative to animation start. Basic release marker is frame 18. These are presentation alignment points, not sources of authoritative damage. Idle begins as a 2-second loop; movement as a 1-second cycle; hit as 0.4 seconds; defeat as 1 second; victory as 1.5 seconds. Adjust clip lengths during animation review without altering gameplay timing.

A defeat uses a brief stagger, kneel or magical dissolve with no injury detail. Stars use UI pips, a subtle trim accent and a brief upgrade flourish; do not produce three separate bodies or enlarge the collision footprint.

## Blender construction and Unreal handoff

Start from the `humanoid_broad` base or a validated compatible family. Block silhouette before bevels; separate body, costume and equipment into named source collections. Build equipment as decorative fantasy game props, not real functional objects. Author model-space Z up and a consistent forward orientation, then prove conversion with the calibration fixture. Materials use one or two runtime slots and a shared atlas where it preserves identity.

Targets to profile: at most 15,000 LOD0 triangles, 1024-pixel default maps, up to 60 deforming bones and 4 influences per vertex. Lower-detail targets begin near 50% and 25% triangles. These are budgets, not measured performance.

Sockets: `weapon_r`, `weapon_l`, `cast_origin`, `head_ui`. Inspect shoulder, elbow, hip and knee extremes. Use separate rig proportions where needed; matching bone names is not proof of animation compatibility. Selection uses a stable unit proxy, not detailed prop collision. Team affiliation uses base rings/icons in addition to color, never a complete costume recolor.

**Specific production risk:** Radius two covers a large portion of a crowded board. Effects must show the true edge and performance tests must include multiple simultaneous rings.

Required source/export locations:

- blender: `art-source/heroes/wc_u_orc_mage/wc_u_orc_mage.blend`

- mesh_fbx: `exports/heroes/wc_u_orc_mage/SK_wc_u_orc_mage.fbx`

- unreal_folder: `/Game/WonderChess/Heroes/wc_u_orc_mage`

- portrait: `exports/heroes/wc_u_orc_mage/portrait.png`

Create separate animation exports and texture maps, a model-derived portrait, front/side/back/three-quarter views, a gameplay-camera screenshot, and an actual Unreal animation capture. Log source/export hashes, skeleton revision, tool versions and import preset. Deliberately change one costume detail, re-export and verify existing material, skeleton, animation and actor references survive.

## Model-sheet generation brief

Original Wonder Chess high-fantasy character production sheet for Zura Stormcall, The Sky Listener. Orc Mage, adult character, height 1.97 m. Front, true side, back and three-quarter views at matching scale, neutral A-pose plus one action pose. A tall stable stance beneath two broad crescent shoulder cloths, with a forked staff held outward. Her costume forms layered triangles rather than a conventional pointed wizard hat. Sage-green skin, silver-gray eyes, modest tusks and dark hair braided into three thick sections. A calm upward gaze suggests listening to the weather. Storm-blue layered coat, pale wool collar, russet belt and wrapped boots. Fabric panels end above the ankles and open around the knees for movement. A tall wooden staff with an open fork framing a small floating sky stone. No hanging chains that require physical simulation. Palette: Storm blue #4A638D; cloud gray #CBD3DA; russet #A7664D; silver #A9B8C4. Flat neutral background, orthographic construction views, equipment inset, readable seams, non-graphic stylized fantasy. No copied franchise designs, text baked into textures, cinematic fog, invented extra limbs or altered gear between views. These are concept directions, not generated images.

## Approval gates

Silhouette passes at 96-pixel preview; costume agrees across all views; all seven clips reviewed; no required missing textures; no unexplained import scale compensation; effect matches declared reach and damage type; portrait agrees with the modeled hero; crowded-board test passes; source revision/reimport is demonstrated. A Python exit code alone does not approve the art.

Canonical source: `data/units.json`. Regenerate this dossier with `python tools/build_documents.py` after data edits. Do not hand-edit a stat table and leave the JSON unchanged.

# Kesh Quickwind — The Ridge Courier

**Orc · Rogue · Disruption · ALPHA**

Stable identity: `wc_u_orc_rogue`. Cost: **2 gold**. Rarity label: **Uncommon**, separate from star level. Production and verification status is recorded separately in reports/implementation_state.json; this generated dossier does not certify an asset or build. All combat values are provisional prototype inputs.

Quick display name: **Kesh**. Informational roles: Control. Role tags provide no additional synergy.

## Character and world

Kesh carries maps and letters between Stormstep’s scattered homes, measuring a route by who it connects rather than how impressive it looks. He joined the trials after Sylas challenged him to a friendly delivery race. Their rivalry is cheerful, but Kesh wants captains to understand that reaching the right place is only useful when the team is ready to follow.

Home region: `stormstep`. Affiliation: `highland_watch`. Neither supplies a hidden third synergy. Proper names are original proposed fiction, not trademark-clearance claims.

## Appearance and art direction

Authored standing height: **1.93 m**, excluding raised equipment. Rig family: `humanoid_broad`. One logical tile at every star. All characters are adults, fully clothed and presented as non-graphic heroic fantasy.

### Silhouette and proportions

A narrow athletic wedge with a high scarf loop, short rounded shoulder guards and two compact hooked fantasy blades. The overall shape is tall and light rather than Rok’s broad mantle.

### Face, hair and expression

Muted jade skin, brown eyes, small tusks and cropped dark hair with a pale cloth tie. An easy grin distinguishes him from a stereotypically menacing Rogue.

### Costume construction

Turquoise courier jacket over charcoal cloth, a tan diagonal sash and light wrapped boots. Large route-marker patches replace armor clutter.

### Color palette

Turquoise #408E91; tan #C1A477; charcoal #3D4C4E; muted jade #708D72.

### Equipment and magical focus

Two short rounded fantasy blades and a flat map case on the hip. Keep the implements stylized and visually simpler than Sylas’s curves.

### Three low-resolution identifiers

High scarf loop, turquoise diagonal jacket and open forward-running posture.

### Materials and surface detail

Waxed cloth, soft leather and minimal brushed metal. No transparent cape or spark trail during normal walking.

### Back and side-view constraints

A route-map case sits close to the lower back, with a broad sash crossing above it. The scarf loop uses a few stiff bones rather than simulated cloth.

## Combat statistics — without traits or temporary effects

| Property | One star | Two stars | Three stars |
|---|---:|---:|---:|
| Health | 820 | 1,476 | 2,656.8 |
| Basic attack damage | 67 | 120.6 | 217.08 |
| Attack delivery | melee | melee | melee |
| Basic damage type | physical | physical | physical |
| Nominal attacks/second | 1.00 | 1.00 | 1.00 |
| Effective attacks/second at 20 Hz | 1.0000 | 1.0000 | 1.0000 |
| Range in tiles | 1 | 1 | 1 |
| Physical armor | 15 | 15 | 15 |
| Magic resistance | 10 | 10 | 10 |
| Movement tiles/second | 1.25 | 1.25 | 1.25 |

Nominal basic-attack DPS at one star: **67.00**, before mitigation, movement, stuns, skills, targeting downtime or timing quantization. Basic windup: 250 ms; ordinary projectile travel: 0 ms. No hidden critical hits, evasion, lifesteal or mana.

## One active skill

### Quickstep

**Player tooltip:** Dashes beside the current target within three tiles.

**Indonesian draft:** Melakukan dash ke petak kosong di samping sasaran saat ini.

| Contract field | Value |
|---|---|
| Stable ability ID | `wc_a_orc_rogue` |
| Effect / target selector | `dash` / `current_enemy_adjacent` |
| One / two / three star magnitude | dash: Not applicable / Not applicable / Not applicable |
| Damage type | Not damaging |
| First-cast delay / cooldown | 1.5 s / 6.5 s |
| Windup / recovery | 0.2 s / 0.15 s |
| Effect duration | 0.0 s |
| Skill reach / area radius | 4 / 0 tiles |
| Can include self | False |
| Max dash distance | 3 tiles |
| Projectile travel | 0 ms |
| Affected stat | Not applicable |

Cooldown starts at successful cast commitment. An interrupted committed cast keeps its cooldown; an unavailable target leaves the ability ready and allows ordinary behavior. Area centers and area recipients are captured at release. Targeted projectiles keep their target ID but never retarget a defeated unit. Dash landing is reserved at commitment and validated before movement. See the rules contract for same-tick ordering, shield replacement and refresh semantics.

Health and basic damage use 1.00/1.80/3.24 star multipliers. Only explicitly authored skill magnitudes vary with stars; stun duration, range, radius, dash distance, cooldown and model footprint do not grow. A status-only skill may deliberately have identical behavior across stars; its owner still gains health and basic damage.

## Positioning and counterplay

**Preferred formation.** A flank near the front, with a path toward a vulnerable current target rather than an isolated leap across the entire board.

**Useful partners.** Sylas completes Rogue; Rok makes an effective nearby damage partner.

**Counterplay.** Protect the current target with occupied neighboring cells or a durable control unit.

**Practical weakness.** Short dash and modest defenses; cannot automatically select the farthest support like Sylas.

**Difference from the nearest alternative.** Kesh chases the existing target; Sylas selects the farthest enemy and has a longer cooldown.

**Character-specific acceptance test.** Never consume cooldown when already adjacent with no improving destination; landing reservation must release on interrupt.

## Animation, effects and sound

Idle is ready to run, not constantly bouncing. Basics use economical alternating motions. The active lowers the lead shoulder and makes one fast grounded glide to the reserved cell.

**Skill effect:** A short pale-cyan streak hugs the ground; mark the landing rather than hiding the unit. No implicit extra strike or slow.

**Sound:** A quick brushed-wind accent and light foot landing. Separate the cue from Sylas’s longer dash with a shorter pitch envelope.

Author at 60 FPS, as in-place animations with no locomotion-driven root translation. Required clips: Idle, Move, Attack, Active, Hit, Defeat, Victory. The active release marker is frame 12 relative to animation start. Basic release marker is frame 15. These are presentation alignment points, not sources of authoritative damage. Idle begins as a 2-second loop; movement as a 1-second cycle; hit as 0.4 seconds; defeat as 1 second; victory as 1.5 seconds. Adjust clip lengths during animation review without altering gameplay timing.

A defeat uses a brief stagger, kneel or magical dissolve with no injury detail. Stars use UI pips, a subtle trim accent and a brief upgrade flourish; do not produce three separate bodies or enlarge the collision footprint.

## Blender construction and Unreal handoff

Start from the `humanoid_broad` base or a validated compatible family. Block silhouette before bevels; separate body, costume and equipment into named source collections. Build equipment as decorative fantasy game props, not real functional objects. Author model-space Z up and a consistent forward orientation, then prove conversion with the calibration fixture. Materials use one or two runtime slots and a shared atlas where it preserves identity.

Targets to profile: at most 15,000 LOD0 triangles, 1024-pixel default maps, up to 60 deforming bones and 4 influences per vertex. Lower-detail targets begin near 50% and 25% triangles. These are budgets, not measured performance.

Sockets: `weapon_r`, `weapon_l`, `cast_origin`, `head_ui`. Inspect shoulder, elbow, hip and knee extremes. Use separate rig proportions where needed; matching bone names is not proof of animation compatibility. Selection uses a stable unit proxy, not detailed prop collision. Team affiliation uses base rings/icons in addition to color, never a complete costume recolor.

**Specific production risk:** The landing must reduce distance to the current target; otherwise a ready skill could loop without tactical purpose. Test same-tick target movement and blocked cells.

Required source/export locations:

- blender: `art-source/heroes/wc_u_orc_rogue/wc_u_orc_rogue.blend`

- mesh_fbx: `exports/heroes/wc_u_orc_rogue/SK_wc_u_orc_rogue.fbx`

- unreal_folder: `/Game/WonderChess/Heroes/wc_u_orc_rogue`

- portrait: `exports/heroes/wc_u_orc_rogue/portrait.png`

Create separate animation exports and texture maps, a model-derived portrait, front/side/back/three-quarter views, a gameplay-camera screenshot, and an actual Unreal animation capture. Log source/export hashes, skeleton revision, tool versions and import preset. Deliberately change one costume detail, re-export and verify existing material, skeleton, animation and actor references survive.

## Model-sheet generation brief

Original Wonder Chess high-fantasy character production sheet for Kesh Quickwind, The Ridge Courier. Orc Rogue, adult character, height 1.93 m. Front, true side, back and three-quarter views at matching scale, neutral A-pose plus one action pose. A narrow athletic wedge with a high scarf loop, short rounded shoulder guards and two compact hooked fantasy blades. The overall shape is tall and light rather than Rok’s broad mantle. Muted jade skin, brown eyes, small tusks and cropped dark hair with a pale cloth tie. An easy grin distinguishes him from a stereotypically menacing Rogue. Turquoise courier jacket over charcoal cloth, a tan diagonal sash and light wrapped boots. Large route-marker patches replace armor clutter. Two short rounded fantasy blades and a flat map case on the hip. Keep the implements stylized and visually simpler than Sylas’s curves. Palette: Turquoise #408E91; tan #C1A477; charcoal #3D4C4E; muted jade #708D72. Flat neutral background, orthographic construction views, equipment inset, readable seams, non-graphic stylized fantasy. No copied franchise designs, text baked into textures, cinematic fog, invented extra limbs or altered gear between views. These are concept directions, not generated images.

## Approval gates

Silhouette passes at 96-pixel preview; costume agrees across all views; all seven clips reviewed; no required missing textures; no unexplained import scale compensation; effect matches declared reach and damage type; portrait agrees with the modeled hero; crowded-board test passes; source revision/reimport is demonstrated. A Python exit code alone does not approve the art.

Canonical source: `data/units.json`. Regenerate this dossier with `python tools/build_documents.py` after data edits. Do not hand-edit a stat table and leave the JSON unchanged.

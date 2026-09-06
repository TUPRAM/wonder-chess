# Tessa Brassbolt — The Clockwork Marksman

**Dwarf · Ranger · Ranged damage · ALPHA**

Stable identity: `wc_u_dwarf_ranger`. Cost: **2 gold**. Rarity label: **Uncommon**, separate from star level. Status: designed, not modeled or implemented by this kit. All combat values are provisional prototype inputs.

## Character and world

Tessa builds reliable tools for Stoneveil’s long-distance couriers and tests every invention herself. She joined the trials to show that dwarven craft can support a team without adding another suit of heavy armor. Borin is her favorite test partner because he notices every rattle, and Liora is the rival whose accuracy she quietly admires.

Home region: `stoneveil`. Affiliation: `hearthwright_union`. Neither supplies a hidden third synergy. Proper names are original proposed fiction, not trademark-clearance claims.

## Appearance and art direction

Authored standing height: **1.32 m**, excluding raised equipment. Rig family: `humanoid_stocky`. One logical tile at every star. All characters are adults, fully clothed and presented as non-graphic heroic fantasy.

### Silhouette and proportions

A compact upright body with a wide horizontal crossbow and a high single-lens goggle shape above the forehead. A short jacket flares just enough to contrast with the weapon bar.

### Face, hair and expression

Freckled medium-brown skin, dark eyes, cropped copper hair and a confident grin. Goggles sit above the eyes during normal play so expressions remain visible.

### Costume construction

Mustard work jacket over charcoal padding, leather forearm guards, sturdy trousers and broad boots. A few oversized straps suggest workshop practicality.

### Color palette

Mustard #C5A04B; charcoal #404851; copper #B67B55; pale linen #D9CDAF.

### Equipment and magical focus

A broad stylized crank crossbow with exaggerated fantasy housing and a circular side wheel. It is a game prop, not a functional construction plan; mechanisms remain decorative.

### Three low-resolution identifiers

Horizontal crossbow silhouette, forehead goggles and mustard jacket.

### Materials and surface detail

Worn painted wood, brushed copper, matte leather and a tiny cool aiming-gem emissive point. Do not use transparent scope glass.

### Back and side-view constraints

A flat bolt case is strapped low between the shoulders; jacket seams form a large X. Keep all parts outside the elbows’ reload arc.

## Combat statistics — without traits or temporary effects

| Property | One star | Two stars | Three stars |
|---|---:|---:|---:|
| Health | 760 | 1,368 | 2,462.4 |
| Basic attack damage | 68 | 122.4 | 220.32 |
| Attack delivery | ranged | ranged | ranged |
| Basic damage type | physical | physical | physical |
| Nominal attacks/second | 0.80 | 0.80 | 0.80 |
| Effective attacks/second at 20 Hz | 0.8000 | 0.8000 | 0.8000 |
| Range in tiles | 4 | 4 | 4 |
| Physical armor | 20 | 20 | 20 |
| Magic resistance | 10 | 10 | 10 |
| Movement tiles/second | 0.95 | 0.95 | 0.95 |

Nominal basic-attack DPS at one star: **54.40**, before mitigation, movement, stuns, skills, targeting downtime or timing quantization. Basic windup: 300 ms; ordinary projectile travel: 150 ms. No hidden critical hits, evasion, lifesteal or mana.

## One active skill

### Heavy Bolt

**Player tooltip:** Fires a stronger physical shot at her current target.

**Indonesian draft:** Memberikan kerusakan fisik kepada sasaran saat ini.

| Contract field | Value |
|---|---|
| Stable ability ID | `wc_a_dwarf_ranger` |
| Effect / target selector | `damage` / `current_enemy` |
| One / two / three star magnitude | 170 / 306 / 551 |
| Damage type | physical |
| First-cast delay / cooldown | 2.5 s / 6.5 s |
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

**Preferred formation.** Backline behind protection, with a clear visual lane and space for the crossbow’s silhouette.

**Useful partners.** Liora completes Ranger; Elin increases ordinary shots between Heavy Bolt casts.

**Counterplay.** Armor reduces both her basics and her active; backline pressure can interrupt the long active windup.

**Practical weakness.** No mobility or area damage, and a shot expires if its target is already defeated.

**Difference from the nearest alternative.** Liora trades burst for movement; Tessa is a stationary physical-damage specialist.

**Character-specific acceptance test.** Heavy Bolt uses ability damage rules, not the Ranger basic-only bonus; source Orclike bonuses must not appear on a Dwarf.

## Animation, effects and sound

Idle checks the line of sight with a small tilt. Basics brace, fire and reset the bow. The active plants both feet, pulls the housing close and releases with a longer visible windup than a basic shot.

**Skill effect:** A bright compact bolt with a short trail and a sharp target flash. It never pierces or explodes.

**Sound:** A dry mechanical click and compact fantasy bow thump; the active adds a short metallic accent rather than a firearm report.

Author at 60 FPS, as in-place animations with no locomotion-driven root translation. Required clips: Idle, Move, Attack, Active, Hit, Defeat, Victory. The active release marker is frame 21 relative to animation start. Basic release marker is frame 18. These are presentation alignment points, not sources of authoritative damage. Idle begins as a 2-second loop; movement as a 1-second cycle; hit as 0.4 seconds; defeat as 1 second; victory as 1.5 seconds. Adjust clip lengths during animation review without altering gameplay timing.

A defeat uses a brief stagger, kneel or magical dissolve with no injury detail. Stars use UI pips, a subtle trim accent and a brief upgrade flourish; do not produce three separate bodies or enlarge the collision footprint.

## Blender construction and Unreal handoff

Start from the `humanoid_stocky` base or a validated compatible family. Block silhouette before bevels; separate body, costume and equipment into named source collections. Build equipment as decorative fantasy game props, not real functional objects. Author model-space Z up and a consistent forward orientation, then prove conversion with the calibration fixture. Materials use one or two runtime slots and a shared atlas where it preserves identity.

Targets to profile: at most 15,000 LOD0 triangles, 1024-pixel default maps, up to 60 deforming bones and 4 influences per vertex. Lower-detail targets begin near 50% and 25% triangles. These are budgets, not measured performance.

Sockets: `weapon_r`, `weapon_l`, `cast_origin`, `head_ui`. Inspect shoulder, elbow, hip and knee extremes. Use separate rig proportions where needed; matching bone names is not proof of animation compatibility. Selection uses a stable unit proxy, not detailed prop collision. Team affiliation uses base rings/icons in addition to color, never a complete costume recolor.

**Specific production risk:** The wide prop can overlap neighboring units. Use its lowered rest pose outside windup and a close-to-body turn pose.

Required source/export locations:

- blender: `art-source/heroes/wc_u_dwarf_ranger/wc_u_dwarf_ranger.blend`

- mesh_fbx: `exports/heroes/wc_u_dwarf_ranger/SK_wc_u_dwarf_ranger.fbx`

- unreal_folder: `/Game/WonderChess/Heroes/wc_u_dwarf_ranger`

- portrait: `exports/heroes/wc_u_dwarf_ranger/portrait.png`

Create separate animation exports and texture maps, a model-derived portrait, front/side/back/three-quarter views, a gameplay-camera screenshot, and an actual Unreal animation capture. Log source/export hashes, skeleton revision, tool versions and import preset. Deliberately change one costume detail, re-export and verify existing material, skeleton, animation and actor references survive.

## Model-sheet generation brief

Original Wonder Chess high-fantasy character production sheet for Tessa Brassbolt, The Clockwork Marksman. Dwarf Ranger, adult character, height 1.32 m. Front, true side, back and three-quarter views at matching scale, neutral A-pose plus one action pose. A compact upright body with a wide horizontal crossbow and a high single-lens goggle shape above the forehead. A short jacket flares just enough to contrast with the weapon bar. Freckled medium-brown skin, dark eyes, cropped copper hair and a confident grin. Goggles sit above the eyes during normal play so expressions remain visible. Mustard work jacket over charcoal padding, leather forearm guards, sturdy trousers and broad boots. A few oversized straps suggest workshop practicality. A broad stylized crank crossbow with exaggerated fantasy housing and a circular side wheel. It is a game prop, not a functional construction plan; mechanisms remain decorative. Palette: Mustard #C5A04B; charcoal #404851; copper #B67B55; pale linen #D9CDAF. Flat neutral background, orthographic construction views, equipment inset, readable seams, non-graphic stylized fantasy. No copied franchise designs, text baked into textures, cinematic fog, invented extra limbs or altered gear between views. These are concept directions, not generated images.

## Approval gates

Silhouette passes at 96-pixel preview; costume agrees across all views; all seven clips reviewed; no required missing textures; no unexplained import scale compensation; effect matches declared reach and damage type; portrait agrees with the modeled hero; crowded-board test passes; source revision/reimport is demonstrated. A Python exit code alone does not approve the art.

Canonical source: `data/units.json`. Regenerate this dossier with `python tools/build_documents.py` after data edits. Do not hand-edit a stat table and leave the JSON unchanged.

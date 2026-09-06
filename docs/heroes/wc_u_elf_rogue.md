# Sylas Duskrun — The Lantern Runner

**Elf · Rogue · Disruption · ALPHA**

Stable identity: `wc_u_elf_rogue`. Cost: **3 gold**. Rarity label: **Rare**, separate from star level. Production and verification status is recorded separately in reports/implementation_state.json; this generated dossier does not certify an asset or build. All combat values are provisional prototype inputs.

Quick display name: **Sylas**. Informational roles: Control. Role tags provide no additional synergy.

## Character and world

Sylas carried lantern messages between isolated settlements when the main roads were closed. He is proud of arriving on time, less proud of the shortcuts that occasionally alarm his friends. Liora recruits him for the trials because he understands how a formation can have safe-looking gaps that are not safe at all.

Home region: `thistlewood`. Affiliation: `greenward_circle`. Neither supplies a hidden third synergy. Proper names are original proposed fiction, not trademark-clearance claims.

## Appearance and art direction

Authored standing height: **1.9 m**, excluding raised equipment. Rig family: `humanoid_slender`. One logical tile at every star. All characters are adults, fully clothed and presented as non-graphic heroic fantasy.

### Silhouette and proportions

A low asymmetrical stance with a short diagonal mantle, one raised scarf end and paired curved fantasy blades. His shoulders form a compact wedge rather than a broad warrior line.

### Face, hair and expression

Light bronze skin, dark hair swept to one side and narrow amber eyes. Keep the lower face visible, with no full mask that resembles a different character identity.

### Costume construction

Dusk-blue leather panels over pale gray cloth, light knee guards and a cross-body courier strap. The mantle covers only the left shoulder and ends at the waist.

### Color palette

Dusk blue #3B4E6B; fog gray #BAC5CC; muted violet #786A8C; lantern amber #D2A35D.

### Equipment and magical focus

Two short stylized curved blades and a small shielded courier lantern fixed to the belt. The lantern is a visual cue, not a source of stealth or detection gameplay.

### Three low-resolution identifiers

Single-shoulder mantle, paired curved silhouettes, and low forward stance.

### Materials and surface detail

Supple matte leather, soft fabric and restrained brushed metal. No black-on-black costume and no constant translucent body.

### Back and side-view constraints

Courier strap ends in a flat document case between the shoulder blades. Keep the case clear of both draw arcs.

## Combat statistics — without traits or temporary effects

| Property | One star | Two stars | Three stars |
|---|---:|---:|---:|
| Health | 790 | 1,422 | 2,559.6 |
| Basic attack damage | 74 | 133.2 | 239.76 |
| Attack delivery | melee | melee | melee |
| Basic damage type | physical | physical | physical |
| Nominal attacks/second | 1.05 | 1.05 | 1.05 |
| Effective attacks/second at 20 Hz | 1.0000 | 1.0000 | 1.0000 |
| Range in tiles | 1 | 1 | 1 |
| Physical armor | 18 | 18 | 18 |
| Magic resistance | 12 | 12 | 12 |
| Movement tiles/second | 1.25 | 1.25 | 1.25 |

Nominal basic-attack DPS at one star: **77.70**, before mitigation, movement, stuns, skills, targeting downtime or timing quantization. Basic windup: 250 ms; ordinary projectile travel: 0 ms. No hidden critical hits, evasion, lifesteal or mana.

## One active skill

### Backline Leap

**Player tooltip:** Dashes beside the farthest enemy when a landing tile is free.

**Indonesian draft:** Melakukan dash ke petak kosong di samping musuh terjauh.

| Contract field | Value |
|---|---|
| Stable ability ID | `wc_a_elf_rogue` |
| Effect / target selector | `dash` / `farthest_enemy_adjacent` |
| One / two / three star magnitude | dash: Not applicable / Not applicable / Not applicable |
| Damage type | Not damaging |
| First-cast delay / cooldown | 1 s / 8.5 s |
| Windup / recovery | 0.2 s / 0.15 s |
| Effect duration | 0.0 s |
| Skill reach / area radius | 8 / 0 tiles |
| Can include self | False |
| Max dash distance | 7 tiles |
| Projectile travel | 0 ms |
| Affected stat | Not applicable |

Cooldown starts at successful cast commitment. An interrupted committed cast keeps its cooldown; an unavailable target leaves the ability ready and allows ordinary behavior. Area centers and area recipients are captured at release. Targeted projectiles keep their target ID but never retarget a defeated unit. Dash landing is reserved at commitment and validated before movement. See the rules contract for same-tick ordering, shield replacement and refresh semantics.

Health and basic damage use 1.00/1.80/3.24 star multipliers. Only explicitly authored skill magnitudes vary with stars; stun duration, range, radius, dash distance, cooldown and model footprint do not grow. A status-only skill may deliberately have identical behavior across stars; its owner still gains health and basic damage.

## Positioning and counterplay

**Preferred formation.** A flank with an unobstructed initial approach; keep him out of immediate focus before the first dash.

**Useful partners.** Kesh completes Rogue and helps pressure the backline, while a Guardian draws ordinary frontline targeting.

**Counterplay.** Reserve a durable unit beside vulnerable supports and avoid leaving every backline neighbor empty.

**Practical weakness.** He can land in a dangerous formation and has no escape immunity; the dash itself does no damage.

**Difference from the nearest alternative.** Kesh closes on the current target over a short distance; Sylas seeks the farthest enemy over the board.

**Character-specific acceptance test.** Validate farthest-target ties, free landing selection, no available landing, and donor ghost clones preserving the skill timer.

## Animation, effects and sound

Idle balances on the balls of the feet. Walk uses quick narrow steps. Basics alternate readable cuts. The active compresses into a low stance and launches along a single clean line; no teleport smoke hides the destination.

**Skill effect:** A brief blue ribbon connects origin and landing, with a small landing ring. No bonus hit, invisibility, invulnerability or untargetability is implied.

**Sound:** Short cloth snap and crisp magical sweep for the dash; attacks remain light rather than explosive.

Author at 60 FPS, as in-place animations with no locomotion-driven root translation. Required clips: Idle, Move, Attack, Active, Hit, Defeat, Victory. The active release marker is frame 12 relative to animation start. Basic release marker is frame 15. These are presentation alignment points, not sources of authoritative damage. Idle begins as a 2-second loop; movement as a 1-second cycle; hit as 0.4 seconds; defeat as 1 second; victory as 1.5 seconds. Adjust clip lengths during animation review without altering gameplay timing.

A defeat uses a brief stagger, kneel or magical dissolve with no injury detail. Stars use UI pips, a subtle trim accent and a brief upgrade flourish; do not produce three separate bodies or enlarge the collision footprint.

## Blender construction and Unreal handoff

Start from the `humanoid_slender` base or a validated compatible family. Block silhouette before bevels; separate body, costume and equipment into named source collections. Build equipment as decorative fantasy game props, not real functional objects. Author model-space Z up and a consistent forward orientation, then prove conversion with the calibration fixture. Materials use one or two runtime slots and a shared atlas where it preserves identity.

Targets to profile: at most 15,000 LOD0 triangles, 1024-pixel default maps, up to 60 deforming bones and 4 influences per vertex. Lower-detail targets begin near 50% and 25% triangles. These are budgets, not measured performance.

Sockets: `weapon_r`, `weapon_l`, `cast_origin`, `head_ui`. Inspect shoulder, elbow, hip and knee extremes. Use separate rig proportions where needed; matching bone names is not proof of animation compatibility. Selection uses a stable unit proxy, not detailed prop collision. Team affiliation uses base rings/icons in addition to color, never a complete costume recolor.

**Specific production risk:** The dash can be tactically too strong against fragile backlines. Keep damage in normal attacks and test crowding, target validity and front/back targeting after landing.

Required source/export locations:

- blender: `art-source/heroes/wc_u_elf_rogue/wc_u_elf_rogue.blend`

- mesh_fbx: `exports/heroes/wc_u_elf_rogue/SK_wc_u_elf_rogue.fbx`

- unreal_folder: `/Game/WonderChess/Heroes/wc_u_elf_rogue`

- portrait: `exports/heroes/wc_u_elf_rogue/portrait.png`

Create separate animation exports and texture maps, a model-derived portrait, front/side/back/three-quarter views, a gameplay-camera screenshot, and an actual Unreal animation capture. Log source/export hashes, skeleton revision, tool versions and import preset. Deliberately change one costume detail, re-export and verify existing material, skeleton, animation and actor references survive.

## Model-sheet generation brief

Original Wonder Chess high-fantasy character production sheet for Sylas Duskrun, The Lantern Runner. Elf Rogue, adult character, height 1.9 m. Front, true side, back and three-quarter views at matching scale, neutral A-pose plus one action pose. A low asymmetrical stance with a short diagonal mantle, one raised scarf end and paired curved fantasy blades. His shoulders form a compact wedge rather than a broad warrior line. Light bronze skin, dark hair swept to one side and narrow amber eyes. Keep the lower face visible, with no full mask that resembles a different character identity. Dusk-blue leather panels over pale gray cloth, light knee guards and a cross-body courier strap. The mantle covers only the left shoulder and ends at the waist. Two short stylized curved blades and a small shielded courier lantern fixed to the belt. The lantern is a visual cue, not a source of stealth or detection gameplay. Palette: Dusk blue #3B4E6B; fog gray #BAC5CC; muted violet #786A8C; lantern amber #D2A35D. Flat neutral background, orthographic construction views, equipment inset, readable seams, non-graphic stylized fantasy. No copied franchise designs, text baked into textures, cinematic fog, invented extra limbs or altered gear between views. These are concept directions, not generated images.

## Approval gates

Silhouette passes at 96-pixel preview; costume agrees across all views; all seven clips reviewed; no required missing textures; no unexplained import scale compensation; effect matches declared reach and damage type; portrait agrees with the modeled hero; crowded-board test passes; source revision/reimport is demonstrated. A Python exit code alone does not approve the art.

Canonical source: `data/units.json`. Regenerate this dossier with `python tools/build_documents.py` after data edits. Do not hand-edit a stat table and leave the JSON unchanged.

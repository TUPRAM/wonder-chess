# Neris Starbloom — The Observatory Keeper

**Elf · Mage · Spell damage · EXPANSION**

Stable identity: `wc_u_elf_mage`. Cost: **3 gold**. Rarity label: **Rare**, separate from star level. Status: designed, not modeled or implemented by this kit. All combat values are provisional prototype inputs.

## Character and world

Neris maintains Thistlewood’s hill observatory, where travelers once gathered to compare calendars. Unusual lights over Cindercrest led her to exchange observations with Oren. She attends the trials to learn how a precisely timed interruption can protect an expedition more reliably than a spectacular but poorly placed spell.

Home region: `thistlewood`. Affiliation: `greenward_circle`. Neither supplies a hidden third synergy. Proper names are original proposed fiction, not trademark-clearance claims.

## Appearance and art direction

Authored standing height: **1.91 m**, excluding raised equipment. Rig family: `humanoid_slender`. One logical tile at every star. All characters are adults, fully clothed and presented as non-graphic heroic fantasy.

### Silhouette and proportions

A narrow column of layered robes topped by a wide broken-circle headpiece. A small star-lens disk rests in the open left hand instead of a long staff.

### Face, hair and expression

Cool brown skin, pale violet eyes and midnight-blue hair braided into a smooth low knot. Long ears extend beneath the open headpiece.

### Costume construction

Violet coat over pale blue layered cloth, a fitted waist sash and short split lower panels. The headpiece is one bold arc, not a crown of many spikes.

### Color palette

Violet #7465A5; pale blue #B4CADD; midnight #3E4166; pearl #E0E3D9.

### Equipment and magical focus

A palm-sized star-lens in a thick silver ring and a flat chart case at the hip. Presentation magic is anchored to hand sockets.

### Three low-resolution identifiers

Broken-circle headpiece, open-hand star lens and clean vertical silhouette.

### Materials and surface detail

Satin-like cloth with restrained specular response, brushed silver and a small emissive star. Keep the face the brightest non-emissive plane.

### Back and side-view constraints

Long central seam and two overlapping panels create an open lower-leg gap. The chart case sits against the belt and cannot swing freely.

## Combat statistics — without traits or temporary effects

| Property | One star | Two stars | Three stars |
|---|---:|---:|---:|
| Health | 690 | 1,242 | 2,235.6 |
| Basic attack damage | 48 | 86.4 | 155.52 |
| Attack delivery | ranged | ranged | ranged |
| Basic damage type | magic | magic | magic |
| Nominal attacks/second | 0.75 | 0.75 | 0.75 |
| Effective attacks/second at 20 Hz | 0.7407 | 0.7407 | 0.7407 |
| Range in tiles | 4 | 4 | 4 |
| Physical armor | 8 | 8 | 8 |
| Magic resistance | 30 | 30 | 30 |
| Movement tiles/second | 1.05 | 1.05 | 1.05 |

Nominal basic-attack DPS at one star: **36.00**, before mitigation, movement, stuns, skills, targeting downtime or timing quantization. Basic windup: 300 ms; ordinary projectile travel: 150 ms. No hidden critical hits, evasion, lifesteal or mana.

## One active skill

### Starbind

**Player tooltip:** Stuns the current target for one and a quarter seconds.

**Indonesian draft:** Melumpuhkan sementara sasaran saat ini.

| Contract field | Value |
|---|---|
| Stable ability ID | `wc_a_elf_mage` |
| Effect / target selector | `stun` / `current_enemy` |
| One / two / three star magnitude | Not applicable / Not applicable / Not applicable |
| Damage type | Not damaging |
| First-cast delay / cooldown | 3.5 s / 9.5 s |
| Windup / recovery | 0.4 s / 0.3 s |
| Effect duration | 1.25 s |
| Skill reach / area radius | 4 / 0 tiles |
| Can include self | False |
| Max dash distance | 0 tiles |
| Projectile travel | 200 ms |
| Affected stat | Not applicable |

Cooldown starts at successful cast commitment. An interrupted committed cast keeps its cooldown; an unavailable target leaves the ability ready and allows ordinary behavior. Area centers and area recipients are captured at release. Targeted projectiles keep their target ID but never retarget a defeated unit. Dash landing is reserved at commitment and validated before movement. See the rules contract for same-tick ordering, shield replacement and refresh semantics.

Health and basic damage use 1.00/1.80/3.24 star multipliers. Only explicitly authored skill magnitudes vary with stars; stun duration, range, radius, dash distance, cooldown and model footprint do not grow. A status-only skill may deliberately have identical behavior across stars; its owner still gains health and basic damage.

## Positioning and counterplay

**Preferred formation.** Protected backline with range to interrupt a dangerous current target.

**Useful partners.** Rowan or Zura gains the damage-bearing benefit of a Mage pair; Neris contributes the count but her nondamaging active receives no bonus. Liora supplies Elf.

**Counterplay.** Several moderate threats reduce the value of locking one target; a flanker can force a poor current target.

**Practical weakness.** Her active deals no damage and has a long cooldown. Mage ability-damage bonus intentionally does not benefit Starbind.

**Difference from the nearest alternative.** Borin controls a nearby group; Neris interrupts one distant opponent for slightly longer.

**Character-specific acceptance test.** Projectile may expire on a defeated target; its 1250 ms control remains constant at all star levels.

## Animation, effects and sound

Idle follows the lens with a small eye-line shift. Basics flick a pale spark. Starbind raises the lens to eye level, aligns both palms and releases one small star toward the target.

**Skill effect:** A pale violet projectile and a geometric ring hovering above the stunned target. No chains, root effect or damage are added.

**Sound:** A clean glass note with a short crystalline arrival tone. No long loop while the target is stunned.

Author at 60 FPS, as in-place animations with no locomotion-driven root translation. Required clips: Idle, Move, Attack, Active, Hit, Defeat, Victory. The active release marker is frame 24 relative to animation start. Basic release marker is frame 18. These are presentation alignment points, not sources of authoritative damage. Idle begins as a 2-second loop; movement as a 1-second cycle; hit as 0.4 seconds; defeat as 1 second; victory as 1.5 seconds. Adjust clip lengths during animation review without altering gameplay timing.

A defeat uses a brief stagger, kneel or magical dissolve with no injury detail. Stars use UI pips, a subtle trim accent and a brief upgrade flourish; do not produce three separate bodies or enlarge the collision footprint.

## Blender construction and Unreal handoff

Start from the `humanoid_slender` base or a validated compatible family. Block silhouette before bevels; separate body, costume and equipment into named source collections. Build equipment as decorative fantasy game props, not real functional objects. Author model-space Z up and a consistent forward orientation, then prove conversion with the calibration fixture. Materials use one or two runtime slots and a shared atlas where it preserves identity.

Targets to profile: at most 15,000 LOD0 triangles, 1024-pixel default maps, up to 60 deforming bones and 4 influences per vertex. Lower-detail targets begin near 50% and 25% triangles. These are budgets, not measured performance.

Sockets: `weapon_r`, `weapon_l`, `cast_origin`, `head_ui`. Inspect shoulder, elbow, hip and knee extremes. Use separate rig proportions where needed; matching bone names is not proof of animation compatibility. Selection uses a stable unit proxy, not detailed prop collision. Team affiliation uses base rings/icons in addition to color, never a complete costume recolor.

**Specific production risk:** The headpiece can alias at low resolution; thicken it and test against bright sky. The control duration must not scale with stars.

Required source/export locations:

- blender: `art-source/heroes/wc_u_elf_mage/wc_u_elf_mage.blend`

- mesh_fbx: `exports/heroes/wc_u_elf_mage/SK_wc_u_elf_mage.fbx`

- unreal_folder: `/Game/WonderChess/Heroes/wc_u_elf_mage`

- portrait: `exports/heroes/wc_u_elf_mage/portrait.png`

Create separate animation exports and texture maps, a model-derived portrait, front/side/back/three-quarter views, a gameplay-camera screenshot, and an actual Unreal animation capture. Log source/export hashes, skeleton revision, tool versions and import preset. Deliberately change one costume detail, re-export and verify existing material, skeleton, animation and actor references survive.

## Model-sheet generation brief

Original Wonder Chess high-fantasy character production sheet for Neris Starbloom, The Observatory Keeper. Elf Mage, adult character, height 1.91 m. Front, true side, back and three-quarter views at matching scale, neutral A-pose plus one action pose. A narrow column of layered robes topped by a wide broken-circle headpiece. A small star-lens disk rests in the open left hand instead of a long staff. Cool brown skin, pale violet eyes and midnight-blue hair braided into a smooth low knot. Long ears extend beneath the open headpiece. Violet coat over pale blue layered cloth, a fitted waist sash and short split lower panels. The headpiece is one bold arc, not a crown of many spikes. A palm-sized star-lens in a thick silver ring and a flat chart case at the hip. Presentation magic is anchored to hand sockets. Palette: Violet #7465A5; pale blue #B4CADD; midnight #3E4166; pearl #E0E3D9. Flat neutral background, orthographic construction views, equipment inset, readable seams, non-graphic stylized fantasy. No copied franchise designs, text baked into textures, cinematic fog, invented extra limbs or altered gear between views. These are concept directions, not generated images.

## Approval gates

Silhouette passes at 96-pixel preview; costume agrees across all views; all seven clips reviewed; no required missing textures; no unexplained import scale compensation; effect matches declared reach and damage type; portrait agrees with the modeled hero; crowded-board test passes; source revision/reimport is demonstrated. A Python exit code alone does not approve the art.

Canonical source: `data/units.json`. Regenerate this dossier with `python tools/build_documents.py` after data edits. Do not hand-edit a stat table and leave the JSON unchanged.

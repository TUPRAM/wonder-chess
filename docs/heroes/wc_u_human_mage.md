# Rowan Emberwick — The Hearth Scholar

**Human · Mage · Spell damage · ALPHA**

Stable identity: `wc_u_human_mage`. Cost: **2 gold**. Rarity label: **Uncommon**, separate from star level. Status: designed, not modeled or implemented by this kit. All combat values are provisional prototype inputs.

## Character and world

Rowan studied old heating runes because he wanted every winter home in Brighthaven to be warm. A damaged ward exposed how those same patterns could defend a road from magical intruders. He dislikes grand speeches but joins the trials to translate useful research into dependable field practice, often testing his theories against Zura’s storm lessons.

Home region: `brighthaven`. Affiliation: `dawn_compact`. Neither supplies a hidden third synergy. Proper names are original proposed fiction, not trademark-clearance claims.

## Appearance and art direction

Authored standing height: **1.78 m**, excluding raised equipment. Rig family: `humanoid_standard`. One logical tile at every star. All characters are adults, fully clothed and presented as non-graphic heroic fantasy.

### Silhouette and proportions

An angular, high folded collar above a tapered traveling coat, with a large open orb frame held beside the right shoulder. Broad sleeve cuffs distinguish him from staff-bearing Priests.

### Face, hair and expression

Copper-brown skin, round spectacles with thick readable rims, charcoal curls and an inquisitive half-smile. Use painted eyes rather than separate transparent lenses in the first pass.

### Costume construction

Indigo scholar’s coat over an amber vest, reinforced fabric cuffs and calf-high boots. The coat splits into two stiff tails at the hips; no cloth simulation is required.

### Color palette

Indigo #494774; amber #E2A148; parchment #E7D9B4; coal #38333E.

### Equipment and magical focus

A hovering presentation-only ember orb inside a hand-held bronze bracket; a closed book fixed to the belt. The orb is not a summoned combat unit.

### Three low-resolution identifiers

High folded collar, round spectacles, and bright orb within an asymmetrical frame.

### Materials and surface detail

Matte wool with broad color planes, worn bronze and a bounded emissive core. Reserve flame transparency for the brief active.

### Back and side-view constraints

Two coat tails form an inverted V, and a stitched star diagram sits high on the shoulders. The closed book does not intersect the thighs while walking.

## Combat statistics — without traits or temporary effects

| Property | One star | Two stars | Three stars |
|---|---:|---:|---:|
| Health | 620 | 1,116 | 2,008.8 |
| Basic attack damage | 45 | 81 | 145.8 |
| Attack delivery | ranged | ranged | ranged |
| Basic damage type | magic | magic | magic |
| Nominal attacks/second | 0.70 | 0.70 | 0.70 |
| Effective attacks/second at 20 Hz | 0.6897 | 0.6897 | 0.6897 |
| Range in tiles | 3 | 3 | 3 |
| Physical armor | 8 | 8 | 8 |
| Magic resistance | 20 | 20 | 20 |
| Movement tiles/second | 1.00 | 1.00 | 1.00 |

Nominal basic-attack DPS at one star: **31.50**, before mitigation, movement, stuns, skills, targeting downtime or timing quantization. Basic windup: 300 ms; ordinary projectile travel: 150 ms. No hidden critical hits, evasion, lifesteal or mana.

## One active skill

### Ember Orb

**Player tooltip:** Damages enemies around the target’s captured location.

**Indonesian draft:** Memberikan kerusakan sihir kepada musuh di area sasaran.

| Contract field | Value |
|---|---|
| Stable ability ID | `wc_a_human_mage` |
| Effect / target selector | `damage` / `current_enemy_area` |
| One / two / three star magnitude | 150 / 270 / 486 |
| Damage type | magic |
| First-cast delay / cooldown | 3.5 s / 8 s |
| Windup / recovery | 0.45 s / 0.3 s |
| Effect duration | 0 s |
| Skill reach / area radius | 4 / 1 tiles |
| Can include self | False |
| Max dash distance | 0 tiles |
| Projectile travel | 250 ms |
| Affected stat | Not applicable |

Cooldown starts at successful cast commitment. An interrupted committed cast keeps its cooldown; an unavailable target leaves the ability ready and allows ordinary behavior. Area centers and area recipients are captured at release. Targeted projectiles keep their target ID but never retarget a defeated unit. Dash landing is reserved at commitment and validated before movement. See the rules contract for same-tick ordering, shield replacement and refresh semantics.

Health and basic damage use 1.00/1.80/3.24 star multipliers. Only explicitly authored skill magnitudes vary with stars; stun duration, range, radius, dash distance, cooldown and model footprint do not grow. A status-only skill may deliberately have identical behavior across stars; its owner still gains health and basic damage.

## Positioning and counterplay

**Preferred formation.** Back or middle row with a stable frontline, positioned to target an enemy cluster early.

**Useful partners.** Borin Stonebell briefly holds nearby enemies together; Zura enables the Mage bonus.

**Counterplay.** Spread formations waste the area component; Kesh can close the distance to an isolated caster.

**Practical weakness.** Fragile, and the projectile resolves at a captured cell rather than following a moving target.

**Difference from the nearest alternative.** Rowan has a smaller, faster-targeted area burst than Zura’s wider delayed storm.

**Character-specific acceptance test.** Move the original target after release and prove the orb still hits only the captured area.

## Animation, effects and sound

Idle balances the orb with a restrained wrist movement. Move with compact forward steps. Basics flick a small spark. The active draws both hands inward then pushes the orb toward its captured ground location.

**Skill effect:** A small amber projectile expands into a low circular burst at the captured cell. Mark the radius briefly on the ground; no lingering fire damage exists.

**Sound:** A brief rising furnace note followed by a soft magical pop; omit crackling loops once the burst resolves.

Author at 60 FPS, as in-place animations with no locomotion-driven root translation. Required clips: Idle, Move, Attack, Active, Hit, Defeat, Victory. The active release marker is frame 27 relative to animation start. Basic release marker is frame 18. These are presentation alignment points, not sources of authoritative damage. Idle begins as a 2-second loop; movement as a 1-second cycle; hit as 0.4 seconds; defeat as 1 second; victory as 1.5 seconds. Adjust clip lengths during animation review without altering gameplay timing.

A defeat uses a brief stagger, kneel or magical dissolve with no injury detail. Stars use UI pips, a subtle trim accent and a brief upgrade flourish; do not produce three separate bodies or enlarge the collision footprint.

## Blender construction and Unreal handoff

Start from the `humanoid_standard` base or a validated compatible family. Block silhouette before bevels; separate body, costume and equipment into named source collections. Build equipment as decorative fantasy game props, not real functional objects. Author model-space Z up and a consistent forward orientation, then prove conversion with the calibration fixture. Materials use one or two runtime slots and a shared atlas where it preserves identity.

Targets to profile: at most 15,000 LOD0 triangles, 1024-pixel default maps, up to 60 deforming bones and 4 influences per vertex. Lower-detail targets begin near 50% and 25% triangles. These are budgets, not measured performance.

Sockets: `weapon_r`, `weapon_l`, `cast_origin`, `head_ui`. Inspect shoulder, elbow, hip and knee extremes. Use separate rig proportions where needed; matching bone names is not proof of animation compatibility. Selection uses a stable unit proxy, not detailed prop collision. Team affiliation uses base rings/icons in addition to color, never a complete costume recolor.

**Specific production risk:** The orb must be driven by a socket/presentation component, not physics. Camera brightness must not erase the unit or neighboring health bars.

Required source/export locations:

- blender: `art-source/heroes/wc_u_human_mage/wc_u_human_mage.blend`

- mesh_fbx: `exports/heroes/wc_u_human_mage/SK_wc_u_human_mage.fbx`

- unreal_folder: `/Game/WonderChess/Heroes/wc_u_human_mage`

- portrait: `exports/heroes/wc_u_human_mage/portrait.png`

Create separate animation exports and texture maps, a model-derived portrait, front/side/back/three-quarter views, a gameplay-camera screenshot, and an actual Unreal animation capture. Log source/export hashes, skeleton revision, tool versions and import preset. Deliberately change one costume detail, re-export and verify existing material, skeleton, animation and actor references survive.

## Model-sheet generation brief

Original Wonder Chess high-fantasy character production sheet for Rowan Emberwick, The Hearth Scholar. Human Mage, adult character, height 1.78 m. Front, true side, back and three-quarter views at matching scale, neutral A-pose plus one action pose. An angular, high folded collar above a tapered traveling coat, with a large open orb frame held beside the right shoulder. Broad sleeve cuffs distinguish him from staff-bearing Priests. Copper-brown skin, round spectacles with thick readable rims, charcoal curls and an inquisitive half-smile. Use painted eyes rather than separate transparent lenses in the first pass. Indigo scholar’s coat over an amber vest, reinforced fabric cuffs and calf-high boots. The coat splits into two stiff tails at the hips; no cloth simulation is required. A hovering presentation-only ember orb inside a hand-held bronze bracket; a closed book fixed to the belt. The orb is not a summoned combat unit. Palette: Indigo #494774; amber #E2A148; parchment #E7D9B4; coal #38333E. Flat neutral background, orthographic construction views, equipment inset, readable seams, non-graphic stylized fantasy. No copied franchise designs, text baked into textures, cinematic fog, invented extra limbs or altered gear between views. These are concept directions, not generated images.

## Approval gates

Silhouette passes at 96-pixel preview; costume agrees across all views; all seven clips reviewed; no required missing textures; no unexplained import scale compensation; effect matches declared reach and damage type; portrait agrees with the modeled hero; crowded-board test passes; source revision/reimport is demonstrated. A Python exit code alone does not approve the art.

Canonical source: `data/units.json`. Regenerate this dossier with `python tools/build_documents.py` after data edits. Do not hand-edit a stat table and leave the JSON unchanged.

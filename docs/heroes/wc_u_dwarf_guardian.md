# Borin Stonebell — The Bridge Sentinel

**Dwarf · Guardian · Defender · ALPHA**

Stable identity: `wc_u_dwarf_guardian`. Cost: **1 gold**. Rarity label: **Common**, separate from star level. Status: designed, not modeled or implemented by this kit. All combat values are provisional prototype inputs.

## Character and world

Borin supervised a narrow stone bridge into Stoneveil long before anyone called it a strategic crossing. He knows that a well-timed pause can prevent a crowd from becoming a crush. In the Compact trials he brings that patience to the frontline, while Tessa repeatedly tries to persuade him that a lighter hammer would be more convenient.

Home region: `stoneveil`. Affiliation: `hearthwright_union`. Neither supplies a hidden third synergy. Proper names are original proposed fiction, not trademark-clearance claims.

## Appearance and art direction

Authored standing height: **1.38 m**, excluding raised equipment. Rig family: `humanoid_stocky`. One logical tile at every star. All characters are adults, fully clothed and presented as non-graphic heroic fantasy.

### Silhouette and proportions

A compact rectangular torso beneath a domed helmet, with wide rounded shoulder plates and an oversized bell-headed hammer. Short legs stay separated enough to read during motion.

### Face, hair and expression

Ruddy tan skin, large brown brows and a thick brown beard divided into two broad braids. A hinged-looking open helmet never hides the eyes.

### Costume construction

Slate plate over a moss-green padded coat, heavy riveted boots and a wide belt with a single square buckle. Avoid dozens of small rivets; bake secondary details.

### Color palette

Slate #697A88; moss #6B7750; muted bronze #A58354; warm beard brown #76533A.

### Equipment and magical focus

A two-handed fantasy hammer shaped like a solid bell housing. Its broad rim helps the stomp animation read without an actual moving bell interior.

### Three low-resolution identifiers

Domed open helmet, paired beard braids and bell-shaped hammer head.

### Materials and surface detail

Rough forged metal, thick wool and a few worn bronze edges. Metal highlights should be broader and less bright than Ada’s polished crest.

### Back and side-view constraints

Overlapping short backplates terminate above the hips. Beard and shoulder plates need separate clearance zones during a downward cast.

## Combat statistics — without traits or temporary effects

| Property | One star | Two stars | Three stars |
|---|---:|---:|---:|
| Health | 1,100 | 1,980 | 3,564 |
| Basic attack damage | 44 | 79.2 | 142.56 |
| Attack delivery | melee | melee | melee |
| Basic damage type | physical | physical | physical |
| Nominal attacks/second | 0.65 | 0.65 | 0.65 |
| Effective attacks/second at 20 Hz | 0.6452 | 0.6452 | 0.6452 |
| Range in tiles | 1 | 1 | 1 |
| Physical armor | 40 | 40 | 40 |
| Magic resistance | 10 | 10 | 10 |
| Movement tiles/second | 0.90 | 0.90 | 0.90 |

Nominal basic-attack DPS at one star: **28.60**, before mitigation, movement, stuns, skills, targeting downtime or timing quantization. Basic windup: 250 ms; ordinary projectile travel: 0 ms. No hidden critical hits, evasion, lifesteal or mana.

## One active skill

### Bell Stomp

**Player tooltip:** Stuns adjacent enemies for one second.

**Indonesian draft:** Melumpuhkan sementara musuh di petak bersebelahan.

| Contract field | Value |
|---|---|
| Stable ability ID | `wc_a_dwarf_guardian` |
| Effect / target selector | `stun` / `adjacent_enemies` |
| One / two / three star magnitude | Not applicable / Not applicable / Not applicable |
| Damage type | Not damaging |
| First-cast delay / cooldown | 3 s / 8.5 s |
| Windup / recovery | 0.4 s / 0.3 s |
| Effect duration | 1 s |
| Skill reach / area radius | 1 / 1 tiles |
| Can include self | False |
| Max dash distance | 0 tiles |
| Projectile travel | 0 ms |
| Affected stat | Not applicable |

Cooldown starts at successful cast commitment. An interrupted committed cast keeps its cooldown; an unavailable target leaves the ability ready and allows ordinary behavior. Area centers and area recipients are captured at release. Targeted projectiles keep their target ID but never retarget a defeated unit. Dash landing is reserved at commitment and validated before movement. See the rules contract for same-tick ordering, shield replacement and refresh semantics.

Health and basic damage use 1.00/1.80/3.24 star multipliers. Only explicitly authored skill magnitudes vary with stars; stun duration, range, radius, dash distance, cooldown and model footprint do not grow. A status-only skill may deliberately have identical behavior across stars; its owner still gains health and basic damage.

## Positioning and counterplay

**Preferred formation.** Central frontline where multiple enemies approach adjacent cells.

**Useful partners.** Rowan’s area burst benefits when enemies are briefly held nearby; Tessa activates Dwarf.

**Counterplay.** Spread ranged units can attack without entering the stun ring; magical burst attacks his lower resistance.

**Practical weakness.** Slow movement and low damage; the active controls enemies but does not hurt them.

**Difference from the nearest alternative.** Ada absorbs a burst; Borin interrupts the local tempo and relies on allies for damage.

**Character-specific acceptance test.** All three stars retain exactly 1000 ms stun; repeated casts refresh expiry rather than adding durations.

## Animation, effects and sound

Idle rocks only slightly with the heavy hammer resting low. Walk is a deliberate short stride. Basics deliver compact side impacts. The active raises one foot and stamps while the hammer settles, emphasizing the ring on the ground.

**Skill effect:** A single amber ground ring and a clear stun marker over affected enemies. The ring has no damage component and no lingering slow.

**Sound:** A low, short bell knock with a firm footfall. Do not layer a long reverberation for each affected target.

Author at 60 FPS, as in-place animations with no locomotion-driven root translation. Required clips: Idle, Move, Attack, Active, Hit, Defeat, Victory. The active release marker is frame 24 relative to animation start. Basic release marker is frame 15. These are presentation alignment points, not sources of authoritative damage. Idle begins as a 2-second loop; movement as a 1-second cycle; hit as 0.4 seconds; defeat as 1 second; victory as 1.5 seconds. Adjust clip lengths during animation review without altering gameplay timing.

A defeat uses a brief stagger, kneel or magical dissolve with no injury detail. Stars use UI pips, a subtle trim accent and a brief upgrade flourish; do not produce three separate bodies or enlarge the collision footprint.

## Blender construction and Unreal handoff

Start from the `humanoid_stocky` base or a validated compatible family. Block silhouette before bevels; separate body, costume and equipment into named source collections. Build equipment as decorative fantasy game props, not real functional objects. Author model-space Z up and a consistent forward orientation, then prove conversion with the calibration fixture. Materials use one or two runtime slots and a shared atlas where it preserves identity.

Targets to profile: at most 15,000 LOD0 triangles, 1024-pixel default maps, up to 60 deforming bones and 4 influences per vertex. Lower-detail targets begin near 50% and 25% triangles. These are budgets, not measured performance.

Sockets: `weapon_r`, `weapon_l`, `cast_origin`, `head_ui`. Inspect shoulder, elbow, hip and knee extremes. Use separate rig proportions where needed; matching bone names is not proof of animation compatibility. Selection uses a stable unit proxy, not detailed prop collision. Team affiliation uses base rings/icons in addition to color, never a complete costume recolor.

**Specific production risk:** Large shoulders and beard can hide the head at the gameplay angle; shorten the rear plate depth and test three Borins standing adjacent.

Required source/export locations:

- blender: `art-source/heroes/wc_u_dwarf_guardian/wc_u_dwarf_guardian.blend`

- mesh_fbx: `exports/heroes/wc_u_dwarf_guardian/SK_wc_u_dwarf_guardian.fbx`

- unreal_folder: `/Game/WonderChess/Heroes/wc_u_dwarf_guardian`

- portrait: `exports/heroes/wc_u_dwarf_guardian/portrait.png`

Create separate animation exports and texture maps, a model-derived portrait, front/side/back/three-quarter views, a gameplay-camera screenshot, and an actual Unreal animation capture. Log source/export hashes, skeleton revision, tool versions and import preset. Deliberately change one costume detail, re-export and verify existing material, skeleton, animation and actor references survive.

## Model-sheet generation brief

Original Wonder Chess high-fantasy character production sheet for Borin Stonebell, The Bridge Sentinel. Dwarf Guardian, adult character, height 1.38 m. Front, true side, back and three-quarter views at matching scale, neutral A-pose plus one action pose. A compact rectangular torso beneath a domed helmet, with wide rounded shoulder plates and an oversized bell-headed hammer. Short legs stay separated enough to read during motion. Ruddy tan skin, large brown brows and a thick brown beard divided into two broad braids. A hinged-looking open helmet never hides the eyes. Slate plate over a moss-green padded coat, heavy riveted boots and a wide belt with a single square buckle. Avoid dozens of small rivets; bake secondary details. A two-handed fantasy hammer shaped like a solid bell housing. Its broad rim helps the stomp animation read without an actual moving bell interior. Palette: Slate #697A88; moss #6B7750; muted bronze #A58354; warm beard brown #76533A. Flat neutral background, orthographic construction views, equipment inset, readable seams, non-graphic stylized fantasy. No copied franchise designs, text baked into textures, cinematic fog, invented extra limbs or altered gear between views. These are concept directions, not generated images.

## Approval gates

Silhouette passes at 96-pixel preview; costume agrees across all views; all seven clips reviewed; no required missing textures; no unexplained import scale compensation; effect matches declared reach and damage type; portrait agrees with the modeled hero; crowded-board test passes; source revision/reimport is demonstrated. A Python exit code alone does not approve the art.

Canonical source: `data/units.json`. Regenerate this dossier with `python tools/build_documents.py` after data edits. Do not hand-edit a stat table and leave the JSON unchanged.

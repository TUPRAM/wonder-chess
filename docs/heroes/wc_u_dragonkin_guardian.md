# Sora Dawnscale — The Beacon Sentinel

**Dragonkin · Guardian · Defender · EXPANSION**

Stable identity: `wc_u_dragonkin_guardian`. Cost: **3 gold**. Rarity label: **Rare**, separate from star level. Status: designed, not modeled or implemented by this kit. All combat values are provisional prototype inputs.

## Character and world

Sora tends a beacon above Cindercrest that once guided winter travelers home. When distant wards began to flicker, she helped Oren organize shared watches rather than blame neighboring kingdoms. She joins the trials to build trust in a coalition whose members may never have seen a Dragonkin before.

Home region: `cindercrest`. Affiliation: `skyward_conclave`. Neither supplies a hidden third synergy. Proper names are original proposed fiction, not trademark-clearance claims.

## Appearance and art direction

Authored standing height: **2.08 m**, excluding raised equipment. Rig family: `humanoid_draconic`. One logical tile at every star. All characters are adults, fully clothed and presented as non-graphic heroic fantasy.

### Silhouette and proportions

A tall broad chest, short swept-back horns and an upright oval shield. A compact crest rises behind the forehead without adding wings or a tail.

### Face, hair and expression

Pearl-gold scales, deep amber eyes and a short rounded muzzle. Keep the mouth closed at rest and use a calm expression, not a permanent display of teeth.

### Costume construction

White-and-blue ceremonial armor with broad articulated panels, a short tabard and armored boots built around plantigrade feet.

### Color palette

Pearl #E0D8C1; royal blue #486A9A; gold #C4A367; dark slate #4D5B67.

### Equipment and magical focus

An oval fantasy shield with a single beacon gem and a short ceremonial mace. The gem is cosmetic outside the shield cast.

### Three low-resolution identifiers

Swept horns, oval beacon shield and pale armored torso.

### Materials and surface detail

Matte scale normals at low frequency, brushed armor and one gem emissive mask. Do not model every scale.

### Back and side-view constraints

A short raised neck crest ends above the shoulders. No wings, tail or dangling cloth; clear shoulders make retargeting manageable.

## Combat statistics — without traits or temporary effects

| Property | One star | Two stars | Three stars |
|---|---:|---:|---:|
| Health | 1,180 | 2,124 | 3,823.2 |
| Basic attack damage | 48 | 86.4 | 155.52 |
| Attack delivery | melee | melee | melee |
| Basic damage type | physical | physical | physical |
| Nominal attacks/second | 0.65 | 0.65 | 0.65 |
| Effective attacks/second at 20 Hz | 0.6452 | 0.6452 | 0.6452 |
| Range in tiles | 1 | 1 | 1 |
| Physical armor | 30 | 30 | 30 |
| Magic resistance | 30 | 30 | 30 |
| Movement tiles/second | 0.95 | 0.95 | 0.95 |

Nominal basic-attack DPS at one star: **31.20**, before mitigation, movement, stuns, skills, targeting downtime or timing quantization. Basic windup: 250 ms; ordinary projectile travel: 0 ms. No hidden critical hits, evasion, lifesteal or mana.

## One active skill

### Beacon Guard

**Player tooltip:** Gains a strong shield for three seconds.

**Indonesian draft:** Memberikan perisai sementara kepada diri sendiri.

| Contract field | Value |
|---|---|
| Stable ability ID | `wc_a_dragonkin_guardian` |
| Effect / target selector | `shield` / `self` |
| One / two / three star magnitude | 240 / 432 / 778 |
| Damage type | Not damaging |
| First-cast delay / cooldown | 2.5 s / 9 s |
| Windup / recovery | 0.35 s / 0.3 s |
| Effect duration | 3 s |
| Skill reach / area radius | 0 / 0 tiles |
| Can include self | True |
| Max dash distance | 0 tiles |
| Projectile travel | 0 ms |
| Affected stat | Not applicable |

Cooldown starts at successful cast commitment. An interrupted committed cast keeps its cooldown; an unavailable target leaves the ability ready and allows ordinary behavior. Area centers and area recipients are captured at release. Targeted projectiles keep their target ID but never retarget a defeated unit. Dash landing is reserved at commitment and validated before movement. See the rules contract for same-tick ordering, shield replacement and refresh semantics.

Health and basic damage use 1.00/1.80/3.24 star multipliers. Only explicitly authored skill magnitudes vary with stars; stun duration, range, radius, dash distance, cooldown and model footprint do not grow. A status-only skill may deliberately have identical behavior across stars; its owner still gains health and basic damage.

## Positioning and counterplay

**Preferred formation.** Primary frontline against mixed damage, with allies using the space behind her.

**Useful partners.** Oren supports her and activates Dragonkin; Ada or Tala activates Guardian.

**Counterplay.** Focused sustained attacks can consume the shield; control denies her already modest damage.

**Practical weakness.** Expensive defensive unit with no area protection or crowd control.

**Difference from the nearest alternative.** Ada is a cheaper physical anchor; Sora pays for broader defenses and a larger shield.

**Character-specific acceptance test.** Dragonkin resistance is applied before damage and does not secretly grant damage immunity.

## Animation, effects and sound

Idle stands tall with the shield close. Walk uses slow deliberate steps. Basics strike compactly. The active angles the shield upward and lights the beacon disk before a protective shell forms.

**Skill effect:** A pale-gold shield outline with a small vertical glint, never a full-screen column of light.

**Sound:** Low resonant chime and a measured armor movement; no roaring requirement.

Author at 60 FPS, as in-place animations with no locomotion-driven root translation. Required clips: Idle, Move, Attack, Active, Hit, Defeat, Victory. The active release marker is frame 21 relative to animation start. Basic release marker is frame 15. These are presentation alignment points, not sources of authoritative damage. Idle begins as a 2-second loop; movement as a 1-second cycle; hit as 0.4 seconds; defeat as 1 second; victory as 1.5 seconds. Adjust clip lengths during animation review without altering gameplay timing.

A defeat uses a brief stagger, kneel or magical dissolve with no injury detail. Stars use UI pips, a subtle trim accent and a brief upgrade flourish; do not produce three separate bodies or enlarge the collision footprint.

## Blender construction and Unreal handoff

Start from the `humanoid_draconic` base or a validated compatible family. Block silhouette before bevels; separate body, costume and equipment into named source collections. Build equipment as decorative fantasy game props, not real functional objects. Author model-space Z up and a consistent forward orientation, then prove conversion with the calibration fixture. Materials use one or two runtime slots and a shared atlas where it preserves identity.

Targets to profile: at most 15,000 LOD0 triangles, 1024-pixel default maps, up to 60 deforming bones and 4 influences per vertex. Lower-detail targets begin near 50% and 25% triangles. These are budgets, not measured performance.

Sockets: `weapon_r`, `weapon_l`, `cast_origin`, `head_ui`. Inspect shoulder, elbow, hip and knee extremes. Use separate rig proportions where needed; matching bone names is not proof of animation compatibility. Selection uses a stable unit proxy, not detailed prop collision. Team affiliation uses base rings/icons in addition to color, never a complete costume recolor.

**Specific production risk:** Muzzle, neck crest and shoulder plates need a draconic rig review. Do not force a human head mesh under a scale texture.

Required source/export locations:

- blender: `art-source/heroes/wc_u_dragonkin_guardian/wc_u_dragonkin_guardian.blend`

- mesh_fbx: `exports/heroes/wc_u_dragonkin_guardian/SK_wc_u_dragonkin_guardian.fbx`

- unreal_folder: `/Game/WonderChess/Heroes/wc_u_dragonkin_guardian`

- portrait: `exports/heroes/wc_u_dragonkin_guardian/portrait.png`

Create separate animation exports and texture maps, a model-derived portrait, front/side/back/three-quarter views, a gameplay-camera screenshot, and an actual Unreal animation capture. Log source/export hashes, skeleton revision, tool versions and import preset. Deliberately change one costume detail, re-export and verify existing material, skeleton, animation and actor references survive.

## Model-sheet generation brief

Original Wonder Chess high-fantasy character production sheet for Sora Dawnscale, The Beacon Sentinel. Dragonkin Guardian, adult character, height 2.08 m. Front, true side, back and three-quarter views at matching scale, neutral A-pose plus one action pose. A tall broad chest, short swept-back horns and an upright oval shield. A compact crest rises behind the forehead without adding wings or a tail. Pearl-gold scales, deep amber eyes and a short rounded muzzle. Keep the mouth closed at rest and use a calm expression, not a permanent display of teeth. White-and-blue ceremonial armor with broad articulated panels, a short tabard and armored boots built around plantigrade feet. An oval fantasy shield with a single beacon gem and a short ceremonial mace. The gem is cosmetic outside the shield cast. Palette: Pearl #E0D8C1; royal blue #486A9A; gold #C4A367; dark slate #4D5B67. Flat neutral background, orthographic construction views, equipment inset, readable seams, non-graphic stylized fantasy. No copied franchise designs, text baked into textures, cinematic fog, invented extra limbs or altered gear between views. These are concept directions, not generated images.

## Approval gates

Silhouette passes at 96-pixel preview; costume agrees across all views; all seven clips reviewed; no required missing textures; no unexplained import scale compensation; effect matches declared reach and damage type; portrait agrees with the modeled hero; crowded-board test passes; source revision/reimport is demonstrated. A Python exit code alone does not approve the art.

Canonical source: `data/units.json`. Regenerate this dossier with `python tools/build_documents.py` after data edits. Do not hand-edit a stat table and leave the JSON unchanged.

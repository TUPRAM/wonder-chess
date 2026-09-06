# Rok Sunward — The Pass Champion

**Orc · Warrior · Melee damage · ALPHA**

Stable identity: `wc_u_orc_warrior`. Cost: **1 gold**. Rarity label: **Common**, separate from star level. Production and verification status is recorded separately in reports/implementation_state.json; this generated dossier does not certify an asset or build. All combat values are provisional prototype inputs.

Quick display name: **Rok**. Informational roles: Melee. Role tags provide no additional synergy.

## Character and world

Rok escorts trade caravans through Stormstep’s high passes and treats a successful arrival as the only meaningful victory. He sees the trials as practice for cooperation, not proof that one people is strongest. Dagna’s exacting workshop habits amuse him, while Zura’s weather lessons taught him when patience matters more than force.

Home region: `stormstep`. Affiliation: `highland_watch`. Neither supplies a hidden third synergy. Proper names are original proposed fiction, not trademark-clearance claims.

## Appearance and art direction

Authored standing height: **2.04 m**, excluding raised equipment. Rig family: `humanoid_broad`. One logical tile at every star. All characters are adults, fully clothed and presented as non-graphic heroic fantasy.

### Silhouette and proportions

A tall broad-shouldered figure with a short circular shoulder mantle, compact fantasy axe and a visibly open stance. The weapon and torso create a diagonal, not Dagna’s horizontal bar.

### Face, hair and expression

Olive-green skin, small rounded tusks, warm amber eyes and black hair tied in a short topknot. Keep the expression determined but friendly, avoiding a permanent snarl.

### Costume construction

Sun-ochre woven mantle over brown padded armor, a red waist sash and practical high boots. The armor uses clean geometric plates with broad woven bands.

### Color palette

Ochre #CAA454; red earth #A95E4D; dark leather #5E5040; muted green skin #6E8260.

### Equipment and magical focus

A single broad stylized axe carried one-handed, with an open off-hand for balance. Its proportions communicate fantasy rather than realistic manufacturing.

### Three low-resolution identifiers

Round ochre mantle, topknot, and broad diagonal axe silhouette.

### Materials and surface detail

Thick cloth, oiled hide, brushed iron and a restrained sun-pattern stitch. No spikes or trophy clutter.

### Back and side-view constraints

A wide sash knot sits on one hip; the mantle is stiff enough for a short bone chain instead of simulation.

## Combat statistics — without traits or temporary effects

| Property | One star | Two stars | Three stars |
|---|---:|---:|---:|
| Health | 950 | 1,710 | 3,078 |
| Basic attack damage | 64 | 115.2 | 207.36 |
| Attack delivery | melee | melee | melee |
| Basic damage type | physical | physical | physical |
| Nominal attacks/second | 0.85 | 0.85 | 0.85 |
| Effective attacks/second at 20 Hz | 0.8333 | 0.8333 | 0.8333 |
| Range in tiles | 1 | 1 | 1 |
| Physical armor | 20 | 20 | 20 |
| Magic resistance | 15 | 15 | 15 |
| Movement tiles/second | 1.10 | 1.10 | 1.10 |

Nominal basic-attack DPS at one star: **54.40**, before mitigation, movement, stuns, skills, targeting downtime or timing quantization. Basic windup: 350 ms; ordinary projectile travel: 0 ms. No hidden critical hits, evasion, lifesteal or mana.

## One active skill

### Battle Rhythm

**Player tooltip:** Temporarily increases his attack speed.

**Indonesian draft:** Meningkatkan kecepatan serang diri sendiri untuk sementara.

| Contract field | Value |
|---|---|
| Stable ability ID | `wc_a_orc_warrior` |
| Effect / target selector | `stat_modifier` / `self` |
| One / two / three star magnitude | stat_modifier: 30% / 35% / 40% |
| Damage type | Not damaging |
| First-cast delay / cooldown | 2.5 s / 8.5 s |
| Windup / recovery | 0.25 s / 0.3 s |
| Effect duration | 3.0 s |
| Skill reach / area radius | 0 / 0 tiles |
| Can include self | True |
| Max dash distance | 0 tiles |
| Projectile travel | 0 ms |
| Affected stat | attack_rate |

Cooldown starts at successful cast commitment. An interrupted committed cast keeps its cooldown; an unavailable target leaves the ability ready and allows ordinary behavior. Area centers and area recipients are captured at release. Targeted projectiles keep their target ID but never retarget a defeated unit. Dash landing is reserved at commitment and validated before movement. See the rules contract for same-tick ordering, shield replacement and refresh semantics.

Health and basic damage use 1.00/1.80/3.24 star multipliers. Only explicitly authored skill magnitudes vary with stars; stun duration, range, radius, dash distance, cooldown and model footprint do not grow. A status-only skill may deliberately have identical behavior across stars; its owner still gains health and basic damage.

## Positioning and counterplay

**Preferred formation.** Frontline flank next to a Guardian, so he can keep attacking one target rather than absorb all focus.

**Useful partners.** Dagna activates Warrior; Zura or Kesh activates Orc to improve direct damage.

**Counterplay.** Stuns interrupt his attacking window, and shields can absorb much of the tempo burst.

**Practical weakness.** All sustained offense is basic attacks; no mobility, area attack or protection.

**Difference from the nearest alternative.** Dagna has an area skill; Rok turns one ordinary attack pattern into a temporary sustained threat.

**Character-specific acceptance test.** Tempo adjusts the next attack interval, never rewinds an already committed attack or accelerates the cooldown.

## Animation, effects and sound

Idle squares shoulders and rolls weight between feet. Basics use alternating short attacks. The active takes a clear breath and sets a quicker rhythm with a firm foot plant, not a transformation.

**Skill effect:** Three short amber speed marks rise from the arms and fade; the buff remains visible as a small icon, not a continuous flame layer.

**Sound:** Rhythmic hand-drum accent and a restrained exhale, with ordinary attack impacts at the new cadence.

Author at 60 FPS, as in-place animations with no locomotion-driven root translation. Required clips: Idle, Move, Attack, Active, Hit, Defeat, Victory. The active release marker is frame 15 relative to animation start. Basic release marker is frame 21. These are presentation alignment points, not sources of authoritative damage. Idle begins as a 2-second loop; movement as a 1-second cycle; hit as 0.4 seconds; defeat as 1 second; victory as 1.5 seconds. Adjust clip lengths during animation review without altering gameplay timing.

A defeat uses a brief stagger, kneel or magical dissolve with no injury detail. Stars use UI pips, a subtle trim accent and a brief upgrade flourish; do not produce three separate bodies or enlarge the collision footprint.

## Blender construction and Unreal handoff

Start from the `humanoid_broad` base or a validated compatible family. Block silhouette before bevels; separate body, costume and equipment into named source collections. Build equipment as decorative fantasy game props, not real functional objects. Author model-space Z up and a consistent forward orientation, then prove conversion with the calibration fixture. Materials use one or two runtime slots and a shared atlas where it preserves identity.

Targets to profile: at most 15,000 LOD0 triangles, 1024-pixel default maps, up to 60 deforming bones and 4 influences per vertex. Lower-detail targets begin near 50% and 25% triangles. These are budgets, not measured performance.

Sockets: `weapon_r`, `weapon_l`, `cast_origin`, `head_ui`. Inspect shoulder, elbow, hip and knee extremes. Use separate rig proportions where needed; matching bone names is not proof of animation compatibility. Selection uses a stable unit proxy, not detailed prop collision. Team affiliation uses base rings/icons in addition to color, never a complete costume recolor.

**Specific production risk:** Large proportions need a broad rig variant rather than scaling a human mesh uniformly. Keep hands and axe away from face during tempo changes.

Required source/export locations:

- blender: `art-source/heroes/wc_u_orc_warrior/wc_u_orc_warrior.blend`

- mesh_fbx: `exports/heroes/wc_u_orc_warrior/SK_wc_u_orc_warrior.fbx`

- unreal_folder: `/Game/WonderChess/Heroes/wc_u_orc_warrior`

- portrait: `exports/heroes/wc_u_orc_warrior/portrait.png`

Create separate animation exports and texture maps, a model-derived portrait, front/side/back/three-quarter views, a gameplay-camera screenshot, and an actual Unreal animation capture. Log source/export hashes, skeleton revision, tool versions and import preset. Deliberately change one costume detail, re-export and verify existing material, skeleton, animation and actor references survive.

## Model-sheet generation brief

Original Wonder Chess high-fantasy character production sheet for Rok Sunward, The Pass Champion. Orc Warrior, adult character, height 2.04 m. Front, true side, back and three-quarter views at matching scale, neutral A-pose plus one action pose. A tall broad-shouldered figure with a short circular shoulder mantle, compact fantasy axe and a visibly open stance. The weapon and torso create a diagonal, not Dagna’s horizontal bar. Olive-green skin, small rounded tusks, warm amber eyes and black hair tied in a short topknot. Keep the expression determined but friendly, avoiding a permanent snarl. Sun-ochre woven mantle over brown padded armor, a red waist sash and practical high boots. The armor uses clean geometric plates with broad woven bands. A single broad stylized axe carried one-handed, with an open off-hand for balance. Its proportions communicate fantasy rather than realistic manufacturing. Palette: Ochre #CAA454; red earth #A95E4D; dark leather #5E5040; muted green skin #6E8260. Flat neutral background, orthographic construction views, equipment inset, readable seams, non-graphic stylized fantasy. No copied franchise designs, text baked into textures, cinematic fog, invented extra limbs or altered gear between views. These are concept directions, not generated images.

## Approval gates

Silhouette passes at 96-pixel preview; costume agrees across all views; all seven clips reviewed; no required missing textures; no unexplained import scale compensation; effect matches declared reach and damage type; portrait agrees with the modeled hero; crowded-board test passes; source revision/reimport is demonstrated. A Python exit code alone does not approve the art.

Canonical source: `data/units.json`. Regenerate this dossier with `python tools/build_documents.py` after data edits. Do not hand-edit a stat table and leave the JSON unchanged.

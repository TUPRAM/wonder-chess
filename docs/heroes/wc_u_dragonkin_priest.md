# Oren Skyward — The Beacon Keeper

**Dragonkin · Priest · Support · ALPHA**

Stable identity: `wc_u_dragonkin_priest`. Cost: **2 gold**. Rarity label: **Uncommon**, separate from star level. Production and verification status is recorded separately in reports/implementation_state.json; this generated dossier does not certify an asset or build. All combat values are provisional prototype inputs.

Quick display name: **Oren**. Informational roles: Support. Role tags provide no additional synergy.

## Character and world

Oren charts the safe paths between Cindercrest’s beacons and corresponds with Neris about the distant sky. He believes cooperation begins when people can find one another, so his maps include taverns and gardens as carefully as watchtowers. He joins the trials to practice protecting an ally before the next blow rather than only repairing the damage afterward.

Home region: `cindercrest`. Affiliation: `skyward_conclave`. Neither supplies a hidden third synergy. Proper names are original proposed fiction, not trademark-clearance claims.

## Appearance and art direction

Authored standing height: **2.02 m**, excluding raised equipment. Rig family: `humanoid_draconic`. One logical tile at every star. All characters are adults, fully clothed and presented as non-graphic heroic fantasy.

### Silhouette and proportions

A tall narrow silhouette framed by a short mantle and a large open lantern staff. Two rounded swept horns form an unobtrusive arch above the head.

### Face, hair and expression

Pale moss-gray scales, warm gold eyes and a short rounded muzzle. The face should appear attentive and scholarly rather than ferocious.

### Costume construction

White traveling robes with deep teal panels, short gold-edged mantle and fitted lower-leg wraps. Split robe panels stop above the ankles.

### Color palette

White linen #E5E2D3; teal #3E7F83; moss gray #92A69D; pale gold #C4AC72.

### Equipment and magical focus

A long staff with an open hexagonal lantern frame and a small sealed map case. No books float as independent actors.

### Three low-resolution identifiers

Hexagonal lantern head, rounded swept horns and teal vertical robe panels.

### Materials and surface detail

Matte cloth, subtle scale normal, brushed gold and frosted opaque lantern panels. Keep glowing area small.

### Back and side-view constraints

A single wide teal panel and short mantle define the rear. Horns clear the staff during over-shoulder poses.

## Combat statistics — without traits or temporary effects

| Property | One star | Two stars | Three stars |
|---|---:|---:|---:|
| Health | 800 | 1,440 | 2,592 |
| Basic attack damage | 38 | 68.4 | 123.12 |
| Attack delivery | ranged | ranged | ranged |
| Basic damage type | magic | magic | magic |
| Nominal attacks/second | 0.75 | 0.75 | 0.75 |
| Effective attacks/second at 20 Hz | 0.7407 | 0.7407 | 0.7407 |
| Range in tiles | 3 | 3 | 3 |
| Physical armor | 15 | 15 | 15 |
| Magic resistance | 30 | 30 | 30 |
| Movement tiles/second | 1.00 | 1.00 | 1.00 |

Nominal basic-attack DPS at one star: **28.50**, before mitigation, movement, stuns, skills, targeting downtime or timing quantization. Basic windup: 300 ms; ordinary projectile travel: 150 ms. No hidden critical hits, evasion, lifesteal or mana.

## One active skill

### Sky Ward

**Player tooltip:** Shield the lowest-health eligible ally in range, including self. Skip an ally whose existing shield would reject the ward; remain ready when no ally can benefit.

**Indonesian draft:** Lindungi sekutu yang memenuhi syarat dengan persentase kesehatan terendah dalam jangkauan, termasuk diri sendiri. Lewati perisai yang akan menolak perlindungan ini; tetap siap jika tidak ada penerima yang mendapat manfaat.

| Contract field | Value |
|---|---|
| Stable ability ID | `wc_a_dragonkin_priest` |
| Effect / target selector | `shield` / `lowest_health_ally` |
| One / two / three star magnitude | shield: 190 / 342 / 616 |
| Damage type | Not damaging |
| First-cast delay / cooldown | 2.5 s / 8 s |
| Windup / recovery | 0.35 s / 0.3 s |
| Effect duration | 3.0 s |
| Skill reach / area radius | 8 / 0 tiles |
| Can include self | True |
| Max dash distance | 0 tiles |
| Projectile travel | 0 ms |
| Affected stat | Not applicable |

Cooldown starts at successful cast commitment. An interrupted committed cast keeps its cooldown; an unavailable target leaves the ability ready and allows ordinary behavior. Area centers and area recipients are captured at release. Targeted projectiles keep their target ID but never retarget a defeated unit. Dash landing is reserved at commitment and validated before movement. See the rules contract for same-tick ordering, shield replacement and refresh semantics.

Health and basic damage use 1.00/1.80/3.24 star multipliers. Only explicitly authored skill magnitudes vary with stars; stun duration, range, radius, dash distance, cooldown and model footprint do not grow. A status-only skill may deliberately have identical behavior across stars; its owner still gains health and basic damage.

## Positioning and counterplay

**Preferred formation.** Protected middle-back row within global support reach, with a durable frontline target.

**Useful partners.** Sora activates Dragonkin; Mira or Orla activates Priest support potency.

**Counterplay.** Sustained multi-target pressure can defeat allies that his single-target ward does not reach.

**Practical weakness.** No healing; shielding an already injured ally does not restore missing health.

**Difference from the nearest alternative.** Mira repairs health directly, while Oren grants temporary absorption to a vulnerable ally.

**Character-specific acceptance test.** Lowest-health selection includes self; stronger existing shields are not replaced by weaker wards, and shields expire at the exact tick.

## Animation, effects and sound

Idle rests the staff near the body. Basics release a small light mote. The active turns the lantern toward the selected ally and lifts the free palm, producing a visibly directed ward.

**Skill effect:** A pale-gold line leads briefly to the recipient, then a hexagonal shield outline appears. It is protection, not healing or revival.

**Sound:** A restrained bell with a short sustaining tail cut on expiry; avoid one continuous sound per shielded target.

Author at 60 FPS, as in-place animations with no locomotion-driven root translation. Required clips: Idle, Move, Attack, Active, Hit, Defeat, Victory. The active release marker is frame 21 relative to animation start. Basic release marker is frame 18. These are presentation alignment points, not sources of authoritative damage. Idle begins as a 2-second loop; movement as a 1-second cycle; hit as 0.4 seconds; defeat as 1 second; victory as 1.5 seconds. Adjust clip lengths during animation review without altering gameplay timing.

A defeat uses a brief stagger, kneel or magical dissolve with no injury detail. Stars use UI pips, a subtle trim accent and a brief upgrade flourish; do not produce three separate bodies or enlarge the collision footprint.

## Blender construction and Unreal handoff

Start from the `humanoid_draconic` base or a validated compatible family. Block silhouette before bevels; separate body, costume and equipment into named source collections. Build equipment as decorative fantasy game props, not real functional objects. Author model-space Z up and a consistent forward orientation, then prove conversion with the calibration fixture. Materials use one or two runtime slots and a shared atlas where it preserves identity.

Targets to profile: at most 15,000 LOD0 triangles, 1024-pixel default maps, up to 60 deforming bones and 4 influences per vertex. Lower-detail targets begin near 50% and 25% triangles. These are budgets, not measured performance.

Sockets: `weapon_r`, `weapon_l`, `cast_origin`, `head_ui`. Inspect shoulder, elbow, hip and knee extremes. Use separate rig proportions where needed; matching bone names is not proof of animation compatibility. Selection uses a stable unit proxy, not detailed prop collision. Team affiliation uses base rings/icons in addition to color, never a complete costume recolor.

**Specific production risk:** The selected ally may already carry a stronger shield. Candidate validation and replacement rules must prevent wasted weak overwrites.

Required source/export locations:

- blender: `art-source/heroes/wc_u_dragonkin_priest/wc_u_dragonkin_priest.blend`

- mesh_fbx: `exports/heroes/wc_u_dragonkin_priest/SK_wc_u_dragonkin_priest.fbx`

- unreal_folder: `/Game/WonderChess/Heroes/wc_u_dragonkin_priest`

- portrait: `exports/heroes/wc_u_dragonkin_priest/portrait.png`

Create separate animation exports and texture maps, a model-derived portrait, front/side/back/three-quarter views, a gameplay-camera screenshot, and an actual Unreal animation capture. Log source/export hashes, skeleton revision, tool versions and import preset. Deliberately change one costume detail, re-export and verify existing material, skeleton, animation and actor references survive.

## Model-sheet generation brief

Original Wonder Chess high-fantasy character production sheet for Oren Skyward, The Beacon Keeper. Dragonkin Priest, adult character, height 2.02 m. Front, true side, back and three-quarter views at matching scale, neutral A-pose plus one action pose. A tall narrow silhouette framed by a short mantle and a large open lantern staff. Two rounded swept horns form an unobtrusive arch above the head. Pale moss-gray scales, warm gold eyes and a short rounded muzzle. The face should appear attentive and scholarly rather than ferocious. White traveling robes with deep teal panels, short gold-edged mantle and fitted lower-leg wraps. Split robe panels stop above the ankles. A long staff with an open hexagonal lantern frame and a small sealed map case. No books float as independent actors. Palette: White linen #E5E2D3; teal #3E7F83; moss gray #92A69D; pale gold #C4AC72. Flat neutral background, orthographic construction views, equipment inset, readable seams, non-graphic stylized fantasy. No copied franchise designs, text baked into textures, cinematic fog, invented extra limbs or altered gear between views. These are concept directions, not generated images.

## Approval gates

Silhouette passes at 96-pixel preview; costume agrees across all views; all seven clips reviewed; no required missing textures; no unexplained import scale compensation; effect matches declared reach and damage type; portrait agrees with the modeled hero; crowded-board test passes; source revision/reimport is demonstrated. A Python exit code alone does not approve the art.

Canonical source: `data/units.json`. Regenerate this dossier with `python tools/build_documents.py` after data edits. Do not hand-edit a stat table and leave the JSON unchanged.

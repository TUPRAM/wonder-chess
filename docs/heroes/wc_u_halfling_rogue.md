# Nella Quickpocket — The Festival Scout

**Halfling · Rogue · Disruption · ALPHA**

Stable identity: `wc_u_halfling_rogue`. Cost: **2 gold**. Rarity label: **Uncommon**, separate from star level. Production and verification status is recorded separately in reports/implementation_state.json; this generated dossier does not certify an asset or build. All combat values are provisional prototype inputs.

Quick display name: **Nella**. Informational roles: Control. Role tags provide no additional synergy.

## Character and world

Nella scouts safe routes for Willowrun’s traveling festivals and knows where crowds tend to form. Her nickname comes from always finding a spare ribbon or missing ticket in a coat pocket. She joins the trials to practice the kind of interruption that gives an ally a moment to recover, often teasing Sylas about his much more dramatic entrances.

Home region: `willowrun`. Affiliation: `wayfarer_fellowship`. Neither supplies a hidden third synergy. Proper names are original proposed fiction, not trademark-clearance claims.

## Appearance and art direction

Authored standing height: **1.1 m**, excluding raised equipment. Rig family: `humanoid_small`. One logical tile at every star. All characters are adults, fully clothed and presented as non-graphic heroic fantasy.

### Silhouette and proportions

A compact side-on stance with a short diamond-shaped cape and a high swept hair tuft. Two flat fanlike fantasy batons form a clear paired shape.

### Face, hair and expression

Rich brown skin, green-brown eyes and dark curls clipped at the sides. Her expression is mischievous without a villainous mask.

### Costume construction

Plum festival jacket, pale shirt, teal waist cord and sturdy close-fitting trousers. Small stitched stars appear only on one large lapel.

### Color palette

Plum #785B83; teal #548B89; parchment #E1D4BB; dark cocoa #594838.

### Equipment and magical focus

Paired short fanlike fantasy batons and a flat messenger pouch. Do not include lockpicking gear or realistic criminal instruction props.

### Three low-resolution identifiers

Diamond cape, swept hair tuft and paired broad baton ends.

### Materials and surface detail

Smooth dyed cloth, matte leather and painted wood with a few metallic accents.

### Back and side-view constraints

A single diagonal teal cord crosses the short cape. Pouch placement must not collide with quick turns.

## Combat statistics — without traits or temporary effects

| Property | One star | Two stars | Three stars |
|---|---:|---:|---:|
| Health | 660 | 1,188 | 2,138.4 |
| Basic attack damage | 58 | 104.4 | 187.92 |
| Attack delivery | melee | melee | melee |
| Basic damage type | physical | physical | physical |
| Nominal attacks/second | 1.10 | 1.10 | 1.10 |
| Effective attacks/second at 20 Hz | 1.0526 | 1.0526 | 1.0526 |
| Range in tiles | 1 | 1 | 1 |
| Physical armor | 12 | 12 | 12 |
| Magic resistance | 12 | 12 | 12 |
| Movement tiles/second | 1.30 | 1.30 | 1.30 |

Nominal basic-attack DPS at one star: **63.80**, before mitigation, movement, stuns, skills, targeting downtime or timing quantization. Basic windup: 250 ms; ordinary projectile travel: 0 ms. No hidden critical hits, evasion, lifesteal or mana.

## One active skill

### Quick Feint

**Player tooltip:** Stuns the current target for one second.

**Indonesian draft:** Melumpuhkan sementara sasaran saat ini.

| Contract field | Value |
|---|---|
| Stable ability ID | `wc_a_halfling_rogue` |
| Effect / target selector | `stun` / `current_enemy` |
| One / two / three star magnitude | stun: Not applicable / Not applicable / Not applicable |
| Damage type | Not damaging |
| First-cast delay / cooldown | 2 s / 7.5 s |
| Windup / recovery | 0.2 s / 0.3 s |
| Effect duration | 1.0 s |
| Skill reach / area radius | 1 / 0 tiles |
| Can include self | False |
| Max dash distance | 0 tiles |
| Projectile travel | 0 ms |
| Affected stat | Not applicable |

Cooldown starts at successful cast commitment. An interrupted committed cast keeps its cooldown; an unavailable target leaves the ability ready and allows ordinary behavior. Area centers and area recipients are captured at release. Targeted projectiles keep their target ID but never retarget a defeated unit. Dash landing is reserved at commitment and validated before movement. See the rules contract for same-tick ordering, shield replacement and refresh semantics.

Health and basic damage use 1.00/1.80/3.24 star multipliers. Only explicitly authored skill magnitudes vary with stars; stun duration, range, radius, dash distance, cooldown and model footprint do not grow. A status-only skill may deliberately have identical behavior across stars; its owner still gains health and basic damage.

## Positioning and counterplay

**Preferred formation.** Frontline edge near a valuable current target, not alone against an entire team.

**Useful partners.** Sylas or Kesh supplies Rogue; Pippa can help occupy the same flank.

**Counterplay.** Long-range focus can defeat her before she reaches stun range.

**Practical weakness.** No dash, shield or active damage; relies on ordinary movement and attacks.

**Difference from the nearest alternative.** Sylas reaches the backline; Nella stays local and interrupts one target.

**Character-specific acceptance test.** Quick Feint cancels an unreleased attack windup but never recalls a projectile already in flight.

## Animation, effects and sound

Idle rests in a sideways stance. Basics use short alternating taps. The active feints with the off-hand and makes one clear forward gesture; no disappearing body or forced camera cut.

**Skill effect:** A compact gold star above the target and a faint impact ring, then the shared stun marker. No damage packet.

**Sound:** A quick double tap and a short bright bell accent.

Author at 60 FPS, as in-place animations with no locomotion-driven root translation. Required clips: Idle, Move, Attack, Active, Hit, Defeat, Victory. The active release marker is frame 12 relative to animation start. Basic release marker is frame 15. These are presentation alignment points, not sources of authoritative damage. Idle begins as a 2-second loop; movement as a 1-second cycle; hit as 0.4 seconds; defeat as 1 second; victory as 1.5 seconds. Adjust clip lengths during animation review without altering gameplay timing.

A defeat uses a brief stagger, kneel or magical dissolve with no injury detail. Stars use UI pips, a subtle trim accent and a brief upgrade flourish; do not produce three separate bodies or enlarge the collision footprint.

## Blender construction and Unreal handoff

Start from the `humanoid_small` base or a validated compatible family. Block silhouette before bevels; separate body, costume and equipment into named source collections. Build equipment as decorative fantasy game props, not real functional objects. Author model-space Z up and a consistent forward orientation, then prove conversion with the calibration fixture. Materials use one or two runtime slots and a shared atlas where it preserves identity.

Targets to profile: at most 15,000 LOD0 triangles, 1024-pixel default maps, up to 60 deforming bones and 4 influences per vertex. Lower-detail targets begin near 50% and 25% triangles. These are budgets, not measured performance.

Sockets: `weapon_r`, `weapon_l`, `cast_origin`, `head_ui`. Inspect shoulder, elbow, hip and knee extremes. Use separate rig proportions where needed; matching bone names is not proof of animation compatibility. Selection uses a stable unit proxy, not detailed prop collision. Team affiliation uses base rings/icons in addition to color, never a complete costume recolor.

**Specific production risk:** Fast motion can become unreadable on a small model. Preserve a brief anticipation pose and avoid motion blur as a substitute.

Required source/export locations:

- blender: `art-source/heroes/wc_u_halfling_rogue/wc_u_halfling_rogue.blend`

- mesh_fbx: `exports/heroes/wc_u_halfling_rogue/SK_wc_u_halfling_rogue.fbx`

- unreal_folder: `/Game/WonderChess/Heroes/wc_u_halfling_rogue`

- portrait: `exports/heroes/wc_u_halfling_rogue/portrait.png`

Create separate animation exports and texture maps, a model-derived portrait, front/side/back/three-quarter views, a gameplay-camera screenshot, and an actual Unreal animation capture. Log source/export hashes, skeleton revision, tool versions and import preset. Deliberately change one costume detail, re-export and verify existing material, skeleton, animation and actor references survive.

## Model-sheet generation brief

Original Wonder Chess high-fantasy character production sheet for Nella Quickpocket, The Festival Scout. Halfling Rogue, adult character, height 1.1 m. Front, true side, back and three-quarter views at matching scale, neutral A-pose plus one action pose. A compact side-on stance with a short diamond-shaped cape and a high swept hair tuft. Two flat fanlike fantasy batons form a clear paired shape. Rich brown skin, green-brown eyes and dark curls clipped at the sides. Her expression is mischievous without a villainous mask. Plum festival jacket, pale shirt, teal waist cord and sturdy close-fitting trousers. Small stitched stars appear only on one large lapel. Paired short fanlike fantasy batons and a flat messenger pouch. Do not include lockpicking gear or realistic criminal instruction props. Palette: Plum #785B83; teal #548B89; parchment #E1D4BB; dark cocoa #594838. Flat neutral background, orthographic construction views, equipment inset, readable seams, non-graphic stylized fantasy. No copied franchise designs, text baked into textures, cinematic fog, invented extra limbs or altered gear between views. These are concept directions, not generated images.

## Approval gates

Silhouette passes at 96-pixel preview; costume agrees across all views; all seven clips reviewed; no required missing textures; no unexplained import scale compensation; effect matches declared reach and damage type; portrait agrees with the modeled hero; crowded-board test passes; source revision/reimport is demonstrated. A Python exit code alone does not approve the art.

Canonical source: `data/units.json`. Regenerate this dossier with `python tools/build_documents.py` after data edits. Do not hand-edit a stat table and leave the JSON unchanged.

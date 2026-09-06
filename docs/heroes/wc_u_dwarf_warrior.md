# Dagna Anvilheart — The Hall Champion

**Dwarf · Warrior · Melee damage · ALPHA**

Stable identity: `wc_u_dwarf_warrior`. Cost: **2 gold**. Rarity label: **Uncommon**, separate from star level. Status: designed, not modeled or implemented by this kit. All combat values are provisional prototype inputs.

## Character and world

Dagna organizes Stoneveil’s annual craft contests, where finishing a useful bridge bracket matters more than winning an argument. She enters the Compact trials because she refuses to send apprentices into danger without learning how the teams will work. Her friendship with Rok began when they rebuilt a damaged caravan platform together, each claiming the other’s measurements were too cautious.

Home region: `stoneveil`. Affiliation: `hearthwright_union`. Neither supplies a hidden third synergy. Proper names are original proposed fiction, not trademark-clearance claims.

## Appearance and art direction

Authored standing height: **1.42 m**, excluding raised equipment. Rig family: `humanoid_stocky`. One logical tile at every star. All characters are adults, fully clothed and presented as non-graphic heroic fantasy.

### Silhouette and proportions

A broad low center of gravity, square apron panels and a single large two-handed hammer held across the body. One uncovered upper sleeve breaks the armored outline without exposing a vulnerable-looking costume.

### Face, hair and expression

Deep brown skin, bright gray eyes and black hair in a thick high braid coiled at the back. A stern resting expression softens during the victory pose.

### Costume construction

Red workshop coat beneath segmented shoulder armor, a short split leather apron and heavy wrapped boots. Metal is limited to the shoulders, wrists and tool head.

### Color palette

Brick red #A64E45; soot #4A4343; honey leather #A67E4B; steel #AAB2B7.

### Equipment and magical focus

A blocky fantasy forge hammer with a large beveled face and short decorative rune strip. The tool reads from shape rather than detailed mechanical parts.

### Three low-resolution identifiers

Wide hammer bar, red split coat and squared apron silhouette.

### Materials and surface detail

Coarse leather, wool, lightly worn iron and painted wood. Use broad edge accents to suggest craft rather than gritty damage.

### Back and side-view constraints

A simple crossed harness stabilizes the hammer rest pose; the braid coil stays above the shoulder blades and outside the swing path.

## Combat statistics — without traits or temporary effects

| Property | One star | Two stars | Three stars |
|---|---:|---:|---:|
| Health | 1,000 | 1,800 | 3,240 |
| Basic attack damage | 70 | 126 | 226.8 |
| Attack delivery | melee | melee | melee |
| Basic damage type | physical | physical | physical |
| Nominal attacks/second | 0.80 | 0.80 | 0.80 |
| Effective attacks/second at 20 Hz | 0.8000 | 0.8000 | 0.8000 |
| Range in tiles | 1 | 1 | 1 |
| Physical armor | 25 | 25 | 25 |
| Magic resistance | 15 | 15 | 15 |
| Movement tiles/second | 1.00 | 1.00 | 1.00 |

Nominal basic-attack DPS at one star: **56.00**, before mitigation, movement, stuns, skills, targeting downtime or timing quantization. Basic windup: 350 ms; ordinary projectile travel: 0 ms. No hidden critical hits, evasion, lifesteal or mana.

## One active skill

### Anvil Sweep

**Player tooltip:** Damages all adjacent enemies.

**Indonesian draft:** Memberikan kerusakan fisik kepada musuh di area sasaran.

| Contract field | Value |
|---|---|
| Stable ability ID | `wc_a_dwarf_warrior` |
| Effect / target selector | `damage` / `adjacent_enemies` |
| One / two / three star magnitude | 140 / 252 / 454 |
| Damage type | physical |
| First-cast delay / cooldown | 3.5 s / 8 s |
| Windup / recovery | 0.4 s / 0.3 s |
| Effect duration | 0 s |
| Skill reach / area radius | 1 / 1 tiles |
| Can include self | False |
| Max dash distance | 0 tiles |
| Projectile travel | 0 ms |
| Affected stat | Not applicable |

Cooldown starts at successful cast commitment. An interrupted committed cast keeps its cooldown; an unavailable target leaves the ability ready and allows ordinary behavior. Area centers and area recipients are captured at release. Targeted projectiles keep their target ID but never retarget a defeated unit. Dash landing is reserved at commitment and validated before movement. See the rules contract for same-tick ordering, shield replacement and refresh semantics.

Health and basic damage use 1.00/1.80/3.24 star multipliers. Only explicitly authored skill magnitudes vary with stars; stun duration, range, radius, dash distance, cooldown and model footprint do not grow. A status-only skill may deliberately have identical behavior across stars; its owner still gains health and basic damage.

## Positioning and counterplay

**Preferred formation.** Frontline beside, rather than in front of, the primary tank; try to contact two opponents.

**Useful partners.** Rok completes Warrior; Borin’s stun gives her time to finish the sweep.

**Counterplay.** Ranged spread formations deny area value; magical focus can wear down her moderate resistance.

**Practical weakness.** Needs close contact and has no self-heal, shield or forced movement.

**Difference from the nearest alternative.** Rok accelerates repeated basics; Dagna delivers a periodic area hit.

**Character-specific acceptance test.** Each adjacent enemy receives one physical packet; no center self-hit and no duplicate diagonal hit.

## Animation, effects and sound

Idle holds the hammer diagonally with settled elbows. Walk uses strong grounded steps. Basics use a short overhead arc. The active pivots through one wide sweep, then returns to the same tile.

**Skill effect:** A low pale-gold sweep arc traces only the adjacent-cell ring; no knockback or extra stun.

**Sound:** A broad whoosh and compact stone-on-metal fantasy impact, limited to one main active sound even with several victims.

Author at 60 FPS, as in-place animations with no locomotion-driven root translation. Required clips: Idle, Move, Attack, Active, Hit, Defeat, Victory. The active release marker is frame 24 relative to animation start. Basic release marker is frame 21. These are presentation alignment points, not sources of authoritative damage. Idle begins as a 2-second loop; movement as a 1-second cycle; hit as 0.4 seconds; defeat as 1 second; victory as 1.5 seconds. Adjust clip lengths during animation review without altering gameplay timing.

A defeat uses a brief stagger, kneel or magical dissolve with no injury detail. Stars use UI pips, a subtle trim accent and a brief upgrade flourish; do not produce three separate bodies or enlarge the collision footprint.

## Blender construction and Unreal handoff

Start from the `humanoid_stocky` base or a validated compatible family. Block silhouette before bevels; separate body, costume and equipment into named source collections. Build equipment as decorative fantasy game props, not real functional objects. Author model-space Z up and a consistent forward orientation, then prove conversion with the calibration fixture. Materials use one or two runtime slots and a shared atlas where it preserves identity.

Targets to profile: at most 15,000 LOD0 triangles, 1024-pixel default maps, up to 60 deforming bones and 4 influences per vertex. Lower-detail targets begin near 50% and 25% triangles. These are budgets, not measured performance.

Sockets: `weapon_r`, `weapon_l`, `cast_origin`, `head_ui`. Inspect shoulder, elbow, hip and knee extremes. Use separate rig proportions where needed; matching bone names is not proof of animation compatibility. Selection uses a stable unit proxy, not detailed prop collision. Team affiliation uses base rings/icons in addition to color, never a complete costume recolor.

**Specific production risk:** The sweep must not imply a larger hit radius than the data. Avoid excessive root rotation that changes gameplay facing or shifts the feet.

Required source/export locations:

- blender: `art-source/heroes/wc_u_dwarf_warrior/wc_u_dwarf_warrior.blend`

- mesh_fbx: `exports/heroes/wc_u_dwarf_warrior/SK_wc_u_dwarf_warrior.fbx`

- unreal_folder: `/Game/WonderChess/Heroes/wc_u_dwarf_warrior`

- portrait: `exports/heroes/wc_u_dwarf_warrior/portrait.png`

Create separate animation exports and texture maps, a model-derived portrait, front/side/back/three-quarter views, a gameplay-camera screenshot, and an actual Unreal animation capture. Log source/export hashes, skeleton revision, tool versions and import preset. Deliberately change one costume detail, re-export and verify existing material, skeleton, animation and actor references survive.

## Model-sheet generation brief

Original Wonder Chess high-fantasy character production sheet for Dagna Anvilheart, The Hall Champion. Dwarf Warrior, adult character, height 1.42 m. Front, true side, back and three-quarter views at matching scale, neutral A-pose plus one action pose. A broad low center of gravity, square apron panels and a single large two-handed hammer held across the body. One uncovered upper sleeve breaks the armored outline without exposing a vulnerable-looking costume. Deep brown skin, bright gray eyes and black hair in a thick high braid coiled at the back. A stern resting expression softens during the victory pose. Red workshop coat beneath segmented shoulder armor, a short split leather apron and heavy wrapped boots. Metal is limited to the shoulders, wrists and tool head. A blocky fantasy forge hammer with a large beveled face and short decorative rune strip. The tool reads from shape rather than detailed mechanical parts. Palette: Brick red #A64E45; soot #4A4343; honey leather #A67E4B; steel #AAB2B7. Flat neutral background, orthographic construction views, equipment inset, readable seams, non-graphic stylized fantasy. No copied franchise designs, text baked into textures, cinematic fog, invented extra limbs or altered gear between views. These are concept directions, not generated images.

## Approval gates

Silhouette passes at 96-pixel preview; costume agrees across all views; all seven clips reviewed; no required missing textures; no unexplained import scale compensation; effect matches declared reach and damage type; portrait agrees with the modeled hero; crowded-board test passes; source revision/reimport is demonstrated. A Python exit code alone does not approve the art.

Canonical source: `data/units.json`. Regenerate this dossier with `python tools/build_documents.py` after data edits. Do not hand-edit a stat table and leave the JSON unchanged.

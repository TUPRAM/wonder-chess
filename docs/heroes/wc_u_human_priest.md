# Mira Dawnwell — The Roadside Healer

**Human · Priest · Support · ALPHA**

Stable identity: `wc_u_human_priest`. Cost: **1 gold**. Rarity label: **Common**, separate from star level. Production and verification status is recorded separately in reports/implementation_state.json; this generated dossier does not certify an asset or build. All combat values are provisional prototype inputs.

Quick display name: **Mira**. Informational roles: Healer. Role tags provide no additional synergy.

## Character and world

Mira originally planned to run a quiet clinic near Brighthaven’s market. Traveling with Ada taught her how much difference an organized defense makes before healing is needed. She enters the trials to help train captains and sends field notes to Orla beneath Stoneveil, turning their friendly arguments into better care for both communities.

Home region: `brighthaven`. Affiliation: `dawn_compact`. Neither supplies a hidden third synergy. Proper names are original proposed fiction, not trademark-clearance claims.

## Appearance and art direction

Authored standing height: **1.7 m**, excluding raised equipment. Rig family: `humanoid_standard`. One logical tile at every star. All characters are adults, fully clothed and presented as non-graphic heroic fantasy.

### Silhouette and proportions

A bell-shaped short coat and a high open staff loop, balanced by a small medicine satchel. Her upper body stays narrower than a Guardian, with the staff serving as the long vertical accent.

### Face, hair and expression

Olive skin, hazel eyes, dark auburn hair in a loose bun, and a practical, attentive expression. A fabric headband frames her face without hiding it.

### Costume construction

Cream wool layers under a coral traveling mantle; the mantle is cut at the elbows for clean arm animation. Fitted trousers and walking boots replace a floor-length robe.

### Color palette

Cream #F0E6CC; coral #CF7067; muted teal #538E8D; warm brass #BC9B58.

### Equipment and magical focus

A polished wood staff ending in an open circular lantern and a square leather satchel with two large clasps. Small bottle shapes remain abstract accessories, never gameplay consumables.

### Three low-resolution identifiers

Circular staff head, coral shoulder mantle, and square hip satchel.

### Materials and surface detail

Soft woven cloth, oiled wood, dull brass and one small lantern emissive area. Paint folds in broad groups rather than dense noise.

### Back and side-view constraints

The mantle has a clean V seam; a wide satchel strap crosses from left shoulder to right hip. Keep the staff away from the bun in overhead poses.

## Combat statistics — without traits or temporary effects

| Property | One star | Two stars | Three stars |
|---|---:|---:|---:|
| Health | 650 | 1,170 | 2,106 |
| Basic attack damage | 34 | 61.2 | 110.16 |
| Attack delivery | ranged | ranged | ranged |
| Basic damage type | magic | magic | magic |
| Nominal attacks/second | 0.75 | 0.75 | 0.75 |
| Effective attacks/second at 20 Hz | 0.7407 | 0.7407 | 0.7407 |
| Range in tiles | 3 | 3 | 3 |
| Physical armor | 10 | 10 | 10 |
| Magic resistance | 20 | 20 | 20 |
| Movement tiles/second | 1.05 | 1.05 | 1.05 |

Nominal basic-attack DPS at one star: **25.50**, before mitigation, movement, stuns, skills, targeting downtime or timing quantization. Basic windup: 300 ms; ordinary projectile travel: 150 ms. No hidden critical hits, evasion, lifesteal or mana.

## One active skill

### Mend

**Player tooltip:** Heals the ally with the lowest health percentage.

**Indonesian draft:** Memulihkan kesehatan sekutu dengan persentase kesehatan terendah.

| Contract field | Value |
|---|---|
| Stable ability ID | `wc_a_human_priest` |
| Effect / target selector | `heal` / `lowest_health_ally` |
| One / two / three star magnitude | heal: 180 / 324 / 583 |
| Damage type | Not damaging |
| First-cast delay / cooldown | 3 s / 7 s |
| Windup / recovery | 0.35 s / 0.3 s |
| Effect duration | 0.0 s |
| Skill reach / area radius | 8 / 0 tiles |
| Can include self | True |
| Max dash distance | 0 tiles |
| Projectile travel | 0 ms |
| Affected stat | Not applicable |

Cooldown starts at successful cast commitment. An interrupted committed cast keeps its cooldown; an unavailable target leaves the ability ready and allows ordinary behavior. Area centers and area recipients are captured at release. Targeted projectiles keep their target ID but never retarget a defeated unit. Dash landing is reserved at commitment and validated before movement. See the rules contract for same-tick ordering, shield replacement and refresh semantics.

Health and basic damage use 1.00/1.80/3.24 star multipliers. Only explicitly authored skill magnitudes vary with stars; stun duration, range, radius, dash distance, cooldown and model footprint do not grow. A status-only skill may deliberately have identical behavior across stars; its owner still gains health and basic damage.

## Positioning and counterplay

**Preferred formation.** Second or third row behind a frontline unit, not alone in a corner exposed to flankers.

**Useful partners.** Ada Brightshield provides a long-lived healing target; Elin Moonsong can increase Mira’s ordinary attack cadence but never her skill cooldown.

**Counterplay.** Sylas Duskrun can reach the support line; burst area damage can outpace single-target Mend.

**Practical weakness.** Low durability and only one healed target per cast; no resurrection or cleanse.

**Difference from the nearest alternative.** Compared with Elin, Mira repairs health directly instead of accelerating nearby allies.

**Character-specific acceptance test.** Verify lowest-health percentage ties, self-healing eligibility, overheal cap, and no cast when all allies are full.

## Animation, effects and sound

Idle checks the battlefield rather than fussing with props. Movement is brisk and balanced. Basics point the staff for a small light bolt. Mend traces a single clear upward curve before its effect leaves the lantern.

**Skill effect:** A warm-gold pulse travels to the selected ally and resolves as two rising leaflike arcs. The target health bar briefly indicates effective healing, not overheal.

**Sound:** Soft bell pair and airy arrival tone, quieter than damage impacts. A dry cloth rustle supports movement without masking action sounds.

Author at 60 FPS, as in-place animations with no locomotion-driven root translation. Required clips: Idle, Move, Attack, Active, Hit, Defeat, Victory. The active release marker is frame 21 relative to animation start. Basic release marker is frame 18. These are presentation alignment points, not sources of authoritative damage. Idle begins as a 2-second loop; movement as a 1-second cycle; hit as 0.4 seconds; defeat as 1 second; victory as 1.5 seconds. Adjust clip lengths during animation review without altering gameplay timing.

A defeat uses a brief stagger, kneel or magical dissolve with no injury detail. Stars use UI pips, a subtle trim accent and a brief upgrade flourish; do not produce three separate bodies or enlarge the collision footprint.

## Blender construction and Unreal handoff

Start from the `humanoid_standard` base or a validated compatible family. Block silhouette before bevels; separate body, costume and equipment into named source collections. Build equipment as decorative fantasy game props, not real functional objects. Author model-space Z up and a consistent forward orientation, then prove conversion with the calibration fixture. Materials use one or two runtime slots and a shared atlas where it preserves identity.

Targets to profile: at most 15,000 LOD0 triangles, 1024-pixel default maps, up to 60 deforming bones and 4 influences per vertex. Lower-detail targets begin near 50% and 25% triangles. These are budgets, not measured performance.

Sockets: `weapon_r`, `weapon_l`, `cast_origin`, `head_ui`. Inspect shoulder, elbow, hip and knee extremes. Use separate rig proportions where needed; matching bone names is not proof of animation compatibility. Selection uses a stable unit proxy, not detailed prop collision. Team affiliation uses base rings/icons in addition to color, never a complete costume recolor.

**Specific production risk:** The circular staff opening must remain readable at distance; overly thin geometry will vanish. Mend must remain distinct from a shield bubble.

Required source/export locations:

- blender: `art-source/heroes/wc_u_human_priest/wc_u_human_priest.blend`

- mesh_fbx: `exports/heroes/wc_u_human_priest/SK_wc_u_human_priest.fbx`

- unreal_folder: `/Game/WonderChess/Heroes/wc_u_human_priest`

- portrait: `exports/heroes/wc_u_human_priest/portrait.png`

Create separate animation exports and texture maps, a model-derived portrait, front/side/back/three-quarter views, a gameplay-camera screenshot, and an actual Unreal animation capture. Log source/export hashes, skeleton revision, tool versions and import preset. Deliberately change one costume detail, re-export and verify existing material, skeleton, animation and actor references survive.

## Model-sheet generation brief

Original Wonder Chess high-fantasy character production sheet for Mira Dawnwell, The Roadside Healer. Human Priest, adult character, height 1.7 m. Front, true side, back and three-quarter views at matching scale, neutral A-pose plus one action pose. A bell-shaped short coat and a high open staff loop, balanced by a small medicine satchel. Her upper body stays narrower than a Guardian, with the staff serving as the long vertical accent. Olive skin, hazel eyes, dark auburn hair in a loose bun, and a practical, attentive expression. A fabric headband frames her face without hiding it. Cream wool layers under a coral traveling mantle; the mantle is cut at the elbows for clean arm animation. Fitted trousers and walking boots replace a floor-length robe. A polished wood staff ending in an open circular lantern and a square leather satchel with two large clasps. Small bottle shapes remain abstract accessories, never gameplay consumables. Palette: Cream #F0E6CC; coral #CF7067; muted teal #538E8D; warm brass #BC9B58. Flat neutral background, orthographic construction views, equipment inset, readable seams, non-graphic stylized fantasy. No copied franchise designs, text baked into textures, cinematic fog, invented extra limbs or altered gear between views. These are concept directions, not generated images.

## Approval gates

Silhouette passes at 96-pixel preview; costume agrees across all views; all seven clips reviewed; no required missing textures; no unexplained import scale compensation; effect matches declared reach and damage type; portrait agrees with the modeled hero; crowded-board test passes; source revision/reimport is demonstrated. A Python exit code alone does not approve the art.

Canonical source: `data/units.json`. Regenerate this dossier with `python tools/build_documents.py` after data edits. Do not hand-edit a stat table and leave the JSON unchanged.

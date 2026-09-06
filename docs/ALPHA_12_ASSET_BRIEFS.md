# Wonder Chess — Twelve Alpha Hero Asset Briefs

Use the per-hero art, animation and numerical contracts below alongside BLENDER_PRODUCTION.md. No model or render is included in this document.

# Ada Brightshield — The Gatekeeper

**Human · Guardian · Defender · ALPHA**

Stable identity: `wc_u_human_guardian`. Cost: **1 gold**. Rarity label: **Common**, separate from star level. Status: designed, not modeled or implemented by this kit. All combat values are provisional prototype inputs.

## Character and world

Ada kept Brighthaven’s river gate open during the evacuation of a flooded caravan road. She joins the Compact trials to teach young captains that protecting an ally is a deliberate choice, not a consolation role. Mira maintained the roadside aid station beside her gate, and the two trust each other without always agreeing on when to advance.

Home region: `brighthaven`. Affiliation: `dawn_compact`. Neither supplies a hidden third synergy. Proper names are original proposed fiction, not trademark-clearance claims.

## Appearance and art direction

Authored standing height: **1.82 m**, excluding raised equipment. Rig family: `humanoid_standard`. One logical tile at every star. All characters are adults, fully clothed and presented as non-graphic heroic fantasy.

### Silhouette and proportions

A broad inverted-triangle shoulder line over a compact waist, anchored by an oversized rounded kite shield on the left. The shield rises to eyebrow height when guarding, but stays below her eyes at rest.

### Face, hair and expression

Warm brown skin, square brows, dark eyes and a short black braid tucked behind the neck. Her calm, alert expression is readable without exaggerated facial animation.

### Costume construction

An ivory quilted coat sits under simplified steel breast and shoulder plates. A split navy tabard ends above the knees, leaving the leg silhouettes clear. Heavy boots and broad bracers make her planted stance apparent.

### Color palette

Navy #25466B; ivory #E9E2CD; brushed steel #9EAAB5; restrained gold #C7A25B. Gold covers only the shield crest and two fasteners.

### Equipment and magical focus

Left-hand kite shield with a raised rising-sun disk; short, broad fantasy sword in the right hand. Build the emblem as shallow geometry with a baked bevel, not dense engraving.

### Three low-resolution identifiers

The high curved shield, squared shoulder line, and single sun disk must survive a 96-pixel hero render.

### Materials and surface detail

Use a shared armor master, a cloth instance and a small emissive crest mask. Keep roughness separation between plate, fabric and the leather shield grip; no mirror-polished surfaces.

### Back and side-view constraints

A navy crossed strap carries a plain bedroll clasp; the braid sits clear of the shoulder plates. No long cape hides the back silhouette.

## Combat statistics — without traits or temporary effects

| Property | One star | Two stars | Three stars |
|---|---:|---:|---:|
| Health | 1,050 | 1,890 | 3,402 |
| Basic attack damage | 48 | 86.4 | 155.52 |
| Attack delivery | melee | melee | melee |
| Basic damage type | physical | physical | physical |
| Nominal attacks/second | 0.70 | 0.70 | 0.70 |
| Effective attacks/second at 20 Hz | 0.6897 | 0.6897 | 0.6897 |
| Range in tiles | 1 | 1 | 1 |
| Physical armor | 35 | 35 | 35 |
| Magic resistance | 15 | 15 | 15 |
| Movement tiles/second | 1.00 | 1.00 | 1.00 |

Nominal basic-attack DPS at one star: **33.60**, before mitigation, movement, stuns, skills, targeting downtime or timing quantization. Basic windup: 250 ms; ordinary projectile travel: 0 ms. No hidden critical hits, evasion, lifesteal or mana.

## One active skill

### Sunward Guard

**Player tooltip:** Gains a shield for three seconds.

**Indonesian draft:** Memberikan perisai sementara kepada diri sendiri.

| Contract field | Value |
|---|---|
| Stable ability ID | `wc_a_human_guardian` |
| Effect / target selector | `shield` / `self` |
| One / two / three star magnitude | 200 / 360 / 648 |
| Damage type | Not damaging |
| First-cast delay / cooldown | 2 s / 8 s |
| Windup / recovery | 0.3 s / 0.3 s |
| Effect duration | 3 s |
| Skill reach / area radius | 0 / 0 tiles |
| Can include self | True |
| Max dash distance | 0 tiles |
| Projectile travel | 0 ms |
| Affected stat | Not applicable |

Cooldown starts at successful cast commitment. An interrupted committed cast keeps its cooldown; an unavailable target leaves the ability ready and allows ordinary behavior. Area centers and area recipients are captured at release. Targeted projectiles keep their target ID but never retarget a defeated unit. Dash landing is reserved at commitment and validated before movement. See the rules contract for same-tick ordering, shield replacement and refresh semantics.

Health and basic damage use 1.00/1.80/3.24 star multipliers. Only explicitly authored skill magnitudes vary with stars; stun duration, range, radius, dash distance, cooldown and model footprint do not grow. A status-only skill may deliberately have identical behavior across stars; its owner still gains health and basic damage.

## Positioning and counterplay

**Preferred formation.** Front row, one cell ahead of a damage dealer; center-left leaves room for her shield silhouette.

**Useful partners.** Mira Dawnwell extends Ada’s time on the frontline; Rowan Emberwick uses the space she buys.

**Counterplay.** Zura Stormcall applies magic damage against Ada’s lower resistance; sustained focused attacks can exhaust the shield before its duration ends.

**Practical weakness.** Low offensive output and a self-only shield: she cannot rescue a distant backline unit.

**Difference from the nearest alternative.** Unlike Borin, Ada prevents damage to herself instead of interrupting surrounding enemies.

**Character-specific acceptance test.** Check that a shielded Ada still takes overflow damage correctly and cannot refresh a stronger shield with a weaker cast.

## Animation, effects and sound

Idle with weight on the rear foot and shield angled outward. Walk with measured short steps. Basic attacks use one readable right-hand sweep. The active lifts the shield before the crest lights; return to guard without whole-body root motion.

**Skill effect:** A thin warm-gold shell follows the shield silhouette and a brief low-opacity arc wraps the torso. Do not use a solid sphere that obscures nearby heroes.

**Sound:** A firm boot placement, restrained metal knock, and short rounded shield chime. Avoid a booming impact on every basic attack.

Author at 60 FPS, as in-place animations with no locomotion-driven root translation. Required clips: Idle, Move, Attack, Active, Hit, Defeat, Victory. The active release marker is frame 18 relative to animation start. Basic release marker is frame 15. These are presentation alignment points, not sources of authoritative damage. Idle begins as a 2-second loop; movement as a 1-second cycle; hit as 0.4 seconds; defeat as 1 second; victory as 1.5 seconds. Adjust clip lengths during animation review without altering gameplay timing.

A defeat uses a brief stagger, kneel or magical dissolve with no injury detail. Stars use UI pips, a subtle trim accent and a brief upgrade flourish; do not produce three separate bodies or enlarge the collision footprint.

## Blender construction and Unreal handoff

Start from the `humanoid_standard` base or a validated compatible family. Block silhouette before bevels; separate body, costume and equipment into named source collections. Build equipment as decorative fantasy game props, not real functional objects. Author model-space Z up and a consistent forward orientation, then prove conversion with the calibration fixture. Materials use one or two runtime slots and a shared atlas where it preserves identity.

Targets to profile: at most 15,000 LOD0 triangles, 1024-pixel default maps, up to 60 deforming bones and 4 influences per vertex. Lower-detail targets begin near 50% and 25% triangles. These are budgets, not measured performance.

Sockets: `weapon_r`, `weapon_l`, `cast_origin`, `head_ui`. Inspect shoulder, elbow, hip and knee extremes. Use separate rig proportions where needed; matching bone names is not proof of animation compatibility. Selection uses a stable unit proxy, not detailed prop collision. Team affiliation uses base rings/icons in addition to color, never a complete costume recolor.

**Specific production risk:** Shield/forearm intersections during attack recovery are the main deformation risk. Test full left-arm elevation and adjacent-hero visibility.

Required source/export locations:

- blender: `art-source/heroes/wc_u_human_guardian/wc_u_human_guardian.blend`

- mesh_fbx: `exports/heroes/wc_u_human_guardian/SK_wc_u_human_guardian.fbx`

- unreal_folder: `/Game/WonderChess/Heroes/wc_u_human_guardian`

- portrait: `exports/heroes/wc_u_human_guardian/portrait.png`

Create separate animation exports and texture maps, a model-derived portrait, front/side/back/three-quarter views, a gameplay-camera screenshot, and an actual Unreal animation capture. Log source/export hashes, skeleton revision, tool versions and import preset. Deliberately change one costume detail, re-export and verify existing material, skeleton, animation and actor references survive.

## Model-sheet generation brief

Original Wonder Chess high-fantasy character production sheet for Ada Brightshield, The Gatekeeper. Human Guardian, adult character, height 1.82 m. Front, true side, back and three-quarter views at matching scale, neutral A-pose plus one action pose. A broad inverted-triangle shoulder line over a compact waist, anchored by an oversized rounded kite shield on the left. The shield rises to eyebrow height when guarding, but stays below her eyes at rest. Warm brown skin, square brows, dark eyes and a short black braid tucked behind the neck. Her calm, alert expression is readable without exaggerated facial animation. An ivory quilted coat sits under simplified steel breast and shoulder plates. A split navy tabard ends above the knees, leaving the leg silhouettes clear. Heavy boots and broad bracers make her planted stance apparent. Left-hand kite shield with a raised rising-sun disk; short, broad fantasy sword in the right hand. Build the emblem as shallow geometry with a baked bevel, not dense engraving. Palette: Navy #25466B; ivory #E9E2CD; brushed steel #9EAAB5; restrained gold #C7A25B. Gold covers only the shield crest and two fasteners. Flat neutral background, orthographic construction views, equipment inset, readable seams, non-graphic stylized fantasy. No copied franchise designs, text baked into textures, cinematic fog, invented extra limbs or altered gear between views. These are concept directions, not generated images.

## Approval gates

Silhouette passes at 96-pixel preview; costume agrees across all views; all seven clips reviewed; no required missing textures; no unexplained import scale compensation; effect matches declared reach and damage type; portrait agrees with the modeled hero; crowded-board test passes; source revision/reimport is demonstrated. A Python exit code alone does not approve the art.

Canonical source: `data/units.json`. Regenerate this dossier with `python tools/build_documents.py` after data edits. Do not hand-edit a stat table and leave the JSON unchanged.

---
# Mira Dawnwell — The Roadside Healer

**Human · Priest · Support · ALPHA**

Stable identity: `wc_u_human_priest`. Cost: **1 gold**. Rarity label: **Common**, separate from star level. Status: designed, not modeled or implemented by this kit. All combat values are provisional prototype inputs.

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
| One / two / three star magnitude | 180 / 324 / 583 |
| Damage type | Not damaging |
| First-cast delay / cooldown | 3 s / 7 s |
| Windup / recovery | 0.35 s / 0.3 s |
| Effect duration | 0 s |
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

---
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

---
# Liora Leafstep — The Canopy Scout

**Elf · Ranger · Ranged damage · ALPHA**

Stable identity: `wc_u_elf_ranger`. Cost: **1 gold**. Rarity label: **Common**, separate from star level. Status: designed, not modeled or implemented by this kit. All combat values are provisional prototype inputs.

## Character and world

Liora mapped the canopy paths above Thistlewood’s old trade road. She believes visitors protect a forest better when they understand it, so she guides traders rather than turning them away. Elin persuaded her to enter the trials, where she studies how to keep a ranged ally safe without simply hiding it in a corner.

Home region: `thistlewood`. Affiliation: `greenward_circle`. Neither supplies a hidden third synergy. Proper names are original proposed fiction, not trademark-clearance claims.

## Appearance and art direction

Authored standing height: **1.88 m**, excluding raised equipment. Rig family: `humanoid_slender`. One logical tile at every star. All characters are adults, fully clothed and presented as non-graphic heroic fantasy.

### Silhouette and proportions

A light forward-leaning profile, long crescent bow and three short leaflike cloak panels. The cloak stops above the knees, revealing long, narrow leg shapes.

### Face, hair and expression

Golden-brown skin, gray-green eyes, swept-back pointed ears and pale brown hair tied into a short fan. Her gaze is alert rather than severe.

### Costume construction

Moss fabric over fitted leather shoulder protection, a single pale scarf and flexible boots. The bow-side shoulder stays clear; no oversized pauldron blocks the draw.

### Color palette

Moss #647A4B; pale mint #B7CBB0; chestnut #765641; warm linen #DACCAB.

### Equipment and magical focus

A stylized crescent bow with broad flattened limbs and a slim back quiver. The bowstring is simplified geometry that can be hidden at distant LODs.

### Three low-resolution identifiers

Crescent bow, three separated cloak panels, and sideways archery stance.

### Materials and surface detail

Matte woven cloth, satin-finished wood and leathery boots. Leaf motifs are broad seam shapes, not transparency cutouts.

### Back and side-view constraints

Quiver sits diagonally and avoids the shoulder draw arc. Cloak panels spread enough to read as three shapes without requiring cloth bones beyond a small secondary chain.

## Combat statistics — without traits or temporary effects

| Property | One star | Two stars | Three stars |
|---|---:|---:|---:|
| Health | 670 | 1,206 | 2,170.8 |
| Basic attack damage | 60 | 108 | 194.4 |
| Attack delivery | ranged | ranged | ranged |
| Basic damage type | physical | physical | physical |
| Nominal attacks/second | 0.85 | 0.85 | 0.85 |
| Effective attacks/second at 20 Hz | 0.8333 | 0.8333 | 0.8333 |
| Range in tiles | 4 | 4 | 4 |
| Physical armor | 10 | 10 | 10 |
| Magic resistance | 10 | 10 | 10 |
| Movement tiles/second | 1.15 | 1.15 | 1.15 |

Nominal basic-attack DPS at one star: **51.00**, before mitigation, movement, stuns, skills, targeting downtime or timing quantization. Basic windup: 300 ms; ordinary projectile travel: 150 ms. No hidden critical hits, evasion, lifesteal or mana.

## One active skill

### Leafstep

**Player tooltip:** Dashes away from her target while keeping it in range.

**Indonesian draft:** Melakukan dash menjauh dari sasaran sambil tetap dalam jangkauan serang.

| Contract field | Value |
|---|---|
| Stable ability ID | `wc_a_elf_ranger` |
| Effect / target selector | `dash` / `retreat_from_current_enemy` |
| One / two / three star magnitude | Not applicable / Not applicable / Not applicable |
| Damage type | Not damaging |
| First-cast delay / cooldown | 2 s / 7.5 s |
| Windup / recovery | 0.2 s / 0.15 s |
| Effect duration | 0 s |
| Skill reach / area radius | 4 / 0 tiles |
| Can include self | False |
| Max dash distance | 2 tiles |
| Projectile travel | 0 ms |
| Affected stat | Not applicable |

Cooldown starts at successful cast commitment. An interrupted committed cast keeps its cooldown; an unavailable target leaves the ability ready and allows ordinary behavior. Area centers and area recipients are captured at release. Targeted projectiles keep their target ID but never retarget a defeated unit. Dash landing is reserved at commitment and validated before movement. See the rules contract for same-tick ordering, shield replacement and refresh semantics.

Health and basic damage use 1.00/1.80/3.24 star multipliers. Only explicitly authored skill magnitudes vary with stars; stun duration, range, radius, dash distance, cooldown and model footprint do not grow. A status-only skill may deliberately have identical behavior across stars; its owner still gains health and basic damage.

## Positioning and counterplay

**Preferred formation.** Backline with at least one free retreat tile; avoid filling every adjacent rear cell.

**Useful partners.** Ada or Borin gives Liora room to reposition; Tessa completes Ranger.

**Counterplay.** A fully crowded backline can deny landing cells, and pursuing Rogues can force repeated relocation.

**Practical weakness.** The skill deals no damage and fails to commit when no useful legal landing exists.

**Difference from the nearest alternative.** Tessa provides burst damage; Liora trades that burst for positional resilience.

**Character-specific acceptance test.** Test blocked board edges, equal-distance destinations, two dash reservations and target loss before release.

## Animation, effects and sound

Idle scans in short head turns. Movement uses light lateral steps. Basics draw, pause visibly at release, and recover. Leafstep crouches briefly then slides through a controlled airborne step to the reserved cell.

**Skill effect:** A short mint leaf trail follows the dash and fades within half a second. No invisibility, shield or damage accompanies the dash.

**Sound:** A soft bow snap and a brief brushlike dash sweep. Keep leaf rustle short and non-looping.

Author at 60 FPS, as in-place animations with no locomotion-driven root translation. Required clips: Idle, Move, Attack, Active, Hit, Defeat, Victory. The active release marker is frame 12 relative to animation start. Basic release marker is frame 18. These are presentation alignment points, not sources of authoritative damage. Idle begins as a 2-second loop; movement as a 1-second cycle; hit as 0.4 seconds; defeat as 1 second; victory as 1.5 seconds. Adjust clip lengths during animation review without altering gameplay timing.

A defeat uses a brief stagger, kneel or magical dissolve with no injury detail. Stars use UI pips, a subtle trim accent and a brief upgrade flourish; do not produce three separate bodies or enlarge the collision footprint.

## Blender construction and Unreal handoff

Start from the `humanoid_slender` base or a validated compatible family. Block silhouette before bevels; separate body, costume and equipment into named source collections. Build equipment as decorative fantasy game props, not real functional objects. Author model-space Z up and a consistent forward orientation, then prove conversion with the calibration fixture. Materials use one or two runtime slots and a shared atlas where it preserves identity.

Targets to profile: at most 15,000 LOD0 triangles, 1024-pixel default maps, up to 60 deforming bones and 4 influences per vertex. Lower-detail targets begin near 50% and 25% triangles. These are budgets, not measured performance.

Sockets: `weapon_r`, `weapon_l`, `cast_origin`, `head_ui`. Inspect shoulder, elbow, hip and knee extremes. Use separate rig proportions where needed; matching bone names is not proof of animation compatibility. Selection uses a stable unit proxy, not detailed prop collision. Team affiliation uses base rings/icons in addition to color, never a complete costume recolor.

**Specific production risk:** Foot sliding during the dash is acceptable only within the deliberate magical slide, not normal walking. Reserved tile and displayed landing must agree.

Required source/export locations:

- blender: `art-source/heroes/wc_u_elf_ranger/wc_u_elf_ranger.blend`

- mesh_fbx: `exports/heroes/wc_u_elf_ranger/SK_wc_u_elf_ranger.fbx`

- unreal_folder: `/Game/WonderChess/Heroes/wc_u_elf_ranger`

- portrait: `exports/heroes/wc_u_elf_ranger/portrait.png`

Create separate animation exports and texture maps, a model-derived portrait, front/side/back/three-quarter views, a gameplay-camera screenshot, and an actual Unreal animation capture. Log source/export hashes, skeleton revision, tool versions and import preset. Deliberately change one costume detail, re-export and verify existing material, skeleton, animation and actor references survive.

## Model-sheet generation brief

Original Wonder Chess high-fantasy character production sheet for Liora Leafstep, The Canopy Scout. Elf Ranger, adult character, height 1.88 m. Front, true side, back and three-quarter views at matching scale, neutral A-pose plus one action pose. A light forward-leaning profile, long crescent bow and three short leaflike cloak panels. The cloak stops above the knees, revealing long, narrow leg shapes. Golden-brown skin, gray-green eyes, swept-back pointed ears and pale brown hair tied into a short fan. Her gaze is alert rather than severe. Moss fabric over fitted leather shoulder protection, a single pale scarf and flexible boots. The bow-side shoulder stays clear; no oversized pauldron blocks the draw. A stylized crescent bow with broad flattened limbs and a slim back quiver. The bowstring is simplified geometry that can be hidden at distant LODs. Palette: Moss #647A4B; pale mint #B7CBB0; chestnut #765641; warm linen #DACCAB. Flat neutral background, orthographic construction views, equipment inset, readable seams, non-graphic stylized fantasy. No copied franchise designs, text baked into textures, cinematic fog, invented extra limbs or altered gear between views. These are concept directions, not generated images.

## Approval gates

Silhouette passes at 96-pixel preview; costume agrees across all views; all seven clips reviewed; no required missing textures; no unexplained import scale compensation; effect matches declared reach and damage type; portrait agrees with the modeled hero; crowded-board test passes; source revision/reimport is demonstrated. A Python exit code alone does not approve the art.

Canonical source: `data/units.json`. Regenerate this dossier with `python tools/build_documents.py` after data edits. Do not hand-edit a stat table and leave the JSON unchanged.

---
# Elin Moonsong — The Grove Cantor

**Elf · Priest · Support · ALPHA**

Stable identity: `wc_u_elf_priest`. Cost: **2 gold**. Rarity label: **Uncommon**, separate from star level. Status: designed, not modeled or implemented by this kit. All combat values are provisional prototype inputs.

## Character and world

Elin directs music at Thistlewood’s seasonal gatherings, where songs help visiting communities learn each other’s histories. When travel became dangerous, she adapted those rhythms into marching exercises. She joins Liora in the trials to prove that cooperation can be felt in a formation as clearly as it can be heard in a chorus.

Home region: `thistlewood`. Affiliation: `greenward_circle`. Neither supplies a hidden third synergy. Proper names are original proposed fiction, not trademark-clearance claims.

## Appearance and art direction

Authored standing height: **1.85 m**, excluding raised equipment. Rig family: `humanoid_slender`. One logical tile at every star. All characters are adults, fully clothed and presented as non-graphic heroic fantasy.

### Silhouette and proportions

An upright pear-shaped silhouette with an open half-moon harp framing one shoulder. Layered petal-shaped sleeves form large, separated planes rather than many small leaves.

### Face, hair and expression

Deep umber skin, pale blue eyes and silver hair in a compact crown braid. Pointed ears remain visible on both sides of the harp.

### Costume construction

Blue-green tunic with ivory sleeve ends, a short overlapping overskirt and practical fitted boots. Silver trim follows one large curved line across the torso.

### Color palette

Deep teal #337A80; moon ivory #E3E8DD; blue-gray #6E86A0; silver #B6C7C9.

### Equipment and magical focus

A compact crescent harp held close to the torso, with only a few thick stylized strings. A small charm at the waist marks her order without introducing a resource.

### Three low-resolution identifiers

Open crescent harp, crown braid, and layered pale sleeve ends.

### Materials and surface detail

Smooth cloth with sparse brocade normals, brushed silver and a faint cool glow on the harp rim. Do not use constantly glowing eyes.

### Back and side-view constraints

Short robe panels leave the legs visible; a braided cord forms a clean circle high on the back. The harp must not clip through the spine during turning.

## Combat statistics — without traits or temporary effects

| Property | One star | Two stars | Three stars |
|---|---:|---:|---:|
| Health | 700 | 1,260 | 2,268 |
| Basic attack damage | 35 | 63 | 113.4 |
| Attack delivery | ranged | ranged | ranged |
| Basic damage type | magic | magic | magic |
| Nominal attacks/second | 0.80 | 0.80 | 0.80 |
| Effective attacks/second at 20 Hz | 0.8000 | 0.8000 | 0.8000 |
| Range in tiles | 3 | 3 | 3 |
| Physical armor | 10 | 10 | 10 |
| Magic resistance | 25 | 25 | 25 |
| Movement tiles/second | 1.05 | 1.05 | 1.05 |

Nominal basic-attack DPS at one star: **28.00**, before mitigation, movement, stuns, skills, targeting downtime or timing quantization. Basic windup: 300 ms; ordinary projectile travel: 150 ms. No hidden critical hits, evasion, lifesteal or mana.

## One active skill

### Quickening Song

**Player tooltip:** Temporarily increases nearby allies’ attack speed.

**Indonesian draft:** Meningkatkan kecepatan serang diri sendiri dan sekutu bersebelahan untuk sementara.

| Contract field | Value |
|---|---|
| Stable ability ID | `wc_a_elf_priest` |
| Effect / target selector | `stat_modifier` / `adjacent_allies` |
| One / two / three star magnitude | 20% / 25% / 30% |
| Damage type | Not damaging |
| First-cast delay / cooldown | 2.5 s / 9 s |
| Windup / recovery | 0.35 s / 0.3 s |
| Effect duration | 3 s |
| Skill reach / area radius | 1 / 1 tiles |
| Can include self | True |
| Max dash distance | 0 tiles |
| Projectile travel | 0 ms |
| Affected stat | attack_rate |

Cooldown starts at successful cast commitment. An interrupted committed cast keeps its cooldown; an unavailable target leaves the ability ready and allows ordinary behavior. Area centers and area recipients are captured at release. Targeted projectiles keep their target ID but never retarget a defeated unit. Dash landing is reserved at commitment and validated before movement. See the rules contract for same-tick ordering, shield replacement and refresh semantics.

Health and basic damage use 1.00/1.80/3.24 star multipliers. Only explicitly authored skill magnitudes vary with stars; stun duration, range, radius, dash distance, cooldown and model footprint do not grow. A status-only skill may deliberately have identical behavior across stars; its owner still gains health and basic damage.

## Positioning and counterplay

**Preferred formation.** One row behind clustered attackers so several allies occupy the eight neighboring cells.

**Useful partners.** Tessa and Liora use the attack-rate bonus effectively; Mira activates Priest support potency.

**Counterplay.** Area spells punish the grouping that makes the song efficient.

**Practical weakness.** She does not heal, and moving away after release does not grant the buff to newly adjacent units.

**Difference from the nearest alternative.** Mira restores health; Elin improves ordinary attack tempo without shortening active cooldowns.

**Character-specific acceptance test.** Priest must strengthen the positive attack-rate buff as well as healing/shields; equal-key casts must not stack indefinitely.

## Animation, effects and sound

Idle shifts a hand over the harp. Basic attacks pluck a single note. The active plants both feet and plays a broad chord, opening the elbows so the cast silhouette differs from an attack.

**Skill effect:** A low teal ring outlines affected adjacent cells, then small wing-shaped chevrons appear briefly over recipients. No continuous aura tick; recipients are snapshotted at release.

**Sound:** One clear string note for basics and a restrained three-note chord for the skill. Separate the buff sound from Mira’s healing bell.

Author at 60 FPS, as in-place animations with no locomotion-driven root translation. Required clips: Idle, Move, Attack, Active, Hit, Defeat, Victory. The active release marker is frame 21 relative to animation start. Basic release marker is frame 18. These are presentation alignment points, not sources of authoritative damage. Idle begins as a 2-second loop; movement as a 1-second cycle; hit as 0.4 seconds; defeat as 1 second; victory as 1.5 seconds. Adjust clip lengths during animation review without altering gameplay timing.

A defeat uses a brief stagger, kneel or magical dissolve with no injury detail. Stars use UI pips, a subtle trim accent and a brief upgrade flourish; do not produce three separate bodies or enlarge the collision footprint.

## Blender construction and Unreal handoff

Start from the `humanoid_slender` base or a validated compatible family. Block silhouette before bevels; separate body, costume and equipment into named source collections. Build equipment as decorative fantasy game props, not real functional objects. Author model-space Z up and a consistent forward orientation, then prove conversion with the calibration fixture. Materials use one or two runtime slots and a shared atlas where it preserves identity.

Targets to profile: at most 15,000 LOD0 triangles, 1024-pixel default maps, up to 60 deforming bones and 4 influences per vertex. Lower-detail targets begin near 50% and 25% triangles. These are budgets, not measured performance.

Sockets: `weapon_r`, `weapon_l`, `cast_origin`, `head_ui`. Inspect shoulder, elbow, hip and knee extremes. Use separate rig proportions where needed; matching bone names is not proof of animation compatibility. Selection uses a stable unit proxy, not detailed prop collision. Team affiliation uses base rings/icons in addition to color, never a complete costume recolor.

**Specific production risk:** String geometry and hands can shimmer or intersect. Simplify the finger action and let the chord’s full-body gesture carry readability.

Required source/export locations:

- blender: `art-source/heroes/wc_u_elf_priest/wc_u_elf_priest.blend`

- mesh_fbx: `exports/heroes/wc_u_elf_priest/SK_wc_u_elf_priest.fbx`

- unreal_folder: `/Game/WonderChess/Heroes/wc_u_elf_priest`

- portrait: `exports/heroes/wc_u_elf_priest/portrait.png`

Create separate animation exports and texture maps, a model-derived portrait, front/side/back/three-quarter views, a gameplay-camera screenshot, and an actual Unreal animation capture. Log source/export hashes, skeleton revision, tool versions and import preset. Deliberately change one costume detail, re-export and verify existing material, skeleton, animation and actor references survive.

## Model-sheet generation brief

Original Wonder Chess high-fantasy character production sheet for Elin Moonsong, The Grove Cantor. Elf Priest, adult character, height 1.85 m. Front, true side, back and three-quarter views at matching scale, neutral A-pose plus one action pose. An upright pear-shaped silhouette with an open half-moon harp framing one shoulder. Layered petal-shaped sleeves form large, separated planes rather than many small leaves. Deep umber skin, pale blue eyes and silver hair in a compact crown braid. Pointed ears remain visible on both sides of the harp. Blue-green tunic with ivory sleeve ends, a short overlapping overskirt and practical fitted boots. Silver trim follows one large curved line across the torso. A compact crescent harp held close to the torso, with only a few thick stylized strings. A small charm at the waist marks her order without introducing a resource. Palette: Deep teal #337A80; moon ivory #E3E8DD; blue-gray #6E86A0; silver #B6C7C9. Flat neutral background, orthographic construction views, equipment inset, readable seams, non-graphic stylized fantasy. No copied franchise designs, text baked into textures, cinematic fog, invented extra limbs or altered gear between views. These are concept directions, not generated images.

## Approval gates

Silhouette passes at 96-pixel preview; costume agrees across all views; all seven clips reviewed; no required missing textures; no unexplained import scale compensation; effect matches declared reach and damage type; portrait agrees with the modeled hero; crowded-board test passes; source revision/reimport is demonstrated. A Python exit code alone does not approve the art.

Canonical source: `data/units.json`. Regenerate this dossier with `python tools/build_documents.py` after data edits. Do not hand-edit a stat table and leave the JSON unchanged.

---
# Sylas Duskrun — The Lantern Runner

**Elf · Rogue · Disruption · ALPHA**

Stable identity: `wc_u_elf_rogue`. Cost: **3 gold**. Rarity label: **Rare**, separate from star level. Status: designed, not modeled or implemented by this kit. All combat values are provisional prototype inputs.

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

### Backline Dash

**Player tooltip:** Dashes beside the farthest enemy when a landing tile is free.

**Indonesian draft:** Melakukan dash ke petak kosong di samping musuh terjauh.

| Contract field | Value |
|---|---|
| Stable ability ID | `wc_a_elf_rogue` |
| Effect / target selector | `dash` / `farthest_enemy_adjacent` |
| One / two / three star magnitude | Not applicable / Not applicable / Not applicable |
| Damage type | Not damaging |
| First-cast delay / cooldown | 1 s / 8.5 s |
| Windup / recovery | 0.2 s / 0.15 s |
| Effect duration | 0 s |
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

---
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

---
# Tessa Brassbolt — The Clockwork Marksman

**Dwarf · Ranger · Ranged damage · ALPHA**

Stable identity: `wc_u_dwarf_ranger`. Cost: **2 gold**. Rarity label: **Uncommon**, separate from star level. Status: designed, not modeled or implemented by this kit. All combat values are provisional prototype inputs.

## Character and world

Tessa builds reliable tools for Stoneveil’s long-distance couriers and tests every invention herself. She joined the trials to show that dwarven craft can support a team without adding another suit of heavy armor. Borin is her favorite test partner because he notices every rattle, and Liora is the rival whose accuracy she quietly admires.

Home region: `stoneveil`. Affiliation: `hearthwright_union`. Neither supplies a hidden third synergy. Proper names are original proposed fiction, not trademark-clearance claims.

## Appearance and art direction

Authored standing height: **1.32 m**, excluding raised equipment. Rig family: `humanoid_stocky`. One logical tile at every star. All characters are adults, fully clothed and presented as non-graphic heroic fantasy.

### Silhouette and proportions

A compact upright body with a wide horizontal crossbow and a high single-lens goggle shape above the forehead. A short jacket flares just enough to contrast with the weapon bar.

### Face, hair and expression

Freckled medium-brown skin, dark eyes, cropped copper hair and a confident grin. Goggles sit above the eyes during normal play so expressions remain visible.

### Costume construction

Mustard work jacket over charcoal padding, leather forearm guards, sturdy trousers and broad boots. A few oversized straps suggest workshop practicality.

### Color palette

Mustard #C5A04B; charcoal #404851; copper #B67B55; pale linen #D9CDAF.

### Equipment and magical focus

A broad stylized crank crossbow with exaggerated fantasy housing and a circular side wheel. It is a game prop, not a functional construction plan; mechanisms remain decorative.

### Three low-resolution identifiers

Horizontal crossbow silhouette, forehead goggles and mustard jacket.

### Materials and surface detail

Worn painted wood, brushed copper, matte leather and a tiny cool aiming-gem emissive point. Do not use transparent scope glass.

### Back and side-view constraints

A flat bolt case is strapped low between the shoulders; jacket seams form a large X. Keep all parts outside the elbows’ reload arc.

## Combat statistics — without traits or temporary effects

| Property | One star | Two stars | Three stars |
|---|---:|---:|---:|
| Health | 760 | 1,368 | 2,462.4 |
| Basic attack damage | 68 | 122.4 | 220.32 |
| Attack delivery | ranged | ranged | ranged |
| Basic damage type | physical | physical | physical |
| Nominal attacks/second | 0.80 | 0.80 | 0.80 |
| Effective attacks/second at 20 Hz | 0.8000 | 0.8000 | 0.8000 |
| Range in tiles | 4 | 4 | 4 |
| Physical armor | 20 | 20 | 20 |
| Magic resistance | 10 | 10 | 10 |
| Movement tiles/second | 0.95 | 0.95 | 0.95 |

Nominal basic-attack DPS at one star: **54.40**, before mitigation, movement, stuns, skills, targeting downtime or timing quantization. Basic windup: 300 ms; ordinary projectile travel: 150 ms. No hidden critical hits, evasion, lifesteal or mana.

## One active skill

### Heavy Bolt

**Player tooltip:** Fires a stronger physical shot at her current target.

**Indonesian draft:** Memberikan kerusakan fisik kepada sasaran saat ini.

| Contract field | Value |
|---|---|
| Stable ability ID | `wc_a_dwarf_ranger` |
| Effect / target selector | `damage` / `current_enemy` |
| One / two / three star magnitude | 170 / 306 / 551 |
| Damage type | physical |
| First-cast delay / cooldown | 2.5 s / 6.5 s |
| Windup / recovery | 0.35 s / 0.3 s |
| Effect duration | 0 s |
| Skill reach / area radius | 4 / 0 tiles |
| Can include self | False |
| Max dash distance | 0 tiles |
| Projectile travel | 150 ms |
| Affected stat | Not applicable |

Cooldown starts at successful cast commitment. An interrupted committed cast keeps its cooldown; an unavailable target leaves the ability ready and allows ordinary behavior. Area centers and area recipients are captured at release. Targeted projectiles keep their target ID but never retarget a defeated unit. Dash landing is reserved at commitment and validated before movement. See the rules contract for same-tick ordering, shield replacement and refresh semantics.

Health and basic damage use 1.00/1.80/3.24 star multipliers. Only explicitly authored skill magnitudes vary with stars; stun duration, range, radius, dash distance, cooldown and model footprint do not grow. A status-only skill may deliberately have identical behavior across stars; its owner still gains health and basic damage.

## Positioning and counterplay

**Preferred formation.** Backline behind protection, with a clear visual lane and space for the crossbow’s silhouette.

**Useful partners.** Liora completes Ranger; Elin increases ordinary shots between Heavy Bolt casts.

**Counterplay.** Armor reduces both her basics and her active; backline pressure can interrupt the long active windup.

**Practical weakness.** No mobility or area damage, and a shot expires if its target is already defeated.

**Difference from the nearest alternative.** Liora trades burst for movement; Tessa is a stationary physical-damage specialist.

**Character-specific acceptance test.** Heavy Bolt uses ability damage rules, not the Ranger basic-only bonus; source Orclike bonuses must not appear on a Dwarf.

## Animation, effects and sound

Idle checks the line of sight with a small tilt. Basics brace, fire and reset the bow. The active plants both feet, pulls the housing close and releases with a longer visible windup than a basic shot.

**Skill effect:** A bright compact bolt with a short trail and a sharp target flash. It never pierces or explodes.

**Sound:** A dry mechanical click and compact fantasy bow thump; the active adds a short metallic accent rather than a firearm report.

Author at 60 FPS, as in-place animations with no locomotion-driven root translation. Required clips: Idle, Move, Attack, Active, Hit, Defeat, Victory. The active release marker is frame 21 relative to animation start. Basic release marker is frame 18. These are presentation alignment points, not sources of authoritative damage. Idle begins as a 2-second loop; movement as a 1-second cycle; hit as 0.4 seconds; defeat as 1 second; victory as 1.5 seconds. Adjust clip lengths during animation review without altering gameplay timing.

A defeat uses a brief stagger, kneel or magical dissolve with no injury detail. Stars use UI pips, a subtle trim accent and a brief upgrade flourish; do not produce three separate bodies or enlarge the collision footprint.

## Blender construction and Unreal handoff

Start from the `humanoid_stocky` base or a validated compatible family. Block silhouette before bevels; separate body, costume and equipment into named source collections. Build equipment as decorative fantasy game props, not real functional objects. Author model-space Z up and a consistent forward orientation, then prove conversion with the calibration fixture. Materials use one or two runtime slots and a shared atlas where it preserves identity.

Targets to profile: at most 15,000 LOD0 triangles, 1024-pixel default maps, up to 60 deforming bones and 4 influences per vertex. Lower-detail targets begin near 50% and 25% triangles. These are budgets, not measured performance.

Sockets: `weapon_r`, `weapon_l`, `cast_origin`, `head_ui`. Inspect shoulder, elbow, hip and knee extremes. Use separate rig proportions where needed; matching bone names is not proof of animation compatibility. Selection uses a stable unit proxy, not detailed prop collision. Team affiliation uses base rings/icons in addition to color, never a complete costume recolor.

**Specific production risk:** The wide prop can overlap neighboring units. Use its lowered rest pose outside windup and a close-to-body turn pose.

Required source/export locations:

- blender: `art-source/heroes/wc_u_dwarf_ranger/wc_u_dwarf_ranger.blend`

- mesh_fbx: `exports/heroes/wc_u_dwarf_ranger/SK_wc_u_dwarf_ranger.fbx`

- unreal_folder: `/Game/WonderChess/Heroes/wc_u_dwarf_ranger`

- portrait: `exports/heroes/wc_u_dwarf_ranger/portrait.png`

Create separate animation exports and texture maps, a model-derived portrait, front/side/back/three-quarter views, a gameplay-camera screenshot, and an actual Unreal animation capture. Log source/export hashes, skeleton revision, tool versions and import preset. Deliberately change one costume detail, re-export and verify existing material, skeleton, animation and actor references survive.

## Model-sheet generation brief

Original Wonder Chess high-fantasy character production sheet for Tessa Brassbolt, The Clockwork Marksman. Dwarf Ranger, adult character, height 1.32 m. Front, true side, back and three-quarter views at matching scale, neutral A-pose plus one action pose. A compact upright body with a wide horizontal crossbow and a high single-lens goggle shape above the forehead. A short jacket flares just enough to contrast with the weapon bar. Freckled medium-brown skin, dark eyes, cropped copper hair and a confident grin. Goggles sit above the eyes during normal play so expressions remain visible. Mustard work jacket over charcoal padding, leather forearm guards, sturdy trousers and broad boots. A few oversized straps suggest workshop practicality. A broad stylized crank crossbow with exaggerated fantasy housing and a circular side wheel. It is a game prop, not a functional construction plan; mechanisms remain decorative. Palette: Mustard #C5A04B; charcoal #404851; copper #B67B55; pale linen #D9CDAF. Flat neutral background, orthographic construction views, equipment inset, readable seams, non-graphic stylized fantasy. No copied franchise designs, text baked into textures, cinematic fog, invented extra limbs or altered gear between views. These are concept directions, not generated images.

## Approval gates

Silhouette passes at 96-pixel preview; costume agrees across all views; all seven clips reviewed; no required missing textures; no unexplained import scale compensation; effect matches declared reach and damage type; portrait agrees with the modeled hero; crowded-board test passes; source revision/reimport is demonstrated. A Python exit code alone does not approve the art.

Canonical source: `data/units.json`. Regenerate this dossier with `python tools/build_documents.py` after data edits. Do not hand-edit a stat table and leave the JSON unchanged.

---
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

---
# Rok Sunward — The Pass Champion

**Orc · Warrior · Melee damage · ALPHA**

Stable identity: `wc_u_orc_warrior`. Cost: **1 gold**. Rarity label: **Common**, separate from star level. Status: designed, not modeled or implemented by this kit. All combat values are provisional prototype inputs.

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

### Battle Tempo

**Player tooltip:** Temporarily increases his attack speed.

**Indonesian draft:** Meningkatkan kecepatan serang diri sendiri untuk sementara.

| Contract field | Value |
|---|---|
| Stable ability ID | `wc_a_orc_warrior` |
| Effect / target selector | `stat_modifier` / `self` |
| One / two / three star magnitude | 30% / 35% / 40% |
| Damage type | Not damaging |
| First-cast delay / cooldown | 2.5 s / 8.5 s |
| Windup / recovery | 0.25 s / 0.3 s |
| Effect duration | 3 s |
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

---
# Zura Stormcall — The Sky Listener

**Orc · Mage · Spell damage · ALPHA**

Stable identity: `wc_u_orc_mage`. Cost: **3 gold**. Rarity label: **Rare**, separate from star level. Status: designed, not modeled or implemented by this kit. All combat values are provisional prototype inputs.

## Character and world

Zura learned to read mountain winds so that Stormstep’s villages could prepare before storms arrived. She now studies disturbances around the distant breach, comparing notes with Rowan instead of accepting easy omens. In the trials she teaches captains to notice where enemies gather and to commit carefully when a spell cannot change direction once released.

Home region: `stormstep`. Affiliation: `highland_watch`. Neither supplies a hidden third synergy. Proper names are original proposed fiction, not trademark-clearance claims.

## Appearance and art direction

Authored standing height: **1.97 m**, excluding raised equipment. Rig family: `humanoid_broad`. One logical tile at every star. All characters are adults, fully clothed and presented as non-graphic heroic fantasy.

### Silhouette and proportions

A tall stable stance beneath two broad crescent shoulder cloths, with a forked staff held outward. Her costume forms layered triangles rather than a conventional pointed wizard hat.

### Face, hair and expression

Sage-green skin, silver-gray eyes, modest tusks and dark hair braided into three thick sections. A calm upward gaze suggests listening to the weather.

### Costume construction

Storm-blue layered coat, pale wool collar, russet belt and wrapped boots. Fabric panels end above the ankles and open around the knees for movement.

### Color palette

Storm blue #4A638D; cloud gray #CBD3DA; russet #A7664D; silver #A9B8C4.

### Equipment and magical focus

A tall wooden staff with an open fork framing a small floating sky stone. No hanging chains that require physical simulation.

### Three low-resolution identifiers

Open forked staff, cloud collar and three thick braids.

### Materials and surface detail

Wool, painted wood, oxidized silver and restrained cyan glow. Keep the sky stone’s bloom local.

### Back and side-view constraints

Two long triangular coat panels split around the legs, with a broad stitched cloud arc high on the back.

## Combat statistics — without traits or temporary effects

| Property | One star | Two stars | Three stars |
|---|---:|---:|---:|
| Health | 750 | 1,350 | 2,430 |
| Basic attack damage | 50 | 90 | 162 |
| Attack delivery | ranged | ranged | ranged |
| Basic damage type | magic | magic | magic |
| Nominal attacks/second | 0.75 | 0.75 | 0.75 |
| Effective attacks/second at 20 Hz | 0.7407 | 0.7407 | 0.7407 |
| Range in tiles | 3 | 3 | 3 |
| Physical armor | 12 | 12 | 12 |
| Magic resistance | 25 | 25 | 25 |
| Movement tiles/second | 1.00 | 1.00 | 1.00 |

Nominal basic-attack DPS at one star: **37.50**, before mitigation, movement, stuns, skills, targeting downtime or timing quantization. Basic windup: 300 ms; ordinary projectile travel: 150 ms. No hidden critical hits, evasion, lifesteal or mana.

## One active skill

### Storm Ring

**Player tooltip:** Strikes enemies around a captured enemy location with magic.

**Indonesian draft:** Memberikan kerusakan sihir kepada musuh di area sasaran.

| Contract field | Value |
|---|---|
| Stable ability ID | `wc_a_orc_mage` |
| Effect / target selector | `damage` / `current_enemy_area` |
| One / two / three star magnitude | 190 / 342 / 616 |
| Damage type | magic |
| First-cast delay / cooldown | 4 s / 10 s |
| Windup / recovery | 0.6 s / 0.3 s |
| Effect duration | 0 s |
| Skill reach / area radius | 4 / 2 tiles |
| Can include self | False |
| Max dash distance | 0 tiles |
| Projectile travel | 300 ms |
| Affected stat | Not applicable |

Cooldown starts at successful cast commitment. An interrupted committed cast keeps its cooldown; an unavailable target leaves the ability ready and allows ordinary behavior. Area centers and area recipients are captured at release. Targeted projectiles keep their target ID but never retarget a defeated unit. Dash landing is reserved at commitment and validated before movement. See the rules contract for same-tick ordering, shield replacement and refresh semantics.

Health and basic damage use 1.00/1.80/3.24 star multipliers. Only explicitly authored skill magnitudes vary with stars; stun duration, range, radius, dash distance, cooldown and model footprint do not grow. A status-only skill may deliberately have identical behavior across stars; its owner still gains health and basic damage.

## Positioning and counterplay

**Preferred formation.** Protected backline with a frontline lasting long enough for the first cast.

**Useful partners.** Rowan completes Mage; Rok activates Orc; Borin can briefly keep targets close.

**Counterplay.** Spread out or force movement after the capture; Rogues can interrupt the long windup.

**Practical weakness.** High cost, slow active cadence and no control effect despite the storm imagery.

**Difference from the nearest alternative.** Rowan casts sooner with a smaller area; Zura risks a longer commitment for broader coverage.

**Character-specific acceptance test.** The storm captures center at release, not at impact; verify every affected unit receives exactly one magic packet.

## Animation, effects and sound

Idle makes a small palm-up listening gesture. Basics release small storm motes. The active raises the staff slowly, draws a visible circular path, then plants it as the captured area resolves.

**Skill effect:** A thin blue circle previews the captured radius during travel, followed by several short vertical magic streaks. The ability is one damage pulse, not damage over time or stun.

**Sound:** Low rising wind followed by a short soft thunder chord, capped to avoid overwhelming every other cue.

Author at 60 FPS, as in-place animations with no locomotion-driven root translation. Required clips: Idle, Move, Attack, Active, Hit, Defeat, Victory. The active release marker is frame 36 relative to animation start. Basic release marker is frame 18. These are presentation alignment points, not sources of authoritative damage. Idle begins as a 2-second loop; movement as a 1-second cycle; hit as 0.4 seconds; defeat as 1 second; victory as 1.5 seconds. Adjust clip lengths during animation review without altering gameplay timing.

A defeat uses a brief stagger, kneel or magical dissolve with no injury detail. Stars use UI pips, a subtle trim accent and a brief upgrade flourish; do not produce three separate bodies or enlarge the collision footprint.

## Blender construction and Unreal handoff

Start from the `humanoid_broad` base or a validated compatible family. Block silhouette before bevels; separate body, costume and equipment into named source collections. Build equipment as decorative fantasy game props, not real functional objects. Author model-space Z up and a consistent forward orientation, then prove conversion with the calibration fixture. Materials use one or two runtime slots and a shared atlas where it preserves identity.

Targets to profile: at most 15,000 LOD0 triangles, 1024-pixel default maps, up to 60 deforming bones and 4 influences per vertex. Lower-detail targets begin near 50% and 25% triangles. These are budgets, not measured performance.

Sockets: `weapon_r`, `weapon_l`, `cast_origin`, `head_ui`. Inspect shoulder, elbow, hip and knee extremes. Use separate rig proportions where needed; matching bone names is not proof of animation compatibility. Selection uses a stable unit proxy, not detailed prop collision. Team affiliation uses base rings/icons in addition to color, never a complete costume recolor.

**Specific production risk:** Radius two covers a large portion of a crowded board. Effects must show the true edge and performance tests must include multiple simultaneous rings.

Required source/export locations:

- blender: `art-source/heroes/wc_u_orc_mage/wc_u_orc_mage.blend`

- mesh_fbx: `exports/heroes/wc_u_orc_mage/SK_wc_u_orc_mage.fbx`

- unreal_folder: `/Game/WonderChess/Heroes/wc_u_orc_mage`

- portrait: `exports/heroes/wc_u_orc_mage/portrait.png`

Create separate animation exports and texture maps, a model-derived portrait, front/side/back/three-quarter views, a gameplay-camera screenshot, and an actual Unreal animation capture. Log source/export hashes, skeleton revision, tool versions and import preset. Deliberately change one costume detail, re-export and verify existing material, skeleton, animation and actor references survive.

## Model-sheet generation brief

Original Wonder Chess high-fantasy character production sheet for Zura Stormcall, The Sky Listener. Orc Mage, adult character, height 1.97 m. Front, true side, back and three-quarter views at matching scale, neutral A-pose plus one action pose. A tall stable stance beneath two broad crescent shoulder cloths, with a forked staff held outward. Her costume forms layered triangles rather than a conventional pointed wizard hat. Sage-green skin, silver-gray eyes, modest tusks and dark hair braided into three thick sections. A calm upward gaze suggests listening to the weather. Storm-blue layered coat, pale wool collar, russet belt and wrapped boots. Fabric panels end above the ankles and open around the knees for movement. A tall wooden staff with an open fork framing a small floating sky stone. No hanging chains that require physical simulation. Palette: Storm blue #4A638D; cloud gray #CBD3DA; russet #A7664D; silver #A9B8C4. Flat neutral background, orthographic construction views, equipment inset, readable seams, non-graphic stylized fantasy. No copied franchise designs, text baked into textures, cinematic fog, invented extra limbs or altered gear between views. These are concept directions, not generated images.

## Approval gates

Silhouette passes at 96-pixel preview; costume agrees across all views; all seven clips reviewed; no required missing textures; no unexplained import scale compensation; effect matches declared reach and damage type; portrait agrees with the modeled hero; crowded-board test passes; source revision/reimport is demonstrated. A Python exit code alone does not approve the art.

Canonical source: `data/units.json`. Regenerate this dossier with `python tools/build_documents.py` after data edits. Do not hand-edit a stat table and leave the JSON unchanged.

---
# Kesh Quickwind — The Ridge Courier

**Orc · Rogue · Disruption · ALPHA**

Stable identity: `wc_u_orc_rogue`. Cost: **2 gold**. Rarity label: **Uncommon**, separate from star level. Status: designed, not modeled or implemented by this kit. All combat values are provisional prototype inputs.

## Character and world

Kesh carries maps and letters between Stormstep’s scattered homes, measuring a route by who it connects rather than how impressive it looks. He joined the trials after Sylas challenged him to a friendly delivery race. Their rivalry is cheerful, but Kesh wants captains to understand that reaching the right place is only useful when the team is ready to follow.

Home region: `stormstep`. Affiliation: `highland_watch`. Neither supplies a hidden third synergy. Proper names are original proposed fiction, not trademark-clearance claims.

## Appearance and art direction

Authored standing height: **1.93 m**, excluding raised equipment. Rig family: `humanoid_broad`. One logical tile at every star. All characters are adults, fully clothed and presented as non-graphic heroic fantasy.

### Silhouette and proportions

A narrow athletic wedge with a high scarf loop, short rounded shoulder guards and two compact hooked fantasy blades. The overall shape is tall and light rather than Rok’s broad mantle.

### Face, hair and expression

Muted jade skin, brown eyes, small tusks and cropped dark hair with a pale cloth tie. An easy grin distinguishes him from a stereotypically menacing Rogue.

### Costume construction

Turquoise courier jacket over charcoal cloth, a tan diagonal sash and light wrapped boots. Large route-marker patches replace armor clutter.

### Color palette

Turquoise #408E91; tan #C1A477; charcoal #3D4C4E; muted jade #708D72.

### Equipment and magical focus

Two short rounded fantasy blades and a flat map case on the hip. Keep the implements stylized and visually simpler than Sylas’s curves.

### Three low-resolution identifiers

High scarf loop, turquoise diagonal jacket and open forward-running posture.

### Materials and surface detail

Waxed cloth, soft leather and minimal brushed metal. No transparent cape or spark trail during normal walking.

### Back and side-view constraints

A route-map case sits close to the lower back, with a broad sash crossing above it. The scarf loop uses a few stiff bones rather than simulated cloth.

## Combat statistics — without traits or temporary effects

| Property | One star | Two stars | Three stars |
|---|---:|---:|---:|
| Health | 820 | 1,476 | 2,656.8 |
| Basic attack damage | 67 | 120.6 | 217.08 |
| Attack delivery | melee | melee | melee |
| Basic damage type | physical | physical | physical |
| Nominal attacks/second | 1.00 | 1.00 | 1.00 |
| Effective attacks/second at 20 Hz | 1.0000 | 1.0000 | 1.0000 |
| Range in tiles | 1 | 1 | 1 |
| Physical armor | 15 | 15 | 15 |
| Magic resistance | 10 | 10 | 10 |
| Movement tiles/second | 1.25 | 1.25 | 1.25 |

Nominal basic-attack DPS at one star: **67.00**, before mitigation, movement, stuns, skills, targeting downtime or timing quantization. Basic windup: 250 ms; ordinary projectile travel: 0 ms. No hidden critical hits, evasion, lifesteal or mana.

## One active skill

### Closing Dash

**Player tooltip:** Dashes beside the current target within three tiles.

**Indonesian draft:** Melakukan dash ke petak kosong di samping sasaran saat ini.

| Contract field | Value |
|---|---|
| Stable ability ID | `wc_a_orc_rogue` |
| Effect / target selector | `dash` / `current_enemy_adjacent` |
| One / two / three star magnitude | Not applicable / Not applicable / Not applicable |
| Damage type | Not damaging |
| First-cast delay / cooldown | 1.5 s / 6.5 s |
| Windup / recovery | 0.2 s / 0.15 s |
| Effect duration | 0 s |
| Skill reach / area radius | 4 / 0 tiles |
| Can include self | False |
| Max dash distance | 3 tiles |
| Projectile travel | 0 ms |
| Affected stat | Not applicable |

Cooldown starts at successful cast commitment. An interrupted committed cast keeps its cooldown; an unavailable target leaves the ability ready and allows ordinary behavior. Area centers and area recipients are captured at release. Targeted projectiles keep their target ID but never retarget a defeated unit. Dash landing is reserved at commitment and validated before movement. See the rules contract for same-tick ordering, shield replacement and refresh semantics.

Health and basic damage use 1.00/1.80/3.24 star multipliers. Only explicitly authored skill magnitudes vary with stars; stun duration, range, radius, dash distance, cooldown and model footprint do not grow. A status-only skill may deliberately have identical behavior across stars; its owner still gains health and basic damage.

## Positioning and counterplay

**Preferred formation.** A flank near the front, with a path toward a vulnerable current target rather than an isolated leap across the entire board.

**Useful partners.** Sylas completes Rogue; Rok makes an effective nearby damage partner.

**Counterplay.** Protect the current target with occupied neighboring cells or a durable control unit.

**Practical weakness.** Short dash and modest defenses; cannot automatically select the farthest support like Sylas.

**Difference from the nearest alternative.** Kesh chases the existing target; Sylas selects the farthest enemy and has a longer cooldown.

**Character-specific acceptance test.** Never consume cooldown when already adjacent with no improving destination; landing reservation must release on interrupt.

## Animation, effects and sound

Idle is ready to run, not constantly bouncing. Basics use economical alternating motions. The active lowers the lead shoulder and makes one fast grounded glide to the reserved cell.

**Skill effect:** A short pale-cyan streak hugs the ground; mark the landing rather than hiding the unit. No implicit extra strike or slow.

**Sound:** A quick brushed-wind accent and light foot landing. Separate the cue from Sylas’s longer dash with a shorter pitch envelope.

Author at 60 FPS, as in-place animations with no locomotion-driven root translation. Required clips: Idle, Move, Attack, Active, Hit, Defeat, Victory. The active release marker is frame 12 relative to animation start. Basic release marker is frame 15. These are presentation alignment points, not sources of authoritative damage. Idle begins as a 2-second loop; movement as a 1-second cycle; hit as 0.4 seconds; defeat as 1 second; victory as 1.5 seconds. Adjust clip lengths during animation review without altering gameplay timing.

A defeat uses a brief stagger, kneel or magical dissolve with no injury detail. Stars use UI pips, a subtle trim accent and a brief upgrade flourish; do not produce three separate bodies or enlarge the collision footprint.

## Blender construction and Unreal handoff

Start from the `humanoid_broad` base or a validated compatible family. Block silhouette before bevels; separate body, costume and equipment into named source collections. Build equipment as decorative fantasy game props, not real functional objects. Author model-space Z up and a consistent forward orientation, then prove conversion with the calibration fixture. Materials use one or two runtime slots and a shared atlas where it preserves identity.

Targets to profile: at most 15,000 LOD0 triangles, 1024-pixel default maps, up to 60 deforming bones and 4 influences per vertex. Lower-detail targets begin near 50% and 25% triangles. These are budgets, not measured performance.

Sockets: `weapon_r`, `weapon_l`, `cast_origin`, `head_ui`. Inspect shoulder, elbow, hip and knee extremes. Use separate rig proportions where needed; matching bone names is not proof of animation compatibility. Selection uses a stable unit proxy, not detailed prop collision. Team affiliation uses base rings/icons in addition to color, never a complete costume recolor.

**Specific production risk:** The landing must reduce distance to the current target; otherwise a ready skill could loop without tactical purpose. Test same-tick target movement and blocked cells.

Required source/export locations:

- blender: `art-source/heroes/wc_u_orc_rogue/wc_u_orc_rogue.blend`

- mesh_fbx: `exports/heroes/wc_u_orc_rogue/SK_wc_u_orc_rogue.fbx`

- unreal_folder: `/Game/WonderChess/Heroes/wc_u_orc_rogue`

- portrait: `exports/heroes/wc_u_orc_rogue/portrait.png`

Create separate animation exports and texture maps, a model-derived portrait, front/side/back/three-quarter views, a gameplay-camera screenshot, and an actual Unreal animation capture. Log source/export hashes, skeleton revision, tool versions and import preset. Deliberately change one costume detail, re-export and verify existing material, skeleton, animation and actor references survive.

## Model-sheet generation brief

Original Wonder Chess high-fantasy character production sheet for Kesh Quickwind, The Ridge Courier. Orc Rogue, adult character, height 1.93 m. Front, true side, back and three-quarter views at matching scale, neutral A-pose plus one action pose. A narrow athletic wedge with a high scarf loop, short rounded shoulder guards and two compact hooked fantasy blades. The overall shape is tall and light rather than Rok’s broad mantle. Muted jade skin, brown eyes, small tusks and cropped dark hair with a pale cloth tie. An easy grin distinguishes him from a stereotypically menacing Rogue. Turquoise courier jacket over charcoal cloth, a tan diagonal sash and light wrapped boots. Large route-marker patches replace armor clutter. Two short rounded fantasy blades and a flat map case on the hip. Keep the implements stylized and visually simpler than Sylas’s curves. Palette: Turquoise #408E91; tan #C1A477; charcoal #3D4C4E; muted jade #708D72. Flat neutral background, orthographic construction views, equipment inset, readable seams, non-graphic stylized fantasy. No copied franchise designs, text baked into textures, cinematic fog, invented extra limbs or altered gear between views. These are concept directions, not generated images.

## Approval gates

Silhouette passes at 96-pixel preview; costume agrees across all views; all seven clips reviewed; no required missing textures; no unexplained import scale compensation; effect matches declared reach and damage type; portrait agrees with the modeled hero; crowded-board test passes; source revision/reimport is demonstrated. A Python exit code alone does not approve the art.

Canonical source: `data/units.json`. Regenerate this dossier with `python tools/build_documents.py` after data edits. Do not hand-edit a stat table and leave the JSON unchanged.

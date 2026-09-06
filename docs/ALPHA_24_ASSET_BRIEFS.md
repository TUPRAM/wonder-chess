# Wonder Chess — Twenty-four Alpha Hero Asset Briefs

Use the per-hero art, animation and numerical contracts below alongside BLENDER_PRODUCTION.md. No model or render is included in this document.

# Ada Brightshield — The Gatekeeper

**Human · Guardian · Defender · ALPHA**

Stable identity: `wc_u_human_guardian`. Cost: **1 gold**. Rarity label: **Common**, separate from star level. Production and verification status is recorded separately in reports/implementation_state.json; this generated dossier does not certify an asset or build. All combat values are provisional prototype inputs.

Quick display name: **Ada**. Informational roles: Tank. Role tags provide no additional synergy.

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

### Sun Guard

**Player tooltip:** Gains a shield for three seconds.

**Indonesian draft:** Memberikan perisai sementara kepada diri sendiri.

| Contract field | Value |
|---|---|
| Stable ability ID | `wc_a_human_guardian` |
| Effect / target selector | `shield` / `self` |
| One / two / three star magnitude | shield: 200 / 360 / 648 |
| Damage type | Not damaging |
| First-cast delay / cooldown | 2 s / 8 s |
| Windup / recovery | 0.3 s / 0.3 s |
| Effect duration | 3.0 s |
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

---
# Rowan Emberwick — The Hearth Scholar

**Human · Mage · Spell damage · ALPHA**

Stable identity: `wc_u_human_mage`. Cost: **2 gold**. Rarity label: **Uncommon**, separate from star level. Production and verification status is recorded separately in reports/implementation_state.json; this generated dossier does not certify an asset or build. All combat values are provisional prototype inputs.

Quick display name: **Rowan**. Informational roles: Caster. Role tags provide no additional synergy.

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

### Ember Burst

**Player tooltip:** Damages enemies around the target’s captured location.

**Indonesian draft:** Memberikan kerusakan sihir kepada musuh di area sasaran.

| Contract field | Value |
|---|---|
| Stable ability ID | `wc_a_human_mage` |
| Effect / target selector | `damage` / `current_enemy_area` |
| One / two / three star magnitude | damage: 150 / 270 / 486 |
| Damage type | magic |
| First-cast delay / cooldown | 3.5 s / 8 s |
| Windup / recovery | 0.45 s / 0.3 s |
| Effect duration | 0.0 s |
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

Stable identity: `wc_u_elf_ranger`. Cost: **1 gold**. Rarity label: **Common**, separate from star level. Production and verification status is recorded separately in reports/implementation_state.json; this generated dossier does not certify an asset or build. All combat values are provisional prototype inputs.

Quick display name: **Liora**. Informational roles: Ranged. Role tags provide no additional synergy.

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
| One / two / three star magnitude | dash: Not applicable / Not applicable / Not applicable |
| Damage type | Not damaging |
| First-cast delay / cooldown | 2 s / 7.5 s |
| Windup / recovery | 0.2 s / 0.15 s |
| Effect duration | 0.0 s |
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

Stable identity: `wc_u_elf_priest`. Cost: **2 gold**. Rarity label: **Uncommon**, separate from star level. Production and verification status is recorded separately in reports/implementation_state.json; this generated dossier does not certify an asset or build. All combat values are provisional prototype inputs.

Quick display name: **Elin**. Informational roles: Support. Role tags provide no additional synergy.

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

### Quick Song

**Player tooltip:** Temporarily increases nearby allies’ attack speed.

**Indonesian draft:** Meningkatkan kecepatan serang diri sendiri dan sekutu bersebelahan untuk sementara.

| Contract field | Value |
|---|---|
| Stable ability ID | `wc_a_elf_priest` |
| Effect / target selector | `stat_modifier` / `adjacent_allies` |
| One / two / three star magnitude | stat_modifier: 20% / 25% / 30% |
| Damage type | Not damaging |
| First-cast delay / cooldown | 2.5 s / 9 s |
| Windup / recovery | 0.35 s / 0.3 s |
| Effect duration | 3.0 s |
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

Stable identity: `wc_u_elf_rogue`. Cost: **3 gold**. Rarity label: **Rare**, separate from star level. Production and verification status is recorded separately in reports/implementation_state.json; this generated dossier does not certify an asset or build. All combat values are provisional prototype inputs.

Quick display name: **Sylas**. Informational roles: Control. Role tags provide no additional synergy.

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

### Backline Leap

**Player tooltip:** Dashes beside the farthest enemy when a landing tile is free.

**Indonesian draft:** Melakukan dash ke petak kosong di samping musuh terjauh.

| Contract field | Value |
|---|---|
| Stable ability ID | `wc_a_elf_rogue` |
| Effect / target selector | `dash` / `farthest_enemy_adjacent` |
| One / two / three star magnitude | dash: Not applicable / Not applicable / Not applicable |
| Damage type | Not damaging |
| First-cast delay / cooldown | 1 s / 8.5 s |
| Windup / recovery | 0.2 s / 0.15 s |
| Effect duration | 0.0 s |
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

Stable identity: `wc_u_dwarf_guardian`. Cost: **1 gold**. Rarity label: **Common**, separate from star level. Production and verification status is recorded separately in reports/implementation_state.json; this generated dossier does not certify an asset or build. All combat values are provisional prototype inputs.

Quick display name: **Borin**. Informational roles: Tank. Role tags provide no additional synergy.

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
| One / two / three star magnitude | stun: Not applicable / Not applicable / Not applicable |
| Damage type | Not damaging |
| First-cast delay / cooldown | 3 s / 8.5 s |
| Windup / recovery | 0.4 s / 0.3 s |
| Effect duration | 1.0 s |
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

Stable identity: `wc_u_dwarf_ranger`. Cost: **2 gold**. Rarity label: **Uncommon**, separate from star level. Production and verification status is recorded separately in reports/implementation_state.json; this generated dossier does not certify an asset or build. All combat values are provisional prototype inputs.

Quick display name: **Tessa**. Informational roles: Ranged. Role tags provide no additional synergy.

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
| One / two / three star magnitude | damage: 170 / 306 / 551 |
| Damage type | physical |
| First-cast delay / cooldown | 2.5 s / 6.5 s |
| Windup / recovery | 0.35 s / 0.3 s |
| Effect duration | 0.0 s |
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

Stable identity: `wc_u_dwarf_warrior`. Cost: **2 gold**. Rarity label: **Uncommon**, separate from star level. Production and verification status is recorded separately in reports/implementation_state.json; this generated dossier does not certify an asset or build. All combat values are provisional prototype inputs.

Quick display name: **Dagna**. Informational roles: Melee. Role tags provide no additional synergy.

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

### Hammer Sweep

**Player tooltip:** Damages all adjacent enemies.

**Indonesian draft:** Memberikan kerusakan fisik kepada musuh di area sasaran.

| Contract field | Value |
|---|---|
| Stable ability ID | `wc_a_dwarf_warrior` |
| Effect / target selector | `damage` / `adjacent_enemies` |
| One / two / three star magnitude | damage: 140 / 252 / 454 |
| Damage type | physical |
| First-cast delay / cooldown | 3.5 s / 8 s |
| Windup / recovery | 0.4 s / 0.3 s |
| Effect duration | 0.0 s |
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

---
# Zura Stormcall — The Sky Listener

**Orc · Mage · Spell damage · ALPHA**

Stable identity: `wc_u_orc_mage`. Cost: **3 gold**. Rarity label: **Rare**, separate from star level. Production and verification status is recorded separately in reports/implementation_state.json; this generated dossier does not certify an asset or build. All combat values are provisional prototype inputs.

Quick display name: **Zura**. Informational roles: Caster. Role tags provide no additional synergy.

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
| One / two / three star magnitude | damage: 190 / 342 / 616 |
| Damage type | magic |
| First-cast delay / cooldown | 4 s / 10 s |
| Windup / recovery | 0.6 s / 0.3 s |
| Effect duration | 0.0 s |
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

Stable identity: `wc_u_orc_rogue`. Cost: **2 gold**. Rarity label: **Uncommon**, separate from star level. Production and verification status is recorded separately in reports/implementation_state.json; this generated dossier does not certify an asset or build. All combat values are provisional prototype inputs.

Quick display name: **Kesh**. Informational roles: Control. Role tags provide no additional synergy.

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

### Quickstep

**Player tooltip:** Dashes beside the current target within three tiles.

**Indonesian draft:** Melakukan dash ke petak kosong di samping sasaran saat ini.

| Contract field | Value |
|---|---|
| Stable ability ID | `wc_a_orc_rogue` |
| Effect / target selector | `dash` / `current_enemy_adjacent` |
| One / two / three star magnitude | dash: Not applicable / Not applicable / Not applicable |
| Damage type | Not damaging |
| First-cast delay / cooldown | 1.5 s / 6.5 s |
| Windup / recovery | 0.2 s / 0.15 s |
| Effect duration | 0.0 s |
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

---
# Cass Vale — The Banner Captain

**Human · Warrior · Melee damage · ALPHA**

Stable identity: `wc_u_human_warrior`. Cost: **2 gold**. Rarity label: **Uncommon**, separate from star level. Production and verification status is recorded separately in reports/implementation_state.json; this generated dossier does not certify an asset or build. All combat values are provisional prototype inputs.

Quick display name: **Cass**. Informational roles: Melee. Role tags provide no additional synergy.

## Character and world

Cass trains Brighthaven’s volunteer patrols and remembers every recruit’s name. Ada taught him that a captain who rushes ahead can leave a stronger team behind. He enters the trials to practice decisive attacks within a formation, carrying a banner sewn by the same market families whose roads his patrols protect.

Home region: `brighthaven`. Affiliation: `dawn_compact`. Neither supplies a hidden third synergy. Proper names are original proposed fiction, not trademark-clearance claims.

## Appearance and art direction

Authored standing height: **1.86 m**, excluding raised equipment. Rig family: `humanoid_standard`. One logical tile at every star. All characters are adults, fully clothed and presented as non-graphic heroic fantasy.

### Silhouette and proportions

A tall upright figure with one squared shoulder plate and a long, broad fantasy blade held diagonally downward. A short rectangular back-banner creates a distinctive vertical behind the head.

### Face, hair and expression

Medium-brown skin, close-cropped dark hair, brown eyes and a composed, focused expression. A pale eyebrow streak is a natural hair accent rather than an injury story.

### Costume construction

Deep red fitted coat under partial silver plate, broad belt, cream trousers and knee boots. The asymmetric armor leaves a clear leading and trailing side.

### Color palette

Crimson #A4464D; cream #E3D7BA; silver #A6B5BF; midnight #344155.

### Equipment and magical focus

Broad two-handed fantasy blade and a short banner fixed to a rigid back bracket. The banner is cosmetic; no area buff or faction system is implied.

### Three low-resolution identifiers

Single large shoulder plate, upright back-banner and long diagonal blade.

### Materials and surface detail

Matte cloth and brushed steel with sparse clean edge highlights. Bake banner folds or use two accessory bones; no cloth solver.

### Back and side-view constraints

A rigid banner bracket attaches visibly to the harness, leaving shoulder motion clear. The cloth stops above the hips.

## Combat statistics — without traits or temporary effects

| Property | One star | Two stars | Three stars |
|---|---:|---:|---:|
| Health | 980 | 1,764 | 3,175.2 |
| Basic attack damage | 72 | 129.6 | 233.28 |
| Attack delivery | melee | melee | melee |
| Basic damage type | physical | physical | physical |
| Nominal attacks/second | 0.80 | 0.80 | 0.80 |
| Effective attacks/second at 20 Hz | 0.8000 | 0.8000 | 0.8000 |
| Range in tiles | 1 | 1 | 1 |
| Physical armor | 25 | 25 | 25 |
| Magic resistance | 15 | 15 | 15 |
| Movement tiles/second | 1.05 | 1.05 | 1.05 |

Nominal basic-attack DPS at one star: **57.60**, before mitigation, movement, stuns, skills, targeting downtime or timing quantization. Basic windup: 350 ms; ordinary projectile travel: 0 ms. No hidden critical hits, evasion, lifesteal or mana.

## One active skill

### Firm Strike

**Player tooltip:** Delivers a stronger physical hit to the current target.

**Indonesian draft:** Memberikan kerusakan fisik kepada sasaran saat ini.

| Contract field | Value |
|---|---|
| Stable ability ID | `wc_a_human_warrior` |
| Effect / target selector | `damage` / `current_enemy` |
| One / two / three star magnitude | damage: 180 / 324 / 583 |
| Damage type | physical |
| First-cast delay / cooldown | 3 s / 7.5 s |
| Windup / recovery | 0.35 s / 0.3 s |
| Effect duration | 0.0 s |
| Skill reach / area radius | 1 / 0 tiles |
| Can include self | False |
| Max dash distance | 0 tiles |
| Projectile travel | 0 ms |
| Affected stat | Not applicable |

Cooldown starts at successful cast commitment. An interrupted committed cast keeps its cooldown; an unavailable target leaves the ability ready and allows ordinary behavior. Area centers and area recipients are captured at release. Targeted projectiles keep their target ID but never retarget a defeated unit. Dash landing is reserved at commitment and validated before movement. See the rules contract for same-tick ordering, shield replacement and refresh semantics.

Health and basic damage use 1.00/1.80/3.24 star multipliers. Only explicitly authored skill magnitudes vary with stars; stun duration, range, radius, dash distance, cooldown and model footprint do not grow. A status-only skill may deliberately have identical behavior across stars; its owner still gains health and basic damage.

## Positioning and counterplay

**Preferred formation.** Frontline second contact, beside a Guardian rather than alone at the center.

**Useful partners.** Rok or Dagna enables Warrior while Ada can provide the Human bonus.

**Counterplay.** High armor and shields reduce the single large physical hit; stuns can cancel its windup.

**Practical weakness.** No area effect or self-protection; he needs access to a useful current target.

**Difference from the nearest alternative.** Dagna spreads damage; Cass concentrates it on one enemy.

**Character-specific acceptance test.** Ensure the active is an ability packet, not a basic attack repeated with all basic-only bonuses.

## Animation, effects and sound

Idle keeps the blade low and feet apart. Basics are short two-handed cuts. The active pulls the blade inward and delivers one measured forward strike; the banner follows slightly after the torso.

**Skill effect:** A single narrow warm-white trail and compact impact spark. No splash damage, armor break or knockback.

**Sound:** One firm cloth movement and a clean resonant hit; no shouted voice requirement.

Author at 60 FPS, as in-place animations with no locomotion-driven root translation. Required clips: Idle, Move, Attack, Active, Hit, Defeat, Victory. The active release marker is frame 21 relative to animation start. Basic release marker is frame 21. These are presentation alignment points, not sources of authoritative damage. Idle begins as a 2-second loop; movement as a 1-second cycle; hit as 0.4 seconds; defeat as 1 second; victory as 1.5 seconds. Adjust clip lengths during animation review without altering gameplay timing.

A defeat uses a brief stagger, kneel or magical dissolve with no injury detail. Stars use UI pips, a subtle trim accent and a brief upgrade flourish; do not produce three separate bodies or enlarge the collision footprint.

## Blender construction and Unreal handoff

Start from the `humanoid_standard` base or a validated compatible family. Block silhouette before bevels; separate body, costume and equipment into named source collections. Build equipment as decorative fantasy game props, not real functional objects. Author model-space Z up and a consistent forward orientation, then prove conversion with the calibration fixture. Materials use one or two runtime slots and a shared atlas where it preserves identity.

Targets to profile: at most 15,000 LOD0 triangles, 1024-pixel default maps, up to 60 deforming bones and 4 influences per vertex. Lower-detail targets begin near 50% and 25% triangles. These are budgets, not measured performance.

Sockets: `weapon_r`, `weapon_l`, `cast_origin`, `head_ui`. Inspect shoulder, elbow, hip and knee extremes. Use separate rig proportions where needed; matching bone names is not proof of animation compatibility. Selection uses a stable unit proxy, not detailed prop collision. Team affiliation uses base rings/icons in addition to color, never a complete costume recolor.

**Specific production risk:** Banner silhouette must not overlap health bars or obscure the next row. Validate that a two-handed pose works with the shared standard rig.

Required source/export locations:

- blender: `art-source/heroes/wc_u_human_warrior/wc_u_human_warrior.blend`

- mesh_fbx: `exports/heroes/wc_u_human_warrior/SK_wc_u_human_warrior.fbx`

- unreal_folder: `/Game/WonderChess/Heroes/wc_u_human_warrior`

- portrait: `exports/heroes/wc_u_human_warrior/portrait.png`

Create separate animation exports and texture maps, a model-derived portrait, front/side/back/three-quarter views, a gameplay-camera screenshot, and an actual Unreal animation capture. Log source/export hashes, skeleton revision, tool versions and import preset. Deliberately change one costume detail, re-export and verify existing material, skeleton, animation and actor references survive.

## Model-sheet generation brief

Original Wonder Chess high-fantasy character production sheet for Cass Vale, The Banner Captain. Human Warrior, adult character, height 1.86 m. Front, true side, back and three-quarter views at matching scale, neutral A-pose plus one action pose. A tall upright figure with one squared shoulder plate and a long, broad fantasy blade held diagonally downward. A short rectangular back-banner creates a distinctive vertical behind the head. Medium-brown skin, close-cropped dark hair, brown eyes and a composed, focused expression. A pale eyebrow streak is a natural hair accent rather than an injury story. Deep red fitted coat under partial silver plate, broad belt, cream trousers and knee boots. The asymmetric armor leaves a clear leading and trailing side. Broad two-handed fantasy blade and a short banner fixed to a rigid back bracket. The banner is cosmetic; no area buff or faction system is implied. Palette: Crimson #A4464D; cream #E3D7BA; silver #A6B5BF; midnight #344155. Flat neutral background, orthographic construction views, equipment inset, readable seams, non-graphic stylized fantasy. No copied franchise designs, text baked into textures, cinematic fog, invented extra limbs or altered gear between views. These are concept directions, not generated images.

## Approval gates

Silhouette passes at 96-pixel preview; costume agrees across all views; all seven clips reviewed; no required missing textures; no unexplained import scale compensation; effect matches declared reach and damage type; portrait agrees with the modeled hero; crowded-board test passes; source revision/reimport is demonstrated. A Python exit code alone does not approve the art.

Canonical source: `data/units.json`. Regenerate this dossier with `python tools/build_documents.py` after data edits. Do not hand-edit a stat table and leave the JSON unchanged.

---
# Neris Starbloom — The Observatory Keeper

**Elf · Mage · Spell damage · ALPHA**

Stable identity: `wc_u_elf_mage`. Cost: **3 gold**. Rarity label: **Rare**, separate from star level. Production and verification status is recorded separately in reports/implementation_state.json; this generated dossier does not certify an asset or build. All combat values are provisional prototype inputs.

Quick display name: **Neris**. Informational roles: Control. Role tags provide no additional synergy.

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

**Player tooltip:** Deal 60 / 108 / 194.4 magic damage to the current enemy, then stun it for 1.25 seconds if it survives. Mage bonuses affect damage only.

**Indonesian draft:** Berikan 60 / 108 / 194,4 kerusakan sihir kepada musuh saat ini, lalu buatnya tertegun selama 1,25 detik jika bertahan. Bonus Mage hanya meningkatkan kerusakan.

| Contract field | Value |
|---|---|
| Stable ability ID | `wc_a_elf_mage` |
| Effect / target selector | `damage then stun` / `current_enemy` |
| One / two / three star magnitude | damage: 60 / 108 / 194.4; stun: Not applicable / Not applicable / Not applicable |
| Damage type | magic; Not damaging |
| First-cast delay / cooldown | 3.5 s / 9.5 s |
| Windup / recovery | 0.4 s / 0.3 s |
| Effect duration | 0.0 s; 1.25 s |
| Skill reach / area radius | 4 / 0 tiles |
| Can include self | False |
| Max dash distance | 0 tiles |
| Projectile travel | 200 ms |
| Affected stat | Not applicable; Not applicable |

Cooldown starts at successful cast commitment. An interrupted committed cast keeps its cooldown; an unavailable target leaves the ability ready and allows ordinary behavior. Area centers and area recipients are captured at release. Targeted projectiles keep their target ID but never retarget a defeated unit. Dash landing is reserved at commitment and validated before movement. See the rules contract for same-tick ordering, shield replacement and refresh semantics.

Health and basic damage use 1.00/1.80/3.24 star multipliers. Only explicitly authored skill magnitudes vary with stars; stun duration, range, radius, dash distance, cooldown and model footprint do not grow. A status-only skill may deliberately have identical behavior across stars; its owner still gains health and basic damage.

## Positioning and counterplay

**Preferred formation.** Protected backline with range to interrupt a dangerous current target.

**Useful partners.** Rowan or Zura completes a Mage pair that amplifies each hero's damage-bearing skill effect. Neris's magic impact gains that bonus once; its stun duration does not. Liora supplies Elf.

**Counterplay.** Several moderate threats reduce the value of locking one target; a flanker can force a poor current target.

**Practical weakness.** Her single-target magic impact is modest and has a long cooldown. A target defeated by the impact receives no stun; Mage damage bonuses never extend the control duration.

**Difference from the nearest alternative.** Borin controls a nearby group; Neris interrupts one distant opponent for slightly longer.

**Character-specific acceptance test.** Projectile may expire on a defeated target; its 1250 ms control remains constant at all star levels.

## Animation, effects and sound

Idle follows the lens with a small eye-line shift. Basics flick a pale spark. Starbind raises the lens to eye level, aligns both palms and releases one small star toward the target.

**Skill effect:** A pale violet projectile makes one compact magic impact, followed by a geometric ring above the surviving stunned target. Damage and stun share one impact; no chains, root or extra damage packets are added.

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

---
# Orla Hearthglow — The Hallkeeper

**Dwarf · Priest · Support · ALPHA**

Stable identity: `wc_u_dwarf_priest`. Cost: **2 gold**. Rarity label: **Uncommon**, separate from star level. Production and verification status is recorded separately in reports/implementation_state.json; this generated dossier does not certify an asset or build. All combat values are provisional prototype inputs.

Quick display name: **Orla**. Informational roles: Healer. Role tags provide no additional synergy.

## Character and world

Orla keeps Stoneveil’s common hall welcoming to miners, craftspeople and travelers alike. She and Mira exchange practical notes, with Orla insisting that a good chair and a warm meal are often as important as a clever spell. In the trials she practices keeping a close-knit team standing without asking anyone to become invulnerable.

Home region: `stoneveil`. Affiliation: `hearthwright_union`. Neither supplies a hidden third synergy. Proper names are original proposed fiction, not trademark-clearance claims.

## Appearance and art direction

Authored standing height: **1.3 m**, excluding raised equipment. Rig family: `humanoid_stocky`. One logical tile at every star. All characters are adults, fully clothed and presented as non-graphic heroic fantasy.

### Silhouette and proportions

A broad rounded coat, low lantern held at the chest and a soft arch-shaped head covering. Her gentle oval outline contrasts with Borin’s rectangular armor.

### Face, hair and expression

Warm dark skin, lively brown eyes and silver hair arranged in two thick side braids. Her smile is restrained and dependable.

### Costume construction

Rust-red wool coat over cream cloth, a wide woven apron panel, short gloves and practical boots. The head covering is a padded travel hood, not a rigid helmet.

### Color palette

Rust #AC6653; oatmeal #DCCEAF; forest #586B57; warm brass #BDA061.

### Equipment and magical focus

A squat octagonal lantern carried on a short handle and a small folded cloth pouch. The lantern’s heavy silhouette stays visible even when unlit.

### Three low-resolution identifiers

Low octagonal lantern, rounded hood and broad warm-colored coat.

### Materials and surface detail

Thick wool, stitched canvas, dull brass and frosted-looking opaque lantern panes with emissive color. Avoid glass refraction.

### Back and side-view constraints

A broad stitched hearth emblem and two large coat folds create readable planes. The hood must not stretch unnaturally during looking down.

## Combat statistics — without traits or temporary effects

| Property | One star | Two stars | Three stars |
|---|---:|---:|---:|
| Health | 820 | 1,476 | 2,656.8 |
| Basic attack damage | 36 | 64.8 | 116.64 |
| Attack delivery | ranged | ranged | ranged |
| Basic damage type | magic | magic | magic |
| Nominal attacks/second | 0.70 | 0.70 | 0.70 |
| Effective attacks/second at 20 Hz | 0.6897 | 0.6897 | 0.6897 |
| Range in tiles | 2 | 2 | 2 |
| Physical armor | 20 | 20 | 20 |
| Magic resistance | 25 | 25 | 25 |
| Movement tiles/second | 0.95 | 0.95 | 0.95 |

Nominal basic-attack DPS at one star: **25.20**, before mitigation, movement, stuns, skills, targeting downtime or timing quantization. Basic windup: 300 ms; ordinary projectile travel: 150 ms. No hidden critical hits, evasion, lifesteal or mana.

## One active skill

### Hearth Glow

**Player tooltip:** Heals herself and adjacent allies.

**Indonesian draft:** Memulihkan kesehatan diri sendiri dan sekutu di petak bersebelahan.

| Contract field | Value |
|---|---|
| Stable ability ID | `wc_a_dwarf_priest` |
| Effect / target selector | `heal` / `adjacent_allies` |
| One / two / three star magnitude | heal: 125 / 225 / 405 |
| Damage type | Not damaging |
| First-cast delay / cooldown | 3 s / 8 s |
| Windup / recovery | 0.35 s / 0.3 s |
| Effect duration | 0.0 s |
| Skill reach / area radius | 1 / 1 tiles |
| Can include self | True |
| Max dash distance | 0 tiles |
| Projectile travel | 0 ms |
| Affected stat | Not applicable |

Cooldown starts at successful cast commitment. An interrupted committed cast keeps its cooldown; an unavailable target leaves the ability ready and allows ordinary behavior. Area centers and area recipients are captured at release. Targeted projectiles keep their target ID but never retarget a defeated unit. Dash landing is reserved at commitment and validated before movement. See the rules contract for same-tick ordering, shield replacement and refresh semantics.

Health and basic damage use 1.00/1.80/3.24 star multipliers. Only explicitly authored skill magnitudes vary with stars; stun duration, range, radius, dash distance, cooldown and model footprint do not grow. A status-only skill may deliberately have identical behavior across stars; its owner still gains health and basic damage.

## Positioning and counterplay

**Preferred formation.** Second row among durable allies rather than alone at maximum range.

**Useful partners.** Borin and Dagna can stay close enough to receive the pulse; Mira enables Priest.

**Counterplay.** Area magic punishes the group formation required for efficient healing.

**Practical weakness.** Short heal reach and modest damage; allies outside the release snapshot receive nothing.

**Difference from the nearest alternative.** Mira can heal a distant single ally; Orla repairs a nearby group.

**Character-specific acceptance test.** Self is counted exactly once, each adjacent ally is healed once, and full-health targets do not inflate effective healing.

## Animation, effects and sound

Idle lifts the lantern slightly as if checking a path. Basics release a small light mote. The active opens the free arm and raises the lantern, then settles into the same stance.

**Skill effect:** A low amber ring washes over adjacent allies once; small rising squares suggest warmth. No lasting zone, regeneration or shield.

**Sound:** A warm bell cluster with a soft wooden resonance, distinct from Mira’s higher single-target cue.

Author at 60 FPS, as in-place animations with no locomotion-driven root translation. Required clips: Idle, Move, Attack, Active, Hit, Defeat, Victory. The active release marker is frame 21 relative to animation start. Basic release marker is frame 18. These are presentation alignment points, not sources of authoritative damage. Idle begins as a 2-second loop; movement as a 1-second cycle; hit as 0.4 seconds; defeat as 1 second; victory as 1.5 seconds. Adjust clip lengths during animation review without altering gameplay timing.

A defeat uses a brief stagger, kneel or magical dissolve with no injury detail. Stars use UI pips, a subtle trim accent and a brief upgrade flourish; do not produce three separate bodies or enlarge the collision footprint.

## Blender construction and Unreal handoff

Start from the `humanoid_stocky` base or a validated compatible family. Block silhouette before bevels; separate body, costume and equipment into named source collections. Build equipment as decorative fantasy game props, not real functional objects. Author model-space Z up and a consistent forward orientation, then prove conversion with the calibration fixture. Materials use one or two runtime slots and a shared atlas where it preserves identity.

Targets to profile: at most 15,000 LOD0 triangles, 1024-pixel default maps, up to 60 deforming bones and 4 influences per vertex. Lower-detail targets begin near 50% and 25% triangles. These are budgets, not measured performance.

Sockets: `weapon_r`, `weapon_l`, `cast_origin`, `head_ui`. Inspect shoulder, elbow, hip and knee extremes. Use separate rig proportions where needed; matching bone names is not proof of animation compatibility. Selection uses a stable unit proxy, not detailed prop collision. Team affiliation uses base rings/icons in addition to color, never a complete costume recolor.

**Specific production risk:** Group-heal effects can look like a persistent aura. Make the one-shot pulse clear and cap repeated target sounds.

Required source/export locations:

- blender: `art-source/heroes/wc_u_dwarf_priest/wc_u_dwarf_priest.blend`

- mesh_fbx: `exports/heroes/wc_u_dwarf_priest/SK_wc_u_dwarf_priest.fbx`

- unreal_folder: `/Game/WonderChess/Heroes/wc_u_dwarf_priest`

- portrait: `exports/heroes/wc_u_dwarf_priest/portrait.png`

Create separate animation exports and texture maps, a model-derived portrait, front/side/back/three-quarter views, a gameplay-camera screenshot, and an actual Unreal animation capture. Log source/export hashes, skeleton revision, tool versions and import preset. Deliberately change one costume detail, re-export and verify existing material, skeleton, animation and actor references survive.

## Model-sheet generation brief

Original Wonder Chess high-fantasy character production sheet for Orla Hearthglow, The Hallkeeper. Dwarf Priest, adult character, height 1.3 m. Front, true side, back and three-quarter views at matching scale, neutral A-pose plus one action pose. A broad rounded coat, low lantern held at the chest and a soft arch-shaped head covering. Her gentle oval outline contrasts with Borin’s rectangular armor. Warm dark skin, lively brown eyes and silver hair arranged in two thick side braids. Her smile is restrained and dependable. Rust-red wool coat over cream cloth, a wide woven apron panel, short gloves and practical boots. The head covering is a padded travel hood, not a rigid helmet. A squat octagonal lantern carried on a short handle and a small folded cloth pouch. The lantern’s heavy silhouette stays visible even when unlit. Palette: Rust #AC6653; oatmeal #DCCEAF; forest #586B57; warm brass #BDA061. Flat neutral background, orthographic construction views, equipment inset, readable seams, non-graphic stylized fantasy. No copied franchise designs, text baked into textures, cinematic fog, invented extra limbs or altered gear between views. These are concept directions, not generated images.

## Approval gates

Silhouette passes at 96-pixel preview; costume agrees across all views; all seven clips reviewed; no required missing textures; no unexplained import scale compensation; effect matches declared reach and damage type; portrait agrees with the modeled hero; crowded-board test passes; source revision/reimport is demonstrated. A Python exit code alone does not approve the art.

Canonical source: `data/units.json`. Regenerate this dossier with `python tools/build_documents.py` after data edits. Do not hand-edit a stat table and leave the JSON unchanged.

---
# Tala Ironroot — The Caravan Wall

**Orc · Guardian · Defender · ALPHA**

Stable identity: `wc_u_orc_guardian`. Cost: **2 gold**. Rarity label: **Uncommon**, separate from star level. Production and verification status is recorded separately in reports/implementation_state.json; this generated dossier does not certify an asset or build. All combat values are provisional prototype inputs.

Quick display name: **Tala**. Informational roles: Tank. Role tags provide no additional synergy.

## Character and world

Tala leads caravan defenses across Stormstep and knows that travelers rarely fit a perfect formation. She joins the trials to make protection adaptable without turning it into a promise that nobody can be hurt. Rok respects her steady judgment, while Kesh keeps returning to ask whether his latest shortcut counts as a sensible route.

Home region: `stormstep`. Affiliation: `highland_watch`. Neither supplies a hidden third synergy. Proper names are original proposed fiction, not trademark-clearance claims.

## Appearance and art direction

Authored standing height: **2.0 m**, excluding raised equipment. Rig family: `humanoid_broad`. One logical tile at every star. All characters are adults, fully clothed and presented as non-graphic heroic fantasy.

### Silhouette and proportions

A wide arch formed by two high shoulder guards and a tall rectangular shield with a rounded top. The lower body remains a stable trapezoid.

### Face, hair and expression

Deep moss-green skin, warm brown eyes, small tusks and tightly braided dark hair. Her expression is attentive rather than aggressive.

### Costume construction

Layered leather-and-bronze armor, a pale ochre shoulder wrap, a blue woven sash and thick boots. Broad woven patterns identify her caravan community.

### Color palette

Bronze #AC8658; ochre #D1B576; deep blue #405E78; moss #60765A.

### Equipment and magical focus

A broad fantasy tower shield and a short ceremonial mace. The shield carries a simple interlocking-road emblem with no dense carving.

### Three low-resolution identifiers

Rounded tower shield, arched shoulders and a bold blue waist sash.

### Materials and surface detail

Worn bronze, thick cloth and matte hide. Shield wear is painted as soft color variation rather than deep damage.

### Back and side-view constraints

A flat travel pack sits beneath the shoulder line. Keep its volume low enough not to collide with the shield when turning.

## Combat statistics — without traits or temporary effects

| Property | One star | Two stars | Three stars |
|---|---:|---:|---:|
| Health | 1,120 | 2,016 | 3,628.8 |
| Basic attack damage | 45 | 81 | 145.8 |
| Attack delivery | melee | melee | melee |
| Basic damage type | physical | physical | physical |
| Nominal attacks/second | 0.65 | 0.65 | 0.65 |
| Effective attacks/second at 20 Hz | 0.6452 | 0.6452 | 0.6452 |
| Range in tiles | 1 | 1 | 1 |
| Physical armor | 30 | 30 | 30 |
| Magic resistance | 20 | 20 | 20 |
| Movement tiles/second | 0.90 | 0.90 | 0.90 |

Nominal basic-attack DPS at one star: **29.25**, before mitigation, movement, stuns, skills, targeting downtime or timing quantization. Basic windup: 250 ms; ordinary projectile travel: 0 ms. No hidden critical hits, evasion, lifesteal or mana.

## One active skill

### Shared Guard

**Player tooltip:** Shields herself and adjacent allies for three seconds.

**Indonesian draft:** Memberikan perisai sementara kepada diri sendiri dan sekutu bersebelahan.

| Contract field | Value |
|---|---|
| Stable ability ID | `wc_a_orc_guardian` |
| Effect / target selector | `shield` / `adjacent_allies` |
| One / two / three star magnitude | shield: 140 / 252 / 454 |
| Damage type | Not damaging |
| First-cast delay / cooldown | 2.5 s / 9.5 s |
| Windup / recovery | 0.35 s / 0.3 s |
| Effect duration | 3.0 s |
| Skill reach / area radius | 1 / 1 tiles |
| Can include self | True |
| Max dash distance | 0 tiles |
| Projectile travel | 0 ms |
| Affected stat | Not applicable |

Cooldown starts at successful cast commitment. An interrupted committed cast keeps its cooldown; an unavailable target leaves the ability ready and allows ordinary behavior. Area centers and area recipients are captured at release. Targeted projectiles keep their target ID but never retarget a defeated unit. Dash landing is reserved at commitment and validated before movement. See the rules contract for same-tick ordering, shield replacement and refresh semantics.

Health and basic damage use 1.00/1.80/3.24 star multipliers. Only explicitly authored skill magnitudes vary with stars; stun duration, range, radius, dash distance, cooldown and model footprint do not grow. A status-only skill may deliberately have identical behavior across stars; its owner still gains health and basic damage.

## Positioning and counterplay

**Preferred formation.** Frontline with at least one adjacent ally at cast time.

**Useful partners.** Dagna or Rok benefits from nearby protection; Orla can sustain the same cluster.

**Counterplay.** Spread ranged attacks and area magic both pressure different weaknesses of her grouped team.

**Practical weakness.** Lower shield amount per recipient than a dedicated self-shield; no control skill.

**Difference from the nearest alternative.** Ada shields only herself for a larger amount; Tala distributes a smaller shield to a nearby formation.

**Character-specific acceptance test.** Shield power is source-derived once, self is not duplicated, and leaving the radius after release does not remove the granted shield.

## Animation, effects and sound

Idle angles the shield protectively toward adjacent allies. Basics use a short mace arc. Shared Guard plants the shield and extends the free hand outward, clearly signaling a group effect.

**Skill effect:** Several short amber shield outlines appear on eligible recipients; a brief ground ring shows reach. No continuous aura follows her afterward.

**Sound:** One low shield chime and quiet recipient ticks, mixed as a single event rather than many full-volume sounds.

Author at 60 FPS, as in-place animations with no locomotion-driven root translation. Required clips: Idle, Move, Attack, Active, Hit, Defeat, Victory. The active release marker is frame 21 relative to animation start. Basic release marker is frame 15. These are presentation alignment points, not sources of authoritative damage. Idle begins as a 2-second loop; movement as a 1-second cycle; hit as 0.4 seconds; defeat as 1 second; victory as 1.5 seconds. Adjust clip lengths during animation review without altering gameplay timing.

A defeat uses a brief stagger, kneel or magical dissolve with no injury detail. Stars use UI pips, a subtle trim accent and a brief upgrade flourish; do not produce three separate bodies or enlarge the collision footprint.

## Blender construction and Unreal handoff

Start from the `humanoid_broad` base or a validated compatible family. Block silhouette before bevels; separate body, costume and equipment into named source collections. Build equipment as decorative fantasy game props, not real functional objects. Author model-space Z up and a consistent forward orientation, then prove conversion with the calibration fixture. Materials use one or two runtime slots and a shared atlas where it preserves identity.

Targets to profile: at most 15,000 LOD0 triangles, 1024-pixel default maps, up to 60 deforming bones and 4 influences per vertex. Lower-detail targets begin near 50% and 25% triangles. These are budgets, not measured performance.

Sockets: `weapon_r`, `weapon_l`, `cast_origin`, `head_ui`. Inspect shoulder, elbow, hip and knee extremes. Use separate rig proportions where needed; matching bone names is not proof of animation compatibility. Selection uses a stable unit proxy, not detailed prop collision. Team affiliation uses base rings/icons in addition to color, never a complete costume recolor.

**Specific production risk:** Large shield and shoulders may occlude neighboring supports. Use a lowered idle pose and test the camera from both encounter orientations.

Required source/export locations:

- blender: `art-source/heroes/wc_u_orc_guardian/wc_u_orc_guardian.blend`

- mesh_fbx: `exports/heroes/wc_u_orc_guardian/SK_wc_u_orc_guardian.fbx`

- unreal_folder: `/Game/WonderChess/Heroes/wc_u_orc_guardian`

- portrait: `exports/heroes/wc_u_orc_guardian/portrait.png`

Create separate animation exports and texture maps, a model-derived portrait, front/side/back/three-quarter views, a gameplay-camera screenshot, and an actual Unreal animation capture. Log source/export hashes, skeleton revision, tool versions and import preset. Deliberately change one costume detail, re-export and verify existing material, skeleton, animation and actor references survive.

## Model-sheet generation brief

Original Wonder Chess high-fantasy character production sheet for Tala Ironroot, The Caravan Wall. Orc Guardian, adult character, height 2.0 m. Front, true side, back and three-quarter views at matching scale, neutral A-pose plus one action pose. A wide arch formed by two high shoulder guards and a tall rectangular shield with a rounded top. The lower body remains a stable trapezoid. Deep moss-green skin, warm brown eyes, small tusks and tightly braided dark hair. Her expression is attentive rather than aggressive. Layered leather-and-bronze armor, a pale ochre shoulder wrap, a blue woven sash and thick boots. Broad woven patterns identify her caravan community. A broad fantasy tower shield and a short ceremonial mace. The shield carries a simple interlocking-road emblem with no dense carving. Palette: Bronze #AC8658; ochre #D1B576; deep blue #405E78; moss #60765A. Flat neutral background, orthographic construction views, equipment inset, readable seams, non-graphic stylized fantasy. No copied franchise designs, text baked into textures, cinematic fog, invented extra limbs or altered gear between views. These are concept directions, not generated images.

## Approval gates

Silhouette passes at 96-pixel preview; costume agrees across all views; all seven clips reviewed; no required missing textures; no unexplained import scale compensation; effect matches declared reach and damage type; portrait agrees with the modeled hero; crowded-board test passes; source revision/reimport is demonstrated. A Python exit code alone does not approve the art.

Canonical source: `data/units.json`. Regenerate this dossier with `python tools/build_documents.py` after data edits. Do not hand-edit a stat table and leave the JSON unchanged.

---
# Pippa Oakstride — The Orchard Defender

**Halfling · Warrior · Melee damage · ALPHA**

Stable identity: `wc_u_halfling_warrior`. Cost: **1 gold**. Rarity label: **Common**, separate from star level. Production and verification status is recorded separately in reports/implementation_state.json; this generated dossier does not certify an asset or build. All combat values are provisional prototype inputs.

Quick display name: **Pippa**. Informational roles: Melee. Role tags provide no additional synergy.

## Character and world

Pippa organizes Willowrun’s orchard crews and can settle an argument about harvest shares before it becomes a feud. She entered the trials after helping Tala guide a stranded caravan home. Her confidence comes from preparation and practical teamwork, not from pretending that being small makes every danger harmless.

Home region: `willowrun`. Affiliation: `wayfarer_fellowship`. Neither supplies a hidden third synergy. Proper names are original proposed fiction, not trademark-clearance claims.

## Appearance and art direction

Authored standing height: **1.12 m**, excluding raised equipment. Rig family: `humanoid_small`. One logical tile at every star. All characters are adults, fully clothed and presented as non-graphic heroic fantasy.

### Silhouette and proportions

A small broad stance with a large round wooden buckler and an upright leaf-shaped fantasy club. An oversized short scarf forms a clear horizontal at the neck.

### Face, hair and expression

Light brown skin, freckled cheeks, bright hazel eyes and dense chestnut curls. Keep the face friendly and visibly adult.

### Costume construction

Apple-green quilted jacket, ochre trousers, a red neck scarf and broad walking boots. Outfit proportions emphasize capable mobility, not toy-like baby features.

### Color palette

Apple green #7A985A; ochre #BE9A59; berry red #A85251; walnut #73553B.

### Equipment and magical focus

Round orchard-mark buckler and short stylized wooden club reinforced with decorative bronze bands. Both are exaggerated fantasy props.

### Three low-resolution identifiers

Circular buckler, large red scarf and wide planted stance.

### Materials and surface detail

Quilted cloth, matte wood and dull bronze. Paint the orchard emblem in one readable silhouette.

### Back and side-view constraints

A square travel patch on the jacket and scarf ends over one shoulder keep the rear identifiable.

## Combat statistics — without traits or temporary effects

| Property | One star | Two stars | Three stars |
|---|---:|---:|---:|
| Health | 760 | 1,368 | 2,462.4 |
| Basic attack damage | 54 | 97.2 | 174.96 |
| Attack delivery | melee | melee | melee |
| Basic damage type | physical | physical | physical |
| Nominal attacks/second | 0.95 | 0.95 | 0.95 |
| Effective attacks/second at 20 Hz | 0.9091 | 0.9091 | 0.9091 |
| Range in tiles | 1 | 1 | 1 |
| Physical armor | 20 | 20 | 20 |
| Magic resistance | 10 | 10 | 10 |
| Movement tiles/second | 1.20 | 1.20 | 1.20 |

Nominal basic-attack DPS at one star: **51.30**, before mitigation, movement, stuns, skills, targeting downtime or timing quantization. Basic windup: 350 ms; ordinary projectile travel: 0 ms. No hidden critical hits, evasion, lifesteal or mana.

## One active skill

### Stout Heart

**Player tooltip:** Gains a temporary personal shield.

**Indonesian draft:** Memberikan perisai sementara kepada diri sendiri.

| Contract field | Value |
|---|---|
| Stable ability ID | `wc_a_halfling_warrior` |
| Effect / target selector | `shield` / `self` |
| One / two / three star magnitude | shield: 150 / 270 / 486 |
| Damage type | Not damaging |
| First-cast delay / cooldown | 2 s / 7.5 s |
| Windup / recovery | 0.25 s / 0.3 s |
| Effect duration | 2.5 s |
| Skill reach / area radius | 0 / 0 tiles |
| Can include self | True |
| Max dash distance | 0 tiles |
| Projectile travel | 0 ms |
| Affected stat | Not applicable |

Cooldown starts at successful cast commitment. An interrupted committed cast keeps its cooldown; an unavailable target leaves the ability ready and allows ordinary behavior. Area centers and area recipients are captured at release. Targeted projectiles keep their target ID but never retarget a defeated unit. Dash landing is reserved at commitment and validated before movement. See the rules contract for same-tick ordering, shield replacement and refresh semantics.

Health and basic damage use 1.00/1.80/3.24 star multipliers. Only explicitly authored skill magnitudes vary with stars; stun duration, range, radius, dash distance, cooldown and model footprint do not grow. A status-only skill may deliberately have identical behavior across stars; its owner still gains health and basic damage.

## Positioning and counterplay

**Preferred formation.** Beside a sturdier frontline ally where she can attack without taking every hit.

**Useful partners.** Finn or Nella supplies Halfling movement; Cass provides Warrior damage.

**Counterplay.** Sustained magic and crowd control can overcome her modest health after the shield ends.

**Practical weakness.** Short reach, no area effect, and less durability than a dedicated Guardian.

**Difference from the nearest alternative.** Ada is a defensive anchor; Pippa is a faster Warrior with a smaller survival window.

**Character-specific acceptance test.** Shield has a fixed 2500 ms duration at every star and a correctly scaled visual shell.

## Animation, effects and sound

Idle is grounded rather than constantly bouncing. Walk uses quick full-foot steps. Basics are short determined swings. Stout Heart lifts the buckler with a compact upward hop that returns to the same logical cell.

**Skill effect:** A small green-gold shield outline that matches her scale. No taunt or healing accompanies it.

**Sound:** A light wooden knock and short warm chime; avoid childish squeaks.

Author at 60 FPS, as in-place animations with no locomotion-driven root translation. Required clips: Idle, Move, Attack, Active, Hit, Defeat, Victory. The active release marker is frame 15 relative to animation start. Basic release marker is frame 21. These are presentation alignment points, not sources of authoritative damage. Idle begins as a 2-second loop; movement as a 1-second cycle; hit as 0.4 seconds; defeat as 1 second; victory as 1.5 seconds. Adjust clip lengths during animation review without altering gameplay timing.

A defeat uses a brief stagger, kneel or magical dissolve with no injury detail. Stars use UI pips, a subtle trim accent and a brief upgrade flourish; do not produce three separate bodies or enlarge the collision footprint.

## Blender construction and Unreal handoff

Start from the `humanoid_small` base or a validated compatible family. Block silhouette before bevels; separate body, costume and equipment into named source collections. Build equipment as decorative fantasy game props, not real functional objects. Author model-space Z up and a consistent forward orientation, then prove conversion with the calibration fixture. Materials use one or two runtime slots and a shared atlas where it preserves identity.

Targets to profile: at most 15,000 LOD0 triangles, 1024-pixel default maps, up to 60 deforming bones and 4 influences per vertex. Lower-detail targets begin near 50% and 25% triangles. These are budgets, not measured performance.

Sockets: `weapon_r`, `weapon_l`, `cast_origin`, `head_ui`. Inspect shoulder, elbow, hip and knee extremes. Use separate rig proportions where needed; matching bone names is not proof of animation compatibility. Selection uses a stable unit proxy, not detailed prop collision. Team affiliation uses base rings/icons in addition to color, never a complete costume recolor.

**Specific production risk:** Small units can disappear behind tall allies. Test camera spacing and health-bar anchors without enlarging her logical footprint.

Required source/export locations:

- blender: `art-source/heroes/wc_u_halfling_warrior/wc_u_halfling_warrior.blend`

- mesh_fbx: `exports/heroes/wc_u_halfling_warrior/SK_wc_u_halfling_warrior.fbx`

- unreal_folder: `/Game/WonderChess/Heroes/wc_u_halfling_warrior`

- portrait: `exports/heroes/wc_u_halfling_warrior/portrait.png`

Create separate animation exports and texture maps, a model-derived portrait, front/side/back/three-quarter views, a gameplay-camera screenshot, and an actual Unreal animation capture. Log source/export hashes, skeleton revision, tool versions and import preset. Deliberately change one costume detail, re-export and verify existing material, skeleton, animation and actor references survive.

## Model-sheet generation brief

Original Wonder Chess high-fantasy character production sheet for Pippa Oakstride, The Orchard Defender. Halfling Warrior, adult character, height 1.12 m. Front, true side, back and three-quarter views at matching scale, neutral A-pose plus one action pose. A small broad stance with a large round wooden buckler and an upright leaf-shaped fantasy club. An oversized short scarf forms a clear horizontal at the neck. Light brown skin, freckled cheeks, bright hazel eyes and dense chestnut curls. Keep the face friendly and visibly adult. Apple-green quilted jacket, ochre trousers, a red neck scarf and broad walking boots. Outfit proportions emphasize capable mobility, not toy-like baby features. Round orchard-mark buckler and short stylized wooden club reinforced with decorative bronze bands. Both are exaggerated fantasy props. Palette: Apple green #7A985A; ochre #BE9A59; berry red #A85251; walnut #73553B. Flat neutral background, orthographic construction views, equipment inset, readable seams, non-graphic stylized fantasy. No copied franchise designs, text baked into textures, cinematic fog, invented extra limbs or altered gear between views. These are concept directions, not generated images.

## Approval gates

Silhouette passes at 96-pixel preview; costume agrees across all views; all seven clips reviewed; no required missing textures; no unexplained import scale compensation; effect matches declared reach and damage type; portrait agrees with the modeled hero; crowded-board test passes; source revision/reimport is demonstrated. A Python exit code alone does not approve the art.

Canonical source: `data/units.json`. Regenerate this dossier with `python tools/build_documents.py` after data edits. Do not hand-edit a stat table and leave the JSON unchanged.

---
# Finn Thistlearrow — The River Lookout

**Halfling · Ranger · Ranged damage · ALPHA**

Stable identity: `wc_u_halfling_ranger`. Cost: **1 gold**. Rarity label: **Common**, separate from star level. Production and verification status is recorded separately in reports/implementation_state.json; this generated dossier does not certify an asset or build. All combat values are provisional prototype inputs.

Quick display name: **Finn**. Informational roles: Ranged. Role tags provide no additional synergy.

## Character and world

Finn watches Willowrun’s river crossings and records changes in water levels for travelers. He is quieter than Pippa but just as determined to keep routes open. The trials give him a way to practice slowing a dangerous opponent’s attacks while the rest of his team carries out a plan.

Home region: `willowrun`. Affiliation: `wayfarer_fellowship`. Neither supplies a hidden third synergy. Proper names are original proposed fiction, not trademark-clearance claims.

## Appearance and art direction

Authored standing height: **1.08 m**, excluding raised equipment. Rig family: `humanoid_small`. One logical tile at every star. All characters are adults, fully clothed and presented as non-graphic heroic fantasy.

### Silhouette and proportions

A small narrow body beneath a broad folded brim and a long simple bow carried upright. A narrow shoulder cape makes a triangular rear profile.

### Face, hair and expression

Tan skin, dark eyes, sandy curls and a thoughtful expression. The hat brim tilts upward enough not to hide his eyes.

### Costume construction

River-blue vest over cream sleeves, moss trousers, a short cape and simple boots. One broad belt pouch breaks the symmetrical torso.

### Color palette

River blue #58899C; cream #E4DABC; moss #6F8158; warm brown #866243.

### Equipment and magical focus

A slim fantasy bow and a compact quiver worn at the side. Keep the active projectile visibly magical instead of suggesting a real substance.

### Three low-resolution identifiers

Folded brim, upright long bow and blue triangular shoulder cape.

### Materials and surface detail

Matte cloth, oiled wood and simple leather. No thin transparent feathers on arrows at gameplay distance.

### Back and side-view constraints

The cape ends above the waist and leaves the side quiver visible; a stitched river line supplies one large motif.

## Combat statistics — without traits or temporary effects

| Property | One star | Two stars | Three stars |
|---|---:|---:|---:|
| Health | 590 | 1,062 | 1,911.6 |
| Basic attack damage | 49 | 88.2 | 158.76 |
| Attack delivery | ranged | ranged | ranged |
| Basic damage type | physical | physical | physical |
| Nominal attacks/second | 1.00 | 1.00 | 1.00 |
| Effective attacks/second at 20 Hz | 1.0000 | 1.0000 | 1.0000 |
| Range in tiles | 4 | 4 | 4 |
| Physical armor | 8 | 8 | 8 |
| Magic resistance | 10 | 10 | 10 |
| Movement tiles/second | 1.25 | 1.25 | 1.25 |

Nominal basic-attack DPS at one star: **49.00**, before mitigation, movement, stuns, skills, targeting downtime or timing quantization. Basic windup: 300 ms; ordinary projectile travel: 150 ms. No hidden critical hits, evasion, lifesteal or mana.

## One active skill

### Dulling Shot

**Player tooltip:** Reduce the basic attack rate of the in-range enemy with the highest current attack rate. Ties prefer the nearer enemy, then stable identity. Movement and skill cooldowns are unchanged.

**Indonesian draft:** Kurangi laju serangan dasar musuh dalam jangkauan dengan laju serangan tertinggi saat ini. Jika sama, pilih yang terdekat, lalu identitas tetap. Gerakan dan jeda skill tidak berubah.

| Contract field | Value |
|---|---|
| Stable ability ID | `wc_a_halfling_ranger` |
| Effect / target selector | `stat_modifier` / `highest_attack_rate_enemy` |
| One / two / three star magnitude | stat_modifier: -20% / -25% / -30% |
| Damage type | Not damaging |
| First-cast delay / cooldown | 2.5 s / 8 s |
| Windup / recovery | 0.3 s / 0.3 s |
| Effect duration | 3.0 s |
| Skill reach / area radius | 4 / 0 tiles |
| Can include self | False |
| Max dash distance | 0 tiles |
| Projectile travel | 150 ms |
| Affected stat | attack_rate |

Cooldown starts at successful cast commitment. An interrupted committed cast keeps its cooldown; an unavailable target leaves the ability ready and allows ordinary behavior. Area centers and area recipients are captured at release. Targeted projectiles keep their target ID but never retarget a defeated unit. Dash landing is reserved at commitment and validated before movement. See the rules contract for same-tick ordering, shield replacement and refresh semantics.

Health and basic damage use 1.00/1.80/3.24 star multipliers. Only explicitly authored skill magnitudes vary with stars; stun duration, range, radius, dash distance, cooldown and model footprint do not grow. A status-only skill may deliberately have identical behavior across stars; its owner still gains health and basic damage.

## Positioning and counterplay

**Preferred formation.** Protected backline where he can keep shooting the most threatening current opponent.

**Useful partners.** Tessa or Liora enables Ranger; Pippa provides a matching-race frontline.

**Counterplay.** Ability-focused casters are less affected because Dulling Shot does not alter active cooldowns.

**Practical weakness.** Low health and no burst active; the debuff has limited value against already slow attackers.

**Difference from the nearest alternative.** Tessa adds a damage burst; Finn reduces an enemy’s basic-attack output.

**Character-specific acceptance test.** Negative speed modifiers use the strongest-key refresh policy, cannot reduce speed below the clamp, and never slow cooldowns.

## Animation, effects and sound

Idle checks the distance under the hat brim. Basics use quick controlled bow draws. The active pauses longer, aims carefully and releases one blue mote-tipped fantasy arrow.

**Skill effect:** Blue chevrons descend briefly over the target to indicate reduced attack tempo. No movement slow, poison or damage-over-time trail.

**Sound:** A clear bow snap followed by a soft descending two-note magical cue.

Author at 60 FPS, as in-place animations with no locomotion-driven root translation. Required clips: Idle, Move, Attack, Active, Hit, Defeat, Victory. The active release marker is frame 18 relative to animation start. Basic release marker is frame 18. These are presentation alignment points, not sources of authoritative damage. Idle begins as a 2-second loop; movement as a 1-second cycle; hit as 0.4 seconds; defeat as 1 second; victory as 1.5 seconds. Adjust clip lengths during animation review without altering gameplay timing.

A defeat uses a brief stagger, kneel or magical dissolve with no injury detail. Stars use UI pips, a subtle trim accent and a brief upgrade flourish; do not produce three separate bodies or enlarge the collision footprint.

## Blender construction and Unreal handoff

Start from the `humanoid_small` base or a validated compatible family. Block silhouette before bevels; separate body, costume and equipment into named source collections. Build equipment as decorative fantasy game props, not real functional objects. Author model-space Z up and a consistent forward orientation, then prove conversion with the calibration fixture. Materials use one or two runtime slots and a shared atlas where it preserves identity.

Targets to profile: at most 15,000 LOD0 triangles, 1024-pixel default maps, up to 60 deforming bones and 4 influences per vertex. Lower-detail targets begin near 50% and 25% triangles. These are budgets, not measured performance.

Sockets: `weapon_r`, `weapon_l`, `cast_origin`, `head_ui`. Inspect shoulder, elbow, hip and knee extremes. Use separate rig proportions where needed; matching bone names is not proof of animation compatibility. Selection uses a stable unit proxy, not detailed prop collision. Team affiliation uses base rings/icons in addition to color, never a complete costume recolor.

**Specific production risk:** The debuff must remain distinguishable from stun. Do not show immobilizing chains or stop the target’s movement animation.

Required source/export locations:

- blender: `art-source/heroes/wc_u_halfling_ranger/wc_u_halfling_ranger.blend`

- mesh_fbx: `exports/heroes/wc_u_halfling_ranger/SK_wc_u_halfling_ranger.fbx`

- unreal_folder: `/Game/WonderChess/Heroes/wc_u_halfling_ranger`

- portrait: `exports/heroes/wc_u_halfling_ranger/portrait.png`

Create separate animation exports and texture maps, a model-derived portrait, front/side/back/three-quarter views, a gameplay-camera screenshot, and an actual Unreal animation capture. Log source/export hashes, skeleton revision, tool versions and import preset. Deliberately change one costume detail, re-export and verify existing material, skeleton, animation and actor references survive.

## Model-sheet generation brief

Original Wonder Chess high-fantasy character production sheet for Finn Thistlearrow, The River Lookout. Halfling Ranger, adult character, height 1.08 m. Front, true side, back and three-quarter views at matching scale, neutral A-pose plus one action pose. A small narrow body beneath a broad folded brim and a long simple bow carried upright. A narrow shoulder cape makes a triangular rear profile. Tan skin, dark eyes, sandy curls and a thoughtful expression. The hat brim tilts upward enough not to hide his eyes. River-blue vest over cream sleeves, moss trousers, a short cape and simple boots. One broad belt pouch breaks the symmetrical torso. A slim fantasy bow and a compact quiver worn at the side. Keep the active projectile visibly magical instead of suggesting a real substance. Palette: River blue #58899C; cream #E4DABC; moss #6F8158; warm brown #866243. Flat neutral background, orthographic construction views, equipment inset, readable seams, non-graphic stylized fantasy. No copied franchise designs, text baked into textures, cinematic fog, invented extra limbs or altered gear between views. These are concept directions, not generated images.

## Approval gates

Silhouette passes at 96-pixel preview; costume agrees across all views; all seven clips reviewed; no required missing textures; no unexplained import scale compensation; effect matches declared reach and damage type; portrait agrees with the modeled hero; crowded-board test passes; source revision/reimport is demonstrated. A Python exit code alone does not approve the art.

Canonical source: `data/units.json`. Regenerate this dossier with `python tools/build_documents.py` after data edits. Do not hand-edit a stat table and leave the JSON unchanged.

---
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

---
# Milo Mistwhistle — The Weather Tinkerer

**Halfling · Mage · Spell damage · ALPHA**

Stable identity: `wc_u_halfling_mage`. Cost: **2 gold**. Rarity label: **Uncommon**, separate from star level. Production and verification status is recorded separately in reports/implementation_state.json; this generated dossier does not certify an asset or build. All combat values are provisional prototype inputs.

Quick display name: **Milo**. Informational roles: Caster. Role tags provide no additional synergy.

## Character and world

Milo makes harmless weather displays for Willowrun’s festivals and became fascinated by why the real winds were changing. Zura answered his questions more patiently than he expected. He enters the trials to turn those lessons into a small dependable spell, while insisting that practical magic can still be delightful.

Home region: `willowrun`. Affiliation: `wayfarer_fellowship`. Neither supplies a hidden third synergy. Proper names are original proposed fiction, not trademark-clearance claims.

## Appearance and art direction

Authored standing height: **1.14 m**, excluding raised equipment. Rig family: `humanoid_small`. One logical tile at every star. All characters are adults, fully clothed and presented as non-graphic heroic fantasy.

### Silhouette and proportions

A round short travel coat, large upturned collar and a thick spiral-topped wand. A small rigid umbrella disk folded against the back adds a distinctive rounded shape.

### Face, hair and expression

Warm tan skin, gray eyes, a small dark mustache and wavy brown hair. Clearly adult proportions and expression; no oversized infant features.

### Costume construction

Sky-blue raincoat, cream collar, copper belt buckle and dark boots. Sleeves are wide but stop at the wrists for clean hand animation.

### Color palette

Sky blue #77AFC2; cream #EAE0C7; copper #B78258; slate #566477.

### Equipment and magical focus

A thick spiral fantasy wand and a collapsed decorative umbrella disk. The disk is not a shield or movement device.

### Three low-resolution identifiers

Spiral wand, upturned pale collar and round coat silhouette.

### Materials and surface detail

Waxed cloth, painted wood and dull copper; use a small bounded emissive spiral rather than transparent mist clothing.

### Back and side-view constraints

Umbrella disk is locked to a short bracket, clear of the head. The coat separates into two broad lower panels.

## Combat statistics — without traits or temporary effects

| Property | One star | Two stars | Three stars |
|---|---:|---:|---:|
| Health | 570 | 1,026 | 1,846.8 |
| Basic attack damage | 42 | 75.6 | 136.08 |
| Attack delivery | ranged | ranged | ranged |
| Basic damage type | magic | magic | magic |
| Nominal attacks/second | 0.80 | 0.80 | 0.80 |
| Effective attacks/second at 20 Hz | 0.8000 | 0.8000 | 0.8000 |
| Range in tiles | 3 | 3 | 3 |
| Physical armor | 8 | 8 | 8 |
| Magic resistance | 20 | 20 | 20 |
| Movement tiles/second | 1.15 | 1.15 | 1.15 |

Nominal basic-attack DPS at one star: **33.60**, before mitigation, movement, stuns, skills, targeting downtime or timing quantization. Basic windup: 300 ms; ordinary projectile travel: 150 ms. No hidden critical hits, evasion, lifesteal or mana.

## One active skill

### Mist Pop

**Player tooltip:** Bursts magic around the target’s captured location.

**Indonesian draft:** Memberikan kerusakan sihir kepada musuh di area sasaran.

| Contract field | Value |
|---|---|
| Stable ability ID | `wc_a_halfling_mage` |
| Effect / target selector | `damage` / `current_enemy_area` |
| One / two / three star magnitude | damage: 135 / 243 / 437 |
| Damage type | magic |
| First-cast delay / cooldown | 3 s / 7 s |
| Windup / recovery | 0.35 s / 0.3 s |
| Effect duration | 0.0 s |
| Skill reach / area radius | 4 / 1 tiles |
| Can include self | False |
| Max dash distance | 0 tiles |
| Projectile travel | 200 ms |
| Affected stat | Not applicable |

Cooldown starts at successful cast commitment. An interrupted committed cast keeps its cooldown; an unavailable target leaves the ability ready and allows ordinary behavior. Area centers and area recipients are captured at release. Targeted projectiles keep their target ID but never retarget a defeated unit. Dash landing is reserved at commitment and validated before movement. See the rules contract for same-tick ordering, shield replacement and refresh semantics.

Health and basic damage use 1.00/1.80/3.24 star multipliers. Only explicitly authored skill magnitudes vary with stars; stun duration, range, radius, dash distance, cooldown and model footprint do not grow. A status-only skill may deliberately have identical behavior across stars; its owner still gains health and basic damage.

## Positioning and counterplay

**Preferred formation.** Middle-back row with enough protection to cast repeatedly.

**Useful partners.** Rowan enables Mage; Finn or Pippa supplies Halfling mobility.

**Counterplay.** Spread formations reduce area value, while a single durable target exposes his low burst.

**Practical weakness.** Fragile and unable to provide any control or protection.

**Difference from the nearest alternative.** Rowan’s burst is stronger and slower; Milo supplies lower-cost repeated small areas.

**Character-specific acceptance test.** Mist Pop is a single damage event and never produces hidden ticking cloud damage.

## Animation, effects and sound

Idle balances the wand with a curious head tilt. Basics send a small pale mote. The active makes one circular stir and flicks a cloudlet toward the captured target area.

**Skill effect:** A small blue-white cloud pops low to the board and vanishes. It does not blind, obscure the camera, slow movement or persist.

**Sound:** A soft rising whistle followed by a light magical pop, without a continuous wind loop.

Author at 60 FPS, as in-place animations with no locomotion-driven root translation. Required clips: Idle, Move, Attack, Active, Hit, Defeat, Victory. The active release marker is frame 21 relative to animation start. Basic release marker is frame 18. These are presentation alignment points, not sources of authoritative damage. Idle begins as a 2-second loop; movement as a 1-second cycle; hit as 0.4 seconds; defeat as 1 second; victory as 1.5 seconds. Adjust clip lengths during animation review without altering gameplay timing.

A defeat uses a brief stagger, kneel or magical dissolve with no injury detail. Stars use UI pips, a subtle trim accent and a brief upgrade flourish; do not produce three separate bodies or enlarge the collision footprint.

## Blender construction and Unreal handoff

Start from the `humanoid_small` base or a validated compatible family. Block silhouette before bevels; separate body, costume and equipment into named source collections. Build equipment as decorative fantasy game props, not real functional objects. Author model-space Z up and a consistent forward orientation, then prove conversion with the calibration fixture. Materials use one or two runtime slots and a shared atlas where it preserves identity.

Targets to profile: at most 15,000 LOD0 triangles, 1024-pixel default maps, up to 60 deforming bones and 4 influences per vertex. Lower-detail targets begin near 50% and 25% triangles. These are budgets, not measured performance.

Sockets: `weapon_r`, `weapon_l`, `cast_origin`, `head_ui`. Inspect shoulder, elbow, hip and knee extremes. Use separate rig proportions where needed; matching bone names is not proof of animation compatibility. Selection uses a stable unit proxy, not detailed prop collision. Team affiliation uses base rings/icons in addition to color, never a complete costume recolor.

**Specific production risk:** Cloud effects can obscure units. Keep opacity low, lifetime short and the gameplay ring more readable than the vapor.

Required source/export locations:

- blender: `art-source/heroes/wc_u_halfling_mage/wc_u_halfling_mage.blend`

- mesh_fbx: `exports/heroes/wc_u_halfling_mage/SK_wc_u_halfling_mage.fbx`

- unreal_folder: `/Game/WonderChess/Heroes/wc_u_halfling_mage`

- portrait: `exports/heroes/wc_u_halfling_mage/portrait.png`

Create separate animation exports and texture maps, a model-derived portrait, front/side/back/three-quarter views, a gameplay-camera screenshot, and an actual Unreal animation capture. Log source/export hashes, skeleton revision, tool versions and import preset. Deliberately change one costume detail, re-export and verify existing material, skeleton, animation and actor references survive.

## Model-sheet generation brief

Original Wonder Chess high-fantasy character production sheet for Milo Mistwhistle, The Weather Tinkerer. Halfling Mage, adult character, height 1.14 m. Front, true side, back and three-quarter views at matching scale, neutral A-pose plus one action pose. A round short travel coat, large upturned collar and a thick spiral-topped wand. A small rigid umbrella disk folded against the back adds a distinctive rounded shape. Warm tan skin, gray eyes, a small dark mustache and wavy brown hair. Clearly adult proportions and expression; no oversized infant features. Sky-blue raincoat, cream collar, copper belt buckle and dark boots. Sleeves are wide but stop at the wrists for clean hand animation. A thick spiral fantasy wand and a collapsed decorative umbrella disk. The disk is not a shield or movement device. Palette: Sky blue #77AFC2; cream #EAE0C7; copper #B78258; slate #566477. Flat neutral background, orthographic construction views, equipment inset, readable seams, non-graphic stylized fantasy. No copied franchise designs, text baked into textures, cinematic fog, invented extra limbs or altered gear between views. These are concept directions, not generated images.

## Approval gates

Silhouette passes at 96-pixel preview; costume agrees across all views; all seven clips reviewed; no required missing textures; no unexplained import scale compensation; effect matches declared reach and damage type; portrait agrees with the modeled hero; crowded-board test passes; source revision/reimport is demonstrated. A Python exit code alone does not approve the art.

Canonical source: `data/units.json`. Regenerate this dossier with `python tools/build_documents.py` after data edits. Do not hand-edit a stat table and leave the JSON unchanged.

---
# Sora Dawnscale — The Beacon Sentinel

**Dragonkin · Guardian · Defender · ALPHA**

Stable identity: `wc_u_dragonkin_guardian`. Cost: **3 gold**. Rarity label: **Rare**, separate from star level. Production and verification status is recorded separately in reports/implementation_state.json; this generated dossier does not certify an asset or build. All combat values are provisional prototype inputs.

Quick display name: **Sora**. Informational roles: Tank. Role tags provide no additional synergy.

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

### Beacon Shield

**Player tooltip:** Gains a strong shield for three seconds.

**Indonesian draft:** Memberikan perisai sementara kepada diri sendiri.

| Contract field | Value |
|---|---|
| Stable ability ID | `wc_a_dragonkin_guardian` |
| Effect / target selector | `shield` / `self` |
| One / two / three star magnitude | shield: 240 / 432 / 778 |
| Damage type | Not damaging |
| First-cast delay / cooldown | 2.5 s / 9 s |
| Windup / recovery | 0.35 s / 0.3 s |
| Effect duration | 3.0 s |
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

---
# Varek Prismshot — The Glasswing Archer

**Dragonkin · Ranger · Ranged damage · ALPHA**

Stable identity: `wc_u_dragonkin_ranger`. Cost: **2 gold**. Rarity label: **Uncommon**, separate from star level. Production and verification status is recorded separately in reports/implementation_state.json; this generated dossier does not certify an asset or build. All combat values are provisional prototype inputs.

Quick display name: **Varek**. Informational roles: Ranged. Role tags provide no additional synergy.

## Character and world

Varek crafts signal mirrors for Cindercrest’s mountain paths and developed an archer’s patience while aligning them. Tessa’s mechanical accuracy fascinates him, and their friendly demonstrations draw crowds in Brighthaven. He joins the trials to show that magical ranged combat can be precise rather than spectacularly noisy.

Home region: `cindercrest`. Affiliation: `skyward_conclave`. Neither supplies a hidden third synergy. Proper names are original proposed fiction, not trademark-clearance claims.

## Appearance and art direction

Authored standing height: **1.98 m**, excluding raised equipment. Rig family: `humanoid_draconic`. One logical tile at every star. All characters are adults, fully clothed and presented as non-graphic heroic fantasy.

### Silhouette and proportions

A long narrow torso with a broad prismatic bow and two short outward horn fins. A split short cloak creates a forked shape without actual wings.

### Face, hair and expression

Blue-gray scales, pale gold eyes and a short angular muzzle. Horn fins are blunt and clearly part of the head rather than a wearable crown.

### Costume construction

Dark blue fitted ranger coat, ivory shoulder panels, silver belt and practical boots. The cloak ends at the hips.

### Color palette

Blue gray #7996AC; deep blue #3F567A; ivory #E6DFC9; prism cyan #8BC9CA.

### Equipment and magical focus

A stylized bow with broad translucent-looking but opaque shaded crystal facets. Keep its central grip readable and its mechanics decorative.

### Three low-resolution identifiers

Prismatic horizontal bow, short horn fins and forked cloak.

### Materials and surface detail

Opaque faceted crystal shader, matte scale surface and soft cloth. Refraction is not required for the crystal look.

### Back and side-view constraints

Cloak panels suggest folded wings in outline only; no hidden wing rig or flight ability. A flat quiver sits between them.

## Combat statistics — without traits or temporary effects

| Property | One star | Two stars | Three stars |
|---|---:|---:|---:|
| Health | 720 | 1,296 | 2,332.8 |
| Basic attack damage | 56 | 100.8 | 181.44 |
| Attack delivery | ranged | ranged | ranged |
| Basic damage type | magic | magic | magic |
| Nominal attacks/second | 0.85 | 0.85 | 0.85 |
| Effective attacks/second at 20 Hz | 0.8333 | 0.8333 | 0.8333 |
| Range in tiles | 4 | 4 | 4 |
| Physical armor | 12 | 12 | 12 |
| Magic resistance | 25 | 25 | 25 |
| Movement tiles/second | 1.05 | 1.05 | 1.05 |

Nominal basic-attack DPS at one star: **47.60**, before mitigation, movement, stuns, skills, targeting downtime or timing quantization. Basic windup: 300 ms; ordinary projectile travel: 150 ms. No hidden critical hits, evasion, lifesteal or mana.

## One active skill

### Prism Shot

**Player tooltip:** Fires a stronger magic shot at the current target.

**Indonesian draft:** Memberikan kerusakan sihir kepada sasaran saat ini.

| Contract field | Value |
|---|---|
| Stable ability ID | `wc_a_dragonkin_ranger` |
| Effect / target selector | `damage` / `current_enemy` |
| One / two / three star magnitude | damage: 160 / 288 / 518 |
| Damage type | magic |
| First-cast delay / cooldown | 3 s / 7.5 s |
| Windup / recovery | 0.35 s / 0.3 s |
| Effect duration | 0.0 s |
| Skill reach / area radius | 4 / 0 tiles |
| Can include self | False |
| Max dash distance | 0 tiles |
| Projectile travel | 150 ms |
| Affected stat | Not applicable |

Cooldown starts at successful cast commitment. An interrupted committed cast keeps its cooldown; an unavailable target leaves the ability ready and allows ordinary behavior. Area centers and area recipients are captured at release. Targeted projectiles keep their target ID but never retarget a defeated unit. Dash landing is reserved at commitment and validated before movement. See the rules contract for same-tick ordering, shield replacement and refresh semantics.

Health and basic damage use 1.00/1.80/3.24 star multipliers. Only explicitly authored skill magnitudes vary with stars; stun duration, range, radius, dash distance, cooldown and model footprint do not grow. A status-only skill may deliberately have identical behavior across stars; its owner still gains health and basic damage.

## Positioning and counterplay

**Preferred formation.** Protected backline against opponents leaning heavily on physical armor.

**Useful partners.** Tessa or Liora activates Ranger; Oren activates Dragonkin.

**Counterplay.** High magic resistance reduces both his basics and his active; Rogues threaten his unprotected flank.

**Practical weakness.** No mobility and no area damage; cannot bypass resistance.

**Difference from the nearest alternative.** Tessa deals physical damage, while Varek’s basic and active shots deal magic damage.

**Character-specific acceptance test.** Ranger boosts his magic basic attacks but not Prism Shot; mitigation selects resistance rather than armor.

## Animation, effects and sound

Idle holds the bow low. Basics release pale magic arrows. The active rotates the bow slightly to align its facets, then fires one clear beamlike projectile with finite travel time.

**Skill effect:** One narrow cyan projectile and compact prismatic target sparkle. It does not pierce, chain or deal true damage.

**Sound:** A crystalline bow note and a short clean impact, mixed below large area spells.

Author at 60 FPS, as in-place animations with no locomotion-driven root translation. Required clips: Idle, Move, Attack, Active, Hit, Defeat, Victory. The active release marker is frame 21 relative to animation start. Basic release marker is frame 18. These are presentation alignment points, not sources of authoritative damage. Idle begins as a 2-second loop; movement as a 1-second cycle; hit as 0.4 seconds; defeat as 1 second; victory as 1.5 seconds. Adjust clip lengths during animation review without altering gameplay timing.

A defeat uses a brief stagger, kneel or magical dissolve with no injury detail. Stars use UI pips, a subtle trim accent and a brief upgrade flourish; do not produce three separate bodies or enlarge the collision footprint.

## Blender construction and Unreal handoff

Start from the `humanoid_draconic` base or a validated compatible family. Block silhouette before bevels; separate body, costume and equipment into named source collections. Build equipment as decorative fantasy game props, not real functional objects. Author model-space Z up and a consistent forward orientation, then prove conversion with the calibration fixture. Materials use one or two runtime slots and a shared atlas where it preserves identity.

Targets to profile: at most 15,000 LOD0 triangles, 1024-pixel default maps, up to 60 deforming bones and 4 influences per vertex. Lower-detail targets begin near 50% and 25% triangles. These are budgets, not measured performance.

Sockets: `weapon_r`, `weapon_l`, `cast_origin`, `head_ui`. Inspect shoulder, elbow, hip and knee extremes. Use separate rig proportions where needed; matching bone names is not proof of animation compatibility. Selection uses a stable unit proxy, not detailed prop collision. Team affiliation uses base rings/icons in addition to color, never a complete costume recolor.

**Specific production risk:** Crystal materials can become too bright against snowlike backgrounds. Keep dark facet planes and verify readability without bloom.

Required source/export locations:

- blender: `art-source/heroes/wc_u_dragonkin_ranger/wc_u_dragonkin_ranger.blend`

- mesh_fbx: `exports/heroes/wc_u_dragonkin_ranger/SK_wc_u_dragonkin_ranger.fbx`

- unreal_folder: `/Game/WonderChess/Heroes/wc_u_dragonkin_ranger`

- portrait: `exports/heroes/wc_u_dragonkin_ranger/portrait.png`

Create separate animation exports and texture maps, a model-derived portrait, front/side/back/three-quarter views, a gameplay-camera screenshot, and an actual Unreal animation capture. Log source/export hashes, skeleton revision, tool versions and import preset. Deliberately change one costume detail, re-export and verify existing material, skeleton, animation and actor references survive.

## Model-sheet generation brief

Original Wonder Chess high-fantasy character production sheet for Varek Prismshot, The Glasswing Archer. Dragonkin Ranger, adult character, height 1.98 m. Front, true side, back and three-quarter views at matching scale, neutral A-pose plus one action pose. A long narrow torso with a broad prismatic bow and two short outward horn fins. A split short cloak creates a forked shape without actual wings. Blue-gray scales, pale gold eyes and a short angular muzzle. Horn fins are blunt and clearly part of the head rather than a wearable crown. Dark blue fitted ranger coat, ivory shoulder panels, silver belt and practical boots. The cloak ends at the hips. A stylized bow with broad translucent-looking but opaque shaded crystal facets. Keep its central grip readable and its mechanics decorative. Palette: Blue gray #7996AC; deep blue #3F567A; ivory #E6DFC9; prism cyan #8BC9CA. Flat neutral background, orthographic construction views, equipment inset, readable seams, non-graphic stylized fantasy. No copied franchise designs, text baked into textures, cinematic fog, invented extra limbs or altered gear between views. These are concept directions, not generated images.

## Approval gates

Silhouette passes at 96-pixel preview; costume agrees across all views; all seven clips reviewed; no required missing textures; no unexplained import scale compensation; effect matches declared reach and damage type; portrait agrees with the modeled hero; crowded-board test passes; source revision/reimport is demonstrated. A Python exit code alone does not approve the art.

Canonical source: `data/units.json`. Regenerate this dossier with `python tools/build_documents.py` after data edits. Do not hand-edit a stat table and leave the JSON unchanged.

---
# Iri Cinderstep — The Quiet Spark

**Dragonkin · Rogue · Disruption · ALPHA**

Stable identity: `wc_u_dragonkin_rogue`. Cost: **3 gold**. Rarity label: **Rare**, separate from star level. Production and verification status is recorded separately in reports/implementation_state.json; this generated dossier does not certify an asset or build. All combat values are provisional prototype inputs.

Quick display name: **Iri**. Informational roles: Control. Role tags provide no additional synergy.

## Character and world

Iri repairs small ward stones along Cindercrest’s footpaths, work that rewards precision more than force. She initially found the public trials overwhelming, but Sora encouraged her to bring a quiet skill to a noisy event. Her friendship with Nella rests on a shared belief that one well-timed action can be more useful than a grand entrance.

Home region: `cindercrest`. Affiliation: `skyward_conclave`. Neither supplies a hidden third synergy. Proper names are original proposed fiction, not trademark-clearance claims.

## Appearance and art direction

Authored standing height: **1.89 m**, excluding raised equipment. Rig family: `humanoid_draconic`. One logical tile at every star. All characters are adults, fully clothed and presented as non-graphic heroic fantasy.

### Silhouette and proportions

A slim low stance with a short swept neck crest, one long diagonal sash and paired broad crescent fantasy blades. The outline stays compact rather than spiky.

### Face, hair and expression

Muted copper scales, dark violet eyes and a short soft-edged muzzle. Two small backward horns sit close to the skull.

### Costume construction

Charcoal traveling jacket with coral lining, short layered hip panels and light boots. Leave elbow and knee shapes visible for agile poses.

### Color palette

Copper #AF7C60; charcoal #454552; coral #CB7B6B; muted violet #837B9E.

### Equipment and magical focus

Paired fantasy crescent blades with small pale inset gems. The true-damage fantasy comes from a brief magical effect, not realistic cutting detail.

### Three low-resolution identifiers

Close neck crest, coral diagonal sash and paired crescents.

### Materials and surface detail

Matte scales, soft cloth and restrained metal. Keep gem glow off except during the active.

### Back and side-view constraints

The sash crosses a flat back panel; no tail or wings. Neck crest must clear the shoulder blades during crouches.

## Combat statistics — without traits or temporary effects

| Property | One star | Two stars | Three stars |
|---|---:|---:|---:|
| Health | 730 | 1,314 | 2,365.2 |
| Basic attack damage | 65 | 117 | 210.6 |
| Attack delivery | melee | melee | melee |
| Basic damage type | physical | physical | physical |
| Nominal attacks/second | 1.05 | 1.05 | 1.05 |
| Effective attacks/second at 20 Hz | 1.0000 | 1.0000 | 1.0000 |
| Range in tiles | 1 | 1 | 1 |
| Physical armor | 15 | 15 | 15 |
| Magic resistance | 20 | 20 | 20 |
| Movement tiles/second | 1.25 | 1.25 | 1.25 |

Nominal basic-attack DPS at one star: **68.25**, before mitigation, movement, stuns, skills, targeting downtime or timing quantization. Basic windup: 250 ms; ordinary projectile travel: 0 ms. No hidden critical hits, evasion, lifesteal or mana.

## One active skill

### Prism Cut

**Player tooltip:** Deals a small true-damage hit to the current target.

**Indonesian draft:** Memberikan kerusakan murni kepada sasaran saat ini.

| Contract field | Value |
|---|---|
| Stable ability ID | `wc_a_dragonkin_rogue` |
| Effect / target selector | `damage` / `current_enemy` |
| One / two / three star magnitude | damage: 100 / 180 / 324 |
| Damage type | true |
| First-cast delay / cooldown | 2.5 s / 8 s |
| Windup / recovery | 0.25 s / 0.3 s |
| Effect duration | 0.0 s |
| Skill reach / area radius | 1 / 0 tiles |
| Can include self | False |
| Max dash distance | 0 tiles |
| Projectile travel | 0 ms |
| Affected stat | Not applicable |

Cooldown starts at successful cast commitment. An interrupted committed cast keeps its cooldown; an unavailable target leaves the ability ready and allows ordinary behavior. Area centers and area recipients are captured at release. Targeted projectiles keep their target ID but never retarget a defeated unit. Dash landing is reserved at commitment and validated before movement. See the rules contract for same-tick ordering, shield replacement and refresh semantics.

Health and basic damage use 1.00/1.80/3.24 star multipliers. Only explicitly authored skill magnitudes vary with stars; stun duration, range, radius, dash distance, cooldown and model footprint do not grow. A status-only skill may deliberately have identical behavior across stars; its owner still gains health and basic damage.

## Positioning and counterplay

**Preferred formation.** Flank where she can reach a valuable durable target without taking the initial focus.

**Useful partners.** Sylas or Kesh enables Rogue; Sora provides protection and Dragonkin.

**Counterplay.** Shields still absorb Prism Cut, and her low health makes focused attacks effective.

**Practical weakness.** No dash and no area attack; true damage is small and does not bypass shields.

**Difference from the nearest alternative.** Other Rogues reposition or stun; Iri offers a narrow anti-defense damage tool only in the expansion.

**Character-specific acceptance test.** True damage bypasses armor/resistance, still applies permitted source bonuses once and is absorbed by shields first.

## Animation, effects and sound

Idle is still and balanced. Basics are compact alternating attacks. Prism Cut draws one crescent inward, pauses for a readable glint and releases a short deliberate gesture.

**Skill effect:** A thin white-violet impact mark and the ordinary damage number with a distinct true-damage icon. No injury detail, teleport or invulnerability.

**Sound:** A clean bright note with a soft impact tick; avoid harsh scraping sounds.

Author at 60 FPS, as in-place animations with no locomotion-driven root translation. Required clips: Idle, Move, Attack, Active, Hit, Defeat, Victory. The active release marker is frame 15 relative to animation start. Basic release marker is frame 15. These are presentation alignment points, not sources of authoritative damage. Idle begins as a 2-second loop; movement as a 1-second cycle; hit as 0.4 seconds; defeat as 1 second; victory as 1.5 seconds. Adjust clip lengths during animation review without altering gameplay timing.

A defeat uses a brief stagger, kneel or magical dissolve with no injury detail. Stars use UI pips, a subtle trim accent and a brief upgrade flourish; do not produce three separate bodies or enlarge the collision footprint.

## Blender construction and Unreal handoff

Start from the `humanoid_draconic` base or a validated compatible family. Block silhouette before bevels; separate body, costume and equipment into named source collections. Build equipment as decorative fantasy game props, not real functional objects. Author model-space Z up and a consistent forward orientation, then prove conversion with the calibration fixture. Materials use one or two runtime slots and a shared atlas where it preserves identity.

Targets to profile: at most 15,000 LOD0 triangles, 1024-pixel default maps, up to 60 deforming bones and 4 influences per vertex. Lower-detail targets begin near 50% and 25% triangles. These are budgets, not measured performance.

Sockets: `weapon_r`, `weapon_l`, `cast_origin`, `head_ui`. Inspect shoulder, elbow, hip and knee extremes. Use separate rig proportions where needed; matching bone names is not proof of animation compatibility. Selection uses a stable unit proxy, not detailed prop collision. Team affiliation uses base rings/icons in addition to color, never a complete costume recolor.

**Specific production risk:** True damage can erase defensive choices if overtuned. Its magnitude is deliberately lower than same-tier physical or magic skills and belongs only to expansion.

Required source/export locations:

- blender: `art-source/heroes/wc_u_dragonkin_rogue/wc_u_dragonkin_rogue.blend`

- mesh_fbx: `exports/heroes/wc_u_dragonkin_rogue/SK_wc_u_dragonkin_rogue.fbx`

- unreal_folder: `/Game/WonderChess/Heroes/wc_u_dragonkin_rogue`

- portrait: `exports/heroes/wc_u_dragonkin_rogue/portrait.png`

Create separate animation exports and texture maps, a model-derived portrait, front/side/back/three-quarter views, a gameplay-camera screenshot, and an actual Unreal animation capture. Log source/export hashes, skeleton revision, tool versions and import preset. Deliberately change one costume detail, re-export and verify existing material, skeleton, animation and actor references survive.

## Model-sheet generation brief

Original Wonder Chess high-fantasy character production sheet for Iri Cinderstep, The Quiet Spark. Dragonkin Rogue, adult character, height 1.89 m. Front, true side, back and three-quarter views at matching scale, neutral A-pose plus one action pose. A slim low stance with a short swept neck crest, one long diagonal sash and paired broad crescent fantasy blades. The outline stays compact rather than spiky. Muted copper scales, dark violet eyes and a short soft-edged muzzle. Two small backward horns sit close to the skull. Charcoal traveling jacket with coral lining, short layered hip panels and light boots. Leave elbow and knee shapes visible for agile poses. Paired fantasy crescent blades with small pale inset gems. The true-damage fantasy comes from a brief magical effect, not realistic cutting detail. Palette: Copper #AF7C60; charcoal #454552; coral #CB7B6B; muted violet #837B9E. Flat neutral background, orthographic construction views, equipment inset, readable seams, non-graphic stylized fantasy. No copied franchise designs, text baked into textures, cinematic fog, invented extra limbs or altered gear between views. These are concept directions, not generated images.

## Approval gates

Silhouette passes at 96-pixel preview; costume agrees across all views; all seven clips reviewed; no required missing textures; no unexplained import scale compensation; effect matches declared reach and damage type; portrait agrees with the modeled hero; crowded-board test passes; source revision/reimport is demonstrated. A Python exit code alone does not approve the art.

Canonical source: `data/units.json`. Regenerate this dossier with `python tools/build_documents.py` after data edits. Do not hand-edit a stat table and leave the JSON unchanged.

---
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

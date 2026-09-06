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

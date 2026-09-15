# Named 2D content specification — planning appendix

**Status: SPEC_ONLY_NOT_PRODUCED.** This file specifies future work. It does not produce or approve art, enable a hero or trait, change tuning, import Unreal content, or authorize a bulk generation batch. All suggested artwork motifs below are proposals.

This appendix preserves the existing **3D heroes and 3D Wondergrove board**. Its 2D deliverables are portraits, illustration plates, glyphs and overlays. Hero spritesheets, Spine replacement rigs and a flat tilemap conversion are not part of this plan. The game has an **8×8 board, ten-slot bench, five-card shop, twelve gameplay relics, three relics equipped per team and one per hero**. There is no approved component-item or combined-item crafting system.

The master plan owns the UI kit, arena textures/decals, VFX sheets, screens and integration specification. This appendix owns the named content subjects only. Numeric combat values continue to come from the canonical catalogue and generated runtime views; none are republished as a separate art balance table.

## Source and acceptance boundaries

- [Canonical successor catalogue](../../../data/vnext/catalog.json) owns identity, enabled status, mechanics, tuning and membership.
- [Generated hero dossiers](../generated/hero_dossiers.md) and [relic catalogue](../generated/relic_catalogue.md) are derived views, never independent authoring inputs.
- [Product and combat contract](../PRODUCT_AND_COMBAT.md) owns gameplay scope; [art/UI production contract](../ART_UI_PRODUCTION.md) owns the existing 3D art pipeline.
- Consult each active asset manifest and milestone record for current approved reference/forms state. The raw catalogue art field is not a substitute for later evidence; Bellback reference approval must be preserved.
- REF01 materials, REF02 layout, REF03 icon/portrait and REF04 FX boards are **unapproved style references only**. Generic objects in REF03 do not add new relics, items or lore.
- Before producing any portrait: accept the identity reference, small silhouette and crop; inspect consistency with approved anatomy. New generated details cannot silently overwrite reference decisions.

## Deliverable contract and counts

| Group | Logical masters | Master specification | Runtime size variants per master |
|---|---:|---|---|
| Hero portraits | 14 | 1024×1024 layered illustration | 512, 256, 128 square |
| Hero ability icons | 14 | 512×512 layered illustration | 128, 64, 32 square |
| Hero silhouettes | 14 | Editable vector; 256×256 reference canvas | 128, 64, 32 square |
| Optional full bestiary plates, deferred | 14 | 1536×2048 layered illustration | 768×1024 |
| Trait identity glyphs | 18 | Editable vector; 512×512 reference canvas | 128, 64, 32 square |
| Relic icons | 12 | 512×512 layered illustration | 256, 128, 64 square |
| Neutral portraits | 7 | 1024×1024 layered illustration | 256, 128, 64 square |
| Neutral silhouettes | 7 | Editable vector; 256×256 reference canvas | 128, 64, 32 square |

**100 logical masters; 272 derived runtime size exports.** These totals include all deferred/future rows. Interaction states are composed from the same art plus UI treatments; they do not multiply the illustration count. Vector sources, layer files, proof sheets and grayscale checks are production deliverables rather than extra unique illustrations. The machine-readable manifest is [2D_CONTENT_INVENTORY.json](2D_CONTENT_INVENTORY.json).

Priority counts: **P1current: 44**, **P2pilot: 3**, **P3future: 53**. P1current still waits for art acceptance. P2pilot is an optional illustration dependency, not automatic promotion of a gameplay hero. P3future is not a bulk-production instruction.

Portrait framing: preserve the strongest silhouette break, keep eyes/head or equivalent identity focus inside a crop-safe area, and leave enough breathing room for square/rounded card masks. Keep background separable and low contrast. Do not bake names, prices, stars, team colors, status, mana or borders into illustration pixels. Ship small-size derivatives from an approved master; retouch where reducing detail is necessary rather than trusting an automatic downscale.

Ability icons: one dominant object or geometric action and a small secondary cue. Paint the hero-specific skill identity, not the activation resource. Range, current mana and readiness remain separate runtime UI. Silhouettes: one outer shape plus a few essential cutouts; no tiny texture detail. Full bestiary plates remain deferred until model/forms approval so a lavish illustration cannot lock an unbuildable or contradictory design.

## Current six heroes

Each current hero requires portrait, skill icon and silhouette in P1current. “Melee” and “ranged” below describe the current basic attack; exact reach and timing are read from runtime. Optional full-body bestiary plates are later work.

| Hero / identity | Current behavior boundary | Proposed portrait and icon directions |
|---|---|---|
| **Bellback** `wc_vn_bellback`; Beast / Guardian | Melee basic; **Sheltering Bell**. Passive guard; do not imply a mana cast or an ordinary group shield. | Portrait: Broad moss-covered quadruped profile, dorsal bronze bell suspended in a wooden mount, protected space behind its shoulder; preserve the separately approved construction packet anatomy. Icon: Suspended bell above a short directional bronze guard arc and one sheltered ally point. |
| **Cragstoat** `wc_vn_cragstoat`; Beast / Warrior | Melee basic; **Stonebound Lunge**. Movement-earned momentum plus a committed charge; retain the current control activation path. | Portrait: Long low predator, rocklike shoulder ridges, lifted expressive tail and compressed springlike spine; keep the head and ridge silhouette readable. Icon: Low stone-ridged lunge silhouette crossing successive footfall sparks toward one landing marker. |
| **Grandmother Root** `wc_vn_grandmother_root`; Plant / Healer | Ranged basic; **Stay and Blossom**. Stationary establishment and effective healing pulses; do not imply immediate team-wide healing or mandatory mana charging. | Portrait: Broad rooted orchard elder with a sheltered garden clearly visible within the torso; three broad foliage masses, quiet warm face, deep root silhouette. Icon: Opening blossom above planted roots inside a clearly bounded patch of ground. |
| **Snapvine** `wc_vn_snapvine`; Plant / Assassin | Ranged basic; **Thornline**. Thornline strikes the first intersected enemy; mana activation exists only in the selectable experiment. | Portrait: Low creeping flower with folded outer petals revealing a single readable thorn-lined jaw; asymmetric hooked root and compact predatory pose. Icon: A thorn jaw ending a thin straight root lane with one intervening impact point. |
| **Prism Organ** `wc_vn_prism_organ`; Construct / Mage | Ranged basic; **Crossing Hymn**. Crossing Hymn releases row then column at separate authoritative times; mana is an experimental activation variant. | Portrait: Floating ceramic organ-pipe assembly around a stained-glass resonator; preserve large gaps between pipes and one luminous central aperture. Icon: One ceramic resonator at the intersection of unequal ordered row and column beams. |
| **Reefglass** `wc_vn_reefglass`; Tidekin / Controller | Ranged basic; **Leading Tide**. Leading Tide damages a directional lane and conditionally pushes its first enemy; show displacement only when it actually occurs. | Portrait: Glass-shelled cuttlefish with one clear interior current, ribbonlike fins and a readable forward cup silhouette; translucency does not erase the body edge. Icon: Cupped glass fin shaping a narrow crest and a separate displacement arrow. |

The selectable mana experiment applies to Snapvine, Prism Organ and Reefglass. Bellback, Cragstoat and Root remain their existing controls. A static portrait/icon cannot decide which activation rule is active. Show passive/conditional, timed and mana badges from the selected definition and explain Root’s stationary requirement and Cragstoat’s momentum in contextual UI.

## Eight authored future heroes

**All eight remain disabled and have no executable ability or stats.** Proposed skill symbols below are conceptual behavior identities, not official final skill names. They receive P3future portrait/icon/silhouette rows. Thimblewake is an AS1 art pilot; that does not make it recruitable.

| Hero / identity | Canonical design idea and proposed artwork |
|---|---|
| **Silkmother** `wc_vn_silkmother`; Insect / Engineer | Portrait: Eight-legged silk architect carrying one large warm lantern abdomen; reserve negative space under the legs and keep threads sparse. Icon: Two lantern stakes joined by one taut silk span. Boundary: Authored future trip line between destructible anchors; no executed ability or final skill name. |
| **Manyfoot** `wc_vn_manyfoot`; Insect / Warrior | Portrait: One banner-shaped iridescent shell carried by a coordinated beetle colony; read as one selectable creature, not a team of independent summons. Icon: One continuous shell outline dividing around a blocker and rejoining behind it. Boundary: Authored future shared-identity flank and re-form behavior; no executed ability or final skill name. |
| **Kilnback** `wc_vn_kilnback`; Construct / Guardian | Portrait: Squat glazed furnace-tortoise with broad hinged plates, a few readable kiln windows and one steam vent. Icon: Frontal projectile entering a lit kiln window with a separate outward vent plume. Boundary: Authored future bounded projectile capture then steam vent; no executed ability or final skill name. |
| **Coilwyrm** `wc_vn_coilwyrm`; Dragon / Controller | Portrait: Branch-antlered dragon forming a broad coil around a suspended pearl; the open center remains the strongest silhouette break. Icon: A pearl centered in an incomplete constricting ring with an unmistakably empty safe center. Boundary: Authored future delayed constricting ring; do not imply full-disc damage or executed mechanics. |
| **Dawnkite** `wc_vn_dawnkite`; Dragon / Ranger | Portrait: Broad dragon wings with ordered layers of dawn-colored membrane and a forked tail; keep the fan span dominant. Icon: Three layered wing wedges opening across a single fan sector. Boundary: Authored future committed fan sweep; no executed ability or final skill name. |
| **Thimblewake** `wc_vn_thimblewake`; Fae / Duelist | Portrait: Flower-mantis noble, petal armor collar, needlelike forearms and an elegant upright asymmetric stance; retain articulated insect anatomy. Icon: Two closing petals framing one needle parry and a short returning stroke. Boundary: Authored future isolated challenge, parry and riposte; AS1 art pilot does not make this hero recruitable. |
| **Wren** `wc_vn_wren`; Human / Engineer | Portrait: Practical itinerant tinkerer beside a small walking repair cart; keep one clear cart canopy/leg cue rather than a crowded miniature workshop. Icon: Small unfolding repair canopy with one visible pulse traveling toward an ally point. Boundary: Authored future destructible repair station; no executed ability or final skill name. |
| **Hushlantern** `wc_vn_hushlantern`; Spirit / Healer | Portrait: Empty rain cloak framing a single lantern instead of a head, with only two or three diminishing firefly echoes. Icon: A descending lantern bead linked to a faint prior-health echo. Boundary: Authored future capped restoration of recent lost health after a delay; never depict resurrection. |

## All eighteen trait glyphs

These names and behaviors are authored; **every current behavioral trait is runtime disabled**. Identity display may be prepared, but progress/active visual treatments are reserved for a future supported runtime. A planned badge must distinguish development content from a functioning bonus. No threshold numbers are baked into glyphs.

| Kind / source identity | Canonical behavior label | Proposed glyph |
|---|---|---|
| Race / `beast` | **Pack momentum** | Heavy paw over one forward motion notch. |
| Race / `plant` | **Established ground** | Rooted sprout within a square ground boundary. |
| Race / `insect` | **Colony routes** | Three linked beetle-wing or colony forms with one route through them. |
| Race / `construct` | **Stored energy** | Glazed vessel enclosing a contained charge core. |
| Race / `human` | **Ingenuity** | Small practical tool beside an incomplete lantern gear. |
| Race / `tidekin` | **Changing currents** | Curled directional current passing through a shell aperture. |
| Race / `fae` | **Unshared attention** | Single petal eye within an isolated crescent. |
| Race / `spirit` | **Echo memory** | Lantern followed by two diminishing echo forms. |
| Race / `dragon` | **Committed majesty** | Branch-horned profile circling one pearl. |
| Class / `guardian` | **Held line** | Shield arch with one sheltered point behind it. |
| Class / `warrior` | **Sustained pressure** | Heavy wedge pressing into three close impact bars. |
| Class / `duelist` | **Single challenge** | Single needle blade framed by two challenge petals. |
| Class / `ranger` | **Clear firing lanes** | Straight arrow through two parallel open lane guides. |
| Class / `mage` | **Prepared magic** | Orderly resonator held within a few casting facets. |
| Class / `healer` | **Care network** | Open leaf cup connecting two living buds. |
| Class / `controller` | **Follow through** | Offset square with one follow-through arrow. |
| Class / `engineer` | **Service radius** | Small workshop canopy inside a service boundary. |
| Class / `assassin` | **Open approach** | Thorn passing through a broken screening line. |

Each glyph uses the same optical weight, quiet outer mask and minimum internal gap. Race and class frames may differ, but the central glyph must remain identifiable without the frame. Provide base glyph, with future planned/inactive/progress/active/focused states composed by UI. Review all eighteen together at 32 pixels and in grayscale; do not solve near-duplicates by color alone.

## All twelve relic illustrations

These are current runtime-enabled **candidate relic designs**, not finished accepted balance. Exact compatibility and transformations come from the generated relic catalogue. Timing relics modify mana gain inversely in mana variants, so art must suggest timing without baking an incorrect cooldown sentence.

| Relic / stable source ID | Current mechanic description | Proposed distinct icon |
|---|---|---|
| **Heavy Bloom** `wc_vn_r_heavy_bloom` | Greater ability impact after a longer visible commitment. | Dense downward-bending bronze flower carrying one heavy luminous seed. |
| **Quick Wick** `wc_vn_r_quick_wick` | More frequent abilities with weaker individual effects. | Short forked exposed wick with two brisk compact flames; no lantern housing. |
| **Long Lens** `wc_vn_r_long_lens` | One extra cell of reach, with lower impact. | Long narrow brass telescope aimed at a small distant star. |
| **Broad Canopy** `wc_vn_r_broad_canopy` | A wider supported area with less concentrated potency. | Wide shallow leaf canopy sheltering three spaced drops. |
| **Close Focus** `wc_vn_r_close_focus` | A stronger commitment restricted to a shorter lane. | Thick near-field loupe concentrating a bright point immediately beneath it. |
| **Tight Choir** `wc_vn_r_tight_choir` | Concentrate power into a smaller area. | Three close ceramic pipes tied together with dark thread. |
| **Silk Trigger** `wc_vn_r_silk_trigger` | Release much sooner with reduced damage. | Taut white silk crossing a tiny bronze release catch in a diagonal snap composition. |
| **Patient Lantern** `wc_vn_r_patient_lantern` | Stronger effects separated by longer gaps. | Broad enclosed hanging lantern with a deep steady amber core. |
| **Far Hourglass** `wc_vn_r_far_hourglass` | Reach farther but wait longer between casts. | Tall narrow hourglass with sighting fins extended along its long axis. |
| **Wide Hourglass** `wc_vn_r_wide_hourglass` | Cover a wider area with less frequent activations. | Squat broad hourglass with a wide horizontal circular rim. |
| **Narrow Metronome** `wc_vn_r_narrow_metronome` | Repeat a smaller area effect more frequently. | Tall tapered wooden metronome with a deliberately narrow tick arc. |
| **Urgent Shard** `wc_vn_r_urgent_shard` | Commit faster now at the cost of a longer following cooldown. | Angular glass shard with a sudden bright leading flash and a long trailing ember. |

Relic icon art remains unchanged across offered, selected, equipped, compatible, incompatible and disabled states. Add these states using separate frame/marker/opacity treatments and runtime text. Provide icon-only views for inventory and the selected hero, plus larger offer-card placement. Long Lens/Close Focus, Far Hourglass/Wide Hourglass and Quick Wick/Patient Lantern must differ by outer shape and orientation, not just palette. Generic reference-board relic objects are composition examples only.

## Seven original neutral identities

All seven execute **basic combat only**; canonical ability is empty. Their following visual motifs are proposed and require original identity acceptance. Portraits and silhouettes support wave previews, recap and bestiary; no new boss skill is implied.

| Neutral / stable ID | Current attack type | Proposed original form |
|---|---|---|
| **Skittering Seedpod** `wc_vn_n_seedpod` | Melee basic | Compact seed husk above a skittering leg silhouette. |
| **Reed Archer** `wc_vn_n_reed_archer` | Ranged basic | Tall split reed bow-stalk and one unmistakably narrow firing profile. |
| **Lantern Bulb** `wc_vn_n_lantern_bulb` | Ranged basic | Round glowing botanical bulb over a small grounded root base. |
| **Slate Ram** `wc_vn_n_slate_ram` | Melee basic | Broad stone horn mass over a low durable quadruped silhouette. |
| **Glass Moth** `wc_vn_n_glass_moth` | Ranged basic | Two translucent wing lobes around a narrow central body; preserve the outer edge. |
| **Root Sentinel** `wc_vn_n_root_sentinel` | Melee basic | Upright root-and-stone guarding mass on broad feet. |
| **Hollow Bellkeeper** `wc_vn_n_hollow_bellkeeper` | Ranged basic | Hollow bell-shaped body or hood framing an empty interior silhouette. |

## Stars and independent presentation states

Shared star-tier overlays and activation badges belong to the UI inventory. They are dependencies only here, with no duplicated content master or export count.

- **One identity master per hero**, overlaid with one, two or three separated star pips. Do not create three repaint sets, confuse cost with stars, or remove team identification when upgrading.
- Future model tier accents may add approved secondary ornament or restrained effects after model acceptance; preserve silhouette, sockets, occupancy and combat readability. This appendix does not authorize new geometry or skins.
- Health/mana bars, team indicators, selected/focused state, stun/shield/heal status, disabled cards and cost frames are independent UI/VFX layers defined in the master plan. An illustration must remain valid with all of them off.
- Effective heal, active shield and actual stun visuals must be driven by authoritative events/state. Freeze, silence, summons and resurrection must not be invented to fill an art checklist.

## 3D motion dependency — not a spritesheet request

For each accepted hero model, plan the following motion coverage in the existing skeletal/assembly pipeline. A 2D pose sheet can explain the motion, but cannot satisfy a rig, animation, imported clip or packaged-motion gate.

| Motion requirement | Required behavior and review |
|---|---|
| Bench/preparation idle | Breathing or family-appropriate resting motion, one quiet variation, readable facing and low persistent movement. |
| Locomotion | Start, steady movement and stop; correct contacts, grounded weight or explicit floating motion; no foot sliding. |
| Turning | Smooth facing changes, including target reacquisition, without moving the authoritative cell. |
| Basic attack | Anticipation, authoritative release/contact, recovery and optional equivalent-timing variation. Each creature attacks independently. |
| Ranged release | Correct projectile socket and direction, clear source identity; projectile and hit timing remain combat-owned. |
| Ability | Hero-specific setup, committed telegraph, release and recovery; repeated casts and interruption tested. Bellback passive guard and Root establishment need distinct non-cast motion logic. |
| Hit reaction | Brief response that does not misleadingly interrupt every basic attack or create a new stun; damage authority unchanged. |
| Stun/interruption | Visible pose/state response plus overhead status grammar, accurate start and expiry; no repeated reset that suggests extra duration. |
| Displacement/charge | Start/travel/landing or recovery; preserve actual path and distinguish ordinary locomotion, push and Cragstoat charge. |
| Defeat/dissolve | Clear defeat, controlled departure and cleanup; source defeat after a released packet cannot cancel valid packet effects. |
| Upgrade transition | Shared tier effect linked to completed merge, then return to correct idle; no permanent uncontrolled glare. |
| Selection/bestiary | Optional greeting/inspect pose only after core motion is accepted; never interfere with normal combat. |
| Blends and extremes | Minimum/maximum attack rate, rapid target changes, stun during setup, simultaneous effects, repeated heals, late defeat and reset. |

Review continuous normal-speed motion before slow motion. Check contacts, hovering props, tail/wing clipping, sockets, scale, culling and abrupt blends. The initial method proofs remain Bellback grounded quadruped, Prism Organ floating assembly and Thimblewake articulated insect. Audio contacts/cast/reaction cues are separate dependencies even where the 2D specification does not count them.

## Production handoff and acceptance

1. Confirm the exact source identity and current gameplay/art status; preserve all earlier approved reference anatomy.
2. Accept the style-reference packet independently. REF01–REF04 remain reference candidates until reviewed; they are not runtime sprite atlases.
3. Approve each subject’s small silhouette and portrait crop before spending effort on final texture/detail. Resolve contradictions against the model and dossier.
4. Produce a layered master in its assigned method, with source provenance, revision and reference list. Export only required sizes with suitable transparent or separable backgrounds.
5. Inspect 32/64/128-pixel views, grayscale, dark/light panel contrast and small text adjacency. Pairwise-test the lens, hourglass and lantern families.
6. Compose states in the interface with runtime text; check English/Indonesian and scaled text without repainting illustrations.
7. Import into the designated candidate lane, record source/export identity and inspect the packaged view. File count and generator completion do not establish visual acceptance.

No production assets were generated by this appendix. Future implementation must record authored, generated, viewed, integrated, technically verified and human-accepted states separately.

# Wonder Chess 2D UI, environment-surface and VFX specification

Status: **SPEC_ONLY_NOT_PRODUCED**. Prepared 2026-09-13. This is a planning appendix, not a production manifest or evidence of an imported/accepted interface. No actual game assets, gameplay code, canonical balance data, release approval or art-stage approval are created by this document.

The companion [machine-readable inventory](2D_UI_ENV_VFX_INVENTORY.json) is the exhaustive record list. The master plan and reference packet own the overall generation order. REF01 materials/style, REF02 layout, REF03 portraits and REF04 effects are **reference candidates only, not approved production assets**.

## Scope and evidence boundary

The successor remains a hybrid 3D Unreal game. Heroes need approved 3D forms, rigs and skeletal animation; Wondergrove remains a modular 3D carved-stone platform within sanctuary roots. Its 2D work comprises surface textures, decals, portraits/icons, UI and selected particle components. A flat illustrated board or complete 2D hero sprite pipeline would be a new product decision.

This appendix does not commission hero idle/run/attack/cast/hurt/death sprite sheets or Spine packs. Those motions remain in the 3D animation work. A cast icon or slash texture does not replace animation anticipation/contact/recovery. Stars use explicit count/shape badges first; three portrait palette swaps or skins per hero are not required.

Canonical successor constraints:

- 8 by 8 encounter board, four preparation rows per side, eight seats.
- Ten-slot bench, five independent shop offers, five costs.
- Three equal copies merge; three star tiers. Price/stat/name text remains source-bound.
- Twelve current relic designs, three draft choices, up to three equipped per team and one per hero. No component crafting, recipe grid or combination-item inventory.
- Six executable successor heroes. Broader candidate roster and trait behavior are not equivalent to shipped content.
- Preparation decisions and automatic combat; telegraphs explain commitments rather than request manual dodging.

Inspected authority: [ART_UI_PRODUCTION.md](../ART_UI_PRODUCTION.md), [PRODUCT_AND_COMBAT.md](../PRODUCT_AND_COMBAT.md), the successor catalog, and WCVNextLab / WCVNextSolo / WCVNextCombatPresentation C++.

The current solo interface is native Slate text buttons, dynamic values, shop/bench/relic/scouting handlers and recap, not an illustrated finished UI kit. Current HP/mana bars and labels are mesh/text based. The combat cues are pooled meshes/text bound to real events. Presentational replacements must preserve that authority. Trait bonuses are explicitly inactive in the current study candidate. A status demonstration can exercise stun/shield/modifiers without giving those effects to the ordinary six hero kits.

The current Move command can swap an occupied destination; the inventory's swap-destination state reflects that existing behavior. It does not invent a separate Swap action or claim an unsupported feature.

## Inventory and counting

| Measure | Count |
|---|---:|
| Specification records | 263 |
| Logical non-screen masters / reusable families | 244 |
| Screen compositions reusing the kit | 19 |
| P1 first integrated slice records | 38 |
| P2 complete current presentation / required frontend records | 199 |
| P3 future-gated records | 26 |
| Vector-authored records | 145 |
| Shader/runtime records | 73 |
| Generator illustration records | 22 |
| Derived technical-map families | 4 |
| Composed screen records | 19 |

These are planning counts, not an estimate of finished image count or effort. A button record contains several required states. A technical-map family may contain multiple texture channels. A particle sheet contains several frames. Ten bench instances reuse one slot master. Screen rows are not full-screen image-generation jobs. Hero portraits, abilities, race/class icons and relic illustrations are counted in the separate content appendix, not duplicated here.

P1 means a bounded first slice after reference acceptance, not authorization to start mass production. P2 includes required finished frontend flows that are not all implemented yet. P3 stays invisible or explicitly labeled in development views until its corresponding mechanic/feature exists. Every JSON row retains a runtime_basis field to separate those cases.

## Visual grammar

Use mythic-storybook field-guide surfaces: deliberate broad shapes, carved stone, restrained weathered bronze, ink-like framing, painterly value groups and selected translucent magic. Place texture richness at panel corners and arena periphery. Keep central cells, text wells, numerical areas and portrait crop boundaries quiet.

Essential meaning survives grayscale, color-vision variation and reduced effects:

- Directional slash and contact mark means melee; traveling core/trail means ranged.
- Plus and actual restored amount means healing; a blue rim/shell means an active shield.
- Overhead swirl and orbiting stars means actual stun.
- Chevron shape signals a modifier direction; displacement shows a real changed position.
- Dashed/light preparation preview differs from committed/released stronger feedback.
- Legal/illegal destinations use checks, cross/hatching or border treatment as well as color.
- Team identity, cost tier, selected target and active protection use different shape roles.
- Ordinary locomotion dust must not look like a charge; a wave damage hit must not falsely announce a push.

REF01 demonstrates materials and restraint. REF02 demonstrates hierarchy and board clearance. REF03 demonstrates portrait cropping and identity. REF04 demonstrates effect shape, phase and restraint. Each reference should include the negative cases it rejects: noisy centers, unreadable microdetail, baked labels, excessive bloom, flat neon mobile-game chrome and effects that hide hero silhouettes.

## UI masters and state coverage

The JSON enumerates six panel types; four button templates; text/search/dropdown/number fields; checkbox/toggle/slider/scrollbar; separators/corners/shadow/tooltip pointer; a unit card; five cost treatments; portrait mask; card overlays; bench/relic slots; relic card; seven bars; three star badges; standings and match markers; and the full semantic glyph set.

Panel/frame surfaces are reusable nine-slice masters. Do not bake the whole shop, all five card offers, ten bench slots or an entire HUD into a bitmap. Native layout composes the pieces and native text supplies all names, values, countdowns, explanations and translations.

Button state contract: default, hover, pressed, keyboard focus, disabled and selected/toggled. Focus can coexist with hover or selected. Disabled does not equal low contrast to the point of illegibility. Rejection has a concrete reason and preserves useful selection.

Card state contract: available, hover/focus, selected, unaffordable, purchased, locked, exact-owned-copy count and immediate merge opportunity. Cost is a five-tier source category; common/rare/legendary naming is not adopted by this document. One card master and badge geometry serve all five tiers.

Bench state contract: empty, occupied, selected, legal move, legal swap, full and phase-locked. The ten-slot structure is responsive. Relic state contract: empty/owned/equipped, compatible/incompatible, no hero selected, equipped elsewhere where relevant and future-use label. No crafting or item-combination state is introduced.

HUD components cover captain health, gold, XP/level, deployment count/capacity, round/phase/clock, opponent, eight standings entries, ready/own/scouted/eliminated/ghost seat identity, health/mana/shield bars, stars and selected-hero facts. Floating mana only appears for an actual mana user. Scouting has a persistent return-to-own-board affordance and never exposes private shops, benches or relic offers.

Glyphs are semantically identified, not decorative miniature posters. Economy, stats, actions, navigation, laboratory, statuses and lifecycle errors each have explicit JSON rows. A glyph needs a textual accessible name. Future glyphs for silence/freeze/taunt/untargetable/revive/summons/constructions/transformation and online recovery are reserved design work, not new kit abilities.

## Wondergrove texture/decal pack

Four quiet stone-albedo variants support one excellent board. One bark, bronze and moss material family dresses roots/edging/perimeter. Each material family gets independently derived technical channels after approved source, not AI-invented normal/roughness claims. A surround illustration is concept or reviewed distant backdrop only; it cannot substitute for geometry, lighting, collision, camera bounds or measurable performance.

The overlay pack provides cell outline, hover, selected, valid/invalid, occupied/swap, keyboard focus, deployment boundary, facing arrow, path straight/corner/end, target ring/link, directional guard sector, lane, square area fill/boundary, cross and radius preview, plus own/opponent boundary. One bench surface is instanced for ten slots.

World geometry supplies true cells, range and path. Textures supply the edge/fill pattern. A square Chebyshev area stays a square clipped to the board; a decorative source ring must not be mistaken for the ability boundary. A directional line shows the actual selected facing. Side B preview transforms must match the board's row/column rotation.

## Six-hero effect suites

| Hero | Components | Required truthfulness |
|---|---|---|
| Bellback | Guard preview, supported-ally link, bronze interception/bell flare | Actual eligible protection and prevented damage, not a generic team-wide shield. |
| Cragstoat | Charge aim, momentum cue, charge trail, charge contact | Momentum from real completed movement; legal committed landing. A basic walk is visually separate. |
| Grandmother Root | Establishment, exact grove boundary, active pulse, recipient heal, break/expiry | Establishment interrupted by actual state; effective healing only for living eligible recipients who recover health. |
| Snapvine | Dotted aim, lash, first-hit impact, seed-like basic projectile | First intersected enemy; no depiction of multiple-target piercing unless the mechanic changes. |
| Prism Organ | Cross lock, row beam, column beam, crystalline impact, crystal basic projectile | Separate row/column authoritative releases and exact committed cells. |
| Reefglass | Cardinal lane, crest, spray impact, actual push trail, blocked-push contact, cyan basic projectile | Damage and actual displacement remain distinguishable; no PUSH label on a stationary recipient. |

Shared effects comprise melee windup/slash/contact, ranged head/trail/release/impact, locomotion dust, stun swirl, active shield, positive/negative modifier, effective-heal plus and optional native damage-number stacking.

Lifecycle effects cover actual three-copy gathering, star reveal, defeat dissolve, encounter cleanup and final victory/defeat. Future ground hazards, summons, constructions, transformations, silence, freeze, cleanse and revive stay P3 and require corresponding gameplay/ownership/expiry contracts.

The first slice should integrate one representative projectile/impact, melee slash, health/mana bars, healing and stun, then validate a busy six-hero fight. Each full hero suite follows its identity approval. Current readable proxy cues remain the comparison; a prettier effect that hides timing is a regression.

## Screen compositions and forgotten cases

Each of the 19 screen records composes shared components. Distinct screens do not justify commissioning 19 flattened illustrations.

| Composition | Coverage |
|---|---|
| Title and setup | Main menu, solo/learning/settings/exit, new/resume, existing-save choice. |
| Loading | Actual loading progress, ready, content incompatibility and failure. |
| Onboarding | Purchase, deploy, facing, ready, automatic combat, skip and reopen help. |
| Preparation | No/selected hero, five offers, ten bench slots, merge, insufficient gold, capacity, rejection, ready/edit-cancels-ready. |
| Combat | Selected/unselected, pause, phase lock, target loss and simultaneous effects. |
| Scouting | Viewed seat, next opponent, public information, return home and private content hidden. |
| Relic draft | Three offers, chosen/equipped, no selection, incompatible, future use, empty inventory. |
| Recap | Win/loss/draw/timeout, captain HP lost, effective damage/heal, expanded actual breakdown. |
| Elimination/results | Spectate, restart/exit, final eight placements, victory and defeat. |
| Save recovery | Existing/save-success, corrupt/incompatible, write/load failure, preserve existing file. |
| Bestiary | List/detail, search/no-results, explicit candidate, stars, ability geometry, sandbox. |
| Laboratory | Edit/run/pause/step, A/B/compare/replay, status fixture, formation save/load. |
| Settings | Graphics, audio, input/remapping, language, text scale, reduced motion/effects, defaults and focus. |
| Future online lobby/recovery | Host/join/wait/ready; lost/rejoin/failed/host-left/content-mismatch. |
| Future profile/formation library | Mastery/achievement/discovery/history; sketches and challenge seeds, empty/incompatible states. |

A battle recap uses recorded facts. It must not present a decorative invented explanation or claim a formation would win without an actual comparison. Player-facing error/safe recovery states should remain clear without developer trace text.

## Proposed source, export and import contract

All sizes, frame counts, atlas limits and visual budgets below are **proposals**, not measured benchmarks or proof of quality. Confirm Unreal import choices against the installed version and official documentation at integration time.

| Class | Proposed master | Delivery/use |
|---|---|---|
| UI panel/frame | 512 by 512 layered/vector source | Nine-slice protected corners, stretchable center, separate shadow. Runtime responsive dimensions. |
| UI glyph | 256 by 256 vector artboard | SVG/editable vector master; clean 64/48/32/24 px raster variants; 16 px needs a deliberate simplified micro form if required. |
| Illustrated icons | Content appendix governs | Hero/relic/ability artwork is separate from semantic glyphs; no baked text/stat/star numbers. |
| Bars | 512 by 128 layered components | Runtime fill/clipping and native numbers, scalable caps. |
| World material albedo | 2048 by 2048 source | Tileability and scale reviewed; 2048/1024/512 import variants proposed. |
| World technical maps | 2048 by 2048 authored/derived | Normal/roughness/coverage or material IDs validated separately; channel packing documented only when selected. |
| Particle component | 256 by 256 per-frame source | 4–8 frames for impacts; 8–16 for loops where animation is actually useful. |
| Screen composition | 1920 by 1080 annotated layout | Responsive design evidence; never import as a flattened interactive UI. |
| Arena surround concept | 3840 by 2160 reference | Composition guide or separately reviewed distant backdrop. |

A glow, beam, ring, filled lane or directional arrow may need only a vector/mask and shader animation. It is wasteful to generate dozens of frames where runtime geometry gives a more accurate result. Image generation produces individual art studies/components; exact pixel atlas packing, padding, crop coordinates and engine metadata are authored deterministically afterward.

Layer contract: separate silhouette/line, base color, optional texture, shadow, decorative edge, gameplay mask and status overlay where applicable. Preserve transparent space and crop-safe identity features. Native text is never a generated illustration layer.

Pivot contract: define normalized pivot per component (center for circular icons, tail or source anchor for directional trails/projectiles, explicit bottom/attachment point for overhead status). Record forward direction, scale reference, bounding box and world-versus-screen intent. Avoid guessing pivots from the visible alpha after import.

Color/alpha contract: display color textures carry the intended color profile; masks/coverage/normals are linear data. Specify straight-alpha PNG exports, dilate edge color beyond covered pixels to avoid matte fringe and inspect on dark/light backgrounds. UI and world sprites use different verified import/material settings. Do not use color art as a technical map.

Depth contract: UI widgets remain screen-space; world projectiles/decals follow actual world position, depth/occlusion and camera perspective. Overhead status/readability layers need a deliberate visibility priority, not blanket through-wall rendering. Avoid z-fighting and huge transparent quads. Reduced-effects mode keeps essential range/direction/release/status information.

Atlas proposal: start at 2048 square per coherent category; consider 4096 only after measured need. UI and world/mipped effect atlases remain distinct. Use explicit frame/grid coordinates, padding/extrusion for the selected filtering/mips and no unrelated automatic repacks that silently change references. Actual memory and overdraw acceptance depends on a captured build, not file dimensions alone.

Timing contract: animation can be retimed or held to the authoritative windup/release/recovery/expiry. A frame index never applies damage, grants mana, displaces a hero or ends stun. Released packets may survive source defeat; target defeat and interruption must not leave stale effects. Pause freezes simulation-bound cues consistently.

## Inventory schema and later production manifest

Each inventory row supplies asset_id, group, source_id, label, priority, method, master_size, runtime_sizes, description, states, dependency and status. Additional runtime_basis and frame_proposal prevent a planning row from being mistaken for implemented content.

source_id is a stable canonical content ID where applicable; shared UI uses null. Dependencies are reference IDs, another inventory ID, or explicit hero: dependencies owned by the content appendix. A generator illustration row is an illustration task, not a guarantee that a generator can supply final alpha, nine-slice alignment or sprite consistency.

When production is authorized, create a separate output manifest rather than changing this specification into fabricated completion evidence. Required output fields: asset ID/revision; input/reference provenance; exact source path and hash; editable source/export paths; dimensions; color/alpha mode; safe area; nine-slice insets; normalized pivot; frame dimensions/count/order; loop flag and retiming policy; channel map; import/material intent; generator or authoring tool/version; engine asset path/hash; acceptance state; capture/test pointers; licensing/source provenance.

Approval statuses remain separate: specified, reference-reviewed, produced, technically checked, imported, visually reviewed in-game and release accepted. This appendix is only the first of those.

## Verification before completing a production batch

1. Review original and reduced-size assets on dark and light surfaces; grayscale and team/cost/legality/status meaning still distinguishable.
2. Stretch every nine-slice panel to narrow/wide/tall conditions; corners and borders remain intact. Long English/Indonesian content wraps without hiding controls.
3. Test 1280x720, 1600x900 or 1600x1000 and 1920x1080; then larger/wider views. Test actual 125/150/200 percent text scale. Collapse secondary detail before covering placement cells.
4. Navigate complete shop/bench/inspect/relic/scout/save flows with keyboard and pointer. Hover, focus, selection and rejection remain distinct and explainable.
5. Review 20 deployed heroes and bounded future summons if enabled; HP/mana/status stacks, hero shapes and target links remain interpretable.
6. Exercise maximum/minimum attack rates, repeat casts, target switches, source defeat after release, target defeat, actual charge/push, stun expiry, pause/resume and interrupted establishment.
7. Confirm pooling/expiry, atlas references, alpha fringe, culling/depth, memory and transparent overdraw in a measured packaged match.
8. Compare normal/reduced-effects at normal speed before slow motion. Human readability/art approval is separate from deterministic or screenshot-automation passes.

## Proposed production sequence

- **Reference gate:** inspect REF01–REF04 and record exact owner feedback. The references remain candidates until that happens.
- **P1 integrated slice:** shared panel/button, one unit card across five cost layers, ten-slot bench using one slot master, one relic card/slot, native HP/mana/star treatment, key economy/combat glyphs, one quiet stone surface with derived maps, valid/invalid/facing cues, and representative melee/projectile/heal/stun. Compose one preparation screen from these pieces.
- **P2 completion:** remaining control states, standings, all six hero effect suites, full material/overlay pack, all current lifecycle and required frontend compositions. Hero/relic/trait illustrations follow the separate identity inventory and its reference gates.
- **P3 hold:** online/profile screens and mechanics without a current runtime contract; do not mass-produce unsupported status/ability art.

The human review target for the first slice is one real game screen and a short normal-speed battle, followed by a few close-up component checks. File count, generated detail and beautiful isolated portraits cannot establish readable gameplay.


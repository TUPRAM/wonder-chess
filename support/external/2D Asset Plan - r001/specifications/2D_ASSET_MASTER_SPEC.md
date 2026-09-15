# Wonder Chess — 2D asset master specification

Revision r001 · 13 September 2026 · planning and generated style references only

## 1. Scope and decisions

The owner's request is to list the full detailed specification before production and make several reference images for the generator. This packet delivers those two things. No production portraits, icons, tile textures, animation sheets, materials or Unreal imports have been created by this planning task. Existing gameplay, packages, approved references and art candidates remain preserved.

The proposed direction is **3D creatures and a simple 3D tactical platform, supported by illustrated 2D art**. The 2D package supplies portraits, cards, interface surfaces, icons, surface textures, decals, particle components, loading art and reference illustrations. A flat backdrop can dress distant scenery, while the platform retains depth, contact shadows, camera compatibility and precise placement. The current adopted Wondergrove contract also includes modular roots, stonework and perimeter dressing. This specification does not silently convert that arena into a tilemap or replace heroes with sprites.

The opening statement about keeping characters 3D is treated as the intended direction. The pasted hero-spritesheet section is adapted into the existing 3D motion checklist plus 2D portrait/ability art. The optional clarification about full sprite conversion remained unanswered while this packet was prepared; no conversion work was performed. A full 2D conversion would need its own camera, direction-count, animation registration, sorting, collision, memory and authoring decision.

Current rules that shape the asset list:

| Concern | Wonder Chess requirement |
|---|---|
| Board | 8 columns × 8 rows; precise cells come from runtime geometry |
| Reserve bench | 10 slots, composed from one reusable slot family |
| Deployment | Up to 10 units per side; capacity depends on current level |
| Shop | 5 offers, 5 cost tiers; cost number is live text |
| Tournament | 8 seats with public scouting and a persistent return-to-own-board action |
| Heroes | 6 executable successors and 8 authored future identities; no final roster cap |
| Race/class | 9 race and 9 class identities; their behavioral trait bonuses remain inactive in the current study build |
| Items | 12 named gameplay relics; 3-choice drafts; up to 3 equipped per team and 1 per hero |
| Crafting | No adopted component-to-combined equipment system; do not commission a generic sword/shield crafting tree |
| Stars | 1/2/3 tiers shown with count/shape; retain hero identity and team/status colors |
| Mana | The current experiment uses mana for Snapvine, Prism Organ and Reefglass; do not bake mana indicators into every portrait |
| Statuses | Live effects own duration and expiry. A synthetic stun demonstration is not a new hero ability. Freeze/silence and future entity effects are reserved designs until their mechanics exist |

The linked [32×32 isometric template](https://route1rodent.itch.io/isometric-sandbox-pixel-world-32x32) is a pixel-art prototyping resource. It is useful as an example of modular tile thinking; this packet does not import it, adopt pixel art, or rely on its archive license. No third-party artwork was downloaded or used in the generated references.

## 2. How to read the packet

1. This master specification sets scope, shared style, production method, order and acceptance.
2. [Content specification](2D_CONTENT_SPEC.md) describes every hero, ability, relic, race/class and neutral illustration, with the 3D animation dependency checklist.
3. [UI, environment and VFX specification](2D_UI_ENV_VFX_SPEC.md) describes the complete component inventory, screen states, overlays, effect parts and technical contracts.
4. [Generator brief and reference rules](2D_GENERATOR_BRIEF.md) explains how to use the actual reference images and prepare one bounded generation request.
5. The combined inventory JSON/CSV lists stable asset IDs, source IDs, description, method, priority, master size, runtime sizes, states and dependency. A logical master is not the same as an exported size, animation frame, button state or screen instance.
6. [Reference review](../../../art-source/2d-style/r001/README.md) identifies what each generated plate establishes and what it cannot establish.

Priority labels are local to each appendix: content P1 means the active named subjects, P2 means deferred art-pilot derivatives, and P3 means future content. UI P1 means the smallest coherent sample set, P2 completes current interface coverage, and P3 reserves future mechanics/screens. The generation batches below are the cross-discipline execution order. No P1 label bypasses an unresolved identity or reference dependency.

## 3. Shared art direction

The theme is **an illustrated field guide discovered inside an ancient living sanctuary**. It should feel warm, curious and tactile. Creatures are extraordinary and legible; the interface helps the player observe and arrange them.

Use broad value groups and clear silhouette breaks. Decorative detail belongs at the edge of a card or board, leaving the portrait, information and placement areas quiet. A few deliberate asymmetric leaf/root features are preferable to dense, identical filigree everywhere. Avoid pixel art, photographic texture noise, glossy mobile-game buttons, giant metallic frames, constant bloom and ornamental markings that resemble targeting indicators.

### Proposed color tokens

These are authored starting values, not colors sampled as exact authority from the generated images. Validate their actual combinations after typography and import are assembled.

| Token | Starting value | Role |
|---|---|---|
| Ink | #182B2E | Primary panel and dark icon backing |
| Parchment | #E9DEC7 | Main light text, field-guide page surfaces |
| Quiet stone | #A8ADA0 | Board center and subdued secondary surfaces |
| Moss | #5C7254 | Botanical material accent, not the sole legal-placement signal |
| Old bronze | #A88C53 | Restrained trim, identity ornament, guard accents |
| Friendly teal | #58B9B1 | Own-side identity accent |
| Coral | #DA8F7C | Opposing-side identity accent |
| Plum | #9E7BA9 | Arcane accents; status meaning also requires a symbol/motion |

Semantic colors are a separate layer: green plus for effective healing; blue contour for active shield; violet overhead spiral/stars for stun; cyan directional trail for displacement; amber short crescent for melee. Costs 1–5 may use gray/green/blue/violet/gold trim, always accompanied by a live cost numeral and distinguishable notch shape. These color proposals do not create common/rare/legendary gameplay categories.

### Material language

| Material | Treatment | Where to use |
|---|---|---|
| Parchment | Subtle fiber; clean center; lightly worn edges | Field-guide detail, help, bestiary and loading panels |
| Ink-green enamel/stone | Matte center; tiny bronze bevel | Main HUD, buttons and compact cards |
| Sanctuary limestone | Broad planes; restrained chips; low-frequency variation | Actual board surface; texture must not contain perspective |
| Weathered bronze | Readable edge wear, limited oxidation | Guard cues, card trim, bells and relic accents |
| Ceramic | Glazed ivory and calm colored cavities | Prism-related art and selected relics |
| Membrane/sea-glass | Translucency suggested by controlled rim and internal current | Reefglass art and water effects |
| Roots/moss/cloth | Strong grouped shapes; restrained fine fibers | Perimeter, botanical heroes and select item details |

Use one consistent soft upper-left key light for isolated painted icons. Cast shadows must not be baked into transparent icons if the UI supplies a separate shadow. Lighting for world textures is handled by the scene; do not paint directional sunlight into albedo.

Typography stays native and localizable. Keep the existing readable font as the initial gameplay body face; any decorative title typeface needs explicit font provenance before adoption. No tiny calligraphy for actionable information. Start layout trials around 18 px body text, 24–32 px section titles and 44 px principal click targets at the 1080p composition; these are proposed screen design dimensions, not texture export sizes. Reflow at smaller widths and at 125/150/200% text scale instead of shrinking everything.

Use 4.5:1 contrast as the ordinary-text target and 3:1 for large text, following [W3C's contrast guidance](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html). This is a design target for the game, not a claim of measured accessibility conformance. Check focus outlines, icon meaning, light/dark backgrounds and color-independent cues in the actual screens.

## 4. What belongs in each production method

| Method | Appropriate outputs | Do not mistake it for |
|---|---|---|
| Image generation + art cleanup | Portrait concepts, approved-identity illustration, painterly relic icons, material appearance studies, noninteractive loading/background artwork | Editable vector, trustworthy normal map, perfect alpha cutout, consistent registered animation, working UI |
| Vector/manual UI authoring | Small glyphs, stars, frame geometry, corner ornaments, nine-slice panels, placement masks and focus shapes | A separate generated painting for every hover/disabled state |
| Shader/native runtime composition | Health/mana fill, progress, targeting geometry, gradients, arrows, beam extents, status duration, damage/heal numbers and state combinations | Static full-screen artwork or a new combat authority |
| 3D model/animation rendering | Final matching hero portraits, bestiary turntable, motion references and selected billboard/VFX passes | A reason to discard the existing skeletal character pipeline |
| Texture/map derivation | Normals, roughness, masks, mips, atlases, technical alpha cleanup and packing | Semantically valid data maps automatically emitted by an illustrative generator |

The current r13 runtime already presents independent attacks and authoritative effects with mesh/text cues. The later asset integration should replace or dress that presentation while keeping the same event sources. Art does not decide the attack target, create damage, advance mana, continue a stun after expiry or invent a push when no displacement occurred.

## 5. Master deliverable contracts

All dimensions below are proposed delivery targets. The generator's returned dimensions must be inspected; prompt text does not guarantee an exact export. A reference plate is never cropped and silently promoted to an atlas.

| Deliverable | Master target | Runtime examples | Source and export |
|---|---|---|---|
| Hero portrait | 1024×1024; clear focal silhouette and 8–10% safe border | 512/256/128 portrait crops;64 roster silhouette supplied separately | Layered foreground/backing; transparent RGBA foreground plus background when needed |
| Optional full bestiary art | 1536×2048, all appendages inside frame | Large detail panel | Prefer approved model render plus paint cleanup; deferred until identity matches |
| Ability/relic illustration | 512×512, one dominant idea | 128/64; simplify for 48/32 | Editable painting and transparent PNG; keep frames/text separate |
| Hero silhouette/trait glyph | 256 or 512 square vector viewBox | 64/48/32/24 | Editable vector; optical redraw at small sizes; raster outputs derived |
| Reusable panel/card frame | 512×512 starting master | Arbitrary native layout sizes | Separate corners/edges/center or nine-slice source; exact insets in metadata |
| Health/mana/progress | 256×64 starting strip where a texture is needed | Width set by layout or camera | Separate shell/fill/mask; stretch direction and cap protection declared |
| World surface texture | 2048×2048 starting material sheet | Chosen by measured camera coverage | Albedo plus separately authored/derived technical maps; tile/repeat test |
| World overlay/mask | 256 or 512 square; geometry often procedural | Actual legal cells/areas | Transparent masks and runtime tint; no baked perspective or numbers |
| Impact frame sequence | 4–8 proposed frames of 256×256 | Short one-shot event | Registered source frames, alpha, pivot and numbered order |
| Looping effect sequence | 8–16 proposed frames of 256×256 | Stun/ambient status if a sequence is appropriate | Seamless endpoints and constant pivot; engine state controls lifetime |
| Beam/trail/wave components | 256×256 heads, 512×128 strips as appropriate | Scaled to actual path/extents | Separate core, edge/noise/mask; shader motion often replaces many frames |
| Title/loading illustration | 2560×1440 starting master, safe central composition | 16:9 plus cropped wider/narrower screens | Separate foreground/background/text safe area; no live UI painted in |

Nine-slice insets are per-axis fractions derived from explicit source pixels, for example 32 px protected margins on a 512 px source gives 0.0625 per edge. A stretched test must preserve corners and keep text away from ornament. Epic documents the Box/Border/Image styling model in its [Styling guide](https://dev.epicgames.com/documentation/en-us/unreal-engine/styling?application_version=4.27); that older page supports the general technique only. Exact current UE5.7 import/compression behavior must be confirmed during integration, not assumed from the historical page.

PNG color exports should contain actual alpha where requested, not a painted checkerboard. Declare straight versus premultiplied handling and test the selected material path; the default proposal is straight-alpha source. Transparent edge colors need suitable padding to prevent fringes. Color art and masks/data maps must have separate color-space/import intent. World sprites need depth, occlusion and mip review; do not automatically apply UI texture settings to world effects.

Propose 2048-square atlases where packing is useful; increase only with a measured reason. Atlas padding and extrusion depend on filtering/mips, with a provisional 8 px padded separation at the base atlas for trials. Record actual trim, original size and pivot, not just packed rectangles. Do not pack localized text or unrelated lifetime groups into a giant all-game atlas.

At 256×256 RGBA8, eight uncompressed frames contain 2 MiB of pixel data before mips/packing/compression; a 2048² RGBA8 atlas contains 16 MiB before those changes. These are arithmetic planning estimates, not measured GPU residency. Use profiling before setting a final texture/particle memory budget.

## 6. Per-file record and naming

Each logical asset uses a stable descriptive ID tied to the canonical subject where applicable, for example portrait_wc_vn_bellback or relic_wc_vn_r_heavy_bloom. Revisions are separate files/directories. A final export must record:

- Source ID, current catalogue hash, intended screen/effect, production status and author.
- Reference images actually provided to the generator, their roles and SHA-256 hashes.
- Exact prompt and returned tool metadata when available; do not invent seed/model details.
- Master dimensions, crop/safe area, alpha convention, color space and lighting intent.
- Layer names and which content is illustration, mask, frame, shadow or live text.
- Nine-slice inset pixels/fractions or frame cell dimensions, count, pivot, order and trim.
- Animation intent: loop/one-shot, event start, release/impact binding, interruption, expiry and reduced-motion behavior.
- UI states composed from it; small-size alternatives and accessibility roles.
- Export settings, atlas membership, import recipe, source/output hashes and review evidence.

The JSON inventory uses SPEC_ONLY_NOT_PRODUCED for production entries. A composed screen row means reuse of the kit in a layout; it is not an instruction to generate a full painted interface. A runtime/shader row is an implementation requirement that may need no new raster image at all.

## 7. Proposed next production batches — not executed

| Batch | Scope | Why this order | Exit before expansion |
|---|---|---|---|
| R0 — current request | Four reviewed reference themes, detailed specs and inventory; preserve the first UI study and its quieter revision | Gives us something concrete to choose before mass generation | Owner selects/revises the style reference direction; no automatic asset approval |
| P1 — smallest integrated art sample | One panel/button family, one five-tier shop-card frame family, one prototype portrait tied to a valid identity reference, one Heavy Bloom icon, health/mana/status unit HUD, one legal/illegal placement overlay and quiet stone surface; stun/projectile/impact sample parts | Exposes readability, slicing, identity and alpha problems with a small set | View together in the real lab/solo build at720p/1080p; reject unclear states or identity drift before batching |
| P2 — active named content | Six hero portrait/ability/silhouette sets as identities become ready; all12 relic icons; shared UI glyphs and all required current states; neutral art in its own checked family batch | Establishes useful variety with the actual rules and no invented equipment | Small-size blind identification, correct bindings, reference/model agreement and complete source files |
| P3 — complete current screen/effect kit | Preparation, combat, scouting, draft, recap, saves/errors, settings and current lifecycle; six skill suites and normal attacks; Wondergrove material/decal kit | Completes the player journey and consistent event feedback | Pointer/keyboard, localization, effects overlap/expiry, clean packaged review and measured performance |
| P4 — art pilots and earned expansion | Accepted Bellback/Prism/Thimblewake derivatives, future authored hero assets, inactive-trait activation presentation, future neutral/boss/entity/online states | Dependent on accepted forms and implemented mechanics | Corresponding model/runtime gates; not merely a full illustration folder |

The names P1–P4 in this table are production-batch labels, distinct from row priority codes. Final portrait production may wait for a model, while panels, glyphs, relic icons and placement art can progress independently. Do not commission all14 final hero illustrations before their identities are reconciled.

## 8. Review criteria and stop conditions

Review each reference at full size for visual direction. Production assets must additionally pass these later checks:

1. **Identity:** correct hero/relic/trait, no invented equipment or extra parts; Bellback's approved dorsal bell and construction decisions retain precedence.
2. **Small size:** identify silhouettes and functional symbols at64/48/32/24px where used; simplify rather than add sharpened detail.
3. **Functional meaning:** guard differs from shield; first-hit lash does not look like piercing; Prism's row/column releases remain separate; heal is effective restoration; PUSH requires actual displacement; stun is overhead and clears promptly.
4. **Interaction:** normal, hover, pressed, keyboard focus, selected and disabled are distinguishable; focus may coexist with other states. Reject reason remains readable.
5. **Layout:** all64 placement cells remain accessible;10bench slots and5shop offers remain usable; secondary details collapse or scroll without covering critical interactions.
6. **Language:** English and Indonesian; long names/descriptions;125/150/200% text scale; no baked words or missing glyphs.
7. **Motion:** normal speed first, then slow review; authoritative release/impact; shortest/longest attack intervals; movement/target changes; defeat during cast; pause/resume and full expiry.
8. **Crowding:**20deployed creatures with health/mana/status stacks; both teams, multiple copies, repeated casts, restrained reduced-effects mode and measured overdraw/pooling.
9. **Import:** alpha fringe, color-space, mip behavior, slices, atlas UVs, pivots, texture budget and package inclusion.
10. **Provenance:** editable source, actual reference pixels and prompts, correct file hashes, per-use rights and exact approval scope.

Stop an asset batch if its identity drifts, critical effects cannot be distinguished, UI art obscures information, or a generator output is being treated as a finished technical export. Change the method after two ineffective bounded revisions. Production stops at the owner's requested planning boundary now; this packet does not ask to bypass that boundary or any later prescribed human art gate.

## 9. Open decisions that the references make reviewable

The recommended hybrid3D/2D route remains the baseline unless the owner chooses a different representation. The next art decision is whether REF01's materials and the quieter REF02 revision express the intended game. Separate decisions concern portrait treatment, relic-object simplicity and effect brightness. We do not need to settle every future hero, online screen or cosmetic before making the first approved small sample.

There is no new approval of final forms, production UI, art release, balance or a whole milestone in this packet. The earlier owner review of r13 combat readability remains recorded independently.

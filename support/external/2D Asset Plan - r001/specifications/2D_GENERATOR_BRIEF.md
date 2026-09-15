# Wonder Chess — generator brief and reference rules

Planning revision r001. The four reference themes are generated proposals. Production assets remain SPEC_ONLY_NOT_PRODUCED.

## What “learn our style” means here

Use the selected reference images as actual image inputs with a consistent text brief. This conditions the next generation on the visible style. It is not model fine-tuning, permanent learning, proof of reproducibility or a guarantee that every new hero will match. We have not trained or uploaded a dataset, purchased a service or started bulk production.

The built-in image-generation tool produced the reference images in this packet. Exact prompts, original file paths, returned sizes and hashes are preserved. No CLI fallback, API key, custom model or invented random seed was used. The outputs are flat raster reference plates; they do not contain editable layers, alpha-ready sprites or technical texture channels.

## Reference precedence

1. Canonical game data owns names, IDs, mechanics, conditions and scope.
2. Approved per-character construction and identity references own anatomy, proportions and attachments. Bellback's approved r004 reference decisions take precedence over the newly drawn portrait examples.
3. The earlier owner-selected Wonder Chess direction owns the shared sanctuary/creature aesthetic.
4. The newly selected style plates may guide materials, framing, composition or effect grammar only within their labeled role.
5. The per-asset brief owns delivery dimensions, crop, padding, alpha, layer and small-size requirements.

Do not pass every reference into every request. A bronze relic does not need a board screenshot; a stun component does not need a creature portrait. Unrelated references can transfer extra anatomy, scene clutter, text or ornament into an asset.

| Reference | Supply when | Explicit exclusions |
|---|---|---|
| REF01 materials and shape | Material treatment, loading/background appearance, painted relic finish, UI ornament language | Exact pixel palette, measured geometry, tactical floor pattern or final lighting |
| REF02 quieter revised preparation study | Whole-screen hierarchy, relative placement, dark/light separation | Board/bench counts, fake statistics, final camera, creature scale, actual roster or exact widgets |
| REF03 icon and portrait language | Crop framing, simple silhouette treatment, painted object finish | Final Bellback/Prism/Thimblewake forms; its six demonstration objects are not the12 canonical relics |
| REF04 combat effect grammar | Slash, shot, heal, shield, stun, push, guard, beam or upgrade shape/motion | Frame timing, alpha sheets, damage, true target geometry, frame counts or actual game status |

Use the revised REF02 for discussion. Preserve the first version for history: its busy tile ornament and extra creature lineup were reasons for a bounded correction. The revised plate is still an illustration, not a production HUD.

## Reusable style block

> Original Wonder Chess illustration for a mythic-storybook tactical auto-battler set in Aurelune's Wondergrove sanctuary. Broad readable shapes, painterly grouped values, calm matte surfaces, deliberate restrained asymmetry. Materials from carved limestone, weathered bronze, moss/bark, glazed ivory ceramic and contained translucent magic. Warm, curious, crafted field-guide character. One clear focal idea. Quiet negative space. Decorative detail kept away from information and silhouette boundaries. Match the supplied reference's material/shape language without copying its layout, text, unrelated objects or speculative anatomy.

## Reusable request fields

Each generation request must contain all applicable fields below, filled with the actual subject rather than placeholders in a production call.

| Field | Required content |
|---|---|
| Use case | Portrait illustration, relic illustration, material appearance study, VFX component or reference-only concept |
| Asset ID and revision | Stable inventory ID plus new candidate revision |
| Gameplay role | One precise sentence from the source definition; identify implemented versus future |
| Input images | List each supplied image, hash/ID and role: identity, construction, style or composition |
| Identity locks | Parts that may not change; approved asymmetry and attachments |
| Subject description | Dominant silhouette, one focal material and supporting details |
| Composition | View, facing, focal region, clear silhouette, crop safe area and background separation |
| Lighting | Common icon key light or scene-neutral material appearance, as appropriate |
| Color | Named semantic roles and exact tokens when needed; no automatic new team/status meanings |
| Delivery | Requested dimensions, transparent/opaque intent, what must be separate in later cleanup |
| Exclusions | No baked text/stats/frame/star/team markers; no extra limbs/items; no checkerboard masquerading as alpha |
| Review target | Identity matching,64/32px readability,edge quality or effect meaning |
| Output status | Candidate until inspected and accepted for its intended use |

A flat generator output cannot satisfy a request for an editable layered source by itself. Preserve it as the raster source, then perform deliberate layer/mask/vector/atlas authoring in the production step. Do not claim automatic recovery of hidden image content as an original editable layer.

## Three example future briefs — not executed

### A. Bellback portrait study

- Subject: Bellback, Beast Guardian, a grounded moss-and-bark quadruped whose dominant bronze bell is suspended in its dorsal mount.
- Actual inputs to attach later: approved Bellback aesthetic/construction references; REF01 only for material restraint; REF03 only for square crop framing.
- Locks: dorsal bell, broad animal face, four toes per foot when visible, approved right-shoulder branch and simplified appendage inventory. Do not reinterpret it as a chest-bell humanoid or add a forest of new attachments.
- Composition: head and recognizable dorsal-bell silhouette within a1024² crop with10% safe margin; three-quarter portrait; readable eye and muzzle; warm expression. Background separable and quiet.
- Exclusions: no gold cost, stars, race/class emblems, mana bar, skill effects, frame or name painted into the image.
- Gate: concept portrait study only until it agrees with the approved final model. A polished speculative portrait is not a substitute for Bellback forms acceptance.

### B. Heavy Bloom relic icon

- Source: wc_vn_r_heavy_bloom; greater impact with longer visible cast commitment for compatible abilities. Runtime tooltip supplies the tradeoff.
- Inputs: REF01 material language and REF03 single-object icon treatment; do not copy one of REF03's unrelated sample objects.
- Proposed motif: a dense downward-bending bronze flower supporting one heavy luminous seed, clearly heavier at its bottom; a short curved stem creates an unmistakable contour.
- Composition: one object filling about75% of a512² canvas; clear separation between petals; soft upper-left key; transparent export intended after alpha verification; no vignette fused to the object.
- Exclusions: no lettering, numeric bonuses, rarity frame, weapons, explosive aura or misleading cooldown clock.
- Review: recognizability against Quick Wick, Broad Canopy and Patient Lantern at64px; preserve a simpler silhouette at32px if used there.

### C. Stun effect component

- Meaning: target actually cannot act because stun is active; duration and expiry come from the combat state.
- Inputs: REF04's STUN mini-study only for the overhead spiral/star relationship; no pawn or scene in the output.
- Proposed pieces: clean violet spiral mask and separate small star shape, each centered on its own256² canvas. Orbit/rotation belongs in the runtime, so an8-frame loop may be unnecessary.
- Composition: controlled thin outline and small filled stars; generous transparent border for camera/rotation; minimal bloom.
- Exclusions: no head/body, UI text, blue shield, healing plus, backdrop or screenshot-style grid. No baked second-by-second timer.
- Review: visible above tall/short units; not confused with an upgrade sparkle; reduces to a clear stationary symbol in reduced-motion mode; clears on actual expiry/defeat.

## Animation and atlas production

An illustrated three-stage diagram explains motion intent. It does not establish a consistent frame sheet. For actual frame animation, choose a fixed canvas, pivot, frame order and direction, then author/clean each frame with continuity review. Generate small bounded components, not all hero animations in one enormous sheet. Assemble atlases with deterministic tooling after frame approval and record coordinates.

Use the engine's existing event time for anticipation, release, arrival and expiry. A loop continues only while its condition is true. A one-shot may complete after source defeat only when the committed event semantics permit it. Testing must cover interruption, repeated casts, pause, speed variation and scene cleanup. Never alter combat timing to hide a poorly registered animation.

Full 3D hero animation stays on the model/rig route. A 2D pose sheet can guide idle/walk/turn/attack/cast/hurt/stun/death design, but this request does not authorize making duplicate sprite or Spine versions of each hero.

## Batch discipline

Select the style packet first. Then make the smallest coherent sample defined in the master specification and view it in the actual game. A full-content generation queue should only include rows whose dependencies are ready. Keep future or unapproved identities out of the batch.

Use one subject and one purpose per generation. Save exact input references and prompt. Inspect the result for the chosen purpose before generating variants. Limit a revision to a stated visible problem; after two ineffective changes, alter the method rather than producing more similar candidates. Keep originals and explicit rejection reasons.

The current packet ends at planning and reference creation as the owner requested. None of these example briefs has been sent for production generation.

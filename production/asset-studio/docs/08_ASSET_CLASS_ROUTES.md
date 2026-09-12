# Different assets require different routes

## Hero / creature

Use the full reference/forms/topology/UV/material/rig/skin/motion/engine route. Creature references must include gait, joint direction, locomotion footprint and required appendages. Do not force a quadruped or winged creature into the human armature because IDs look similar. For the initial game, limit unapproved creature complexity rather than claim it is free through rig reuse.

Required extras: identity closeups, grip/paw/wing construction, motion contacts, visibility of team states, complete clips, socket and culling tests. Hand/face rigs are use-dependent; non-speaking small heroes do not automatically need cinematic facial rigs.

## Equipment and rigid props

Use independent front/side/three-quarter views and section/attachment details when needed. Model pivots, grip axis, scale and contact surface as part of the asset. No skeleton for a completely rigid sword unless the existing pipeline deliberately embeds it. Animated hinge/chain/bow-string equipment needs an approved rigged profile or simpler named deformation route.

Do not weld a prop to a hand during concept-to-3D generation. It should remain reusable/editable. Export either as a socket-attached static mesh or part of the character skeletal mesh according to the active contract, not both accidentally.

## Modular environment and arena

Define kit grid, module dimensions, pivot conventions, connectors, snap directions, wall thickness, trim-sheet/material family and assembly examples. Test corners, doorways, stairs and repeated tiling from the actual camera. The one reference tile defines the measured grid, not a loosely scaled illustration.

Use procedural generation for repeatable pieces after one authored module is accepted. Validate variations and their bounds/collision; do not generate thousands of unreviewed variants. Preserve player/board readability over decorative architecture. Lightmap UVs are required where the selected lighting path uses them—not a blanket extra channel on every asset.

Run an assembled arena review with heroes, UI, shadows and effects. Assets that look excellent alone may obscure the board together. Set a background contrast/value budget so characters remain the focal point.

## Foliage

Add botanical shape/scale references, card or mesh-clump design, alpha/masked-material policy, normals, wind masks, pivot/branch hierarchy and LOD strategy. Evaluate overdraw, shadows, mip behavior and wind silhouette. Avoid extremely thin detail that flickers at strategy-camera scale. Not every tree needs bones: wind/material deformation is an explicit alternative.

Test repeated instances for obvious repetition, lighting differences and performance. Do not let waving foliage cross the strategic board or imitate a combat signal.

## VFX

Reference packet is a timing storyboard, shape/color meaning, event source/target, world/screen size and lifetime—not a body turnaround. Build anticipation/release/travel/impact/recovery timing appropriate to the actual skill. Separate shader/mesh/flipbook/Niagara components and their responsibilities.

Specify maximum simultaneous emitters/particles, overdraw, pooling, bounds, gameplay event bindings and reduced-effects mode. No speculative damage logic inside VFX. Stun/shield/heal/dash must remain distinct through shape and timing, not only color. Run crowded-combat video reviews and profile rather than approve an isolated effect loop.

The route's `motion` stage evaluates effect timing, not skeletal animation. Tool names in the route are stage labels; use Unreal-native effect tooling where suitable.

## UI/icons/portraits

Define actual display sizes, states, contrast, localization growth, touch/click target, alpha/padding and atlas use. Icon clarity at 24/32/48 pixels can matter more than a large illustration. Illustrations remain separate from live text. Selected/disabled/hover/focus/team states need explicit design rather than arbitrary hue changes.

Final hero portraits should derive from the approved character model or pass an identity-matching review. Do not keep an idealized concept portrait beside a materially different in-game mesh and call the identity complete. If vector output is required, do not pretend a raster image is editable vector artwork.

UI assets skip retopology/rig/skin. They still need in-engine implementation and packaged-screen review at the supported resolutions/languages.

## Audio

Define sonic function, timbre, event time, duration, variants, loop boundaries, sample format, peak/loudness policy, attenuation and concurrent voice budget. Reference audio must have provenance. Generate/synthesize/record only through permitted tools.

Review dry sound, in-context mix and crowded battle. Check clipping, clicks, unwanted silence, loops, repetition fatigue and masking of important cues. The ledger requires actual audio evidence rather than screenshots of waveforms as listening approval. `forms` means the approved timbre/envelope; `optimization` covers formats/budgets; no UV or skinning steps apply.

## Route exceptions

A custom asset may need a hybrid route. Add an explicit profile change with tests; do not waive stages ad hoc. A static prop later given bones changes its route/dependencies. A UI-only concept later used as a 3D texture needs material/runtime validation. All routes end with engine/context evidence and human release acceptance.

# 03 — Hair: shape one clump before building a hairstyle

**Task:** MR1-HAIR. **Scope:** one broad asymmetric sweep, then a few primary masses if the proof works.

## Why this is not a repeat of r003
The submitted review already reports a scalp-supported trial that pinched near the temple and lost the intended sweep. The new method must preserve both scalp attachment and a designed three-dimensional volume. Merely projecting a different dense strip onto the scalp is not enough.

The current image's conspicuous repeating strands are not improved by adding more strands. Start with fewer, broader shapes whose silhouettes and overlaps are individually chosen.

## A. Establish the scalp and visible hairline
Inspect `ADA_Hair_Foundation` and the actual head under it. It may be usable context; its name is not approval. The foundation must follow the cranial volume without an unwanted open arch exposing the skull through the hairstyle. Do not fuse all hair, ears and face in an indiscriminate remesh.

Mark the approved part line, frontal hairline, temple transition and rear gathering area as references on the candidate. Record which small gaps are intentional and which expose the scalp contrary to the reference. No general 'all hair must touch skin everywhere' rule is appropriate: styled hair has volume.

Isolate one leading sweep; hide old overlapping/tube objects in the candidate render allowlist. Preserve them in the baseline/archive.

## B. Build a shaped solid ribbon or wedge
Preferred starting representation: a small hand-shaped polygon cage with a broad convex top and flatter fitted underside. Start from a manageable strip or small box, not dozens of circular bevel tubes.

For an exploratory clump, 6–10 length stations and 4–6 width samples can give useful editing control. These are optional starting scales, not required counts. Shape each station deliberately; do not keep every cross-section identical.

At each station consider:
- the direction along the scalp;
- width across the sweep;
- depth away from the scalp;
- crest position, which may be off-center;
- tilt/twist;
- contact or overlap at the underside.

A flattened section wider than it is deep is a useful starting hypothesis. Do not force one ratio on the root, crest and tip. Its broad surface should read as swept hair, not a hose pressed flat after generation.

Use a modest subdivision preview only after the cage reads correctly. Add controlled thickness and a tapered end without collapsing many vertices into a visible star point.

## C. Alternate tool implementation
A curve with a purpose-built flattened/asymmetric bevel object, deliberate tilt and varying radius/taper may be used when it exposes sufficient local control. Blender supports custom bevel cross-sections, tilt/radius and taper controls [S3]. The exact property behavior must be verified in the installed version.

The acceptance target is identical whichever representation is used. Default circular bevels replicated over several paths are specifically not a new solution. Convert a duplicate to mesh for inspection when necessary; retain an editable source.

## D. Anchor roots, not the whole surface
The root/underside anchor region needs a controlled relationship to a smooth scalp proxy. Use individually edited contacts or a constrained vertex group with a verified direction/offset. Fade influence over several deliberately chosen rows.

Do not nearest-project every vertex of the clump to the head. That can erase the crest, collapse the underside/top distinction or force neighboring rows together at the temple. The crown of the hair volume should remain independently shaped above the scalp.

Inspect from above and behind as well as from the flattering front. The root should enter the base mass naturally; it should not float as an arch or end as a tube pressed against the skin. Limited hidden overlap is permitted for the stylized assembly when it does not create visible intersections or deformation problems. Hidden overlap is not an excuse for a broken root silhouette.

Preserve the approved sweep and hairline while correcting contact. A clump that touches the scalp but points the wrong way fails.

## E. Prove asymmetry and hierarchy
For the single proof, establish a dominant sweep with a root, crest, overlap edge and taper. Show that its profile reads differently from a circular tube.

Only after that succeeds, form the hairstyle from a small set of primary volumes: leading sweep, counter-sweep and rear gathering mass. An eventual set of roughly 5–8 major masses may be sufficient for this study; do not treat that as a universal hairstyle rule.

Vary their width, length, taper and direction. The spaces between them must follow the approved flow, not a regularly spaced array. Use a few subordinate locks only where they improve the reference likeness or silhouette.

## F. Braid after gathering
Do not produce a long mechanical three-helix braid as compensation for a weak crown. First create a tapered gathered volume that belongs to the hairstyle. Then suggest interwoven segments with deliberate taper, overlap and a finite tie/tail.

Retain the approved shorter braid proportion. The precise back-view construction must follow the approved local reference, not a guessed shape from a front crop.

## G. Required review
Record front, profile, three-quarter, rear and crown/top views under the same settings as the baseline. Add a closeup of the root, a cross-section/end view of the clump, and a cage view. The diagnostic cross-section is a temporary review copy or clipping view, never an accidental cut in the saved candidate.

Pass the single-clump method only when it preserves the intended sweep, has credible scalp attachment, avoids temple pinching and has a clearly non-tubular mass. It remains an agent method decision until human forms review.

If two bounded corrective passes do not improve the critical relationship, stop that method. Deliver the source and concise fallback brief rather than expanding the rejected shape across the whole head.

## Required outputs
`hair_mass_proof_<revision>.blend`; a root/cross-section/cage review; matched camera images; exact source parts changed; retained and rejected alternatives; remaining defects. No textures, groom simulation, rigging, LOD or export is needed to prove this form.

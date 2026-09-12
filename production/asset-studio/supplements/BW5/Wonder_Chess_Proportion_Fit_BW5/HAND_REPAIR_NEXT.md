# BW5 — Separate fixed-hand root/web repair

This is a secondary independent lane. It must not block the torso and shoulder fit work. Read the current BW4 report and [integration boundary](docs/04_REVIEW_AND_INTEGRATION.md).

## Target and preserved decisions

Keep the selected 30 × 26 mm hilt section, 110 mm exposed length and 154.4 mm total. Keep the actual blade and guard geometry. No hidden pommel is assumed. Preserve canonical equipment, sockets, rig and actions.

The new glove remains a fixed closed representation; no open-to-close trajectory or new digit-animation system is required. Preserve the original licensed open glove and master MPFB data. Use independent derivative data.

The source report locates the worst intrusion in the middle proximal/metacarpal BASE, around candidate vertex709; evaluated self-crossings are concentrated in the thumb/web. Those IDs are diagnostic seeds for the BW4 topology, not selections to reuse after reconstruction. Source-specific metrics do not apply automatically to a rebuilt surface.

## Why another interpolation pass is not enough

Distal fingers can sit outside a handle while the surface connecting them to the palm cuts through the handle. An interpolated bridge is not constrained to stay outside the volume merely because its boundary vertices are outside it. Subdivision also changes the evaluated surface. Fix the root construction and verify both raw and evaluated geometry.

Do not apply another coefficient-driven displacement or smooth the outside until it looks cleaner. The report already rejects that method.

## 1. Establish the actual keep-out shape

Open the selected sword and glove in an isolated native Blender scene. Inspect handedness, digit labels, hand registration and where the unchanged guard begins. Define the handle axis from guard toward exposed grip end. Check that the digit order and intended conventional grip make sense; do not infer finger names solely from screen position.

Use the selected octagonal/actual hilt geometry, not the old 28mm cylinder and not an ellipse inferred from its two diameters. Include the guard in all construction clearance tests. A wireframe view is allowed; removing the guard from the calculation is not.

If the original single hand registration is itself incompatible with a plausible grip, show one deliberate candidate-only registration proposal before remodelling, retaining the old comparison. Do not alter hilt dimensions or guard/blade. Lock the chosen candidate placement before individual fitting; no per-finger/per-frame relocation.

Inspect whether the target pieces are closed and suitable for signed queries. If a closed diagnostic envelope is required, document exactly how it approximates the target. Do not treat an unverified proxy as the exact sword.

## 2. Make transverse construction sections

At the index/middle/ring/little base regions, inspect sections normal to the actual handle axis. Display the occupied hilt section, the palm-side volume, the digit cross-section and the intended empty grip channel.

This is the key proof: there must be a continuous OUTSIDE route from each useful distal form back into a separate coherent palm. Do not fill the channel with a straight face bridge, cap a finger root across the handle, or stitch loops whose winding creates crossing sheets.

Use the source distal shapes as references; retain only geometry that remains anatomically and geometrically useful. Nothing forces preservation of an invalid proximal root.

## 3. Replace the root/web mesh on the derivative

Tools: Edit Mode selection; delete only failed local faces; Knife/Poly Build; extrude and deliberate Bridge Edge Loops; proportional editing with a bounded connected selection; optional sculpt form-target copy. Verify installed keymap and actual selections.

A. Remove the invalid middle/base transition rather than moving its worst vertex outward and leaving the same crossing faces.
B. Shape the palm/thenar as a coherent volume on the appropriate side of the actual hilt.
C. Establish proximal finger sections with recognizable knuckle rhythm and sensible spacing. Avoid identical sausage loops.
D. Route the new connecting surface around the hilt clearance envelope. Bridge small confirmed boundary segments incrementally, inspecting winding and connection order. Bridge's Twist option changes correspondence; it does not automatically select an anatomically safe bridge (B5).
E. Rebuild the thumb root with enough three-dimensional web volume. Distinguish the opposing thumb body from a thin membrane linking it to the palm. Do not paste a covering patch over an intersecting interior.
F. Keep all fingers distinct. No mitten conversion or wholesale scaling to hide the fit problem.
G. Inspect the raw cage before restoring subdivision. Stop immediately on an inverted seam, confirmed self-crossing or target intrusion; do not wait for a final render.

Optional sculpt/remesh must produce a real new form, not erase detail indiscriminately. A Boolean subtraction of an enlarged handle can be a temporary diagnostic of forbidden volume but is NOT a finished-hand method: inspect any resulting holes/tunnels, thin walls, finger separation and topology before adoption. Do not merge the weapon into the hand.

## 4. Protect the intended empty space

Every reconstructed section must be outside the occupied hilt and guard except explicitly declared surface contact. Inspect whole surfaces and triangle interiors, not just distal-pad vertices. The previous 11.814mm intrusion is not a contact-tolerance issue.

Use existing raw/evaluated self/handle/guard queries and actual section images. Confirmed transverse crossings and visible invalid containment remain blockers. Tangency/coplanar contact is a separate case that the existing query may not classify. Report it instead of silently excluding it.

After topology changes, create a reviewed mapping for each anatomical pad BEFORE fitting. No blind evaluated-index reuse. Do not reselect favorable closest vertices after observing results.

Keep the earlier numerical pad band as a comparison screen only. Quality requires a convincing hand holding the actual hilt, not a fabricated claim of force closure or universal anatomical validity.

## 5. Test construction and wrist integration separately

Capture hilt-visible palm, dorsal, both sides, axial sections, thumb-web underside, handle-hidden construction and actual cage. Use balanced/reversed light. New images must identify the selected hilt and which obstacles are hidden visually but still tested.

If construction passes, convert the candidate into the existing game hand bind space ONCE; retain the shared rest pose. Keep one equipment attachment chain and an intentional forearm/cuff transition. Follow the existing BW4 runtime procedure and verify its real transforms before use. No copy of arbitrary MPFB Euler angles onto the game rig.

Test the candidate's actual sword orientation and glove on all seven canonical actions and transitions. The old 865 samples only verified the older source contract; they do not test the new hand.

An always-gloved export derivative may omit truly covered bare-hand faces only after coverage is demonstrated; the master remains intact. This does not approve the old bare-hand fold or allow hiding a malformed glove.

## Exit and bounded fallback

Initial new construction plus up to two substantive non-improving corrections. Do not count every small edit/render as a whole attempt, and do not reset the method counter by renaming scripts.

If the outside-channel/root reconstruction still fails, park the glove with a precise minimal source/cage intervention. Do not spend the rest of the armor assignment on it. Continue independent torso/shoulder work. No human approval, completed-Ada claim, canonical replacement, or universal-recipe promotion is authorized.

# 02 — Construct Ada's fixed closed hand

**Task H1. Output: one deliberate closed right glove around the actual sword handle.**

This is a proposed modeling recipe. It has not been executed in this package. It deliberately abandons the failed requirement to reach the shape through the current MPFB thumb animation. It retains geometric integrity and equipment contact as requirements.

## H1.0 — Resolve the target before posing anything

Read the current local fixed-option audit and the actual sword asset. Establish anatomical handedness, hand-to-sword orientation, measured grip cross-sections, usable length between guard/pommel, and the existing wrist socket/offset. Record the exact object, source hash, evaluated state, units and camera evidence in a copy of [equipment_fit.template.json](../templates/equipment_fit.template.json).

Default: fit Ada's candidate to the actual current hilt without modifying the sword. The old 28 mm diagnostic cylinder is an archived control, not this task's target. A proxy is acceptable only when it accurately represents the chosen hilt and is labeled as a proxy.

If the actual hilt is implausibly large/small for the approved proportions, make a side-by-side **proposal** for one local hilt adjustment. Do not silently resize the whole hand, alter the blade, or overwrite the source. Stop dependent fitting until that changed target is explicitly selected. Independent armor blockout can continue.

## H1.1 — Recover a clean editing surface, not the failed posed web

Create an independent candidate collection. Inspect the source/open-pose glove and underlying MPFB hand as anatomical references. Confirm object data, keys, materials needing edits and armature targets are not linked to protected originals.

Preferred construction surface: a derived copy of the clean fitted glove in its uncollapsed open/relaxed state, with the current intended body shape resolved. Make it independently editable, without a live finger rig driving the same coordinates you are changing. Source shape keys remain on the master; the static derivative need not preserve all keys or vertex indices.

Do not take the BW3 folded frame-25 surface and merely apply its armature. BW3 is a motion-failure example, not a form template.

Store the open reference in a non-export collection. Preserve the source license and adaptation label (`toigo_gloves_short`, if that is the actual source). This is a licensed adaptation, not an original mesh created from nothing.

## H1.2 — Make the handle/frame easy to inspect

Use the proven measurement helpers; do not repeat all 90 direction probes. Put the hilt in the candidate's verified rest-space working frame. Display a few labeled axes and pad-side direction. Keep full affine scale/orientation accounted for exactly once.

Create fixed palm, dorsal, side, axial and three-quarter cameras. The palm/side/axial set must show both handle ends, the thumb and the cuff. Add handle-hidden views for anatomy, but retain the handle in geometry queries.

A displayed measuring overlay should distinguish total hilt, usable handle and actual contact span. Do not report the guard/blade extents as handle size.

## H1.3 — Design the closed gesture with a small number of meaningful landmarks

Mark the thumb base, thumb pad, index/middle/ring/little knuckle arc, and expected finger-pad contacts. Keep four individually recognizable curled fingers and a separate opposing thumb.

Use the approved Ada hand proportions. No uniform sausage fingers and no conversion to a mitten without a separate design decision. Knuckles and finger lengths should not be leveled into a straight row solely to simplify a script.

Use the Proko hand-mass reference (S01) for broad anatomy. It does not dictate numerical joint angles. A stiff cylindrical pose is not the target; a readable protective sword hold is.

## H1.4 — Shape the four curled fingers directly

**Tools:** Edit Mode selection groups; 3D cursor/custom orientation for pivots; G/R/S at part scope; controlled loop edits; limited proportional editing; optional temporary posing as a starting placement only.

Work on middle and index first, then ring and little. Rotate/reshape selected segments about verified anatomical locations to surround the actual hilt. The distal pad should face the target surface rather than reach it with the dorsal side. Check the underside after every major edit.

Because this is static source modeling, there is no obligation to preserve the failing animator's angle limits. There is still an obligation to preserve plausible lengths, joint form, continuous surface and nonintersecting neighboring fingers.

Add or redistribute a support row only where a bend needs it. Do not solve contact by stretching a fingertip, shrinking the entire hand or moving the fixture. Leave a controlled visible separation/crease between fingers; they may touch tangentially but must not cut through one another.

Temporary disconnected construction pieces are permitted during blockout, but are not the delivered topology. A duplicated tube laid on the palm is not a completed finger.

## H1.5 — Rebuild the thumb and web in the intended closed shape

**Tools:** purposeful control-cage edits; Knife/edge dissolve; Poly Build; extrusion and Bridge Edge Loops; optional local sculpt on a disposable form target followed by retopology.

Place the thumb pad as an exterior opposing surface relative to the selected handle. Establish its proximal mass and the rounded web between thumb and index. Do not require the old web to survive the failed trajectory. Delete and reconstruct the folded candidate patch when needed, preserving the outer transition boundary and wrist interface.

Construct the base with distributed faces following the curved volume. Keep unusually high-valence convergence and long skinny faces away from the narrow web crease. Use enough local control to separate palmar thumb volume, dorsal web and finger root; do not send all three into one sharp pinch.

Bridge boundary loops deliberately, checking edge order/twist. The mere existence of quads is not an anatomical or surface-quality pass. Inspect at base cage and chosen smoothing level.

Do not hide a self-intersecting body layer immediately beneath the glove and claim both are repaired. Follow the explicit output-representation policy in document 03.

## H1.6 — Prove the local glove geometry before scoring contact

Hide the handle for one set of captures. Show palm, axial, dorsal, underside, and the actual cage. Under reversed lighting the web must remain a volume, not a folded sheet.

Inspect all nonadjacent glove triangles for confirmed transverse crossings using existing checked tooling. Classify tangencies, near-coplanar contact, deliberate component interfaces and ambiguous reports separately. Do not equate BVH candidate pairs with confirmed collisions. Do not blanket-exempt all adjacent anatomical regions.

Restore the actual hilt and test the whole contacting surface including triangle interiors, guard and pommel. Sampled pad distance alone cannot clear an intersection.

Failure at this step goes back to mesh form, not to a global curl search.

## H1.7 — Check contact with the correct target and anatomical regions

Declare new semantic pad patches on the final candidate topology before measuring success. Old evaluated vertex IDs are invalid unless correspondence is proved. A new fixed topology may need a new patch record; that is not permission to cherry-pick favorable vertices.

Measure against the selected real handle. Use an ideal cylinder only if it is an accurate declared proxy; document where its profile differs. Report each pad, palm support and thumb facing separately.

The old -0.5 to +1.0 mm band is an inherited comparison screen, not a requirement to push every fingertip into the same analytic cylinder. Aim for no visible gap suggesting floating grip and no confirmed problematic penetration. Use an error tolerance appropriate to world scale and measurement precision, record it before judging, and keep appearance as a separate review.

Do not claim physical force closure or anatomical certification. This is a game-art enclosure/attachment test.

## H1.8 — Resolve the cuff and existing bare hand explicitly

The selected runtime asset is a fully gloved fixed hand. Keep its interior open at the cuff with a proper return/rim if visible, and give it enough overlap with the established forearm/sleeve through supported motion.

A derived runtime-body copy may remove or mask genuinely occluded hand faces, leaving the original body untouched. Record the removed region. Verify all gallery/game cameras and existing clips: no view can see the cut, double shell, missing fingertip or bare palm through a gap.

The glove itself must be correct before this representation change. Do not use it to hide a failed visible thumb or wrist. If any skin is meant to remain visible, preserve and fit that skin instead of omitting it.

## H1.9 — Finish the local surface, then add limited craft detail

Once the shape works, add cuff seam, a few glove folds and a restrained dorsal protective plate if present in the approved design. Keep the palm treatment thin enough not to undo the fit.

Avoid engraving and leather grain until H1.7 passes. The plate and seams must follow hand construction, not cover defects. Check again after any thickness or subdivision change.

Deliver one editable control surface plus an explicit runtime derivative. A clean low-detail hand can be more useful than a dense sculpt whose finger gaps vanish after conversion.

## H1.10 — Handoff to actual animation

Continue to document 03 for bind-space mapping and the seven current clips. Do not simulate or invent finger opening for this fixed task. Record that opening, object exchange and bare-hand anatomy remain unsupported research cases.

If the local static grip is credible, attach the real sword before styling its cuff/bracer. The aim is a useful assembly, not another isolated cylinder study.

## H1.11 — Method limit and fallback

Allow one deliberate construction and two substantive form corrections. If they fail, do not repeat the trajectory method or build another solver. A fallback may use one locally available or properly licensed alternative hand control surface; preserve its origin and redo the actual fit. New paid assets or private-art uploads require approval.

If still blocked, submit the exact failed region and a short specialist brief. Continue independent chest/shoulder design under its own scope rather than declaring the hand done. Do not promise the hand will pass just because this document is detailed.

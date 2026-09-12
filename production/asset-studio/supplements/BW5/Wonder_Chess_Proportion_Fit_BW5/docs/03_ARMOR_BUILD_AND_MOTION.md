# 3 — Build the fitted torso and moving shoulder

## 0. Candidate ownership and tool use

Duplicate BW4's final armor source into a new work location under `stages/body-costume/BW5/armor/`. Reuse its independent garment context and temporary rig only after checking datablock ownership. Retain baseline geometry and the measured rendering setup.

Do not execute an old all-character generator. Do not modify the master MPFB controls, shared rig, game data or unrelated head/hair. Background Blender scripts with inspected render outputs are sufficient. All source-dependent names and vertex sets must be discovered from the real scene.

Use the [proportion contract](02_PROPORTION_CONTRACT.md) first. The operations below implement its chosen dimensions; they do not override it.

## 1. Fit the front plate without discarding useful construction

**Tools:** Edit Mode, vertex/edge selection, explicit scale about chosen sectional pivots, G/R transforms in the verified torso frame, Knife or loop insertion only where necessary; optional independent Lattice.

1. Display the coat in a distinguishable diagnostic tone, the body ghosted or isolated, and the front plate without thickening/bevel/subdivision while inspecting its actual cage. Leave final modifier settings recorded, not deleted.
2. Mark the neckline, armhole boundaries, maximum forward chest position, side returns, waist points and center hem as named semantic selections. Existing arbitrary vertex numbers are not a new recipe.
3. Correct the central plate's vertical occupancy between neck and belt without moving those body anchors. In particular, shortening the visible center plate does NOT mean raising/lowering its whole object rigidly. Adjust the hem, neckline and chest station independently according to the selected reference and collar.
4. In profile, reduce the actual excessive outer-chest projection where it exceeds the chosen envelope, while maintaining room around the final evaluated coat. Work along fore-aft depth at the relevant sections; preserve front width unless its independent fit record says it needs changing.
5. Rebuild the central ridge and adjacent broad planes. Preserve a deliberate sternum/waist transition, rather than globally smoothing until the armor becomes a balloon. The reference's painted brightness changes are not all seam lines.
6. Keep side returns where useful but refit them after any depth/height change. Treat intersections/containment against the padded body and coat as separate from whether a seam looks covered.
7. Restore modifiers one at a time and inspect their effect. Re-measure the final evaluated inner surface. The old clear-front query does not automatically transfer to changed geometry.

**Reject:** a broad slab pushed closer to the torso; an overextended lower point; reduced width obtained by squeezing the undergarment; a fitted front with detached side edges.

## 2. Tailor the collar and close the waist honestly

**Tools:** independent garment Edit Mode, extruded/bridged edge loops, local volume adjustment, normals and retained Solidify settings; simple diagnostic materials.

The current neck/collar and waist context need actual tailoring, not a floating trim added to hide unfinished geometry.

Build a collar that surrounds the existing neck with intended thickness, height and opening, leaving jaw clearance. Its major width must be judged with the compact plate, not in isolation. Do not change the head/neck to manufacture a match. Retain the ivory padded/navy split treatment in material planning; exact quilting is later.

Make the navy waist underlayer continuous between lower torso and belt. The visible band in the reference is fabric-covered space, not a hole into the torso. Establish an intentional side closure and sufficient overlap beneath the plate and belt in all sampled bends. Do not grow belt thickness to hide large openings.

Keep the approved rear tabard split below. Only edit the local upper attachment needed for the torso relationship; do not restart all lower-garment deformation in this task.

Keep body/cloth visibility available for diagnostic review. A later export-only hidden-surface mask may be considered after motion coverage is demonstrated, but is not permitted as the current crossing fix.

## 3. Fit the backplate independently

**Tools:** local cage replacement, Knife/Poly Build where appropriate, open-edge shaping, selective edge returns.

1. Inspect the upper-back/armhole conflict at its recorded source pose and the nearest preceding clean pose; do not invent an onset when the report supplies only a maximum.
2. Identify whether the conflict involves the inner wall, rim extrusion, shoulder connector, or broad shell. Display only the relevant pair, then restore full context.
3. Recut the armhole and upper lateral corner to clear the moving shoulder; reshape an inner return that points into the coat. Do not simply lift the whole backplate away from the back.
4. Fit back curvature to the actual padded torso, keeping broad designed planes. Its lower central hem rises as shown in the new reference. Leave a coherent navy layer beneath it.
5. Reconcile side returns and shoulder straps with the front. A continuous large rigid torso shell can restrict motion differently than separate plate/strap construction; record the chosen attachment and review it instead of welding everything for convenience.
6. Confirm local fit and silhouette in back, both sides and three-quarter. A beautiful back view alone can hide a deep backpack-like offset.

## 4. Solve the padded sleeve before its cap

**Tools:** garment local rest edits, appropriate weight edits, evaluated-pose inspection. Constraints are not collision solvers.

Hide armor temporarily. Inspect shoulder elevation, forward reach, arm across chest, and the range actually present in the 97-frame diagnostic. Look for insufficient underarm volume, gaps, incorrect weights and sharp garment corners separately.

Permit scoped changes to the derived sleeve rest surface or weights when diagnosis supports them. Do not remove padding, collapse cloth onto skin or shorten the motion range solely to make a shell pass. Preserve the old coat and document any candidate change.

The final guard/attack need actual runtime validation later. These authoring probes do not establish that result.

## 5. Shape the cap and two lames as moving construction

**Tools:** Edit Mode shell-cage editing, selective inset/extrude, low controlled subdivision or bevel, explicit rigid parenting/constraints on the temporary candidate, mirrored geometry only where appropriate.

The useful design is a broad shaped cap and subordinate overlapping plates. Avoid hemispheres and identical cylinders. Prototype the anatomical-right assembly first.

1. Mark the cap crown, medial edge facing the neck, rear edge, lower rim and its intended attachment. Inspect which surface actually contacts the padded layer.
2. Reconstruct the medial/rear rim and inner wall at the conflict. Prefer a local cutaway/shorter inward return/changed local curvature when appropriate, rather than moving the complete cap outward.
3. Give the cap a fixed rest attachment and an intentional motion owner. Inspect whether it follows upper arm, clavicle-equivalent or another actual rig transform. Do not presume a bone exists, and do not blend rigid metal broadly as skin.
4. Preserve useful first-lame geometry but re-test it against the revised cap, garment and neighbors. Its BW4 coat query was clear only for its old context.
5. Recut/reposition the second lame at the recorded frame20 onset and its worst measured pose. Reduce the particular offending corner/length or change overlap where justified. Maintain visible coverage and enough sleeve below it. Do not shrink the entire lame until it disappears.
6. Inspect plate-to-plate clearance and ordering, not just plate-to-coat. Sliding overlap can be designed without two solids crossing. Any intentionally touching region must be named, bounded and visually reviewed; a generic adjacency exclusion is not approval.
7. Test the main cap and lower plate relationship in the reference-like lowered pose as well as raised motion. A pose that clears only because all plates flare away is not accepted.
8. If the existing rig owners cannot achieve both reference fit and motion, present the conflict and a candidate-only rig/attachment proposal. Do not silently add bones to the shared game skeleton or keyframe unexplained per-frame translations.

### Use the moving envelope correctly

Inspect coat positions relative to the MOVING plate frame: transform evaluated coat points with the inverse plate world matrix at the same time. A world-space union of a moving arm across every frame can demand an absurdly large shell. Use relative motion to locate local conflicts; it is not an instruction to inflate armor around the union of all poses.

Do not nearest-point shrinkwrap the entire plate to a deforming sleeve every frame. That changes a rigid design into skin-following cloth. Selective Shrinkwrap may help initialize limited fitting controls, but its normal-based inside/outside behavior and projection choices require inspection (B3).

## 6. Detail only the accepted large forms

Once major fit and movement work, add narrow rims, fastening interfaces, modest leather closures and the reference's restrained gold pieces. Match the hierarchy: major steel forms, visible padded sleeves, leather belt, navy waist/tabard, limited gold.

Use bevels to expose designed edges, not uniformly round away the breastplate ridge. Add actual shell thickness after accounting for it in the fitting envelope; do not assume Solidify preserves world thickness on nonuniformly scaled objects (B4). Keep the known garment even-offset corrections intact.

A color-ID preview is allowed now to judge layer separation. It is not final texture approval. Final UVs, quilting, bakes, scratches and cosmetic weathering remain downstream.

## 7. Complete the local assembly

When one shoulder is credible, adapt the other side to its own anatomy and shield clearance. Do not mirror translations or angles blindly across a reflected frame. Keep a labeled baseline version until the counterpart passes the same tests.

Do not wait for a full grip to fit the independent forearm sleeve and proximal bracer shape; the distal wrist/cuff closure still depends on the candidate hand interface. Label that dependency, do not fake a complete arm.

Deliver complete front/back torso, collar/waist enclosure and the prototyped shoulder assembly, with all unchanged parts explicitly marked context. Save and reopen the actual scene, cage, modifiers and selected action.

## Required motion/captures

Re-evaluate all affected surfaces across the 97 original authoring frames; include half/quarter-frame samples near first crossing and peaks as needed. Inspect native frame1 and the worst poses, and review the resulting whole short recording. Keep the original timestamps/action, not a shortened range.

Reports must distinguish raw cage, evaluated surface, transverse crossing, near contact, containment ambiguity, and unsupported continuous-time claims. One repeated static source triangle can generate many pair observations: localize defects rather than treating count alone as severity.

Then preserve a candidate for actual seven-clip integration. Passing authoring motion is not game acceptance.

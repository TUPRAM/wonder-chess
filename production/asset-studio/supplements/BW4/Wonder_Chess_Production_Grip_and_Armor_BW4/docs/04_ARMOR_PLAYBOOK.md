# 04 — Ada's armor: construct it, articulate it, then detail it

**Task A1/A2. Target: a finished-looking cuff/bracer plus a coherent chest/back/one-shoulder assembly.**

This is original proposed art direction applied to Ada. Museum objects illustrate construction relationships; they do not replace the approved concept or dictate literal historic reproduction. Do not add a locking gauntlet, ornate engraved suit, giant tassets or a different shield just because they appear in the research.

## A. The visual contract

Ada remains a grounded human guardian: ivory padded underlayer, navy tabard, controlled steel surfaces and restrained gold. Keep the approved rear tabard split, shield on anatomical left and sword on right. Use the current approved written construction decisions where the concept sheet is inconsistent. Head/hair remain outside this pass.

The armor should read as protective manufactured pieces with attachment, edge thickness and clearance. It should not read as hemispheres, inflated torso pieces, flat cutouts or continuous metal sleeves that bend like skin.

Large shapes: shoulder span, chest curvature, waist taper, shield. Medium shapes: plate boundaries, overlapping shoulder plates, collar, cuff, strap/buckle, major quilting. Small shapes: rivets, engraved borders and wear. Do not begin with the small shapes.

## B. Before modeling: a short construction sheet

Choose one actual body/undergarment candidate at its approved scale. Capture front, back, both sides and three-quarter. Mark neckline, waist, shoulder rotation area, elbow, wrist, sleeve opening and where each armor part ends.

List each part's proposed owner: chest bone, forearm bone, upper-arm bone, existing shoulder bone if present, or soft cloth deformation. These are not assumed bone names. Inspect what exists in the 27-bone rig.

Create a candidate collection with separately editable parts. Do not rebuild the 24-hero roster, retarget everything, or install a physics package for this study.

Use [armor_parts.template.json](../templates/armor_parts.template.json) as a small planning record. Its empty fields are not measurements.

## C. Gauntlet exterior and cuff — after hand fit

**Purpose:** finish the hand visually without damaging its accepted grip.

1. Start from H1's clean glove, not the failed BW3 web. Keep the palm and finger contact surfaces locked while adding dorsal treatment.
2. Duplicate only the intended dorsal plate region or draw a new patch with Poly Build. Offset deliberately from the glove, then reshape so it reads as a plate, not a skin copy.
3. Establish a simple metacarpal shield and restrained knuckle protection if consistent with Ada's concept. Individual fingers must stay recognizable. No mitten silhouette by stealth.
4. Use narrow secondary finger protection only where it contributes at gallery scale; avoid a complicated moving miniature mechanism for a fixed-grip hand.
5. Build a flared cuff with a clear mouth and return edge. Keep the wrist bend area free. The cuff may follow the hand while the bracer follows the forearm; test that interface rather than joining everything rigidly.
6. Add a fastening seam/strap where visible. Keep gold accents small. Recheck guard and pommel clearance after adding any plate or rim.

**Reference use:** S13/S14 for palm-versus-dorsal separation; S15 for overlapping plate logic, not its special lock. Museum ornament is not copied onto Ada.

## D. Bracer — the first completed hard-surface asset

**Tools:** edited cylinder/plane strip; Loop Cut; extrusion; inset; deliberate shell thickness; Bevel; normals inspection.

1. Measure two or three cross-sections along the actual forearm in the chosen rest pose. Elliptical proportions are a construction decision, not permission to clamp tightly around every skin contour.
2. Create a tapered outer shell using a modest number of radial edges. Avoid a straight cylindrical tube. Establish the dorsal ridge/planes, lower wrist opening and upper cuff shape.
3. Add a plausible inner opening or separate inner plate/straps. The BW1 bracer's excessive back opening must not remain an unexplained gap.
4. Give the shell thickness. Add a deliberate rolled/rimmed edge using an inset/extruded strip, or a separate controlled curve profile for a truly shaped rim. Do not place torus rings on every opening.
5. Add a selective Bevel modifier to relevant boundaries. Use width in measured object units and inspect actual cross-sections. Start with few segments; add more only for visibly necessary curvature. Hardened/custom normals can improve shading, not change the silhouette (S05).
6. Bind the rigid bracer to the existing appropriate forearm bone in a candidate runtime rig. A soft strap may use separate compatible weights; do not make the plate rubbery to cover cuff failure.
7. Inspect wrist twist, elbow flexion, sword guard sweep and shield interference through actual actions.

**Acceptance:** readable taper/edge construction, deliberate underside closure, no sharp penetration, stable motion, correct silhouette at the actual gallery distance. Leather grain alone does not satisfy it.

## E. Breastplate and backplate — surface design before thickness

**Tools:** low-density plane/control cage; Mirror where appropriate; proportional editing/Lattice on new shell only; edge extrusion/inset; Solidify; selected bevels.

1. Establish an armor envelope outside the padded underlayer. A few measured front/side/back sections provide fit constraints. Do not use the body skin as the final armor surface.
2. Model one intentional thoracic shell with neckline and arm openings. For Ada, use a broad, coherent chest plane/curvature and a compact waist; do not split it into two decorative bust cups.
3. Add the important plane changes and a restrained central ridge only if it agrees with the selected concept. The side view should show meaningful depth, not a flat breastplate pasted onto a chest.
4. Turn the lower edge away from the abdomen enough for the selected waist/cloth transition. Avoid a deep cutting edge aimed into the pelvis during bend.
5. Build the backplate independently to fit the scapular area and waist. Show its fastening relationship to the front through shoulder/side straps or overlapping side pieces. Do not leave it floating far behind the body.
6. Inspect raw surface, symmetry seam and open boundaries. Apply scale only on the safe new modeling object or account for it explicitly; never blindly apply transforms to the animated master.
7. Add shell thickness with Solidify or manually modeled inner/outer surfaces where required. Set offset intentionally relative to undergarment clearance. Check normals and inside views.
8. Add rolled or thickened edges as actual construction details. Distinguish broad shape curvature, silhouette rim and tiny bevel. Do not use one enormous Bevel to imitate all three.
9. With the shell acceptable in clay, add only the fasteners needed to explain construction. Keep decorative etching for the later bake/material pass.

**Suggested experiment values, not recovered measurements:** new steel shell 2–4 mm thickness, small edge bevel around 0.4–1.0 mm, selected visible rolled rim around 4–8 mm. Choose a single consistent set appropriate to Ada's actual scale, then inspect; these are not historical or shipping requirements. A rim can be larger than the shell wall because it is a separate shaped edge.

**Reference use:** S16–S18 explain why neckline, arm opening, waist and side attachment deserve their own construction. Do not import museum torso dimensions into Ada.

## F. One shoulder/sleeve assembly — the decisive articulation proof

**Tools:** continuous sleeve cage; dedicated pauldron shells; simple candidate bone attachments; actual action playback; only later constrained helper experiments.

1. Hide the armor and fix the padded sleeve first. Inspect armpit, shoulder cap, elbow and cuff while raising/bending the arm. Establish adequate rest volume, an intelligible underarm region and appropriate weights. A static enclosure pass is not a moving-sleeve pass.
2. Design one main shoulder cap with a flatter top/controlled convex side, a clear lower edge and front/back asymmetry suited to Ada's pose. Avoid a hemisphere and avoid concentric horizontal band cylinders.
3. Add a small number of subordinate overlapping plates. A starting design of one cap plus two lames is a proposed simplification, not a mandatory exact copy of historic armor. Match the approved silhouette first.
4. Draw which plate covers which at rest and at key action extremes. Leave deliberate overlap and volume for the sleeve. Each plate should have a reason to end where it does.
5. Assign each rigid component a defensible existing bone/attachment. Test existing upper-arm/shoulder/chest options before proposing extra helper bones. Do not invent a perfect runtime hinge that has not been implemented.
6. Evaluate the actual seven clips and state transitions. If a plate collides, first adjust its cutout, overlap, pivot/owner or rest clearance. Do not shrink the arm or cut away exposed skin just to clear it.
7. If a temporary authoring helper is necessary, label it AUTHORING_ONLY until the behavior has a compatible runtime representation. Preserve the shared rig; a proposed rig amendment is a separate decision.
8. Show cap/lames alone, sleeve alone, and complete assembly under neutral/reversed light. Open joints can be believable when the underlayer is present; empty holes into the body are not.

**Reference use:** museum shoulder and breastplate records distinguish assemblies; the exact Ada attachment design is ours and must be tested. S19's fetched page did not provide its image, so it cannot justify an invented hinge detail.

## G. Materials and detail after the above shapes pass

Use consistent base-color and roughness treatment across glove leather, padded cloth, steel and gold. The reflected highlights should reveal the designed planes, not turn every piece into a glossy inflated cap.

UV seams should follow underside/part boundaries where appropriate; keep scale consistent within each material family. Plan any mirrored UVs and asymmetrical heraldry explicitly. Do not stamp identical damage on both sides by accident.

Bake shallow quilting/engraving from appropriate detail geometry, or paint those details intentionally. Keep rim silhouette and large plate layering in geometry. Inspect tangent normals and seams against the actual runtime triangulation. S23 documents the relevant bake features; it does not guarantee the chosen bake is correct.

The optional ArtStation mask breakdown (S21) is for later material organization. Do not add multiple damage states now. The optional Blue Spirit armor (S20) is a study model requiring license verification, not a replacement for Ada's approved design.

Review at gameplay size, gallery size and diagnostic closeup. Small detail may be simplified or baked; major surface failures cannot.

## H. Later pieces, not all blockers for this assignment

After A1/A2: complete the other shoulder with independent clearance, waist/tabard deformation, knee/greave articulation and boot finishing. Preserve the improved sole and rear split. BW1's failed knee parenting recipes are not reused as proven methods.

A whole Ada release still requires the existing head/hair status, materials, all clips, engine review and user approval. Hand/armor local completion does not erase those open items.

## I. Bounded output for the next pass

Deliver: H1 fixed hand + chosen sword fit, wrist assembly, one refined cuff/bracer, chest/back clay model, and one shoulder/sleeve proof. Where a dependency or method fails, retain that status and complete only independent work. Do not turn the session into another catalog of unexecuted scripts.

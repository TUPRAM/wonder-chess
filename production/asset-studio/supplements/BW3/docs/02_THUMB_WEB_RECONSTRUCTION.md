# BW3 — Anatomical-right thumb/web and finger-clearance procedure

**Proposed authoring procedure. Not an executed correction or guaranteed outcome.**

## 0. Make a real editable branch

Use the frozen BW2 file as an immutable baseline; inspect the live session for unsaved user work. Save a distinct BW3 work file in a new unused directory. Record actual object names rather than assuming new names already exist.

Create independent copies of the relevant body, glove, rig data and diagnostic action. Inspect mesh/armature/action/shape-key users and every modifier/constraint target. Point candidate influences to the candidate rig; do not let a duplicated modifier still evaluate the original rig by accident. The master remains available for comparison but outside the candidate render allowlist.

Preserve world transforms. Do not apply object transforms on the skinned originals. Keep the wrist frame and fixture parent chain intact. If changing thumb-rest controls on the candidate, revalidate affected thumb axes and bind behavior; do not re-probe unrelated joints.

Retain the full indexed master. When a localized topology rebuild requires dropping generator correspondence, do so only in an explicitly derived hand/glove output with recorded source mapping and a fixed wrist-interface boundary. Never pretend its changed vertices are still the original MPFB indices.

## 1. Observe the first failure rather than the final fold alone

Temporarily return candidate digits to their recorded open state. Save that pose. Keep the handle transform frozen and its analytic/mesh collider enabled even when hidden from renders.

Inspect body alone, glove alone, and combined with differentiated diagnostic material. Use armature-deformed unsubdivided cages as well as the normal evaluated meshes. These are different observations; do not compare raw-rest body to evaluated posed glove and call it a weight difference.

Replay the old closure only for diagnosis. Locate the first failing intervals for: thumb/palm crossing, thumb/index/middle crossing, middle/ring crossing, and any glove/handle penetration. Refine temporal sampling around onset. The uploaded data only establishes maximum handle penetration at14, not the first self-crossing or its cause.

At the failing interval, use explicit vertex/face selections to inspect which influences move the crease and which side of the surface folds. Existing inspection seeds are pointers, not an approved correction mask. Log the frame, affected region, intended movement, actual movement, and one causal hypothesis.

## 2. Isolate one cause

With index through little fingers relaxed, test the thumb base/opposition alone. Reintroduce thumb flexion next, then non-thumb closure. This distinguishes a failing thumb path from crowding caused by closing all digits together.

Choose the smallest method that matches the observed failure:

| Diagnosis observation | Candidate intervention |
|---|---|
| Base/pad travels through the palm even before a large web distortion | Correct the staged thumb trajectory or candidate control distribution; inspect rest pivot/axis only when needed |
| Correct bone motion but the web is pulled by inappropriate influences | Local weight repair with preserved surrounding groups and pose evidence |
| Reasonable motion/weights but the web lacks a usable volume or support surface | Reshape or rebuild that local rest surface on a derived copy |
| A local surface fails only in a known supported pose range | A verified pose corrective with explicit activation and runtime status |
| Glove fails independently of a correct body | Repair garment fit/weights independently rather than deforming the body to compensate |

These rows describe tests, not diagnoses already proved by BW2. No automatic full reweight or general rig regeneration.

## 3. Construct an external thumb path

The intended visual action is a continuous thumb base that moves away enough to clear the palm, sweeps around toward opposition, then flexes to meet the handle with the pad. Determine suitable local rotations from the actual rig; no generic Euler angles or anatomical range numbers are imposed.

Work with deliberate intermediate key poses, not only linear interpolation from one open pose to a forced final pose. A key on frame1 and a key on25 do not guarantee a valid route between them. The exact timing is a modeling decision: inspect both joint angles and evaluated surfaces before adjusting interpolation.

Preserve a broad fleshy thumb-base volume and a web that forms a valley, not a sharp sheet stretching diagonally across the palm. Thumb pad orientation should become external without relying on large distal axial twist. The old distal-Z bounds are search limits, not targets.

When the thumb silhouette becomes plausible, restore the fixture's visibility and check whether that route clears the actual handle. Temporarily missing pad contact is allowed while discovering a valid path; self-crossing is not a valid intermediate candidate to optimize for contact.

## 4. Local weights/rest shape/corrective, when justified

### Local weight repair

Inspect existing influences on both sides of the web. Remove only demonstrably wrong influences, preserve intentional blending, normalize the affected weights, and compare the same poses before/after. Do not copy a hard binary palm/thumb mask into a region that needs a smooth transition. Do not assert that the known143-vertex set is accidentally weighted100% to the wrist: BW2 reports otherwise.

### Rest-surface reconstruction

If required, reshape the thenar mass and web in the candidate's correct rest space. Preserve continuity, wrist boundary, finger lengths and unaffected silhouette. Rebuild local edge flow only when needed; adding subdivision does not untangle a crossing cage. Test neutral, partly opposed, partly flexed and closed states after each structural revision.

Both body and glove must be handled consistently. MakeHuman fitting correspondence, skin weights and diagnostic pad labels are separate data. If body geometry changes, refit the glove without assuming that old fitting correspondence remains semantically correct. Do not paste identical deltas between noncorresponding vertices or apply unrestricted nearest-surface transfer between adjacent fingers.

### Pose corrective

Blender shape keys store positions on the object's shared topology [W2]. Use an independent candidate with a Basis and a clearly named corrective. Where the installed Armature modifier supports edit-cage display, first test a single reversible vertex edit to verify its effect in the deformed view. Edit only the intended key, then test its influence at0, intermediate values and1 across the required poses.

A sculpted evaluated mesh is in a different state from a pre-armature shape key. Do not paste its world positions directly into a rest-space key and then deform them a second time. Use verified cage editing or an explicitly validated transfer in the correct coordinate/deformation space. A same-topology count does not establish correct space. If a transfer cannot be validated, retain the sculpt only as a reference, not as a functional corrective.

Do not perform a singular or unverified inverse of blended skinning transforms. A single inverse bone transform applies to a rigid hand-space conversion, not generally to vertices driven by multiple finger bones. DQ and nonlinear modifier stacks require different reasoning.

A pose-driven correction should respond to the relevant pose, not merely a hard-coded frame number. Frame-keyed corrections can be retained as diagnostic-only; arbitrary body/arm motion must not trigger or double-apply the correction.

References [W1]/[W2] are API/mechanism context, not evidence that the correction works. Retain the failed Preserve Volume comparison; do not rebrand it a new solution.

## 5. Resolve middle/ring clearance before final contact

Keep the thumb in a known clear state while studying middle/ring independently. Examine their base spread, proximal flexion, middle joints and distal segments together. Move only controls with a demonstrated effect in the measured hand frame.

Restore natural knuckle staggering and a compact wrap. Do not create large unnatural gaps, shorten bones, scale entire digits, or interpenetrate one digit to let another reach its sample targets. Contact between adjacent skin surfaces may be intentional; transverse crossings, trapped/inverted web surfaces and visibly collapsed pads are not.

Reintroduce the thumb and test it against index/middle. Reintroduce index and little if they were relaxed. More than one valid sequence is possible; choose the sequence supported by the current geometry rather than forcing all joint curls to share one timeline ramp.

## 6. Restore contact with a feasibility-first rule

Keep the original28mm/105mm usable fixture and single parent chain. Use the declared pads' anatomical intent from the open state. Where topology is unchanged, verify stable evaluated correspondence before retaining IDs. If changed, record a reviewed remapping before fitting. Do not choose the closest vertices after seeing the result.

At each new pose candidate: evaluate self/neighbor collisions, body/glove validity and whole-surface handle penetration first. Only feasible candidates can be ranked for pad distance, apparent enclosure or smoothness. A weighted loss must not trade a confirmed crossing for better contact.

The original negative0.5 to positive1.0mm band remains a screening tolerance, not a license for visible penetration. Keep the original per-digit screen as a comparable result; report any unmet contact rather than driving through the hand to satisfy it. A changed acceptance target needs a separate explicit version, not quiet relaxation.

If the original fixture is shown unsuitable, stop and document why. An alternative diameter or placement is a new fitting study requiring approval/versioning; never move it per frame or per finger.

## 7. Integrate the real sword only on success

Fit the existing sword grip to the same verified frame and usable span, in an independent equipment copy. Check guard/pommel against fingers, glove and bracer. Do not change the grip pose to accommodate a new handle without rerunning the checks.

Produce the local result and stop for review. The left shield grip, elbow armor and cloth remain independent next tasks. A right-side proof is not approval of them.

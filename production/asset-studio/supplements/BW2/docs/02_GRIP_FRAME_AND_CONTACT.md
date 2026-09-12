# BW2-G1 — dimensioned hand frame and reliable grip

**Goal:** A believable anatomical-right sword grip whose evaluated glove surfaces surround a fixed handle, with opposing-thumb contact and stable carrying through the required motion.

This is an executed Blender art/rig task, not an instruction to build a new autonomous grasping framework. Keep the live tools; use Edit/Pose Mode, named empties, constraints, real captures and small scripts where useful.

## 0. Establish source and scope

Preserve frozen r003. Create an independent candidate, armature/action copies as needed, and a new owned diagnostic collection. Do not alter the complete indexed MPFB source or its original target system. The fitted glove is a licensed adaptation; preserve provenance/UVs in its source. Local copied weights or fit may change when justified.

Find the actual temporary hand and finger chains; do not assume names. Confirm finger-base joints, middle/last joints, thumb base, hand bone, armature transforms and evaluated glove. List them in `hand_contract.json`. Check whether source bone points are REST or POSE data before use.

Use an open neutral hand for calibration. A closed fingertip is not a stable definition of finger-forward.

## 1. Put landmarks in one coordinate frame

Read actual evaluated wrist, middle finger-base joint, index and little finger-base joints, middle fingertip and an explicitly identified palm-side surface point. Finger-base joint is anatomically MCP (metacarpophalangeal); this is unrelated to the editor's Model Context Protocol.

For a pose-bone endpoint already in armature space:

```python
# Illustration of the conversion; use the ACTUAL evaluated objects/names.
depsgraph = bpy.context.evaluated_depsgraph_get()
rig_eval = rig.evaluated_get(depsgraph)
pb = rig_eval.pose.bones[actual_name]
world_head_bu = rig_eval.matrix_world @ pb.head
world_tail_bu = rig_eval.matrix_world @ pb.tail
# Convert BU to metres once, using the verified scene length convention.
```

Do not multiply pb.head by pb.matrix again. A pose matrix represents a bone-local transform in armature object space; endpoint data and local vectors are not interchangeable. Use the installed Blender API/space conversions when assigning rotations, especially with constraints and parent inheritance. [S1]

Evaluated mesh vertices use their own evaluated object matrix. Body-local vertex coordinates cannot be compared directly with armature-space joints or world-space handles. Transform points with translation; directions without translation; normals with the appropriate inverse-transpose when nonuniform transforms matter.

Check unit conversion with the measured body/hand dimensions. Do not multiply by 100 because Unreal eventually uses centimetres: this authoring task is metric world space. Do not apply Ctrl+A to an already rigged or keyed source merely to simplify arithmetic.

## 2. Build a semantic hand frame

Use these proposed semantics, not Blender's unknown bone-roll convention:

- Origin: wrist landmark O.
- Y: distal direction from wrist toward middle finger-base joint.
- X: across the finger bases, orthogonalized against Y.
- Z: perpendicular to X and Y, oriented toward the palm side.

Pseudocode:

```text
Y = normalize(middle_base - wrist)
raw_X = index_base - little_base
X = normalize(raw_X - dot(raw_X,Y) * Y)
Z = normalize(cross(X,Y))
if dot(Z, known_palmar_point - midpoint(wrist,middle_base)) < 0:
    X = -X
    Z = -Z
```

Keep Y fixed. Flip X and Z together when needed: the frame must remain a proper right-handed rotation with determinant +1. Record whether X points anatomically toward the index or little finger. Its anatomical sign need not be the same on both hands.

Validate:

- `(middle_tip - middle_base)` points substantially along +Y in the OPEN pose, not toward the wrist.
- Axes are unit and mutually orthogonal; no negative determinant.
- The palm-side marker is genuinely off the joint plane and visible as palmar, not guessed from a bone name.
- World→local→world round-trip is consistent.
- Nonuniform scale, shear, or negative transforms are identified, not silently discarded. The supplied math helper intentionally rejects such transforms; use explicit full-space handling for the real rig or fix only a permitted candidate setup.

Create small named axis markers and show palm/back/side captures. Use a color scheme with labels; do not depend on color alone. This is the one calibration approval by actual inspection required before curl fitting, not a human gate for every coordinate.

Store the frame relative to the evaluated hand bone at calibration. During motion propagate that stored frame with the hand bone. Recomputing it from curling fingertips causes a moving target and circular fitting.

## 3. Check flexion axes with reversible probes

For each finger chain, identify the intended flexion axis in its local joint frame. Apply a small test angle (for example +5 degrees), update the scene, observe endpoint/surface displacement, then restore the exact prior pose. Reverse sign when the probe extends away from the intended palmward curl. Test the thumb separately; opposition is not merely the same curl as an index finger.

Record axis, sign, zero pose, safe working range and actual control used. Do not infer all finger rotations from one world axis. Do not use the same Euler sign on left and right merely because names end in .L/.R.

The new calibration is a genuine method correction to BW1's wrong-frame failure. Once it is correct, artistic contact still requires inspection and adjustment.

## 4. Create one dimensioned handle proxy

Choose a neutral circular cylinder with labeled axis endpoints A/B, radius and usable length, and cap-exclusion margins. Its axis is across the grip, not finger-forward. Measure the current intended sword grip along its actual axis; an oblique world-axis-aligned bounding box is not its true radius/length.

Where a clean initial fixture is needed, **28 mm diameter × 105 mm usable length** is a proposed diagnostic starting point. It is NOT a recovered Ada measurement or a mandatory sword design. Fit it once against the actual palm, glove thickness and approved weapon proportions, record the decision, then lock it for the curl study.

Place the cylinder just above the palm-side contact region, with enough room for the curled digits and an opposing thumb. Confirm both ends and the side view. Keep the blade/guard out of view during the pure-cylinder fit to avoid confusing handle placement with a dramatic weapon pose.

One directed dependency graph:

```text
arm/hand control -> hand bone -> fixed local handle frame -> weapon
                -> finger joint rotations -> glove deformation
```

Do not simultaneously drive the same hand from the weapon and the weapon from that hand. Do not attach equipment through both bone parenting and a second equivalent constraint/armature influence.

For ideal rigid frames, use `T_weapon_world = T_hand_world @ T_weapon_in_hand`; record the relative transform once. Blender Child Of and normal bone parenting have their own inverse/rest behavior. If Child Of is used, verify the Set Inverse behavior through actual before/after transforms rather than repeatedly clearing it until the picture looks right. [S2]

## 5. Close individual fingers and the thumb

Use Pose Mode with the verified local axes or bounded assignments to the actual controls. Preserve phalange lengths; do not scale finger bones to reach the cylinder.

Start with the middle finger to establish one useful contact, then ring, index and little. Work proximal-to-distal in small increments. Examine the knuckle arc, intermediate joint positions and tips. The aim is an enclosure, not five tips coincident with the same target.

Then solve the thumb base/opposition and its subsequent flexion, using a real pad region on the other side of the handle. Avoid thumb tunneling through the cylinder, self-intersection with the index, or a floating thumb posed merely for the camera.

Do not prescribe a universal set of finger angles. For each chain the existing hand proportions, glove envelope and handle position determine the usable pose. Use the connected foundation, not newly added finger tubes.

A weak glove fit and a wrong bone pose are different causes. Review body skin and glove separately. Correct copied glove weights within the intended digit groups; uncontrolled nearest mapping can connect adjacent fingers. Do not deform a protected source or normalise MHCLO fitting coefficients as though they were skeletal influences.

## 6. Measure small, predeclared contact patches

Select visible glove pad patches before assessing results: middle/ring/index/little and thumb, plus a palm support region where appropriate. Record their mapping to the evaluated surface. Base indices may not match modifier-generated vertices; use a deliberate correspondence or a stable triangulated/barycentric sample scheme.

For a diagnostic capped circular cylinder, the supplied helper computes signed distance and radial side gap. Negative means inside; positive means separation. Do not confuse bone-tip distance with skin/glove-surface distance. Points near the ends must be screened against usable axial length; touching a cap is not proof of wrapping the side.

**Proposed screening targets, adjustable only by a declared fit decision:**

- Meaningful pad region on every required digit, not one lucky closest vertex.
- At least half the selected localized pad samples within -0.5 to +1.0 mm of the cylinder side.
- No sampled penetration deeper than 0.5 mm, and no visually meaningful mesh penetration.
- Smallest-to-largest gap, median and p95 reported separately per patch.
- Opposing thumb and fingers visibly enclose the grip; thumb-side contact is not on the same exposed face as all fingers.

These are prototype tolerances, not biological laws or proof of physical force closure. Adjusting the tolerances to hide a failed grip is prohibited. The glove may require a designed compression allowance, documented explicitly.

Check the full evaluated triangles and moving surfaces for additional collisions; sampled-point distances alone can miss a crossing face or an unselected region. An ideal cylinder metric is invalid for a substantially elliptical/nonuniformly scaled or differently shaped production handle. Use the actual handle mesh for that stage.

## 7. Freeze contact and test carrying

Retain a reviewed grip pose and a fixed handle transform in the hand frame. Test open-to-close, hold, wrist turning, elbow bend, arm raise and the intended guard/attack path. Use at least a short continuous movie plus axial/palm/back/side closeups.

The handle must not move independently to keep contact in each frame. Report drift in the hand frame: a proposed screen is ≤1 mm translation and ≤1 degree orientation change for a supposedly rigid held prop, with actual matrix/numeric precision documented. This is an engineering screen, not a substitute for visual grip quality.

Do not require contact in a deliberately open-hand segment; label phases so open→close does not falsely count as persistent contact failure. Freeze the grasp evaluation set once closure begins and inspect all closed/held frames. Keep the original 169-frame action unchanged; create a separate owned action or explicitly documented overlay for this study.

## 8. Replace proxy with actual sword, then adapt the shield

Fit the actual sword grip to the fixed approved proxy frame and inspect guard/finger and pommel clearance. Don't move the hand to conceal a grip shape that differs from the proxy. If the actual grip cross-section needs a small permitted change, record it and rerun contact checks.

Once successful, independently calibrate the left hand. The shield's handle, panel clearance and forearm strap produce different constraints. Do not literally mirror the right-hand matrix, sword pose or curl angles. Preserve the approved equipment handedness.

The shield must not pull the hand through the panel or lock the wrist through competing parents. Establish one primary owner, then fit the passive strap/visual contact without cyclic dependencies.

## 9. Deliver and stop

Save/reopen the candidate and source-bound screenshots/movie; report actual data, not a prose-only result. Provide measured frame/handle JSON, per-patch screens, scope changes, and top remaining defects. No unrelated head/cloth/knee edits in this proof.

A local reviewable grip is not full-body approval, a successful replay, a runtime skeleton decision or a trained model. Only then schedule the next assembly. If the genuine calibrated method still fails after two non-improving corrections, retain it and return a specific failed contact/axis/fitting mechanism, not another unrestricted “polish everything” task.

# BW2 — separate assembly tasks after the grip proof

These are queued bounded tasks, not simultaneous demands for the next session. Each task changes a named dependency and requires one visible improvement before repetition. All numerical sample poses below are proposed diagnostic values; verify safe axes and compare the actual game's required ranges.

## Task G2 — sleeve / pauldron / bracer

**Do not try to fix a cloth opening by adding another armor band.** The soft clothing should provide enclosure; the armor should provide rigid protection and its intended silhouette.

1. Retain the connected upper-coat source and its corrected Solidify setting. In a duplicate, inspect clavicle, shoulder and elbow joint placement, rest pose, garment openings, topology and current weights with armor hidden.
2. Distinguish designed open edges at collar/cuff/hem from holes, intersections or too-little volume. Identify whether the shoulder failure is insufficient garment ease, missing geometry, a wrong rest fit or incorrect weights.
3. Shape the underarm and sleeve cap with enough material for the intended range. Add only the local supporting topology needed. A cloth gusset is an option, not a requirement to add a visible patch to every character. Do not shrinkwrap the complete sleeve tightly to the skin.
4. Test the unarmored sleeve in neutral, forward reach, raised arm, elbow bend and wrist rotation. Proposed samples: elbow 0/45/90/120 degrees and arm raise 0/45/90; classify any extended range as stress-only when not used by game animation. Blend across clavicle/upper-arm/forearm intentionally. Restrict transferred weights and inspect them rather than assigning the nearest bone indiscriminately.
5. Once the sleeve encloses correctly, fit one pauldron's upper shell and lower lames as rigid parts. Establish a fixed attachment relation to the shoulder/clavicle and an explicit movement policy for each lower plate. Give each plate one owner; do not make overlapping matrices accidentally scale/bend a rigid plate.
6. Pose the arm through the same sequence. Inspect plate overlap, undergarment coverage, clearance to chest/back plate and inward edges. Some mechanical separation is intentional; exposed voids, skin clipping and detached plates are not.
7. Fix the bracer as a tapered forearm shell with explicit wrist opening and fastening/undergarment coverage. Do not fuse the bracer to the glove simply to hide a cuff gap. A visible opening can be legitimate if the underlying material and construction are coherent.
8. Where residual soft deformation remains, a constrained local Corrective Smooth/shape correction may be tested only after rest fit and weights are correct. Blender's Corrective Smooth is a deformation correction, not a clothing collision solver; its rest/bind settings matter. [S3]
9. Deliver paired naked-sleeve/armored motion views and one whole-arm view with the already solved grip.

**Runtime note:** A temporary pauldron helper or pose corrective must be labeled AUTHORING_ONLY until its game representation is chosen. An authoring-space constraint is not automatically a runtime bone or driver.

## Task G3 — one moving hanging panel

BW1 reported thigh penetration into root-weighted panels. Disabling Solidify spikes did not supply cloth motion.

1. Preserve the approved front/rear garment separation, especially the rear tabard split. Identify actual independent panels and waist attachments. Do not turn two split panels into one rigid skirt tube.
2. Establish a clearance envelope with the actual posed thigh, not a vertex copied from the rest body. Audit root-only influence on the moving portion.
3. Keep waistband/upper attachment controlled by pelvis. Give each lower side panel a deliberate relationship to the corresponding thigh or a dedicated authoring control. Do not make the whole front panel rigidly follow one thigh and drag the opposite side with it.
4. Initial candidate: smooth, localized pelvis-to-same-side-thigh weighting on the lower panel, preserving rest flare and seam topology. This is a starting method, not a guarantee. Body-weight transfer alone may cling the panel to a leg or produce a cross-body bridge; inspect before accepting.
5. Test forward step, backward step, opposite-leg step, hip spread and kneel. The source reports game thigh range ±22° and calf range 19°, but their axes differ from MPFB. Recreate equivalent world-space motion before calling it runtime coverage; do not copy those Euler angles blindly.
6. If simple skinning cannot keep the desired drape, use a small independent authoring panel-control chain or a targeted pose corrective. The next task must declare its export path. This is preferable to quietly enabling a simulation dependency for the whole roster.
7. For a shape corrective, construct the required delta in the correct pre-skin/reference space. A sculpted evaluated pose cannot simply be copied as an unposed shape key without accounting for deformation, or it may be deformed twice. Verify intermediate weights 0/.25/.5/.75/1 and combined joint poses, not only the sculpted endpoint.
8. Preserve hem/cuff/waist thickness and the BW1 even-offset fix. No deletion masks, changed camera, raised skirt length or hidden leg may be used as an undeclared way to erase the penetration.
9. Scan every frame of the original range probe plus the new candidate motion. At fast transitions inspect intermediate samples. Numerical scans screen for outliers; they do not certify zero continuous-time collision.

**Recommended first target:** a correctly moving split panel under the actual walk range. Deep kneeling remains an explicit stress test if the current gameplay never uses it. Do not label failure at a required attack/defeat/kneel as stress-only merely to pass. Keep the prior diagnostic result in the record.

**Not first:** full dynamic cloth. It can be evaluated later in Unreal with explicit cost, collision and reset behavior. A Blender cloth cache is not a runtime cloth implementation.

## Task G4 — articulated knee, greave and improved boot

The retained knee cup is not a proven articulated structure. Prior shin-parenting, thigh-side parenting, blended pivot and weighted surface-proxy attempts failed according to BW1. Do not retry the same relationships with new arbitrary offsets.

### Knee control proof

1. Isolate one knee with body, trousers, thigh edge, kneecap shell and greave. Observe at rest and several bend states from front/profile/three-quarter.
2. Locate the real evaluated knee joint in one common frame. Label the rest attachment frame, surface-facing direction and shell offset. Do not use an object-origin guess, averaged global Euler angles or a current nearest skin point that can jump between surfaces.
3. Build a temporary dedicated rigid knee control in the candidate. Keep the cup's geometry rigid and independently shape its shell. This control is an authoring experiment, not permission to add a production joint.
4. At bends such as 0/30/60/90/120 degrees, explicitly pose the cup to maintain useful front-knee coverage and clearance. Record its local transform relative to the verified joint frame. Inspect actual skin/body motion: do not assume a static midpoint is the anatomical kneecap trajectory.
5. Interpolate only after the sampled poses work. Use coherent quaternion/local-frame rotations, not elementwise matrix averages that can introduce scale/shear. Sample between authored angles and during the original motion to find drift or popping.
6. Give upper and lower lames intentional overlap with the thigh piece and greave. A rigid plate must not stretch like rubber to conceal missing overlap. Keep visible fabric or a constructed strap beneath legitimate openings.
7. If the desired shape and whole diagnostic range require unsupported controls, choose an explicit design/export decision. Do not silently shorten the range, widen the cup until it floats, or disable a failed action.

### Boot junction proof

1. Preserve the improved anatomical-right footprint sole and its scale. Compare it with the old left blockout only as baseline; neither approves the whole boot.
2. Establish a shared seam/lip between the upper, heel and sole, with intentional overlap or welded construction as appropriate. Remove z-fighting and actual through-gaps rather than adding floating decorations.
3. Resolve influence by region: sole/toe/foot upper follows the foot; shaft follows its appropriate calf/ankle blend with a designed flex region. A stiff shaft and flexible ankle should not be assigned one arbitrary weight distribution.
4. Test ankle bend, foot roll, planted foot, step and knee bend. Confirm greave-to-boot clearance. Do not scale the foot to fit a poorly shaped boot.
5. Only after one complete side works, reproduce the method on the other side using separately validated transforms. Do not just negative-scale the rigged object and assume handedness/normals are correct.

## Task G5 — tailoring and silhouette finish

After the assembly moves, refine its actual appearance: breastplate/backplate clearances, collar and seam design, curved shoulder shells/lame thickness, purposeful bracer shape, cloth flare and large folds, boot seam/sole construction and scale of fasteners. Review against the approved reference from full-body and gameplay viewpoints.

Do not solve every face by projecting it tightly to the body. Armor needs designed planes; cloth needs volume. Do not add stitching, roughness noise or 4K textures while the assembly still floats or penetrates.

A correct coordinate frame and collision screen do not make a slab-like garment beautiful. The final part review must cover both movement and intended style.

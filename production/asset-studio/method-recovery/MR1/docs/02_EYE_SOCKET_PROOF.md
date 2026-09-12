# 02 — Eye, socket and cheek: construction proof

**Task:** MR1-FACE. **Scope:** a single deliberate facial region before full-head production.
**Technique proposal:** low-density control-cage editing, with optional focused sculpting after the cage works. This is not a claim that a prescribed vertex count guarantees likeness.

## A. Define the proof before modeling
Inspect the actual approved face crop, current face closeup, front and profile. Record the intended eye aperture, upper-lid arc, lower-lid shape, corner locations, globe placement, brow plane and cheek fullness in a brief visual note. One image is not a measurement of unseen depth.

Use the approved head identity, not a generic photoreal human. Ada should retain a calm, alert gaze; do not solve the stare by turning her eyelids into an angry squint. Closed relaxed lips and a stable jaw are context, not permission to redesign the face in this task.

Choose one anatomical side and record it. Retain a centerline and enough nose/forehead/jaw context to assess proportions. Hide the old eye overlays only in the candidate or review scene. Do not delete source history.

## B. Start from an editable region, not a high-density displacement patch
Use manual mesh editing, Poly Build, or a clearly documented equivalent operation through the available tools. Numeric vertex edits are allowed when driven by visible anatomy and local control points; they are not an excuse to regenerate a dense regular grid.

A few hundred control vertices can be a reasonable initial work scale for one eye-to-cheek region. It is a manageability target, not a minimum, maximum or pass condition. The count should follow the shapes actually required.

The region extends from the nose-side orbital boundary to the temple, from brow to upper cheek. Its outer edge must follow planned surface flow rather than an axis-aligned rectangle. Do not deform an existing rectangular selection and then hide its border with repeated all-axis smoothing.

The proof may be a standalone shell with intentional open outer boundaries. Label it an isolated study. Render it without an old facial surface directly underneath; stacked surfaces can mimic thickness or cause false ridges. A local proof is not yet an integrated head.

## C. Establish an eye globe and a real eyelid opening
Use a simple smooth eyeball as a geometry reference. Fit its size and center deliberately from the chosen views. A sphere is useful as an underlying object but does not generate eyelid anatomy by itself.

For the anatomy test, use an unembossed globe. Add iris/pupil only as simple diagnostic material/color for the gaze check, not as raised circular skin relief. This is a temporary inspection aid, not a production-texture task. Also show a uniform clay version.

Create an open loop describing the visible eye aperture. Upper and lower arcs must have independently placed peaks and slopes; do not create a perfect symmetric almond and attach it to the face. Place inner and outer corners intentionally, with finite geometry rather than a single pinched star vertex.

Build adjoining rows for lid margin/thickness and skin transition. The topology should travel around the opening and outward toward the brow and cheek, not converge as a radial fan at the iris. Keep poles or abrupt changes in edge flow away from the lid margin and visible corner turns where possible.

A starting aperture with roughly 16–24 thoughtfully placed control points can be explored; this is only an illustrative density range. A clean lower-density result is preferable to a dense badly shaped one. Do not use the number as a quality score.

## D. Separate three different shapes
1. **Lid edge:** wraps the globe and defines the opening, with readable thickness.
2. **Lid body/socket:** transitions from that edge into the brow and surrounding tissue.
3. **Cheek/temple:** remains a deliberately modeled facial volume, not a spherical depression.

Do not shrinkwrap the whole region to the eyeball. If a constraint is useful, apply it only to a named lid-margin vertex group, with verified offset and direction. The upper cheek and brow must not inherit the globe's curvature. Blender's Shrinkwrap can be restricted by vertex group [S2]; the chosen weights and result still require review.

Do not project the entire new face onto `ADA_Head_Continuous` either: that would copy the very cheek bands and orbital artifacts under repair. The old head can guide approximate scale and surrounding proportions, not final regional curvature.

The lower lid should flow into a continuous upper cheek. Preserve enough volume beneath the eye; avoid a deep horizontal trough running across the cheek. Outer-row positions and tangents should converge smoothly into surrounding facial planes, not flatten into a hard boundary.

## E. Use subdivision as a probe
Review the unsmoothed cage first, then a single subdivision level. Use an additional level only after the low-density shape already behaves correctly. Keep the original cage accessible.

Subdivision creates a smoothed surface from a lower-density mesh; it is not equivalent to smooth shading and it does not select the right forms [S1]. If a starburst, pinch, ridge or hollow appears, fix vertex placement, edge flow or boundary behavior. Do not add levels until the defect is too soft to notice.

Show a wireframe image that makes the aperture, lid rows, corners and outward flow inspectable. Quads are a working preference, not a ban on every triangle. A triangulated fan covering the visible iris is the wrong construction for this task.

## F. Validate the specific failed relationships
Use fixed front, profile and both three-quarter views. Show:
- eye with diagnostic iris/pupil;
- eye in uniform clay;
- lid/socket/cheek with the eyeball hidden;
- control cage with the smoothed surface;
- the same clay under a key light from the opposite side.

An artifact that stays attached to the cheek as lighting reverses is useful evidence of a geometric/normal problem; do not declare the exact cause without inspecting the mesh. A shadow that moves does not by itself establish correct anatomy.

Look for floating patches, intersections, missing lid thickness, pointed corner cuts, hard orbital craters, horizontal bands, implausible brow pinching and a surprised/staring expression. Review nearby nose and jaw context for regressions.

## G. Integration only after local improvement
An agent reviewer may mark the isolated construction `METHOD_PROOF_ACCEPTED`, with explicit limitations. This allows an internal continuation, not Pram's approval.

Then extend the method to a full front face or integrate into a continuous head candidate. Mirror only after confirming the symmetry plane and retain the ability to make approved asymmetry. Do not mechanically mirror an expression defect.

Remove overlapping old skin in the replacement region within the candidate only. Join/weld or rebuild boundary topology deliberately; simply joining objects leaves the integration problem unresolved. Inspect front, both three-quarters and profile again. A regional success must not create a seam at the temple, nose or jaw.

Only then make a coherent two-eye expression check. Do not claim Ada's face is finished because one eye improved.

## H. Iteration and failure
Use an initial constructed candidate and at most two bounded corrective passes without meaningful improvement. Each pass names the changed relation, actual geometry edits and visible effect. Parameter shuffles of the same formula are not different methods.

If the tool cannot support deliberate cage editing or the new representation still fails, retain the best source and use the focused intervention brief in document 04. Do not fabricate an approval or reset the counter by renaming the task.

## Required outputs
`face_proof_<revision>.blend`; work/cage images; fixed comparison captures; a concise list of edited parts; remaining defects; an explanation of how this method differs from the rejected radial/rectangular patch. All figures remain `NOT_RUN` until actually captured.

References [S1–S4] are listed in document 04. This procedure is a modeling recommendation, not a quotation from the submitted review.

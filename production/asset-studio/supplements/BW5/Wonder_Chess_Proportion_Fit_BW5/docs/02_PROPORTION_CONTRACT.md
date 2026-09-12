# 2 — Match Ada's proportions without forcing impossible geometry

## A. Replace vague fitting with defined relationships

The key problem is not just armor width. The supplied reference has a compact central plate, a substantial tailored collar, a fitted profile, visible navy waist coverage and shoulders that carry their own volume. BW4 has a taller central plate relative to its width and a relatively small collar. In profile, the report independently identifies excess forward projection.

Do not execute “scale armor down 20%.” Translation, width, depth, height and local edge shape are different variables. A whole-object scale would move neck/waist/armhole contacts together and change thickness behavior.

See [annotated ratios](../references/armor_ratio_comparison_annotated.png) and [construction relationships](../references/armor_construction_relationships.png).

## B. These are the measured image conventions

Original turnaround: 1658 × 949 pixels. Uploaded BW4 comparison: 918 × 2048 pixels. Coordinates have origin top-left, x to the right and y down. Endpoints are manually selected visible features; the stated uncertainty is an allowance for picking/ambiguous boundaries, not a statistical confidence interval.

- **W:** selected wide visible torso-plate span, excluding pauldrons, padded sleeves and straps. It is not shoulder-joint span and not a hidden body measurement.
- **H:** center neckline to the lowest front-center plate hem.
- **B:** horizontal span between the left and right lateral hem endpoints. These endpoints need not be at the same image y because the drawing is not perfectly symmetric.
- **C:** visible outer span of the collar near its top rim.
- **U:** vertical centerline exposure between the front hem and the top of the belt/buckle region. It says something about layering, not empty space behind the shell.

| Projected ratio | Reference estimate | Manual selection interval | Uploaded BW4 estimate | BW4 interval |
|---|---:|---:|---:|---:|
| H / W | 0.60 | 0.54–0.68 | 0.74 | 0.69–0.79 |
| B / W | 0.81 | 0.73–0.89 | 0.86 | 0.79–0.92 |
| C / W | 0.65 | 0.57–0.74 | 0.48 | 0.43–0.53 |
| U / H | 0.14 | 0.07–0.23 | 0.02 | 0.00–0.07 |

The hem-taper intervals overlap. Do not claim the data proves a large width-taper error. Height/collar/layering and the independently reported profile projection are the stronger starting signals.

The reference numerator/denominator values are H=90px, W=149px, B=120px, C=97px, U=13px. BW4 values are H=153px, W=208px, B=178px, C=100px, U=3px. Re-mark from the source/camera on your local evidence if these endpoints do not correspond to the intended anatomical section. Keep the new records instead of silently replacing old observations.

`reference_measurements.json` stores all endpoints, tolerances and formula outputs. A ratio interval is [minimum numerator / maximum denominator, maximum numerator / minimum denominator]. Do not average these into a likeness percentage.

### What not to calculate from this sheet

No metric armor thickness, exact body stature, hidden padded torso circumference, absolute chest/back depth, shoulder-joint spacing, or motion clearance is established by the reference. The left side's arm conceals part of the rear torso. Consequently its full shell depth remains null.

The reference side shows the plate returning toward the waist below a controlled chest projection. Use that visible contour, but obtain absolute depth from the live padded model and multi-view fit. Do not reconstruct a rear edge through an occluding arm and call it measured.

## C. Normalize views without distorting the character

1. Preserve BW4's historical cameras and original frame1. Generate baseline images by reopening the frozen source read-only; exclude unrelated hidden experiments by an explicit allowlist.
2. Add separate reference-comparison cameras: front, back, anatomical left, anatomical right, plus a three-quarter review. Use orthographic projection for construction comparisons. Orthographic size is controlled by its scale rather than object-camera distance (Blender camera reference B1).
3. Create a duplicate posing context matching the reference's shoulder/arm posture where feasible. Never change the canonical rest pose or source action. Record the comparison pose. Use both original authoring pose and reference-pose evidence.
4. Align two BODY anchors, such as the base-of-neck/sternum landmark and waist/pelvis landmark, and use a single uniform image scale/translation within each view. Do not use the plate's own corners as both registration anchors and scored fit points.
5. Do not stretch width independently from height, warp images, move the camera to flatter the newest revision, or resize different parts independently. Different orthographic view crops may be framed differently, but their world scale and landmark policy must be recorded.
6. For unknown perspective in the painted reference, describe the residual discrepancy and prioritize visible construction. Do not demand exact pixel agreement across incompatible views.

Only internal torso ratios are used from the current source comparison. Whole shoulder span is pose dependent: the source A-pose and artwork are not the same, so that span must be re-evaluated in matching poses before quantitative comparison.

## D. Build a real 3D fit record

Do this before reshaping the plate.

Use the existing metric world transforms once; inspect nonuniform/negative scale and object/armature parenting. Create an analysis torso frame from the neck/waist centerline and shoulder landmarks. Normalize and orthogonalize it, verify handedness and anatomical front with a known sternum point, and record signs. Do not assume arbitrary local X/Y or a camera's left means anatomical right.

Let t=0 at the natural-waist reference plane and t=1 at the base-of-neck/clavicle plane. Sample at t=0, 0.25, 0.50, 0.75, 1.00, plus the actual hem and armhole extrema. These are proposed analysis stations, not automatically the only topology rows.

At each station record in the SAME metric frame:
- Body extent where available, without inferring it from art.
- Final evaluated padded-coat extent, including the retained thickness/modifier state.
- Plate inner and outer surfaces, separately at front, sides and back.
- Section width, front/back projection, local clearance, and intentional overlap regions.
- Which surfaces are visible versus occluded in the reference.

Do not double-count padding: the evaluated garment already includes its own construction. Do not use the naked body alone as the armor collision target.

Let the layer relation be: **body -> padded garment -> clearance -> shell thickness -> exterior**. A trial 3mm gap and 2mm shell would put the exterior about 5mm from the garment at that local normal, not 5mm from the skin. Those numbers are ONLY an illustrative trial, not inferred historical thickness or mandated tolerances. Choose and record appropriate values for the measured character and animation.

Do not approximate this with one global bounding box. Use sectional intersections/rays and verify front versus back correspondence. A shortest-distance query may hit a neighboring sleeve rather than the intended torso surface. Open/complex surfaces can make signed containment ambiguous; qualify the query.

## E. Solve feasibility before iterating blindly

Start with the unchanged body preset. Adjust shell sections, silhouette, armhole trimming and garment tailoring on independent derivatives. Do not shrink the hidden body merely to make the armor appear fitted.

If the minimum viable padded silhouette is already broader/deeper than the selected design envelope, render body, coat, and shell separately at that section. Record the conflicting constraints. Propose one bounded candidate-only body/padding decision for human review; do not change body proportions or shared skeleton automatically.

A zero-crossing shell floating far from the body is not a pass. A beautiful two-dimensional outline with the coat protruding through it is not a pass either.

## F. Fit by sections, not a global scale

On the front plate, edit independent controls for neckline, upper rim, chest projection, lower-rib width, waist taper, center hem and side returns. On the back, use its own neckline/armholes and hem.

A Lattice can help make a reversible broad shape change, and it supports restricting influence with a vertex group (B2). For the current editable cages, direct section editing is preferred when it gives more precise control. Neither method creates collision safety by itself. All dependent side returns and attachment points must be rechecked after reshaping.

Do not widen W merely to reduce H/W, inflate the collar until C/W passes, or hide the waist under a large belt. Use actual body anchors, the whole silhouette and sectional clearance to decide which variable is incorrect.

## G. Front and back are intentionally different

The supplied front hem has a shallow downward central point. The back lower rim rises centrally, exposing a shaped navy waist layer. Do not copy one hem onto both plates. Hair partly obscures the back upper edge: complete it consistently with the collar and shoulder construction and label the decision.

The new reference also has broad shoulder masses above a comparatively compact torso. Keep that design intent, but do not derive exact cap-to-body ratios from the unmatched source A-pose. The required cap still has to clear the padded shoulder and move plausibly.

## Exit from proportion fitting

A candidate may proceed to interface-detail work when the major silhouette is visibly closer under the fixed comparison policy and the 3D fit is feasible. Human final approval remains pending. Quantitative ratios are supplementary guides, not a standalone gate.

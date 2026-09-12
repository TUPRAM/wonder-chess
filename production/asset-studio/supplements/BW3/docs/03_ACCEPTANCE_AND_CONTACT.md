# BW3 — Evidence and promotion rules

## Priority order

1. Correct source/coordinate state and valid geometry.
2. No confirmed problematic self/neighbor crossing or path tunneling in the tested interval; plausible web and digit volumes.
3. Stable attachment, usable handle/guard clearance and coherent movement.
4. Pad-contact screens and visual enclosure.
5. Artistic local review.

A lower item cannot compensate for a failure above it. This does not demand physically simulated force closure or every tiny skin detail for an auto-battler. It prevents the specific false-positive mechanism in BW2.

## Minimal result record

Use `templates/BW3_REVIEW_TEMPLATE.md`; it is a pending report, not prefilled passes. Include candidate filename/hash, actual rig/body/glove IDs and versions, frame range, interpolation, evaluated modifier levels, fixture revision and contact-map revision.

Report what changed among pose, rest mesh, weights, topology, controls and corrections. Evidence gathered before the last material geometry change is stale unless exact geometry/matrix equivalence is proved.

## Temporal coverage

- Evaluate all145 integer frames for the candidate diagnostic when retaining its source range.
- Frames1–24: no required contact; do require valid movement and fixture clearance.
- Frames25–145: same validity plus held contact and attachment checks.
- Sample subframes adaptively around first contact, known fold onset, near-collisions and fast control changes. Record actual sampling, not a claim of all continuous time.
- If timing changes, label the new ranges and map them to the intended approach/hold phases. Do not relabel failing approach frames out of the record.
- A separate free-space thumb study is allowed, but is not a fixed-handle approach proof.

Check body, glove, glove-versus-body fit and handle, not just the contact-pad samples. Body-only and glove-only views are essential because the underlying body already fails in BW2.

## Collision methodology

Reuse the existing verified triangle-interior and crossing checks after inspecting their assumptions. Blender's BVHTree API provides proximity/overlap operations [W3]; their return value alone is not the complete authored-art verdict.

Use deterministic triangulation and report its identity. Avoid counting a surface's normal topological adjacency as a defect; also do not exempt whole digit groups or neighboring patches merely because a fold lies near a joint. Report degeneracy, local fold/inversion indicators, uncertain coplanar contact, containment and detected crossings distinctly. Containment can exist without a new transverse crossing in the current pose; an open wrist boundary means signed-volume interpretations require care.

Classify persistent problem regions by semantic parts and location. Retain triangle-pair counts for reproduction, but do not use a reduction from375 to100 as an acceptance threshold. Retopology changes the number of triangles and therefore the pair count without necessarily changing the defect.

Target: zero confirmed problematic self-crossings in the checked candidate states, no visually significant fold/tunneling, and no unresolved collision ambiguity at a critical contact. Report numerical precision and method limits; do not promise a mathematically certified collision-free asset from sampled tests.

## Contact and attachment

The original screen is−0.5…+1.0mm on previously declared pad patches, within the105mm usable span. Preserve per-digit fractions and gaps for comparison. It does not establish thumb travel, whole-finger clearance, force closure, or anatomical correctness.

Whole-surface handle checks cover all fingers and palm, not just target pads. Evaluate triangle interiors when appropriate; no new sparse-vertex pass should replace the existing stronger retained-pose check. Use the actual fixture mesh and explain any ideal-cylinder approximation.

Report hand-to-fixture drift in physical units. The source's below0.001mm attachment drift is already strong; do not spend this run making that metric smaller while the thumb remains folded.

## Required images and motion

Capture matched palm, side, axial, dorsal and reversed-key views; handle-hidden views; body-only/glove-only; actual posed cage; and a closeup of the corrected thumb-web and middle/ring gap. Use the same saved cameras for baseline/candidate comparisons. Add a full arm/equipment view only after the local grip succeeds.

Render and inspect the complete approach/hold/carry sequence from the frozen candidate. Record the first/worst/last failure if any. Do not cut away from an unsatisfactory transition. Diagnostic colors may expose regions but must not conceal penetrations with transparency, deleted faces, or occluding equipment.

## Reopen/preservation

Save the work and a frozen candidate. Reopen both using actual Blender and inspect active scene/object links, corrections, action binding, cameras, modifier states and fixture transforms. Source references retained only in an unsaved session do not satisfy delivery.

Check protected originals. Candidate edits are allowed within the authorized region: do not accidentally require its weights or face array to equal the baseline while authorizing reconstruction. Verify unrelated objects and master data remain unchanged.

## Statuses

- `ART_REVISE`: a required visual/construction failure remains.
- `LOCAL_ANIMATED_GRIP_CANDIDATE`: the tested local animated route passed its stated technical and art-review checks, pending human acceptance and integration.
- `FIXED_GRIP_CANDIDATE`: the separate scoped option in doc04 only; not an animated-grip pass.
- `AUTHORING_ONLY`: required runtime mapping/export has not been tested.

No automated process writes human forms approval. No reusable recipe is promoted from a single candidate. Independent replay and a second supported-body/fixture fit remain later gates. Fixed-pose successes and failed animated closures must not be mixed into one successful training label.

## Stopping and next independent work

Retain the method-review rule. Count actual meaningful corrective revisions, not every render or solver evaluation. Do not continually reset the attempt counter. After the bounded method fails, produce its best evidence, a precise remaining causal question and the optional fixed-game-grip decision.

A failed grip blocks sword/grip-dependent promotion. It does not block independent sleeve enclosure, costume silhouette, boot construction or existing game development under separate tasks and ownership. Do not launch them inside the same short grip assignment without a clear handoff.

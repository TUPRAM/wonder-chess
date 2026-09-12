# ACB1-ART — Close the Ada head study through a real surface reconstruction

## Assignment and completion boundary

Continue from the uploaded/locally verified `ada_head_polish_checkpoint_r016.blend`, not an old procedural regeneration. Build one new candidate using a sculpted form target followed by deliberate local cage reconstruction. Deliver the strongest reviewed result and an explicit development-use decision request. This is not a promise of a successful artistic outcome in one run.

Use one bounded work block; a proposed budget is three active working hours, logging modeling, render waiting and review separately. Do not sacrifice required checks to meet a clock. At the end, either submit a usable candidate for user review or park the art task with its precise remaining defect. Do not let this block become another indefinite r017–r040 polish series.

### Source-derived facts

Read `evidence/REVIEW_LOCAL.md` and `evidence/verification_submitted.json`. r016 improved the anatomical-right opening but remains REVISE. Its cage has 1,670 vertices and 1,612 faces. The report attributes the remaining transitions to dense lid/lip rows meeting much broader adjoining faces. The report calls this an evidence-supported inference, not proof that a larger polygon count would fix the form.

Only the right-side region and five shared centerline controls were changed. The two-sided difference is an intentional experiment; do not mistake it for an accidental rig or mirroring error. The new head has not passed deformation, textures, animation, LOD, Unreal, or human forms approval.

Expected uploaded frozen file SHA-256:
`775815688dc4aa30dce7085b78ef79bf9ff89f603f243af9110d8ef7b8d00b6b`

A different local hash is a reason to identify the revision, not to overwrite newer work. Read the current scene and active object instead of trusting an old hard-coded object name; the submitted audit names `HP1_HEAD_POLISH_Head_r016`.

## 1. Create an isolated candidate and preserve the correct things

Use the existing MCP/editor connection. Check source identity, active scene, selection, object transforms, modifier stack, user activity and successful image return. A short preflight suffices; do not rerun unrelated game tests for an eyelid edit.

Save a new work file under a new stage directory selected after checking for collisions. Suggested stage label: `head-closure/ACB1/`. Never overwrite r014, r016, the approved references, existing source body/rig, or a user's unsaved work.

Create clearly named candidate roles:

- `ACB1_HEAD_BASELINE`: hidden, read-only comparison copy of the retained input.
- `ACB1_FORM_TARGET`: disposable sculpt target.
- `ACB1_HEAD_CAGE`: reconstructed editable candidate.
- `ACB1_CONTEXT_ONLY`: duplicated diagnostic brows/hair/collar and simple materials, excluded from export.

Record an explicit render allowlist. Failed or hidden experimental meshes must never silently become the active surface.

Preserve camera matrices and lighting baselines. Use new cameras only for separately labeled context/game-scale views. Do not change the comparison camera to make the result look better.

Preserve actual anatomical handedness, eye globe transforms initially, important opening/corner landmarks, nostril interiors, mouth seam and neck interface. **Do not preserve the failed interior face layout as an invariant.** Vertex and face counts may change. Stop using old vertex-index selectors after topology changes; replace them with verified semantic groups and boundary correspondences.

## 2. Specify a meaningful correction region

Select the connected right region containing upper/lower lid support, inner socket, nasal sidewall, upper cheek, columella, philtrum and upper-lip support. Include a transition apron into surrounding skin so the correction is not forced against a sharp rectangular border.

Separate these controls:

- Protected anatomical boundaries: eye opening, mouth seam, nostril openings/interiors and neck boundary.
- Shape landmarks: canthi, eyelid high point, nasal tip/base, centerline and lip center.
- Editable support surface: lids away from the margin, orbital-to-cheek transition, sidewall, philtrum and upper-muzzle volume.
- Outer integration boundary: a continuous border placed on a relatively calm part of the surface, with surrounding context for continuity checks.

Preserve successful opening/corner positions within a documented local tolerance chosen after measuring the model. Do not invent exact millimeter targets from the painted reference. An edit to a shared midline can influence both sides after subdivision; disclose that and avoid double application later.

An overly tight pinned boundary can preserve a visible ridge. If that happens, modestly enlarge the *local transition apron* and record the scope change, rather than changing the whole head or smoothing across the eye/nose/mouth.

## 3. Establish the target forms before rebuilding the cage

On a disposable duplicate, create a sculptable surface that initially matches r016's evaluated appearance. Do not accidentally apply subdivision twice or introduce a different smoothing shape before the comparison. The supplied report used an existing level-2 Subdivision Surface preview; inspect the actual stack.

A mesh copy of the evaluated surface is acceptable as a sculpt target. Add resolution only where the brush cannot represent a required form. Preserve the source cage separately. Multiresolution is an option where it fits the inspected stack; it is not permission to replace useful low-level shaping with high-frequency detail.

Use masks or face sets to protect openings, internal nostril surfaces and unrelated anatomy. Keep a protected collar around those boundaries. Work at broad primary/secondary-form scale, inspecting from more than one direction.

### A. Lid and socket

Tools: a controllable move/grab brush or cage edits for shape; low-strength Clay/Clay Strips or Inflate/Deflate for support volume; local Smooth/Surface Smooth only as a finishing operation. Select the corresponding available brush assets in the installed Blender version rather than assuming one API identifier.

Retain the better eye aperture and lid peak. Reduce the *excess tissue behind the margin*, not simply lower the margin until the eye becomes a narrow slit. Make the lid read as a thinner band wrapping the globe, tapering naturally into the corners. The upper lid can overlap the iris as indicated by the approved image, but do not impose a generic anatomical ratio or change diagnostic iris size just to hide the aperture problem.

The inner corner must join the nasal sidewall without a raised rope or a deep radial crater. Treat inner corner, sidewall and cheek as related but independently shaped forms. Keep the actual eye opening visible with globes hidden. Do not paint an eyelid illusion onto a flat surface.

### B. Upper cheek

Use a broad, soft falloff to create one coherent cheek mass beneath the socket. Inspect whether the perceived band is a ridge, trough, or both under reversed key light before choosing to remove or add volume. Often the correct operation is a small fill of the trough plus restrained reduction of a ridge—not flattening the whole cheek.

Do not deepen a circumferential under-eye groove or preserve regularly spaced horizontal bands. Preserve a deliberate cheek-to-side-face change of plane without building a hard shelf. Avoid tiny repeated brush strokes that manufacture new texture noise.

### C. Nose base, philtrum and upper lip support

Inspect a true profile and underside closeup alongside the main portrait. Establish a compact nasal base, distinct columella, short gentle philtral transition, and upper-muzzle support. Do not mistake the reference's painted shadow for a carved trench.

Build volume where the long recession collapses the upper-muzzle support. Keep the upper lip from projecting as a free ledge beneath an empty trough. The columella and philtrum should remain distinct shapes without a sharp central spike. Preserve nostril vaults and the successful tip unless a clearly documented local change is necessary.

Tools: broad Grab/Elastic-style deformation for placement, low-strength Clay/Inflate for support, a restrained flatten/scrape operation for a deliberate plane only where suitable, and narrow smoothing that respects boundaries. A crease brush is not a shortcut to every facial transition.

### Explicit exclusions

No voxel remesh across the open eye/mouth/nostril interfaces on the retained production candidate. No whole-head Gaussian displacement grid. No third retuning of the same 137 controls under a new script name. No global facial scaling, new jaw shelf, scalp reshaping, or hair polish. No forced hyper-realistic anatomy; the selected stylized Ada remains the target.

## 4. Review the unilateral sculpt target immediately

Render r016 and the sculpt target with the same front, profile, both three-quarter, primary-portrait and reversed-key setups. Include eyes-hidden and an underside crop. Inspect actual images, not render success messages.

This local target is successful only if the heavy rim, under-eye band and nose-to-lip recess are materially less distracting without loss of the improved eye opening or new hollows. A new smoother surface alone is insufficient.

Do not yet mirror an unproven target. One initial construction and at most two corrective revisions form the bounded method experiment. Document improvement or lack of it in visible terms rather than a made-up likeness percentage.

## 5. Reconstruct local topology to hold the successful target

On `ACB1_HEAD_CAGE`, preserve the successful opening and outer boundary, then replace the faulty transition faces. Use Edit Mode / Poly Build / extrusion / edge slide / loop insertion and merging as appropriate. Target the sculpt, not the old r016 surface.

The topology must provide control across both directions of the transitions. Gradually distribute spacing from lid to socket to cheek; do not funnel tear corner, nose sidewall and cheek through one narrow strip. Give nasal base and philtrum enough transverse support before joining the denser lip area. Avoid placing high-valence poles at a canthus or directly on a demanding curvature transition when an alternative is feasible.

No fixed polygon target or exact required loop count is imposed. Keep geometry editable and purposeful. Review the unsubdivided cage and subdivided result; structural cleanliness is a constraint, not the visual objective.

For transfer, use a controlled target projection or Shrinkwrap limited by vertex groups/selection. Test normal direction, offset and front/back surface selection. Do not nearest-project eyelids onto the opposite surface, or shrinkwrap the cheek onto the eyeball. Weld shared patch seams exactly once and confirm continuity.

**Multires Reshape is only suitable when the required topology and vertex indices match.** It does not transfer arbitrary sculpt topology into an unrelated cage. For changed topology, retopology/projection plus inspection is the relevant path. No stale source-index replay is permitted.

Recompute semantic groups and mesh audits. UVs/weights/shape keys tied to replaced topology must be reworked later; do not claim they were preserved merely because the mesh still opens.

## 6. Extend only a successful new construction

If the unilateral *new method* proof is clearly better, extend the successful structure to the opposite side. This is explicit permission to progress beyond a one-eye experiment after that conditional proof, not to mirror r016's existing defects.

Use the verified sagittal plane and anatomical correspondence. Mirror or reconstruct the local region only; do not symmetrize ears, jaw or the entire existing head without need. Preserve the mouth seam and centerline once. Eliminate duplicate midline vertices and recompute the full-head evaluation.

A convincing isolated side is not enough. Inspect both eyes together, gaze direction, canthal relationship and expression. The final deliverable must be a bilaterally coherent candidate, or an honestly incomplete proof—not an accidentally asymmetric interim head labeled finished.

## 7. Add context as a separate diagnostic, not camouflage

Only after the full clay candidate has been inspected, create a duplicate context scene. Existing authorized brow/hair proxies, collar and flat skin/hair materials may be used without modifying those source assets. New context-only simple brow/hair silhouettes may be authored if they are clearly labeled diagnostic, not final art or new reference identity.

No hair hides the bad cheek. No eyelash geometry hides an unresolved lid hole. Keep the same camera and a clay view beside context. Do not reduce the skull simply because the concept's hair hides it.

Use three display conditions:

1. Close-up clay and reversed-light diagnostic for surface defects.
2. Contextual head/shoulders or actual unit-inspection camera for likeness and expression.
3. Actual gameplay camera in Unreal if available, with the whole character at its true pixel size. Otherwise provide a clearly labeled Blender/proxy screen-scale test, recording that it is not engine evidence.

Optional 96/160/256-pixel **whole-character** downscales can diagnose readability; they are not proof of actual game projection. Do not show only a 96-pixel head and call it a battlefield test. The current hero gallery also makes close-range quality relevant.

## 8. Close with an honest development-use decision

Required local outcome checks:

- Improved opening retained; expression is not strongly startled or sleepy from either side.
- Heavy lid shelf and under-eye band are reduced under both key-light directions.
- Nasal-base/upper-lip profile no longer reads as the same exaggerated trench and shelf.
- Continuous skin, intended openings, unchanged neck interface, no new neutral-pose intersections or degenerate faces.
- No unresolved source overlap; actual skin is the candidate, not two coincident heads.
- No claim of rig/deformation, final texture, LOD, gallery, Unreal, or beta approval from neutral geometry.

Submit `REVIEW_READY_DEV_USE` only when there is a materially improved candidate worth the user's review. Keep any existing art-major defects explicitly listed. The user can authorize bounded internal use with those defects still open; Codex cannot relabel them minor or write human approval.

If the method fails, set `PARKED_ART_REVISE`, preserve the best result and give a narrow request for an experienced modeler's targeted surface intervention. Do not buy assets, upload proprietary art, or hire anyone without authorization. The existing in-game Ada stays available as an internal fallback; do not replace it automatically with a head-only study.

Either way, leave a resumable handoff and proceed to the independent game task in `02_GAME_RESUME_TASK.md` when authorized. Missing art approval blocks production promotion of this head, not unrelated match/bot/network work.

## Deliverables

A new work `.blend`, frozen candidate, editable cage plus separate sculpt target, matched actual renders, opening/cage diagnostics, a one-page review with outstanding defects, preservation/geometry observations and exact source/build paths. Run a neutral structural audit and limited needed attachment checks; do not invent facial animation acceptance.

Do not supply another large architecture document instead of the modeling proof. Do not cite hundreds of unrelated passing tests as visual evidence.

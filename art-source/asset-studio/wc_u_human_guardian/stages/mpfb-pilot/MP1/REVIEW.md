# Ada MPFB pilot MP1 — retained foundation, ART_REVISE

Date: 2026-09-09. Candidate: r002. This is a separate untextured head study, not a finished Ada, development-use approval, or AS1 forms approval.

MPFB 2.0.17 produced a visibly more coherent anatomical foundation than the preserved r016 head. Keep the connected foundation and editable source controls. Stop the trial here: the remaining eye shape, parted mouth and soft jaw are major likeness defects. The final mouth-only adjustment was modest and did not achieve lip closure.

## Decision and visible results

| Method | Observed result | Decision |
|---|---|---|
| MPFB core human foundation, with a separately derived head cage | More recognisable nasal underside, alar wings, philtrum, upper-cheek volume and ear anatomy than r016; fewer conspicuous transition bands | Keep as a candidate foundation |
| Native target controls applied on the full indexed MPFB source | A bounded way to adjust proportions while retaining the connected source topology | Keep the editable capability and recorded parameters; the trial does not prove each slider independently improves likeness |
| Fitted eyeballs plus a separate grayscale iris/pupil diagnostic | The lid covers the upper iris and the exposed-globe stare is reduced; eye shape still differs from Ada | Keep for review, not as production eye materials |
| r002 lip-height/volume controls | At most a modest upper-lip projection change; a dark gap and pouting profile remain | Do not reuse as a successful mouth-closure recipe |
| Repeated blind parameter tuning or a new automation toolkit | No evidence that this resolves the remaining defects | Do not continue or build that now |

The primary approved portrait remains the identity authority. The supplementary construction study is an anatomy aid; its more open eyes and fuller lips do not replace the primary design. The saved primary-fit camera is an approximation to the illustrated portrait, not a recovered photographic camera. No likeness percentage is claimed.

## Matched evidence

All before/after clay sheets put the frozen r016 baseline on the left and MP1 r002 on the right. The baseline was reopened in a separate background process, rendered with the same clay and saved cameras, and never saved. The original file hash remains unchanged.

- [Front](captures/comparison_front.png)
- [Profile](captures/comparison_profile.png)
- [Three-quarter](captures/comparison_three_quarter.png)
- [Primary portrait camera](captures/comparison_primary_fit.png)
- [Reversed lighting](captures/comparison_reverse_key.png)
- [Primary reference / r016 / MP1 diagnostic gaze](captures/reference_comparison.png)
- [Opening, actual control cage and diagnostic gaze](captures/diagnostics.png)

The clay captures use uniform gray surfaces, 48 Cycles samples, the preserved world and camera settings, and 900 × 900 pixels (primary camera: 840 × 788). Reversed-light views move both review lights across the head and then restore them. The source camera transforms are unchanged; the largest restored light-matrix difference is 5.96e-8, within a 1e-6 comparison tolerance.

The eye-hidden image exposes the real apertures. Eye and mouth recesses have interior surfaces; they are not unfilled surface patches. The cage evidence is an actual Blender Edit Mode screenshot with viewport subdivision disabled. The comparison sheets were made with the existing AS1 image helper, using labels and downsampling, without image warping or generative retouching. Diagnostic irises are separately labeled and are not a texture-production pass. No hair context was added.

## Remaining defects

| ID | Severity | What still fails | Next useful correction |
|---|---|---|---|
| MP1-M01 | Major likeness | Eyes are too compact horizontally and too regularly rounded. The outer corner and upper socket do not yet give Ada's firm almond-shaped expression. | One eye aperture/corner proof, preserving iris coverage, lid thickness and independent cheek volume |
| MP1-M02 | Major expression | Lips still read slightly parted. The upper lip remains rounded and projecting; the lower lip is full and the profile is pouty. | Inspect actual lip margins and make a deliberate local contact/support correction, preserving the improved nasal base |
| MP1-M03 | Major likeness | Lower cheek and jaw remain soft and generic; the diagonal jaw turn toward a compact chin is insufficiently distinct. | Defer until the higher-priority eye and lip relationships work |

The independent reviewer agrees that the foundation is useful and the mouth correction is not complete. See [independent review](independent_review.md) for the exact images reviewed and its limits. r002 is retained as the latest non-regressed study, not a materially stronger likeness than r001. The initial foundation and both bounded revisions are preserved in the verified file's active/archive scenes; no further corrective attempt is included.

## Editable delivery and reopening

- [Working file](ada_mpfb_work.blend)
- [Frozen r002, verified by reopening](ada_mpfb_checkpoint_r002_verified.blend)
- [Target parameters and alignment](trial_parameters.json)
- [Static geometry audit](geometry_audit.json)
- [Provenance and verification](verification.json)

Open the working file to continue. Scene `MP1_ADA_HEAD` contains only the head and two eyeballs in its render allowlist, plus the preserved cameras/lights. `MP1_Head_r002` is an editable 4,271-vertex cage with a subdivision modifier. `MP1_SOURCE_CONTROLS` retains the full 19,158-vertex MPFB source and its 38 shape keys; its preview mask hides the body without deleting or renumbering source vertices. Use MPFB target controls on that full indexed source, not on the extracted head. `MP1_ARCHIVED_TRIALS` keeps the earlier head candidates separate.

The installed MPFB extension is `bl_ext.user_default.mpfb` under Blender 5.1's user extensions directory. The saved head itself can reopen without the extension enabled. Editing through MPFB's own controls requires enabling the installed extension in Blender Preferences if it is not already enabled. Broad user preferences were not saved or replaced. The sequential scripts in `operations/` record this executed session; they are not a promised one-click generation tool.

## Verification and preservation

The initial reopen check caught a scene-retention defect: the live head scene had zero users and was omitted from the first r002 saved scene list. The session still contained all geometry. Setting explicit scene retention (Blender's fake-user flag) and saving a new checkpoint fixed the delivery without changing the mesh. The verified checkpoint reopened with all three scenes, the exact head/source counts and saved camera transforms. The earlier files are retained as session evidence, not the recommended reopening path. The failed check remains recorded in `reopen_verification.log`; use `ada_mpfb_checkpoint_r002_verified.blend` for the frozen delivery.

The control and evaluated meshes have no observed degenerate faces, loose edges, edges shared by more than two faces, or nonadjacent BVH overlap pairs. The deliberate neck cut is the only boundary loop. These static observations do not prove deformation quality or certify every possible collision. Evaluated subdivision produces 135,872 head triangles; this is an authoring study, not a runtime budget.

The original r016 and ACB1 checkpoint hashes match their recorded originals. The existing AS1 status command still reports the brief and approved references as `accepted_current`; forms and downstream gates remain pending. No prior Ada geometry was used to construct this head. The copied scene was cleared of old geometry before MPFB generation; only saved cameras, lights and world served as the comparison setup. The user expressly authorized this isolated MPFB foundation trial, so the accepted original-method manifest was not rewritten to pretend that MPFB had always been its method.

Blender 5.1.1 and MPFB 2.0.17 were executed locally through the existing MCP connection and visible Blender session. Computer use was used to inspect the real application and capture its editable cage. No paid services or remote art upload were used; additional software/generation fees for this trial were $0. MPFB's tagged license identifies code as GPLv3 and its bundled core graphical assets as CC0; the exact package and license copies/hashes are retained in verification.

No hair, eyebrows, eyelashes, torso or armor were edited. No UV/bake work, final materials, rigging, skinning, animation, LOD work, Unreal integration, packaged-game test or performance approval was performed. The existing game and 24-hero work remain outside this assignment.

## Recommended next action

Keep MPFB as the free connected foundation and reuse the existing AS1 comparison/review process. Before turning more operations into reusable tools, prove one local eye correction on this foundation in front, profile, primary, eye-hidden and reversed-light views. Do not propagate that correction until it visibly helps. Address the lip contact as a separate bounded intervention after that. The present candidate stays ART_REVISE for likeness; no human approval or asset promotion is issued.

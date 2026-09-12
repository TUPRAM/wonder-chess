# Ada FH1 - nose, mouth, ear and head construction

Status: **EXECUTED AND COMBINED; VISUAL FORMS REVISE.** No human approval was issued.

The user requested nose, mouth, ears and facial/head geometry first, then combination and edge repair. All four have executed editable source in the new FH1 candidate. The supplied portrait and turnaround remain authoritative. A generated supplementary construction sheet clarifies hidden anatomy but is not an approved replacement reference or a Blender render.

## Open and inspect

- `ada_features_work.blend`: live working file.
- `ada_features_checkpoint_r004.blend`: saved review checkpoint.
- Scene `FH1_NOSE_STUDY`: initial and revised original nasal cage, including real nostril vaults.
- Scene `FH1_MOUTH_STUDY`: initial and revised lip/perioral cages, including closed contact support.
- Scene `FH1_EAR_STUDY`: original and revised continuous pinna/helix/concha cage.
- Scene `FH1_HEAD_SHAPE_STUDY`: original jaw/face/cranium envelope before features.
- Scene `FH1_COMBINED_HEAD`: current `FH1_Combined_Head_Control_Cage_r004`, with separate diagnostic eyeballs.

The combined skin has **1,621 control vertices and 1,564 faces**: 1,562 quads and two six-sided nostril-vault caps. It has one connected component. Nose (32), mouth (34), two ears (20 each), and two orbital regions (20 each) reuse their shared boundary indices. It is not an object join presented as a weld, and it does not use the rejected MR1 zipper bridge or old head geometry.

## What changed and what remains

| Part | Executed change | Remaining visual limitation |
|---|---|---|
| Nose | Original editable bridge/tip/alar cage; actual recessed nostrils; smaller downward-facing apertures and restrained projection | Pinched nasal root, weak base/columella differentiation, stepped philtrum transition |
| Mouth | Original upper/lower lips and perioral volume; narrow closed contact line; reduced projection and lateral taper | Soft cupid bow and rounded lower-center/under-lip transition |
| Ears | Original continuous shell, rim, concha, antihelix/tragus/lobe controls; thinner revised profile; both ears attached | Broad oval-dish appearance and insufficiently distinct folds/lobe |
| Head/jaw | Original sparse face, jaw, chin and skull; narrower lower jaw; rounded crown with quad cap | Angular rear-skull/neck silhouette; cheek/jaw planes and expression still differ from Ada |
| Joins | Shared-index attachment, corrected medial nose/eye ordering, removed exposed outer-globe crescents and repaired distorted crown cap | Surface pinching at inner brow/root/under-eye remains; visual continuity is not approved |

The two broad assembly corrections did not eliminate the inner-brow/root defect. A subsequent specific interface diagnosis found the nasal boundary lateral to the inner orbital controls; correcting that order removed the conspicuous strip edge but still left pinched forms. Do not continue with general smoothing or another whole-head deformation pass. Retain R004 and use one directly edited nasal-root/inner-brow/subnasal study if further work is authorized or steered.

## Evidence and boundaries

- The actual Blender session created and saved the geometry. Native Computer Use selected/observed the window and exposed the editable cage.
- `captures/combined_initial_*` and `captures/combined_r004_*` use matching cameras for this run's before/after comparison. This is a within-FH1 comparison, not a registered likeness measurement against the illustrations.
- `captures/final_uniform_clay_*`, `final_openings_*`, `final_reversed_key_*` and `final_control_cage_*` show untextured surfaces, genuine openings, opposite lighting and the actual unsmoothed cage.
- `scene_audit.json` records current geometry observations, named scene objects, cameras and render settings. Historical failed objects and review wire overlays are hidden and excluded from the current render allowlist.
- Structural checks find no degenerate faces or unexpected non-manifold edges. The four intended boundary loops are the neck (40), mouth interior (34), and eyelid openings (20 each). These checks do not certify deformation, self-intersection freedom, artistic quality, or runtime suitability.
- `reviews/independent_features_review.md` records an independent inspection of the actual pixels, with per-region REVISE statuses and image hashes.
- `verification.json` records final hashes and protected-file checks. The incoming unsaved MR1 session was saved to `incoming_live_checkpoint.blend` before starting FH1. The seven protected source/reference files match their pre-run hashes.
- Torso, armor, collar, neck, hair studies and gameplay were not remodeled. No UV, production texture, rigging, animation, LOD, Unreal or packaging work was performed.

The next useful modeling intervention is a directly edited inner-brow/nasal-root and nasal-base/philtrum region with clear anatomical planes, judged in the same front/profile/three-quarter cameras. The ear and skull/jaw remain separate revision items. Forms and release approval remain with Pram.

# Ada Head Closure ACB1

**Outcome: PARKED_ART_REVISE.** The native sculpt workflow executed, but the resulting target did not resolve the local likeness and construction defects well enough to guide reconstruction. Correction 2 is retained as an executed study. The input control cage remains unchanged and pending reconstruction. No human art approval was recorded.

The first Clay Strips correction created a visible horizontal ridge under the anatomical-right eye. The final bounded correction removed most of that ridge and added modest nasal-base support. That was useful recovery from a newly introduced defect, but the lower-lid/cheek still reads as a raised pad, the medial socket transition remains uneven, and the nasal underside/philtrum still leads into an upper-lip shelf. The target therefore stays parked rather than being projected onto a new cage or propagated to the opposite side.

## Review images

These are diagnostic assemblies of actual Blender captures. Source pixels were pasted at native size without retouch, resampling, cropping, warping, or image registration. Labels identify the compared state. All source hashes remained unchanged during assembly, and all eight completed sheets were visually inspected.

- [Front comparison](captures/comparison_front.png)
- [Profile comparison](captures/comparison_profile.png)
- [Three-quarter comparison](captures/comparison_three_quarter.png)
- [Primary-reference camera comparison](captures/comparison_primary_fit.png)
- [Reversed-key comparison](captures/comparison_reverse_key.png)
- [Openings comparison](captures/comparison_openings.png)
- [Underside comparison](captures/comparison_underside.png)
- [Initial / correction 1 / correction 2 process sheet](captures/process_three_quarter.png)

The reference-camera comparison is useful evidence, not proof of an exact orthographic or near-perfect reference match. The primary portrait remains the identity authority; hair, eyebrows, and eyelashes were excluded from the work.

## Executed and not-run boundaries

| Work | Actual state |
|---|---|
| Evaluated target and bounded native sculpt work | Executed and saved; target remains ART_REVISE |
| Actual clay, profile, openings, reversed-light review | Executed; local visual defects remain |
| Input editable control cage | Preserved unchanged; pending reconstruction |
| Cage reconstruction or target projection | NOT_RUN because the sculpt target failed its visual gate |
| Bilateral propagation / mirroring | NOT_RUN because the local target failed |
| Integrated contextual head validation | NOT_RUN because the local target failed |
| Human forms approval | Not issued |

## Structural observations

The session owner's executed audit is recorded in [geometry_observations.json](geometry_observations.json). The independent visual reviewer read this audit record but did not rerun it.

- Evaluated sculpt target: 26,042 vertices and 25,816 faces; four boundary loops of 80, 80, 136, and 160 vertices; zero edges incident to more than two faces; zero degenerate faces; zero reported nonadjacent BVH overlaps.
- Target edits: 2,074 changed vertices; maximum displacement 2.8705 mm. Fully masked vertices changed: 0. Fully protected opening-collar vertices changed: 0.
- Input cage: 1,670 vertices and 1,612 faces; coordinates and face indices unchanged. Its four boundary loops remain 20, 20, 34, and 40 vertices. Zero over-two-face edges and zero degenerate faces are reported. Five raw-cage BVH overlap pairs are retained from the unchanged input; they were not introduced by the target work. The evaluated target reports zero.
- All ten recorded camera/light matrices remain unchanged.

These checks establish only their stated structural and preservation boundaries. They do not establish likeness, acceptable surface transitions, production topology, or human approval.

## Saved source and detailed review

- [Frozen ACB1 ART_REVISE checkpoint](ada_closure_checkpoint_ACB1_ART_REVISE.blend)
- [Editable ACB1 work file](ada_closure_work.blend)
- [Independent sculpt review with capture hashes](reviews/sculpt_review.md)

## Strict stop and next intervention

Both bounded target corrections have been used. **Stop ACB1 geometry work at this visual gate.** Do not spend another pass smoothing the same target, reconstruct the rejected shape, project it to the cage, mirror it, or claim contextual completion. Preserve the clean input and the executed target experiments.

The practical next handoff is to an experienced character sculptor for one small editable intervention: correct the anatomical-right eyelid/medial socket/upper-cheek volume and the columella-to-philtrum-to-upper-lip profile, using the existing primary portrait, fixed camera set, opening landmarks, and protected outer boundary. The intervention must replace the padded cheek and lip-shelf relationships with coherent anatomy, not merely erase brush marks. Request the editable Blender source plus the same front/profile/three-quarter/primary-fit/openings/reversed-light/underside captures. Leave hair, the opposite eye, ears, jaw, torso, rigging, and materials outside that brief unless a later explicit task changes scope. Any necessary shared centerline changes must be named and their neighboring-surface effects documented.

That is a specific intervention recommendation, not authorization to contact or commission someone. A corrected target must be inspected and accepted for the local method before reconstruction or wider propagation resumes.

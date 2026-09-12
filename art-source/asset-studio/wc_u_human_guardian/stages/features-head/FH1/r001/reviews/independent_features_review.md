# Independent Ada FH1 visual review

Reviewed: 2026-09-08T08:23:49Z. Reviewer: independent Codex subagent `features_review`. Role: advisory visual reviewer, not human owner or release approver.

**Overall verdict: REVISE.** R004 shows visible improvement over the initial combined construction, but it does not yet reproduce Ada's facial forms or expression. Preserve this candidate as a construction checkpoint. Continue only with targeted form correction and evidence collection; do not promote it to accepted likeness, accepted forms, or production art.

## Scope and evidence limits

Actual pixels were opened before implementation notes. The primary comparison is `combined_r004_{front,profile,three_quarter,underside}.png` against all four `combined_initial` views and the supplied portrait and turnaround. All initial/revised isolated nose and mouth views, all `ear_r002` views, R002 front/three-quarter, and R003 front/profile/three-quarter were also visually inspected during this review sequence.

The candidate PNGs were supplied as Blender renders. This reviewer used file image inspection only: no Blender, native UI, geometry writes, scene inspection, or provenance authentication. The image hashes below bind the observations to the pixels inspected. The exact render-to-source snapshot, camera metadata, wireframe, reverse-light evidence, and technical topology audit are not independently established by this report and must remain in the operator's separate evidence record. Pixel inspection cannot establish welded topology, normals, manifoldness, rig suitability, performance, or runtime behavior.

The supplied portrait is the stronger facial/style authority. The turnaround supplies useful profile context but contains small painted facial landmarks. Neither image has been registered to the candidate cameras. No beauty score, silhouette percentage, exact reference ratio, or mathematical orthographic claim is made. Hair obscures the reference skull and part of the ears; hidden anatomy remains a construction decision. The generated supplementary construction study was not used as independent likeness authority.

## Pixel description before claims

The reference shows a warm-brown adult face with defined high cheeks, a firm tapered jaw, compact projecting nose, closed centrally full lips, strong shaped brows, and a calm stern expression. The visible ear is close to the skull and partly covered by hair.

R004 is a bald neutral-gray head with separate white eyeball presentation and brown circular irises. Its crown is rounded, its cheeks broad, its nasal bridge narrow and strongly defined, its mouth closed, and its ears exposed. Deep inner-brow folds, a stepped transition below the nose, a broad ear bowl, and an angular rear-skull/lower-neck silhouette remain visible. Absence of hair and skin materials is understood as this construction stage, rather than treated as a geometry defect by itself.

## Three largest remaining discrepancies

1. **Major: orbital and nasal-root construction, shape.** Front and three-quarter views show narrow pinched furrows running from the inner eyes into the brow, with abrupt under-eye and nasal-sidewall transitions. The combined gaze and surrounding shapes read strained and wide-eyed rather than the reference's controlled stern expression. The pale outer-eye crescents seen in the initial candidate are gone, but their removal does not resolve the surrounding form. Bounded correction: rebuild or directly adjust the inner-brow/nasal-root/orbital transition as a continuous anatomical region, with deliberate planes and eyelid support. Avoid another uniform smoothing pass over the entire head. Maintain eye and feature positions until the shared surfaces have a coherent shape.

2. **Major: nose-to-philtrum relationship, shape.** Profile and underside still show a strong inward step immediately below the nasal base. R004's nose is less dominant than the initial long wedge, but the tip, columella, alar base, and upper-lip transition remain weakly differentiated. Three-quarter views retain a narrow sculpted ridge along the bridge and compressed-looking nostril ends. Bounded correction: shape the nasal base and philtrum together; soften the abrupt depth step while retaining the small nostril apertures and short columella. Do not widen the mouth on the basis of this depth problem. The current images do not support an exact face-relative width measurement.

3. **Major: head/jaw silhouette and ear construction, shape.** Profile retains a flattened/angular occiput and a long diagonal rear transition toward the open neck. The lower cheeks/jaw still read as broad continuous mass rather than the reference's clearer cheek-to-jaw planes. The ears read as thick oval dishes with a continuous rolled rim and limited lobe/tragus differentiation. Bounded next choice: establish a deliberate rear-skull/jaw silhouette, then revise the exposed ear's outline and main folds using direct anatomical construction. Hair must not become a substitute for resolving these visible forms. Exact hidden skull shape is uncertain in the supplied reference.

## Per-region result

| Region | Advisory status | Visible improvement | Remaining limitation |
|---|---|---|---|
| Nose | REVISE; useful retained construction | Smaller, less front-facing nostrils than the first isolated study; reduced tip projection and less wedge-like profile than initial assembly | Narrow pinched bridge/root, stepped base-to-philtrum transition, and limited tip/columella/alar distinction |
| Mouth | REVISE; strongest component progress | Broad opening replaced with narrow closed contact line; profile shelves reduced; lateral lip taper improved | Upper border/cupid's bow still soft; lower-center fullness and under-lip transition remain rounded; contextual nasal-base relationship unresolved |
| Ears | REVISE; placeholder-quality main forms | Outer rim and internal depression readable; no missing-ear issue | Thick oval-dish impression, weak distinct lobe/tragus/antihelix construction, partially uncertain reference anatomy |
| Head/jaw | REVISE | Crown rounded compared with initial and R003; lower cheek definition somewhat clearer | Orbital furrows and soft jaw mass depart from reference; angular rear silhouette remains; identity not established |
| Visible joins | REVISE for visual continuity; technical acceptance NOT VERIFIED | Initial outer-eye crescents removed; R003's conspicuous straight nasal patch strip and apparent crown discontinuity are no longer visible in R004 | Nasal-root and under-eye shading transitions remain abrupt; small bright slivers persist at lower-neck edges in front/profile/underside; no pixel-only weld or topology claim |

The open neck is an understood assembly boundary, not a missing whole-body defect in this head-only study. Thin bright edge artifacts around it still warrant the operator's wireframe/normal/reversed-light check. Their geometric cause cannot be diagnosed reliably from these beauty renders alone.

## Revision comparison and regression check

- Initial to R004: observable reduction in nose projection; retained closed lips; removal of separate outer-eye crescents; rounder crown. These are actual visible improvements, not inferred from script success.
- R002 sampled views: straight, strongly separated nasal/root borders and shelf-like orbital transitions remained obvious. R004 integrates the region better but has replaced some of the straight border reading with pinched furrows rather than fully resolving the anatomy.
- R003 sampled views: a conspicuous straight central nasal patch and apparent crown edge discontinuity were visible. Those particular artifacts are not visible in the corresponding R004 front/profile/three-quarter captures.
- The ear did not receive a claimed R003/R004 comparison-based improvement in this review. Its R002 isolated and combined appearance remains a form revision item.
- No second-side, rear, wireframe, reverse-light, deformation, or engine regression verdict is included here.

## Advisory continuation recommendation

Preserve R004 and complete the pending technical/capture evidence. The next modeling work should target the orbital/nasal-root/subnasal transition with explicit form construction, followed by skull/jaw and ear structure. This is not a recommendation for repeated global smoothing or adding finished materials to conceal the form issues.

If the next bounded regional revision cannot improve these remaining major defects, change the modeling method or request focused owner guidance rather than repeatedly deforming the same patch structure. This reviewer does not self-issue Pram's reference, forms, or release approval. The model is a useful executed construction study with unresolved major visual defects.

## Reviewed pixel hashes

Paths below are relative to `FH1/r001/`. SHA-256 was read from the actual files after inspection.

| File | SHA-256 |
|---|---|
| `captures/combined_r004_front.png` | `4a2791beb93a4cc2a841d579864d550af963820db2087e75cd0feb32125386a1` |
| `captures/combined_r004_profile.png` | `faa87a090cebe9069eb4a223d58439bdb4924c87548abd1dcaaa35f55eaca03a` |
| `captures/combined_r004_three_quarter.png` | `bd4b161ba0684edd43e3fe944739b72e288ec94d94673d5dc125f241d7e09c74` |
| `captures/combined_r004_underside.png` | `736955293608f56ea5ccfbea53351cf3cb67e2bdd715df807f3a8f96f3827c99` |
| `captures/combined_initial_front.png` | `a51c063809ed472718c8ed12e252948ac4e1b64bda4c4fb69e4060c9754d2910` |
| `captures/combined_initial_profile.png` | `92a91445467caf683c36057576b691ed85f9518bc20bdfb88ae1d872f006bfdb` |
| `captures/combined_initial_three_quarter.png` | `1119cb0e41538460a14701db9d380d23c437f4d5d74036a0a7d26d561730baf1` |
| `captures/combined_initial_underside.png` | `bffa6db9398c0a10dd72e56524a724ba0576011e44571d0d9bc7361c151b85a7` |
| `captures/ear_r002_front.png` | `91989a9005f72a479aab8241aff4bbf3167683ced7ab9203c1bce71a5bf8646c` |
| `captures/ear_r002_profile.png` | `5d70cba87d4696e1865641cc2460f4b06981193c3682b7c162b44fad5b666068` |
| `references/user_portrait.png` | `ccdee0b58735a75d8e59f6a842c467b5dd1ee531d6d9cca1e29e8f26e9922984` |
| `references/user_turnaround.png` | `5f1640b44b8fabdbf04e3a7c8b3de5f1cd528a0f85d062358619cd23889b71bc` |

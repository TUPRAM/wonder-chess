# Independent head-polish review: current r014

Current verdict: **REVISE. Retain r014 as the best current checkpoint. Meaningful construction improvement is visible, but Ada's facial likeness is not yet established and no near-perfect match or human approval is claimed.**

Reviewer: head_likeness_review, independent model context. Date: 2026-09-08. Scope: facial/head shape and actual diagnostic images only; no hair, eyebrow, or eyelash expectations. This latest review supersedes the earlier working-baseline recommendation below.

## r014 evidence actually inspected

I inspected r014 front, profile, primary_fit, reverse_key, and openings images and compared baseline_primary_fit against r014_primary_fit. The source portrait was previously inspected at native resolution and remains the identity authority. This is an image-bound review, not independent validation of the final Blender snapshot, self-intersection audit, or human acceptance.

| Image | SHA-256 |
|---|---|
| r014_front.png | 471078700E185A8DA79D8915845FFC6FA78B16F16794CE1AA71FEC09C0A19843 |
| r014_profile.png | 2CAF4BA26DBE296E09C2F4494309A23FDB45B4E66FD8630760EB251894E87022 |
| r014_primary_fit.png | 2BD1E1C953E0AA403E2FEC58E1A7A22F946651780B7C27F11CA1FC8C998B578E |
| r014_reverse_key.png | 81016DD8B4D6388EF485797DC413C0761B4B78B61FB63C2F4A05B31AA6E71B46 |
| r014_openings.png | 9A2A87E8A85F9642959ACB6BA72E4477AF6ACC0C9DF707230430EC504E8E87A9 |
| baseline_primary_fit.png | 48DE2AF15D9665192D5975D5FD8F79204611707B21848548D3B32AC34DD9CA77 |

## Meaningful improvements retained in r014

- The baseline's sharp folded ridges at the inner brow and long nasal sidewalls are largely reduced. The face no longer reads as the same severe folded mask in the matched primary view.
- The nasal tip now has a separately readable convex volume instead of simply terminating a narrow wedge.
- The upper lip and surrounding muzzle are more coherent and less scalloped than the failed r002 version. The mouth remains closed and calmer in contour.
- Reduced cheek inflation and facial width produce a more purposeful taper.
- The rejected r012 shelf beneath the ear is removed. The visible neck transition is more continuous, although the jaw's anatomical turn is still weak.
- The openings image shows actual eye apertures rather than an embossed eye plaque. This observation does not independently establish the mesh's numeric validity.

## Remaining major defects

| ID | Severity | Observation and views | Required focused intervention |
|---|---|---|---|
| HP1-M01 | Major | Wide exposed globe and a startled expression remain in front and primary_fit. The upper lid is still too evenly arched relative to Ada's firm oblique opening. The corners and neighboring planes do not yet have convincing anatomical flow. | Directly edit the existing upper-lid arc and corner control vertices, preserving useful opening width while controlling globe coverage. Give the medial corner its own small transition and let the lid crease dissipate into the socket; do not repeat a global aperture-height scale. |
| HP1-M02 | Major | Nasal underside to upper muzzle still forms a long swept/recessed profile, with weak distinction between columella base, philtrum, and adjoining muzzle. The tip improvement does not resolve this connection. | Edit a connected profile strip from the columella through the philtrum and upper lip, with adjacent cross-sections defining the alar-to-muzzle volume. Preserve the compact tip while making the philtrum short and gently concave. Avoid compensating with dark nostrils or a sharper lip shelf. |
| HP1-M03 | Major | Cheek-to-jaw and lower-cheek-to-chin changes of plane remain generic and weak in primary_fit; Ada's firm diagonal contour is not established. The r012 shelf must not return. | Construct a lower, forward jaw turn through a small deliberate mandibular volume edit, keeping the skin immediately below the ear continuous. Review front and profile before retaining any silhouette change. |
| HP1-M04 | Major | Reverse-key lighting still reveals uneven broad transitions under the eye and beside the nasal root, including a cheek band and elongated medial transition. These are visible at the requested close-up scale. | Correct the sparse control-cage plane arrangement across the lid/socket/cheek junction, guided by cross-sections. Do not merely increase subdivision or smooth a selected rectangle. |

No additional critical defect is established by this image-only review. That is not a statement that all technical checks pass. The root agent's reported self-overlap audit remains a separate technical evidence item, not a substitute for these visual defects.

## Current method limit and next editable intervention

The current methods have produced visible construction gains, but continue to miss the requested likeness at the relationships between features. Another broad head-wide polish or smoothing pass is not supported by the evidence. Retain r014 and the fixed cameras. The user's pending feedback should select which remaining region leads; absent that selection, the strongest next local study is one connected medial-eye, nasal-sidewall, and upper-muzzle control-cage region. It should demonstrate an intentional upper-lid/canthus form and a clean nasal-base-to-philtrum profile while preserving cheek volume. Keep successful geometry outside that small study unchanged. Inspect the same front/profile/primary-fit/reversed-light views before retaining or extending the result.

The approximate primary camera improves comparison but does not make the illustrated source an exact orthographic measurement. The reference hair conceals portions of the skull and is explicitly outside this run; do not force the bare cranium to its hairstyle outline. No similarity percentage, full-forms gate, or human approval is issued.

---

# Historical comparison: r011 versus r012

Reviewer: head_likeness_review, independent model context. Date: 2026-09-08. Role: visual critique only; no human approval. Scope: head silhouette, eyes, nose, and mouth. Hair, eyebrows, and eyelashes are excluded.

Verdict: **REVISE. Retain r011 as the next working baseline. The r012 jaw change is a visual regression.**

## Actual evidence inspected

I inspected the primary 210 x 197 portrait and the actual r011/r012 front, profile, three-quarter, and primary_fit PNGs under this stage's captures directory. The primary portrait controls identity; the supplementary sheet is secondary construction guidance. This review is bound to the images below, not to an independently verified immutable Blender snapshot. I did not inspect or mutate Blender state.

| Image | SHA-256 |
|---|---|
| Primary portrait | CCDEE0B58735A75D8E59F6A842C467B5DD1EE531D6D9CCA1E29E8F26E9922984 |
| r011_front.png | F1D52116ACBE98DF063FA878B21EDF4D723215D3E2C0F85B319DBF363B565447 |
| r012_front.png | DA7B1CD80BE0B20EBC0C0CA560B08473C179803B34DEC32C58E83584B3325B79 |
| r011_profile.png | 3DF1EA2104E0520EC54A5DCAA9983F38FAEE6991D74A6226490D9F0BF983A6E2 |
| r012_profile.png | B6893E64BB145280B28F8AC5FE5E3AF3E8694AA4AE0105E516B44FB07B08B7E8 |
| r011_primary_fit.png | 75821E9E40BB8BD1BBADE77045266C05FDCD907DA4C137A61D3181D61A07AD8A |
| r012_primary_fit.png | CAC1AE98428001EEB34E7A814F510EBC58834843B3FA03F2CFCE51EFC3BBCACE |

## Three largest discrepancies

1. **r012 jaw/ear transition, major shape regression.** The front gains abrupt inward steps immediately below the ears. Profile, three-quarter, and primary_fit show a sharp shelf or crease emerging from the ear base. This is not the broad mandibular turn visible in Ada. Retain r011 continuity and construct the jaw angle farther forward and lower, through the mandibular body and ramus volume. Do not pull the whole lower-ear ring inward or sharpen this crease.
2. **Eye expression, major likeness discrepancy.** The new opening is recognizably almond and better constructed than r006's boxy aperture, but the wide exposed globe still gives a startled expression. The primary reference's upper lid is firmer and more oblique, with more upper-globe coverage. Continue using independent corner and lid controls; a wholesale vertical flattening would repeat the r002 squinting regression. Excluded eyebrow and lash detail must not be used to conceal this shape issue.
3. **Nasal underside to upper muzzle, major construction discrepancy.** The tip has a clearer separate turn than earlier revisions, but its underside and the philtrum still read as one long recessed/swept transition. Resolve the columella base, gentle philtrum concavity, and surrounding muzzle as connected volumes. Avoid making the entire bridge shorter or increasing nostril darkness to suggest shape.

## Mouth and silhouette priorities

The central upper lip is more visible and its contour is less scalloped than r002. Preserve that progress. It remains somewhat sharp at the border; a restrained roll and corners that recede into the muzzle are better next actions than widening the whole mouth.

r011's lower cheek/jaw remains too weakly articulated, but it is a cleaner starting point than r012's ear-base shelf. In the primary portrait the visible jaw turn is approximately (91, 140), whereas the lower ear attachment is approximately (80, 123), with several pixels of uncertainty. The jaw turn therefore lies forward and lower in image space. At apparent 4x primary_fit framing, the approximate target region is around (364, 560); r012's conspicuous notch is near (300, 515). These are loose review locations, not an exact silhouette acceptance test.

## Camera and acceptance limitations

The primary_fit view now has a pupil-line slope consistent with the source, making comparison more useful. The camera fit and individual points still carry uncertainty from illustrated perspective, gaze, and partly concealed anatomical landmarks. Preserve neutral front/profile cameras. Do not force the unknown skull contour to follow the reference hair silhouette. No similarity percentage, technical gate, full forms approval, or human approval is issued here.

Next action: retain r011; await the user's pending visual feedback while performing only independently justified local work. If continuing jaw construction, use a bounded lower-jaw volume study with continuous skin below the ear, then inspect all four established views before retaining it.

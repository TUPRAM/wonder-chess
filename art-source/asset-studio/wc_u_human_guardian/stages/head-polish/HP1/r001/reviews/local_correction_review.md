# Independent review: anatomical-right local correction, final r016

Reviewer: head_likeness_review, independent model context. Date: 2026-09-08. Final local verdict: **REVISE. Retain r016 as the best local result of the two attempts; do not extend or mirror it as an accepted likeness solution.** Two bounded attempts have been used. No further geometry attempt is recommended within this run.

## Final evidence actually inspected

I inspected all six r016 front, profile, three_quarter, primary_fit, reverse_key, and openings captures and compared them with the corresponding r015 and r014 evidence inspected earlier. I also inspected the actual r016 cage front/three-quarter images and the side-by-side r014/r016 front/profile/three-quarter comparisons. I read attempt_2.py after viewing the rendered result. I have not independently executed the geometry audit or verified a final immutable Blender snapshot. Reported non-manifold, degenerate, and self-overlap checks remain separate technical evidence. No model/UI access or geometry mutation occurred in this review.

| r016 image | SHA-256 |
|---|---|
| front | 758914BA635649547A57D47864EAC3730137C520A195BF5F85C3FACB4182202D |
| profile | E3886B69D90F179FF4FBF004AD3151A09A9F0F2EDFB0008A293605C4DDD03243 |
| primary_fit | E2EB3B55A4627D819FE7440DFB37F909BF271478A3D18FFA800B2158D1B3BC6A |
| reverse_key | F639EAF3E7B9774DE6290C7500DB6257732BC530CE78DD48124BDFE2DED14D50 |
| cage_front | 61468C4F5C5DFB5B54A74B9F48DF9831AB41CFAC43E35ADFF553283BCFAB8365 |
| cage_three_quarter | 72F953959C60302674BDDB87849663D09C2F88348B390FF805C31C70F2243911 |

## What improved

- Versus r014, the anatomical-right upper lid covers the globe more deliberately and reduces the startled expression. The medial socket transition is less severe.
- Versus r015, r016 restores a small convex upper-lid peak without returning to the fully open baseline arc. The result remains somewhat hooded, but is less flat.
- The abrupt right cupid/philtral peak from attempt 1 is reduced. The upper-muzzle gradient is more continuous.
- The center profile has received a small correction, but this produces only partial visual resolution of the nose-base-to-upper-lip relationship.
- The opening remains visibly real in the globe-hidden capture. The unchanged opposite eye is a useful comparison, not a target to edit during this local run.

## Remaining local defects

| ID | Severity | Specific observed defect | Evidence |
|---|---|---|---|
| LC-M01 | Major | The upper lid still reads as a hooded rim, and the medial corner/crease does not dissolve into the nasal sidewall with convincing plane flow. The opening is more useful than its surrounding transition. | front, three_quarter, primary_fit, reverse_key |
| LC-M02 | Major | The under-eye to upper-cheek surface retains an uneven broad band/turn. Changing the aperture alone has not resolved the connected socket and cheek volumes. | three_quarter and reverse_key |
| LC-M03 | Major | The nasal underside through columella/philtrum still reads as a long swept recession that ends at a projecting upper-lip shelf. The profile correction is partial; the intended short, gently concave philtrum and supporting muzzle are not convincingly established. | profile, primary_fit |

No new critical defect is established from these images. The local correction's intentional left/right difference is not itself classified as a regression: mirroring was deliberately excluded. Human approval, full-head likeness, and a near-perfect reference match remain unestablished.

## Shared-midline record

Attempt 2 explicitly names five shared midline controls (767, 248, 1098, 1064, 1030) within the columella/philtrum/upper-support chain. The source asserts negative-X control coordinates are fixed and records that adjacent subdivided faces respond to the shared seam. This is the correct distinction. I did not independently verify the coordinate assertions; the audit should retain that proof. No claim of zero opposite-side evaluated-surface change is made.

## Recommendation: local sculpt intervention, not extension

The cage images explain the limitation more specifically. Closely spaced rim rows expand quickly into much broader socket/cheek cells. At the medial corner, those rows turn into a narrow near-vertical nasal strip; that small area must currently supply the tear-corner recession, nasal-sidewall turn, and upper-cheek transition at once. Below the nose, the nasal underside spans toward the philtrum as broad sloping faces before meeting the more densely controlled lip boundary. These spacing and direction changes are visible cage observations. The inference is that the current depth edits improve a margin or profile point while leaving a ridge, bowl, or shelf in the intervening surface; the matched clay and reversed-light captures support that inference.

This does not prove the existing topology is mathematically incapable of a good result or that extra polygons would solve it. It explains why repeating the current coordinate/depth adjustment has not supplied separately controlled anatomical transitions. The next method should first establish the actual local volume and cross-section turns, then redistribute or rebuild only the controls needed to retain that shape.

Retain r016 and all frozen reference/camera evidence. Choose a focused local sculpt or directly rebuilt transition-surface intervention instead of extending this result across the head or running a third version of the same coordinate adjustment. Preserve the improved lid opening and corner landmarks as constraints. Reconstruct the small surrounding medial socket/nasal-sidewall/upper-cheek volume and the columella-to-philtrum profile as actual shape; then adjust or rebuild only the sparse cage needed to represent that corrected shape. Keep a defined outer boundary and record any necessary shared seam edits. The intervention must remain editable and local, with the existing aperture hidden-globe, front/profile/primary-fit, and reversed-key checks.

The limitation is not lack of polygon count. The two edits improved local landmarks but still did not establish the required relationships between neighboring surfaces. More global smoothing, a uniform lid scale, projection of the cheek onto the globe, or mirroring the current result would not address the observed failure.

---

# Historical review: attempt 1 / r015

Reviewer: head_likeness_review, independent model context. Date: 2026-09-08. Status: **attempt 1 / r015 remains REVISE; one second bounded correction is visually justified.** This is technical/art critique, not human approval or authorization to expand the editing scope.

## Scope and evidence

The reviewed scope is the anatomical-right eye/socket, nasal sidewall, columella/philtrum connection, upper cheek, and upper lip. Hair, eyebrows, eyelashes, jaw, ear, and the opposite eye are excluded. I inspected actual r015 front, profile, three_quarter, primary_fit, reverse_key, and openings PNGs under local-correction/captures, compared against the previously inspected same-camera r014 evidence. I read attempt_1.py only after viewing the resulting pixels. I did not access Blender or mutate geometry/UI.

| r015 image | SHA-256 |
|---|---|
| front | 63D6D32247359366D4A76C3744CF87788EB9F87FCEC02C2E72B3EF3A3E4F0D47 |
| profile | 0FCFDAB506D44454185822EFDA125DE0E9DCD852CF1638421BEF2202F66239BE |
| primary_fit | 5F86EE7361F03ECE16411A6B034520DBAA80CE74C1D1638B0D8E297104C62764 |

## Observations before author-source review

1. The right eye has more controlled globe coverage and a less severe medial-socket transition. This is useful progress. Its upper arc is now too straight and hooded, particularly in front and primary_fit. The new opening should not be narrowed further.
2. Right upper-muzzle support is more present, but a sharp local cupid/philtral peak appears in front and three_quarter. The skin transition should not terminate as this little ridge. The intended cupid's bow belongs to the lip border and should be shallow.
3. The side profile gains support above the lip but the central nasal-base-to-upper-lip recession remains. The improvement in the right flank cannot by itself establish a correct centerline profile when that profile is held fixed.

## Narrow second-attempt recommendation

- Restore a small convex upper-lid peak on the existing right controls j11-j13, tapering into j10 and j14. Approximately +0.8 to +1.2 mm in the central upper-margin height is a test hypothesis, not an exact anatomical target. Keep canthi and the current lower margin stable for this check; preserve coverage rather than returning to the baseline stare.
- Let the associated lid-body controls follow the revised arc while keeping the crease independently shaped. Do not regenerate all depths from the globe, alter the other eye, or apply a global aperture scale.
- Reduce the abrupt control gradient at the new right philtral/cupid peak. Do not widen the whole mouth, change its contact line, or add another wave to the surrounding upper muzzle.
- A very small number of central columella/philtrum profile controls could geometrically resolve the remaining centerline recess. Root must determine that these shared controls lie within the exact user-authorized scope. This reviewer does not issue permission.

## Shared-midline limitation

Moving shared midline vertices necessarily changes the adjoining negative-X faces and their subdivided surface, even when every negative-X control coordinate remains unchanged. Therefore a shared-midline correction cannot honestly be described as zero opposite-side surface propagation. If the user's boundary requires the opposite-side evaluated surface to remain unchanged, retain the seam and report the profile limitation instead of crossing that boundary. If the named columella/philtrum authorization includes the shared center profile, use only those named central controls, record their indices and deltas, retain all negative-X control coordinates, and inspect both sides of the seam. Do not mirror or propagate the correction across the head.

The second-attempt comparison must use the same cameras, diagnostic globe appearance, openings view, and reversed lighting. After that attempt, retain the best result and report any remaining local major defects without extending the two-attempt budget.

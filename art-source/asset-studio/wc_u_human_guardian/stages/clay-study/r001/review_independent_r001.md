# Ada clay study r001: independent visual review

Reviewer: Codex subagent `clay_review`, read-only Blender role. Date: 2026-09-08.

**Verdict: REVISE. The current method has not yet demonstrated the approved likeness or shoulder/hair construction. This is not human art approval and does not pass the whole-hero forms gate.**

## Evidence actually inspected

I opened and inspected all six supplied PNG files with `view_image`: the before/after three-quarter assembly, final front, true-profile candidate, back, and face closeup. I previously inspected the original selected concept, native `face-primary.png` and `torso-layering.png` crops, and the r002 construction illustration. The original head portrait remains the facial identity authority; `construction_decisions_r002.md` controls the agreed construction exceptions.

The files are supplied as Blender clay captures. This review establishes that I inspected their pixels; I did not independently query the Blender scene, camera matrices, saved source hash, or render execution. The views are adequate to identify the shape defects below, but no registered silhouette overlap or numeric likeness percentage is asserted. The parent supplied its own concerns with the review request before image inspection, so this is a separate visual assessment rather than a blinded review.

| Capture | SHA-256 |
|---|---|
| `captures/assembly_before.png` | `1e6c448cbfd9895dcded1c72a48db6cf04076f8619160c7a7097f9479e26b094` |
| `captures/assembly_after.png` | `f53663e3993f46cc47c4ee8dec583d12b11a2c67e19097588596eaca7f01610c` |
| `captures/front_r001.png` | `86d145bfa6eca17da0e9ef7195b8d59178f6ddf170e49a3c09dd43dfea8737fe` |
| `captures/profile_r001.png` | `63cb34f9cc1edbb978300e00cc2d49cf9fc3d594308a782454ab7f47c81bbaa2` |
| `captures/back_r001.png` | `649be6ca9ecfb953b3ddb6ee09cc04ef01dc68654b8c0ac0325b025ecf655e06` |
| `captures/face_r001.png` | `de1b223dc83e4c1a3a9c047c5658b873e96d678da3ea863a9386d36c1fc73ffc` |

## Three largest discrepancies

### 1. Major: facial anatomy and identity remain generic

Class: shape. Evidence: `face_r001.png`, `front_r001.png`, `profile_r001.png`.

The original has shaped upper eyelids, a recessed ocular surface, a convincing brow-to-socket transition, broad cheek planes, and a firm jaw. The candidate's eyes read as thin oval loops on flattened orbital patches. Its eyebrow strips sit separately above them, and the iris rings do not establish eyeball depth. In profile, the eye remains a surface appliqué. This is an anatomical construction defect, not a request for eye color.

The central face is softly blended and does not establish the reference's transitions between nasal bridge, cheek, nostril wings, philtrum and closed lips. The candidate has lip relief and avoids a large open mouth, but the mouth corners and upper-lip shape are indistinct. The ear reads as a narrow hoop rather than a helix, concha and attached lobe. The jaw and neck meet with a mannequin-like transition in profile.

Bounded next correction: change the local head construction method. Build explicit eyelid boundaries integrated into the surrounding socket/cheek surface, with a recessed eye volume behind the opening; reshape the brow ridge and cheek-to-jaw planes; then construct closed lip and mouth-corner transitions on that same facial surface. A fresh sculpt surface or a locally rebuilt polygon cage is justified. Do not spend the next pass adding iris detail, smoothing the entire head, or thickening detached loops.

### 2. Major: hair reads as straps on a cap, with a rope-like braid

Class: shape. Evidence: all final views, especially `profile_r001.png`, `back_r001.png`, and `face_r001.png`.

The broad sweep is directionally recognizable, but its very wide, nearly constant-width ribbons have abrupt independent ends and exposed areas of smooth cap between them. From the side and back, the pieces read as overlapping bands rather than organic masses emerging from the scalp and gathering into a braid. The after capture adds lengthwise grooves; these make the bands more explicit without correcting their underlying volume or roots.

The long, narrow, repetitive braid hangs straight down the back like a manufactured rope. The approved original shows fuller interwoven gathering at the rear of the head and a more compact upper-back termination. The current braid attachment and its small repeated lobes do not reproduce that hierarchy.

Bounded next correction: rebuild the sweep from fewer asymmetrical, tapered solid clumps with broad roots, varied cross-sections, and ends that merge into the rear gathering. Establish the hairline and scalp coverage without open cap wedges. Rebuild the braid with a fuller nape transition, fewer larger interwoven lobes, and a shorter compact tail. Inspect the silhouette before reintroducing any grooves.

### 3. Major: the shoulder assembly is too separated and band-like

Class: shape/construction. Evidence: `front_r001.png`, `profile_r001.png`, `assembly_after.png`.

Three plates are present, but their presence is not sufficient. The front and profile show three long, separated hanging bands stepping down the upper arm. The broad open gaps and near-parallel contours make them read as a ladder of strips. The reference shoulder is a compact protective assembly: a shaped upper shell wraps the shoulder volume, with substantially overlapping smaller plates underneath.

Bounded next correction: establish one compact shoulder volume and rebuild three nested shells around it. Give the upper shell a crown, front/back coverage and an intentional outer flare; nest the lower two mostly underneath it with restrained exposed margins. Verify thickness and clearance in profile, front and back. Preserve a real gap between steel and the padded sleeve, but remove the impression that the plates float independently down the arm.

## Other construction findings

- **Collar: major remaining garment-read defect.** The after version has a useful tapered shape and a less uniform top line. It still reads as a rigid open tube with a cable-like rim. Establish a padded garment cross-section, a narrow internal facing, and a believable base transition into the undercoat. Quilting is not required to establish those forms.
- **Breastplate: useful blockout, incomplete secondary forms.** Its tapered silhouette and planar upper transition avoid paired breast domes. The after shading is less cluttered. It remains a broad, largely featureless polygonal shell: the upper neckline/arm openings, controlled sternum transition, side wrapping and lower contour need construction work. The back has similar broad planes. The exposed side gaps and abrupt shell terminations should be reviewed as designed openings rather than assumed finished.
- **Upper fasteners: blockout only.** The two tubular/strap-like upper pieces do not yet express the original compact fastening plates. They can wait until the face, hair and shoulder volumes are corrected.
- **One shoulder and truncated torso are intentional study scope.** I am not reporting the absent second shoulder, lower body, hands, equipment or rear tabard as missing parts of this bust. The approved rear tabard split remains a later full-body requirement.

## Did the bounded corrections improve the candidate?

| Observed change | Assessment |
|---|---|
| Collar taper and top-line variation | A modest genuine construction improvement; still reads as rigid tubing. |
| Cleaner chest shading / reduced visible cage clutter | Easier to inspect the main planes; does not establish the missing secondary forms. |
| Upper shoulder repositioning | Some improvement in coverage near the neck; the separated-band assembly remains a major mismatch. |
| Hair grooves | No convincing improvement to the critical hair-volume defect; the ribbon construction remains. |
| Facial likeness | No meaningful improvement is visible between the supplied before and after captures. |

These findings concern visible results, not the number of successful operations. I did not review intermediate attempts beyond the two supplied assembly images and therefore do not independently certify the exact count of attempts.

## Recommended continuation

Preserve r001 as the inspected checkpoint. Change the construction method for the head's local anatomy, hair masses and shoulder shell arrangement before another polished assembly pass. Work first on the head and hair without armor hiding the neck/profile, then rebuild the representative shoulder. Produce another fixed front/profile/three-quarter set and a native face closeup. Do not proceed into full-body production, topology approval, UVs, material polish, rigging or animation on the basis of this study.

The technical ability to construct, edit, save and capture the source can be recorded separately. The actual clay remains **revise**, with major likeness and construction defects unresolved.

# Ada diagnostic clay r003: independent visual review

Reviewer: Codex subagent `clay_review`; date: 2026-09-08. Read-only scene role.

**Verdict: REVISE / likeness not demonstrated.** The shoulder and braid silhouette improved, but major facial and hair-construction defects remain. This report provides no human approval and does not pass the full-hero forms gate.

## Inspected evidence and limits

I opened all five r003 PNGs with `view_image`: front, profile, back, face closeup and three-quarter. Comparison uses the previously inspected r001 captures, original Ada identity concept and native face crop, and approved construction decisions. The original portrait controls likeness; the generated turnaround is not an exact orthographic blueprint.

| Capture | SHA-256 |
|---|---|
| `captures/front_r003.png` | `e18e786b16a413ff88d2c03a49496e06c6363e128adbf2e1dee22e5ff890b37f` |
| `captures/profile_r003.png` | `b6bf27e905c912bf676aca84e866264b27a467c44a2ca76bb5f7b32f836339d9` |
| `captures/back_r003.png` | `60bdcb473e1dbc846ecb886d697b3738bd981c7ea0b22b9238642cf09168dda5` |
| `captures/face_r003.png` | `8d6df642b17bd88c1bc9094be388986d94552988e1d7f734bbcdae7d25a50cd5` |
| `captures/three_quarter_r003.png` | `7c68660bb50ccdb68b40cf64c2b3798f041b4ae49847821857ef500195a35241` |

The parent supplied implementation notes and its concerns before the review; this is not a blinded assessment. I did not open the scene, inspect mesh topology, audit source hashes or verify the reported winding fix. The parent reports actual eye openings, bridged eyelid rings and zero inconsistent internal edge winding. Those are technical claims separate from the visible quality findings below. I did not inspect r002, so I do not independently establish its defects or the exact count of failed operations.

## Major remaining defects

### Facial construction and identity

Evidence: `face_r003.png`, `front_r003.png`, `profile_r003.png`.

The eye volumes now appear separated from the surrounding face, but the outlines read as protruding oval goggles. The reference's shaped upper lid, thinner lower lid, recessed eye, canthi and brow-to-socket transition are not present convincingly. The surrounding bridge surface shows visible stepped/jagged shading, with small dark notches at the corners and lower rim. These defects are especially evident at native face-closeup size. Their precise geometric or shading cause needs scene inspection; a zero winding-error count does not establish that this surface is visually sound.

Relative to r001, removing the floating eyebrow strips avoids that particular appliqué, but the original strong brows and their supporting anatomy have not been replaced successfully. The visible eye region is less clean overall. The central face still has softly blended cheek/nose/lip transitions, weak mouth-corner definition and hoop-like ears. Profile remains generic and mannequin-like around jaw, ear and neck.

Classification: major shape and visible surface defect. No accepted facial-likeness improvement is demonstrated.

### Hair construction

Evidence: `profile_r003.png`, `back_r003.png`, `face_r003.png`.

The retained earlier clumps remove the distracting groove treatment, but the main form remains a set of very broad, nearly constant-width bands over a smooth cap. The gaps expose cap wedges, and abrupt piece endings read as straps. The back lacks the reference's layered interwoven gathering before the braid. This is a primary/secondary-volume mismatch, not a lack of fine strand detail.

Classification: major shape defect. A new cap experiment being rejected is a useful selection decision, but the retained geometry is still not approved hair construction.

### Secondary costume and armor construction

Evidence: `three_quarter_r003.png`, `front_r003.png`, `profile_r003.png`.

The shoulder's new cup and tighter nesting are real progress. It now covers the shoulder more coherently, particularly in profile, and the lower shells sit closer together. However, the front/back edges still terminate like broad strips, the lower tiers remain geometrically repetitive, and the shoulder-to-sleeve/neck attachment needs a deliberate construction solution. The source is promising blockout rather than an approved finished assembly.

The collar still reads as a rigid tube with a cable-like border. The breastplate has a useful tapered shell and broad planes, but neckline, arm openings, side wrapping, lower contour and fastening construction remain incomplete. These findings are carried forward from r001 rather than newly discovered regressions.

Classification: major remaining construction work; shoulder overlap itself improved.

## Real improvements to retain

| Change visible in r003 | Assessment |
|---|---|
| More cupped upper shoulder shell and tighter lower overlap | Clear improvement in protective volume and profile continuity. Retain as a useful blockout direction. |
| Shorter braid | Clear correction toward the approved upper-back termination. |
| Fuller braid lobes | More volume than r001, but still reads as a regular flattened chain. A fuller nape gathering and less repetitive interweaving remain necessary. |
| Simpler retained hair surface | Less distracting than grooved ribbons; underlying hair-volume defect unchanged. |
| Revised eye openings and bridges | A different construction attempt is visible, but the present goggle outline and stepped surface remain a major failure. No visual pass follows from the technical winding repair. |

## Stage decision and next useful evidence

Preserve r003 as a diagnostic checkpoint and retain r001 for comparison. Do not advance to full-body production, UVs, materials, rigging or animation on the strength of these images. The unchanged critical likeness problem supports the parent's decision to stop this modeling iteration and obtain focused user feedback under the anti-stagnation rule, rather than adding decoration.

The next attempt should first demonstrate one clean eye/socket/cheek region and its likeness in a neutral face-only front/profile/three-quarter comparison. That proof should use a modeling method capable of locally controlling eyelid and facial surface continuity. Hair needs solid tapered clumps and an integrated rear gathering, not another globally smoothed cap or groove pass. Preserve the improved shoulder overlap and shorter braid proportion while changing the unsuccessful local construction methods.

The most useful user-facing review is the actual r003 face next to the original identity portrait, accompanied by the explicit statement that the current likeness has failed. Asking the user to approve the current clay as if it passed would misrepresent this evidence.

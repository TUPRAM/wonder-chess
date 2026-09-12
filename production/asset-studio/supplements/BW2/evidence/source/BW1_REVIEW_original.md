# Ada BW1 — body and costume review, technical checkpoint r003

**Status: ART_REVISE.** The independent MPFB body and layered costume candidate were executed in Blender. The requested convincing arm/grip and leg/boot proofs were **not achieved**. This is a reviewable development study, not a finished Ada, a production asset, a promoted recipe or a human approval.

## Delivered candidate

- Work file: `ada_body_costume_work.blend`.
- Frozen retained candidate: `ada_body_costume_checkpoint_r003_ART_REVISE.blend`.
- Frozen SHA256: `03829ab406d6bd5e6a1c5f86e045e9f2edc720b05e620e70017667c59be8b3f8`.
- Original r001 and r002 checkpoints and their faulty motion remain preserved as diagnostic evidence.
- Four retained scenes: `BW1_BODY_COSTUME`, `MP1_SOURCE_CONTROLS`, `MP1_ADA_HEAD`, `MP1_ARCHIVED_TRIALS`.
- The visible head is the unchanged MP1 contextual head, still ART_REVISE. Its neck interface is exposed and unjoined. No hair, eyebrow or eyelash objects are in the BW1 scene.
- Source, soft clothing, rigid armor, equipment, temporary rig and presentation have separate collections and editable objects. Failed cloth, sole and knee experiments are excluded from the final render allowlist.

The current game, packaged checkpoints, canonical data and shared runtime skeleton were not changed by BW1. The temporary MPFB rig has 163 bones; it is not declared compatible with the current 27-bone game skeleton.

## What visibly helped

1. **Coherent indexed foundation.** One full MPFB source supplies torso, limbs, hands and feet. Its 19,158 indexed vertices, original Basis/topology and 38 original shape keys remain intact; six native body-target keys were added only to the independent copy.
2. **Continuous upper-coat envelope.** Retaining the torso and sleeves as a continuous helper-derived garment removed the first extraction's jagged shoulder seams and improved static enclosure. Neck/cuff/hem tailoring is still rough, and this does not establish moving cloth.
3. **Right footprint sole.** A new closed three-ring loft follows the observed fitted boot footprint. It reduces the oversized sole silhouette and follows the sampled ankle rotation. The left sole remains the older blockout for comparison.
4. **Separate authored layers and rear split.** The rear tabard split is retained from the approved written construction decision, even though the approved generated sheet does not depict it clearly.

These are limited retained observations. No construction was independently replayed on a second compatible body, so **zero recipes were promoted**.

## Actual source use

Only one glove and one boot were extracted and fitted:

| Asset | Executed use | Provenance |
|---|---|---|
| MargaretToigo / MRT `toigo_gloves_short` | Native MHCLO fitting against the full indexed body; original finger envelope and UVs retained; temporary inherited weights; uniform clay | CC0 on original project pack page, packed registry, OBJ and MHCLO headers |
| MargaretToigo / MRT `toigo_ankle_boots_male` | Native MHCLO fitting; toe-box adaptation and separate original sole/strap construction; temporary inherited weights; uniform clay | Same corroborated CC0 evidence |

These are **licensed adaptations**, not meshes created from scratch. Complete publisher archives remain quarantined; other models were not imported. `culturalibre_hero_boots_1` was rejected before extraction because its OBJ license header contradicted the other CC0 records. Details and hashes are in `source-quarantine/SOURCE_REVIEW.md` and `source_inspection.json`.

The archives show current geometry and correspondence, not the creator's complete modeling history. Our proposed construction explanations are inferences. The numbered scripts and actual renders document what was executed here.

## Body preset and scale

Native target values were shoulder distance +0.12, torso V-shape +0.08, shoulder muscle +0.12 on each arm and hand scale +0.03 on each side. These are dimensionless installed MPFB target amounts, not centimetres or reference measurements.

The complete source skin measures **1.82000024 m**. The retained contextual head plus body feet measures **1.79924476 m**, excluding hair, soles and equipment. The distinction is deliberate: the original head was preserved rather than silently resized to fit the source scalp. Measured shoulder-joint span is 0.36369 m; hip span 0.21637 m; foot skin length 0.24060 m. Full definitions, matrices, torso sections and joint locations are in `reviews/body_measurements.json`.

The source retains the complete hidden head/helpers and all indexed correspondence. Preview masks are not destructive deletion. New garment Delete masks were disabled so they cannot conceal body intersections.

## Executed tests and remaining defects

| Test | Observed outcome |
|---|---|
| Front, profile, back and both three-quarter body/clothing views | Executed and inspected. Adult coherent foundation; substantial costume silhouette, plate-fit and tailoring defects remain. |
| Uniform clay and reversed key | Executed and inspected. Front/back plates stand away from the torso; horizontal facets, cylindrical shoulder bands and slab-like cloth remain apparent. |
| Open and relaxed hand | Executed as diagnostics. Connected digits and cuff preserved; these poses are not grip approval. |
| Sword and shield grip | **Failed.** Initial construction plus two corrections did not produce proper cylinder enclosure or opposing thumb contact. |
| Shoulder, elbow and wrist range | **Failed complete assembly.** Raised/bent arm exposes a shoulder-to-sleeve gap and excessive bracer back opening. Equipment contact remains unproven. |
| Planted boot and ankle flexion/foot roll | Executed. Right sole's static fit improved and it follows the foot; heel/upper/sole junction artifacts remain. |
| Bent knee and grounded kneel | **Failed complete assembly.** Knee cup coverage/attachment and greave overlap remain unresolved. |
| Range-informed step | **Failed cloth clearance.** The moving thigh passes through root-weighted hanging coat/tabard panels. |
| Short diagnostic action | 169 frames at 24 FPS, with marked pose samples. This is a local range probe, not the actual runtime Move clip or a production animation. |
| Actual Edit Mode cages | Captured for coat/sleeve, pauldron, glove, boot, footprint sole and greave. No rendered wireframe is substituted for editability. |
| Save/reopen and numeric audit | See `reviews/final_reopen_r003_audit.json` and `verification.json` for executed results and exceptions. |

The game Move was inspected read-only: its thigh range is ±22 degrees and calf range 19 degrees; exact source bone axes differ from MPFB. The local step uses those ranges as a diagnostic, not a validated retarget. `reviews/CURRENT_MOVE_RANGE.md` records the boundaries.

### Why the bounded methods stopped

**Grip:** the study inferred finger-forward from bone-axis metadata in the wrong coordinate frame. The handle frame pointed toward the wrist instead of the distal fingertips. Two corrective attempts then curled the fingers below/behind the cylinder. Final samples showed approximately 5.4 mm thumb penetration and 4.7–13.7 mm non-thumb clearances. The rejected studies, poses and closeups are preserved in `hand-pose-study/`. A later read-only endpoint-based frame diagnosis is explicitly UNTESTED. Equipment uses that corrected frame only as an unapproved blockout placement; no third grip attempt was performed.

**Knee:** the original shin-parented badge lost patella coverage in bend. A replacement thigh-side cup improved its static attachment but still lost coverage. Correction 1, a blended thigh/shin pivot, detached the cup in kneel. Correction 2, a weighted surface-parent proxy, introduced a larger placement error even at rest. The failed scene is frozen in `knee_surface_failed_ART_REVISE.blend`. The retained candidate restores the first thigh-side cup. This is not a successful knee articulation recipe.

The stops are visual/method failures, not connection failures. Further equivalent scripts or added subdivision are not justified by this run.

## Numeric fixes versus art results

The complete r001 motion review caught reproducible leggings extrusion spikes at frames 129 and 159. Fresh Workbench and Cycles renders reproduced the error. Modifier isolation showed that raw geometry, Armature and Subdivision were bounded; Solidify's even-offset correction introduced the spike. Disabling only `use_even_offset` removed outliers across all 169 tested frames while retaining 2 mm inward thickness. Clamp settings did not fix it. Technical r002 contains that leggings modifier correction.

A more sensitive temporal scan of r002 found the same Solidify problem in the continuous upper coat. Matched frame 67 renders exposed a thin spike behind the right shoulder. Disabling only the coat's `use_even_offset`, while retaining its 6 mm inward thickness, reduced the largest adjacent-frame vertex jump from 0.65880 m to 0.04885 m and removed flagged outliers in the independent 169-frame probe. Technical r003 stores that second property change. The stopped art methods were not reopened: source geometry, shape keys, weights and diagnostic action remained unchanged across these two technical revisions.

The final source-bound movie, 169 PNG frames and review are in `motion-r003/`. Faulty predecessors remain in `motion-final/` and `motion-r002/`. These numerical corrections do not fix the known panel penetration, failed grips or armor attachments. Native work and frozen saves have different file hashes; independent reopen compares their scene, geometry, keys, weights, rig and action semantics instead of claiming byte identity.

The r003 contextual captures are named `captures/r003_context_*.png`. Earlier body and cage views retain unchanged source geometry; their original capture provenance is preserved. `reviews/reference_comparison_r003.png` is an unregistered visual comparison, not a likeness score.

The final audit found two stray 10-vertex wrist-helper components in the derived leggings. These were removed from that garment only, leaving its single 945-vertex lower-body component. The source indices and full body were untouched.

Imported skeletal weights were normalized separately from MHCLO fitting coefficients. This affected 125 glove and 347 boot vertices. Effective posed geometry changed by 0 for the glove and at most 2.24e-8 local units for the boot; Blender already normalized the evaluated deformation. This fixes stored numeric data, **not the failed grips**.

## Recommended next intervention

Keep the indexed body, source correspondence and right footprint sole. Begin the next authorized art assignment with **one correct hand/handle frame and one opposing-thumb grip**, using actual MCP-to-tip endpoints and a fixed, dimensioned cylinder. Solve that one contact before returning to full equipment presentation.

Treat armor suspension and cloth deformation as separate tasks: one constrained pauldron/sleeve interaction; a deliberately articulated knee/greave interface; then leg-aware panel weights or a tested cloth control method. Do not promote the current band shells or root-weighted skirt panels into a generator.

Independent replay, second-body fitting, recipe promotion, hair/facial changes, final textures, full animation bank, export/reimport and Unreal integration were **not run**. No human forms or release approval was recorded. AS1 retains the current brief/reference acceptance and pending downstream gates.

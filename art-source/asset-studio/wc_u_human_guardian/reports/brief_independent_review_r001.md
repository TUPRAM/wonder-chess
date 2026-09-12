# Ada AS1 independent technical brief review r001

Reviewer: Codex ada_contract_review independent pass

Reviewed on 2026-09-08. Recommendation: PASS for the technical brief gate only, against candidate `reviews/brief/candidate_6574e1c0271c4972b2264aee57013ba8.json` and design revision `ada_as1_scratch_r002`. This review neither approves the references nor accepts any modeled, rigged, imported or packaged character. The approval record is created separately by `assetctl.py` with role `technical_reviewer`.

## Corrected candidate and evidence identity

The first candidate, `candidate_e4e72ce8cb1044ccb8a2eab95a729b61.json`, was not approved. Its original brief and inventory had reversed anatomical X signs. The review lane initially overlooked that error; the tool-verification lane identified it before approval. The new source artifacts correct the mapping to right = +X and left = -X when forward = +Y and up = +Z. The original artifacts remain historical evidence, with no inherited approval.

Current manifest SHA-256: `bcf236683e1a61c4afc1755d42828047ed0644201e17657cf629025a2ae5789e`.

Current AS1 manifest/rules digest: `5738b0420db276f8f3450110e22adc176dd3733ece3b36984ac7b3aada871860`.

| Reviewed source | Verified SHA-256 |
|---|---|
| `stages/brief/brief_r002.md` | `e2c840a00f5c1823d7c7cb1244293bf25ebef225d08e20170c1068363421a646` |
| `stages/brief/canonical_snapshot_r001.json` | `d85964ef49b0b68bcd0e1076588c6f86fe85f500c22549de6e795512cb756c24` |
| `stages/brief/part_inventory_r002.json` | `40be34c36927e785a51b55157b2b03367b061ea711b9dc1b0b362a144b340b9d` |
| `inputs/provenance_r001.json` | `5157a377e35f53f9c7d4053374e1a999181233b58abfc4b5463e25dda5c7be22` |
| `stages/references/construction_decisions_r002.md` | `dc2ad675c381b66381dbb915db762160123a96d6c017d69b90e64f9bf4e919d1` |
| `reports/brief_r002.json` | `75cb8849b5f0048cd2d2d9397570abaf0c5ad6579b687bceea59f292338624bc` |

All five evidence files matched their sealed byte counts and SHA-256 values. The report hash also matched. The six source hashes embedded in the canonical snapshot matched the live files, and the complete copied Ada unit object exactly matched the current `data/units.json` object. `Studio.validate_snapshot()` passed for this candidate using the installed AS1 helper. Before recording this review, `state.json` contained an empty accepted map.

## Brief checks

| Required check | Result | Actual observations |
|---|---|---|
| `scope_and_asset_type` | PASS | Hero route and stable ID are retained. Forty-four semantic parts cover body, head, hair, costume, armor, hands and equipment, with parent, treatment, symmetry, references, risks, ownership and authoring-source policy. All geometry, textures, materials, rig and motion are to originate in a new isolated source. Existing canonical asset paths are provenance only. |
| `rights_and_upload_policy` | PASS | The package identifies the two supplied images and their origins/hashes. It limits use to the requested private task and built-in reference generation. Third-party uploads/jobs, purchases and public publishing remain unauthorized. It makes no independent copyright-clearance claim. |
| `dimensions_and_camera` | PASS | Height is 1.82 m, logical footprint is one tile, source units are meters with +Y forward/+Z up, and corrected anatomical coordinates place the right sword at +X and left shield at -X. Root remains at ground. The normal board camera and closer art-review override are explicitly distinguished. The construction A-pose is a proposed source pose, not a measured claim about generated illustrations. |
| `budgets_and_dependencies` | PASS | Canonical seven clips, 60 FPS, in-place/root-motion policy, four socket interfaces and simulation-owned timings are preserved. Triangle, texture, material, bone and influence values remain unprofiled starting targets. Reference, forms and release require owner approval. The bust study cannot substitute for complete-hero forms acceptance. |

No unresolved critical or major defect was found in the corrected technical brief. Proposed design amendments are clearly pending the reference decision; this brief acceptance does not adopt them into canonical art data.

## Exact camera source

Reviewed source: `game/Source/WonderChessRuntime/Private/WCBoardPresenter.cpp`, SHA-256 `e08999a1dc98343dbe2e40bf6957a9da9dbd0b101c4ca8125a8e1f497dd3df90`.

- Lines 142-150: normal orthographic camera at `(2450, 0, 2800)` cm, rotation pitch/yaw/roll `(-50, 180, 0)`, orthographic width `4300` cm, `MaintainXFOV`.
- Lines 153-156: `WCArtReview` override at `(2400, 0, 3100)` cm, rotation `(-52, 180, 0)`, width `2300` cm.
- Lines 75-76: tile pitch `200` cm.

These are source-code observations, not newly executed gameplay evidence. Eventual camera acceptance still requires 1920x1080 and 1280x720, crowded encounters, both team orientations, normal motion and the 96-pixel identity test.

## Supplemental pixel review: pending reference stage

The selected supplied concept and both new construction candidates were actually opened as images. This supplemental inspection does not issue an art-review or human-reference approval.

- `ada_construction_r001.png`, SHA-256 `5f1640b44b8fabdbf04e3a7c8b3de5f1cd528a0f85d062358619cd23889b71bc`: the front and rear tabard tips extend below the knee line; the frontal collar divides into navy and ivory halves; extra diagonal belt sections and side fittings remain. These conflict with the selected proposed short-hem, continuous-collar and single-belt interpretation.
- `ada_construction_r002.png`, SHA-256 `c65d1d5093f9b15d71cf1e3dfaed059253d659a17a02fc4949533a532486e05b`: the hems are shorter, the ivory collar is continuous and the waist has one simple belt. The face, swept dark braid, broad steel shoulders and ivory/navy grouping retain the supplied identity. The rear tabard has lost the center split and the upper fasteners/shoulder segmentation are simplified. The r002 construction decisions explicitly retain the original rear-split and shoulder/fastener design while using the new above-knee hem. That component-level source priority must be visible in the packet presented to Pram.

Side-arm projections alone do not establish a pose mismatch: lateral abduction may project out of a profile view. Conversely, generated labels and roughly matched silhouettes do not prove a shared measured A-pose or exact orthographic projection. No registered overlay, silhouette score or 3D-likeness percentage was used. Future source geometry needs real fixed-camera front, profile and three-quarter evidence.

Reference approval remains necessary for the explicit changes to braid length, gold distribution, full radial sun, glove construction and back treatment. Hidden shield grips, collar internals and plate clearances remain proposed construction. They have not been built or visually validated in 3D by this review.

## Verification and limits

The independent verification used Python JSON parsing and SHA-256 comparisons, exact canonical-unit equality, the installed AS1 snapshot validator, source reads, and actual image viewing. The verification process exited 0. The corrected inventory retains the already reviewed 44 part records and changes the anatomical axis mapping; its full current bytes were rehashed.

No old Ada scene was opened in this review. No modeling, Blender deformation, texture baking, skeleton testing, animation playback, Unreal import, reimport, performance measurement or packaged-game review was executed by this reviewer. No human gate was approved. The next dependency is completion and Pram's approval of the concrete reference/interpretation packet, followed by the new-source head-and-torso method study.

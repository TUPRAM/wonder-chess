# ACB1 independent preservation and provenance review

Observed between 2026-09-08T16:46:25.351587+00:00 and 2026-09-08T16:46:25.707844+00:00.

**Preservation: PASS**. 11/11 protected-source files match the recorded hashes. 31/31 reference-ledger evidence entries match, the ledger-bound reference report matches, and 3/3 FH1 reference copies match their recorded hashes. All successful reads had stable byte size and modification time.

Frozen r016 is independently located in HP1/r001/local-correction/verification.json and matches the parent-supplied expected hash. Frozen r014 matches its prior protection record and the parent-supplied hash. The earlier protected MR1 files, r003 baseline, FH1 work/checkpoint, reference decision file and approval ledger are also unchanged. The mutable ACB1 work file is not an immutable-source acceptance target.

## Source and artifact identity

- Frozen input r016: `art-source/asset-studio/wc_u_human_guardian/stages/head-polish/HP1/r001/ada_head_polish_checkpoint_r016.blend`; SHA-256 `775815688dc4aa30dce7085b78ef79bf9ff89f603f243af9110d8ef7b8d00b6b`.
- Earlier frozen r014: `art-source/asset-studio/wc_u_human_guardian/stages/head-polish/HP1/r001/ada_head_polish_checkpoint_r014.blend`; SHA-256 `95f8c084c97914a9a6ab198764a3ba80f478dac6fbd8e5b3cc8132d37599d851`.
- Current work snapshot: `art-source/asset-studio/wc_u_human_guardian/stages/head-closure/ACB1/ada_closure_work.blend`; 13990913 bytes; SHA-256 `0bb2e2df185a14aca0ce73e74b218da58e31b7a655ab9d6e6bfed65fe725ab78`; modified 2026-09-08T16:45:52.686817+00:00. This is timestamp-bound and may change when root saves.

Root reports that ACB1 was initialized by cloning r016 and then received native local sculpt strokes. The preserved r016 source and its expected hash are verified here. The initial cloning action and stroke execution are not independently established by this filesystem audit. File size, object-count assertions, a saved script and image names do not prove source selection, sculpt quality or a reconstructed cage.

## Reviewed source scope

`00_setup_target.py` requires the exact ACB1 work path and inspects the selected mesh and Subdivision modifier. It creates a new ACB1 scene, copied camera/light/diagnostic-eye objects, a separate baseline mesh, an evaluated sculpt target, an origin copy, and a hidden cage copy explicitly marked `INPUT_CAGE_PENDING_RECONSTRUCTION`. It does not add subdivision a second time in this source. It creates local masks and protected opening-collar attributes on the new target. The mask is source intent; its effectiveness during native strokes requires live geometric checks.

The setup reads the active source object rather than selecting it by frozen-file hash. It records the r016 hash as scene metadata, but the metadata is a declaration rather than independent proof. It makes no topology reconstruction operation on `ACB1_HEAD_CAGE`; its existence cannot be presented as newly reconstructed topology.

`01_render_target.py` alternates the baseline and target render visibility under the same named ACB1 cameras. Reverse-light and eye-visibility diagnostics act on ACB1 copies with try/finally restoration. The reviewed source contains no hair, brow, lash, torso or armor geometry edits, no material-node edits, and no writes to the old frozen sources. Native sculpt strokes and any unscripted live edits are outside this source review. The separate pixel reviewer reports `PARKED_ART_REVISE` in reviews/sculpt_review.md; that is their actual-image judgment, not a new visual verdict from this preservation task.

`02_audit_and_freeze.py` reads target/origin differences and input-cage arrays, then creates a separate copied input-cage wire diagnostic. It explicitly labels the outcome `PARKED_ART_REVISE` and reconstruction `NOT_RUN: sculpt target failed visual gate`. Its final save paths are the ACB1 work file and the new `ada_closure_checkpoint_ACB1_ART_REVISE.blend` with `copy=True`. No reviewed statement rewrites frozen r014/r016 or reconstructs the input cage. The audit code is inspected source; this task did not execute it or certify its numerical output.

All three operation files were parsed as Python without execution. Exact hashes follow. Further files added after this observation are outside this review.

| Operation | SHA-256 | Syntax |
| --- | --- | --- |
| 00_setup_target.py | `d8a258cd680a8136dda33ae810340d29d2b3a5343afda819a5386c6a2dd0e60d` | PASS |
| 01_render_target.py | `25ed26737b3fd56bbb1d80e69e9469148cd73c99a7cfbd1923c63a378021a60c` | PASS |
| 02_audit_and_freeze.py | `e3f556ecfd1bdba4e0d35cb976221d8c88506d879785508602f438d6e859e209` | PASS |

## Acceptance boundary

This audit used only local filesystem reads and source inspection. It made no Blender, socket, native-UI or rendering call; executed no supplied operation; and did not inspect .blend structures, native strokes, evaluated meshes or actual rendered pixels. It therefore does not certify unchanged cage coordinates, protected opening tolerances, zero unintended overlap, topology quality, likeness, bilateral coherence, or successful target-to-cage transfer. Root owns those live and visual observations.

The original reference ledger records human reference acceptance only and explicitly says identity is not authenticated. Its bytes and bound evidence are preserved; this audit grants no new reference, modeled-forms, development-use, rigging, Unreal or release approval. The supplementary construction images remain reference copies; their hashes do not turn them into measured 3D blueprints.

At this observation, the following ACB1 checkpoint snapshots existed: `art-source/asset-studio/wc_u_human_guardian/stages/head-closure/ACB1/ada_closure_checkpoint_ACB1_ART_REVISE.blend` SHA-256 `5deb2ead3d282a6ea0646452f2ee85a35506a5f4b1a1d275b8711623dbe96e2c`. These are observed files, not artistic approval.

## Protected-source hash table

Paths below are repository-relative. Expected records come from the prior actual preservation/verification records; r016 is additionally traced to local-correction/verification.json.

| Protected source | Current SHA-256 | Result |
| --- | --- | --- |
| art-source/asset-studio/wc_u_human_guardian/stages/method-recovery/MR1/r001/face_proof_r002.blend | `90c10ffc6c0182f110dda9099281543142100b8592fd769558d3fee12ed1831f` | PASS |
| art-source/asset-studio/wc_u_human_guardian/stages/method-recovery/MR1/r001/hair_mass_proof_r002.blend | `9a975792a03087a4dfdb32a2889a58db797a557e012514f560633a2e2414726b` | PASS |
| art-source/asset-studio/wc_u_human_guardian/stages/method-recovery/MR1/r001/contextual_head_candidate_final.blend | `751e43f061d05626f8b7adb9492cff85edbee1c4530bf76df0939390e5b02fab` | PASS |
| art-source/asset-studio/wc_u_human_guardian/stages/method-recovery/MR1/r001/ada_method_proof_work.blend | `751e43f061d05626f8b7adb9492cff85edbee1c4530bf76df0939390e5b02fab` | PASS |
| art-source/asset-studio/wc_u_human_guardian/live/ada_clay_study_r003.blend | `15f7fdc7c842d57ff05873a7cd988637411ad8985eadf852757ebbd62877043b` | PASS |
| art-source/asset-studio/wc_u_human_guardian/stages/references/construction_decisions_r002.md | `dc2ad675c381b66381dbb915db762160123a96d6c017d69b90e64f9bf4e919d1` | PASS |
| art-source/asset-studio/wc_u_human_guardian/reviews/references/accepted_f6ea0a9d2e1f427790481f24f4b6b346.json | `c199ef9bcaef185cadee12355bb0f353b4d1adedd920d0cea2fe66327e4fb3b9` | PASS |
| art-source/asset-studio/wc_u_human_guardian/stages/features-head/FH1/r001/ada_features_work.blend | `e773b3ddcf5fd7df744b1024b9d5538378f361e93975ef0dcf8cb611cc0688b0` | PASS |
| art-source/asset-studio/wc_u_human_guardian/stages/features-head/FH1/r001/ada_features_checkpoint_r004.blend | `9fb627c90655c0cfc227d85aad4448c260cd53650034c5b7d6e5c93cb94785e3` | PASS |
| art-source/asset-studio/wc_u_human_guardian/stages/head-polish/HP1/r001/ada_head_polish_checkpoint_r014.blend | `95f8c084c97914a9a6ab198764a3ba80f478dac6fbd8e5b3cc8132d37599d851` | PASS |
| art-source/asset-studio/wc_u_human_guardian/stages/head-polish/HP1/r001/ada_head_polish_checkpoint_r016.blend | `775815688dc4aa30dce7085b78ef79bf9ff89f603f243af9110d8ef7b8d00b6b` | PASS |

<details>
<summary>Reference-ledger and supplementary-copy hash details</summary>

Approval ledger: `art-source/asset-studio/wc_u_human_guardian/reviews/references/accepted_f6ea0a9d2e1f427790481f24f4b6b346.json`. All evidence paths are resolved beneath the active asset directory. Preserving a rejected-render record preserves evidence, not acceptance of that rejected design.

| Evidence path | Current SHA-256 | Result |
| --- | --- | --- |
| art-source/asset-studio/wc_u_human_guardian/stages/references/construction_decisions_r002.md | `dc2ad675c381b66381dbb915db762160123a96d6c017d69b90e64f9bf4e919d1` | PASS |
| art-source/asset-studio/wc_u_human_guardian/stages/brief/part_inventory_r002.json | `40be34c36927e785a51b55157b2b03367b061ea711b9dc1b0b362a144b340b9d` | PASS |
| art-source/asset-studio/wc_u_human_guardian/stages/references/reference_index_r001.json | `f222cf76e9a296d584f5d646857916b35b1c3e980a42dcc95d875a9fe0aa24b1` | PASS |
| art-source/asset-studio/wc_u_human_guardian/stages/references/blender_r001/ada_reference_scene_r001.blend | `b304de05d93d3ba78562ccc80551750f03e8ba27b81d7e1e19ef55ce33d6306b` | PASS |
| art-source/asset-studio/wc_u_human_guardian/stages/references/blender_r001/calibration_r001.json | `056403e9467e7cb2b7e016b6b1f5ac45d0f24e6886e2323f18ab0e22a3cac142` | PASS |
| art-source/asset-studio/wc_u_human_guardian/stages/references/reference_review_r002.md | `1e547669bf2e4d060f21a3175b5bc747e6863d54b64b5edfa78bd4a000dd45d1` | PASS |
| art-source/asset-studio/wc_u_human_guardian/stages/references/source_image_review_r001.md | `6f84a63f2d9ef78fa406625d115257cf05e3477694773bad1bb53ec6c4729d04` | PASS |
| art-source/asset-studio/wc_u_human_guardian/reports/image_generation_r001.json | `65bf0885bda631d418673b52052e41dd0a4fdfcb7f832a997f215fa64a5d47ee` | PASS |
| art-source/asset-studio/wc_u_human_guardian/reports/reference_scene_execution_r001.json | `d5bca95e9223d102552cec0cf82bd6bc69b42bb3190db2486c682d69e08fd4da` | PASS |
| art-source/asset-studio/wc_u_human_guardian/stages/references/blender_r001/saved_scene_audit_r001.json | `9d8689727f5df3cca106d4fe04ecb403d2b50f47a9c86fd8df173c5da71edd49` | PASS |
| art-source/asset-studio/wc_u_human_guardian/inputs/provenance_r001.json | `5157a377e35f53f9c7d4053374e1a999181233b58abfc4b5463e25dda5c7be22` | PASS |
| art-source/asset-studio/wc_u_human_guardian/stages/references/blender_r001/native-crops/crops.json | `6ce9271bb544a881b0447942d75864af3cd2a0effb7d2ee93954d4df7031d8f0` | PASS |
| art-source/asset-studio/wc_u_human_guardian/inputs/ada_selected_concept.png | `891ecb33ae496156c2824578ab0b92daafdefa00c48070072899c720939fa432` | PASS |
| art-source/asset-studio/wc_u_human_guardian/inputs/ada_rejected_render.png | `f371269c7c3efaac4130379fd7a091b3af8c964535a3c7575ddfc6a95be877d7` | PASS |
| art-source/asset-studio/wc_u_human_guardian/stages/references/ada_construction_r001.png | `5f1640b44b8fabdbf04e3a7c8b3de5f1cd528a0f85d062358619cd23889b71bc` | PASS |
| art-source/asset-studio/wc_u_human_guardian/stages/references/ada_construction_r002.png | `c65d1d5093f9b15d71cf1e3dfaed059253d659a17a02fc4949533a532486e05b` | PASS |
| art-source/asset-studio/wc_u_human_guardian/inputs/crops/action-context.png | `354378b270194277b0a5ddd75bee01709a631fdd39f66da56e77b2570c8fd566` | PASS |
| art-source/asset-studio/wc_u_human_guardian/inputs/crops/back-panel-candidate.png | `a578ced66cfef03a049b987de7362e9a29b69242dd36f2d1ebf70376c0edfa56` | PASS |
| art-source/asset-studio/wc_u_human_guardian/inputs/crops/boot-knee-context.png | `934cd98d7594aed207e1146e2f6b671fa87975769d73cd0ef9b2f80b6f0cd095` | PASS |
| art-source/asset-studio/wc_u_human_guardian/inputs/crops/face-primary.png | `007bb9f56c127d44a3d8d2c6cb850485fb00664348af6716f18b75d8448e2236` | PASS |
| art-source/asset-studio/wc_u_human_guardian/inputs/crops/front-panel-candidate.png | `5dd4945eb8f4c514daad6afa07a8acc344d4f0b8be1f60cdf4fa44342656df4b` | PASS |
| art-source/asset-studio/wc_u_human_guardian/inputs/crops/hair-back.png | `958e093703b9c0255a24a1708263a58303e502285c1cbfa2c44d939a2a7bf0d4` | PASS |
| art-source/asset-studio/wc_u_human_guardian/inputs/crops/identity-three-quarter.png | `f73dc53cac40236208c55c5cd64c8d6f78c6b379e603611a819277ac9ff4daf1` | PASS |
| art-source/asset-studio/wc_u_human_guardian/inputs/crops/shield-detail.png | `eba09dad51eb5b1f0d0d6bcc4cbbeda2ea823311757af60e2015bb4056024001` | PASS |
| art-source/asset-studio/wc_u_human_guardian/inputs/crops/side-panel-candidate.png | `9fb04714efa8ddbdfc649abbcd61667ebabb908235bd105b3550282b5a4b93b7` | PASS |
| art-source/asset-studio/wc_u_human_guardian/inputs/crops/sword-detail.png | `c56a0e2e0336123ecf072160396e6d6a56236e5b2299f9eeff8dee244f5358bc` | PASS |
| art-source/asset-studio/wc_u_human_guardian/inputs/crops/torso-layering.png | `fc525a536af496477df808644fe92d74b5fa726b8ffa4c8ee85eceb06ab34c52` | PASS |
| art-source/asset-studio/wc_u_human_guardian/stages/references/blender_r001/native-crops/body-back.png | `0b9380b883b6d68fd479448102bcd4ea7b0635c7431e645fd5246f6f745e25fb` | PASS |
| art-source/asset-studio/wc_u_human_guardian/stages/references/blender_r001/native-crops/body-front.png | `ad65e46308dd96414a7c0471622e7ee54079dc081427d12cc46cbaeff0bf6811` | PASS |
| art-source/asset-studio/wc_u_human_guardian/stages/references/blender_r001/native-crops/body-left.png | `2e8094a2573460b40c869cc6b87d6ff0c1eb5d210f7fe0f0dbbefbcf775b863a` | PASS |
| art-source/asset-studio/wc_u_human_guardian/stages/references/blender_r001/native-crops/body-right.png | `e33cb5f59bffe8f5bdf42ab2f315a3d9783a3d73a88513866cf2c28fefba01a9` | PASS |
| art-source/asset-studio/wc_u_human_guardian/reports/references_r002.json | `2d592f40f03c795c4affcbbfcb39fd76fe43ca214758238099ec63973ff82bd1` | PASS |
| art-source/asset-studio/wc_u_human_guardian/stages/features-head/FH1/r001/references/supplementary_construction_study.png | `d6fb15a50c2816830b9299fdd161c481a0fc1fac8e9e3dd281a62f156da710d0` | PASS |
| art-source/asset-studio/wc_u_human_guardian/stages/features-head/FH1/r001/references/user_portrait.png | `ccdee0b58735a75d8e59f6a842c467b5dd1ee531d6d9cca1e29e8f26e9922984` | PASS |
| art-source/asset-studio/wc_u_human_guardian/stages/features-head/FH1/r001/references/user_turnaround.png | `5f1640b44b8fabdbf04e3a7c8b3de5f1cd528a0f85d062358619cd23889b71bc` | PASS |

</details>

This verification task wrote only `stages/head-closure/ACB1/reviews/preservation_review.md`. No protected artifact, shared state, script, scene or candidate was modified.

Final source-review extension at 2026-09-08T16:47:16.662735+00:00: `02_audit_and_freeze.py` was read in full; SHA-256 `e3f556ecfd1bdba4e0d35cb976221d8c88506d879785508602f438d6e859e209`. Frozen r014 and r016 were rehashed again and both still match.

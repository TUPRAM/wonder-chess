# Wonder Chess successor — playable laboratory checkpoint

Recorded 2026-09-11, Singapore time. The adopted M0–M7 programme remains in progress. This checkpoint delivers a packaged six-creature combat laboratory, tested tournament/economy foundations and reviewable art references. It does not close human gameplay, finished art, full tournament presentation, performance, online or release acceptance.

## Play this candidate

Double-click [Launch Wonder vNext.cmd](../../Launch%20Wonder%20vNext.cmd) in the workspace. It selects **WonderChess-VNext-Lab-r3**, the `wonder_vnext` profile and its laboratory entry point. Do not start the package executable without those launch arguments: the default entry remains the preserved legacy flow.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/unreal/launch_vnext_lab.ps1
```

The [play guide](../../docs/vnext/LAB_PLAYGUIDE.md) explains placement, facing, relic fixtures, pause/step and repeatable formation experiments. [The implementation matrix](../../docs/vnext/IMPLEMENTATION_MATRIX.md) maps the whole blueprint to actual work and remaining requirements.

The laboratory supports two formations of up to ten units, three stars, initial orientation, compatible relics, automatic combat, event inspection and exact replay. Bellback, Cragstoat, Grandmother Root, Snapvine, Prism Organ and Reefglass execute distinct mechanics. Their 3D bodies and the board are explicitly unapproved gameplay proxies.

## Implemented systems and important limits

- A separate canonical catalogue, strict schema, generated native/runtime definitions, fourteen dossiers, twelve relic designs and race/class coverage reports. Six heroes are active. The other eight dossiers remain authored candidates. All eighteen traits remain inactive until their behavior is implemented and tested.
- Authoritative directional protection, movement momentum and charge, stationary healing groves, intercepted backline strikes, crossing beam lanes, facing-dependent tides and bounded pushes. Release/interruption ordering, occupied destinations, mirrors, relic geometry and repeated replay have focused tests.
- Native independent shops, five cost tiers, ten bench slots, deployment growth from three to ten, economy transactions, three-copy merges, eight-seat tournaments, actual off-screen combat, bots, neutrals, elimination and restart. The seven new neutral identities and twelve provisional waves use basic combat; teaching and boss signatures are unfinished.
- Twelve executable relic transforms, compatibility and equip commands, three-offer drafts after milestone rounds, ownership limits and deterministic sale/merge conservation. The lab equips fixtures directly; it has no acquisition interface.
- Version 3 preparation snapshots with exact content compatibility, corruption and semantic validation, deterministic resume and explicit offline/network boundaries. Persistent original human-seat and network identity prevent bot takeover from making an online match eligible for solo saves. Filesystem autosave and the packaged save/resume interface remain unfinished.
- Responsive native Slate laboratory UI and package launch tools. The successor shop, scouting, relic draft and full tournament frontend still need implementation. Starting `wonder_vnext` through the unfinished tournament frontend rejects explicitly.

## Exact candidate identity

| Item | Verified identity |
|---|---|
| Package | `builds/WonderChess-VNext-Lab-r3/Windows` — Development |
| Engine | Unreal 5.7.4-51494982 |
| Profile / balance | `wonder_vnext` / `wonder_vnext_lab_0.1.0` |
| Canonical source SHA-256 | `6f9a4178ec78d48c8f6fb8d487d88069327a5ca526652724dc12a8654f574ebb` |
| Runtime JSON SHA-256 | `2264f260087e5f40f08512f6066245b9058add7290f2f67d0e5c47a109aa797d` |
| Inner game executable SHA-256 | `55ff18047e8a21216ddcd8121f883da9b1d5f0a2bd2bd5081e8c7247170c6333` |
| Provenance manifest SHA-256 | `673138d984989a27971983d072aa67ff43bb0315176ffd6f60637bc89c3ee583` |
| Payload | 49 manifested files; 926,913,837 bytes |
| Git | `codex/wonder-vnext`, HEAD `9623fd82f98ff80a90985b9f552d8851ccece30f`; uncommitted checkpoint in an already dirty workspace |

The [provenance manifest](package/r3/provenance.json) identifies package, source, staged data and build inputs. All **47** pre-build source/configuration/runtime inputs remained unchanged through final verification: [source verification](package/r3/source-verification.json). Older successor candidates and the existing `WonderChess-Update24-Checkpoint-r4` package are preserved.

## Executed verification

| Check | Result and boundary |
|---|---|
| Python suite | **194 tests passed**, including strict catalogue and adversarial result-analysis checks. [Log](python-tests-final-194.log) |
| Authoring parity | **400 kit checks**, 28 generated documents, six legacy catalogue artifacts and seven successor artifacts passed. [Record](authoring-validation-final.json) |
| Focused native combat | **21,597 assertions passed**; synthetic combat/relic/geometry/replay fixtures. [Log](native-combat-final/tests.log) |
| Final native tournaments | **1,000 seeded tournaments**, seeds 1–1000 in four non-overlapping batches with identical compiled source hashes; technical reconciliation passed. [Analysis](native/final-analysis.json) |
| Final packaged tournaments | **100 tournaments**, 4,317 rounds and 18,777 encounters matched native results, state/event hashes and phase clocks; actual inner process exited 0. [Reconciliation](engine-tournaments/r3/reconciliation.json), [process](engine-tournaments/r3/process-exit.json) |
| Packaged laboratory | **39 boolean checks passed at each of 1280×720, 1600×1000 and 1920×1080**, five completed captures per size. All 64 cell centers visible and projection round trips valid. [Review](engine-lab/r3-visual-review.json) |
| Exact lab replay | Default seed 314159: A won at tick 434 with 238 events; repeated signature `486bfbd4785d7b281700d390a12a9e1360a23191`; no timeout. |
| Legacy regression | **100 `alpha_24` native tournaments passed**, 3,379,152 assertions. This preserves the tested legacy behavior, not a new legacy art/release approval. [Log](native/legacy-final/runtime-tests.log) |

The packaged tournament run is accelerated headless bot execution. The laboratory exercise calls the actual native handlers and checks projected geometry; it is not an external player's mouse/keyboard session. Selected final captures were actually viewed, including full Health/Armor text after creature selection changes. Continuous animation, listening review and full-match CPU/GPU/frame-time acceptance were not performed. The earlier three-test Unreal Data automation result is retained separately and is not substituted for these final candidate checks.

## Gameplay findings: acceptance remains open

The native batch produced **187,141 encounters, 26,434 timeouts (14.125%) and 199 round-capped tournaments**. The proposed timeout threshold is below 2%, so this gate **fails** for the current laboratory balance. A process finishing correctly is not evidence that the game has satisfactory pacing.

Median simulated tournament duration was **31.332 minutes**. Bots ready early; median preparation was only 2.911 minutes, combat 24.946 and settlement 3.5. These phase medians need not sum to the median total. This does not establish the intended 35–45-minute human experience.

The [timeout investigation](TIMEOUT_FINDINGS.md) found active healing and damage late in long fights, rather than a general frozen-combat failure. In seed 1, all 22 inspected timeouts retained Grandmother Root. Of 54 Cragstoats in those fights, 36 never charged, often because they began adjacent to opponents. These are associations with composition and placement confounders. No global tuning change has been adopted from that probe.

Remaining presentation defects include unfinished creature forms, materials, motion, effects and audio, possible label/telegraph overlaps and rendering trails requiring continuous-motion review. The lab is useful for controlled interaction experiments; it is not the finished visual slice.

## Art direction and human gates

The owner's **“Use this direction”** reply is recorded against the shared Bellback / Prism Organ / Thimblewake / Wondergrove concept direction. It does not approve modeling references, modeled forms or release.

Bellback's [detailed reference packet](../../art-source/asset-studio/wc_vn_bellback/inputs/references/r004_construction/README.md) contains the aesthetic target, reconciled four-toe and internal-bell details, calibrated body views, mount sections and proposed gait/contact geometry. Root accepted technical intake and sealed **27 reference artifacts**, snapshot SHA-256 `83de2292eeb1195963b1d479e194be171a87dd3c5eb960d47de870250fb2f842`. The separate formal human reference question is pending. No complex modeling or human forms acceptance has occurred.

Prism Organ's first generated reference has six documented construction inconsistencies and remains **ART_REVISE**. Its next step is reference reconciliation. Thimblewake and Wondergrove still require their detailed production work. No Blender production queue was started for these successor assets.

Bellback's approved direction places the bell dorsally; the frozen catalogue retains earlier chest-bell prose. Reconcile that presentation wording in the next deliberate content revision and regenerate/re-identify the candidate. It is not a runtime mechanic change, but it prevents declaring the design contract fully reconciled today.

AS1 requires: “Pram approves that this is the intended character before complex modeling begins.” [Reference manual](../../production/asset-studio/docs/01_CONCEPT_AND_REFERENCES.md). Independent gameplay work remains authorized while that specific art gate is pending.

## Milestone state and exact next work

| Milestone | Current state |
|---|---|
| M0 | Substantial contract/catalogue/tooling delivered; Bellback presentation wording reconciliation remains. |
| M1 | Six executed mechanics and packaged formation/replay lab delivered; recruitment/scouting flow and five external-player acceptance remain. |
| M2 | Direction selected and reference work underway; finished pilots/arena/UI/audio/normal-speed study and performance remain. |
| M3 | Core economy, relics, bots and snapshot foundations tested; full frontend, interruption lifecycle and measured pacing remain. |
| M4–M7 | Full-roster production, solo beta, remote online beta and release acceptance remain open. |

1. Run the controlled sustain experiment defined in `TIMEOUT_FINDINGS.md`: separate candidate at 75% Grove pulse magnitude, unchanged timing/geometry, same seed set and mirrored equal-investment fixtures. Independently compare Cragstoat approach-lane placement. Retain the current candidate as the comparison.
2. Implement successor recruitment, relic acquisition and scouting screens using the authoritative commands, then perform the five-player M1 tasks. Record exposure and purchase opportunity before inferring hero weakness from usage.
3. Reconcile Bellback's presentation prose at the next content revision. If the owner approves the sealed reference packet, record that exact decision against its snapshot and proceed through the serial Blender blockout/forms queue. Forms still require their own human decision.
4. Complete and measure the three art pilots and Wondergrove visual slice before estimating full-roster production effort. Add later mechanics/traits in bounded batches with actual runtime evidence.

No external-player studies, comparative Auto Chess study, clean-machine installation, remote hardware tests, successor dedicated-server/EOS setup, public deployment or release acceptance is claimed. No paid service or asset purchase was used. The authoritative machine-readable checkpoint is [implementation_checkpoint.json](implementation_checkpoint.json); the shared [implementation ledger](../implementation_state.json) retains prior baseline records.

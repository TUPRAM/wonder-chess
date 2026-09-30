# Current state and workstation audit

Audit dated **30 September 2026, Asia/Shanghai**; consolidated observation window began at 16:13. This report is research and planning. It creates report artifacts only. Existing code, binaries, acceptance ledgers, jobs and launchers were preserved; no game test, provider call, editor operation, installation or account-entitlement check was run for this audit. The accompanying [current-state.json](current-state.json) records observations, source identities, per-file timestamps and limits. Other development activity changed a live build input during inspection, so this is a dated read-only snapshot rather than an atomic project freeze.

Wonder Chess has a real seven-creature Unreal development candidate, substantial authoritative simulation and preparation/lifecycle engineering, several increasingly useful creature-production probes, and one narrowly owner-accepted Bellback delivery. The outstanding problem is completing and qualifying coherent player and production journeys. Neither the historical six-creature laboratory, the current seven-creature package, nor the number of skills establishes a complete game or professional studio capability.

## Authority and evidence interpretation

The active checkout is `C:/Users/USER/Documents/Wonder Chess`, branch `codex/milestones-b0-m7-20260912`. The former external worktree is retired. Ignored `builds/` and `support/` contain preserved project material and must travel with a workstation transfer; a GitHub clone alone is incomplete. [README](../../README.md), [transfer guide](../../TRANSFER_TO_NEW_PC.md), and [retained pause history](../../PAUSED.md) establish this boundary.

The intended successor is `wonder_vnext`: eight Windows seats, preparation decisions, authoritative automatic combat, mythic-storybook identity, independent shops, ten deployment/bench capacity, five costs, and a **35–45-minute full tournament target requiring measurement**. The successor has **no fixed final hero count**. The historical `alpha_24` rules and Ada/AQ1 art evidence remain their own baseline. The [successor contract](../vnext/README.md) governs product intent; [canonical data](../../data/vnext/catalog.json) and its [compiler](../../tools/vnext/catalog.py) govern current executable tuning.

| Evidence state | Meaning in this audit | Example |
|---|---|---|
| Authored | A design, contract, recipe or test exists | Seven disabled successor dossiers; Root r010 recovery recipes |
| Implemented | Actual code or editor assets express behavior | Cocoon lifecycle in `WonderSimulation.cpp`; guide/focus handling in `WCVNextSolo.cpp` |
| Executed | A named process and its measured results are preserved | Development r3 package exercises; Root r008 failed contact study |
| Imported / packaged | The exact import/build has a receipt and identity | Root/Snapvine static imports; Development r3 executable |
| Visually / audibly reviewed | Recorded viewing/listening of actual output, with scope | Root r008 operator image witness; Bellback final review |
| Owner-accepted | Pram's actual decision is bound to exact candidate and scope | Bellback r4 appearance/motion/sound; Root/Snapvine exact input approval |

These states are separate. The audit read existing review records; it did not independently re-view every image, continuous clip or audio file. A saved picture path or zero process exit is never counted as visual or technical acceptance.

## Current content, code and package

Direct catalogue inspection finds **14 authored heroes, seven enabled heroes, 18 inactive trait designs, 12 runtime-enabled relics, seven neutral identities and 12 authored waves**. `roster_cap` is null. The seven executed mechanics are directional guard (Bellback), momentum charge (Cragstoat), stationary grove (Grandmother Root), screened strike (Snapvine), crossing beams (Prism Organ), tide/push (Reefglass), and damage-free cocoon projectile (Silkmother). The other seven heroes remain authored/disabled. Neutral special teaching/boss abilities remain unfinished. These counts describe a development snapshot, not the eventual roster.

Read code at [simulation](../../game/Source/WonderChessRuntime/Private/Simulation/WonderSimulation.cpp), [tournament](../../game/Source/WonderChessRuntime/Private/Simulation/WonderTournament.cpp), [save filesystem](../../game/Source/WonderChessRuntime/Private/Simulation/WonderSaveFile.cpp), [solo frontend](../../game/Source/WonderChessRuntime/Private/WCVNextSolo.cpp), [Silkmother presentation](../../game/Source/WonderChessRuntime/Private/WCSilkmotherPresentation.cpp), and [editor helpers](../../game/Source/WonderChessArtTools/Private/WCAssetAuthoringLibrary.cpp). Existing [native combat fixtures](../../tests/runtime/vnext_combat_tests.cpp) and [authority fixtures](../../tests/runtime/vnext_online_contract_tests.cpp) demonstrate concrete verification surfaces; their presence alone does not prove every current edit was executed.

| Identity / result | Actual observation and limit |
|---|---|
| Canonical balance | `wonder_vnext_silkmother_0.2.0`; source SHA-256 `281a1323b6ea104fb4f9bd49f9a3e8468701c741f3544ecee05a81fb84c987ef`, rehashed during this audit |
| Preserved current joined build | `builds/WonderChess-Development-20260930-r3/Windows/WonderChess/Binaries/Win64/WonderChess.exe`; rehashed SHA-256 `64837d56863b640bb3f3744db3cdc4c6eab888d78871ae659b856bf96b89972e` |
| Recorded package evidence | UE 5.8.2; 134 source/50 payload identity at capture; package handler 35/35 booleans; native visual captures at 720, 1000 and 1080 sizes, each 21 true booleans and nine captures |
| Physical input | Scoped r2 1280×720 operator run: 11 true checks; this is not r3 physical-input coverage or an unfamiliar-player study |
| Recorded local tests | 250 Python tests; 400 authoring checks; 28 document, six legacy and six successor generated artifacts; 61 native save checks; 248 native authority checks; 27,781 focused combat assertions |
| Effective Storybook recipe | `wonder_vnext_silkmother_0.2.0+mana100_hit20_v1+combat_clarity_v1`, digest `e05b61d4c0da438aaffc4f308076930a60e96549de2e8c717100d6ff628d4525`; distinct from the native pacing baseline |
| Live source/build-input drift | Eight of the 134 r3 recorded inputs differ at the final identity read: seven source/configuration files plus the live `game/Binaries` executable. The preserved r3 executable still matches. Later revisions require their own build/evidence and cannot inherit r3 execution results |

Sources: [30 September execution report](../../reports/development-20260930/README.md), [r3 identity](../../reports/development-20260930/package-r003/identity.json), [UX verification](../../reports/development-20260930/ux/execution-verification.json), and [prospective recipe identity](../../reports/development-20260930/study/candidate-proposal.json). Live drift affects `game/Binaries/Win64/WonderChess.exe`, `DefaultGame.ini`, `WCAssetAuthoringLibrary.cpp/.h`, `WCSilkmotherExercise.cpp`, `WCSilkmotherPresentation.cpp/.h`, and `WCVNextLab.h`; the JSON lists exact paths. Hash comparison is an audit of identity, not a fresh full package validation or bit-reproducible build.

### Gameplay and unfinished player journeys

Independent shops, copies/merges, economy/XP, formation/facing, scouting, relic drafting/equip conservation, actual off-screen fights, tournament elimination/results/restart, versioned preparation saves and cold-process recovery have substantial executed engineering. The latest guide offers five pages, English/Indonesian, 100/125/150/200% guide text and a session creature-sound toggle. **Language and scaling apply to the guide, settings are session-only, and the sound toggle is not independently mixed volume buses.**

The exact current baseline pacing sample has 350/4,746 timeouts (7.375%), 15/25 round-capped tournaments, PvP 12.379% and ghost 16.402% timeouts. The isolated allied-cocoon-reservation candidate reduces overall timeouts to 333/4,737 (7.030%) but retains 15 caps and fails the below-2% screens. It is **REVISE, unpromoted**. The 96 single-caster fixture rows remain byte-identical; nine protected skill-on timeouts persist. Neither bot median (30.9125 baseline, 30.7583 candidate minutes) measures the human target. Silkmother has zero compatible relics, a current ecosystem gap. [Exact comparison and retained failures](../../reports/development-20260930/gameplay/reservation-r002/README.md).

The minimum unfinished acceptance journey is: unfamiliar player → new/load choice → recruitment/merge/full bench → deployment/facing/relic/scouting → normal-speed combat → factual recap → independent adaptation after loss → elimination/spectating or final winner → results/restart → exit/cold resume. Physical pointer/keyboard coverage is still required at 1280×720, 1600×1000 and 1920×1080, including modal expiry/focus and command rejection. Full HUD scaling/localization, remapping, reduced motion/effects, persistent settings, learning sandbox/bestiary and history remain incomplete. The [WC-P004 kit](../../reports/development-20260930/study/README.md) is prospective: empty forms and qualified templates establish no participant outcomes.

M6 native 2H6B/4H4B/8H0B authority fixtures do not establish successor remote transport, authenticated sessions/reclaim, dedicated server operations, independent devices or human whole matches. M7 clean-machine, final-content crowded performance, appropriate human/art approvals and owner release acceptance remain open. Historical same-machine clean-checkout builds cannot close current-candidate clean-machine requirements. [Milestone gates](../vnext/milestones/MILESTONE_STATUS.md).

## Creature production: actual stage reached

The owner-selected route is **Meshy → Unreal**. Preserve accepted maps/palette and use shared soft lighting; no Blender dependency is imposed on this route. New geometry uses Main/front, anatomical Left, Back, anatomical Right. Krita remains the chosen precise assembly tool. One combined G3/G4 forms/color/rig owner review retains separate construction, topology, UV/material and deformation evidence. Animation-ready is distinct from complete motion, engine integration, asset acceptance and game release. [Handbook](../../production/creature-pipeline/README.md), [animation-ready contract](../../production/creature-pipeline/ANIMATION_READY.md).

| Creature / exact candidate | Authored / implemented / executed now | Review / acceptance still required |
|---|---|---|
| Bellback `Bellback_r001`, package r4 | Preserved modeled/PBR/rigged, motion/audio/package delivery | Exact 20 September owner reply accepts appearance, motion and sound for that six-point task; game/G1 changes are separate. Existing diagnostic inspection hash discrepancy needs preservation/reconciliation |
| Cragstoat `production_r002` → SageTail r003 / validator r004 | Separate owner-requested pastel and full-tail revision. Latest cold LOD0 report: 601 poses, 157 captures, zero failures; original geometry/map pixels preserved | New material/motion decision, continuous natural movement, complete combat/locomotion, LODs, board fit, package/performance remain open |
| Grandmother Root `production_20260930_r001`, r008/r009 | Exact four-view inputs approved; source generation/download/PBR/static import executed. r008: 23-bone rest correction passes, 231 contact failures remain. r009: 112 sole weights corrected, 19,288 untouched, full LOD0 numeric readback passes; copied rig fails and is not saved | r010 rig-only recovery is authored/NOT_RUN at snapshot; cold contact and difficult poses, garden articulation, motion/LOD/package and combined owner review remain open |
| Snapvine `production_20260930_r001` | Exact four-view inputs approved; source generation/download/PBR/static import executed. Cold partial study: 601 poses, 160 captures, zero failures, anchored-base centroid slide zero | Probe covers fused base and small body/jaw/hook FK only. Independent-root locomotion, full extension, clipping, animation readiness, LODs/performance/package and owner review remain open |
| Silkmother `Silkmother_r003` / isolated motion r003 | Existing solo/arena source, nine clips, PBR and opt-in integration. Latest isolated cold revision: 1,803 poses (601 × three LODs), zero failures, 60Hz sampling proof | Status explicitly says visual/runtime review pending. Actual runtime crossfade/recoil/event path, natural whole-body motion, board/mix review, package and exact appearance/motion/effects/sound acceptance remain open |
| Prism Organ | Current construction studies and canonical executed mechanic | Hollow resonator/key clearance and coherent exact G2 set require resolution before paid generation; no accepted production geometry/rig |
| Reefglass `four_view_r003` | Executed SVG/PNG construction diagrams and supplemental material images | Exact G2 approval, occluded underside/roots/fin joins, layered Krita source/profile and transparent-shell/readability decisions remain open; no production Meshy source/rig/import |

Sources: [full batch](../../art-source/asset-studio/production-batch-20260930/README.md), [Bellback decision](../../reports/bellback-production-20260920/owner-acceptance.json), [Cragstoat latest cold report](../../reports/development-20260930/cragstoat-revision/sage-keymotion_r004/validation_r001/validation.json), [Root r009 failure audit](../../reports/development-20260930/root-recovery/r009-author-audit.json), [Root r010 proposal](../../reports/development-20260930/root-recovery/r010-ready.json), [Snapvine cold report](../../reports/development-20260930/assets/generated-inspection/wc_vn_snapvine/unreal-rig-r001/cold-validation-r001/validation.json), [Silkmother all-LOD report](../../reports/development-20260930/silkmother-revision/cold-validation-r003/validation.json), and [Reefglass handoff](../../art-source/asset-studio/wc_vn_reefglass/stages/production_r003/handoff.md).

Root/Snapvine paid production history records **two successful 30-credit jobs, 60 credits total**, observed provider balance 3,088→3,028, no separate remesh/rig charge. Their downloaded sources have zero source skins/animations; local Unreal rig work is distinct. These are historical receipts, not this audit's live account allowance. [Cost reconciliation](../../reports/development-20260930/meshy-preflight/credit-reconciliation.json), [exact owner input/spend record](../../reports/development-20260930/meshy-preflight/owner-authorization.json). Preserve existing authorized decisions; this planning request initiates no new paid operation.

### Three concrete qualification pilots

These are proposed capability-qualification subjects, using existing unfinished work. They do **not** replace the original M2 Bellback/Prism Organ/Thimblewake gate identities.

1. **Grandmother Root recovery:** reused r009 mesh → isolated executable r010 rig/rest gate → fresh sequence/contact study → actual volume/extreme review → combined G3/G4 decision. This tests failure recovery, per-vertex preservation and saving/reopening a copied Control Rig. Stop on unusable geometry/graph or unresolved major deformation; do not lift the floor or weaken tolerance.
2. **Cragstoat revision delivery:** preserve SageTail r003 bytes → review full-tail motion/material → complete charge/move/attack/turn/hit/defeat and event anchors → LOD/board/package → cold restoration and exact owner decision. This tests selective invalidation and complete quadruped delivery without regeneration.
3. **Silkmother runtime motion delivery:** preserve passing isolated three-LOD study → view continuous/key poses → qualify opt-in runtime recoil/crossfade under authoritative damage events → package/normal-speed busy-board/mix/performance → exact owner decision. This tests many-limb contacts, compression/sampling, interruption and transition coverage.

Snapvine is a useful subsequent anatomy proof. Formal M2 still requires Prism Organ and Thimblewake or an explicit owner scope amendment; an asset-only Thimblewake rig is not proof of an executed duel mechanic or normal recruitment.

## Actual workstation and integration surfaces

Read-only probes used CIM, `Get-Volume`, `nvidia-smi`, version commands and executable metadata. They did not install or launch editors, access credentials, change permissions, or inspect private account files.

| Resource | Observed now | Planning consequence |
|---|---|---|
| CPU / RAM | Intel Core Ultra 7 265K, 20 cores/20 logical processors; 32GiB physical (31.71GiB available to Windows); 2 × 16GiB DDR5 configured 5600 | One editor/binary writer and bounded jobs. No assumed 64GiB upgrade |
| GPU | NVIDIA RTX 5060; `nvidia-smi` reports 8,151MiB, driver 616.92 | Budget for 8GB, measure texture/mesh/overdraw residency. CIM AdapterRAM truncates near 4GB and is not the VRAM authority |
| Storage | Lexar NM790 1TB, NTFS C:, usable 952.79GiB, 458.10GiB free at probe | Enough headroom for bounded initial work is an inference, not future build capacity or backup proof; retain builds/support and measure growth |
| OS | Windows 11 Pro 10.0.26200/build 26200 | Current dev hardware only; minimum supported hardware is unmeasured |
| Unreal | Build.version 5.8.2 / changelist 56702186; project association 5.8 | Use installed APIs; binding, implicit compile and compressed key behavior have caused real failures |
| Build/Python | VS Build Tools 17.14.37710.0; SDK 10.0.22621.0; project Python 3.12.14; bare Python 3.11.9 | Wrappers should resolve project environment explicitly; earlier bare-Python `jsonschema` failures are preserved |
| Supporting tools | Git 2.55.0; LFS 3.7.1; Node 24.19.0; Blender 5.2.1 LTS; Krita 5.3.4; Audacity 4.0.0; OBS 32.2.2; MeshLab Store 2025.7.0.0 | Installation is separate from integration/qualification. Blender stays available for legacy/non-creature routes |
| Adobe presence | Photoshop 2026 v27.10, Audition 2026 v26.5.0, Lightroom v9.6, Creative Cloud desktop v6.10.0.253 executables | Account entitlement, first-run readiness and scripting interoperability UNVERIFIED; no silent substitution for Krita |

| Tool / route | Evidence available | Unsupported inference / requalification needed |
|---|---|---|
| Meshy official MCP/helper + website | Preserved setup and paid-job receipts; local explicit helpers and no-POST-retry fixture | No Meshy tool is loaded into this audit's direct tool inventory. Helper presence/old balance does not prove current session/authentication/allowance. API humanoid rigging and website quadruped/Smart Rig are separate dated capabilities; unusual roots/vines/assemblies need anatomy qualification. See current official-source research in the companion report |
| Unreal Python/editor C++ | Editor-scoped module/plugins, source, real saved anatomy candidates and cold studies | Not arbitrary universal editor access. Check actual API names (`get_all_triangle_i_ds` failed under assumed spelling), executable VM/rest state, saved binary and native sampling per version |
| Krita | Native Scripter, `.kra`/PNG interchange, exact-pixel fixture and Cragstoat assembly evidence | Previous security-dialog interruptions and missing layered sources remain explicit; headless export is unqualified |
| Audacity / OBS / MeshLab | Recorded native WAV/session, Lua image recording, OBJ fixture round trips | No inferred Audacity MCP/script pipe or rigged MeshLab round trip; OBS fixture is not busy gameplay/audio/performance evidence |
| Insights | CPU trace timer export executed | Memory analyzer errors remain; no qualifying GPU/memory/final-content performance result |
| LFS / recovery | Local hydrated object restore fixture | Remote quotas/uploads and full-project independent restore are separate; ignored support/builds require explicit backup |
| Codex / Adobe / cloud providers | Tools/application presence only for this audit | Usage limits, plan rights and future service costs UNVERIFIED; no assumed render farm, API freedom or cloud budget |

Supporting scope and test receipts: [toolchain record](../LOCAL_TOOLCHAIN.md), [21 September qualification](../../reports/pipeline-tools-20260921/README.md), [qualified command matrix](../../production/creature-pipeline/TOOLCHAIN.md), [actual Root/Snap rig-route audit](../../reports/development-20260930/rig-tool-qualification/README.md), [old constrained Meshy helper](../../support/tools/meshy/call_meshy.py). That old helper deliberately only permits Meshy-7 single-image untextured generation for its historical 20-credit scope; it is not a valid default adapter for the latest colored four-view contract.

## Conflicts and scoped resolution

| Conflicting records / dates | Scope and actual resolution |
|---|---|
| `GPT_PRO_REVIEW.md` (12 Sep), implementation handoff/matrix (11 Sep), milestone status (13 Sep) vs 30 Sep package/catalogue | Historical six-hero counts, missing frontend/save and pending Bellback decisions are superseded only for delivered later components. Keep original pacing/human/art/remote/release gates and historical results |
| `PAUSED.md` historic external paths vs consolidation 15 Sep and transfer/toolchain 17 Sep | Development was explicitly resumed; root is canonical. Keep old paths as provenance, never resume retired checkout |
| Legacy AS1 source/queue/forms rules vs creature handbook v1.3/owner amendment 21 Sep | Meshy raw source plus editable Unreal recipes/assets replace `.blend` authority for selected creatures; combined G3/G4 review applies. Ownership, immutable evidence, failure/change-method and human authority remain |
| 30 Sep plan says Root/Snap have no approved inputs/production source vs later exact approval/jobs | Approved Root r003/Snapvine r004 input hashes and 60-credit successful jobs govern those specific sources. Do not re-request unchanged approvals or regenerate; hidden anatomy/new output acceptance remains separate |
| Root recovery earlier r009 NOT_RUN vs later r009 author audit/r010 proposal | r009 numeric mesh succeeded but stage failed on copied rig; r010 is authored/NOT_RUN. Process exit zero does not erase the gate failure; current recipe differs from actually executed r009 recipe |
| Cragstoat/Silkmother summaries still describe prior failure/pending rebake vs latest same-day validators | Latest raw reports establish their stated contact-study passes, with human/runtime/game gates still open. Do not carry a stale failure forward, or inflate a scoped pass into acceptance |
| Bellback prior tint/emissive recipe vs preserved-color soft-light standard | Retain accepted Bellback baseline; new creatures preserve maps. Owner-requested Cragstoat pastel is a isolated explicit exception, not collection-wide repaint approval |
| Old bottom-shop screen contract vs current r29/Development modal shop | Current owner-directed modal five-offer shop/round portraits/circular bench is implementation baseline; responsive physical journeys and coherent screen acceptance remain required |
| Plan's 140-credit proposal/handbook budget vs later owner spend relay | Preserve later scoped authorization and actual receipts; planning scope runs no new job. No account subscription is treated as unlimited allowance or unseen-anatomy approval |
| Bellback approval manifest vs live hashes | Audit finds 38/41 matching files: diagnostic rig-inspection sequence and subsequently changed shared Lab `.cpp/.h` differ. Preserve original package/art and recorded decision; reconcile the diagnostic discrepancy and do not transfer its exact shared-code evidence to current code |
| Shared ledger top-level timestamps/old fields vs later nested records and raw reports | Ledger retains 13 Sep top-level timestamps and historical alpha/Ada fields while nested later records exist. Read dated candidate records by concern; propose an explicit current pointer/status projection rather than overwriting history or inventing acceptance |
| M2 original Bellback/Prism/Thimblewake pilots vs convenient Crag/Silk/Root qualification | Proposed pilots qualify tooling; they do not substitute formal M2 deliverables without owner amendment |

## What is and is not established

This audit establishes actual local hardware/version observations, canonical counts and identity, preserved executable identity, source drift, concrete code/fixture presence, and correctly scoped existing execution/approval records. It does not establish current remote repository completeness, live Meshy balance or licenses, Adobe/Codex plan entitlement, editor connectivity today, whole-project restoration, every visual/listening judgment, unknown latest parallel editor changes, human enjoyment or release readiness. Sources that changed during this read-only audit are treated as dated snapshots; the JSON freezes the inspected record hashes.

The next capability investment should complete the existing journeys and recovery/promotion evidence. Increasing creature count, board variants or mechanic complexity requires a measured tactical/acquisition gap, accepted production method, understandable counterplay and available performance budget. Documentation maturity and actual production capability must stay separately labeled.

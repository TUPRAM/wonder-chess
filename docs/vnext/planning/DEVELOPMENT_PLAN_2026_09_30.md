# Wonder Chess development plans and goals

Prepared 30 September 2026, Asia/Shanghai. **Status: authored planning revision; implementation and acceptance remain separately evidenced.**

The goal is an eight-seat Windows Unreal auto-battler where players recognize extraordinary creatures, understand the consequences of a formation, obtain a practical alternative, and want to try again. Preparation holds the decisions; authoritative C++ resolves automatic combat. The mythic-storybook world begins with one excellent Wondergrove board.

This plan organizes the adopted B0–M7 programme into three deliveries and ten workstream goals. Existing product requirements remain in force. New task priorities, batch sizes and completion checklists below are planning proposals, not new approvals, measured results or production-date promises. The companion [prioritized backlog](DEVELOPMENT_BACKLOG_2026_09_30.csv) makes the work assignable.

## 1. Start from the actual current project

| Area | Current evidence | Planning consequence |
|---|---|---|
| Product | `wonder_vnext`; canonical balance `wonder_vnext_silkmother_0.2.0`; 14 authored heroes, seven enabled | Preserve the seven-creature candidate and separate historical six-creature experiment controls. No fixed final roster count. |
| Playable content | Bellback, Cragstoat, Grandmother Root, Snapvine, Prism Organ, Reefglass, Silkmother; 12 runtime relics; seven neutral definitions / 12 authored waves | Prove comprehension, acquisition and pacing before adding broad content. Neutral teaching and boss behavior remain unfinished. |
| Traits | All 18 race/class designs have runtime activation disabled | Show accurate identities; do not imply an executed synergy bonus. Activate only bounded, tested behavior. |
| Presentation | Visual r29 packages an enlarged 8×8 board, five-offer modal shop, ten circular bench sockets and compact eight-seat standings | Improve and review this interface. The older bottom-shop layout is not the current presentation baseline. |
| Input evidence | r29 packaged exercises at 1280×720 and 1920×1080 include board click projection and accelerated match completion | Full physical pointer/keyboard, normal-speed lifecycle and accessibility journeys remain open. |
| Bellback | Exact Bellback_r001 / r4 appearance, motion and sound have recorded owner acceptance | Reuse the accepted candidate and preserve its scope. A new shared-look revision needs its own affected review. |
| Cragstoat | production_r002 is colored, textured and technically animation-ready; exact forms/color/rig review remains open | Resume that candidate rather than resubmitting geometry. Combat motion, audio/effects and full game validation remain. |
| Silkmother | Packaged solo/arena candidate exists; exact owner appearance/motion/effects/sound acceptance remains open | Review and correct the current delivery; do not infer acceptance from its preview flag in r29. |
| Other active creatures | Root, Snapvine, Prism Organ and Reefglass have current reference/construction candidates, without exact new G2 approval or production geometry | Resolve the precise reference defect/decision before charged generation. |
| Balance and studies | Historical pacing screens fail; current-candidate human pacing, comprehension and repeat-use gates are open | Re-measure the identified current candidate. Earlier six-creature results do not certify the seventh mechanic. |
| Technology | Consolidated repository; verified toolchain record uses Unreal 5.8.2; creature route is Meshy → Unreal | Work in this root, retain ignored builds/support, and qualify affected tools when execution resumes. |

Sources: [successor authority](../README.md), [current catalogue](../../../data/vnext/catalog.json), [generated coverage](../generated/coverage.json), [r29 readout](../../../reports/vnext/milestones/visual-20260924/README.md), [implementation ledger](../../../reports/implementation_state.json), [toolchain](../../LOCAL_TOOLCHAIN.md).

The September 13 [milestone tracker](../milestones/MILESTONE_STATUS.md) still supplies outstanding gates, but its latest-r20, six-active-hero and rejected-Bellback-forms statements describe earlier checkpoints. The later scoped Bellback acceptance does not erase those failed attempts. Old external checkout paths are historical; this repository root is the active location.

## 2. Three delivery plans

| Delivery | What the player receives | Main work | Exit condition |
|---|---|---|---|
| **Plan A — Reviewable gameplay and visual slice** | A reliable solo preparation → combat → recap → adaptation loop, readable creature cues, and a coherent Wondergrove screen | B1/B2 comprehension and pacing investigation; physical input; shared look; resume existing creature candidates; complete required M2 pilots | Scoped control journeys pass; the sampled player-comprehension and normal-speed pacing gates pass; exact art decisions are recorded for the accepted slice. Contributes to M1–M3; one creature does not close M2. |
| **Plan B — Complete solo beta** | A bounded, coherent roster with accessible strategies, learning tools, settings, recovery and reasons to replay | Earned M4 hero/trait/neutral batches; finish art for the frozen solo roster; onboarding, bestiary, sandbox, accessibility and expression progression | Eight required strategic families are demonstrated through normal acquisition and counterplay; accepted content/pacing/visual prerequisites; M5 repeated-day study with at least 12 external people; critical defects resolved. |
| **Plan C — Remote beta and release candidate** | Fair, recoverable multiplayer, a clean install, stable performance and clear support diagnostics | M6 dedicated-server/authenticated sessions and independent-device journeys; M7 final content freeze, package/hardware/study evidence and rollback | Actual 2H6B → 4H4B → 8H0B journeys pass; exact final package passes required regression, clean-machine and performance gates; required human/art/release decisions are recorded. Publication is a separate action. |

These are sequential deliveries. Network prerequisites, production tooling and environment work may progress independently while a balance or art decision is pending. M5 entry and M7 acceptance still require their actual dependencies.

Do not assign calendar release dates yet. Estimate remaining effort after timing one complete creature delivery, one UI journey correction batch and one gameplay experiment, including review/rework. Re-estimate after each accepted batch. A study requires actual available participants and devices before it can be scheduled.

## 3. Ten workstream plans and measurable goals

### G01 — Gameplay: understandable formation and accepted pacing

**Goal:** players can predict a formation relationship, explain its principal effect, and make a useful change after a loss.

First freeze the current candidate, flags, source/runtime identity and scenario rules. Retain the six-mechanic historical control; add a separately specified Silkmother scenario and regression coverage for trapping, expiry, interruption and repeat targeting. Observe useful/unfavorable and mirrored positions, blocked charge/push destinations, guard recipients, sustain reset, beam commitments and released packets after source defeat.

Investigate combat timeouts and tournament round caps separately. Record battle, preparation, settlement, pause and spectator time; first meaningful action/death; effective healing/overheal; charge opportunities/failures; control uptime; acquisition and bot composition drift. Choose at most one justified interaction change per comparison. Fixed rosters isolate combat; legal shops/full tournaments reveal acquisition effects. Avoid padding waits to manufacture duration.

**Existing gates:** B1 uses five external participants and independent unfamiliar-scenario explanation/revision; B0 operationalizes a four-of-five formative target. Its pacing screen requires timeout below 2% overall, PvP and ghost separately, with at least 100 encounters per assessed stratum. Report neutrals and caps without silently inventing a cap ceiling. Obtain five complete normal-speed tournament-to-final-winner observations; report the 35–45-minute target separately from player time to elimination and paused time. Five observations are formative evidence, not a population estimate.

**Dependencies:** identifiable candidate and prospectively fixed rubric. Human evidence informs further interaction selection. Retain unused confirmation seeds 900001–900250 until a justified confirmation run; verify they are still unused at execution. No historical timeout rate is assigned to r29 without a matching run.

### G02 — Ecosystem: earn roster, traits, relics and neutral encounters

**Goal:** normal recruitment makes distinct strategies and practical counters available without redundant heroes or hidden bot advantages.

Map the eight required families—protected carries, momentum rush, positional sustain, artillery, backline pressure, constructions, displacement and isolated duels—to executed behavior, normal shop access, useful and unfavorable formations, and an observable counter. An authored archetype label is insufficient. Start with current seven-hero acquisition/adaptation evidence; identify a specific gap before promoting another hero. Proposed work limit: one new mechanic at a time; a second closely related hero follows only after the first is understood.

Each hero promotion includes canonical stats/ability, meaningful star comparisons, compatible relic tradeoffs, bot use/counter behavior, view models, recap, saves, art and focused regression. Compile from `data/vnext/catalog.json` through `tools/vnext/catalog.py`; generated dossiers/widgets never become a second balance source. Preserve asymmetric races/classes and the five costs. Do not impose 14 or 24 as the final successor roster.

Begin trait work with a bounded Beast pair after acquisition evidence. Specify triggers, recipients, interruption, caps, expiry and movement response. Plant waits for accepted sustain and an explicit finite protection budget/reset rule. Compare trait off/on and include cases where completing the pair is a poor choice. Keep the other designs inactive until independently earned.

Retain the 12 current relics, deterministic private three-offer drafts, three-equipment team limit and one relic per hero. Validate incompatibility, selling, merge survivor/extras and repeated equip/inspection without cumulative transforms. Give the seven neutral identities and scheduled waves genuine screening/spreading/support-protection lessons and milestone boss behavior; test later transfer rather than claiming teaching from a basic-attack layout.

**Done:** each promoted feature has a defined decision, counter, legal acquisition path, complete executed contract and separately accepted presentation. Eight accessible families are a Plan B content goal. No recruited-type synergy from summons; enforce the four-per-side summon cap when that system is implemented.

### G03 — Creature assets: complete reusable, game-ready production

**Goal:** every hero in the frozen solo-beta roster has accepted appearance, readable continuous motion, sound/effects and measured packaged integration.

Use [the creature handbook](../../../production/creature-pipeline/README.md) and AS1 ownership/evidence rules. New geometry uses a reviewed four-view set: Main/front, anatomical Left, Back, anatomical Right. Preserve accepted Meshy color maps; use shared soft lighting. Creature rigging, animation and integration proceed in Unreal without Blender processing.

| Production batch | Next concrete delivery | Gate/dependency |
|---|---|---|
| Existing approvals/shared look | Preserve Bellback r4 and compare a separate copy under the proposed collection lighting | Record actual G1 shared-look decision. Do not apply Bellback's old tint/emissive recipe to new creatures. Reconcile the recorded rig-inspection hash mismatch without overwriting sources. |
| Cragstoat | Exact production_r002 forms/color/rig review, then full charge/attack/move/turn/hit/defeat clips, effects/audio and packaged board tests | Existing 30-credit generation and rig study remain preserved. No fresh generation is needed for this review. Resolve the small/dark on-board preview before default promotion. |
| Silkmother | Exact existing solo/arena review and focused fixes to gait, cocoon clarity, timing, audio and overlap | Preserve the owner's selected damage-free cocoon and no-voice sound direction. Art review cannot silently alter gameplay. |
| Root and Snapvine | Current exact construction/reference decisions, then combined colored/PBR/rigged candidates | Root: two supports. Snapvine: four ground roots and one anatomical-left hook. Direction approval does not equal G2 image-hash approval. |
| Prism Organ and Reefglass | Resolve construction/transparency issues before generation, then anatomy-specific rigs | Prism: five pipes, four keys, two perpendicular emitters; hollow central chamber decision open. Reefglass: six tentacles, two fins; hidden-root evidence and membrane readability need review. |
| Further roster | One method-proven body family and justified gameplay gap per batch | No automatic regeneration, roster expansion or inherited art acceptance. |

Per creature, deliver immutable raw source/maps, Unreal mesh/skeleton/weights/controls/sockets, editable recipes, required motion and transitions, portraits/ability icon, event-mapped effects/audio, LODs, selection bounds, cold reopen/reimport, mixed crowded-board evidence, executable/launcher and rollback. Test actual skinned poses, planted contacts, turning/displacement, slow/fast attacks, interrupted casts, defeat and blends. File counts, auto-rig success and a still image cannot establish motion quality.

**Budget:** the latest four-creature estimate is 140 Meshy credits maximum: four 30-credit colored generations and at most one 5-credit remesh per hero. It remains a proposal, with exact G2 review and charged-call authorization open. The existing Cragstoat candidate has its own historical cap and expenditure; neither authorizes another batch. Track provider credits, local authoring time and rework separately.

**Milestone caveat:** the original M2 pilots are Bellback, Prism Organ and Thimblewake. Cragstoat/Silkmother provide valuable method evidence but do not silently replace Thimblewake's required pilot. Record an owner-approved scope amendment before counting a substitution. Original closure requires executed signature-event alignment and real duel readability as well as the art pipeline. Generic animation fixtures prove family/motion only. A bounded executed prototype must satisfy those original requirements, or the owner must explicitly amend them; it does not automatically enable Thimblewake in normal recruitment.

### G04 — Environment and visual direction: one coherent Wondergrove

**Goal:** the board remains readable during a busy battle while its sanctuary setting and creature materials share a recognizable storybook identity.

Build one modular platform: readable 8×8 cells, bench integration, roots/stonework, perimeter foliage/props, camera and collision limits, lighting and ambience. Keep architectural detail, stronger contrast and incidental motion at the edges. Inspect large silhouettes, floating bodies, membrane/translucent surfaces and dense effects at the actual game camera before producing extra arenas.

Consolidate design tokens for type, spacing, surface values, team markers, icon grammar and panel states. Preserve the current modal-shop/circular-bench direction and accepted 2D work. Audit portraits, seven enabled ability identities, 12 relic illustrations, statuses, neutral/boss tells and frontend art against the active roster. Reuse the existing detailed 2D inventory rather than restart hundreds of assets.

**Done:** actual mixed/crowded gameplay views pass cell visibility, selection, team/status recognition and material consistency at required resolutions; reduced-effects/grayscale review preserves critical information; exact shared look and slice decisions are recorded. Local beauty renders alone do not satisfy this goal.

### G05 — UI/UX and accessibility: complete independent player journeys

**Goal:** a first-use player can complete preparation, learn from a battle, recover a save and reach results using physical controls.

Verify the current modal shop's open/close/reopen/focus flow, round-opening behavior and preparation expiry; ten-slot bench selection/return; full-bench purchases/merges; placement/swapping/facing; copy counts; XP/reroll/lock/ready; compatible relic draft/equip/unequip; scouting identity and persistent return; loss/elimination/spectating; results/restart; existing-save choice, pause/exit and cold resume. Rejections state the reason and preserve useful selection. Combat locks purchases and movement consistently.

Deliver launch/menu, new/load flow, onboarding, normal preparation/combat/recap, settings, bestiary/sandbox, results/history, plus later lobby/join/reconnect/mismatch/server-abort states. Recap leads with one or two event-grounded facts; claimed alternatives require an actual replay comparison. Context panels collapse or scroll before obstructing placement cells.

**Existing review matrix:** physical pointer and keyboard journeys at 1280×720, 1600×1000 and 1920×1080; keyboard focus/remapping/pointer alternatives; 125/150/200% text scale; English and Indonesian with real long strings; color-independent team/status information; reduced motion/effects retaining direction/range/timing; independent volume buses. Also inspect the actual chosen OS scaling settings and record them.

Baseline accessibility/localization, packaged audio review and measured complete-slice performance belong to Plan A's M2 acceptance. Plan B extends those checks to the expanded roster and new learning screens rather than deferring the initial obligations.

**Existing B2 formative gate:** four of five eligible first-use participants independently complete each of the nine registered preparation/lifecycle tasks, including adaptation after loss, the personal endpoint, restart and cold resume; four of five pass two of three unfamiliar principal-cause explanations. Include the study kit's separate group eliminated-player spectating observation. Record assistance, errors, task times and experience separately. Returning B1 users do not count as new first-use participants. Automated same-handler/click-projection checks support engineering, while human journeys establish usability.

### G06 — Animation, VFX and audio: communicate real combat

**Goal:** players recognize the source, target, commitment, release and result of important combat events in normal-speed mixed fights.

Use a shared grammar for basic strikes/projectiles, guard, effective healing, shield, stun/trap, charge, beam/line, push, establishment/reset, defeat and victory. Evaluate overlap among Bellback protection, Root sustain, Silkmother cocoon and other status indicators. Shapes, motion and timing carry meaning alongside color. Essential cues remain in reduced-effects mode.

Animation and sound follow authoritative events; they never create damage or introduce a second targeting/timing system. Validate event spawn/cancel/release, ownership, pooling, expiry, source defeat, off-screen visibility and target changes. Review continuous normal-speed motion first, then slow motion for defects.

Deliver original/right-cleared creature contacts/casts, UI feedback, ambient loops and music with separate mix controls. Respect Silkmother's accepted no-voice design. Check varied repeated sounds, clipping, masking, latency and competing casts in the packaged full mix. A free AI sound provider remains unqualified until actual rights/quality/tool evidence exists; use qualified local/source options rather than imply availability.

**Done:** required cues align with engine events, repeated/overlapping effects have bounded lifetimes, critical cues stay discernible, and exact candidate motion/appearance/listening reviews are recorded. Measure effect/audio cost with the final mixed content.

### G07 — Engineering and performance: reliable exact builds

**Goal:** the intended package preserves authority and recovery, executes identical viewed/off-screen battles and meets the supported hardware target.

Maintain deterministic streams, atomic command validation, private/public state boundaries and preparation-boundary saves. Test full-bench/relic transactions, duplicate/reordered requests, phase cutoff, corrupt/incompatible saves and interrupted writes. State clearly that combat interruption returns to the last valid preparation checkpoint; arbitrary mid-combat resume is not implemented. Audit bots through ordinary legal economy/commands and public information.

Qualify memory capture first: the pipeline evidence retains memory-analysis errors. Profile source and final package with CPU/GPU/frame distributions, memory/loading, hitch traces and leak checks across menus, transitions, twenty deployed units, permitted entities, busy effects and actual off-screen fights. Set per-asset material/texture/LOD/effect budgets from the working slice; label provisional limits and measured exceptions. Bellback-only r4 timings at 1600×1000 cannot certify mixed r29 or minimum specifications.

**Existing performance target:** 1080p/60 FPS; active-gameplay p95 ≤16.7 ms and p99 ≤25 ms, with no recurrent unexplained >100 ms stalls. Disclose loading/intentional pauses, named CPU/GPU/RAM/device/settings and actual content. Additional devices establish minimum specifications; the current development PC alone cannot do so.

Run appropriate source/compiler/native/transaction/tournament/package checks for affected changes. After final content freeze, M7 requires at least 1,000 native and 100 packaged full tournaments, exact source/runtime/package identity, independent clean-checkout and clean-machine journeys. Existing unchanged evidence remains scoped; repeat large batches only when promotion or invalidated evidence requires them.

### G08 — Learning and replay: complete the solo beta experience

**Goal:** players learn a new strategy, adapt after losses and choose to return without earning permanent competitive power.

Start with contextual onboarding, a controlled sandbox, accurate bestiary models/geometry/counters/star comparisons, factual match history and saved formation sketches. Add discoveries, mastery, achievements and offline challenge seeds only when they answer observed learning/replay needs. Rewards unlock expression and learning. Preserve preparation-only match decisions and offline operation without a runtime LLM.

**Existing M5 gate:** at least 12 external participants across separate days after accepted content/visual/pacing entry gates. Record independent versus assisted learning, build changes, losses, fatigue, session lengths, early exits and optional replay choice. Keep repeat-use evidence separate from first-impression liking. No retention percentage or monetization system is adopted by this plan.

### G09 — Multiplayer: fair remote whole matches

**Goal:** independent human devices complete matches with authenticated seat ownership, private shops/benches/drafts and explicit recovery/failure outcomes.

Qualify the source-engine dedicated-server path and actual authenticated service prerequisites for the intended OSS EOS architecture. Deliver private rooms and unranked play, disclosed bot filling, join/content mismatch states, ready/scouting cutoff, reconnect/reclaim, bot takeover/yield and an explicit aborted-match result for server failure. Ranked play follows operational reliability and human balance evidence.

**Existing progression:** local multiprocess diagnostics → actual remote 2H6B → 4H4B → 8H0B. Use independent devices and human operators; test latency/jitter/loss, duplicate reclaim, disconnects, interrupted matches and server crashes. Local authority fixtures are prerequisite evidence rather than remote acceptance. New paid/public service work requires its applicable authorization when a concrete deployment is ready.

### G10 — Production, QA and release: reviewable progress and supported delivery

**Goal:** every milestone ends in an identifiable artifact, an honest decision, defects and a precise next action; the eventual release is reproducible to inspect and recover.

Assign one integration owner for canonical data/schema/generated files, one writer per asset binary/rig/material family, and an independent reviewer where practical. Parallelize immutable reads, separate art candidates, study preparation and isolated UI/gameplay tasks. Do not concurrently edit shared `.uasset`, `.umap`, skeletons or manifests. Keep durable tools, backups and recovery under `support/`.

Track authored → executed → imported → visually/listening reviewed → packaged → externally tested → accepted as separate states. Maintain exact candidate/source hashes, tool versions, commands, flags, seeds, captures, rights records and failed outputs. A hash establishes identity; it does not prove visual quality. After two ineffective critical art corrections, change the method or stop only that affected stage.

For M7, freeze content/protocol and intended solo/online scope; preserve rollback and saves/support diagnostics; verify prerequisites, install/uninstall behavior, settings/results/restart and required remote journeys on a clean machine. Resolve critical crash/stall/data-loss/economy/authority/required-ability defects. Record exact owner release approval. Decide whether the 30-person counterbalanced comparative study is a release gate before it runs; do not silently delete or claim that gate.

## 4. First three execution batches

Each batch is a bounded work package, not a promised calendar week. Actual participant availability and measured pilot effort determine elapsed time.

| Batch | Gameplay/UI lane | Asset/visual lane | Verification/review output |
|---|---|---|---|
| **1 — Close the current review gaps** | Identify exact seven-hero source/package/control; prepare physical full journeys at three resolutions; prospectively specify Silkmother study cases; retain current pacing defects | Prepare one combined G1/Cragstoat review, existing Silkmother delivery review and exact remaining G2 decisions; preserve Bellback | Candidate/defect register, actual input observations, review packets, participant/device logistics sheet. No speculative new hero, trait or paid job. |
| **2 — Correct and measure** | Fix observed journey/cue defects; conduct eligible B1/B2 observations when people exist; select only an evidenced pacing candidate; run affected native/package comparisons | Advance only candidates with their dependencies met; prove Cragstoat game motion; resolve Prism cavity and Reefglass hidden parts; assemble readable Wondergrove slice | One versioned study candidate, scoped regressions, normal-speed observations, complete creature handoff and qualified profiling capture. |
| **3 — Accept the slice, then choose expansion** | Decide technical/comprehension/pacing outcomes separately; finish complete tournament observations; identify practical acquisition gaps | Complete original M2 pilot obligations or record an explicit amendment; accept exact look/art and finish mixed-board audio accessibility/localization and performance review | M1–M3 gate disposition. Only passed dependencies open the relevant M4/M5 tasks; failed balance does not halt independent UI/art work. |

## 5. Priority and ownership rules

The backlog uses **P0** for current identity, actual-input and recovery/authority blockers; **P1** for comprehension/pacing and existing-candidate production; **P2** for ecosystem and solo-beta completion; **P3** for later remote/release gates. A discovered critical defect moves its affected task to P0.

Dependencies identify required inputs, not a requirement to implement every optional proposal. Hero/trait/progression candidates may receive a documented not-selected disposition; audit and freeze the content actually promoted. Plan B still needs its eight-family and other entry evidence. Plan C assumes the adopted remote scope; narrowing release to solo requires an explicit scope decision and corresponding backlog revision.

Owner roles describe responsibilities, not an assumed staffed team. The integration owner coordinates source and packages; gameplay owner manages rules/experiments; asset owner manages a single candidate/rig; UX owner manages flows/accessibility; QA/study owner manages evidence and eligibility; project owner makes prescribed human art/scope/release decisions. One person may hold several roles sequentially. No participant outreach is authorized merely by assigning study tasks.

For each execution task, record intended player outcome, candidate, dependencies, owner, bounded change, verification, actual findings, defect severity and next step. Report pass/revise/inconclusive/blocked against the precise claim. Continue independent authorized work when a dependency blocks one lane.

## 6. Development dashboard

| Measure | Target or decision rule | Status at planning |
|---|---|---|
| First-use preparation/lifecycle | Existing B2: ≥4/5 independent successes for each of nine tasks; separate group spectating observation | Current-candidate external study open |
| Principal-cause explanation | Existing B2: ≥4/5 participants pass ≥2/3 unfamiliar explanations | Open |
| Formation revision | Existing B1 rubric, five external participants, four-of-five formative gate | Open |
| Timeouts | Existing B0 screen: <2% overall/PvP/ghost; ≥100 per assessed stratum | Historical controls fail; current candidate needs identified evidence |
| Tournament duration | Existing 35–45-minute target; five normal-speed final-winner observations | Unverified; accelerated bot runs excluded |
| Accessible strategies | Eight required strategic families, normal acquisition/counter evidence | Full ecosystem not accepted |
| Creature completion | Proposed tracking: accepted game-ready heroes / frozen enabled roster, currently seven | Bellback exact candidate accepted; remaining candidates incomplete/open |
| UI coverage | Existing three-resolution physical journeys; scale/localization/accessibility review | r29 handler/projection evidence at two sizes; full human journeys open |
| Performance | Existing 1080p: p95 ≤16.7 ms; p99 ≤25 ms; investigate recurring >100 ms stalls | Final mixed-content/hardware evidence open |
| Repeat play | Existing M5: ≥12 people across separate days, losses/adaptation/replay observed | Not run |
| Remote play | Existing independent-device 2H6B/4H4B/8H0B whole matches | Prerequisites incomplete; not remotely accepted |
| Release reliability | Existing final freeze: ≥1,000 native + ≥100 engine tournaments; clean machine; zero unresolved critical defects | Historical exact builds retained; final scope/candidate open |

## 7. Authority and execution references

- [Product/combat contract](../PRODUCT_AND_COMBAT.md), [art/UI contract](../ART_UI_PRODUCTION.md), [validation/rollout](../VALIDATION_AND_ROLLOUT.md).
- [B0 adopted execution defaults](../milestones/B0_EXECUTION_CONTRACT.md), [human study kit](../milestones/HUMAN_STUDY_KIT.md), [historical milestone proposal](../milestones/DEVELOPMENT_MILESTONES.md), [outstanding milestone tracker](../milestones/MILESTONE_STATUS.md).
- [Creature pipeline](../../../production/creature-pipeline/README.md), [acceptance](../../../production/creature-pipeline/ACCEPTANCE.md), [four-view route](../../../production/creature-pipeline/FOUR_VIEW.md), [AS1 skill](../../../.agents/skills/wca-orchestrate/SKILL.md), [creature-production skill](../../../.agents/skills/wc-creature-production/SKILL.md).
- [Bellback exact owner acceptance](../../../reports/bellback-production-20260920/owner-acceptance.json), [Cragstoat current handoff](../../../art-source/asset-studio/wc_vn_cragstoat/stages/production_r002/handoff.md), [Silkmother current plan](../../../art-source/asset-studio/wc_vn_silkmother/DEVELOPMENT_PLAN.md), [2D master inventory](../art/2D_ASSET_MASTER_SPEC.md).

This planning revision runs no game tests, submits no provider jobs and changes no gameplay/art acceptance. Its completion means the plan and backlog are authored and locally checked; the goals above remain future work.

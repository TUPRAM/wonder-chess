# Wonder Chess — detailed development milestones after the critical review

Prepared 12 September 2026, Asia/Singapore. Status: **PROPOSED — NOT STARTED OR ADOPTED BY THIS DOCUMENT**.

Read [Review notes and decision register](REVIEW_NOTES.md) first. This plan uses successor commit `d80635f615810a93c3161c6bfd6c34c758b08260`, matching the supplied GPT Pro review and the remote refs verified during planning. It preserves the adopted [M0–M7 programme][contract]. All new tasks, numerical study gates, and policy refinements below are proposals unless explicitly identified as existing contract requirements. This planning task runs no game tests and changes no implementation status.

## 1. The development direction

The near-term player promise is: **“I understand what my formation did, I can obtain another approach, and I want to try it.”** Each batch must produce an observable player outcome, a bounded reviewable artifact, and evidence that can reject the underlying hypothesis.

Keep six creatures as the initial control; keep independent shops and authoritative C++ systems. Test three contrasting plans before broad expansion: protected firing, approach pressure, and screen-breaking/displacement. Do not turn the control into a final roster cap. Preserve the existing eight-archetype long-term product requirement, but require actual acquisition and human evidence before counting an archetype as accessible.

## 2. Sequence and mapping to the adopted programme

| Work package | Player-facing outcome | Existing milestone contribution | Completion boundary |
|---|---|---|---|
| B0 — Decision and study setup | Future comparisons have a stable, explainable rule set | M0 amendments and evidence setup | Decisions/measurement ready; no gameplay acceptance |
| B1 — Readable formation consequences | Predict, observe, explain, and improve a formation | M1 combat comprehension; M3 pacing investigation | Formation study; balance and UI accepted separately |
| B2 — Complete solo adaptation loop | Recruit, scout, adapt, draft, finish, save, and resume | Remaining M1 interaction work; major M3 frontend/recovery work | Functional 1H7B study candidate; pacing and repeat play still measured separately |
| B3 — Small trait experiment and Bellback pilot | Make a meaningful pair decision; read one finished creature in combat | Partial M2; bounded M4 ecosystem experiment | Two independent trait/art decisions; not all of M2 or M4 |
| Complete M2 and residual M3 | Coherent three-pilot Wondergrove visual slice and reliable measured tournament | M2 and remaining M3 | Three families, screen, motion/audio, recovery and pacing evidence |
| M4 — Earned roster/ecosystem expansion | Discover several accessible plans with distinct weaknesses | M4 | Small accepted batches; eight-archetype goal earned through play |
| M5 — Solo beta | Learn unaided, adapt over repeated sessions, choose to return | M5 | Solo usability, accessibility, repeat-session evidence and stabilization |
| M6 — Remote online beta | Play fair, recoverable games with real remote opponents | M6 | Independent-device networking, authority, privacy and operations |
| M7 — Frozen release candidate | Install and play the exact supported product reliably | M7 | Exact content/build, clean machine, human signoff, performance, rollback |

Dependency sequence: **B0 → B1 → B2 → B3**, then finish M2/residual M3 and expand through M4 → M5 → M6 → M7. Dependencies are per deliverable, not blanket stops. B2 control/view work can proceed once its authority contracts are stable even if a B1 tuning candidate fails. Bellback's approved-stage production can run alongside independent gameplay work when separately authorized. Shared catalogue, generated files, and Blender binaries still have one writer at a time.

M1 does not close from the formation lab study alone. M2 does not close with one pilot. M3 does not close from serialization alone. Existing test results remain evidence for their exact candidate, not acceptance of future changes.

## 3. B0 — Decide the experiment before implementing it

**Outcome:** the team can state what the next candidate is meant to prove and what would cause it to be rejected.

**Entry:** owner discussion of this proposal; re-verify successor checkout and current authority. Local `main` at planning time is historical, so do not start development there merely because it is the current directory. Preserve existing untracked work and the tested Lab-r3 control. Use the verified successor checkout or a properly registered Codex worktree if implementation later needs isolation.

| Task | Concrete deliverable | Done when |
|---|---|---|
| B0.1 — Candidate identity | Control record with Git revision, profile/balance version, source/runtime/package digests and known defects | The intended package and content are unambiguous; historical alpha is not substituted |
| B0.2 — Product decisions | Recorded outcomes for D01–D03 in the notes; owners/deadlines for D04–D09 | Required decisions are adopted or explicitly open with affected work named |
| B0.3 — Experiment specification | Fixed task rubric, metrics, scenario IDs, investment convention, regression inputs and held-out strategy | No threshold or exclusion rule will be changed after seeing candidate outcomes |
| B0.4 — Study logistics | Moderator, build operator, participant eligibility/experience categories, minimum group sizes, scoring unit, consent/session plan and target hardware | Novice definition and sample plan are fixed before recruiting; actual people/hardware available before scheduling |

**Recommended decisions to discuss:** elimination as the intended primary victory, existing timeout adjudication retained in the control and made visible; six-creature default with a narrow counter-gap exception; independent shops retained; live public scouting with explicit update identity; at least one owned-team compatible relic offer when feasible. Plant's finite protection budget and Bellback's precise reference remain separate decisions.

**Verification:** source provenance review; confirm that frozen inputs have not changed; review scenario and study specifications for confounded variables. Do not rerun a large combat batch just to approve a planning document.

**Human requirement:** owner decisions for new gameplay policy and study expectations. Bellback's reference decision is needed only before its affected production stage.

**Stop:** an unresolved rule stops the implementation that depends on it. No date promise until actual capacity and pilot effort are known. A discussion document is not implementation authorization.

## 4. B1 — Make formation consequences understandable and testable

**Player outcome:** a player independently makes a useful positional change and explains its main observed effect in an unfamiliar encounter.

**Artifact:** one versioned formation-study package with saved scenarios, rapid A/B comparison, engine-derived inspection, factual recap, and a completed formative study report.

**Dependencies:** B0 control and measurement rules; existing six active mechanics. No new hero, trait, final art, or new architecture is required for the default scope.

### Work packages

| Task | Scope and deliverable | Acceptance evidence |
|---|---|---|
| B1.1 — Scenario persistence | Save/load named formations with schema/content identity, both rosters, stable IDs, stars, relics, positions, facing, seed, and intended variable | Exact load/replay; clear unsupported/corrupt-data rejection; previous valid scenario preserved |
| B1.2 — Six scenario pairs | One pair for each core mechanic, including favorable/unfavorable and mirrored cases | Within a causal pair, roster, stars, relics, investment and seed stay fixed; only declared formation inputs differ |
| B1.3 — Factual inspection | Selected guard recipient and link change; charge momentum/path/landing; grove establishment/reset; committed line, crossing and push destination | Display derives from the same rules/geometry as combat; no separate guessed targeting table |
| B1.4 — A/B and recap | Quick repeat and comparison, comparable timelines, one or two event-grounded findings, optional unit/events detail | Repeat produces identical events; a claimed alternative outcome has an actual replay behind it |
| B1.5 — Sustain candidate | Separately versioned 75% Root pulse candidate; timing, geometry, bot policy, and other tuning unchanged | Effective healing, deaths, timeouts, counterplay and sustain utility compared with the control |
| B1.6 — Charge experiment | Manual approach/landing formations; separate bot-placement candidate only after a useful human placement is established | Distinguish unavailable opportunity, no attempt, interruption, illegal landing and released charge; no simultaneous damage compensation |
| B1.7 — Early counter scenario | Protected sustain versus obtainable level-3-to-6 tools, with level-specific offer/cost limits | A practical early response is shown or a precise counter-access gap is recorded; no free Reefglass conceals the gap |
| B1.8 — Held-out and human review | Unfamiliar formations, mirrored orientations, unused seeds and five external-player sessions | Technical, comprehension and tuning findings recorded separately |

### Scenario inventory

| ID | Single relationship under study | Player task and observation |
|---|---|---|
| F01 Guard | Intended rear ally versus flank/separation | Predict the selected ally; recognize why protection changes after movement |
| F02 Approach | Available approach and landing versus front-line crowding | Create a useful charge opportunity; recognize how a defender can deny it |
| F03 Grove | Establishment position versus burst/forced reset | Choose where holding ground is worthwhile; see establishment and disruption |
| F04 Strike screen | Blocked distant strike versus another angle | Open or close a strike path and identify the actual intercepted recipient |
| F05 Crossfire | Shared rows/columns versus spread | Reduce or exploit beam coverage without assuming placement guarantees a win |
| F06 Tide | Facing and free destination versus stagger/blockage | Predict the lane, first target and legal push result |
| F07 Early response | Affordable pressure against protected sustain | Compare cost-1 tools at level 3, later Snapvine angles and Prism access; identify remaining gaps |

Across F01–F06 keep the army literally identical for formation comparisons; declare any facing change. F07 is a separate acquisition/counter experiment, so it may vary roster within a stated affordable budget. Define investment consistently, including copies represented by stars, rather than comparing arbitrary team prices. Unfamiliar variants must not merely reproduce a demonstrated answer with changed names.

### Technical and measurement requirements

Use the existing combat engine and focused fixtures. Check occupied destinations, full boards, blocked pushes, interrupted commitments, grove movement/stun/defeat reset, delayed released damage after source defeat, dead-recipient exclusion, side mirroring, and exact replay. Preserve the distinction between persistent damage packets and tethered Root healing. Test that inspection and repeated relic evaluation do not mutate combat state.

Record effective healing and overheal separately; guard recipient/uptime; charge opportunity, commitment, release, landing and failure reason; first meaningful action and first death; combat duration; elimination/deadline/tie result; survivor count/investment; encounter category and round cap. Reconcile metric totals against authoritative events rather than inferred animation.

Use existing seeds 1–1000 as regression evidence for a promoted tuning candidate. Reserve a genuinely unused seed set and held-out formations before tuning, verified against the run inventory. A proposed starting confirmation size is 250 new tournaments; record seed IDs, all failures, and denominators. Once used to select a change, those inputs are no longer held out. Additional candidate iterations need fresh confirmation inputs. Do not use repeated package/native matches as independent balance samples.

Unchanged bot-policy code does not guarantee unchanged bot purchases: ability valuation can respond to the modified healing magnitude. Fixed-roster combat fixtures isolate the local mechanic comparison. Full tournaments also measure resulting recruitment/composition changes; log that drift and do not attribute every tournament difference directly to healing.

The existing below-2% combat-timeout target is **proposed acceptance**, not a current pass. For this batch, propose requiring it overall and separately for PvP and ghost strata with adequate observed counts; always disclose neutral results. Adopt or refine this stratum rule in B0 before execution. A tiny or absent stratum is insufficient evidence, not a zero-rate pass. Report round caps separately and investigate persistent cap-heavy compositions; no numeric round-cap target is silently invented here. Lower timeout rate alone is insufficient if sustain becomes useless or burst deaths become unreadable.

### Human protocol and advancement

Five external participants, with newcomers and genre-experienced players represented. After standardized controls onboarding, use normal speed: prediction → battle → explanation before recap → independent formation revision → replay. Record moderator help as assisted, not independent success. Include losses and unfamiliar scenarios; make extra attempts optional.

Proposed formative gate: at least four of five independently identify a useful change and explain its principal effect on unfamiliar scenarios. Report per-participant and per-mechanic results, plus novice/experienced counts. A pooled pass must not conceal a systematically misunderstood mechanic. This is a small-sample formation-comprehension checkpoint; it does not satisfy the separate M1 recruitment/scouting study or establish a population success rate.

Every creature needs at least one demonstrably useful and one unfavorable placement, and the three strategic plans need distinct weaknesses. A tuning candidate advances only with technical correctness, transparent timeout/round-cap findings, useful positional sustain, and held-out/human review. If only the UI passes, accept that component and retain the prior tuning control.

**Stop/rework:** after two failed iterations on the same interaction, review targeting, movement or cues before adjusting damage again. Reject a “fix” that removes the intended healing decision. If early counterplay cannot be made practical without distorting current identities, stop that acceptance claim and choose a bounded contract revision or a one-creature Manyfoot prototype. This is a new scope decision, not automatic roster expansion.

**Wait:** global trait activation, new classes, summons/constructions, new relics, finished roster art, and timer padding. Independent B2 UI work can continue under a clearly labeled experimental balance candidate; do not call its balance accepted.

## 5. B2 — Deliver the full solo recruitment-and-adaptation loop

**Player outcome:** one human can recruit against seven bots, understand owned copies and money, scout, alter a plan, equip relics, finish or leave a tournament appropriately, and resume an offline preparation save.

**Artifact:** a coherent packaged 1H7B successor flow: preparation → automatic combat → factual recap → next preparation → elimination/results → restart, with durable preparation save/resume.

**Dependencies:** B1 usable mechanics/inspection and a known-defect list; chosen rules candidate; D04 scouting/cutoff and D05 relic usefulness policy. Stable transaction/view work may start while balance investigation remains open. Final study findings identify the exact tuning used.

### Work packages and acceptance

| Task | Deliverable | Required verification |
|---|---|---|
| B2.1 — Preparation/economy | Five shop offers, exact owned copies including represented star copies, buy/sell, reroll, lock, XP, gold/income, level, ready and phase clock | Widgets call existing authority; no second economy implementation; correct affordability and reject feedback |
| B2.2 — Board/bench controls | Ten-slot bench, actual level-based deployment capacity, move/swap, meaningful facing, legal-cell previews, click alternatives and visible keyboard focus | Real pointer/keyboard journeys, full bench and merge paths, phase cutoff, selection retained on rejection |
| B2.3 — Public scouting | Viewed seat/round/update identity, deployed roster, actually implemented traits, equipped relics, standings, next opponent and persistent return action | No benches, shops or draft choices exposed; no actions accidentally sent to the viewed opponent |
| B2.4 — Relic acquisition | Three-offer draft, inventory, compatibility, equip/unequip, drawbacks, speculative labels and exact effective-mechanic explanation | Draft entitlement, empty/no-compatible team fallback, incompatible equip, deterministic offers, no duplicated or lost relics |
| B2.5 — Tournament lifecycle | Opponent and ghost identity, combat/recap, standings, loss/elimination, spectate/exit and results/restart | Every off-screen fight uses actual combat; elimination cannot stall progression; restart clears prior match state |
| B2.6 — Durable offline recovery | Preparation-boundary autosave, pause/save/resume controls, visible completion/error, retained previous valid save | Atomic replacement and interrupted-write tests; profile/content validation; cold package relaunch reproduces state and streams |
| B2.7 — Full input journey | Coherent onboarding and observable command feedback, basic text readability, focus, color-independent states | Actual controls complete the journey; direct handler calls alone do not count |
| B2.8 — M1 study and pacing report | Five external participants, acquisition telemetry, adaptation observations, full tournaments and resume tasks | Unassisted/assisted tasks and explanations scored separately; reported human phase durations |

Scouting recommendation: show a live public state and visible revision/update identity, with a common preparation cutoff for authoritative changes. Define ready/unready behavior, clock expiry, snapshot displayed during combat, and interaction with the existing bot reposition cutoff before implementation. No player or bot receives private information or extra action privileges. If the product instead chooses a locked scouting snapshot, state its age and apply one clear rule; do not silently mix live and stale views.

Relic recommendation: at draft generation, use currently owned deployed and benched recruits to guarantee one compatible option when possible. Specify no-owned-compatible fallback, roster changes before choice, duplicate-offer handling, and replay/save determinism. This is a proposed policy change. Retain all twelve existing definitions; onboard tradeoffs progressively rather than adding more. Bellback's expanded radius still chooses one recipient; do not imply an area shield.

For recovery, define what is saved at preparation boundaries and what progress can be lost if interrupted during combat. Never advertise arbitrary mid-combat saves. Stage a new file, verify it, replace atomically using an appropriate platform operation, and retain the previous known-good save. Confirm recovery if interruption occurs before write, during write, before replacement, and after replacement. Failures must preserve the last valid save. Do not allow an online-origin match to become an offline save through bot takeover.

### Tests

Cover full-bench three-copy merges, insufficient funds, simultaneous relevant commands, replayed/changed-payload/reordered/stale requests, wrong ownership, phase-boundary buys/moves/facing/draft actions, max-level XP, relic conservation on sale/merge, incompatible equipment, snapshot semantic errors, corrupt/incompatible versions, interrupted writes and failed resume. Verify no duplicated spend, relic or settlement. Include eliminated-human progression, ghost labels, results and a fresh restart.

Run actual packaged pointer/keyboard paths at 1280×720, 1600×1000 and 1920×1080, retaining readable cells and required controls. Match focused native and packaged outcomes for the frozen candidate. Keep the existing legacy regression when shared authority code changes. A human study candidate needs a reproducible source/input manifest; establish a clean-checkout build before distribution outside the development machine, rather than assuming the historical dirty build is portable.

### Human study and advancement

Propose five external participants who are new to Wonder Chess for this M1 checkpoint, with genre-new and genre-experienced coverage recorded separately. B0 must explicitly adopt this definition of novice; if the intended target instead means genre novices, recruit five eligible genre novices and report experienced observations separately. Returning B1 participants supply repeat-use observations rather than first-use novice evidence. Each first-use participant should buy toward an upgrade, place and orient a relevant creature, scout and return, make an informed formation change, explain a battle before recap, experience a loss, draft/equip a relic, play to victory or their elimination, and resume a preparation save after closing/relaunching the package. Elimination ends active participation; it does not end the eight-seat tournament. At least one observed journey must cover continued spectating through final results; a loss must not trap the user. Full-tournament and resume evidence can occupy separate sessions to avoid fatigue confounds.

Use the documented proposed 80% novice preparation-task and 80% principal-cause recognition targets. For the five-person first-use group, propose four-of-five independent successes on each required preparation task. For explanation scoring, each participant attempts three predefined unfamiliar encounters and passes that participant-level task by correctly identifying the principal observed mechanism in at least two; the group target is four-of-five participant passes. Adopt the encounter rubric in B0, report all encounter-level errors, and flag any consistently misunderstood mechanic. Report raw numerators/denominators per task and experience group. Fewer than five eligible first-use participants leaves this proposed gate incomplete. Observe actual strategy adaptation after scouting/defeat, not just successful button use.

Log shop exposure, affordability at offer time, purchased/sold/deployed copies, gold spent on XP/rerolls, available alternatives, unit access by round/level, and proposed reasons for choices. Separate participant explanations from telemetry-based inference. Measure time to first meaningful decision; active preparation, waiting, combat and recap; unproductive combat time; repeated late rounds; elimination/restart behavior; optional replay. Report active player-session/time-to-elimination separately from complete standard tournament time through the final winner. Exclude early-exit sessions from the full-tournament median; do not substitute accelerated post-elimination bot completion for normal-speed human duration evidence. For an initial duration readout, propose at least five complete normal-speed tournament observations, scheduled separately if needed, with clock endpoints, pauses, settings, sample count, median and spread disclosed. This is exploratory evidence, not a stable population duration estimate. One spectating journey does not supply five duration observations. Report misses honestly and do not add waiting to make the number fit.

Advance functional M1/M3 components only with no unresolved critical crash, match stall, economy, command-authority, privacy, or save-loss defect, and demonstrated unassisted adaptation. Full M3 pacing acceptance remains open if its human-duration or timeout target fails. Recruitment and recovery can be accepted independently with their precise limits recorded.

**Stop/rework:** automatic purchase/upgrade sequences with little meaningful tradeoff, inaccessible counters, repeated assistance, save loss, or an inability to finish/restart. Investigate costs, offer distribution, star power and information before adding a shared pool or many heroes. Critical defects block the affected participant build. Independent safe UI/content work can continue.

**Wait:** remote multiplayer, ranked systems, full progression/bestiary production, elaborate menus and broad cosmetic manufacturing. Carry full localization, remapping, text scaling and reduced effects explicitly into M2/M5 rather than deleting them from scope.

## 6. B3 — Prove a small composition choice and one complete art pilot

**Player outcome:** a player understands when a pair is worth a deployment slot, when another tactical tool is better, and what Bellback is doing during crowded combat.

**Artifact:** independently reviewable trait-off/trait-on candidates, one Bellback asset taken through the full applicable pipeline into a package, restrained Wondergrove support presentation, and a twelve-participant study. **This is partial M2 and exploratory M4 work.**

**Dependencies:** B2 acquisition evidence and usable flow. Beast's limits must be specified before implementation; Plant waits for sustain findings and an adopted finite-budget/reset contract. Bellback complex modeling waits for the exact reference approval. A blocked asset stage does not block unrelated gameplay work, and a rejected trait does not invalidate an accepted model.

### B3-G — Trait experiment, accepted separately

| Task | Deliverable | Tests and review |
|---|---|---|
| B3-G1 — Beast 2 contract | Explicit trigger after completed charge, recipients, bounded movement response, expiry, caps and no recursion | Distinct recruited-type counting, activation snapshot, duplicates/bench exclusion, interrupted/failed charge, repeated trigger boundaries |
| B3-G2 — Beast comparison | Trait-on versus identical trait-off scenarios using three-to-five-slot teams | Measure coordinated movement, lost guard links, denied landings, unintended clustering and practical opportunity cost |
| B3-G3 — Plant 2 contract | Explicit stationary protection amount, establishment, recipient, lifetime, exhaustion and reset/rearm policy | Movement/displacement/stun/defeat resets; no unapproved free replenishment; no hidden healing amplification |
| B3-G4 — Plant comparison | Separate Plant-only versus trait-off candidate after sustain acceptance permits testing | Compare first burst survival, protection consumed, late-fight healing, timeout/round-cap regressions and alternative slot choices |
| B3-G5 — Interaction check | Both accepted pairs together only after individual effects are understood | Deterministic replay, recipients, caps, expiry, pair tradeoffs at low capacity and automatic-completion risk at high capacity |

Do not activate inaccessible higher thresholds or class icons. Do not lower thresholds or alter membership just to make them light up. Record balance changes separately from behavior activation. Use the same catalogue version except for the declared experimental differences.

**Gameplay gate:** players can explain examples of both completing and rejecting a pair, and make those choices in an actual opportunity-cost task. Propose an individual task rubric before the study; observe decisions rather than teaching a required answer. A trait fails if it simply boosts the existing default formation, breaks intended guard/approach decisions without clear counterplay, or restores sustained timeout problems. Disabling/revising a failed trait is a valid result; two active traits are not a mandatory success outcome.

### B3-A — Bellback pipeline, accepted separately

| Task | Deliverable | Stage exit |
|---|---|---|
| B3-A1 — Exact reference and prose | Owner decision against the sealed reference snapshot; reconciled dorsal-bell catalogue wording in a deliberate new content revision | Recorded asset reference approval; generated content identity consistent; frozen control preserved |
| B3-A2 — Blockout and full forms | Recognizable silhouette, proportions, paws, face, dorsal bell/mount and facing at the actual camera | Owner full-form decision and inspected crowded-board views; no downstream topology used to hide unresolved forms |
| B3-A3 — Production asset | Topology, UVs, readable materials, rig/weights, sockets, selection bounds and optimization | Actual deformation/identity/export checks; measured scale and one-cell interaction contract |
| B3-A4 — Essential motion and tells | Idle, locomotion, turning, attack anticipation/release/recovery, guard communication, hit, interruption and defeat | Continuous normal-speed review; combat-event timing owns gameplay; no second damage authority in animation |
| B3-A5 — Unreal/package integration | Exact imported asset/material/rig/animation bindings and package content | Reimport/cold-load identity; locomotion/turning/target change/interruption; neighboring-cell visibility and input bounds |
| B3-A6 — Measured approval | Reviewed gameplay captures, performance trace and stage/rework effort report | Owner's applicable asset release decision plus technical/package/readability results recorded independently |

The Bellback pilot inventory also includes LOD representations and transition review, portraits/icons, guard VFX/audio, and binding into the available creature-inspection presentation. Preserve an editable-source bundle with references, materials/texture sources, rig, motion, exports, presets, hashes, provenance and known defects. If the complete gallery/bestiary frontend is still deferred, record its final binding as open and approve only the explicitly named pilot use; do not claim full release-inventory acceptance from that limited integration.

The formal gates come from AS1: reference identity before complex modeling, accepted full forms before downstream production, and exact asset release signoff. The pending Bellback reference snapshot is `83de2292eeb1195963b1d479e194be171a87dd3c5eb960d47de870250fb2f842`. Its shared-direction selection does not supply those approvals. If the snapshot changes, re-identify and review the affected evidence. This plan neither asks for nor records an approval.

Use one Blender queue and one writer per binary/rig family. Review two unsuccessful critical-form revisions as a method problem, then change construction method or stop the affected stage. Preserve candidate files and invalidation dependencies; do not restart historical Ada work as a Bellback prerequisite.

### B3-P — Supporting screen, references and study

Provide the Wondergrove gameplay context needed to evaluate Bellback: clear cells and bench, restrained central detail, ownership/selection/facing/status cues, coherent shop/recap frame, and essential guard audio/visual tells. Label unfinished board and remaining creature proxies. One polished creature does not make the full screen accepted.

Resolve Prism Organ's specific reference inconsistencies and prepare Thimblewake's production decisions. These reference tasks can inform the next serial pilots, but do not promise two additional finished assets inside B3. Thimblewake's art pilot and its future combat mechanic have separate entry gates.

At least twelve external participants, including newcomers and genre-experienced players. Run the trait study separately from visual comparisons. Hold presentation fixed for trait-on/off tasks. For proxy-versus-Bellback readability, use identical recorded combat, fixed camera/timing/labels, and counterbalanced viewing order. Use a separate unseen live fight to test transfer. Do not count repeated views as new independent participants.

Test recognition, team ownership, facing, guarded ally, guard transfer/loss, committed effects, losses and willingness to try again. Include duplicate Bellbacks, both orientations and crowded twenty-unit scenes. Record incorrect interpretations, time to identify relevant cues, occluded cells, moderator assistance, and optional replay separately from attractiveness ratings. Novelty or preference for the finished mesh cannot establish a gameplay benefit.

Profile the actual target Windows machine at 1080p using the existing targets: p95 frame time ≤16.7 ms, p99 ≤25 ms, and no recurrent unexplained >100 ms stalls. Record CPU/GPU/RAM, graphics settings, engine/driver identity where relevant, memory, active effects, simultaneous off-screen fights and loading. B3's performance result covers its mixed finished/proxy content only; later content requires renewed measurement. Record hands-on stage hours, tool waits, failed revisions, rework causes, and engine integration effort separately.

**Advance:** trait and art get separate accept/revise/inconclusive decisions. Bellback must satisfy its owner gates and normal-speed crowded-camera readability; traits must create understandable tradeoffs without erasing positional choices. Full twelve-person visual-slice acceptance for M2 remains open until its full required content is present.

**Stop/rework:** automatic pair selection, renewed sustain timeouts, unclear recipient/ownership, important cells hidden by the model, event/motion disagreement, or material performance failure. Reduce visual complexity if it harms play. A beautiful render or successful import cannot override these findings.

**Wait:** broad roster manufacturing, all eighteen traits, additional finished boards, simultaneous rig-family scaling, online release. One successful pilot provides measured information about that family only.

## 7. Finish the existing M2 and residual M3 gates

**Player outcome:** the solo candidate presents a coherent world and complete screen, with three readable creature pilots, usable UI, intelligible effects/audio, reliable recovery and measured pacing.

**Dependencies:** B3 Bellback method and cost evidence; B2 player flow. Prism and Thimblewake need their own exact reference/forms gates. Accepted gameplay need not wait for all final roster art, but the M2 visual claim requires the actual slice.

| Task | Scope | Done when |
|---|---|---|
| M2-R1 — Prism Organ pilot | Reconcile references, then serial floating-assembly production, ordered beam cues, core/material clarity and motion | Full applicable owner, import, continuous motion, gameplay-camera and package gates |
| M2-R2 — Thimblewake pilot | Reconcile references, then articulated insect production, readable limb reach/selection and motion | Separate family proof; combat-kit status remains explicit if not yet implemented |
| M2-R3 — Complete Wondergrove | Board, bench, perimeter, lighting, ambience, camera/collision and transitions | Complete preparation/combat/recap screen with no essential cell/control occlusion |
| M2-R4 — UI, effects and audio | Consistent state language; heal/guard/stun/displacement/damage cues; creature motion and sound; direct listening review | Actual input journeys and normal-speed busy matches; no misleading effects or masking/clipping |
| M2-R5 — Accessibility slice | English/Indonesian parity, long text, 125/150/200% scale, focus, remapping, pointer alternatives, reduced motion/effects, volume controls | Actual required actions remain possible and readable across supported layouts/settings |
| M2-R6 — Complete slice review | Full three-pilot slice with at least twelve participants and measured target-hardware traces | Content-complete human/readability/performance findings; B3's narrower study is not substituted |
| M3-R1 — Recovery/lifecycle closure | Remaining restart, elimination, save boundary, corruption/interruption and actual relaunch defects | No critical unresolved lifecycle or save-loss defect on the exact candidate |
| M3-R2 — Human pacing closure | Preparation/combat/recap duration, late-game repetition, deadlines, round caps and elimination experience | Accepted pacing evidence or explicit unresolved/revised target; no padding to reach 35–45 minutes |

Observe all required behavior continuously: locomotion and turns, cast/attack start-release-recovery, minimum/maximum attack-rate timing, target changes, interrupted actions, source defeat after release, displaced units, hit/defeat and blends. Listen to a full busy match. Polygon or clip counts cannot substitute.

Original M2 art-pilot priority does not force Thimblewake to be the next gameplay addition. If its combat kit remains authored, a controlled animation/presentation fixture can verify the articulated family and generic motion only. Signature event alignment and actual duel readability remain unpassed until that mechanic executes. Do not fabricate an executed duel. Closing M2 with that limitation requires an explicit owner-approved amendment to the original milestone scope; otherwise M2 remains partial.

**Stop:** unresolved critical forms, repeated ineffective revisions, misleading combat cues, accessibility failures affecting core tasks, uncontrolled tool/integration cost, or missed performance. Stop the affected stage and continue unrelated approved work. Freeze roster production estimates until all three family pilots supply real data; identify which future families remain unproven.

## 8. M4 — Expand only to fill demonstrated strategic and acquisition gaps

**Player outcome:** players can discover, recruit, change between, and counter several coherent plans. The long-term contract calls for eight accessible strategic archetypes, not eight labels in dossiers.

**Dependencies:** useful B1/B2 play, measured acquisition, stable integration conventions, and family-specific production proof before art scaling. Small mechanic prototypes may be explored before full art production when a documented gameplay gap justifies them. The default batch is one mechanic at a time, with at most two tightly related creatures after the first is understood; this is a proposed work-in-progress limit, not a final roster cap.

| Candidate | Evidence that earns the experiment | First bounded proof |
|---|---|---|
| Manyfoot | Affordable screen bypass is missing after testing current units | One logical entity/health pool; legal rear destination, crowding denial and cost-2 acquisition; colony art later |
| Silkmother | Route control creates a distinct preparation choice | One specified destructible trip-line/anchor behavior; explicit entity cap, placement, lifetime, ownership and demolition |
| Thimblewake | Isolation creates useful side engagements and clear counterplay | One bounded challenge/parry/riposte contract; nearby-support eligibility and ranged counters |
| Kilnback | A defensive alternative is useful without reinforcing the default fortress | Frontal projectile capture/vent decision first; Guardian/Construct bridge only afterward |
| Wren / Hushlantern | Existing sustain is accepted and service/delayed rescue changes decisions | Separate station or capped delayed-rescue test; compare against Root rather than accepting different animation as variety |
| Dawnkite / Coilwyrm | Existing artillery/displacement leaves a concrete tactical or acquisition gap | Distinct sector or ring-edge decision with real failure cases and normal acquisition |

M4.1 maintains a live strategic matrix: plan, early entry pieces/cost, core positional relationship, counter and counter access, later adaptation, trait tradeoff, and human example. M4.2 prototypes the chosen behavior with useful/unfavorable/mirrored fixtures. M4.3 integrates economy, targeting, release/interruption, previews, recap, relics, saves, bots and packaged replay. M4.4 runs real recruitment/formation sessions and updates the matrix. M4.5 produces accepted art only after the behavior and relevant family method earn it.

Per-hero production promotion requires the full art-contract inventory: approved references/forms, mesh/topology, UV/materials, rig/weights/sockets, continuously reviewed motion, LODs and visible transition review, selection bounds, portraits/icons, skill VFX/audio, and actual gallery/bestiary binding. Include the AS1 editable-source/export/preset/provenance bundle and exact package identity. Any deferred item stays explicitly open; a limited pilot approval does not automatically satisfy this full-content promotion checklist.

Keep distinct-type trait counting; no filler memberships to meet arithmetic. Introduce a class only when its members and behavior offer a real choice. Apply the existing four-summons-per-side cap when implementing summons; specify construction limits separately rather than assuming summons rules cover every spawned object. Validate occupancy, ownership, death/destruction, reset, persistence and save behavior for each entity family. Avoid recursive summons/copy behavior beyond the adopted scope.

Include the seven neutral identities and all provisional waves in content acceptance. Choose a teaching objective, implement a mechanic that actually makes the lesson useful, then test player transfer to a later encounter. A wave named “Spread against Reeds” cannot count as spread teaching while it only uses basic attacks without the required pressure. Boss signatures, wave assets, audio and actual acquisition/reward lifecycle need their own execution/readability tests.

**Human evidence:** targeted unfamiliar-encounter tests and full recruitment sessions for every promoted batch, with experience, exposure and affordability logged. Reuse existing scenarios for regressions; use fresh formations for learning transfer. Choose participant numbers and score rules before each batch based on the question; never claim statistical superiority from this formative work.

**Advance:** each hero has normal access, a distinct reason to recruit, a useful and unfavorable formation, practical counters, meaningful star comparisons, coherent relic behavior, honest bot handling, and normal-speed human comprehension. Each counted archetype has an observed acquisition-to-adaptation example and a counter example. M4 closes only for a deliberately frozen release roster and accepted ecosystem; no fixed total of fourteen or twenty-four is imposed.

**Stop:** duplicated decisions, universal utility units, automatic synergy completion, counters available only after the problem dominates, runaway interaction complexity, or art-family effort exceeding the measured budget. Revise/remove the candidate or change the next experiment. Do not expand to hide a failed earlier gate.

## 9. M5 — Solo beta that earns repeat play

**Player outcome:** a new player learns without a developer present, recovers from a loss, explores another build, and can choose another session on a later day.

**Entry:** coherent M2 visual slice, reliable M3 lifecycle/pacing, and a deliberately bounded M4 content candidate. Freeze content for each study period so improvement is not confused with changing rules.

**Work:** complete onboarding and a learning sandbox; animated bestiary with accurate ability geometry, counters and star comparisons; relevant discovery/mastery/history and saved formation tools; expression-only rewards; full accessibility/localization; useful settings and error messages; normal installation/launch; stabilization of UX, economy, performance and recovery defects. Stage optional progression breadth after the core journey works; no permanent combat power or runtime LLM dependency.

**Technical verification:** full input and save/relaunch journeys; content/profile compatibility; onboarding reset/skip; locale and text-scale overflow; remapping/focus persistence; reduced-effects essential cues; sound mix; repeated tournament/restart state; low-resource and busy-scene performance on named hardware. Reuse frozen-candidate native/package regressions when code or content changes warrant them.

**Human study:** at least twelve participants across experience levels, with repeated sessions on separate days as required by the existing visual/solo protocol. Propose three scheduled observations across a week plus a genuinely optional extra session; record scheduled compliance separately from voluntary replay. Include losses, early elimination, unfamiliar opponents and counter-access opportunities. Report enjoyment of losses, fatigue, time burden, formation/build changes, clarity and replay choice separately. Owner/developer sessions are supplementary, not external-user evidence.

**Advance:** core preparation and cause-recognition targets remain satisfied under the adopted definitions; no unresolved critical defects; participants demonstrate independent adaptation across days; replay/attrition and time-cost findings are sufficient for an owner go/revise decision. There is no validated retention threshold in the current contract: define one before any formal retention study, not after observing the data. Repeated formative sessions establish observed repeat use in that sample only.

**Stop:** persistent failure to understand or recover from losses, repetitive optimal buying, inaccessible counters, fatigue-driven abandonment, or polish that fails to improve the core experience. Revisit combat/recruitment before increasing rewards, content volume or online scope. Stabilization is planned work, not a last-day cleanup.

## 10. M6 — Remote dedicated-server beta

**Player outcome:** real remote players share fair matches, see only permitted information, and receive clear recovery or abort behavior when connections fail.

**Entry:** accepted solo candidate, stable protocol/content identity, source-engine dedicated-server toolchain, actual EOS/session registration and independent test hardware. Paid services, public hosting and deployment require separate explicit authorization; this plan does not create or register services. Verify installed versions and official documentation when this work begins.

**Work:** authoritative match server, private rooms and unranked quick play, visible bot filling, authenticated seat control/reclaim, bounded bot takeover, mismatch rejection, error states and support diagnostics. Ranked systems wait for reliability and human balance evidence.

**Progression:** local multi-process development checks → remote 2H6B → remote 4H4B → remote 8H0B. Each remote step uses independent devices, records client/server/build identities and completes whole matches. A successful local eight-client run cannot close any remote-device gate.

**Tests:** stale/reordered/duplicated/wrong-owner inputs, cross-seat private-state access, shop/bench/draft privacy, protocol/content mismatch before join, exactly one controller on reclaim, bot handover without duplicate resources, disconnect at phase boundaries, latency/jitter/loss, server crash and interrupted match. Public deployed information remains visible as designed. Server failure reports an aborted match rather than inventing an outcome. Online-origin sessions remain ineligible for offline resume.

**Human evidence:** people operate all human seats for remote journey acceptance; observe invite/join, scout, draft, reconnect, lose, spectate, finish and rematch. Record geography/network conditions and failures. Agent-controlled clients are useful technical probes but not human online-usability evidence.

**Advance:** phase/economy/formation/outcome agreement on exact builds, no critical authority/privacy/reclaim failure, successful remote progression and understandable recovery. **Stop:** duplicated control, hidden-information leaks, desync, silent result fabrication or unavailable service/toolchain prerequisites. These block online acceptance; independent solo work continues.

## 11. M7 — Freeze and verify the release candidate

**Player outcome:** a player on supported hardware can install, launch, complete, resume where allowed, and restart the exact documented product without the development workspace.

**Entry:** accepted intended release scope from M2–M6, explicit content/protocol freeze, asset approvals and a defined supported-platform promise. If an offline-only release is desired, explicitly revise the release scope rather than silently treating an unpassed M6 as complete.

**Work:** reproducible clean-checkout build, generated/staged/source consistency, exact package manifest, clean-machine installation, settings/save lifecycle, support diagnostics, rollback package and known-issue handoff. Freeze the actual roster and implemented traits/relics/waves; do not imply authored backlog is included.

**Technical gate:** the existing contract requires at least 1,000 full native tournaments and 100 full packaged-engine tournaments on the same frozen content. Record every seed/failure, source/build/tool versions, hashes, start/end states, outcomes, timers and reconciliation. New release content needs fresh evidence; Lab-r3's passing technical batch cannot certify it. Add full normal-speed human package journeys, clean cold launches, save/version mismatch, full tournament/results/restart and relevant remote regression. Measure the real final content, including twenty deployed units, permitted summons, busy effects and concurrent off-screen fights, against the named 1080p frame-time targets. Set minimum specs only after additional hardware evidence.

**Human gate:** owner approval of exact asset/release candidates, external gameplay/visual evidence, actual supported-machine journeys and direct continuous motion/listening review. Zero unresolved critical crash/stall/economy/authority/required-ability defects; material readability/performance failures cannot be reclassified as trivial polish to pass.

**Comparative study:** retain the planned at-least-thirty genre-familiar participant study for a stable candidate. Counterbalance Wonder Chess/Auto Chess order and record versions, prior familiarity, training, session duration and hardware/conditions. Analyze agency, creature appeal, battle clarity, usability and desire to replay separately. Report uncertainty, participant exclusions and sample limitations. The study can support sampled preference claims; it is not a prerequisite for every internal build, and it cannot support universal superiority or long-term retention claims. Whether the comparison is an owner release gate must be decided in advance; no comparative marketing claim is justified without it.

**Stop:** wrong or unreproducible package identity, incomplete clean-machine evidence, critical defect, missing required asset/ability, unresolved human gate, unaccepted performance, or unsupported deployment assumptions. Retain rollback and report the exact unpassed gate. Publication/deployment is a separate authorized action after the candidate is concrete and reviewed.

## 12. Evidence, task ownership and scheduling

### One compact record per work package

When implementation is later authorized, each B/M task records: task ID and player outcome; source/control/candidate identity; owned files and owner; dependencies; tested seeds/scenarios; expected versus observed behavior; actual command/tool/hardware; raw evidence paths; result and failures; human participants and scoring; decision and next action. Preserve unsuccessful candidates and do not overwrite prior raw evidence.

Use separate status columns for **authored, executed, imported, visually reviewed, packaged, externally tested, and accepted**. Operational results are PASS, FAIL, NOT_RUN, or BLOCKED with reasons. Human results may be accepted, revise, or inconclusive; no automatic status promotes them. A proposed task is not an executed result. Update the actual `reports/implementation_state.json` only in the verified successor lane for real work completed, retaining historical records. This document does not alter that ledger.

### Proposed owners and safe parallelism

| Responsibility | Ownership and sequencing |
|---|---|
| Gameplay/source owner | Owns canonical catalogue, rules changes, generated headers/manifests and balance candidate identity; integrates one candidate at a time |
| UI/lifecycle owner | Owns views/input/persistence integration; consumes authoritative commands and agreed interfaces; coordinates shared-file edits |
| Art owner | Owns each active asset binary and the one Blender operation queue; advances only accepted dependencies |
| Verification/research owner | Owns preregistered protocol, run inventory, failure reconciliation and study moderation; independently reviews promotion claims |
| Pram | Decides product amendments, exact human art gates, acceptance tradeoffs and eventual release authorization |

These are roles, not claims that staff are assigned. One person may hold several, but should preserve an independent review of critical promotion decisions. Parallel work is useful for scenario/metric specification, separate UI views, reference reconciliation and evidence review. Do not allow concurrent writes to catalogue/generated outputs, shared schema, `.blend`, `.uasset`, `.umap`, or a rig family. Integration and acceptance remain sequential.

### Effort estimates and calendar commitments

No production date is promised before measured M2 pilot effort, consistent with the existing contract. Track hands-on work, tool/build waiting, failed attempts, owner-review wait and rework by stage. After B1/B2, estimate UI/gameplay throughput from accepted work packages. After Bellback, estimate that family only; after Prism/Thimblewake, estimate their families separately. Schedule a bounded method proof for colony, serpent, cloak/spirit and translucent families before scaling them.

At every batch review, publish completed outcomes, remaining uncertainty, next critical dependency, measured effort to date, and the next bounded commitment. Participant recruitment, owner art decisions and remote hardware are explicit dependencies rather than invisible schedule assumptions. Reserve stabilization before beta and release based on observed defect/rework rates. Do not fill an uncertain plan with invented week counts.

### Existing verification entry points

These commands were located in the reviewed source; they were **not run in this planning task**. They are for the verified successor checkout after later authorization, not the historical local `main` as it stood during this task.

```powershell
python tools/vnext/catalog.py --check --stage
python tools/validate_kit.py
python -m unittest discover -s tests -v
python tools/build_documents.py --check
python tools/compile_catalog.py --check
```

Existing native runners are `tests/runtime/run_vnext_combat.ps1` (explicit fresh `-OutputDirectory`) and `tests/runtime/run_vnext_tournament.ps1` (`-Tournaments`, `-FirstSeed`, fresh `-OutputDirectory`). Inspect their current versions and tools before execution; use unique candidate directories. The reviewed tournament runner accepts seeds through 10000. The known laboratory launcher is `tools/unreal/launch_vnext_lab.ps1`, not a complete successor tournament frontend. B2 must supply and verify the actual new lifecycle launcher/package rather than pretending the lab already provides it.

Run focused checks for each change, then candidate-level regression when promoting behavior or content. Large frozen-candidate batches belong at deliberate balance/release checkpoints. Handler checks, headless simulation, real input journeys, human studies, art approvals and remote hardware tests each answer different questions; none replaces another.

## 13. End-of-batch decision form

At each review, answer these seven questions with evidence rather than percentage-complete estimates:

1. What can a player now do, understand, or choose that was previously missing?
2. Which exact candidate and control were tested, and which variables changed?
3. What passed technically, what failed, and what was not run?
4. What did external participants actually do, including assistance, losses and counterexamples?
5. Which design hypothesis survived, failed, or remains inconclusive?
6. Which original M0–M7 acceptance columns can change, and which remain open?
7. Is the next action to promote, revise, run another bounded experiment, stop the affected scope, or request a concrete owner decision?

The immediate recommendation for discussion is **B0 and B1 first**, while defining B2's interfaces and study access. B3 and broader content remain dependent on the observed player experience. Nothing in this plan starts that work automatically.

## 14. Sources and planning verification

The supplied GPT Pro text is the external review input. [Review notes](REVIEW_NOTES.md) records its original path, SHA-256, source assessment and decision register. Source links below pin the exact reviewed commit; re-verify current state before execution.

- [Adopted successor programme and original milestone meanings][contract].
- [Exact package and recorded implementation/human-gate handoff][handoff].
- [Implementation boundary matrix][matrix].
- [Gameplay, acquisition, relic, save and content contracts][combat].
- [Art, UI, accessibility and serial production requirements][art].
- [Validation targets, study sizes, remote progression and release requirements][validation].
- [Controlled sustain/charge investigation][timeouts].
- [Canonical authored/runtime catalogue][catalog] and [generated trait coverage][coverage].
- [Bellback reference packet and its human decision boundary][bellback].

Planning verification consists of reading the attachment, inspecting source/evidence at the pinned revision, cross-checking gameplay and art-state claims, mapping all three proposed batches to M0–M7, and checking the two planning documents for source links and internally consistent task/study gates. It does not certify any new runtime, art, balance, usability, performance, online or release result.

[contract]: https://github.com/TUPRAM/wonder-chess/blob/d80635f615810a93c3161c6bfd6c34c758b08260/docs/vnext/README.md
[handoff]: https://github.com/TUPRAM/wonder-chess/blob/d80635f615810a93c3161c6bfd6c34c758b08260/reports/vnext/IMPLEMENTATION_HANDOFF.md
[matrix]: https://github.com/TUPRAM/wonder-chess/blob/d80635f615810a93c3161c6bfd6c34c758b08260/docs/vnext/IMPLEMENTATION_MATRIX.md
[combat]: https://github.com/TUPRAM/wonder-chess/blob/d80635f615810a93c3161c6bfd6c34c758b08260/docs/vnext/PRODUCT_AND_COMBAT.md
[art]: https://github.com/TUPRAM/wonder-chess/blob/d80635f615810a93c3161c6bfd6c34c758b08260/docs/vnext/ART_UI_PRODUCTION.md
[validation]: https://github.com/TUPRAM/wonder-chess/blob/d80635f615810a93c3161c6bfd6c34c758b08260/docs/vnext/VALIDATION_AND_ROLLOUT.md
[timeouts]: https://github.com/TUPRAM/wonder-chess/blob/d80635f615810a93c3161c6bfd6c34c758b08260/reports/vnext/TIMEOUT_FINDINGS.md
[catalog]: https://github.com/TUPRAM/wonder-chess/blob/d80635f615810a93c3161c6bfd6c34c758b08260/data/vnext/catalog.json
[coverage]: https://github.com/TUPRAM/wonder-chess/blob/d80635f615810a93c3161c6bfd6c34c758b08260/docs/vnext/generated/coverage.json
[bellback]: https://github.com/TUPRAM/wonder-chess/blob/d80635f615810a93c3161c6bfd6c34c758b08260/art-source/asset-studio/wc_vn_bellback/inputs/references/r004_construction/README.md

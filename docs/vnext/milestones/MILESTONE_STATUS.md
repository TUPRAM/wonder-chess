# Milestone status and resume queue

## Latest presentation checkpoint — Storybook r20, 13 September 2026

The owner explicitly approved the preceding r15 slice ("I approve the slice") and authorized the larger current collection plus a native interface following the original REF02 image. The r20 candidate now contains all six portrait studies, six ability icons, twelve relic illustrations, matching live panels, a separate sanctuary painting, a perspective board, hero-specific cues and true merge/death presentation. Eight packaged graphical runs, two packaged contract suites, 230 Python tests/authoring checks, exact 122-source/49-payload identity and scoped physical input pass. Eighteen frozen gameplay/control files remain unchanged. All portraits/abilities/relics were viewed at native sizes. Expanded owner acceptance remains open; the 3D creatures are still proxies. This advances M2/B3 without closing B0–M7 acceptance, pacing or external studies. [Readout and launchers](../art/STORYBOOK_READOUT.md), [verification](../../../reports/vnext/milestones/storybook-20260913/verification.json).

**Development RESUMED on 13 September 2026 under the owner's explicit "Continue the work" instruction.** This is the current execution tracker. The pause record and r4 results remain historical evidence; the active next work is B1 diagnostic instrumentation/counter access and B2 input clarity/verification.

Current location: **B1/B2 engineering candidate**, with remaining M1/M3 features implemented and tested in scoped ways. B3 art has approved references but failed forms. Later M2–M7 product acceptance remains open. Independent M6 authority checks and M7 regression/identity checks are completed components, not acceptance of those later milestones.

## Preserved 2D planning and reference checkpoint — 13 September

The following describes the earlier planning-only stage. The owner subsequently approved the r15 slice and authorized the completed r20 expansion recorded above; statements about production not having started are historical.

The owner requested a full detailed2Dasset specification and several style-reference images, explicitly before production. The [master specification](../art/2D_ASSET_MASTER_SPEC.md), named-content and UI/environment/VFX appendices, generator briefs, full363-entry inventory and four reference themes are authored. Five1536×1024 PNGs preserve four themes plus the first UI-composition attempt. Source hashes, schema, IDs and local references were checked. No production asset, sprite conversion, Unreal import or new gameplay change occurred.

The plan retains3Dheroes and modular3Dboard geometry, with2Dportraits/icons/UI/materials/decals/effect components. It uses10bench slots,5shop offers,12actual relics and explicit current/future mechanic status. Owner selection/revision of these references is the next operation before a small integrated art sample. It is an M2 planning component; reference/forms/final-art approval and all existing milestone requirements remain open. The earlier positive owner review of r13 combat cues does not automatically approve these newly generated references.

Accessible review: [2D Asset Plan r001](../../../support/external/2D%20Asset%20Plan%20-%20r001/START_HERE.html).

## Latest component — combat clarity r13

**Owner review, 13 September:** "It looks good to me, what should we do next?" Positive owner acceptance of the prototype combat-presentation direction is recorded. No exact session duration, scenario/effect checklist or resolution was supplied; earlier automated/manual evidence remains separately scoped. Final character forms, external comprehension and balance/release acceptance remain open.

Recommended next three bounded batches: (1) B1/M3 diagnose capped tournaments on the frozen20-mana and clarity variants, then test one justified pacing change; (2) B2/M1 complete normal-speed solo journeys and targeted charge/push review, fix observed usability defects and prepare a clean study build; (3) B3/M2 deliver accepted Bellback forms and take that pilot through materials, rig, attack/hit/skill/death motion and packaged review before scaling the other art pilots. Owner solo feedback and the cap investigation can proceed independently. Keep the six-hero baseline until these results justify an ability/roster expansion.

The owner-requested attack/skill visualization is packaged for all six active successor heroes. Melee swings, ranged shots, effective healing, guard, charge aim/trail, Snapvine lash, Prism cross, tidal wave/push, active shields and head-top stun swirls now have distinct cues. The separate synthetic status test verifies actual status appearance and expiry without changing the roster. See the [readout](COMBAT_CLARITY_2026_09_13.md) and [r13 verification](../../../reports/vnext/milestones/combat-clarity-20260913/verification.json).

Use `Launch Combat Clarity.cmd`. The optional20-mana-based nearest-target/mobile-recovery rules retain attack intervals and committed casts. In20 development tournaments per arm, timeouts fall from14.883% to10.826%, but caps rise from4 to10. **Keep opt-in: pacing FAIL, human acceptance OPEN.** The original20-mana rules can be run in r13 for a visuals-only control.

R13 passes2 packaged contract suites (2,929 clarity +581 mana assertions),5 native/engine-reconciled tournaments (222 rounds /981 encounters),41 lab checks at720p and1080p,12 synthetic status checks,20 solo handler checks, stable61 build inputs and86-source/49-payload identity. The native suite passed25,385 assertions;230 Python tests and required authoring checks passed. Rendered cues were inspected; actual charge-displacement and push-displacement trail inspection remains open. The normal review launcher executed, then the owner stopped Computer Use with Escape before r13 physical input. This is a completed implementation/technical component, with manual review unfinished. It does not advance M2 art approval or close B1/B2/M3/M7.

Next: actual input and charge/push rendered checks; normal-speed readability comparison; investigate increased tournament caps before promotion. Continue B3 forms and the existing milestone order after those bounded studies as dependencies permit.

## Resumed engineering checkpoint

The default **r6** package adds an explicit selection prompt to the r5 preparation-feedback and diagnostic work. r6 passes 20 solo handler checks and ten packaged-engine tournaments reconciled across 427 rounds / 1,852 encounters; r5 separately passed 100 engine tournaments across 4,288 rounds / 18,685 encounters. That continuation preserved the catalogue and shared simulation; the later owner-directed opt-in mana experiment is recorded separately below. See the [continuation readout](CONTINUATION_2026_09_13.md), [B1 findings](B1_DIAGNOSTIC_READOUT.md) and [r6 verification inventory](../../../reports/vnext/milestones/resume-20260913/verification.json).

### Owner-directed three-hero mana experiment

The owner authorized mana for Snapvine, Prism Organ and Reefglass while preserving Bellback, Cragstoat and Root, damage, prices and targeting. The opt-in `mana100_v1` implementation uses zero starting mana, a 100-mana cast, 10 per landed basic and capped HP-loss charging. It adds a separate generated profile identity, live mana presentation and a separate default solo save. Original catalogue values and default activation behavior remain preserved. See the [exact contract and measured readout](MANA_EXPERIMENT_2026_09_13.md) and [experiment verification](../../../reports/vnext/milestones/mana-20260913/verification.json).

**The first tuning is REVISE, not promoted.** Across 100 tournaments per arm, caps increase from14 to25 and timeout rates from13.6580% to13.9963%. Across576 fixed encounters per arm, timeouts increase from24 to39 and406 pairs become longer. Position-dependent charging works, but signature abilities fire substantially later and less often. Both arms fail the existing pacing screen; no external playtest or enjoyment acceptance is implied. The owner subsequently authorized and completed the20-per-hit comparison recorded below.

The launcher selects the separate **r9 mana package** only with `-ManaExperiment`; its default remains r6. R9 passes445 packaged mana assertions,20 native/engine-reconciled tournaments across856 rounds /3,745 encounters,41 lab checks at both720p and1080p,20 solo handler checks, and exact82-source/49-payload package identity. Physical input is blocked by the Windows security dialog; no permission action occurred. r5/r6 clean-checkout and human-input evidence does not certify the new mana package. Remaining B1/B2 studies, full journeys, art and M2–M7 acceptance remain open.

### Completed follow-up:20 versus10 mana per hit

The opt-in **r10** package implements the authorized20-per-basic comparison for the same three heroes. Original catalogue values and the10-mana recipe are preserved; only the new recipe's basic-hit gain differs. All recorded10-mana CSV outcomes and activity rows reproduce exactly. See the [comparison and recommendation](MANA20_COMPARISON_2026_09_13.md) and [r10 verification](../../../reports/vnext/milestones/mana20-20260913/verification.json).

Across100 tournaments per arm, caps fall from25 to14, overall timeouts from13.9963% to13.8977%, and fixed-formation timeouts from39 to24 of576.407 fixed fights become shorter. Skills cast earlier and more often, but the protected/exposed first-cast median is equal for Prism Organ and Reefglass in the one-star fixtures. **Prefer20 for the next human mana playtest; keep opt-in, with pacing FAIL and human acceptance OPEN.** No third tuning or ability swap was implemented.

R10 passes230 Python tests and required authoring checks,22,456 native combat assertions,581 packaged mana assertions,20 packaged/native-reconciled tournaments across862 rounds /3,790 encounters,41 lab checks at720p and1080p,20 solo handler checks, and82-source/49-payload identity verification. Its physical-input attempt is blocked by the Windows firewall prompt; no security action occurred. Use `-Mana20Experiment` to launch r10. Earlier default packages and their evidence remain preserved; r10 clean-checkout/clean-machine/human/release gates remain open.

B1 now includes two 100-tournament diagnostic arms, explicit charge/grove accounting, recruitment observations, 400 normal-command acquisition trials and a 384-encounter ordering/approach follow-up. Root75 remains rejected. A four-gold army price does not guarantee four-gold acquisition, and one fixed-seed width victory does not transfer reliably across acquired identities and orientation. The follow-up is completed evidence; no new balance candidate was promoted.

r5 actual input passed nine scoped cases with 23 screenshots: relic draft/equip/unequip, an equipped three-copy upgrade, keyboard movement/facing, save/exit/cold resume, normal-speed loss and combat purchase cutoff, and content-version mismatch feedback. It also exposed the unselected-inspector clarity defect fixed in r6. Full-bench and all-resolution complete lifecycle journeys remain open. r6 actual input currently awaits manual dismissal of a Windows firewall dialog; no security UI action was performed.

Both r5 and r6 independent clean-checkout builds, exact archive identity and ten-tournament engine checks passed. r6 uses local snapshot `b0cc92571735f74a01592f01e018f2d9bbd13b68`, with all 80 build-source inputs identical before building; its 427 rounds and1,852 encounters reconcile against native results. Initial r5 checkout failed on archived long paths, recovered with command-scoped Git support. These are same-machine project-checkout tests, not independent clean-machine installations.

The active implementation checkout remains uncommitted and unpublished. Local r5/r6 build-snapshot branches preserve their sources independently of the active index and were not pushed. Raw evidence, failed candidates and art approvals are preserved.

## Complete milestone list

| Milestone | Current status | Completed work | Remaining work to close it |
|---|---|---|---|
| B0 — Decisions and evidence contract | Engineering/protocol work delivered; logistics open | Verified successor lane/control, D01–D09 defaults, study definitions, ownership, holdout seeds 900001–900250 reserved and unused | Confirm actual external participant/device availability; decide any later release/comparative scope amendments before those gates |
| B1 — Formation agency and pacing | Technical work delivered; balance FAIL; human NOT_RUN | Six A/B pairs, mirrored scenarios, diagnostic traces, prior 1,000-per-arm experiments, new 100-per-arm diagnostics, 400 acquisitions and 384 ordering/approach encounters | External comprehension/acquisition/formation study; use cap and opportunity findings to justify one bounded interaction candidate;5 external formative participants and held-out confirmation only when warranted |
| B2 — Recruitment and adaptation | Solo engineering candidate delivered; acceptance open | Shop/bench/copies/merges/economy/XP, facing/deployment, public scouting, relic draft/inventory policy, real tournament lifecycle, atomic preparation saves and cold resume, scoped real input | Full pointer/keyboard journeys at3 resolutions including full bench, relic draft/equip, phase cutoff, loss/spectate/final results/restart; clearer feedback/onboarding; current-candidate clean-build verification before external distribution;5 eligible first-use participants; acquisition/adaptation evidence |
| B3 — Small composition experiment and art pilot | Reference accepted; forms ART_REVISE; traits waiting | Bellback exact reference approval, dorsal-bell prose revision, 3 actual forms attempts and method review; no trait activation | Bounded Beast 2 contract and trait-off/on comparison after acquisition evidence; Plant waits for accepted sustain/finite budget; approved Bellback forms then full pilot pipeline; restrained Wondergrove presentation;12 external participants |
| M0 — Successor foundation | Historical contract/catalogue delivered | Six-creature control and authored successor backlog retained; versioned solo catalogue and explicit execution decisions | Resolve later owner choices without rewriting historical acceptance; authored content is not runtime content |
| M1 — Core laboratory/preparation experience | Engineering components delivered; human acceptance open | Formation workbench and complete solo preparation frontend; inspection, previews, factual recap and private/public boundaries | Close relevant B1/B2 comprehension, adaptation and full-input gates |
| M2 — Coherent visual slice | 2D/UI r20 component verified; 3D forms and owner acceptance open | Shared direction and Bellback exact references; owner-approved r15 slice; six portraits/abilities, twelve relics, reference-inspired native interface and event-driven effects packaged/tested | Owner review of expanded 2D/interface; accepted Bellback, Prism Organ and Thimblewake pilots; geometry→topology→UV/material→rig/weights/sockets→motion/VFX/audio→LODs→Unreal/package; Wondergrove slice; visual study, localization/accessibility; separate human approvals |
| M3 — Lifecycle and pacing | Saves/lifecycle tested; pacing FAIL | Actual off-screen combat, standings/elimination/restart, preparation recovery, native/package consistency | Accepted timeout/cap behavior;5 complete normal-speed human tournament observations with pause/elimination/final-winner endpoints separate; full lifecycle control journeys |
| M4 — Evidence-earned ecosystem | Not promoted | Six active heroes,12 relics,7 neutral definitions / 12 waves remain the bounded control;18 traits inactive | Freeze earned roster; practical early counters/acquisition; bounded hero/trait/entity contracts; useful/unfavorable formations; real neutral teaching behaviors; full art and ecosystem acceptance; avoid arbitrary14/24hero promotion |
| M5 — Solo beta/repeat use | Not entered; study tools ready | Preregistered study tool, assistance-aware scoring and5 empty CSV templates; reliable solo components | Accepted visual/pacing/content entry gates; onboarding/sandbox/bestiary/settings/accessibility/localization; history/mastery as justified;12 external participants across separate days; losses/adaptation/fatigue/voluntary replay evidence |
| M6 — Remote beta | Native prerequisites tested; remote path incomplete |248 native authority/privacy/replay/takeover assertions across2H6B / 4H4B / 8H0B;6 static checks; protocol 6 and facing transport fixes | Source-engine dedicated server, authenticated session/service path and successor online frontend; independent devices; human-operated remote2/4/8-seat whole matches; mismatch/reconnect/latency/crash/abort tests; explicit authorization before paid/public service work |
| M7 — Release candidate | Exact-build technical checkpoint passed; release NOT_ACCEPTED | r4/r5/r6 archives and exact manifests;1,000 native reference +100 r5 engine reconciliation; r6 targeted regression; r5/r6 clean checkouts, source snapshots and independent archives; scoped input | Accepted intended release scope; final-candidate clean-checkout evidence; independent clean-machine installation; final-content20-unit/effects/permitted-entity 1080p performance and named hardware; required art/human/remote gates; owner release approval;30-personcomparison if adopted as release gate |

## Ordered work after resume

Checked items below mean a component was actually completed, not that the corresponding milestone is accepted.

### 0. Protect the checkpoint

- [x] Preserve registered branch, uncommitted code, generated assets, raw successful/failed experiments, r1–r4 archives and Bellback r001–r003 sources.
- [x] Record exact r4 source/runtime/executable identity, final tests and current pause.
- [x] Verified the resumed worktree/branch and historical pause record; the r4 manifest passed again on 13 September before source changes. Do not automatically rebuild or rerun 1,000 seeds if nothing changed and no new concern warrants it.

### 1. Finish B1's bounded pacing investigation

- [x] Compare Root75 with frozen control without silently promoting it.
- [x] Keep unused confirmation seeds 900001–900250 reserved.
- [x] Classify cap-heavy survivors/compositions and effective-heal/overheal patterns; separate combat timeouts from tournament caps and neutral effects.
- [x] Add authoritative charge opportunity/commitment/release/cancellation reasons and grove pulse outcomes; every commitment and event stream reconciles in two new 100-seed arms.
- [x] Execute early counter acquisition/copy/reroll/affordability trials with ordinary commands, and retain failed acquisitions and formation losses. Human acquisition/adaptation remains open.
- [x] Complete a bounded ordering/approach experiment before changing combat: three orderings, two placements, two orientations and32 development seeds. No runtime rule change was justified or promoted.
- [x] Execute the owner-directed three-hero mana experiment with protected catalogue values,100 tournaments and576 fixed encounters per arm. Retain this first tuning as opt-in REVISE; reserved holdouts remain unused.
- [x] Execute the authorized20-versus10-per-basic follow-up with exact10-mana reproduction,100 tournaments and576 fixed encounters per arm, native/packaged contracts and rendered lab/solo exercises. Prefer20 for human testing; pacing still fails and the first-cast exposure tradeoff weakens. No automatic promotion.
- [ ] Use human comprehension and pacing evidence to select at most one further interaction candidate; stop if timeout/cap behavior remains unacceptable.
- [x] Run native/engine/event reconciliation for instrumentation and package checks for feedback changes. Holdouts remain unused; current pacing still fails.

### 2. Finish B2 input clarity and full journeys

- [x] Actual three-copy upgrade, board deployment/keyboard move, XP purchase/rejection, scout privacy/return and cold preparation resume observed.
- [x] Existing-save choice now blocks orders and prevents accidental checkpoint replacement; exact same-handler restore passed.
- [x] Improve purchase/merge, XP, placement and relic feedback and distinguish captain HP from creature damage in recap. r5 real relic/upgrade/placement/save inputs passed; r6 fixes the unselected inspector found in that review.
- [ ] Complete real-input full-bench merge, facing, relic draft/inventory/equip/unequip, rejected commands/phase cutoff, eliminated-player spectating, final results and restart at 1280×720, 1600×1000, 1920×1080.
- [x] Verify actual content-version mismatch through r5 Load at1920×1080 with a checksum-valid old-version copy; specific rejection, unchanged live state and original valid saves preserved.
- [x] Establish an independent r5 Git-checkout build, exact80-source parity and reconciled ten-tournament engine check.
- [x] Complete r6 independent-checkout build, 81-source/49-payload identity verification and ten-engine-tournament reconciliation after the inspection correction. Independent clean-machine installation remains open.

### 3. Collect B1/B2 human evidence

- [x] [Human study kit](HUMAN_STUDY_KIT.md), preregistration/eligibility/assistance rules and empty intake templates prepared; no participant data invented.
- [ ] Schedule5 external B1 participants with genre experience recorded; prediction→normal-speed observation→explanation before recap→independent revision.
- [ ] Schedule5 eligible first-use Wonder Chess B2 participants; returning B1 users do not become new first-use observations. Record independent versus assisted task outcomes and 3 unfamiliar explanation encounters/person.
- [ ] Capture acquisition/adaptation after scouting and losses, plus5 complete normal-speed tournament-to-final-winner observations. Do not replace human durations with the accelerated 31.361-minute bot median.
- [ ] Record accept/revise/inconclusive separately for comprehension, acquisition and pacing; continue only the components whose dependencies passed.

### 4. Change Bellback's art method and complete B3

- [x] Owner exact r004 reference acceptance recorded; brief/reference seals remain current.
- [x]3 actual Blender forms candidates saved/reopened/rendered; latest shape quality ART_REVISE, all sources retained.
- [ ] Use focused sculpt control for face/root planes/support integration. Preserve the approved 2.2 m crown, dorsal bell, toe count and branch; do not conceal mismatches by shrinking the bell.
- [ ] Internally review actual clay/closeup/crowded views; seek owner forms approval only for an internally adequate exact candidate.
- [ ] After acceptance, advance topology, UV/material, rig/weights/sockets, continuously reviewed motion, LODs, exports, Unreal and packaged review in order.
- [ ] Define and compare bounded Beast 2 after acquisition evidence. Plant remains inactive until sustain and finite budget/reset rules are accepted. No global trait activation.

### 5. Complete M2/M3, then earn M4/M5

- [ ] Complete the remaining two art pilots, Wondergrove and their12-person visual/comprehension study.
- [ ] Close lifecycle/control gaps and human pacing; do not add waiting to manufacture a duration target.
- [ ] Promote each new hero/trait only after a concrete tactical/acquisition gap, distinct counterplay and accepted production method justify it. Include neutral teaching behaviors and actual reward flow.
- [ ] Freeze a bounded solo-beta roster; complete onboarding/bestiary/accessibility/settings and appropriate progression. Run12-person repeat-use observations across separate days, retaining losses and optional replay behavior.

### 6. Complete M6 remote prerequisites and journeys

- [ ] Verify source-engine/dedicated-server and authenticated-service prerequisites; do not treat native multi-seat fixtures as real remote operation.
- [ ] Implement and validate the complete successor online path, then proceed local multi-process→remote2H6B→remote4H4B→remote8H0B with independent devices and real human operators.
- [ ] Close privacy/ownership/reclaim, mismatch, network impairment, interrupted match and abort diagnostics; no silent fabricated results or online-origin offline saves.

### 7. Freeze and verify M7 on the accepted release scope

- [x] Current six-creature r4 technical sample:1,000 native / 100 engine, exact source/payload binding and deterministic reconciliation passed.
- [ ] Re-freeze actual final content/protocol and collect new evidence when changes invalidate this checkpoint; the current six-creature results cannot certify expanded content.
- [x] Complete independent clean-checkout builds for the current six-creature r5/r6 study candidates; preserve snapshots, archives and engine reconciliation.
- [ ] Complete independent clean-machine install, settings/save/result/restart and required remote regressions for the accepted intended release content.
- [ ] Measure real final content at 20 deployed units with allowed entities, busy effects and actual off-screen fights on named hardware; establish minimum specs from evidence.
- [ ] Obtain exact required art/release approvals and external-user acceptance. Decide the30-participantcomparative gate before running it. Publication is a separate explicit action.

## Numerical checkpoint and evidence

Unchanged solo catalogue: `wonder_vnext_solo_0.1.0`, SHA-256 `6e80932173071ef05e58d90a44db3490cfcfde86d48edf33f4a940ff1748efa0`. Native 1,000: 186,984 encounters, 26,219 timeouts (14.0221%), 187 caps, 31.3608-minute median accelerated simulation. PvP 22.9497% and ghost 39.3683% each fail the below-2% screen; neutrals 0 / 77,903. No human duration/enjoyment conclusion follows.

Evidence: [implementation readout](IMPLEMENTATION_READOUT.md), [current verification inventory](../../../reports/vnext/milestones/resume-20260913/verification.json), [current ledger](../../../reports/implementation_state.json), [B1 scenarios](B1_SCENARIO_EVIDENCE.md), [M6 engineering](M6_ENGINEERING_EVIDENCE.md), [M7 engineering](M7_ENGINEERING_EVIDENCE.md). The ledger retains prior candidate/top-level records separately so older results cannot silently certify the current candidate. Frozen r4 verification remains preserved separately.

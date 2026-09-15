# Wonder Chess — notes on GPT Pro's critical review

Prepared 12 September 2026, Asia/Singapore. Status: **DISCUSSION DRAFT — planning only**.

Companion: [Detailed development milestones](DEVELOPMENT_MILESTONES.md).

## Recommendation

Continue the successor project and preserve its technical foundation and mythic-storybook direction. Make the next investment prove a player can understand a loss, acquire a practical response, change a formation, and want another attempt. Sequence the next work as **formation comprehension → complete solo recruitment/adaptation → a bounded trait experiment and Bellback art pilot**. Expand content after those experiments identify an actual missing decision.

This is a proposal for discussion. It does not adopt new tuning, activate traits, approve art, close existing milestones, or authorize implementation. The adopted M0–M7 programme remains the product authority. The next three batches divide work within that programme; they do not replace it.

## Source and version boundary

The user supplied GPT Pro's review as an attachment. Its SHA-256 is `8f781361468162384876025214a0a01183867ec6015898097a33018121675a7e`; the original is [pasted-text.txt](<C:/Users/iputu/.codex/attachments/a14a1a9b-6b81-40c9-941a-414e1b99878d/pasted-text.txt>). GPT Pro describes a source-and-evidence review, without launching the package, rerunning tests, or visually approving image binaries.

I read the prescribed successor documents and recorded evidence through local Git objects, and cross-checked focused gameplay claims against source. The reviewed commit is **`d80635f615810a93c3161c6bfd6c34c758b08260`**. During this planning task, `git ls-remote` confirmed both GitHub `main` and `codex/wonder-vnext` at that commit. Local `codex/wonder-vnext` also matches it.

The current working checkout is different: local `main` remains at `9623fd82f98ff80a90985b9f552d8851ccece30f`, with pre-existing untracked `art-source/asset-studio/` and `reports/vnext/`. No checkout switch, synchronization, branch creation, staging, commit, or push was performed. These documents live under Project Support to avoid placing successor planning into the historical checkout. Re-verify the canonical development checkout before any later implementation or integration of these notes.

All existing game-test counts below are **recorded results inspected at the reviewed snapshot**, not new execution in this task. No package, combat test, player study, art review, or performance measurement was run here. Git publication identity and the earlier package's dirty-checkpoint provenance are separate records; publication does not retroactively establish a clean build.

## What to preserve and what still needs proof

| Area | Evidence at the reviewed snapshot | What the next plan must not assume |
|---|---|---|
| Gameplay | Six executed mechanics and a packaged formation/replay laboratory | Understandable play, varied teams, accessible counterplay, enjoyment |
| Tournament | Native economy, shops, merges, eight seats, bots, actual off-screen combat, ghosts, neutrals, elimination, restart | A complete successor player journey |
| Roster | Fourteen authored dossiers; six active creatures | Fourteen playable creatures or a final roster cap |
| Traits | Nine race and nine class designs; zero runtime traits | An implemented ecosystem or reachable class choices |
| Relics | Twelve executable transformations and native draft/equipment lifecycle | Twelve distinct strategic experiences or a usable draft interface |
| Recovery | Versioned, validated preparation snapshots and deterministic resume API | Durable disk saves and packaged crash/relaunch recovery |
| Art | Owner-selected shared direction; Bellback reference candidate; Prism reference revision required | Approved successor models, animation, audio, or a complete visual slice |
| Validation | 1,000 native tournaments and 100 packaged tournament reconciliation; focused combat and authoring tests | Human usability, repeat play, clean-machine installation, remote multiplayer, or release acceptance |

Sources: [successor contract][contract], [handoff][handoff], [implementation matrix][matrix], [coverage][coverage].

## Review findings to carry forward

### 1. Formation depth is the central product hypothesis

The six mechanics differ, but this does not establish six strategic choices. Bellback, Grandmother Root, and Prism Organ may converge on one protected firing position. That is a credible hypothesis drawn from their relationships, not a demonstrated dominant composition. Require three contrasting plans to survive controlled tests: protected firing, approach pressure, and screen-breaking/displacement. Each needs a favorable situation, a counter, and a reason to switch.

Test the same army and investment with only a positional change. Ask the player to predict, watch at normal speed, and explain before revealing a recap. Movement should make the outcome understandable even when it changes the original preparation relationship. Bellback's selected protection recipient and transfers need clear feedback. Directional signature behavior is material for Bellback and Reefglass; rotation should not imply equivalent tactical depth for all six creatures. Sources: [combat contract][combat], [dossiers][heroes], [simulation source][simulation].

### 2. Counter availability matters as much as counter existence

Root is cost 2. Reefglass is the only active displacement creature, costs 5, and cannot appear before level 7. At level 7 the cost-5 probability is 1% per slot. With five independent slots and exactly one enabled cost-5 creature, the chance of at least one Reefglass is `1 - 0.99^5 = 4.90099501%` per refreshed shop. This calculation excludes affordability, XP investment, time to reach that level, and opportunities forgone. It is not a measured acquisition rate. [Canonical catalogue][catalog], [shop implementation][tournament].

There is a second early-access issue: Snapvine first enters the shop at level 4 and Prism at level 5. Test the cost-1 tools and ordinary placement against early Root as well as the later angles/artillery answers. Record what was offered, what the player could afford, and what was bought. Usage without exposure cannot distinguish weak design from unavailable opportunity.

Manyfoot is a conditional candidate for affordable screen bypass. It should receive one logical unit/one health pool in a combat prototype before colony art. Do not automatically add it, but do not turn the six-creature control into a permanent constraint if two disciplined experiments show a missing early response.

### 3. Separate sustain tuning from Cragstoat's placement policy

The recorded final sample has 26,434 timeouts in 187,141 encounters (14.125%) and 199 round-capped tournaments. This fails the proposed below-2% timeout target. Median 31.332-minute accelerated bot duration does not establish the 35–45-minute human target. [Final analysis][analysis], [validation contract][validation].

The investigation associates sustained healing with long fights, but it does not isolate Root's causal contribution. Test the proposed 75% Grove pulse candidate with timing and geometry unchanged. Separately test human-designed Cragstoat approaches before changing bot scoring or charge damage. The current bot score rewards forward deployment and checks an adjacent friendly-clear cell; it does not adequately model approach distance, enemy contact, or legal landing opportunity. [Timeout findings][timeouts], [bot/tournament source][tournament].

One source nuance belongs in the implementation brief: Cragstoat does not always require completed movement before it can charge. A valid nonzero charge landing path can contribute momentum; an adjacent target needs prior momentum for the adjacent charge case. Inspect commitment, landing, momentum, and failure reasons rather than treating all non-charges as one defect. [Simulation source][simulation].

### 4. Deadline adjudication needs an explicit product decision

`Combat::Assess` compares the sum of surviving units' remaining-health fractions, using integer common-denominator arithmetic. Full-health survivors each contribute equally to this score, regardless of cost or star investment. This is an actual victory rule whenever combat reaches the deadline. It must be explained and tested as such. [Simulation source][simulation].

Recommended decision: treat elimination as the intended primary outcome and deadline adjudication as a transparent bounded fallback for the next study, retaining the existing rule in the control. If preservation-at-deadline is intended as a supported strategy, document and balance that deliberately. Any new adjudication formula or overtime rule must be a separate experiment. Longer timeouts are not a neutral adjustment: the recorded 45→90-second probe changed the winner. [Timeout findings][timeouts].

Predefine timeout denominators. Report PvP, ghost, and neutral rates separately as well as the aggregate; easy neutrals must not conceal stalled player battles. Report elimination wins, deadline wins, ties, round caps, and survivor investment separately.

### 5. Traits must create a choice, not merely reward roster completion

Only Beast 2 and Plant 2 are reachable with the six active creatures. No class threshold is reachable. Across all fourteen authored dossiers, Warrior still has two members against a first threshold of three, and Mage one against three. An authored threshold is not an executed behavior. [Catalogue][catalog], [coverage][coverage].

Beast 2 is the first proposed experiment, with charge-triggered bounded movement, explicit recipients, expiry, and no recursive triggers. Investigate whether it disrupts Bellback's protection relationship. Plant 2 follows only after sustain is understood. The proposed finite setup-protection budget is a design amendment to settle explicitly, not a silent interpretation of the existing trait prose.

Test pairs in three-to-five-slot decisions. With room for all six, completing both pairs can become automatic. Players should sometimes choose a pair and sometimes reject it for another tactical tool. Even successful pair experiments do not close the full ecosystem gate. A class bridge such as Kilnback must earn its own gameplay role before Guardian activation is considered.

### 6. Recruitment and relics need a usable adaptation loop

Retain independent shops for the first study. This keeps the adopted rule stable and lets scouting prove value through tactical adaptation. A shared pool would introduce recruitment denial and change the product promise; it is not an automatic repair for weak shop decisions.

Use authoritative transactions to expose the shop, exact owned copies, upgrades, bench, XP, rerolls, lock, buy/sell, facing, public scouting, relic draft/inventory, results, and restart. Save/resume needs actual files, interrupted-write handling, previous-save preservation, clear errors, and package relaunch tests. [Combat contract][combat], [matrix][matrix].

Relic eligibility currently checks the enabled catalogue, not the owned roster. Proposed policy: include at least one compatible owned-team option when possible, counting deployed and benched recruits; label speculative options. Define empty-team/no-compatible cases and the selection timing before changing the policy. Broad Canopy increases Bellback's eligibility radius but still supports one selected ally. Mechanic-specific descriptions should explain effective changes and drawbacks, including charge momentum scaling. [Relic catalogue][relics], [simulation][simulation], [tournament source][tournament].

### 7. Preserve art direction, prove production at the gameplay camera

Do not reopen the whole aesthetic because the pipeline is unfinished. Bellback's dorsal bell must coexist with readable facing, recipient indication, neighboring units, and one-cell interaction bounds. Evaluate normal-speed crowded combat early, before expensive surface polish. Prism's ordered beams and Thimblewake's limbs have different readability risks. [Art/UI contract][art].

Bellback's formal reference decision remains pending against the sealed 27-artifact snapshot `83de2292eeb1195963b1d479e194be171a87dd3c5eb960d47de870250fb2f842`. The shared direction selection is not per-asset reference or forms approval. Prism's first reference remains `ART_REVISE`. Reconcile dorsal-bell art with chest-bell catalogue prose in a deliberate content revision and regenerate its identity. Do not alter the frozen package's description in place. [Handoff][handoff], [Bellback reference packet][bellback].

One complete Bellback pilot is a useful near-term result. M2 still requires three serial pilots, Wondergrove, full preparation/combat/recap presentation, motion, audio, and measured performance. Colony, serpent, translucent, and cloth-like families need their own method proofs; one quadruped cannot establish a universal time-per-creature estimate.

### 8. Preserve the architecture and test integration boundaries

Keep authoritative C++ combat, shared deterministic geometry, native tournament simulation, generated catalogue identity, effective relic evaluation, and the snapshot foundation. A broad rewrite is not justified by this review.

Each new mechanic needs one integration checklist across source generation, targeting, movement/commit/release/interruption, event reporting, preview, recap, bots, saves, and packaged replay. Released damage packets can survive source defeat; Root's healing areas have a tethered lifecycle. Tests must respect these different contracts rather than asserting that all persistent effects survive defeat. Source consistency does not prove a clean build, performance, or enjoyment. [Simulation source][simulation], [validation contract][validation].

## Decisions to resolve before the affected work

All recommendations below are **PROPOSED**, not adopted decisions.

| ID | Decision | Recommended starting position | Needed before |
|---|---|---|---|
| D01 | Deadline victory purpose and comparison metric | Elimination primary; visible fallback; keep existing rule in control | Balance candidate promotion and final recap copy |
| D02 | Six-creature scope and counter-access exception | Six as control; one explicit prototype only if evidence shows a missing decision | Roster changes |
| D03 | Promotion thresholds and study scoring | Predeclare denominators, held-out seeds/formations, tasks, and rubric | B1 experiments and participant sessions |
| D04 | Scouting updates and cutoff | Live public view with viewed seat/round/revision, return action, and common cutoff | B2 scouting implementation |
| D05 | Relic draft usefulness | At least one owned-team compatible option when possible; explicit fallback | B2 draft policy change |
| D06 | Beast/Plant behavior limits | Beast first; Plant only after sustain, with explicitly chosen finite budget/reset rules | B3 trait implementation |
| D07 | Exact Bellback reference and wording | Per-asset reference decision; deliberate versioned prose correction | Complex modeling/content revision |
| D08 | Duration and elimination experience | Measure meaningful time and repetition; keep 35–45 provisional; allow spectate/exit/restart | M3 pacing acceptance and M5 |
| D09 | Study access, owners, and effort budget | Identify external participants, moderator, target machine, and per-stage ownership; no dates before pilot data | Scheduling sessions or promising delivery |

## How this plan refines GPT Pro's recommendation

1. **Keep independent progress possible.** A failed sustain experiment blocks promotion of that tuning, not the scenario browser, accessible controls, save UI, or all art work. A critical crash/data-loss defect blocks the affected build or study.
2. **Do not silently close M2 or M3.** Bellback alone is partial M2. A functional six-creature tournament closes tested lifecycle work but leaves measured human pacing and full-content acceptance open.
3. **Separate small-study results from population claims.** Four of five is a practical formative checkpoint. Report individual results and novice/experienced denominators; it is not proof that 80% of future novices will succeed.
4. **Keep a narrow escape from the six-creature experiment.** If existing tools cannot supply affordable counterplay, decide whether to revise targeting/movement or test one missing tool. Do not compensate with a large roster.
5. **Make testing proportional.** Use focused fixtures while iterating, broad frozen-candidate regressions at promotion, and external studies for experience. Repeating 1,000 seeds after every text/UI change does not create useful evidence.

The proposed milestone document supplies the work packages, dependencies, measurements, human tasks, acceptance boundaries, and stop criteria. Its completion statuses remain proposed; the actual implementation ledger was not advanced.

[contract]: https://github.com/TUPRAM/wonder-chess/blob/d80635f615810a93c3161c6bfd6c34c758b08260/docs/vnext/README.md
[handoff]: https://github.com/TUPRAM/wonder-chess/blob/d80635f615810a93c3161c6bfd6c34c758b08260/reports/vnext/IMPLEMENTATION_HANDOFF.md
[matrix]: https://github.com/TUPRAM/wonder-chess/blob/d80635f615810a93c3161c6bfd6c34c758b08260/docs/vnext/IMPLEMENTATION_MATRIX.md
[combat]: https://github.com/TUPRAM/wonder-chess/blob/d80635f615810a93c3161c6bfd6c34c758b08260/docs/vnext/PRODUCT_AND_COMBAT.md
[heroes]: https://github.com/TUPRAM/wonder-chess/blob/d80635f615810a93c3161c6bfd6c34c758b08260/docs/vnext/generated/hero_dossiers.md
[catalog]: https://github.com/TUPRAM/wonder-chess/blob/d80635f615810a93c3161c6bfd6c34c758b08260/data/vnext/catalog.json
[coverage]: https://github.com/TUPRAM/wonder-chess/blob/d80635f615810a93c3161c6bfd6c34c758b08260/docs/vnext/generated/coverage.json
[relics]: https://github.com/TUPRAM/wonder-chess/blob/d80635f615810a93c3161c6bfd6c34c758b08260/docs/vnext/generated/relic_catalogue.md
[timeouts]: https://github.com/TUPRAM/wonder-chess/blob/d80635f615810a93c3161c6bfd6c34c758b08260/reports/vnext/TIMEOUT_FINDINGS.md
[analysis]: https://github.com/TUPRAM/wonder-chess/blob/d80635f615810a93c3161c6bfd6c34c758b08260/reports/vnext/native/final-analysis.json
[validation]: https://github.com/TUPRAM/wonder-chess/blob/d80635f615810a93c3161c6bfd6c34c758b08260/docs/vnext/VALIDATION_AND_ROLLOUT.md
[art]: https://github.com/TUPRAM/wonder-chess/blob/d80635f615810a93c3161c6bfd6c34c758b08260/docs/vnext/ART_UI_PRODUCTION.md
[bellback]: https://github.com/TUPRAM/wonder-chess/blob/d80635f615810a93c3161c6bfd6c34c758b08260/art-source/asset-studio/wc_vn_bellback/inputs/references/r004_construction/README.md
[simulation]: https://github.com/TUPRAM/wonder-chess/blob/d80635f615810a93c3161c6bfd6c34c758b08260/game/Source/WonderChessRuntime/Private/Simulation/WonderSimulation.cpp
[tournament]: https://github.com/TUPRAM/wonder-chess/blob/d80635f615810a93c3161c6bfd6c34c758b08260/game/Source/WonderChessRuntime/Private/Simulation/WonderTournament.cpp

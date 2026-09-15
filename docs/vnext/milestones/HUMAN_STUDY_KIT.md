# Human study kit — B1 through release evidence

Version `wc-human-study-1`, prepared 12 September 2026 under `B0_EXECUTION_CONTRACT.md`. **No participants have been enrolled or observed by this kit. All supplied CSVs are empty.** The implemented tool validates observations supplied later; it does not certify a participant's explanation, contact anyone, or approve a milestone.

The B0 cohort sizes and thresholds remain fixed. This document specifies the task order, observation unit and scoring details before collection. A changed rule, candidate or answer key requires a new registered study; preserve the prior study and report the amendment. Do not revise an unsuccessful primary task into an exploratory task after seeing its result.

## Operator preparation and privacy

Assign three responsibilities before the first participant: a moderator, a package/build operator and a scoring reviewer. Record them as local `R###` IDs. One person may moderate and operate, but have a second reviewer adjudicate primary explanation/revision scores from the frozen rubric and original evidence. Record unresolved disagreement and treat the affected criterion as inconclusive until reviewed. Owner/developer practice sessions are supplementary.

This initial protocol enrolls consenting adults who self-confirm that they are at least 18; record only `adult_eligible=yes`, not a birth date. An external participant is neither the owner, a project developer, nor an automated agent. For B2's primary cohort, **novice means zero previous Wonder Chess play sessions**, not zero auto-battler experience. Returning B1 participants may supply supplementary B2 observations and must not fill its first-use slots.

Record genre experience separately: `newcomer` means zero through two completed auto-battler tournaments before enrollment; `experienced` means three or more. This is an operational experience band, not a skill claim. Plan three newcomers and two experienced participants for each five-person cohort where available; both groups must be represented. If recruitment produces a different eligible composition, report its actual counts. The tool will not call a single-experience cohort complete.

Use local participant IDs `P001`, `P002`, etc.; local sessions `S###`, observers `R###`, hardware `H###`, matches `M###` and duration observations `D###`. Reuse a person's ID across sessions and study recruitment records. A second visit is never a second person. Each study has its own directory and five preassigned primary cohort slots; a slot cannot be reassigned after reviewing results. Slot `0` is supplementary. If someone withdraws, stop their session and honor the agreed removal request; disclose anonymous attrition and leave the primary sample incomplete. A replacement needs a prospectively registered cohort amendment, not reuse of the withdrawn result's slot.

Keep enrollment/contact mappings, consent records and raw recordings under local application data, outside Git; for example `C:/Users/iputu/AppData/Local/WonderChess/Studies/<study-id>/`. This kit neither creates contact records nor supplies fictitious consent. The repository templates are schema examples only. Before enrolling, tell participants who can inspect the local notes, whether optional screen/audio recording is requested, the deletion/withdrawal route, and a specific retention end date. A proposed operational default is deletion of raw recordings and contact mappings 30 days after study close, retaining only anonymous aggregates; confirm the actual promise before collection. Record no account credentials, private messages, names, email addresses, exact birth dates or unrelated desktop content in study CSVs.

Suggested invitation/consent script for the human moderator, only when contacting participants is separately authorized:

> We are evaluating the game and its controls. You may stop, skip an activity or take a break. A loss is useful feedback. We record what happened and your explanation under a local code. Recording is optional and has its own consent choice. We will explain who sees the notes and when they are deleted. Your decision to continue or replay is optional.

Do not ask an agent to impersonate a participant. Do not use participation, scheduled attendance, repeated trials, a signed form or a favorable questionnaire as proof of enjoyment.

## Freeze the candidate and scoring inputs

1. Copy the empty `reports/vnext/milestones/study-templates/` files into the local study directory. Preserve the templates empty in Git. Complete a separate directory and protocol for B1 and B2.
2. Record the exact source commit, package SHA-256 and content digest. The study is invalid if a patched package or a new tuning profile is silently substituted between people. Preserve package command line, display size, hardware/settings and normal-speed verification in a locally identified hardware/session record.
3. Prepare unfamiliar formation files and moderator-only answer keys. A fixture's exact roster, stars, relics, cells, facing and seed must be retained. Use original saved `.wcf` files plus actual engine event logs; no inferred alternative outcome. Record their relative paths and SHA-256 values in `scenarios.csv`.
4. The six built-in F01–F06 pairs are useful development/control examples. An unfamiliar primary encounter must not be an answer already demonstrated to that participant. Do not merely rename the demonstrated arrangement. Freeze a materially different legal arrangement, verify it with real combat, identify its valid event-based scoring conditions, then assign its scenario ID. F04 side sensitivity and F03's stronger separated Root position must remain visible in the answer key.
5. Register `protocol.json` before the first session: fill `registered_utc`, anonymous `registered_by`, source/package/content identity and SHA-256 of the final `scenarios.csv`. Preserve the fixed B1 primary-task allocation. Calculate the complete protocol file hash and record it in every session row. Changing the scenario/answer-key registry or protocol after sessions begin is rejected by the validator.
6. Check the participant's self-reported prior exposure to the exact study scenarios. A disclosed previously seen formation is not unfamiliar. Use the registered alternate input if one was assigned prospectively; otherwise mark the affected task invalid/not run and retain the limitation.
7. Run a moderator rehearsal with a developer under supplementary slot `0`. Rehearsal checks controls and logging; it supplies no external-human gate evidence. Freeze the procedure before external collection.

An answer-key file should contain: scenario/task ID, fixture identity, preparation screenshot or cells, observed event log/hash, initial prediction prompt, actual principal mechanism, acceptable explanations, mechanically useful revision conditions, known unsuccessful changes, permissible information, and scoring reviewer ID. Winning is not required. Record the exact event/cell/target that supports each explanation. A useful revision outside the anticipated examples can earn credit only under the already specified mechanic condition and an actual replay, with the reviewer's reasoning retained.

## Observation and scoring rules

Use one `observations.csv` row per participant/task/attempt. Attempts start at 1 and remain contiguous across the person's sessions. Record an unsuccessful first attempt before a retry. Optional retries are retained and summarized separately; they never replace the primary first opportunity. `not_run` is a missing opportunity, not a successful or failed participant observation.

`assistance=none` means no moderator instruction after the measured task begins, beyond the standardized onboarding and the written task prompt. `controls` means operational help; `clarification` means an additional explanation of the requested task; `strategy` means a tactical cue; `takeover` means somebody else operates any part of the measured action. All four are assisted. If a cue becomes necessary, first freeze the unassisted result, then help the person continue safely and record the assisted retry. Normal on-screen game information is allowed; moderator directions to a particular solution are assistance.

Explanation scores:

| Score | Meaning |
|---:|---|
| 0 | No account of the observed mechanism, contradiction of the event evidence, or only “stronger stats/randomness” when that does not explain the observed event. |
| 1 | Names a relevant mechanic but misses the actual affected creature, geometry, timing or consequence needed to explain this encounter. |
| 2 | Identifies the principal observed spatial/temporal mechanism and its actual recipient/consequence, consistent with the retained authoritative events. Exact jargon and memorized numbers are unnecessary. |

Freeze the participant's explanation **before** opening the battle recap, A/B comparison, event log or moderator answer. Record `pre_recap=yes` only then. A person who independently opens Compare before explaining has used valid game UI, but that explanation does not measure unaided cause recognition; record `pre_recap=no`. A correct initial prediction is informative but is not required for a comprehension pass after watching. Record the initial prediction and later explanation separately in the local evidence note.

B1's `revision_useful=yes` requires an independently proposed formation revision, fixed roster/stars/relics/seed, and an actual replay satisfying the predeclared mechanical objective. A win without that relationship does not qualify. A loss can qualify. Record ineffective or harmful revisions honestly. `outcome=pass` records successful completion of the stated task; the tool still requires assistance, score, familiarity, timing and useful-revision conditions before counting independent success.

Do not retrospectively discard confusion, losses, crashes, pauses, fatigue or early exit. A critical crash, authority error, save loss or inaccessible required control stops the affected candidate study; preserve its failing observations. Restart under a new candidate identity after the defect is corrected. An unresolved scoring disagreement prevents human acceptance even if the numerical summary says MET.

## B1 — Five external formation participants

Player question: “Can I observe a formation consequence, explain it, and independently make a useful change?” Use standardized controls onboarding that teaches placement, selection, facing, Start/reset and pause without demonstrating the six scored answers. Measured combats run at normal speed. Pausing for a break is allowed; tactical step-through or slowed viewing is supplementary and is not a normal-speed primary observation.

The first two tasks below are each participant's preassigned unfamiliar primary encounters. Every participant also attempts the remaining mechanics. With five people this is a prospectively balanced rotation, not a perfectly balanced six-person Latin square. Preserve the actual order rather than asserting exact balance.

| Cohort slot | Mechanic task order | Primary unfamiliar tasks | Initial variant/orientation |
|---:|---|---|---|
| 1 | F01, F04, F02, F05, F03, F06 | F01 and F04 | A first, original orientation |
| 2 | F02, F05, F03, F06, F04, F01 | F02 and F05 | B first, mirrored orientation |
| 3 | F03, F06, F04, F01, F05, F02 | F03 and F06 | A first, original orientation |
| 4 | F04, F01, F05, F02, F06, F03 | F04 and F01 | B first, mirrored orientation |
| 5 | F05, F02, F06, F03, F01, F04 | F05 and F02 | A first, original orientation |

For each encounter: read the neutral task prompt → participant predicts → observe one normal-speed combat → record explanation before recap → participant states and makes one revision → replay the fixed inputs → record usefulness and explanation score → optional recap and retry. Do not load the known better formation in place of the participant's revision.

| CSV task ID | Neutral task prompt | Score-2 principal relationship | Useful revision condition and common mistake |
|---|---|---|---|
| `B1_F01` | “Predict which ally benefits from this creature's protection, then watch.” | Bellback's selected nearby rear recipient and incoming frontal sector match observed protection. Movement/facing may break the relationship. | Restore or intentionally deny the observed guard relationship. “Every nearby ally is shielded” is incorrect; surviving or winning alone is insufficient. |
| `B1_F02` | “Predict how this creature will approach and make contact.” | Distinguish walking, committed charge, actual release and legal landing; an adjacent charge can release without movement. | Create a released useful approach/landing or deny an opponent's one. Extra walking is not automatically extra useful momentum; do not invent a hidden no-attempt reason. |
| `B1_F03` | “Where will this healer establish itself, and who benefits?” | Root needs stationary establishment and injured recipients in its actual radius; movement/displacement/stun/defeat can reset/tether-stop it. | Improve the specified useful allied healing opportunity or force an observed reset. Higher aggregate healing, overheal or longer life alone is not necessarily a better team choice. |
| `B1_F04` | “Which creature will receive the distant strike?” | Identify the actual committed line and first intercepted recipient. | Open a useful line onto the intended recipient or insert a screen. An angle is useful only when replay confirms it; the known mirror may change the winner. |
| `B1_F05` | “Which positions will the crossing attack affect?” | Identify the fixed committed row/column and sequential recipient hits. | Spread to reduce harmful coverage or align to exploit it. A shared cell can receive both pulses; different targeting/timing may change a revised outcome. |
| `B1_F06` | “Predict the lane and where its first target can finish.” | Facing selects the lane; the first eligible target is displaced only along legal unoccupied destinations, while damage can continue. | Produce a useful actual push or prevent harmful displacement with placement/obstruction. Do not score an imagined push through an occupied cell. |
| `B1_F07` | “Choose an affordable response at this level and explain what you can actually recruit.” | Exploratory acquisition/counter record: cost band, represented copies, budget and available offer weights; no free late unit. | Observe the decision, actual response and unavailable opportunities. It is required as an observed task, but does not enter the primary comprehension numerator or declare the counter-access decision solved. |

**Preregistered primary scoring:** each participant must independently earn score 2 and a useful revision on both of their two preassigned unfamiliar tasks. The group criterion is at least **four of five distinct participants**. All six mechanics and F07 must have recorded first opportunities for a complete study; assistance and `not_run` remain visible. This two-encounter operationalization fixes the ambiguous scoring unit before collection. It does not replace the B0 group threshold or claim a population success rate.

Report all per-mechanic counts and experience groups even if the primary criterion is met. Any mechanic with fewer than four independent successes is flagged for specific review; a pooled pass cannot conceal a consistently misunderstood mechanic. Flags require inspection of actual errors and may justify revise/inconclusive. The tool never resolves that judgment automatically. Technical UI acceptance, tuning promotion and human comprehension are separate decisions.

## B2 — Five first-use Wonder Chess participants

Use a frozen 1H7B package with complete shop/bench/scouting/relic/save/result paths and no critical technical blocker. Provide the same brief control orientation, then observe the participant operating actual pointer/keyboard controls. Direct handler invocations are technical probes, not these human tasks.

Counterbalance independent ordering while keeping real dependencies: slots 1/3/5 begin with recruiting and placement before their first scouting task; slots 2/4 scout and return before recruiting. Within the placement task, odd slots first use pointer controls and even slots first use the documented keyboard alternative, then optionally try the other. Relic/restart/resume tasks occur only when their true entitlements and phases permit them. Do not create resources invisibly to avoid a difficult acquisition; record unavailable opportunities and schedule a declared continuation if needed.

| CSV task ID | Participant task and independent pass |
|---|---|
| `B2_BUY_UPGRADE` | Recruit toward a real three-copy upgrade, read represented owned copies and explain the gold/copy consequence. Observe a merge through actual shop purchases; no free injected copy. |
| `B2_DEPLOY_FACE` | Move a purchased creature from bench to a legal cell, respect actual capacity, and orient a creature whose facing matters. Complete using the assigned initial input method without assistance. |
| `B2_SCOUT_RETURN` | Inspect an opponent, identify whose deployed board/update is shown, and return to the owned board before issuing an order. Distinguish public deployment from private shop/bench information. |
| `B2_ADAPT` | After scouting or a loss, choose and execute an informed formation/recruitment change and explain its intended response. Observe a meaningful alternative and cost; a random move or moderator-suggested purchase is insufficient. |
| `B2_RELIC` | Use an earned three-offer draft, explain a chosen compatible effect and drawback, equip it and inspect the resulting effective mechanic. Report speculative/no-compatible context accurately. |
| `B2_LOSS` | Experience a loss, identify remaining choices and independently continue or select the appropriate elimination action. Losing does not fail the task. |
| `B2_FINISH` | Continue to personal victory or personal elimination and correctly distinguish that endpoint from the whole eight-seat tournament's final winner. |
| `B2_RESTART` | From the appropriate end state, start a fresh tournament and recognize the reset state without carrying an old match's resources/selection. |
| `B2_RESUME` | Save at a valid preparation boundary, close the actual package, cold launch it, resume the same state and continue. Explain which preparation is restored after an interruption. |
| `B2_EXPLAIN_1`–`B2_EXPLAIN_3` | Explain three preregistered unfamiliar actual combat fixtures before recap. Score each with the 0/1/2 rubric. Freeze and counterbalance their order by slot; use a fresh fixture set for returning people. |
| `B2_SPECTATE` | At least one participant continues from personal elimination to the tournament's actual final result, at normal speed. Record this group lifecycle observation separately; five individual spectating passes are not required. |

Primary task criterion: at least **four of five** independent first opportunities on each of the nine preparation/lifecycle tasks. Explanation criterion: at least two of three score-2 unfamiliar pre-recap explanations per participant, with **four of five participant passes**. A returned B1 participant cannot fill a B2 primary slot. A continuation of the same enrolled B2 person's tournament/resume work can use another session and the same slot; it is still one participant and prior Wonder Chess exposure must increase.

The three explanation inputs are fixed study encounters so their answer keys can be registered before collection. Record the player's own live loss explanation additionally; do not mislabel a dynamic user-created encounter as a preregistered fixture. Observe practical acquisition separately: offers seen, level, gold available, purchased/sold/deployed copies, XP/reroll spending, alternatives, and the person's stated reason. Event logs can establish actions and opportunity; inferred strategy is not the person's own explanation.

The tool reports primary-task and pacing criteria independently. A numeric preparation/explanation MET does not complete B2/M3 when spectating, durable package recovery, adaptation quality, pacing or a critical defect is unresolved.

## Duration, losses and voluntary replay

Timestamp sessions and observed intervals in UTC. Record active preparation, waiting, combat, recap, pauses and other time separately in seconds. Their sum must reconcile to interval wall time within two seconds of logging precision. Record pause reason in the local evidence note. Keep player-session/time-to-elimination observations separate from tournament-to-final-winner observations; both may exist for a match under separate local observation IDs.

For the 35–45-minute exploratory full-tournament target, count at least **five distinct complete standard match observations** from actual normal-speed human sessions. Start at a fresh tournament's first preparation and end at its actual final winner. Exclude early exit/elimination endpoints, resumes that did not observe the whole start, interrupted sessions and accelerated bot endings from the full-standard denominator. Report them as other observations. The summary subtracts explicit pause time from the standard interval while retaining all preparation, game waiting, combat, recap and other active elapsed time. It also retains wall time; do not subtract inconvenient game waiting.

Five matches observed by fewer than five people remain five match observations with the smaller distinct-person count disclosed. The same match watched by two people is one timing sample. Do not label a full tournament that crosses an unobserved save/resume gap as continuously measured standard duration. Record sample count, participant count, median/range, settings, exclusions and any unusually long/short encounter. Never pad waits to meet the target.

After the measured activity and before a leading question about liking, offer a neutral optional choice: “You may finish now, or play another encounter/session if you want.” Record `voluntary_replay=yes/no`; use `not_offered` if time, fatigue or an unmet prerequisite prevented a real choice. Scheduled attendance is not voluntary replay. Preserve early losses, fatigue, reasons for stopping and optional attempts. A single optional replay choice is not retention.

## Empty schemas and analysis tool

The CSV headers are defined by `tools/vnext/human_study.py`. Keep the exact columns. Required assessed rows reference a local evidence file and its SHA-256. The tool verifies identity and integrity; it cannot determine whether a recording really supports an observer's score. Evidence paths must be relative to the study directory and may not escape it. The summary never loads raw transcript text into its output.

Audit actual counterbalanced task order, permissible onboarding, consent details, exposure classification and reviewer agreement from the original session records. The validator does not infer those events from a CSV checkbox. Sixteen unit tests exercise synthetic temporary records, including malformed protocols, schema changes and escaping evidence paths; none is participant evidence.

| File | What it records |
|---|---|
| `participants.csv` | One anonymous person, external status, consent, adult eligibility and genre band. |
| `sessions.csv` | Person/slot, true repeated-session order/exposure, dates, frozen candidate/protocol, observer/hardware and completion flags. |
| `scenarios.csv` | Frozen task input, familiarity classification, seed and hashed formation/answer-key references. |
| `observations.csv` | First opportunity and separately numbered retries, assistance, outcome, explanation/revision evidence and task time. |
| `durations.csv` | Genuine observed match/session intervals, endpoints, components, acceleration/interruption, losses and optional replay. |
| `protocol.json` | Registration, candidate identity, fixed primary allocation and hash of the scenario/answer-key registry. Empty identity/time fields must be completed before any real study. |

Check only the empty repository template:

```powershell
python tools/vnext/human_study.py reports/vnext/milestones/study-templates --check-template
```

This returns `TEMPLATE_ONLY` and `human_evidence=NOT_RUN`. It must not be recorded as a human-study pass.

After collecting real local records, use the actual directory:

```powershell
python tools/vnext/human_study.py 'C:\Users\iputu\AppData\Local\WonderChess\Studies\B1-candidate-01' --output 'C:\Users\iputu\AppData\Local\WonderChess\Studies\B1-candidate-01\summary-01.json'
```

The output file must not exist; the tool refuses to overwrite evidence. Exit `0` means the selected B1/B2 primary numerical criterion is MET, `1` means NOT_MET, `2` means invalid/inconsistent input, and `3` means INCOMPLETE. Zero participants, insufficient cohort, missing first opportunities, incomplete primary sessions or missing experience coverage cannot produce MET. Pacing and spectating are separate output fields. Every ordinary summary states `acceptance=HUMAN_REVIEW_REQUIRED`; even a complete numerical readout leaves the owner/research review open.

Reviewers should publish a compact anonymous report: exact candidate, sample/experience counts, all first-opportunity numerators and denominators, assistance, failures, attrition, retries, actual adaptation examples and counterexamples, timing endpoints, replay choices, unresolved scoring disputes and a component-level go/revise/inconclusive decision. Retain failed evidence. Do not export contact mappings or raw private recordings into the repository.

## Later human dependencies

| Gate | Required experience/evidence | What must be ready first |
|---|---|---|
| B3 traits | At least twelve external participants; explicit complete-a-pair and reject-a-pair tasks with real slot opportunity cost; individual explanations and choices, then unfamiliar transfer. Analyze Beast, Plant and interaction candidates separately. | Frozen trait-off/on behavior, genuine acquisition, bounded trigger/reset contracts, technical regressions and accepted sustain basis for Plant. A rejected trait is a valid result, not forced success. |
| Bellback pilot / M2 | At least twelve external participants across genre bands. Compare the same recorded combat across presentation variants, then fresh normal-speed crowded encounters. Measure role/ability recognition, readability, creature appeal and accessibility separately. Retain continuous motion and listening review. | Exact reference/forms approvals and technical asset stages; implemented mechanics cannot be inferred from a visually finished proxy. Complete Bellback, Prism Organ, Thimblewake and Wondergrove screen/audio/effects requirements before closing M2. |
| M4 ecosystem | Observe acquisition → formation → counter → adaptation for every claimed strategic archetype and each promoted roster batch. Use held-out formations and record exposure/affordability. | A deliberately chosen content batch with actual mechanics, relics, bots, saves and useful/unfavorable placements; no counting authored kits as experienced content. |
| M5 solo beta | At least twelve external people across experience bands, repeated days. Proposed study schedule is three planned observations across a week plus an independently optional extra session; register actual dates before collection. Report fatigue, losses, independent build changes, return/attrition and desire to replay separately. | Coherent M2 slice, reliable M3 lifecycle, frozen M4 candidate, accessible onboarding/settings, technical recovery and performance evidence. There is no adopted retention percentage: define any formal retention hypothesis before running it. |
| M6 | Actual human-operated remote journey and recovery across independent devices; local agent clients remain technical probes. | See the separately owned network evidence protocol; real service, dedicated server and hardware prerequisites. |
| M7 release | Owner approval of exact assets/package, real clean supported-machine installation/cold launch/full-match/resume/results/restart, continuous motion/audio review, no critical unresolved defects, final performance and rollback/support evidence. | Intended M2–M6 scope accepted and frozen. The six-hero lab, successful compile, 1,000 native and 100 packaged tournaments do not replace human approval or a clean machine. An offline-only release requires an explicit scope decision. |
| Stable comparative study | At least thirty genre-familiar participants, counterbalanced Wonder Chess/Auto Chess order, equal declared learning/time conditions, versions/hardware/familiarity recorded; separate agency, creature appeal, clarity, usability and replay desire with uncertainty. | Stable candidate and a preregistered comparative analysis/eligibility plan. Decide before running whether comparison is a release gate. No result supports universal superiority or long-term retention. |

The current validator deliberately implements B1/B2 only. Register distinct B3/M2, M4, repeated-day M5 and comparative datasets/rubrics when their exact candidate and question exist. Do not squeeze later evidence into B1 participant rows or let a numerical tool issue aesthetic/release approval. Human availability, reference decisions, supported hardware and external studies remain actual work, not completed template fields.

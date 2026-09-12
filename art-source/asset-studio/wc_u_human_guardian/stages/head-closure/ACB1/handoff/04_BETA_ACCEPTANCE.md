# Closed-beta acceptance — proposed gates, all new results pending

This checklist is a release decision aid, not a test runner and not current evidence of passing. Reconcile historical results against the exact new candidate; record actual commands only after verifying they exist and running them.

## Severity and approvals

- **S0 / blocker:** authority/privacy breach, fabricated or duplicated resources/results, corrupted persistent state, reliable crash, inability to start/finish/rejoin a required session.
- **S1 / major:** important skill/rule wrong, recurring unrecoverable interaction, severe performance, misleading essential UI, obvious release-blocking visual/audio defect.
- **S2 / minor:** localized polish issue that does not invalidate intended use; explicit owner, impact and deferral.

Zero unresolved S0 and zero unresolved beta-blocking S1 before inviting the closed-beta cohort. Other S1 issues require an explicit scope decision, not relabeling. Technical and visual gates do not average together. Product, art and release approvers must be the actual authorized people, not agent-written identities.

An art task may be parked while internal gameplay continues. That does not clear its defects for beta.

## Gate table

| ID | Gate | Minimum proposed evidence | Current-session status |
|---|---|---|---|
| BETA-01 | Candidate identity | Executable, content, data, protocol, engine, settings and source manifest; whole payload reproducible | NOT_RUN |
| BETA-02 | Standalone lifecycle | Clean-machine launch, menu, settings persistence, complete tournament, spectating, results and restart | NOT_RUN |
| BETA-03 | Roster/data | All 24 selected stable IDs, correct skills/stars/traits, gallery/runtime parity, no missing dependencies | NOT_RUN |
| BETA-04 | Rules/integrity | Atomic economy, merge/copy conservation, phase locks, replays/idempotency, movement/effect/settlement fixtures | NOT_RUN |
| BETA-05 | Tournament breadth | 8/7/6/5/4/3/2/1/0 active-seat cases, ghosts, simultaneous eliminations, PvE and cap, no stalled settlement | NOT_RUN |
| BETA-06 | Actual-combat regression | At least 100 fresh seeded actual-runtime tournaments against the candidate; targeted and held-out seeds; no unexplained crash/stall/invariant failure | NOT_RUN |
| BETA-07 | Balance investigation | Current timeout/hero-use/wave reports with opportunity and mode denominators; high-impact causes diagnosed; human strategy notes | NOT_RUN |
| BETA-08 | Human playability | At least 8 observed newcomer/relevant-player sessions in the internal cohort; record assisted vs unassisted, completion, confusion and subsequent decisions | NOT_RUN |
| BETA-09 | Assets/motion | Per-hero and per-neutral matrix; continuous clips/transitions/contact, portraits, materials and actual display-scale review | NOT_RUN |
| BETA-10 | Audio | Actual listening, sliders, stacked-event limits, release/contact timing and fatigue review | NOT_RUN |
| BETA-11 | Physical/remote networking | Two-machine 2H6B, 4H4B, and actual remote 8H0B; separate processes and independent devices documented | NOT_RUN |
| BETA-12 | Recovery/security | Authenticated seat reclamation, bot/human authority handover, duplicate commands/logins, version mismatch, private-state traffic checks | NOT_RUN |
| BETA-13 | Impairment | Recorded RTT/jitter/loss settings and measured behavior; mild/degraded/harsh sessions; no economy or state corruption | NOT_RUN |
| BETA-14 | Performance | Named hardware/presets, full match, worst PvP/PvE, all-gallery and repeated loading, percentile/stall/memory/server traces | NOT_RUN |
| BETA-15 | Usability/localization | Core English/Indonesian review, scaling, keyboard/tap alternatives, focus, tooltips, statuses and reduced motion | NOT_RUN |
| BETA-16 | Distribution/operations | One actual delivery route, prerequisites, build mismatch handling, bug/crash intake, logs, rollback rehearsal and monitoring owner | NOT_RUN |
| BETA-17 | Product/art signoff | Explicit selected-content acceptance and documented residual debt; no invented approvals | NOT_RUN |

A prescribed sample is for defect detection, not proof of population reliability or competitive balance. Report denominators, selection bias and confidence limits where statistics are claimed. Repeating 100 known passing seeds after every cosmetic change is less useful than updating affected fixtures and running broad regressions at integration/release checkpoints.

## Proposed performance target to confirm

Reference PC: define an actual available system; the historic laptop is a starting comparison, not an established minimum. At 1080p with the declared 60 FPS preset, propose active-play p95 <=20 ms and p99 <=33.3 ms for representative busy samples. Inspect maximum spikes and all loading intervals separately; no silent frame exclusion.

Run at least three full normal-speed tournaments and a defined busy-encounter/gallery stress capture on each selected machine class. Do not profile under concurrent Blender rendering or compiler load unless explicitly testing contention. Report actual duration and thermal/power state. A 60 FPS capped opening is not a full-match headroom measurement.

## Proposed remote recovery fixtures

| Fixture | Observe |
|---|---|
| Disconnect in preparation | Pending purchase final authority; no double deduction; seat/reservation preserved |
| Disconnect in combat | Combat continues; returning presentation reconstructs actual state |
| Disconnect during settlement | Exactly one result/reward; correct next round or final placement |
| Temporary bot then human | One controller authority at a time; canonical roster and command sequence |
| Repeated reconnect | No duplicate pawns/rosters/private subscriptions or economic actions |
| Wrong user / wrong token | No seat theft from display-name matching |
| Wrong protocol/catalog | Clear rejection before incompatible match state is accepted |
| Server unavailable/crash | Defined abort/no-result message and menu recovery; no promised migration |
| Lag/loss near deadline | Authority uses accepted order; user receives success/reject; no silent state divergence |
| Spectator/eliminated client | Only permitted information and actions; no revived economy ownership |

Use the project's existing policy when it passes. Proposed grace windows and control handoff details require a recorded product/security decision before changes.

## Tester rollout and stop conditions

Begin with 8–16 internal invitees. A proposed first closed cohort is 32–64 total invited players with scheduled measured concurrency; registrations are not simultaneous load. Close invitations or roll back when a blocker, repeatable crash/seat corruption, private-state leak or unbounded server/resource growth appears.

For each session record build ID, match ID, start/end, mode, seats/human count, result/failure classification, permitted performance/network data and user-consented repro material. Minimize identifying information and redact keys/local paths. The retention and access policy must exist before external collection.

Create a single bug template: expected result, actual result, reproduction, approximate time, build/match ID, optional screenshot/log attachment. Do not require a tester to install development tools or provide secret credentials.

## Evidence record

Each result names gate ID, status, owner/reviewer, timestamp, candidate identity, hardware/network, actions, expected/actual behavior, artifacts, limitations and unresolved defects. Never inherit a pass from an older candidate without verifying the relevant inputs are identical.

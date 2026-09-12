# ACB1-GAME — Resume the real 24-hero game, not a historical bootstrap

## Objective

Re-establish the current playable checkpoint, identify the few most consequential gaps between that build and closed multiplayer beta, and close one reproducible high-priority issue. This task is independent of whether the new Ada head is artistically accepted.

Do not create another game, downgrade to twelve heroes, replace the framework, reimplement working shop/combat systems from scratch, or build a marketing website first.

## 1. Read current authority, not every historical prompt

Read repository AGENTS.md, START_HERE.md, `reports/UPDATE24_CHECKPOINT_HANDOFF.md`, `reports/implementation_state.json`, active update instructions and the canonical profile. Identify any more recent local handoff, branch, uncommitted changes, and packaged build.

The public snapshot inspected for this plan was `9623fd82f98ff80a90985b9f552d8851ccece30f`. It reports:

- 24 playable stable hero IDs, six races/classes, highest eligible two-/four-member tiers.
- PvE on rounds 1–3 and positive multiples of five; seven neutral archetypes.
- Solo 1H7B, all-bot tests, a lobby, hero gallery, and a LAN route.
- A Windows Update24 checkpoint r4; actual-combat and packaged-loopback tests.
- Open manual normal-speed, physical two-machine, current disconnect/recovery, continuous audiovisual, full-match and busy-load reviews.

These are historical repository-authored claims to reconcile, not present-session pass results. The supplied head-only r016 is separate from the packaged Ada source revision. Do not substitute the study for the functioning hero automatically.

## 2. Identify the runnable artifact

Locate the existing package and retain its entire directory, not only the launcher. The public handoff's local locator is `builds/WonderChess-Update24-Checkpoint-r4/Windows/WonderChess.exe`; verify it rather than assuming it exists here. The canonical Unreal project is `game/WonderChess.uproject` in the inspected repository.

Record executable/payload identity, source commit or dirty-state manifest, canonical data hash, schema/balance/protocol, engine version, machine and graphics settings. A rebuilt executable and an older passing report are not the same evidence.

Run the current known package before forcing a new engine build. If it is absent or inconsistent, resolve the build provenance first using installed supported tools. Missing local executables must not be replaced by invented sandbox or Windows links.

## 3. Make a feature-to-evidence inventory

For each row below, classify current status as Verified this run, Historical report only, Failed, Blocked, or Not inspected. Include paths and observations.

| System | Current-session test |
|---|---|
| Launch/menu/settings | Launch standalone, persist basic settings, return to menu |
| Hero gallery | All 24 records/models, actual skill and star values, readable text |
| Shopping and bench | Buy, sell, reroll, lock, full-bench merge and failed-input feedback |
| Formation | Select, place, swap, scout, return to own board, team capacity |
| Traits | Exact distinct counts, 2/4 replacement, battle snapshot, tooltips |
| Combat | Single/area effects, movement, interruptions, real off-screen matches |
| Tournament | Pairings, ghosts, PvE, draw/cap, simultaneous outcomes, eliminations |
| Player journey | Start, learn, finish or be eliminated, spectate, restart |
| Networking | Real client state, ownership/privacy, version rejection, recovery |
| Assets | Appearance, motion/contact, VFX release, audio, actual screen scale |
| Performance | Normal-speed full match, busy PvP/PvE, gallery, repeated transitions |

## 4. Play a normal-speed human session

Capture one complete normal-speed match with a human or genuinely interactive available computer-use control. Distinguish human input, agent-driven interaction and scripted command injection in the report. An accelerated all-bot match does not replace this review.

Observe purchase feedback, valid/invalid placement, near-deadline actions, upgrade identity, scouting, formation understanding, skill readability, PvE difficulty, health loss, elimination, spectating and a subsequent restart. Inspect the game at its actual resolution with audio audible; rendered silent clips cannot pass listening review.

If the session lacks real input or audio inspection, prepare the exact executable, controls and observation form for Pram. Mark the manual/listening rows blocked. Continue independent reproducible tests rather than pretending script injection is manual play.

Do not interrupt the user's active Blender or native-window input. Coordinate access to the shared desktop and GPU.

## 5. Audit the reported balance warning signs before tuning

The published closeout reports 1,844 timeouts among 12,597 fights (~14.64%), a large difference in raw use between Neris and Dagna, guaranteed wins in sampled opening waves, and only 32 wins in 132 round-30 PvE encounters. These are investigation leads, not proven balance defects.

Recover the original event data for the matching build and separate PvP, ghosts, and each PvE wave. For timeout cases distinguish pathing idle/stalls, inability to acquire targets, healing/shield equilibrium, low DPS and an intentional timer outcome. Do not indiscriminately nerf healing or shorten the timer.

For hero use measure offer opportunity, affordability, purchase conditional on opportunity, bench-to-field conversion, cost/level/round, bot persona and pairing. Low total unit-round use alone is not proof that a hero is weak. Debug policy bias before declaring a unit buff necessary.

Opening PvE victories may be an intentional tutorial outcome; evaluate human experience. A late wave may deliberately test composition. State expected wave role before changing numbers.

Retain independent shop draws unless the user approves an economic redesign. The active rules explicitly do not implement a finite shared pool.

## 6. Close one real issue, do not just produce an audit

Prioritize in this order: launch/crash or broken match progression; economy/ownership/privacy corruption; wrong combat or settlement; interaction/readability preventing play; significant performance; cosmetic polish.

Select one reproducible issue within available scope. Add or adapt its specific fixture, make a bounded fix, rerun the affected tests, rebuild/repackage when runtime changed, and reproduce the repaired flow in the actual candidate. Preserve the failed baseline and do not update balance merely to make an unrelated test pass.

If no defect is reproducible, make progress on the highest-risk unverified gate (for example a physical two-machine test with access), not another broad rewrite. If a required device or permission is missing, prepare the exact blocked test and proceed with an independent lane.

## 7. Hand off the next three tasks

Output a concise current-state report, the top ten prioritized issues with severity/owner/repro/evidence, work actually completed, and the next three executable tasks drawn from the beta roadmap. Identify each prerequisite rather than promising dates.

No purchases, cloud provisioning, public publishing, new accounts, engine upgrades or destructive source replacement without explicit authorization. Run current project validation commands only after inspecting them and their actual availability. Do not invent launcher flags or claim that a Python test is a packaged Unreal game test.

# Wonder Chess — Major steps from the current checkpoint to closed beta

This is a proposed production roadmap, not a claim that these gates have passed. Preserve the existing 24-hero update and any newer local work. Evidence from the published checkpoint is explicitly historical unless reproduced against the same candidate.

## 1. Product target and boundaries

### Proposed first closed-beta product

A coherent Windows high-fantasy auto-battler supporting private online eight-seat matches with one to eight humans and clearly labeled bot fill. One arena; the existing 24-hero roster and seven neutral archetypes; six race/six class two/four synergies; a functioning onboarding, lobby, gallery, scouting, economy, automatic combat, results and recovery loop.

The content target is a readable polished stylized game, not a cinematic RPG or a requirement for every portrait to match a painting pixel-for-pixel. Actual gallery/showcase use still matters: small gameplay scale is not permission to leave a highly exposed hero visibly unfinished.

No new item inventory, power-progression economy, paid cosmetics store, battle pass, guilds, voice/public chat, campaign, additional races, or multiple regional boards before this loop is reliable. Existing visual equipment and authored skills stay intact. A novelty mechanic is not required to validate whether the current game is enjoyable.

Windows is the first engineering/delivery target because that is the reported package. SEA interest does not establish mobile readiness. Run an early bounded physical Android feasibility test before committing further irreversible art/performance choices if mobile is a business priority; a Windows beta does not count as mobile validation. The actual beta platform must be recorded as a product decision.

### Three different uses of a build

1. **Internal playtest:** controlled participants, identified placeholders/art debt allowed, current failure risks disclosed. This can begin before Ada's new head is finished.
2. **Closed beta:** coherent selected content, actual remote eight-player capability, recoverable sessions, understandable gameplay and supportable distribution. This is the first target here.
3. **Wider/open beta:** larger acquisition, server capacity and support commitments; a separately approved stage after evidence from closed beta. Not a launch claim.

## 2. What already exists according to the repository

The checked public handoff reports a packaged 24-hero update with 168 hero animation clips, seven neutral sources and 40 neutral clips, functional solo/all-bot testing, a gallery, and 2H6B loopback. It explicitly says finished art, continuous audiovisual approval, manual play and real physical/network checks remain open.

Its 100-tournament dataset reports median simulated duration 1,284.525 seconds (21.41 minutes), p95 1,426.95 seconds (23.78 minutes), 1,844/12,597 fight timeouts, and uneven hero selection. Do not translate simulated duration into a measured human-session duration. Manual decision time, network waits and tutorial time are different observations.

The reported performance sample covers a 150-second opening at 1080p on a Ryzen 7 6800H / RTX 3060 Laptop GPU / 16 GB machine. It is not a full-match, every-hero, all-gallery or worst-case busy-PvP performance pass. Updated head studies are not integrated into that old evidence automatically.

## 3. Program structure: parallel work without binary conflicts

Maintain two independent delivery lanes:

- **Art/reference lane:** Ada closure, whole-hero integration, family-specific art improvements.
- **Game/beta lane:** current package audit, human playtesting, combat/bot tuning, networking, UX, operations and release checks.

They join at candidate integration and final beta acceptance, not at every eyelid change. Use a stable temporary presentation binding for internal tests. One owner per `.blend`, shared rig, Unreal map or other binary asset; schema and balance ownership remain serialized. Do not run GPU-intensive renders while profiling the game or compare contended performance against an uncontended baseline.

Suggested dependency order:

```
Current runnable checkpoint -> normal-speed playtest -> prioritized fixes
                         \-> early remote/network feasibility
Ada head closure -> full Ada roundtrip -> representative family pilots
             \-> parked art work does not stop the game lane

Core rules + bot baseline + UX + selected art + real networking
          -> integrated closed-beta candidate
          -> perf/recovery/regression/usability verification
          -> controlled tester waves -> fix -> expand
```

## 4. Milestone G0 — Re-establish the current playable baseline

**Goal:** stop estimating progress from old prompts and start using the actual build.

Run ACB1-GAME. Produce an evidence-backed current-state matrix and keep the existing package as a rollback point. Verify schema, content, protocol and executable identity, including newer local changes. Never silently roll back to the earlier 12-hero plan.

Perform a full normal-speed match, elimination/spectating, results and restart. Use the actual menu and UI. Preserve whether the actor was a human, an interactive agent or a scripted test.

**Exit:** a reproducible build plus a prioritized issue list and at least one concrete fix or newly completed high-risk check. This is an internal milestone, not an art or beta certification.

## 5. Milestone G1 — Freeze a small beta product and the rules that determine it

Record decisions once instead of repeatedly expanding scope:

| Decision | Recommended beta default | Why / caveat |
|---|---|---|
| Mode | One eight-seat tournament | Focus the core experience |
| Human/bot mix | 1–8 humans with clearly labeled fill | Bots must not masquerade as people |
| Roster | Existing 24 authored IDs | Already adopted; no unapproved roster reset |
| Arena | Existing courtyard/lobby | One consistent environment over several unfinished ones |
| Abilities | Current simple authored active skills | Do not add another resource layer |
| Economy | Retain versioned current independent draws initially | Explicitly does not test contested finite-pool drafting |
| Synergies | Current distinct-type 2/4 tiers | Freeze scope/stacking and show them clearly |
| Progression | Match-local, no paid power | Keep beta interpretation straightforward |
| Initial languages | English + Indonesian core UI | Draft translations still require human review |
| Hosting | Private dedicated-server sessions as beta target | Requires an actual hosting/build/network decision |
| Distribution | One controlled channel, versioned payloads | Avoid multiple incompatible builds |

Discuss the target session duration, skill accessibility and losing experience with players rather than changing them solely to match a competitor. A proposed goal remains around 15–25 minutes excluding pauses/tutorial, but measure it rather than guarantee it.

A shared pool is an explicit later product choice. It changes rarity, purchase competition, shop reservations, releases on sell/elimination, and bot policies. Do not toggle it on as an incidental balance patch. Preserve current documented behavior until a migration and test plan is approved.

**Exit:** one short decision record and one active rules/data profile; no mutually conflicting masters. This is not permission to create another lengthy foundation instead of improving the game.

## 6. Milestone G2 — Prove that choices matter and results are correct

### Correctness before balance

Recheck economy atomicity, copy conservation, shop locking, level limits, trait snapshots, movement/dash reservations, target changes, released projectiles, stun interruption, shields/healing, PvE reward timing and round settlement. Use actual runtime combat for tournament tests; an arithmetic reference or fabricated battle outcome is not equivalent.

Pairing and ghosts must have recipient/donor separation, exactly one health-affecting outcome per real seat, sensible odd-count behavior, and defined zero-/one-survivor outcomes. Concurrent PvE involves up to eight active encounters rather than just four pairwise fights; test actual maximum wave sizes from data.

The server's accepted command order—not a client clock—decides preparation-deadline transactions. Repeated requests must not duplicate spending or merging. The UI needs an acknowledged/rejected result, not silent optimism that drifts from authority.

### Diagnose the existing warnings

The raw historical timeout rate is ~14.64%. Split by PvP, ghost, monster wave, team size, round and cost before proposing a fix. Replay examples with target/path/idle, effective healing/shielding and damage-event overlays. Identify genuine deadlocks separately from a legitimate attrition timer.

Do not declare Dagna overpowered or Neris weak from raw unit-round counts. Measure appearances in shops, affordability, purchases conditional on opportunity, deployed use, star level, role, bot policy and outcomes. A bug in bot evaluation can create selection imbalance without a character-stat defect.

Treat opening neutral wins and late neutral losses as questions about intended role. Tutorial waves can appropriately be forgiving. A sudden wave difficulty cliff might be undesirable; verify whether it comes from stats, targeting, late-game economy, or intended composition checks.

### Controlled tuning

Use a held baseline and one meaningful change at a time. Separate changes to balance numbers, bot intelligence and engine mechanics. Run mirrored/reversed-seat fixtures and several bot policies on both tuning and held-out seeds. Report cost/level/round denominators and uncertainty; observational hero placement is not causal strength.

Proposed progress criteria are several viable formation plans with intelligible counters, different purchase/level decisions at different health/gold states, and no dominating forced composition found in testing. Do not manufacture perfectly equal win rates for every archetype.

**Exit:** reliable rules and a documented balance baseline with diagnosed high-priority pathologies. Human playtests confirm that at least several decisions have visible consequences. No claim of solved competitive balance.

## 7. Milestone G3 — Make bots useful training opponents and a trustworthy test tool

Retain persistent seat economy, shop, roster, bench, position, health and policy state. Use the same validated commands as humans. No hidden resource/stat advantage, access to opponents' private shop/bench, future draws or impossible last-frame reaction to private intent.

Add decision observability: top candidate actions, utility terms, missing frontline, merge opportunity, reachable synergy, budget reserve and public scouting snapshot. Log enough to debug, not unlimited raw data. Difficulty should alter planning/noise/decision cadence, not secretly alter the rules.

Test an inexperienced policy, coherent planner and adaptive policy against each other; a single optimizer can overfit the whole game to itself. Raw bot usage should not set the art-production order automatically. Bot fill and temporary disconnected-seat control must be visibly labeled.

**Exit:** legal, varied competitors that finish whole matches, use the roster when opportunities exist, and reveal rather than hide strategic defects. Bots are not evidence for real remote multiplayer quality.

## 8. Milestone G4 — Make one whole hero excellent in motion, then standardize the roster

After the Ada head closure, complete her head/hair/brows, armor/body/equipment, UVs/materials, rig integration, weights and seven clip states. Reuse working bones/sockets/animations only where the new proportions actually fit; do not discard working rigs gratuitously or freeze defective anatomy for their convenience.

Keep sculpt source separate from the runtime mesh. Do not ship the full evaluated head simply because it previews well. Recheck scale, facing, root, normals/tangents, shader convention, skin weights, grip and shield clearance. Perform a deliberate source revision/reimport into a candidate Unreal folder and cold reload the result.

Inspect in the real gallery and real battle camera. Show neutral clay for form diagnosis and actual lighting/materials for the experience; neither alone is sufficient. Visual-only hair/brows context during head review is not final production art.

Next test two contrasting bodies (a slender/cloth-led hero and a stocky hero), then improve the remainder by visible severity and reuse opportunity. Preserve all 24 gameplay IDs. Halfling and Dragonkin body families need their own checks; do not force every body into an identical cage.

Review all 168 hero/clip combinations and the 40 reported neutral clips at least once on the beta-selected content. Shared animations do not remove per-character contact/deformation review. Newly changed geometry invalidates relevant earlier clip evidence. Sampling static bone transforms or encoding silent movies does not constitute continuous visual/audio approval.

For each hero, track silhouette, portrait/model consistency, facial treatment, material separation, idle/move/attack/active/hit/defeat/victory, transitions, weapon contact and effects. Skin that intersects a weapon or hair that detaches during motion is an integration defect, not a cosmetic note to ignore.

**Exit:** coherent selected roster/neutral presentation at the actual display sizes, with no unresolved release-blocking visual defects. Minor accepted polish debt remains explicit. A runtime-compatible asset is not automatically gallery-quality.

## 9. Milestone G5 — Complete the player experience

Make the first five minutes teach buy -> place -> synergy -> watch -> interpret -> upgrade, with skip/reset and readable feedback. Do not force a lore introduction before a returning player can enter a match.

Review shop costs/rarity, available gold/XP, capacity, bench overflow, merge previews/results, lock state, selection, hover/tap inspection, range/effect descriptions, opponent scouting and returning to the home board. Provide a click-select/click-place alternative to dragging and settings that survive restart.

Display the current two/four synergy tier and its actual recipients. Distinguish racial/class bonuses from descriptive role tags. Source UI stats from canonical/derived runtime data, not separately maintained text. Do not imply inventory bonuses for visual weapons.

Combat feedback should communicate attacks, ability release, hit, shield, stun, heal and defeat without continuously obscuring the board. Align presentation to authoritative events; never change damage timing solely to hide a bad animation. Honor reduced camera motion, sensible effect limits and color-independent status shapes.

Provide actual damage/heal/shield contributions and a comprehensible health-loss result. Advice can be added as labeled interpretation, not fictional causal certainty. Let an eliminated player spectate or leave cleanly. Online pause behavior must not freeze the whole tournament for one client.

Listen to attacks, UI, shield/heal/stun, round stingers, victory/defeat and ambience. Set priority/concurrency limits for stacked events and inspect repeated playback fatigue. Silent motion review is not audio review.

English and Indonesian core flows need native review, consistent terms, font coverage, text expansion and small-screen checks. Other SEA markets require separate language/device tests; do not equate Indonesian coverage with all of SEA.

**Exit:** new participants can navigate a complete match without the founder explaining every action, and returning participants can quickly start another one.

## 10. Milestone G6 — Prove real eight-human multiplayer and recovery

Start this technical lane early; do not wait until all 24 faces are polished.

1. Revalidate 2H6B on two physical machines using the exact candidate.
2. Test separate packaged clients against a dedicated-server target where available.
3. Exercise 4H4B and 8H0B with actual independent clients.
4. Repeat over actual remote networks plus controlled impairment.
5. Add the invite/session/distribution flow and recovery tests before outside cohorts.

Dedicated hosting is the proposed competitive beta default, not a feature inferred from a LAN button. Epic's setup guide distinguishes a listen host from a headless dedicated server, and its documented dedicated-server tutorial requires a suitable C++/source-build setup. Check the project's installed build path and dependencies rather than promise deployment from an arbitrary editor executable.

The required service responsibilities are seat identity, session creation/join/leave, invites or codes, version/protocol/catalog compatibility, allocation of an actual running game server, and monitoring/termination. A lobby listing is not game-server hosting. Choose the smallest suitable integration after checking current project code; do not rewrite it just to adopt a fashionable framework.

The server owns gold, offers, unit IDs, placement, phase, combat and results. Replicate public board/standings separately from owner-private shop/bench. Test serialized traffic and ownership rules, not just whether a panel is visually hidden.

### Recovery policy to decide explicitly

Use the existing implemented policy where valid. If missing, proposed beta defaults are a short disconnect grace followed by visibly labeled bot control, authenticated seat reclamation within a limited window, and a single authoritative control-ownership transition. Record exact grace windows in rules before coding them.

A reconnecting client gets a fresh authoritative snapshot, last acknowledged command/sequence, current phase and private seat state. It must not recreate the roster, replay purchases, or compete with the temporary bot for authority. Return human input at a defined safe boundary if necessary. Never use the display name alone as seat authentication.

Handle preparation, combat and settlement disconnects; repeat reconnects; client process crash; duplicate login; application alt-tab; slow loading; packet loss; late/ineligible rejoin; and server termination. Server failure may abort a beta match with an explicit no-result policy; do not promise live host migration unless it is genuinely implemented/tested.

### Impairment matrix (proposed test conditions, not regional measurements)

| Test target | Example observed RTT / loss target | Required behavior |
|---|---|---|
| Reference | Measured local path | Correct authority and state |
| Typical test | ~80 ms / 1% | Clear acknowledgements, no state corruption |
| Degraded | ~150 ms / 3%, variable delay | Responsive waiting/rejection feedback, eventual consistency |
| Severe | ~300–500 ms / 5–10% | Bounded recovery or clear failure; no duplicates/exploits |

RTT is measured. Record which directions receive emulation so that an 80 ms one-way delay is not mislabeled as 80 ms RTT. Harsh tests stress fault behavior, not a promise of smooth play or a statement about SEA network quality. Unreal supplies lag/loss emulation; it does not eliminate the need for physical and remote sessions.

**Exit:** a real eight-human session completes remotely, ownership/privacy/version/reconnect cases pass, and failure behavior is documented. Eight bots or eight processes on one developer machine do not establish this alone.

## 11. Milestone G7 — Performance, reliability and controlled distribution

Use named reference and minimum-candidate hardware and recorded presets. The previously reported laptop is a useful anchor, not a verified minimum specification. Keep compiler, Blender rendering and unrelated game loads out of comparable performance captures.

Profile normal-speed full tournaments, maximum deployed PvP, the largest configured simultaneous PvE waves, camera switching, repeated results/restart, and gallery cycling across all 24 heroes. Track frame time percentiles/spikes, game/render/GPU time, memory/VRAM, network bandwidth and server simulation time. At the documented 20 Hz simulation step, 50 ms is the interval, not a recommended CPU occupancy; reserve headroom for jitter and other sessions.

Unreal Insights provides CPU/GPU, memory, network and loading analysis. Use the relevant tools rather than treating an FPS cap at 60 as proof of spare capacity. Gauntlet can orchestrate multi-process game tests, but reuse working project harnesses when they already solve the need; do not introduce a new infrastructure project as a beta dependency.

Proposed client target: 1080p/60 FPS on the named reference preset, with 95% of active-play frames <=20 ms and 99% <=33.3 ms during defined busy samples. Report all frames and loading separately; do not discard unexplained hitches. These are decision targets, not measured results or universal standards. Choose lower-end/mobile targets from actual devices.

Check packaging from a clean environment, prerequisites, fonts/content paths, offline practice, application focus/resolution behavior, a fresh user profile, installation location with spaces, log rotation, update/version rejection and rollback. Never disable security tools to make distribution work.

Use build and content IDs in crash/bug reports; retain symbols securely where needed. Do not ship API keys, developer console powers that mutate authority, private local paths or unlimited telemetry. Draft a clear tester notice and data retention/access policy before collection; any legal obligations need appropriate jurisdiction-specific review.

Choose one distribution mechanism and one initially tested hosting region based on actual access, latency and cost measurements. No location is assumed to be the best for all SEA players. No unauthorized cloud spend or public exposure.

**Exit:** reproducible artifact, current manifests, measured worst-case behavior, recoverable distribution, and an owner who can monitor and roll back the test.

## 12. Milestone G8 — Staged external testing

### Internal cohort

Proposed 8–16 invited participants across available skill levels, including auto-battler newcomers. Run observed sessions before expanding. Gather device, settings, chosen language and optional network metrics without unnecessary personal data.

Ask whether players understood purchasing/upgrades, why an action failed, what a synergy did, why a round ended, and what they would change next time. Watch where they hesitate. Do not replace observation with a leading satisfaction question.

### First closed-beta cohort

Proposed 32–64 total invitees, scheduled so actual concurrent load is controlled. Eight participants fill one tournament; 64 simultaneous participants require eight eight-seat matches plus service overhead. Total registrations are not concurrency. Begin with measured capacity and increase only after clean operations.

Test small live tournaments, voluntary bot practice, disconnect recovery, different compositions, repeated matches and language/device variations. Have one clear bug channel and a structured report template including build ID, match ID, approximate time, steps and consented logs.

### Fix and expand

Triage crashes/economy/privacy/progression first, then readability, balance and cosmetic issues. Freeze content for a candidate and avoid multiple simultaneous economy rewrites. Preserve a known-good build, patch notes and rollback path. Repeat impacted gates after every change.

Evaluate return-to-play and completion with explicit denominators and small-sample limits. Do not declare product-market fit from a handful of friendly testers or equal bot win rates.

**Exit:** enough observed real play to decide whether to expand, revise the design or address a specific bottleneck. Wider/open beta remains a separate go/no-go decision.

## 13. What to work on immediately after the head task

1. Audit and play the current packaged 24-hero candidate at normal speed.
2. Diagnose timeouts/selection behavior and fix the most disruptive reproducible issue.
3. Run a physical 2H6B test and start the actual remote eight-player path.
4. Integrate one complete Ada in parallel, then review representative body families before batch polish.

Do not make completion of Ada's artistic study a prerequisite for steps 1–3. Do not mistake permission to use existing art internally for permission to call it polished beta content.

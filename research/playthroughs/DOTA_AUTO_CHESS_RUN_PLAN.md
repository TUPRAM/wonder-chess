# Dota Auto Chess — original plan and execution note

**Execution update, 6 September 2026:** one match completed in the standalone Auto Chess client opened by the user, through Epic, after its identity was disclosed. Result: first of eight, round 42, approximately 48 min 40 sec. See [findings](runs/next-dota-auto-chess/findings.md), [gallery](runs/next-dota-auto-chess/gallery.md) and [session](runs/next-dota-auto-chess/session.json). The historical preparation plan below remains for provenance; its not-yet-run inventory statements describe preparation, not current execution.

**Original preparation plan:** On the next requested execution turn, play one actual complete match of Dota Auto Chess through Computer Use and extract a few evidence-backed design lessons for Wonder Chess. Approximately 40 minutes is a planning estimate, not a timer that ends a live match. Installation state, supported modes, rules and controls must be verified from the actual application rather than assumed here.

Use `research/playthroughs/runs/next-dota-auto-chess/` for the root-owned run manifest, observation CSV, screenshots and findings. The root's README/templates own filenames and field definitions; do not create a competing schema. Keep Wonder Chess source, assets, canonical data, balance and existing acceptance evidence unchanged.

The preparation inventory reported a Steam shortcut but no Dota-specific entry or running Steam/Dota window. Installation and playability are **NOT_YET_VERIFIED**, not “missing.” The selected research game remains Dota Auto Chess. The next execution must verify its actual launch path and available mode.

## Before entering a match

1. Read the current Computer Use instructions and inventory the actual available apps/tools. Confirm which installed application and mode is Dota Auto Chess; do not substitute a different auto-battler because its name or menu is similar. Record the visible title/version or workshop identification when available. A hidden version remains unknown.
2. Select the exact game window and record its process/window identity, visible resolution and initial screen. Check that a fresh capture is legible and includes the phase timer, shop, bench, board and economy when those appear. Native screenshots and input must address the same window.
3. **Prove control before queueing.** Use a harmless reversible menu interaction visible in the fresh capture, such as opening and closing a displayed help/options panel. Observe → perform one action → take a fresh capture → verify the change. Test the actual pointer/input path, not merely a successful screenshot. Do not use an unknown shortcut or a match-start button for this test. If input is blocked, stale or directed at another app, stop before queueing and record the exact tool error/window state. Existing authorization does not make an untargetable window targetable.
4. Inspect the currently offered modes. Prefer a private/bot or unranked run suitable for one player **only if the actual UI offers it and its launch requirements are met**. Record the exact displayed mode and whether other seats are bots, humans or unknown. Do not claim an eight-seat bot match from appearance alone. If only ranked play, missing content, a download, purchase, account step or inaccessible lobby prevents the intended run, report the concrete blocker instead of inventing a supported mode or changing account/security settings.
5. Confirm the available basic controls from visible help/tooltips and the chosen mode: purchase, select, place/move, sell, reroll, leveling, scouting and exit/spectate. Do not import Wonder Chess hotkeys or costs into Dota Auto Chess. Set up the root's evidence destination before queueing, then enter just one match.

## Play the match first

Most of the session should be actual play. Buy useful affordable units, keep the legal deployment filled, position a plausible frontline and ranged/support backline, and adapt to visible shops, upgrades, traits and opponents. Inspect the rules when needed; do not pursue a predetermined composition or guess that this game's economy matches Wonder Chess. Avoid intentionally throwing the match to complete an observation checklist. Do not send chat messages or alter another player's controls.

Use the same interaction loop throughout: **fresh observation → one intended action → fresh observation → verify the visible result**. Before spending, locate the current item, cost, gold and capacity. After spending or moving, check the actual offer/bench/board/gold change; an issued click is not a confirmed purchase. After a phase change, panel switch, modal or resize, reacquire targets. If an action fails, inspect the reason and retry only against the current state. Do not chain blind clicks or reuse old screenshot coordinates through changing shops.

| Match situation | Adaptive attention and cadence |
|---|---|
| Early preparation | Learn the live controls while securing the basic team. Read the timer first, then prioritize purchase/deployment over tooltips or evidence notes. Refresh after every consequential action. |
| Later preparation | Decide the next one or two goals from current gold, board capacity, duplicates and visible traits, then execute them separately with confirmation. When little preparation time remains, finish reliable legal actions and return to the board; defer notes and optional browsing. |
| Combat | Observe target choice, attack/skill readability, shields/healing, ownership and why the fight turns. Use longer observation intervals while no action is needed—roughly 5–10 seconds if the visible timer permits—then shorten them near resolution. Capture a meaningful cue, not every attack. |
| Transition/settlement | Refresh promptly to see the result, health/economy update, new shop and next timer. Record the changed state during a safe pause rather than missing the next preparation. |
| Elimination | Capture actual placement and the available choices. Continue spectating the same match through final results if the UI supports it. If it does not, preserve the eliminated-player result and explicitly mark full-tournament observation unavailable. |
| Final results | Capture standings, the player result and any explanation/replay/return options actually offered. Confirm the match ended before leaving. Finish this run rather than starting another to fill evidence gaps. |

The suggested intervals are upper-level pacing guidance, not fixed sleeps: tool latency and the visible timer govern the next action. Do not idle through an entire unknown combat/transition. Keep user progress updates brief at safe moments, without replacing play with minute-by-minute narration. If the match extends beyond the approximately 40-minute estimate, continue to its actual end unless the user stops the run or a concrete obstacle makes continuation impossible. Record real elapsed time.

## Observe the patterns relevant to Wonder Chess

Use `docs/UI_AUDIO_AND_ONBOARDING.md` as the question list, not a demand that Dota Auto Chess implement identical rules. Focus on a few moments that reveal whether a player can understand and act:

| Design question | Useful first-hand evidence |
|---|---|
| What is actionable now? | Preparation/combat distinction, timer urgency, selected-unit state, capacity and placement feedback. |
| Can the shop explain an economic choice? | Cost/affordability, purchase confirmation, duplicate/upgrade feedback, full bench, lock/reroll/level tradeoffs actually encountered. |
| Do traits and inspection help formation decisions? | Counts/thresholds, highlighted recipients, tooltip readability and a visible team change after acting. |
| Can a busy fight be read? | Team identification, frontline/support silhouettes, health versus shield, skill windup/release/impact, clutter and audio cues if actually audible. |
| Does scouting preserve orientation? | Entry to another board, what information is public, return-home path and retained selection/context. |
| Can the player explain the loss and continue? | Settlement/health-loss feedback, recap, elimination/spectating and final-result clarity. |

Observe ordinary opportunities during the match. A feature not encountered is **not observed**, not absent. Do not deliberately provoke costly errors or abandon sound play merely to test every question. Only claim audio impressions when the actual output is audible through the available tools; otherwise label them unreviewed.

## Lightweight evidence and interpretation

Aim for roughly **20–35 useful event-based screenshots**, a soft target rather than a quota. Prefer the verified mode/start, a few early buying/placement decisions, an upgrade or trait change, meaningful mid/late economy decisions, a readable fight/skill moment, scouting/return, a notable loss, elimination/spectating and final results. Capture before/after pairs when they establish an important change. Skip redundant images; fewer real useful captures are better than missing play to hit a count. Do not invent a missing event or replay a match solely to pad coverage.

Use the root-owned files in the run directory:

- `session.json`: starts `PLANNED`, with actual timestamps/result null until observed; records run identity, actual mode and outcome.
- `observations.csv`: `event_id, recorded_utc, elapsed_seconds, round, phase, topic, observed_fact, action, rationale, observed_result, screenshot_ids, confidence, wonder_chess_hypothesis`.
- `screenshots/raw/` and `screenshots/index.jsonl`: original captures and their source/window/time/round/hash metadata. The root's `evidence.mjs` `saveCapture` helper saves original returned screenshot bytes; it performs no UI automation and does not prove that an action succeeded.
- `findings.md`: the post-match account, bounded lessons, uncertainties and later evaluation ideas.

Use actual UTC timestamps and elapsed time; record round/phase only when shown. Each factual event should retain the observed state, one action, visible result and its screenshot reference. Fill short notes during combat or after the match; do not spend preparation time writing prose. Preserve raw files and failed attempts; never rename an illustration or another game's image as this run's screenshot. A capture displayed only in the conversation has no durable screenshot path unless a file was actually saved. Screenshot bytes remain locally ignored; tracked notes retain their evidence references.

Keep factual observations separate from hypotheses and confidence. For example: **observed:** an actual purchase reduced visible gold and placed a named unit on the bench; **hypothesis:** that confirmation may reduce ambiguity in Wonder Chess; **confidence:** medium, based on one event, with alternatives stated. The example is a template, not a claimed event. A proposed lesson must point to its observed moment and explain the player problem it could address. Distinguish “I could not find it in this run” from “the feature does not exist.”

After the match, reconcile the run identity, selected mode, actual start/end, outcome, screenshot paths and unresolved events. Produce a short account of the full match and three to five prioritized Wonder Chess hypotheses, each with evidence and a way to evaluate it later. Report losses, mistakes, input failures and time spent just as directly as successful actions. One match cannot establish balance, the best composition, opponent skill, typical win rate or a generally superior design.

Borrow generic interaction and readability principles only. Do not copy Dota names, lore, models, portraits, music, VFX, proprietary code, exact layouts or asset files into Wonder Chess. Research captures remain labeled private playthrough evidence. No Wonder Chess implementation or balance change is authorized by this preparation plan; findings should become reviewable proposals for a later task.

## Run closeout

Leave the completed result or current exact blocker visible and record whether the process remains open. Return to the game's normal menu after a completed match when practical, without signing out or changing account settings. Preserve all run evidence under the assigned directory. Summarize the actual mode, match outcome, elapsed duration, evidence saved, the most useful observations and any unobserved questions. The completed report must say whether the tournament was observed to final results, only the player's elimination was observed, or a blocker prevented play.

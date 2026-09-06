# Reference game playthroughs

Private, local observation of games played through Computer Use, to inform original Wonder Chess design. This is research, not Wonder Chess release verification. The next session is **one Dota Auto Chess match**, estimated by the user at about 40 minutes. Preparation is complete when the workspace and evidence workflow are ready; no match has started.

## Next run

- [Execution plan](DOTA_AUTO_CHESS_RUN_PLAN.md)
- [Session record](runs/next-dota-auto-chess/session.json): scope, actual start/end times, mode, result, tool checks and interruptions.
- [Observation log](runs/next-dota-auto-chess/observations.csv): visible facts, actions, reasoning, outcomes and screenshot references.
- [Design findings](runs/next-dota-auto-chess/findings.md): a short illustrated debrief and proposed Wonder Chess experiments.
- `runs/next-dota-auto-chess/screenshots/raw/`: original Computer Use captures.
- `runs/next-dota-auto-chess/screenshots/annotated/`: optional clearly labeled derivatives; retain originals.
- `runs/next-dota-auto-chess/screenshots/index.jsonl`: one provenance entry per saved original image.

`next-dota-auto-chess` is a reserved run folder. Keep its stable path for the first session; set its actual timestamps when play begins. Create a fresh `YYYY-MM-DD_HHMMSS_dota-auto-chess` folder for later matches. Never reset or reuse a populated session as a new match. Notes and the screenshot index are versioned; raw images, derivatives and optional video stay local and are ignored by Git. Original game imagery is private reference material, not an asset source for Wonder Chess or permission to publish it.

Update session status as work actually happens: `PLANNED` → `PREFLIGHT` → `IN_PROGRESS` → `COMPLETED`, or `PARTIAL` / `BLOCKED` with the exact reason. Record the played-match endpoint separately from `tournament_end_observed`. A loss can be a completed playthrough; an interrupted input session must not be recorded as a completed match. Retain prior notes and interruption timestamps when resuming.

## Logging without losing preparation time

Use event IDs `OBS-001`, `OBS-002`, etc. Capture important changes, not every click: first shop, first deployment, a merge, trait activation, economy tradeoff, scouting, formation change, readable or confusing combat, elimination and results. Aim for roughly 20–35 useful images, with no quota. Play takes priority over a photo opportunity. Keep brief notes during automatic combat and expand them after the match.

CSV columns:

| Field | Meaning |
|---|---|
| `event_id`, `recorded_utc` | Stable observation ID and actual ISO UTC note time. |
| `elapsed_seconds`, `round`, `phase` | Time since actual match start and visible game state; leave unknown values empty. |
| `topic` | For example shop, economy, placement, synergy, readability, pacing, scouting, feedback or results. |
| `observed_fact` | What was visible, without assuming a hidden rule or cause. |
| `action`, `rationale`, `observed_result` | What I tried, why, and what visibly happened. Record missed/rejected inputs and uncertain outcomes honestly. |
| `screenshot_ids` | IDs from `screenshots/index.jsonl`, separated by semicolons; empty if no photo exists. |
| `confidence` | High for directly readable facts, medium for a plausible interpretation, low for an uncertain reading. |
| `wonder_chess_hypothesis` | A proposed original design improvement, kept separate from the observed fact. |

Use `JSON.stringify` or a CSV writer when logging programmatically; quote CSV values containing commas/newlines/quotes. Never fill a missing observation from game lore or a later guess. Mark retrospective notes as such in `observed_fact`. A screenshot can support layout and a visible state; it cannot establish audio quality, continuous animation, frame rate or causation. A single match is qualitative research, not a balance study.

## Saving a real Computer Use capture

Read the installed [Computer Use skill](<C:/Users/iputu/.codex/plugins/cache/openai-bundled/computer-use/26.901.51231/skills/computer-use/SKILL.md>) before the next run; refresh its path from the available-skills list if the plugin updates. The helper below only writes an already returned screenshot to disk. It does not capture the screen, send input, inspect game memory, or control any application.

In the persistent `node_repl` session, select exactly one game window returned by `sky.list_apps()` / `sky.list_windows()`. Observe first, inspect the displayed image, then decide whether to save it or act. Import the local helper once:

```javascript
globalThis.playthroughEvidence = await import('file:///C:/Users/iputu/Documents/Wonder%20Chess/research/playthroughs/evidence.mjs');
globalThis.dacRun = 'C:/Users/iputu/Documents/Wonder Chess/research/playthroughs/runs/next-dota-auto-chess';
```

Capture with `sky.get_window_state` using the actual selected window. Record `new Date().toISOString()` immediately after the tool returns. Then save the selected original image for the user's requested archive, without re-emitting or decoding it for inspection:

```javascript
// dacState is the actual returned state; dacObservedAtUtc is its recorded time.
nodeRepl.write(JSON.stringify(await playthroughEvidence.saveCapture({
  runDirectory: dacRun,
  state: dacState,
  observedAtUtc: dacObservedAtUtc,
  tag: 'shop-before-purchase',
  round: null,
  elapsedSeconds: null
})));
```

Replace null context only when observed. If the state contains multiple screenshots, inspect them and pass the intended `screenshotIndex` explicitly. The helper refuses stale-directory overwrites, unsupported image signatures and malformed data. It writes original PNG/JPEG bytes with an exclusive filename and appends the actual time, source window, capture ID, dimensions when provided, byte count and SHA256 to `screenshots/index.jsonl`. One operator owns each run; do not save concurrently.

The file-writing helper passed [ten local checks](preparation-check.json) with synthetic image fixtures, which are not game evidence. Actual Dota capture/export, controls, installed game version, accessible mode and continuous play remain **NOT_RUN** until the next session's preflight. No external game screenshots have been recorded in this prepared folder.

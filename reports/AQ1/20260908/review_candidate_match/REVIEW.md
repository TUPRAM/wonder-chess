# AQ1 candidate board review

**Real Unreal board integration is visible, with art acceptance still open.** This lane inspected 16 original candidate screenshots: all 15 combat-start captures for rounds 1-15 plus Ada's skill capture. It also inspected the original canonical round-9 control and five unaltered native crop derivatives. This is sparse screenshot inspection, not continuous match playback, manual human testing or audio review.

`engine_candidate_match_r01` ran current `UnrealEditor.exe -game` with uncooked candidate content, scripted seat 0 and seven bots, normal simulation speed 1, seed **828301**, `-WCFollowHero=0`, `-WCShots`, and a requested 600-second exit. Process 68392 started 2026-09-08T02:31:34.0983701Z and exited **0** at 02:41:56.0294848Z. Startup and shutdown make this different from 600 seconds of sampled match time. Final session match elapsed was 590.819489 seconds. This was not a packaged executable.

| Evidence | Result |
|---|---|
| Valid match snapshots | 1,206: preparation 276, combat 808, settlement 122 |
| Rounds reached | 1-15; completed settlement records for 1-14 |
| Final state | Round 15 combat, complete=false, aborted=false, timed exit requested |
| Elimination / restart | Neither demonstrated; all eight seats alive, seat 0 at 1 HP |
| Eight unfinished neutral encounters | 76 saved states, rounds 1,2,3,5,10,15 |
| Ada actual-visible flag with selected encounter at least 12 living | 69 saved states, rounds 7,8,9,11,12,13,14 |
| Session maximum | 12 living rendered units, 80 living logical units, 8 simultaneous encounters |
| Saved images | 62 PNGs: 15 combat, 14 preparation, 14 settlement, 18 skill, 1 lobby |
| Candidate loading errors | Empty launch record list |
| Timing samples | Zero in frame/game/render/GPU channels; no performance inference |

The followed-encounter count and Ada actual-visible flag are distinct instrumentation fields; they do not recount all rendered units at every snapshot. The round-9 PNG independently shows twelve pieces. Eight live neutral encounters represent eight actual simulations with one observed board, not eight rendered viewports.

**Best comparison:** `match-1-seat-0-pid-68392-phase-1-round-9.png`. Ada faces the camera at the center just above the board split. `matched_round9_board.png` places the actual baseline and candidate crops side by side using the same seed, round and board layout. The candidate's breastplate and shield volumes read more coherently than the fragmented baseline. Navy, ivory and steel preserve the guardian identity, and Ada keeps a recognizable board footprint.

Round 11 shows both a friendly rear Ada at the left side and an enemy frontal Ada at the right. Team disks remain visible. At this scale, there is no gross missing candidate material or detached equipment apparent. The normal board images are too small to approve facial anatomy, grip contact or fine costume intersections; the known close-up/gallery defects remain open. Round 4 also visibly includes `Preparing SoundWaves (2)` and `Preparing Static Meshes (1)` debug messages, a limitation of this uncooked session.

Ada's `active-def-0.png` occurs in round 2 against the Thorn watch neutral wave. The actual image shows the shield raised and `PERISAI 200`; the accompanying skill record contains shield 20000 fixed-point units. The capture is requested on observed cast recovery and supplied by the next rendered frame. It does not establish exact contact timing or the full effect sequence.

One integrity failure remains recorded: `WC_EVIDENCE_WRITE_FAILED` at **02:39:47.454 UTC** for the match snapshot JSONL. It falls within the largest saved-record interval, lines 956-957, **02:39:46.934 to 02:39:47.944 UTC**, a **1.010247-second** gap in round-12 combat. This is the only interval over 0.75 seconds; all saved rows parse and timestamps are monotonic. The periodic recorder schedules approximately every 0.5 seconds, so a missing attempted record is consistent with the warning. The reviewer read the mutable JSONL during the run before stopping at the parent's instruction; reader contention is possible, but the cause was not proven. No log or missing record has been repaired or concealed.

The expected round-15 preparation PNG is absent. Round-15 preparation exists in recorded states and its combat PNG exists. All 18 recorded skill screenshot paths exist. Counts and integrity limitations must not be converted to an entirely clean capture pass.

`run_summary.json` includes final launch/session fields, exact snapshot gaps, the original warning, skill record and hashes of the completed source evidence. `snapshot_summary_rows.json` retains compact per-record fields. `review.json` contains the 16 viewed candidate PNG hashes, and `derivative_manifest.json` records crop provenance. All source artifacts remain unchanged.

**Status: board visual comparison completed; incomplete tournament and open art defects.** Packaged acceptance, full human play, elimination/spectating/restart, two-machine LAN, continuous video/audio review, performance cost and Pram's character/budget approval are not established by this visual run.

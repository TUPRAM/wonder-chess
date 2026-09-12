# AQ1 baseline match visual review

Actual uncooked Unreal `-game` capture with scripted seat 0 and seven bots, seed **828301**. Preserve this seed for a later candidate comparison. This run is visual evidence only; it does not demonstrate packaged or manual human play.

## Reach and boundaries

- 1,202 snapshot rows: preparation 278, combat 805, settlement 119. Reached rounds 1–15; settlement captured for rounds 1–14. Final state: round 15 combat, `complete=false`, requested timed exit, process exit 0. No terminal tournament result, elimination, or restart was demonstrated.
- Eight unfinished neutral encounters were concurrently present in 75 sampled states across rounds **1, 2, 3, 5, 10, 15**. These are sampled states, not 75 separate tournament runs. Individual screenshots show one selected board; concurrency comes from the authoritative snapshot data.
- Maximum followed encounter living count 12; 69 snapshots also report followed Ada actually visible at a living count of at least 12.
- Saved 63 screenshots. This review visually inspected exactly eight originals: combat rounds 7, 9, 11, 13, 10, 15 and skill definitions 0 and 22. Other screenshots were not visually inspected by this reviewer.
- No performance result: the timing channels contain zero samples, and other GPU work was concurrent. Audio was not listened to.

## Recommended before controls

**Best front-facing normal board control:** `../engine_before_match/match-1-seat-0-pid-2120-phase-1-round-9.png`. The transition record reports 12 living units and followed Ada visible, selected unit 1227882573. Ada appears just above the central board split, facing camera with navy shield/gold crest visibly separated from pale armor. Her shield identity survives the small board size, but facial forms and grip detail do not resolve; the armor reads as chunky pale plates. This is an initial combat layout, not a dense overlapping melee.

**Useful alternatives:** round 11 has a clear front-facing shield hero near the board right side plus another Ada seen from behind at left; round 13 has Ada isolated at left seen mostly from behind; round 7 has 12 living units in a central cluster. These alternate orientations expose how similar the pale shoulders and straight, narrow navy lower silhouette become at board scale. Do not infer silhouette uniqueness or clipping clearance from one frame.

**Ada skill control:** `../engine_before_match/match-1-seat-0-pid-2120-active-def-0.png`, round 2. Actual frame shows Ada from behind near center-right with `PERISAI 200` text. It proves a captured shield event presentation during a monster encounter, not exact Active contact pose or visual approval of the animation. The recorder requests the next rendered frame after the observed recovery state.

**Later moving battle context:** `../engine_before_match/match-1-seat-0-pid-2120-active-def-22.png`, round 13. Followed Ada is at upper-left with shield text; telemetry at request reports 11 living in the encounter. This image contains a `Preparing SoundWaves (1)` overlay. Keep the original as-is and do not treat the overlay as polished release UI or audible verification.

**Neutral controls:** combat round 10 shows Prowler path and round 15 Bell ward, each with monster labels and ten living in the selected encounter at request. Round 15 visibly has seat 0 at 1 HP. Neither image proves all eight fights visually; that evidence is the snapshot count above.

Screenshots are saved on a subsequent rendered frame after telemetry capture, so numerical counts describe the request state and can differ after deaths. `review.json` records image hashes; `snapshot_summary_rows.json` preserves the compact parse of every source snapshot.

No numeric art score, completed art assertion, tournament pass, LAN claim, or performance claim is made.

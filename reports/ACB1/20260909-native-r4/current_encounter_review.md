# Current r4 encounter review

**Scope: current run only; partial tournament at the fixed acquisition cutoff.** PID `36432`, match namespace `1`, authoritative seed `846842640`. This is a read-only telemetry review. No game/UI action, compile, replay, or gameplay mutation was performed by this reviewer.

The round-14 Highbanner versus Hearthkeeper encounter **did not time out**. It completed with Highbanner winning and four surviving units. The global round timer continued while another encounter was unfinished. The actual round-14 timeout was Starwatch versus Sunstride. The earlier observation of multiple visible models near timer expiry was an investigation lead; model count is not evidence of living-unit count because downed models may remain.

## Evidence boundary

- Read exactly the first **65,309,416 bytes / 2,277 complete JSONL records** of [the current snapshot stream](normal-speed/match-1-seat-0-pid-36432-snapshots.jsonl). No malformed lines were found in this prefix. All records match the stated PID, namespace, and seed.
- Prefix SHA-256: `01d7d485e788c13dc5fa24f0235338e653bfafcac0fe909d048ec3b26931a4d7`. The live file may subsequently grow; this hash describes the reviewed byte prefix, not its future full contents.
- Snapshot UTC span: `2026-09-08T16:49:52.640Z` to `2026-09-08T17:08:39.732Z`. Cutoff is **2026-09-09 01:08:39.732 Singapore time**, round **21 preparation**. Completed recaps cover rounds **1–20**. Later outcomes are not included.
- The session metadata sampled during this review recorded Unreal `5.7.4-51494982+++UE5+Release-5.7`, simulation multiplier `1`, network mode `0`, and an unfinished, non-aborted match. This review does not independently certify the executable/source hash relationship or performance.
- Snapshot content digest `95509d001ca0e6c55fa64a616df6e2e9a01a3809a9b9c82d9bd0a725dad3a1ec` matches the currently checked generated catalog digest. Hero names use its verified alpha definition order. Health/damage values below are **centipoints (cp), 100 cp = 1 displayed HP**; captain damage uses its own integer health scale.
- `public.recap.encounters` supplies settled outcomes. `public.encounters` supplies per-encounter ticks, unit states, cumulative effective totals, and rolling event windows. Repeated snapshots/recaps were deduplicated by round and encounter; repeated events were deduplicated by their entire serialized field tuple.

## Outcome coverage

**104 completed encounters**: 52 PvE, 47 ordinary PvP, and 5 ghost encounters. Recorded timeouts: PvE 0, PvP 9, ghost 0. These are descriptive counts from one partly agent-controlled run, not balance or acceptance rates.

PvE means `kind=neutral`, with side B the listed neutral wave. PvP means `kind=pvp`. Ghost means `kind=ghost`: side A is the recipient and side B is a donor copy; the recorded donor-side captain damage is zero. No donor-side damage is inferred from its copied units being defeated.

Names: 0 = Captain 1; 1 = Rowanfield; 2 = Starwatch; 3 = Hearthkeeper; 4 = Sunstride; 5 = Gemseeker; 6 = Highbanner; 7 = Wayfinder.

In the table, survivors and captain damage are ordered **A / B**, exactly as recorded. `B wave` denotes the neutral wave, not seat -1 as a player. All rows below have `complete=true`.

| Round | Kind | Side A | Side B | Winner | Survivors A/B | Captain damage A/B | Timeout |
|---:|---|---|---|---|---:|---:|---|
| 1 | PvE | Captain 1 | wc_wave_01 | wc_wave_01 | 0 / 2 | 0 / 0 | no |
| 1 | PvE | Rowanfield | wc_wave_01 | Rowanfield | 4 / 0 | 0 / 0 | no |
| 1 | PvE | Starwatch | wc_wave_01 | Starwatch | 4 / 0 | 0 / 0 | no |
| 1 | PvE | Hearthkeeper | wc_wave_01 | Hearthkeeper | 4 / 0 | 0 / 0 | no |
| 1 | PvE | Sunstride | wc_wave_01 | Sunstride | 4 / 0 | 0 / 0 | no |
| 1 | PvE | Gemseeker | wc_wave_01 | Gemseeker | 4 / 0 | 0 / 0 | no |
| 1 | PvE | Highbanner | wc_wave_01 | Highbanner | 3 / 0 | 0 / 0 | no |
| 1 | PvE | Wayfinder | wc_wave_01 | Wayfinder | 4 / 0 | 0 / 0 | no |
| 2 | PvE | Captain 1 | wc_wave_02 | wc_wave_02 | 0 / 2 | 0 / 0 | no |
| 2 | PvE | Rowanfield | wc_wave_02 | Rowanfield | 4 / 0 | 0 / 0 | no |
| 2 | PvE | Starwatch | wc_wave_02 | Starwatch | 4 / 0 | 0 / 0 | no |
| 2 | PvE | Hearthkeeper | wc_wave_02 | Hearthkeeper | 4 / 0 | 0 / 0 | no |
| 2 | PvE | Sunstride | wc_wave_02 | Sunstride | 4 / 0 | 0 / 0 | no |
| 2 | PvE | Gemseeker | wc_wave_02 | Gemseeker | 4 / 0 | 0 / 0 | no |
| 2 | PvE | Highbanner | wc_wave_02 | Highbanner | 4 / 0 | 0 / 0 | no |
| 2 | PvE | Wayfinder | wc_wave_02 | Wayfinder | 4 / 0 | 0 / 0 | no |
| 3 | PvE | Captain 1 | wc_wave_03 | wc_wave_03 | 0 / 3 | 0 / 0 | no |
| 3 | PvE | Rowanfield | wc_wave_03 | Rowanfield | 5 / 0 | 0 / 0 | no |
| 3 | PvE | Starwatch | wc_wave_03 | Starwatch | 5 / 0 | 0 / 0 | no |
| 3 | PvE | Hearthkeeper | wc_wave_03 | Hearthkeeper | 5 / 0 | 0 / 0 | no |
| 3 | PvE | Sunstride | wc_wave_03 | Sunstride | 5 / 0 | 0 / 0 | no |
| 3 | PvE | Gemseeker | wc_wave_03 | Gemseeker | 5 / 0 | 0 / 0 | no |
| 3 | PvE | Highbanner | wc_wave_03 | Highbanner | 5 / 0 | 0 / 0 | no |
| 3 | PvE | Wayfinder | wc_wave_03 | Wayfinder | 5 / 0 | 0 / 0 | no |
| 4 | PvP | Captain 1 | Wayfinder | Wayfinder | 0 / 5 | 7 / 0 | no |
| 4 | PvP | Rowanfield | Highbanner | Highbanner | 0 / 4 | 6 / 0 | no |
| 4 | PvP | Starwatch | Gemseeker | Gemseeker | 0 / 3 | 5 / 0 | no |
| 4 | PvP | Hearthkeeper | Sunstride | Sunstride | 0 / 3 | 5 / 0 | no |
| 5 | PvE | Captain 1 | wc_wave_05 | wc_wave_05 | 0 / 3 | 2 / 0 | no |
| 5 | PvE | Rowanfield | wc_wave_05 | Rowanfield | 5 / 0 | 0 / 0 | no |
| 5 | PvE | Starwatch | wc_wave_05 | Starwatch | 5 / 0 | 0 / 0 | no |
| 5 | PvE | Hearthkeeper | wc_wave_05 | Hearthkeeper | 5 / 0 | 0 / 0 | no |
| 5 | PvE | Sunstride | wc_wave_05 | Sunstride | 5 / 0 | 0 / 0 | no |
| 5 | PvE | Gemseeker | wc_wave_05 | Gemseeker | 5 / 0 | 0 / 0 | no |
| 5 | PvE | Highbanner | wc_wave_05 | Highbanner | 5 / 0 | 0 / 0 | no |
| 5 | PvE | Wayfinder | wc_wave_05 | Wayfinder | 5 / 0 | 0 / 0 | no |
| 6 | PvP | Captain 1 | Rowanfield | Rowanfield | 0 / 5 | 7 / 0 | no |
| 6 | PvP | Starwatch | Hearthkeeper | Hearthkeeper | 0 / 3 | 5 / 0 | no |
| 6 | PvP | Sunstride | Highbanner | Highbanner | 0 / 4 | 6 / 0 | no |
| 6 | PvP | Gemseeker | Wayfinder | Gemseeker | 4 / 0 | 0 / 6 | no |
| 7 | PvP | Captain 1 | Hearthkeeper | Hearthkeeper | 0 / 6 | 8 / 0 | no |
| 7 | PvP | Rowanfield | Starwatch | Rowanfield | 4 / 0 | 0 / 6 | no |
| 7 | PvP | Sunstride | Wayfinder | Wayfinder | 0 / 4 | 6 / 0 | no |
| 7 | PvP | Gemseeker | Highbanner | Gemseeker | 1 / 1 | 0 / 3 | yes |
| 8 | PvP | Captain 1 | Gemseeker | Gemseeker | 0 / 6 | 8 / 0 | no |
| 8 | PvP | Rowanfield | Sunstride | Rowanfield | 4 / 0 | 0 / 6 | no |
| 8 | PvP | Starwatch | Wayfinder | Wayfinder | 0 / 3 | 5 / 0 | no |
| 8 | PvP | Hearthkeeper | Highbanner | Highbanner | 0 / 1 | 3 / 0 | no |
| 9 | PvP | Captain 1 | Starwatch | Starwatch | 0 / 6 | 8 / 0 | no |
| 9 | PvP | Rowanfield | Hearthkeeper | Rowanfield | 2 / 1 | 0 / 4 | yes |
| 9 | PvP | Sunstride | Gemseeker | Gemseeker | 0 / 3 | 5 / 0 | no |
| 9 | PvP | Highbanner | Wayfinder | Highbanner | 4 / 0 | 0 / 6 | no |
| 10 | PvE | Captain 1 | wc_wave_10 | wc_wave_10 | 0 / 2 | 2 / 0 | no |
| 10 | PvE | Rowanfield | wc_wave_10 | Rowanfield | 6 / 0 | 0 / 0 | no |
| 10 | PvE | Starwatch | wc_wave_10 | Starwatch | 6 / 0 | 0 / 0 | no |
| 10 | PvE | Hearthkeeper | wc_wave_10 | Hearthkeeper | 6 / 0 | 0 / 0 | no |
| 10 | PvE | Sunstride | wc_wave_10 | Sunstride | 6 / 0 | 0 / 0 | no |
| 10 | PvE | Gemseeker | wc_wave_10 | Gemseeker | 6 / 0 | 0 / 0 | no |
| 10 | PvE | Highbanner | wc_wave_10 | Highbanner | 6 / 0 | 0 / 0 | no |
| 10 | PvE | Wayfinder | wc_wave_10 | Wayfinder | 5 / 0 | 0 / 0 | no |
| 11 | PvP | Captain 1 | Sunstride | Sunstride | 0 / 4 | 6 / 0 | no |
| 11 | PvP | Rowanfield | Gemseeker | Gemseeker | 1 / 3 | 5 / 0 | yes |
| 11 | PvP | Starwatch | Highbanner | Highbanner | 0 / 2 | 4 / 0 | no |
| 11 | PvP | Hearthkeeper | Wayfinder | Hearthkeeper | 2 / 0 | 0 / 4 | no |
| 12 | PvP | Captain 1 | Highbanner | Highbanner | 0 / 6 | 10 / 0 | no |
| 12 | PvP | Rowanfield | Wayfinder | Rowanfield | 3 / 1 | 0 / 7 | yes |
| 12 | PvP | Starwatch | Sunstride | Sunstride | 0 / 2 | 6 / 0 | no |
| 12 | PvP | Hearthkeeper | Gemseeker | Hearthkeeper | 2 / 0 | 0 / 6 | no |
| 13 | PvP | Captain 1 | Gemseeker | Gemseeker | 0 / 6 | 10 / 0 | no |
| 13 | PvP | Rowanfield | Sunstride | Rowanfield | 4 / 1 | 0 / 8 | yes |
| 13 | PvP | Starwatch | Highbanner | Highbanner | 0 / 2 | 6 / 0 | no |
| 13 | PvP | Hearthkeeper | Wayfinder | Hearthkeeper | 2 / 0 | 0 / 6 | no |
| 14 | Ghost | Gemseeker | Highbanner (copy) | Highbanner (copy) | 0 / 4 | 8 / 0 | no |
| 14 | PvP | Rowanfield | Wayfinder | Rowanfield | 4 / 0 | 0 / 8 | no |
| 14 | PvP | Starwatch | Sunstride | Starwatch | 1 / 1 | 0 / 5 | yes |
| 14 | PvP | Hearthkeeper | Highbanner | Highbanner | 0 / 4 | 8 / 0 | no |
| 15 | PvE | Rowanfield | wc_wave_15 | Rowanfield | 6 / 0 | 0 / 0 | no |
| 15 | PvE | Starwatch | wc_wave_15 | Starwatch | 5 / 0 | 0 / 0 | no |
| 15 | PvE | Hearthkeeper | wc_wave_15 | Hearthkeeper | 4 / 0 | 0 / 0 | no |
| 15 | PvE | Sunstride | wc_wave_15 | Sunstride | 6 / 0 | 0 / 0 | no |
| 15 | PvE | Gemseeker | wc_wave_15 | Gemseeker | 5 / 0 | 0 / 0 | no |
| 15 | PvE | Highbanner | wc_wave_15 | Highbanner | 5 / 0 | 0 / 0 | no |
| 15 | PvE | Wayfinder | wc_wave_15 | Wayfinder | 5 / 0 | 0 / 0 | no |
| 16 | Ghost | Highbanner | Rowanfield (copy) | Rowanfield (copy) | 0 / 3 | 7 / 0 | no |
| 16 | PvP | Rowanfield | Starwatch | Rowanfield | 4 / 0 | 0 / 8 | no |
| 16 | PvP | Hearthkeeper | Gemseeker | Gemseeker | 1 / 1 | 5 / 0 | yes |
| 16 | PvP | Sunstride | Wayfinder | Wayfinder | 1 / 1 | 5 / 0 | yes |
| 17 | Ghost | Sunstride | Hearthkeeper (copy) | Hearthkeeper (copy) | 0 / 3 | 7 / 0 | no |
| 17 | PvP | Rowanfield | Hearthkeeper | Rowanfield | 3 / 0 | 0 / 7 | no |
| 17 | PvP | Starwatch | Gemseeker | Gemseeker | 0 / 4 | 8 / 0 | no |
| 17 | PvP | Highbanner | Wayfinder | Highbanner | 2 / 0 | 0 / 6 | no |
| 18 | Ghost | Starwatch | Hearthkeeper (copy) | Starwatch | 2 / 0 | 0 / 0 | no |
| 18 | PvP | Rowanfield | Gemseeker | Rowanfield | 2 / 1 | 0 / 6 | yes |
| 18 | PvP | Hearthkeeper | Wayfinder | Hearthkeeper | 2 / 0 | 0 / 6 | no |
| 18 | PvP | Sunstride | Highbanner | Highbanner | 0 / 4 | 8 / 0 | no |
| 19 | Ghost | Wayfinder | Starwatch (copy) | Wayfinder | 2 / 0 | 0 / 0 | no |
| 19 | PvP | Rowanfield | Hearthkeeper | Rowanfield | 3 / 0 | 0 / 9 | no |
| 19 | PvP | Starwatch | Highbanner | Highbanner | 0 / 3 | 9 / 0 | no |
| 19 | PvP | Sunstride | Gemseeker | Gemseeker | 0 / 5 | 11 / 0 | no |
| 20 | PvE | Rowanfield | wc_wave_20 | Rowanfield | 4 / 0 | 0 / 0 | no |
| 20 | PvE | Hearthkeeper | wc_wave_20 | wc_wave_20 | 0 / 1 | 2 / 0 | no |
| 20 | PvE | Gemseeker | wc_wave_20 | Gemseeker | 2 / 0 | 0 / 0 | no |
| 20 | PvE | Highbanner | wc_wave_20 | Highbanner | 2 / 0 | 0 / 0 | no |
| 20 | PvE | Wayfinder | wc_wave_20 | wc_wave_20 | 0 / 1 | 2 / 0 | no |

## Round 14: Hearthkeeper versus Highbanner correction

- Encounter key: `round=14, a=3, b=6, ghost=false, neutral=false`. Snapshot lines **1724–1812**. First completed record is line **1766**, UTC `2026-09-08T17:04:28.974Z`.
- Final encounter tick **422** = **21.1 simulated seconds**, `complete=true`, `timeout=false`, `winner=1` (Highbanner), survivors **0 / 4**, captain damage **8 / 0**. At first completion the public round timer still had **18,800 ms** remaining.
- Near expiry, snapshot line **1801**, UTC `2026-09-08T17:04:46.729Z`, has public timer **1,050 ms** and this encounter still at completed tick **422**, survivors **[0, 4]**. The snapshot survivor field establishes those four living units; the screenshot model count alone does not.

| Recorded measure | Hearthkeeper (A) | Highbanner (B) |
|---|---:|---:|
| Initial units | 6 | 6 |
| Initial stars | 2, 2, 1, 1, 2, 1 | 2, 2, 2, 2, 2, 2 |
| Initial effective HP (cp) | 723,860 | 813,600 |
| Effective HP lost (cp) | 723,860 | 504,644 |
| Damage absorbed (cp) | 62,000 | 54,000 |
| Effective healing (cp) | 0 | 0 |
| Final HP (cp) | 0 | 308,956 |

Action coverage: **89 snapshot samples, 43 distinct encounter ticks**, tick 1 through 422, largest successive tick gap 12. Each rolling event window covers 40 ticks. The union contains **145 distinct events**: 133 damage, 7 shield, 1 dash, and 4 stat-modifier events. Summed event health loss and absorption exactly reconcile to the final cumulative totals above. The first damage event is at tick 6 and the killing damage is at tick 422.

The records establish a completed attrition fight with a starting effective-health and star-distribution difference. They do not isolate which roster, trait, formation, targeting, or ability choice caused the margin. No claim of balance or optimal bot play follows from this encounter.

## Round 14: actual Starwatch versus Sunstride timeout

Encounter key: `round=14, a=2, b=4, ghost=false, neutral=false`. First completed snapshot is line **1804**, UTC `2026-09-08T17:04:47.918Z`. Final tick **800 = 40.0 simulated seconds**; `complete=true`, `timeout=true`, winner side 0 (Starwatch), survivors **1 / 1**, captain damage **0 / 5**.

| Recorded measure | Starwatch (A) | Sunstride (B) |
|---|---:|---:|
| Initial effective HP (cp) | 755,200 | 857,600 |
| Effective HP lost (cp) | 679,200 | 836,217 |
| Damage absorbed (cp) | 0 | 72,000 |
| Effective healing (cp) | 0 | 0 |
| Final survivor | Tessa, 1 star | Liora, 2 stars |
| Final survivor HP (cp) | 76,000 / 76,000 | 21,383 / 120,600 |

Action coverage: **89 samples, 81 distinct ticks**, tick 1 through 800, maximum gap 12 ticks against the 40-tick event window. The union contains **233 distinct events**: 211 damage, 2 shield, 8 stun, 3 dash, and 9 stat-modifier events. Event-derived HP loss and absorption exactly match both final totals; no heal event is recorded. Thus the effective totals are reconciled across this sampled event stream.

The late fight was still active, not a demonstrated movement deadlock:

- At tick 699 (5,050 ms on the public timer), Starwatch has Finn at 31,165 cp and Tessa at 76,000 cp; Sunstride has Liora at 104,270 cp. Sampled states continue cycling through attack/cast windup and recovery.
- Liora damages Finn at ticks 698, 720, 742, 764, and 792. The tick 792 hit removes Finn's final 1,165 cp. Finn's already released hit still damages Liora by 9,221 cp at tick 795; the source unit being defeated before impact is explicitly compatible with the current catalog's released-packet rule.
- Tessa damages Liora at ticks 694, 719, 745, 757, and 782. At tick 799 Tessa has a new attack windup with releaseTick 804, beyond the cutoff. Liora is in attack recovery; its sampled target still references the now-defeated Finn. That transient target field alone does not prove a stuck target selector.
- The final two survivors occupy Tessa (column 1, row 2) and Liora (column 3, row 6), zero-based logical cells. Their lack of movement in these late samples coexists with confirmed ranged damage. It is not by itself evidence of pathfinding failure.
- The current source timeout rule compares summed surviving HP/maxHP fractions. With one survivor on each side, 1.0 for Tessa exceeds 21,383/120,600 for Liora, consistent with the recorded winner 0. This is a source-reading interpretation consistent with the telemetry, not a separately executed replay of the running binary.

**Conclusion for this encounter:** combat activity continued until the configured timeout with both sides still alive. That is sufficient to explain the recorded timeout condition, but not why the overall fight took 40 seconds or whether any rule/balance change is justified. There is no basis here to blame a freeze, healing loop, missing damage, or pathfinding failure.

## Remaining evidence needed and next action

- For a causal movement/targeting diagnosis, capture every-tick target selection reasons, rejected path/occupancy decisions, and pending action/packet cancellation or release state, or run a controlled source-bound replay of this exact encounter and initial formation. The public stream has sampled unit states and resolved events; it does not expose every decision or path search.
- Reconcile a controlled replay to this run's initial units, effective stats, cells, actions and final totals before changing combat duration, bot behavior, targeting, or balance. This review does not authorize or execute those changes.
- The tournament is partial at this report's cutoff. The parent owner may append final outcomes after the current native run completes. Current 1H7B input was agent-operated, included early sparse player boards and planning pauses as documented in [the native journal](interaction_journal.md); it cannot be promoted to human usability, balance, networking, continuous animation, audio-listening or packaged-release acceptance.
- No screenshots were independently reviewed for this encounter analysis; all live/dead and action statements above come from telemetry. No old run was used as current evidence.

Interpretation references inspected read-only: `game/Source/WonderChessRuntime/Public/Simulation/WonderSimulation.h` (effect/state enums); `Private/WCMatchRuntime.cpp` (rolling event windows and target-side cumulative totals); `Private/Simulation/WonderSimulation.cpp` (timeout assessment); `Private/Simulation/WonderTournament.cpp` (round settlement waits for all encounters); `data/rules.alpha.json` (50 ms ticks, 40 s timeout, 100 cp health scale and released-packet semantics). The three `Private/...` paths are within `game/Source/WonderChessRuntime/`.

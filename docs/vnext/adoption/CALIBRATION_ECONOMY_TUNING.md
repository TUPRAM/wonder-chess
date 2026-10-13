# Calibration, economy and tuning design (Phases 0, 4, 6)

Status: design accepted by the owner on 2026-10-10 (decisions in `README.md` section 5). No code written.

References: **T** = `game/Source/WonderChessRuntime/Private/Simulation/WonderTournament.cpp`
(all match, shop and bot logic lives here), **H** = `.../Public/Simulation/WonderSimulation.h`,
**py** = `tools/vnext/catalog.py`. Line numbers are from the survey of 2026-10-09.

## 1. Phase 0: a baseline that can be trusted

Nothing can be tuned until the bots play the current roster sensibly and the tournament
tool measures the live rule set. Phase 0 fixes the measuring instrument first.

### 0.1 Repair the bots

**Problem.** Bot code decides a unit's role by class name, and the names are from the old
roster (T:149-176, 290-311, 1135-1141):

| Bot code tests for | Current roster has |
|---|---|
| guardian (frontline weight, front row) | tank, fighter |
| priest, healer (support weight) | priest, shaman |
| everything else (damage weight) | assassin, sniper, mage, warlock, engineer, summoner |

So tanks and fighters are valued as damage dealers and placed in the back row. Separately,
the bot's trait score reads two legacy fields that the roster traits leave at zero
(T:181-182), so bots do not see a two-unit trait as worth anything.

**Design.**
- Move the role out of code and into data: each class in the catalogue gets a `bot_role`
  (frontline, damage, support) and a `bot_row` (front, middle, back). The bot reads those.
  A new class can never again be silently mis-handled.
- Proposed mapping: tank and fighter are frontline, front row; assassin is damage, front
  row; priest and shaman are support, back row; sniper, mage, warlock, engineer and
  summoner are damage, back row.
- The trait score reads the same threshold list the fight uses.
- Bots keep the same information as a player. No rule or stat advantage is added.

**Tests.** A bot with a tank and a sniper puts the tank in front. Buying the second member
of a trait raises the bot's evaluation. Existing honesty tests still pass.

### 0.2 Point the tournament tool at the live rules

**Problem.** `tests/runtime/run_vnext_tournament.ps1` builds against the control catalogue.
The balance-experiment program accepts the roster rule set but its script's allowed list
omits it. Output has no per-seat data.

**Design.** The tool takes a rule-set argument (control or roster; roster by default for
balance work, control kept for the regression comparison). It writes, in addition to
today's files:

| New file | One row per | Columns |
|---|---|---|
| `seats.csv` | seat per round | gold, level, health, streak, deployed count, income received |
| `placements.csv` | seat per match | bot profile, final placement, round eliminated |
| `boards.csv` | board unit per seat per round | hero, star, relic |
| `traits.csv` | active trait per seat per round | trait, count, threshold reached |
| `waves.csv` | seat per monster round | wave, won, lost or draw, time taken |
| `ability_share.csv` | hero per fight | basic damage, ability damage, healing, casts |

`tools/vnext/analyze_runs.py` gains a second time figure. Today it reports simulated
minutes, in which bots take about three seconds to prepare. It will also report a
**player-time ceiling**: combat and settlement as simulated, plus the full configured
preparation time for every round.

### 0.3 Baseline run B0

After 0.1 and 0.2, before any balance change: 200 bot tournaments on the roster rule set.
(For scale: 1,000 tournaments took 33 minutes on the six-hero build; the 25-hero cost is
not recorded and will be measured by the first run.) B0 is the reference every later run
is compared against.

### 0.4 The three hero fixes

Ironwall health 1000 to 850; Forge King 845 to about 1050; Tide Caller 1000 to about 1070.
Applied only if the owner approves, as one balance version, followed by a run compared
with B0.

### 0.5 Monsters

Wave health measured in cost-1 health bars (our median 650; the reference's 550):

| Round | Ours | Reference | Note |
|---|---|---|---|
| 1 | 0.3 | 0.5 | |
| 2 | 0.6 | 1.0 | |
| 3 | 1.4 | 2.2 | |
| 5 | 3.2 | - | they have no round 5 |
| 10 (boss) | 13.1 | 5.5 | ours 2.4x heavier |
| 15 | 5.5 | 12.7 | ours lighter than our own round 10 |
| 20 (boss) | 23.4 | 10.9 | ours 2.1x heavier |
| 25 | 14.3 | 14.5 | |
| 30 (boss) | 30.7 | 21.8 | |
| 35 | 17.1 | 18.2 | |
| 40 (boss) | 60.4 | 49.5 | |
| 45 | 27.2 | 36.4 | |
| 50 (boss) | 77.1 | 72.7 | |
| 55, 60 | 41.0, 95.8 | - | |

Readings: openers are lighter than theirs, which fits starting at level 3 with 10 gold.
Late rounds match. The early bosses at 10 and 20 are more than twice as heavy for their
round as the reference's, and each boss round is far harder than the pack round after it.
That may be intended ("bosses give the relic"), but it is untested.

**Design.** No numbers change on this table alone. `waves.csv` from B0 gives the clear
rate of every wave by bots. Target bands to propose once measured: opening rounds above
95% cleared; pack rounds 70-90%; bosses 40-70%, falling with the round. Waves outside
their band are rescaled through `hpScaleBp` and `damageScaleBp`, which exist for this.

Also to reconcile: `production/monsters/MONSTER_ROUNDS_DESIGN.md` states boss health that
the catalogue does not match (Old Tusk 2,600 proposed against 4,500; Glass Queen 3,000
against 5,000; Wonder Heart 9,000 against 8,000). One of the two should be corrected.

### 0.6 Housekeeping

- Restore the eleven stand-ins' planned abilities from the last commit as `design_intent` text.
- Correct the stale line in the in-game guide that says trait bonuses are inactive.

**Phase 0 is done when:** bots place frontliners in front and value two-unit traits, with
tests; the tool runs the roster rules and writes the six new files; B0 exists with a
written summary; the monster clear-rate table exists.

## 2. Phase 4: economy and match rules

### What already exists

| Rule | State |
|---|---|
| Income | `base + pending reward + min(cap, gold at fight start / divisor)`, granted at the start of preparation (T:868-874) |
| Loss damage | Stage value plus one per surviving enemy unit (T:1078). Draw: fixed. Monster loss: fixed |
| Sell | Full refund |
| Shop lock, reroll | Exist |
| Star-up | On purchase, across board and bench |
| Auto-deploy | None. Bots deploy themselves; a person's benched units stay benched |
| Streak | Counted and shown by the solo screen only; includes monster rounds; not saved, not reset on a new match; pays nothing |

### 4.1 Streak income

**Data.** New rule `streakIncome`: a list of steps, proposed `3 -> 1`, `5 -> 2`, `7 -> 3`.

**State.** The seat gains a signed streak counter: positive for wins, negative for losses.
- Player fights only. Monster rounds neither advance nor reset it.
- A draw resets it to zero.
- Income uses its absolute value, so loss streaks pay the same as win streaks.

**Behaviour.** Added in the same place as base income. The solo screen shows the seat's
counter and drops its own.

**Touches.** Catalogue, schema, validator bounds, `Rules`, `Validate`, seat state, restart,
state hash, save format (magic bump), two contract tests that assert the income formula
exactly (`tests/runtime/update_contract_tests.h:240`, `runtime_tests.cpp:236`), income
text on the solo screen, the catalogue site.

**Bots.** They ignore win income today and will ignore streaks. Acceptable for a first
version; teaching them to value a streak is a later tuning item.

### 4.2 Shop odds

Data only. Proposed, against today's and the reference (percent for cost 1/2/3/4/5):

| Level | Today | Proposed | Reference |
|---|---|---|---|
| 3-7 | unchanged | unchanged | close to ours |
| 8 | 15/20/35/25/5 | 15/25/35/22/3 | 20/28/35/16/1 |
| 9 | 10/15/30/35/10 | 12/20/30/32/6 | 20/25/27/25/3 |
| 10 | 5/10/25/40/20 | 10/15/25/38/12 | 15/25/25/29/6 |

Bots do not read the odds, so no bot change. Free experience stays at 2. The owner approved
level 10 at 12% cost-5; the level 8 and 9 rows are the matching taper and await confirmation.

### 4.3 Preparation time

**The arithmetic.** In bot matches on the control catalogue the median match is 46 rounds:
22.8 minutes of fights and 3.75 of settlement, 26.6 minutes that do not depend on the
player. Preparation at 45 s for 46 rounds adds 34.5 minutes: a ceiling of **61 minutes**
against a target of 35-45.

| Option | Preparation total | Ceiling |
|---|---|---|
| Today: 45 s flat, 46 rounds | 34.5 min | 61 min |
| 25 / 30 / 35 s by stage, 46 rounds | 24.8 min | 51 min |
| 20 / 25 / 25 s by stage, 46 rounds | 18.8 min | 45 min |
| 25 / 30 / 35 s by stage, match shortened to about 38 rounds | 20.1 min | about 42 min |

Stages are rounds 1-5, 6-20, 21 on. The ceiling assumes the player uses every second;
the Ready button means real matches run shorter. The numbers are from the control
catalogue with the unrepaired bots, so B0 will replace them.

**Decided.** Stage the timer at 25 / 30 / 35 s **and** shorten the match by raising
late loss damage (4.4) so the median match ends near round 38, then confirm with a run. Time alone cannot reach the target
without making late turns feel rushed for a ten-unit board.

**Data.** `preparationMs` becomes `preparationStages`, the same shape as `lossStages`.
The first round keeps its own longer value. Bots are safe down to about 10 s.

### 4.4 Loss damage

Already stage plus survivors. Two changes:
- Summoned units are excluded from the survivor count (with S9).
- The stage values (1 / 3 / 5 / 8 today) are the lever for match length. Candidates to
  test against B0: 2 / 4 / 6 / 9 and 2 / 4 / 7 / 10. Chosen by measured rounds per match.

### 4.5 Auto-deploy (decided: yes)

When preparation ends, each seat with free board capacity has benched units placed until
the level cap is reached.
- Order: lowest bench slot first.
- Cell: the free cell nearest the centre of the back row, so an unplaced unit is at least
  not in front.
- Applies to every seat. Bots already deploy fully, so their games do not change.
- The solo screen shows a one-line message naming what was placed.

### 4.6 Goblin gold

The Goblin trait part from S3 uses the same pending-reward path as win income, paid at
the next preparation.

### 4.7 Not in this phase

- **Shared pool (decided: not now).** It would touch shop refresh, sell, merge, the state hash,
  the save format, a validator rule that requires independent shops (py:81) and two tests
  that assert shop independence. Left out.
- **Relics.** The cap of 3 and the round-60 draft that cannot fire are left for the relic discussion.
- **Bounties, items, talents.** Skipped.

**Phase 4 is done when:** each rule has tests; contract tests are updated; a 200-tournament
run reports rounds per match, the player-time ceiling, gold and level by round, and the
share of matches ending inside 35-45 minutes, with the gap stated if it misses.

## 3. Phase 6: the tuning loop

Run after Phase 0, after every slice, and after Phase 4.

### Each run

1. Bump `balance_version`; regenerate and check the catalogue.
2. 200 roster tournaments, fixed seed range, same bots.
3. `analyze_runs.py` writes a report to `reports/vnext/balance/<version>/` with the tables
   below and a diff against the previous run and against B0.
4. Anything outside its band is listed with a proposed change. The owner accepts or rejects.
5. Accepted changes become the next balance version. One kind of change per version
   where possible, so a movement can be traced to its cause.

### What is measured, and the proposed bands

| Measure | Band | Why |
|---|---|---|
| Hero average placement when fielded | 4.0-5.0 (8 seats, 4.5 is neutral) | No hero is a free win or a trap |
| Hero pick rate within its cost | within 0.5x-2x of the cost's mean | Finds ignored and auto-picked heroes |
| Trait: placement when active at 2 and at 4 | 3.8-5.0 | 4 members should beat 2, but not decide the match |
| Trait: share of final boards with it active | above 5% each | Every trait is reachable |
| Ability share of a hero's damage | reported, then banded once the one-third ability weight is in | Checks the attack or ability balance chosen |
| Seconds to first cast, by cost | reported | Mana pacing |
| Median rounds per match | 36-42 | Feeds match length |
| Player-time ceiling | 35-45 min | The project target |
| Fights ending by timeout | under 3% | Stalls (today 82 of 1,996, 4.1%) |
| Wave clear rate | bands in 0.5 | Monster difficulty |
| Gold and level by round, median and spread | reported | Economy pacing |

With 200 tournaments a hero fielded by a third of seats has roughly 500 placements, which
puts the uncertainty of its average placement near +/- 0.2. Bands narrower than that need
more runs.

### Limits of the loop

- Bots are not people. A hero bots misuse will look weak. Bot placement of the hero is
  checked before its numbers are changed.
- The reference tables are a yardstick for shapes (cost curve, time to kill, wave curve),
  not targets to match.
- Human playtests remain a separate gate and are not replaced by this loop.

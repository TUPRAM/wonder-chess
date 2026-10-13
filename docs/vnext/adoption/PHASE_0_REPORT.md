# Phase 0 report: baseline

Status: **Phase 0 complete, 2026-10-10.** Bot tournaments only. Nothing here is human
evidence or balance acceptance.

## What was done

| Item | Result |
|---|---|
| Bot roles and rows | Now read from a per-class table in the roster rule set (`roster_recipe.class_roles`). Legacy and control rule sets keep their old behaviour |
| Bot trait scoring | Reads the tier list the fight uses; no credit below the first tier |
| Bot formation | A unit swapped in from the bench is moved to the correct half of the board |
| Bot spending (found during the baseline) | Gold above the interest cap is spent on experience and rerolls (`roster_recipe.bot_spends_surplus`) |
| Tournament tool | `run_vnext_tournament.ps1 -RuleSet roster` runs the live rules and writes `seats`, `boards`, `traits`, `settlements`, `waves` and `placements` CSVs |
| Report tool | `tools/vnext/balance_report.py` turns a run into `REPORT.md` and `report.json`, with a baseline column |
| Housekeeping | Eleven planned abilities restored as `design_intent`; stale guide sentence corrected in both languages |
| Balance 0.2.1 | Ironwall health 1000 to 850, Forge King 845 to 1050, Tide Caller 1000 to 1070; shop odds at levels 8-10 lowered at the top |

Tests added: bot role coverage, trait visibility, formation halves, surplus spending
(`tests/runtime/vnext_bot_tests.h`); bot role table in the catalogue (`tests/test_vnext_catalog.py`).

**Control rule set unchanged:** after every change, the control tournaments for seeds 1-2
reproduce the earlier recorded results exactly (412 of 412 fights).

Not done: `ability_share.csv` (per-hero basic and ability damage). The match records keep
only per-side totals, so it needs a small addition to the fight summary; it is moved to S1.

## Runs

200 tournaments each, seeds 1-200, roster rule set. Raw data is under `support/runs/balance/`
(not in git); reports are under `reports/vnext/balance/`.

| Run | What | Report |
|---|---|---|
| `b0-roster-20261010` | Bots with roles fixed, before the spending fix | kept as the "before" record |
| `b0-roster-20261010-spending` | **Baseline B0**: repaired bots, balance 0.2.0 | reference for all later runs |
| `b1-roster-0.2.1-20261010` | Balance 0.2.1 | compared with B0 |

## Baseline B0

| Measure | Value |
|---|---|
| Median rounds per match | 47 (10th-90th percentile 43-51) |
| Median fight time per match | 22.8 minutes |
| Player-time ceiling (full preparation every round) | 62 minutes; no match inside the 35-45 minute target |
| Fights ending by timeout | 2.7% |

**Monster waves cleared by bots**

| Round | 1-5 | 10 | 15 | 20 | 25 | 30 | 35 | 40 | 45 | 50 |
|---|---|---|---|---|---|---|---|---|---|---|
| Cleared | 100% | 99% | 100% | 44% | 100% | 96% | 100% | 21% | 100% | 0% |

Pack rounds are trivially easy. The bosses at 20, 40 and 50 are walls, while the bosses at
10 and 30 are nearly free. 63% of round-40 boss fights end on the clock.

**Economy at preparation lock (median)**

| Round | Gold | Level | Board value |
|---|---|---|---|
| 10 | 16 | 6 | 21 |
| 20 | 59 | 8 | 32 |
| 30 | 101 | 9 | 40 |
| 40 | 178 | 10 | 47 |
| 50 | 284 | 10 | 48 |

**Heroes** (4.5 is a neutral average placement; lower is better)

- Strongest when fielded: Ironwall 3.70, Earthbreaker 3.75, Rifleman 4.10, Dartblower 4.15, Shieldbearer 4.16.
  All three tanks lead, as the stat comparison predicted.
- Weakest: Forge King 5.16, Soul Jailer 5.09, Siege Master 5.02, Bonechanter 5.00, Moonblade 4.99.
- Bots take Bearguard 2.8 times as often as the average cost-2 hero, and almost never take
  Treant Caller (0.07), Soul Jailer (0.27), Ember Wisp (0.32) or Rifleman (0.35).

**Traits**

- The four-member tier is reached in under 0.3% of seat-rounds. With 25 of 40 heroes
  playable, most traits have only two or three playable members, so the second tier cannot
  be measured until the roster is complete.
- Dragonkin never appears (no playable member). Mage appears in 2% of seat-rounds.
- When active at two members: Tank 3.68, Mage 3.83, Beastkin 4.01, Orc 4.14, Fighter 4.24, Human 4.48.

**Bot profiles.** Mean placement ranges from 4.04 to 6.53. `wc_vn_bot_2` is far behind the
rest (6.53).

## Balance 0.2.1 against B0

| Change | Effect |
|---|---|
| Ironwall -15% health | Still strong when fielded (3.70 to 3.78); bots take it less (final boards 27% to 18%) |
| Forge King +24% health | Placement 5.16 to 4.70; no longer the weakest hero |
| Tide Caller +7% health | 4.24 to 4.46. With 128 samples this is inside the noise (about +/- 0.2) |
| Shop odds, levels 8-10 | No visible change in match length, boss clears or board value |
| Match | 47 rounds, ceiling 61.6 minutes, timeouts 2.5%: unchanged |

The shop-odds change shows nothing because bots barely field expensive heroes at all (below).

## What the baseline says about the measuring tool

These limit how far bot results can be trusted, and should be fixed before fine tuning.

1. **Bots field cheap boards.** Cost-1 heroes fill 55% of all board slots across a match;
   cost-4 fill 4% and cost-5 under 1%, even at level 10. Bots buy pairs of cheap heroes
   until the bench is full, rarely sell, and cannot reroll with a full bench.
2. **Gold still piles up late** (median 178 at round 40) for the same reason.
3. **Late bosses are therefore under-tested.** A 21% clear rate at round 40 is measured
   against boards worth less than a human's would be.
4. **One bot profile is much weaker** than the others, which widens every hero's placement spread.

## Recommended follow-ups

| # | Item | When |
|---|---|---|
| 1 | Teach bots to sell stale bench units and replace cheap board units with higher-cost ones once levelled | Before Phase 4's measurement run |
| 2 | Re-measure waves after item 1, then rescale: ease bosses 20, 40 and 50, stiffen packs and bosses 10 and 30 | After item 1 |
| 3 | Review `wc_vn_bot_2`'s weights | With item 1 |
| 4 | Tank health and armour: all three tanks lead placement | With the cost-curve pass after S9, or sooner if the owner wants |
| 5 | Match length: 47 rounds and a 62-minute ceiling confirm that preparation time and loss damage both have to change (Phase 4) | Phase 4 |

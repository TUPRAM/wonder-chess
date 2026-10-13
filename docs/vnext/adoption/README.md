# Adoption design: overview

Status: **design accepted by the owner on 2026-10-10 with the decisions in section 5. No code has been written; implementation waits for the owner's go-ahead.**

This folder turns `../AUTO_CHESS_ADOPTION_PLAN.md` into a buildable design. It is based on
a read of the current source and catalogue (file and line references are in the three
design files), not on the plan's first guesses, several of which turned out to be wrong.

| File | Covers |
|---|---|
| `README.md` | Corrections, structure of the work, decisions needed |
| `ENGINE_AND_CONTENT.md` | Phases 1-3: effect engine, thirteen traits, roster to forty |
| `CALIBRATION_ECONOMY_TUNING.md` | Phases 0, 4 and 6: baseline, economy and match rules, tuning loop |
| `INTERFACE_AND_TEACHING.md` | Phase 5: interface gaps and the guided first match |

## Progress

| Step | State | Evidence |
|---|---|---|
| Phase 0: baseline | Done 2026-10-10 | `PHASE_0_REPORT.md`; reports under `reports/vnext/balance/` |
| S1: effect chains, Stitcher | Implemented 2026-10-10 | `EffectChains` in `tests/runtime/vnext_combat_tests.cpp`; two catalogue tests; run `s1-roster-0.3.0-20261010` |
| S2: stat modifiers, Undead, four heroes | Implemented 2026-10-10 | `Modifiers` in `tests/runtime/vnext_combat_tests.cpp`; catalogue test; run `s2-roster-0.4.0-20261010` |
| S3: fight-start and per-second effects, six traits | Implemented 2026-10-10 | `FightStartAndPerSecondTraits` in `tests/runtime/vnext_combat_tests.cpp`; Goblin checks in `vnext_bot_tests.h`; run `s3-roster-0.5.0-20261010` |
| S4: chance, evasion, crit, lifesteal, bonus true damage, reflect | Implemented 2026-10-10 | `Chance` in `tests/runtime/vnext_combat_tests.cpp`; run `s4-roster-0.6.0-20261010` |
| S5: damage over time, ground zones, auras | Implemented 2026-10-10 | `RepeatingEffects` in `tests/runtime/vnext_combat_tests.cpp`; catalogue test; run `s5-roster-0.7.0-20261010` |
| S6: target shapes (farthest, densest area, random areas, all allies, line, cone, chain) | Implemented 2026-10-10 | `SelectorsAndShapes` in `tests/runtime/vnext_combat_tests.cpp`; catalogue test; run `s6-roster-0.8.0-20261010` |
| S7: hex, silence, taunt, mana drain; Shaman trait | Implemented 2026-10-10 | `Statuses` in `tests/runtime/vnext_combat_tests.cpp`; catalogue test; run `s7-roster-0.9.0-20261010` |
| S8: blink and leap, guaranteed critical hits; Assassin leap | Implemented 2026-10-10 | `BlinkAndLeap` in `tests/runtime/vnext_combat_tests.cpp`; catalogue test; run `s8-roster-0.10.0-20261010` |
| S9: summoned units, limit, lifetime, walls, fallen units; Summoner trait | Implemented 2026-10-10 | `Summons` in `tests/runtime/vnext_combat_tests.cpp`; catalogue test; run `s9-roster-0.11.0-20261010` |
| Phase 4: streak income, staged preparation time, auto-deploy | Implemented 2026-10-11; loss damage measured, not changed | `Economy` in `tests/runtime/vnext_tournament_tests.cpp`; catalogue test; run `p4-roster-0.12.0-20261011` and four `p4-loss-*` runs (table below) |
| Phase 5, Part A: fight chart gaps | Implemented 2026-10-11 | `FightCharts` in `tests/runtime/vnext_combat_tests.cpp` (includes the viewer-is-second-seat case); chart seen in the running game through autoplay screenshots |
| Phase 5, Part B: cues for S5-S9 mechanics | Implemented 2026-10-11 | `PresentationViews` in `tests/runtime/vnext_combat_tests.cpp`; zone outline seen in autoplay screenshots; status, blink and summon cues compile but were not caught in a screenshot |
| Phase 5, Part C: guided first match | Implemented 2026-10-11 | `Guided` in `tests/runtime/vnext_tournament_tests.cpp` plays all six lessons and wins every fight; catalogue test; the scripted run `-WCGuideAutoPlay` completes the guide in the running game with a screenshot of each step |

Phase 4 match length, 200 bot tournaments each on balance 0.12.0 (staged timer, streak income and auto-deploy on in every row). The ceiling assumes a player uses all of every preparation timer.

| Loss damage by stage | Median rounds | 10th-90th percentile | Ceiling, minutes | Matches with ceiling in 35-45 min | Fights ending by timeout |
|---|---|---|---|---|---|
| Before Phase 4 (1 / 3 / 5 / 8, flat 45 s timer) | 48 | 44-53 | 61.2 | 0% | 1.9% |
| 1 / 3 / 5 / 8 (catalogue today) | 48 | 43-53 | 51.3 | 3% | 1.9% |
| 2 / 4 / 6 / 9 | 44 | 41-49 | 47.2 | 25% | 1.6% |
| 2 / 4 / 7 / 10 | 43 | 39-47 | 46.0 | 38% | 1.5% |
| 3 / 6 / 9 / 12 | 39 | 36-43 | 40.9 | 87% | 0.9% |
| 4 / 7 / 10 / 14 | 37 | 33-41 | 38.3 | 80% | 0.7% |

The two candidates named in the design (2 / 4 / 6 / 9 and 2 / 4 / 7 / 10) do not reach the round-38 goal. 3 / 6 / 9 / 12 and 4 / 7 / 10 / 14 bracket it. With either stronger option almost no seat reaches the round-50 boss, and only about one seat in ten (3 / 6 / 9 / 12) or one in thirty (4 / 7 / 10 / 14) reaches the round-40 boss.

**Owner decision, 2026-10-11: 3 / 6 / 9 / 12**, applied as balance version 0.13.0. The confirming run `p4-roster-0.13.0-20261011` repeats the measurement: 39 median rounds (36-43), 40.9-minute ceiling, 87% of matches inside 35-45 minutes, 0.9% of fights ending by timeout.

Deviations from the design so far:

- S1: an effect with its own selector picks its targets when the ability releases, not after
  its delay. The delay only postpones the impact. No designed hero needs later re-selection.
- S1: the three lists of ability names stay in the generator and the schema, but a test now
  fails if they differ, instead of the schema being generated.
- S1: `ability_share.csv` and reading Indonesian tooltips in the solo screen are not done yet.
- S2: the Undead trait is a new trait stat (`enemy_armor_reduction_flat`, applied to the other side at fight start), not yet the general "list of parts" trait shape, which arrives with S3.
- S3: a trait with several parts is written as `runtime` plus `runtime_extra` in the catalogue and becomes one runtime entry per part. Scope stays members, team or enemies; the summons scope arrives with S9.
- S3: the Dwarf shield has no expiry. A larger shield cast later replaces it, as any shield would.
- S4: reflect is a timed modifier stat, so Scaleguard's thorns are a cast self-buff rather than a new passive mechanic.
- S4: lifesteal emits no event when the attacker is already at full health.
- S4: a floating "Miss" and larger crit numbers were added to the fight presentation; they compile but have not been looked at in the running game.
- S5: a repeating effect is queued as one packet per interval when the ability releases, rather than kept as a list on the unit. Recasting replaces the packets still pending from the same ability. Damage over time outlives its caster; an aura that follows its caster ends with it.
- S5: zone rings and damage-over-time badges are not drawn yet; each hit shows as a normal damage number.
- S6: every new shape picks its targets when the ability releases. A line runs from the caster through its current target to the board edge; a cone is the cells within its length and within 45 degrees of that direction; the densest area is the cell in reach with the most enemies around it, nearer the caster on a tie.
- S6: a chain deals the same damage on every jump (no falloff), each jump landing two ticks after the last, to the nearest enemy not yet hit. Bonechanter heals himself a flat amount per cast rather than a share of the damage dealt.
- S6: random areas draw from the fight's chance stream, one draw per shot, and each shot lands on a different enemy while enough are in reach. The `lowest_health_enemy` selector exists in the engine, but no hero uses it yet and it has no native test of its own.
- S6: lines, cones and chains have no drawn shape yet; each hit shows as a normal damage number.
- S7: the three statuses are fixed slots on a unit (expiry and source), not a growing list. They are new effect kinds (`hex`, `silence`, `taunt`), plus `mana_drain`.
- S7: a status carries its duration in milliseconds at each star as its magnitude, so control lasts longer at higher stars; `durationMs` repeats the one-star value. This was not in the design.
- S7: a hex or a silence cancels a cast that is winding up (the mana is lost, as with a stun); a hex also cancels a swing that is winding up. A taunt does not interrupt the current swing. When a taunt ends, the unit keeps its target under the normal rule, so it stays on the taunter while the taunter is in reach; it re-chooses when the taunter dies.
- S7: mana drain does nothing to units that cast on timers (the three passive heroes and all monsters). Silence and hex still stop them casting.
- S7: the Shaman trait's duration is a `durationMs` field on the trait part. Its picks come from the fight's chance stream before the first tick, and each pick is recorded as a hex event at tick 0.
- S7: Owl Seer hexes the enemy it is fighting, not a chosen or random one. Void Wyrm reaches 3 cells rather than only adjacent enemies, because it attacks from range 3.
- S7: floating "Hexed", "Silenced" and "Taunted" text was added to the fight presentation; it compiles but has not been looked at in the running game. There is no status icon or critter model yet.
- S7: the status enum is `wc::UnitStatus`. It was first named `wc::Status`, which clashed with an alias in `WonderSaveFile.cpp` and broke the Unreal build only; the 200-tournament run `s7-roster-0.9.0-20261010` was measured before that rename, which changes no behaviour (native combat tests re-passed after it).
- S8: a blink is a chained effect whose own selector is a cell rule relative to the ability's first target: beside it (nearest the caster), behind it (farthest past it, then straightest), or through it (the farthest free cell on the line, within `maxDash`). The design's "free cell nearest a point" rule is left for S9, which needs it for summons.
- S8: a blink happens when the ability releases, ignoring travel time and delay. After a blink beside or behind, the caster's target becomes the unit it blinked to.
- S8: a line cast by an ability that has a dash length (`maxDash` above zero) is only that long, so Shadow Fiend damages the cells he can cross. He may stop short of the end when cells are occupied, and enemies on the rest of that length are still hit.
- S8: a guaranteed critical hit is a flag on a direct damage effect and uses the same 150% as a basic-attack critical; it draws nothing from the chance stream.
- S8: the Assassin leap is a second trait part (`start_leap`, value 1 at both tiers). Leaps happen before the first tick, in initiative order, before the Shaman hex is drawn. Foxclaw's leap reaches 4 cells and is skipped when he is already beside his target.
- S8: a blink is drawn as the same trail line as a step; there is no leap arc. Not looked at in the running game.
- S9: summoned units are authored in their own catalogue list, `summons`, but reach the engine at the end of the neutral list, after the wave monsters, and a summoned unit is flagged both `neutral` (which list defines it) and `summoned`. This keeps every existing definition lookup working; waves cannot reference a summon.
- S9: no room is reserved in the unit list. Summons are only queued by a cast and are added at one point at the start of the next tick, where nothing holds a reference into the list. They are not added while a finished fight is draining its last hits.
- S9: the limit (`summon_limit_per_side`, 4) counts summons alive at once. A cast that could add none (side at the limit, or nobody fallen for Necromancer) is held and keeps its mana. A summon over the limit, or with no free cell, is dropped and counted (`SummonsRefused`); it is not written to the mechanic trace.
- S9: a summon takes its owner's star (the usual star multiplier on health and damage) and the Summoner bonus through the existing health and damage scales. It gets no traits, no relic and none of the fight-start effects (Undead armour loss, Dwarf shield).
- S9: Necromancer is a cast, not a death trigger. Fallen units (not summons) leave their cell in a list; his cast raises up to 2 skeletons on the newest of those cells, from either side's dead. This avoids a passive ability in a hero the roster recipe treats as a mana caster, and an endless chain of skeletons raising skeletons.
- S9: a summon is placed on the free cell nearest an anchor: its owner (ties broken toward the owner's target), an enemy target (ties toward the caster, so walls land between them), or the cell where a unit fell.
- S9: a wall is an inert unit (`inert`): it never acts and alone does not keep a fight going. Enemies may attack it. Summons keep a fight going after their owner falls, but `survivors` counts only units that started the fight, so they add no player damage.
- S9: a summon arriving or leaving is one event kind (`summon`): source is the owner on arrival and the summon itself on leaving. The damage chart still lists heroes only, so a summon's damage is not shown under its owner yet.
- S9: the scenario runner's ledger was changed to accept units that appear mid-fight; it compiles in the Unreal build but no test runs a scenario with a summoner. The presentation creates a piece for any unit it is given each frame, so a summon should appear like a monster on the player's side; this has not been looked at in the running game, and the four summoned units have no models or portraits.
- Phase 4: the three new rules (`preparationStages`, `streakIncome`, `autoDeploy`) live in the catalogue's shared `rules`, so they apply to the control rule set as well as the roster. `preparationMs` was kept, as the time for any round no stage covers, instead of being replaced.
- Phase 4: a seat's streak is saved, so the save format moved to version 4 and older saves are refused. The solo screen now reads the match's streak; it used to count monster rounds too.
- Phase 4: auto-deploy runs for every seat when preparation ends, before gold is fixed for interest. It never exceeds the level's board limit and never merges.
- Phase 4: the shop odds of 4.2 were already applied in Phase 0. Bots still ignore streak income.
- Phase 4: the catalogue's loss damage is unchanged. The tournament tool gained `-LossDamage` (for example `'2,4,6,9'`) to measure other values without editing the catalogue; such a run records the override in `summary.json` and `process.json`.
- Phase 4: the income line, the streak gold and the "placed from your bench" message on the solo screen compile but have not been looked at in the running game. The catalogue site does not list the new rules.
- Phase 5 A: the chart's numbers come from `Public/Simulation/WonderDamageChart.h`, a pure function with native tests, instead of code inside the screen. A summoned unit's numbers are added to its owner's row rather than listed under it. The last fight's totals are kept as text in the Recap, not as bars.
- Phase 5 B: cues use the existing line, ring, star, text and particle pieces. Statuses are drawn on the unit (ring and star for hex, cross for silence, ring and line to the taunter for taunt, falling drops for damage over time), not as name-plate badges. A zone is a square outline in its damage type's colour. Summoned units keep the ordinary name plate.
- Phase 5 B: the engine gained three read-only helpers for this: a `periodic` flag on events, `Combat::Zones()` and `Combat::PeriodicTargets()`.
- The running game can be looked at through `-WCSoloAutoPlay` screenshots (launch line in `AGENTS.md`); autoplay now also takes a picture 1.3 seconds into each fight.
- Phase 5 C: the guide is the catalogue's `tutorial` key (six stages, 24 steps, English and Indonesian), generated as `wcvnext::WonderVNextTutorial()`. The design's five stages became six: the relic draft is its own short stage after the boss.
- Phase 5 C: a lesson is not "a real solo match with a prepared start" but a prepared two-seat state inside the ordinary match (`Match::BeginGuidedStage`): the captain and one fixed opponent play, the other six seats sit out, the preparation clock is held, nothing is saved, no income is paid, and after the fight the match waits for the next lesson. Leaving or finishing the guide starts a fresh ordinary match rather than continuing the lesson state.
- Phase 5 C: a step is completed by a condition the match checks (`GuidedStepDone`), and the orders a step allows are listed with it; any other order is refused with a hint. Opening the shop and clicking a synergy are screen actions and are never blocked.
- Phase 5 C: the boss lesson uses the real round-10 wave with a prepared two-star board; the relic lesson grants the draft directly instead of running the round after the boss.
- Phase 5 C: progress is one small file beside the save (`guide-progress.txt`: the next lesson to play). A missing file, with no save to resume, makes the guide offer itself once; the guide is always in the Menu. Stage progress is resumed from the Menu, not asked about.
- Phase 5 C: interface controls are framed by tag; the bench and the board are in the 3D yard, so they are pointed at with rings and a row glow there instead. The scripted run gives orders through the same command path a player uses; it does not click widgets.
- Phase 5 C: whether a new player understands each lesson is untested; that is a human study. The native test plays the guide on eight seeds and the captain wins every lesson's fight on each, but a player who follows a step differently (other cells, other purchases where allowed) could still lose one.
- S2: no timed range modifier; no design needs one. The Sniper range bonus is a fight-start value in S3.
- S2: name-plate arrows for buffs and debuffs are not built; the event carries the stat so the interface can add them.
- The control rule set shares its hero list with the roster, so adding a hero changes control
  tournament results. The regression gate is the native combat comparison tests, which pass.

## 1. What the code survey changed

| Earlier claim | What the code shows | Effect on the plan |
|---|---|---|
| Loss damage is fixed by round | A PvP loss already costs the stage value **plus one per surviving enemy unit** (`WonderTournament.cpp:1078`) | Decision 5 is already built the recommended way. Only summons need a rule |
| No damage panel, no shop odds display | Both exist in uncommitted work: a per-hero dealt / taken / healed chart and a "Level N odds" row in the shop (`WCVNextSolo.cpp:891-916, 1176-1187`) | Phase 5 shrinks to gaps plus the guided match |
| Abilities hold one effect | They hold a list, but validation allows only "damage then stun" and every effect shares one target set | The effect-chain work is a widening, not a rewrite |
| Bots just need to learn new rules | Bot role and formation logic still tests for the old class names (guardian, warrior, rogue, ranger, healer, controller). With the current roster, tanks and fighters are scored as damage dealers and placed in the back row. Bots also cannot see two-unit traits | **Every bot tournament on the current roster is unreliable until this is fixed.** It moves to the front of Phase 0 |
| Tournaments measure the live rule set | The native tournament harness runs the control catalogue (timers, no traits), and writes no per-seat gold, level or health | The harness must run the roster rule set and report more before any tuning |
| Combat can take chance effects | Combat has no random numbers at all after the opening initiative shuffle | Crit and evasion need a designed, deterministic chance source |
| Summons need a limit | Nothing can create a unit mid-fight; unit lists, ids and tick order are fixed at fight start. `summon_limit_per_side` is read by nothing | Summons are the largest single engine item |
| Stat changes are general | The timed modifier has no stat field; it only ever changes attack rate | Generalising it is the highest-value engine step: enemy debuffs are the most-needed missing capability |

Two documents carried the wrong claims and are corrected: `COMPARISON.md` (loss damage)
and `../AUTO_CHESS_ADOPTION_PLAN.md` (rows D2, E1, E2).

Other findings worth knowing:

- The planned abilities of the eleven stand-ins are no longer in the working catalogue;
  they survive only in the last commit. They need restoring as reference text.
- Four traits have no authored numbers: Undead, Sniper (bonus damage), Engineer, Shaman (duration).
- The relic draft listed for round 60 can never fire, and the relic cap of 3 is fixed in
  two validators.
- Bot-only matches on the control catalogue run a median of 46 rounds and 29 simulated
  minutes, of which only 2.3 minutes is preparation because bots finish in seconds.
  A person using the full 45 seconds would add about 32 minutes. See decision 3.

## 2. Shape of the work: slices, not layers

The plan listed "engine, then traits, then heroes". Built that way, nothing new is playable
until the whole engine is done. The design instead cuts Phases 1-3 into **nine slices**.
Each slice adds one engine capability and immediately ships the traits and heroes that
capability unlocks, with tests, tooltips and visuals.

| Slice | Engine capability | Traits it completes | Heroes it completes |
|---|---|---|---|
| S1 | Effect chains: several effects per ability, each with its own target rule | - | Stitcher |
| S2 | General timed modifiers (any stat, buffs and debuffs), armour below zero | Undead | Jinxer, Bone Archer, Curse Weaver, Ironwall (armour half) |
| S3 | Fight-start and per-second effects, trait hooks | Dwarf, Priest, Engineer, Sniper, Elemental, Goblin | - |
| S4 | Chance source; evasion, crit, lifesteal, bonus true damage, reflect | Elf, Warlock, Demon, Assassin (crit half) | Scaleguard |
| S5 | Damage over time and ground zones | - | Dartblower, Hellblade, Pit Lord |
| S6 | New selectors and shapes: farthest, cluster, random cells, all allies, line, cone, chain | - | Rifleman, Siege Master, Forge King, Dawn Oracle, Longbow Scout, Flame Regent, Bonechanter, Storm Spirit |
| S7 | Statuses: hex, taunt, silence; mana drain | Shaman | Owl Seer, Ironwall (taunt half), Void Wyrm |
| S8 | Blink and leap | Assassin (leap half) | Moonblade, Foxclaw, Shadow Fiend |
| S9 | Summons, death triggers, walls | Summoner | Treant Caller, Wolf Caller, Necromancer, Stone Shaper |

After S9 all twenty traits execute and all forty heroes are playable with their planned
abilities. Phase 4 (economy) and Phase 5 (interface) do not depend on the slices and can
run alongside them. Phase 0 comes first; Phase 6 runs after every slice.

## 3. Order and dependencies

```
Phase 0  baseline: bot repair, harness on the live rules, first measurement, three hero fixes
   |
   +--> S1 -> S2 -> S3 -> S4 -> S5 -> S6 -> S7 -> S8 -> S9      (Phases 1-3)
   |        each slice ends with a tuning run (Phase 6)
   +--> Phase 4  economy and match rules       (needs only Phase 0)
   +--> Phase 5  interface gaps, guided match  (guided match needs Phase 4's rules settled)
```

S2 before S3 because trait hooks reuse the modifier. S4 before S8 because Moonblade needs
crit. S6 before S7 and S9 because taunt and summons need cell selectors. S9 is last because
it changes the most assumptions and benefits from everything before it being stable.

## 4. Rules every slice follows

- The control catalogue's behaviour must not change. Its comparison tests are the regression gate.
- Same seed gives the same fight, observed or not. Every new mechanic gets a determinism test.
- New data fields are appended, never inserted, because several structures are built positionally.
- The three lists of allowed effects, selectors and mechanics (validator, schema, C++) are
  brought down to one source in S1, so later slices add a name in one place.
- A hero or trait is called executed only when its runtime test passes; tooltips say what
  really happens, in English and Indonesian.
- Catalogue changes go through `tools/vnext/catalog.py` and bump `balance_version`.

## 5. Decisions (owner, 2026-10-10)

The owner accepted every recommendation. These are now the working rules for this programme.

| # | Decision | Outcome | Applies in |
|---|---|---|---|
| 1 | Ability weight | Single-target abilities deal about a third of a same-cost health bar at one star | Phase 3 numbers |
| 2 | Late shop | Cost-5 odds at level 10 drop from 20% to 12%; free experience stays at 2 per round | Phase 4 |
| 3 | Preparation time | 25 / 30 / 35 seconds by stage (rounds 1-5, 6-20, 21 on), and late loss damage is raised so matches end near round 38 | Phase 4 |
| 4 | Shared hero pool | Not now. Shops stay independent | - |
| 5 | Summons and loss damage | Summoned units do not count as survivors | S9 |
| 6 | Chance | A seeded stream per fight; the same fight replays identically | S4 |
| 7 | Open trait numbers | Undead: enemies -10 / -20 armour. Sniper: +10% / +20% basic damage with the range. Engineer: +3 / +6 mana per second. Shaman: hex lasts 3 seconds | S2, S3, S7 |
| 8 | Auto-place benched units at fight start | Yes | Phase 4 |
| 9 | Language of new interface text | English and Indonesian | Phase 5 and every slice |
| 10 | Work in slices | Yes, S1 to S9 as in section 2 | Phases 1-3 |

Still open:

| # | Item | State |
|---|---|---|
| 11 | Relic cap of 3 and the round-60 draft that cannot fire | Held for the owner's relic discussion |
| 12 | The three hero fixes (Ironwall, Forge King, Tide Caller) | Proposed in `COMPARISON.md`; not yet approved |
| 13 | Shop odds at levels 8 and 9 | The owner approved 12% at level 10. The design tapers levels 8 and 9 to match (cost-5 at 3% and 6%); confirm or leave them as they are |
| 14 | Exact late loss-damage values | Chosen by measurement against the round-38 goal, then shown to the owner |

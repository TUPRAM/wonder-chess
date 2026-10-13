# Engine and content design (Phases 1-3)

Status: design accepted by the owner on 2026-10-10 (decisions in `README.md` section 5). No code written.

References: **H** = `game/Source/WonderChessRuntime/Public/Simulation/WonderSimulation.h`,
**C** = `.../Private/Simulation/WonderSimulation.cpp`, **py** = `tools/vnext/catalog.py`.
Line numbers are from the survey of 2026-10-09 and will drift.

## 1. Where the engine stands

- **Ability** (H:111-127): one selector, one target set, a list of effects that validation
  limits to "damage, then stun" (C:316-318, py:131-134). Seven special mechanics are
  hand-written branches and must have an empty effect list.
- **Impact** is one function, `Apply` (C:1378-1437), in this order: mitigation, guard,
  shield, health, mana, death, event, displacement.
- **Unit state** (H:324-354) is bespoke per effect: one shield slot, a stun expiry, a list
  of timed modifiers that only ever feed attack rate.
- **No chance.** The only random draw is the initiative shuffle in the constructor.
- **Traits and relics** apply once, at fight start, from a list of ten stat names (C:336-338).
  A trait's runtime shape is one stat, one scope, one value per threshold.
- **Units** are created only in the constructor. Targets and packets refer to units by
  index into one vector.
- **Events** (H:355-371) carry source, target, amounts, damage type and whether it was a
  basic attack. The interface already builds its damage chart from them.

## 2. Design principles

1. **Additive.** Existing abilities, mechanics and the control catalogue run through
   unchanged paths. New behaviour is reached only by new data.
2. **One impact pipeline.** Every new damage rule is a numbered step in `Apply`, in a fixed
   order written down in section 4. No rule lives in a hero-specific branch.
3. **Everything visible is an event.** A miss, a crit, a tick of poison, a spawn: each
   pushes a `CombatEvent`, so the chart, floating text and recap stay correct for free.
4. **Deterministic.** Any draw comes from one stream owned by the fight, taken in the
   already-total packet order.
5. **No new special mechanics.** The seven existing ones stay; nothing new is added to
   that list. New abilities are compositions of generic effects.

## 3. The slices

Each slice lists the data change, the behaviour, the rules that need a ruling, what is
delivered, and how it is tested.

### S1. Effect chains

**Data.** `AbilityEffect` gains, appended: `target` (same targets as the first effect, or
its own selector), `delayMs`, `radius`. The ability's own selector stays the default.
Validation changes from "damage then stun" to: up to four effects; any of the generic
effect kinds; a non-damage first effect is allowed.

**Behaviour.** At release, effects are queued in order as they are today. An effect with
its own selector resolves its targets at its own release time (after `delayMs`), using the
same re-selection rule the engine already uses at release.

**Housekeeping in this slice.** The lists of effects, selectors and mechanics exist three
times (py:12-21, the JSON schema, the C++ enums). They are reduced to one list in the
generator, which emits the schema fragment and the C++ mapping.

**Delivers.** Stitcher (heal, then shield, on the lowest-health ally). Restores the eleven
stand-ins' planned abilities from the last commit into a `design_intent` text field so the
target of each later slice is written in the catalogue.

**Tests.** A four-effect ability resolves in order with correct delays; a chain whose first
target dies still resolves effects that re-select; control catalogue comparison unchanged.

### S2. General timed modifiers

**Data.** `Modifier` gains a `stat` field (appended). Stats: attack rate (today's only
one), attack damage, armour, resistance, damage dealt, damage taken, movement, range.
The stat-modifier effect names its stat. Magnitude may be negative.

**Behaviour.** Stacking is unchanged: same ability refreshes or replaces by strength;
different abilities add. Every read of a stat at release or impact goes through one
function that adds the unit's active modifiers for that stat.

**Rulings.**
- *Armour below zero.* The current curve `100 / (100 + armour)` breaks at -100. Rule:
  for negative armour, damage is multiplied by `2 - 100 / (100 - armour)`. That is
  symmetric: -25 armour gives +20% damage, as +25 gives -20%. Armour is clamped at -75.
- *When stats are read.* Attack damage and bonuses are fixed at release, as today.
  Defence and damage-taken are read at impact, as today.
- *Cleansing.* Nothing removes modifiers early. Not needed by any design.

**Delivers.** Undead trait (all enemies lose 10 / 20 armour, decided; a fight-start
modifier with no expiry). Jinxer (lowers the target's attack damage). Bone Archer (lowers the target's
armour). Curse Weaver (target takes more damage). Ironwall's armour gain.

**Tests.** Each stat changes the expected number; two sources add; the same source
refreshes; a negative-armour hit matches the rule; expiry restores the base value.

### S3. Fight-start and per-second effects, trait hooks

**Data.** A trait's runtime becomes a short list of parts instead of one stat. Each part
has a kind, a scope and one value per threshold. Scopes: members, team, **enemies**,
**summons**. Kinds: the ten existing stats, plus the hooks below. Existing single-stat
traits read as a one-part list, so nothing authored today changes.

**New unit fields.** Health regeneration per second, mana per second, skill-damage
reduction, range bonus. All are plain numbers set at fight start.

**Behaviour.** A per-second step runs at a fixed point in the tick for every living unit
that has regeneration or mana income. Regeneration emits a heal event once per second,
not per tick, to keep event volume down.

**Delivers.**

| Trait | Part(s) | Authored value at 2 / 4 |
|---|---|---|
| Dwarf | Fight-start shield, share of maximum health, members | 20% / 40% |
| Priest | Health regeneration per second, share of maximum health, team | 1.5% / 3% |
| Engineer | Mana per second, team | 3 / 6 (decided) |
| Sniper | Range bonus, members; basic damage bonus, members | +1 / +2; +10% / +20% (decided) |
| Elemental | Skill-damage reduction, team | 15% / 30% |
| Goblin | Gold after a won player fight | +1 / +2 |

Goblin is a match-level hook, not a combat one: the fight reports which traits were active
for the winner and settlement adds the gold to the existing pending-reward path.

**Rulings.**
- The Dwarf shield uses the existing single shield slot, so a later, larger shield replaces it.
- Regeneration is not affected by healing bonuses and does not overheal.
- Skill-damage reduction applies after armour or resistance and before guard.

**Tests.** One test per trait at 2 and at 4 members, plus one at 1 member showing no
effect. A regeneration test over ten seconds checks the total healed exactly.

### S4. Chance, and the attack rules that use it

**Chance source (decided: seeded stream).** The fight keeps one random stream, seeded from the same
encounter seed that already shuffles initiative. Draws are taken only inside `Apply`, in
packet order, and only when a unit actually has a chance-based rule. A fight with no such
rule draws nothing, so the control catalogue's results cannot move. A counter of draws is
exposed so a test can assert that.

**New rules, as numbered steps in section 4.**
- *Evasion.* Basic attacks only. Sources combine as `1 - product(1 - x)`. A miss deals no
  damage, grants no mana to either side, and emits an event flagged evaded.
- *Crit.* Basic attacks only, unless an ability says "guaranteed crit". One roll against
  the summed chance, capped at 100%. Multiplier 150% unless the source states another.
  The event is flagged critical.
- *Lifesteal.* After health loss: the source heals for a share of the health actually
  lost, if it is alive. Emits a heal event. Overkill does not count.
- *Bonus true damage (Demon).* After health loss: a second event of true damage equal to
  a share of the health just lost. It does not trigger lifesteal, reflect or itself.
- *Reflect (Scaleguard).* After health loss: the attacker takes true damage equal to a
  share of the health lost. It never triggers another reflect.

**Event fields added** (appended): evaded, critical, and a "secondary" marker for
lifesteal, bonus true damage and reflect, so the chart can attribute them.

**Delivers.** Elf (20% / 40% evasion, members). Warlock (team heals 10% / 20% of damage
dealt). Demon (+15% / +30% of damage again as true, members). The crit half of Assassin
(15% / 30%, members). Scaleguard.

**Tests.** With a fixed seed, the exact sequence of hits and misses is asserted and must
repeat. Over 10,000 simulated attacks, the miss rate is within a stated tolerance of the
configured chance. Lifesteal on a dead source heals nothing. Reflect against reflect
terminates.

### S5. Damage over time and ground zones

**Data.** A new effect kind, periodic damage: amount per second, duration, damage type,
tick interval (default 1 s). A second form attaches the same thing to a set of cells
instead of a unit.

**Behaviour.** Each unit keeps a small list of periodic effects, keyed by source ability.
The same ability refreshes its own entry; different abilities stack. Each tick of damage
goes through `Apply` as ability damage from the original caster, so mitigation, the chart
and kill credit all work. A ground zone damages every enemy standing in it at each tick.

**Rulings.**
- Periodic damage continues after the caster dies.
- It grants mana to the target like any damage, within the existing per-second cap, and
  none to the caster.
- A ground zone does not block movement.

**Delivers.** Dartblower (poison, plus the attack-rate slow from S2). Foxclaw's bleed
(the leap arrives in S8; until then the tooltip says so). Hellblade (aura that burns
adjacent enemies each second: a zone that follows the caster). Pit Lord (large zone for
several seconds).

**Tests.** Total damage over the duration matches amount x seconds after mitigation;
refresh does not double; a zone hits a unit that walks in and stops when it leaves.

### S6. Selectors and shapes

**New selectors.** Farthest enemy; cell with the most enemies within a radius (cluster);
N random enemy-occupied cells (uses the S4 stream); all allies; lowest-health enemy.

**New shapes.** Line from the caster through the target to the board edge (reuses the
existing beam cell walk, C:51-61); cone in front of the caster; chain (the next nearest
enemy within a range, up to N jumps, each hit reduced by a stated share).

**Rulings.**
- Ties break by initiative then id, as everywhere else.
- Cluster picks the cell, not a unit, so it can land between units.
- A chain never hits the same unit twice.

**Delivers.** Rifleman, Siege Master, Forge King, Dawn Oracle, Longbow Scout, Flame Regent,
Storm Spirit, and Bonechanter (chain with the S4 lifesteal rule for the drain).

**Tests.** One fixed board per selector with the expected target written out; a line and a
cone on a known layout list the expected cells.

### S7. Statuses

**Data.** A small generic status list per unit: kind, expiry, source. Kinds: hex, taunt,
silence. Stun and cocoon keep their existing bespoke fields; they are not migrated.

**Behaviour.**
- *Hex:* the unit can move but cannot attack or cast. Mana gain is paused.
- *Silence:* the unit cannot cast; it attacks normally.
- *Taunt:* the unit must target the taunter while it is alive and reachable.
  Target choice (C:650-678) checks this first.
- *Mana drain:* a new effect kind that removes mana from the target, floored at zero.

**Rulings.** Statuses of the same kind do not stack; the later expiry wins. Bosses can be
hexed and taunted (no immunity rule is added; revisit in tuning if bosses become trivial).

**Delivers.** Shaman (1 / 2 random enemies hexed at fight start for 3 s, decided). Owl Seer.
Ironwall's taunt. Void Wyrm (drain plus silence in an area).

**Tests.** A hexed unit performs no attack for the duration and resumes after; a taunted
unit switches target and switches back when the taunter dies.

### S8. Blink and leap

**Data.** A new effect kind, blink: the caster moves instantly to a cell chosen by a cell
selector. Cell selectors: free cell adjacent to the target; free cell behind the farthest
enemy; free cell nearest a point.

**Behaviour.** Reuses the occupancy check that dash already uses (C:755-801). If no legal
cell exists the blink is skipped and the rest of the chain still runs. A trait part
"leap at fight start" performs one blink before the first tick.

**Rulings.**
- Order at fight start: trait leaps resolve in initiative order, one at a time, so two
  assassins cannot pick the same cell.
- A leaping unit keeps its facing rule from the destination.
- With the current "nearest reachable target" rule, a unit that leaps behind the enemy
  line will naturally retarget to a back-line unit. That is the intent.

**Delivers.** The leap half of Assassin. Moonblade (blink behind the farthest enemy,
guaranteed crit from S4). Foxclaw (leap to target, bleed from S5). Shadow Fiend (line dash
that damages every enemy crossed: a blink plus a line from S6).

**Tests.** Destination cell asserted on fixed boards, including the no-free-cell case.

### S9. Summons, death triggers, walls

The largest change. Today unit lists, ids, initiative and tick order are fixed at fight
start, and code holds references into the unit vector across calls.

**Design.**
- *Definitions.* Summoned units are ordinary unit definitions in a new catalogue list,
  `summons`, never offered in a shop.
- *Capacity.* The unit vector reserves room for both sides' full summon limit when the
  fight is built, so adding a unit never moves existing ones.
- *Spawn queue.* A summon effect only queues a request. Requests are served at one fixed
  point at the start of the next tick, before the tick's unit order is built.
- *Identity.* Summons take instance ids from a reserved range and initiative values after
  every starting unit, in spawn order.
- *Limit.* `summon_limit_per_side` (4 in the catalogue) is finally read. A request over
  the limit is dropped and traced.
- *Lifetime.* Optional duration; at expiry the unit is removed with a death event.
- *Stats.* A summon's health and damage scale with the caster's star, and with the
  Summoner trait part (scope "summons", +30% / +60%).
- *Death trigger.* A new ability trigger: "when a unit dies within range". Necromancer
  uses it to queue a skeleton on the fallen unit's cell.
- *Walls.* Stone Shaper's wall is a summon with health, no attack and a short lifetime.
  No separate terrain system is needed.

**Rulings.**
- Summons do not count as survivors for player damage (decided).
- Summons do not count toward traits and carry no relic.
- Summons grant mana to attackers like any unit.
- A summon's kills and damage are credited to the summon in the chart, shown under its owner.

**Knock-on work.** Tournament summaries, scenario metrics and the save's survivor list look
units up by id and assume the starting set (`WonderTournament.cpp:1046`, `WonderScenario.cpp:325`,
`WonderSave.cpp:119`). Each needs to tolerate units that did not exist at the start. The
presentation layer's handling of a new unit id mid-fight was not determined and must be
checked first; it is the main risk in this slice.

**Delivers.** Summoner trait. Treant Caller (treant that taunts, using S7). Wolf Caller.
Necromancer. Stone Shaper.

**Tests.** Spawn appears on the tick after the cast; the fifth summon is refused; a fight
with summons still replays identically; every consumer listed above runs on a fight that
ends with summons alive.

## 4. The impact pipeline after all slices

For one packet reaching one target. New steps are marked with their slice.

1. Target dead: stop.
2. Basic attack and target has evasion: roll; on a miss emit an evaded event and stop. (S4)
3. Basic attack and source has crit, or the packet is a guaranteed crit: roll; multiply. (S4)
4. Mitigation by armour or resistance, including modifiers and the below-zero rule. (S2)
5. Damage-taken modifiers on the target. (S2)
6. Skill-damage reduction, abilities only. (S3)
7. Guard reduction. (existing)
8. Shield absorption. (existing)
9. Health loss and overkill. (existing)
10. Lifesteal to the source. (S4)
11. Bonus true damage from the source. (S4)
12. Reflect to the source. (S4)
13. Mana to source and target. (existing)
14. Death, then death triggers. (existing, S9)
15. Event pushed. (existing)
16. Displacement. (existing)

Steps 10-12 create secondary events that skip steps 2, 3 and 10-12.

## 5. Traits after all slices

| Trait | Kind | Slice | Parts |
|---|---|---|---|
| Human, Orc, Beastkin, Dragonkin, Tank, Fighter, Mage | - | done | unchanged |
| Undead | race | S2 | enemies lose armour |
| Dwarf | race | S3 | fight-start shield |
| Goblin | race | S3 | gold on a won player fight |
| Elemental | race | S3 | skill-damage reduction |
| Priest | class | S3 | regeneration |
| Engineer | class | S3 | mana per second |
| Sniper | class | S3 | range and basic damage |
| Elf | race | S4 | evasion |
| Demon | race | S4 | bonus true damage |
| Warlock | class | S4 | lifesteal |
| Shaman | class | S7 | hex at fight start |
| Assassin | class | S4 + S8 | crit, then leap |
| Summoner | class | S9 | stronger summons |

Assassin ships its crit half in S4 and is marked partial until S8. All thresholds stay 2 and 4.

## 6. Heroes after all slices

| Slice | Stand-ins given their planned ability | Planned heroes made playable |
|---|---|---|
| S1 | - | Stitcher |
| S2 | Jinxer, Ironwall (armour) | Bone Archer, Curse Weaver |
| S4 | - | Scaleguard |
| S5 | Dartblower | Hellblade, Pit Lord |
| S6 | Rifleman, Siege Master, Forge King, Longbow Scout, Bonechanter | Dawn Oracle, Flame Regent, Storm Spirit |
| S7 | Ironwall (taunt) | Owl Seer, Void Wyrm |
| S8 | Moonblade, Foxclaw | Shadow Fiend |
| S9 | Treant Caller | Wolf Caller, Necromancer, Stone Shaper |

Eleven stand-ins and fifteen planned heroes: all forty playable after S9.

**Per hero, done means:** stats and ability in the catalogue; listed in the roster recipe
(mana or passive); tooltip in English and Indonesian stating what really happens; one
runtime test of the ability; a placeholder portrait and model reference so it can be
shown; catalogue site regenerated. Art approval is a separate track and is not claimed.

**Cost curves (plan items A1-A3).** Applied once, to all forty, after S9 and before the
final tuning run, so heroes are not retuned twice. Proposed targets relative to the cost-1
median, to be adjusted by tuning:

| Cost | Health | Attack output | Armour (non-tank) | Resistance |
|---|---|---|---|---|
| 1 | 1.00 | 1.00 | 10 | 5 |
| 2 | 1.10 | 1.10 | 12 | 5 |
| 3 | 1.25 | 1.25 | 15 | 10 |
| 4 | 1.45 | 1.45 | 20 | 15 |
| 5 | 1.65 | 1.65 | 25 | 20 |

**Ability weight (decided).** A single-target ability deals about a third of a same-cost
health bar at one star. With the cost-1 median at 650 health that is about 215 at cost 1,
rising with the health column above (about 235, 270, 315 and 360 at costs 2-5), against
120-200 today. Per-star growth keeps today's ratio (about x1.6 and x2.5). Area abilities
start at half the single-target value per target and are set by tuning. Heals and shields
follow the same budget as damage of their cost. Applied in the same single pass as the
cost curves.

Class sets the split between health and attack output within a cost (tanks high health and
low output, assassins and snipers the reverse), using the ratios the current cost-1 heroes
already show. A script proposes the new stats; the owner reviews the table before anything
is written to the catalogue.

## 7. Risks

| Risk | Where | Mitigation |
|---|---|---|
| Summons break code that assumes a fixed unit set | S9 | Check the presentation layer first; reserve capacity; one spawn point per tick |
| Chance makes results feel unfair or hard to read | S4 | Events flag misses and crits; the chart and floating text show them |
| Event volume grows with periodic effects | S3, S5 | One event per second per effect, not per tick |
| Bosses trivialised by hex and taunt | S7 | Measured in the slice's tuning run; an immunity flag is the fallback |
| Save files stop loading | every slice | Saves are already tied to the content digest; each catalogue change invalidates old saves by design. Bump the save magic only when seat or unit state changes |
| Validator, schema and C++ drift apart | S1 | Single source for the enum lists |

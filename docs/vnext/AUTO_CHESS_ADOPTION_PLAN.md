# What to adopt from the Auto Chess reference, and the plan that follows

Status: **proposal, 2026-10-07. Nothing here is adopted or implemented until the owner says so.**

> Superseded in detail by `adoption/README.md` (2026-10-09), which is based on a read of the
> source. Rows D2, E1 and E2 and decision 5 below were corrected on that date.

Sources: the decoded reference under `support/reference/autochess/` (`FINDINGS.md`,
`COMPARISON.md`, `reference/*.csv`) and the current Wonder Chess catalogue and simulation.
"The reference" below always means Auto Chess.

## Ground rules

- **Take:** rules, numbers, formulas, mechanic types, interface ideas, tooling ideas.
- **Never take:** their hero names, text, art, sound, lore, code, or a hero kit copied one
  for one. Wonder Chess heroes keep their own identities; a reference mechanic is a building
  block, used where one of our own designs already calls for it.
- Owner directions that already stand and are not reopened here: races and classes with
  2/4 thresholds; twelve universal, drawback-free relics; no equipment system; simple
  readable art.
- Every change goes through `data/vnext/catalog.json` and `tools/vnext/catalog.py`, and
  is called executed only after its runtime tests pass.

Sizes are relative: **S** a data change, **M** one new engine feature with tests,
**L** a system touching simulation, bots and interface.

## 1. The full list

### A. Numbers (data only)

| # | Reference | Wonder Chess now | Verdict | Size |
|---|---|---|---|---|
| A1 | Health and attack grow with cost: cost 5 has 1.8x the health and 2x the attack output of cost 1 | 1.42x and 1.08x | **Adopt** a cost curve for basic stats | S |
| A2 | Armour rises with cost (10% to 35% physical reduction) | Flat 10-15, tanks 35 | **Adopt** per-cost armour for non-tanks | S |
| A3 | No magic resistance on cheap heroes, 10-15% at the top | Flat 15 on everyone | **Adopt** per-cost resistance | S |
| A4 | A cost-1 ability removes about half a cost-1 health bar | About a fifth | **Decide.** Heavier abilities make mana and positioning matter more, and fights swingier | S |
| A5 | Win and loss streak income, up to +3 | Streak is tracked and shown, pays nothing | **Adopt** | S |
| A6 | Monster wave health curve: 300 total at round 1, 3,000 at round 10, 10,000 boss at 35, 40,000 at 50 | 16 monsters, untested targets | **Check** against this curve (calibration step 3) | S |
| A7 | Shop odds: 6% cost-5 at level 10 | 20% | **Adopt** a leaner top end, with A8 | S |
| A8 | 1 free experience per round | 2 | **Decide** together with A7 | S |
| A9 | Preparation 15-25 s early, 30-50 s late | 60 s then 45 s flat | **Decide.** Shorter early rounds are the cheapest way to hit 35-45 minutes | S |
| A10 | Gold bounty for killing units (1/3/5 by star) | None; selling already exists | **Skip** | - |
| A11 | Three attack ranges only (melee, mid, long) | Per-hero range in cells | Keep ours | - |
| A12 | Star scaling x2, x4 | x1.8, x3.24 | Keep ours | - |
| A13 | Interest cap 4 | Cap 5 | Keep ours | - |
| A14 | Monster rounds 1, 2, 3, 10, 15 ... | 1, 2, 3, 5, 10 ... 60 with a boss every tenth | Keep ours | - |

### B. Combat mechanics the engine lacks

The simulation has six effects (damage, heal, shield, stun, dash, stat modifier) and ten
target selectors. The reference kernel has about a hundred buff types. Only the ones our
own unimplemented traits and planned abilities need are listed.

| # | Mechanic | How the reference does it | Needed by | Verdict | Size |
|---|---|---|---|---|---|
| B1 | Evasion and accuracy | Dodge sources combine as 1 - product(1 - x); accuracy multiplies the result down; normal attacks only | Evasion trait | **Adopt** | M |
| B2 | Critical hits | Sources rolled one at a time, first success applies, no stacking | Leap/crit trait | **Adopt** | M |
| B3 | Lifesteal | Share of final damage returned as healing | Lifesteal trait | **Adopt** | M |
| B4 | Health regeneration and mana per second | Flat per-second values on the unit | Regeneration and mana traits | **Adopt** | S |
| B5 | Starting shield, starting mana | Applied at fight start | Starting shield trait | **Adopt** | S |
| B6 | Armour reduction on the enemy, including below zero | Negative armour amplifies damage through the same curve | Enemy armour trait | **Adopt**; our curve needs a rule for negative values | M |
| B7 | True damage | Third damage type, skips mitigation | True damage trait | Already in the engine (`DamageType::True`); wire a trait to it | S |
| B8 | Bonus attack range | Flat range bonus | Range trait | **Adopt** | S |
| B9 | Gold from a trait | Paid on a round result | Gold trait | **Adopt** | S |
| B10 | Hex (target cannot attack or cast for a time) | A disable flag distinct from stun | Hex trait | **Adopt** as a second disable alongside stun | M |
| B11 | Summons | 6 heroes summon; summons are ordinary units with their own record | Summons trait, Wolf Caller, Necromancer, Stone Shaper, Treant Caller | **Adopt**; a per-side limit already exists in the catalogue | L |
| B12 | Blink and leap | Move to a chosen cell: farthest reachable, behind the farthest enemy, nearest free | Assassin-style abilities, leap trait | **Adopt**; extends the existing dash | M |
| B13 | Line and cone areas | Projectile travelling in a direction hitting everything it overlaps; half-circle in front | Stand-ins waiting for "lines" | **Adopt** | M |
| B14 | Damage over time | Repeating damage with a duration | Stand-ins waiting for it | **Adopt** | M |
| B15 | Drain | Steal health from the nearest enemy on a timer | Warlock-type abilities | **Adopt** (B3 plus B14) | S |
| B16 | Bouncing projectile | Hops between targets with falling damage | Optional | Later | M |
| B17 | Silence, disarm, taunt, spell immunity, block, reflect, execute, dispel | All present | Nothing designed yet | **Skip** until a design asks | - |

### C. Target selection

The reference uses 26 selectors. Ours missing and worth having:

| # | Selector | Verdict | Size |
|---|---|---|---|
| C1 | Random enemy (their most common, 24 of 98 heroes) | **Adopt** | S |
| C2 | Farthest enemy; lowest-health enemy; highest-attack enemy | **Adopt** | S |
| C3 | The cell or line that covers the most enemies | **Adopt** with B13 | M |
| C4 | Lowest health percentage ally (ours picks lowest health) | **Check** which ours means | S |
| C5 | Free cell: nearest, farthest from self, behind the target | **Adopt** with B11 and B12 | M |

### D. Match systems

| # | Reference | Wonder Chess now | Verdict | Size |
|---|---|---|---|---|
| D1 | Shared hero pool with limited copies (18-21 down to 9-12 by cost) | Unlimited independent shops, an adopted design choice | **Decide.** A shared pool is the main source of interaction between players outside fights | L |
| D2 | Loss damage is the sum of surviving enemy units (1-4 each) | Stage value plus one per surviving enemy unit (already built) | Keep ours | - |
| D3 | Benched units are placed automatically when the fight starts and there is room | Not found in source | **Adopt** | S |
| D4 | Late-match pressure: overtime damage from round 51 | 60-round cap | Keep ours | - |
| D5 | Relic choice: pick 1 of 2 or 3; up to 10 held | Drafts after boss rounds; 3 slots | Hold for the owner's relic discussion | - |
| D6 | Equipment with recipes, 6 per unit | Owner chose no equipment | **Skip** | - |
| D7 | Talents at rounds 5/15/25/35, legendary pieces, many side modes | None | **Skip** | - |
| D8 | Private lobby with bots and a pause button | Pause exists in the lab; solo mode against bots exists | **Check** that solo has pause | S |

### E. Interface

Seen in the live client. Each is an idea, built in our own style.

| # | Feature | Verdict | Size |
|---|---|---|---|
| E1 | Live damage panel: per-unit running totals, tabs for dealt, taken and healing, bar split by physical and magic | Exists in uncommitted work (dealt / taken / healed). Missing: blocked, damage-type split, kept totals | **Close the gaps** | S |
| E2 | Shop shows the current odds per cost at your level | Exists in uncommitted work, inside the shop | Keep ours | - |
| E3 | Synergy list with count and thresholds, trait icons under each unit | **Check** ours against it | S |
| E4 | Loss card that states the health lost; streak counter | Ours has round cards and streak text | Keep ours | - |
| E5 | Pre-round popup listing what is special this round | **Skip** | - |

### F. Teaching

| # | Reference | Verdict | Size |
|---|---|---|---|
| F1 | A five-stage guided match against one bot: board pre-filled, plenty of gold, no timers, one concept per stage (level up and deploy, star up, synergies ...) | **Adopt** the structure | L |
| F2 | About 27 puzzle levels with fixed boards | Later | L |

### G. Data and tooling

| # | Reference | Verdict | Size |
|---|---|---|---|
| G1 | An ability is a chain: skill -> projectile or area object -> one or more buffs, each a separate record | **Adopt the idea.** Our ability is one record with one effect, which is why eleven heroes need stand-ins. Chaining effects is the single change that unlocks most of section B | L |
| G2 | One override file per mode on top of shared unit data | We have the roster recipe and the control catalogue; same idea | Keep ours | - |

## 2. Decisions needed from the owner

> Answered on 2026-10-10: the owner accepted every recommendation below. The decided
> wording is in `adoption/README.md` section 5.

These change what the plan builds. My recommendation is in brackets.

1. **A4 ability weight:** keep fights attack-driven, or move toward ability-driven? [Move part of the way: raise single-target abilities to about a third of a same-cost health bar.]
2. **A7 + A8 late shop:** lower cost-5 odds, or drop free experience to 1? [Lower the odds; keep 2 experience.]
3. **A9 preparation time:** keep 45 s flat, or scale with the round? [Scale: 25 s for rounds 1-5, 35 s to round 20, 45 s after.]
4. **D1 shared pool:** keep independent shops, or share a pool? [Keep independent for now; revisit once eight-seat bot matches are measured.]
5. **D2 loss damage:** settled. The code already charges the stage value plus one per surviving enemy.

## 3. Development plan

Each phase ends with evidence, not a date. Phases 1 and 4 can run side by side; 2 and 3
depend on 1.

### Phase 0: calibrate what exists

- Apply the three accepted hero fixes from `COMPARISON.md` (Ironwall, Forge King, Tide Caller) once approved.
- Calibration step 3: monsters and economy curve (A6).
- Owner answers the five decisions above.
- Done when: catalogue regenerated, `validate_kit`, unit tests and catalogue checks pass.

### Phase 1: effect engine (G1, B1-B15, C1-C5)

Order chosen so each step unlocks designed content:

1. Effect chains: an ability may apply several effects, each with its own selector and delay.
2. Per-second and fight-start effects (B4, B5) and the simple stat traits (B7, B8, B9).
3. Attack modifiers: evasion and accuracy, crit, lifesteal, armour reduction (B1, B2, B3, B6).
4. New selectors (C1, C2, C4).
5. Damage over time, drain, hex (B14, B15, B10).
6. Movement and areas: blink and leap, lines and cones, cell selectors (B12, B13, C3, C5).
7. Summons (B11).

- Done when: every new effect has deterministic simulation tests, and the native comparison tests on the control catalogue still pass unchanged.

### Phase 2: the thirteen remaining traits

- Implement each on its Phase 1 mechanic with 2/4 thresholds; starting values taken from the reference's first two tiers where a like-for-like synergy exists (for example +3 armour and +15; 25% evasion; 10% lifesteal and 30%).
- Done when: all twenty traits execute and each has a test that fields 2 and 4 members.

### Phase 3: the roster to forty

- Replace the eleven stand-in abilities with their planned ones.
- Make the fifteen planned heroes playable through the standard ability system.
- Apply the cost curves A1-A3 to all forty in one pass, and A4 if chosen.
- Done when: forty heroes enabled, tooltips state what really happens, catalogue site regenerated.
- Not in scope: art and models, which stay on their own approval track.

### Phase 4: economy and match rules (A5, A7-A9, D2, D3, and D1 if chosen)

- Streak income; shop odds; preparation timing; loss damage; auto-deploy.
- Teach the bots the new rules under the same no-hidden-advantage constraint.
- Done when: an eight-seat bot tournament reports match length, rounds played, level reached by round, and gold curves, and match length sits in the 35-45 minute target or the gap is stated.

### Phase 5: interface and teaching (E1-E3, F1)

- Damage panel, shop odds line, synergy list review.
- Guided first match in five stages.
- Done when: verified in the running game with captures. Human playtest stays a separate gate.

### Phase 6: tuning loop

- Bot tournaments per balance version: pick rate, win rate and average placement per hero and per trait; flag anything beyond agreed bands; adjust; repeat.
- The reference tables stay the yardstick for shapes (cost curve, time to kill), not for exact values.

## 4. What this plan does not claim

- The reference combat formulas come from a 2019 build; its stat tables are current.
- "Not found in source" items (auto-deploy, damage panel) were checked by text search only.
- No time estimates are given; sizes are relative.

# Wonder Chess — Game Rules v3

**Active numeric profile:** `data/rules.alpha.json`. **Status:** provisional design; no completed game-balance study. This document defines behavior missing from earlier broad prompts.

## 1. Tournament progression and economy

Eight competitors start with 60 health, 10 gold, level 3, zero XP, eight bench slots and five shop offers. Level is deployment capacity; cap is six. The initial preparation lasts 45 seconds, subsequent preparations 25 seconds, combat at most 40 seconds and settlement four seconds. All clocks advance under the authoritative match state. Offline pause may pause all eight seats; a network client cannot pause the world alone.

Five base gold and one victory gold are awarded only when a surviving seat enters another preparation. Interest is `min(3, floor(preparationLockGold/10))`, snapshotted after accepted preparation commands and before any battle settlement. Loss/draw do not pay a win bonus. Ghost recipients receive normal recipient-side reward; donors receive nothing from their copy. No streak income. A finished or eliminated seat receives no next-round income or passive XP.

Paid reroll costs two gold. Buying four XP costs four gold. Passive XP is two per completed round only for surviving seats with a next preparation. XP thresholds are 4 for 3→4, 8 for 4→5 and 12 for 5→6; carry overflow, discard XP at cap, reject paid XP purchases at cap. Process settlement → elimination/end check → eligible income/XP → free shop refresh unless locked. Do not advance shops before final placement is known.

### Shop distribution

Independent draws with replacement; no shared finite pool. First draw a cost tier using level weights, then a unit uniformly among eligible alpha units of that tier. Use the seat’s private shop RNG stream. Duplicate offers are legal. Purchase empties its slot; there is no free replacement. Paid reroll replaces all five slots and clears lock. Lock preserves the remaining offers through the next automatic refresh, including empty slots, and stays enabled until toggled or a paid reroll. Re-evaluate a new draw at the current level; leveling does not silently reroll existing offers.

| Level | 1 gold | 2 gold | 3 gold |
|---|---:|---:|---:|
| 3 | 75% | 25% | 0% |
| 4 | 55% | 40% | 5% |
| 5 | 35% | 50% | 15% |
| 6 | 20% | 50% | 30% |

Validate all enabled tiers contain units. Independent draws explicitly do not test contested drafting. Adding a shared pool later requires a separate profile, conservation rules and bot/economy retuning.

### Transactions and merges

Buy, sell, reroll, lock, buy-XP, move, swap and ready are commands with authenticated seat ownership, phase, sequence, request ID and revision checks. A command commits completely or changes nothing. Cache successful replies for idempotent retransmission; reused ID with different payload is an error. A reject does not consume resources. Keep server-authoritative sequencing, not client clock time, for commands at the phase boundary.

Three identical unit types of the same star combine, up to three stars. One three-star represents nine purchased copies. Selling pays `profileCost * 3^(star-1)`; no bonus profit from merging. A full bench purchase may succeed only when the complete transaction merges into a legal arrangement. Reserve a transaction-local pending item; do not expose it as a ninth bench slot.

Choose surviving instance identity from the eligible three deterministically: prefer the lowest-ID deployed unit, otherwise the lowest-index bench unit, then the new pending unit. Preserve the survivor’s preparation location. Remove other members and repeat bounded merges through star three. Never silently move a deployed unit to the bench to simplify the code. Validate next-instance-ID uniqueness.

Move requires owned unit and legal destination; move into an owned occupied cell swaps atomically only when both resulting locations are legal. Board-to-bench swap may not leave deployment over cap. An opponent cell is never a legal preparation destination. Bench capacity is fixed; do not extend it to solve an edge case. Sell during combat is rejected. Ready does not bypass unresolved commands; editing after ready clears readiness. Pairings are fixed for the round, even if a participant later disconnects and is replaced by a bot.

## 2. Coordinates and movement

Internal cell `(column,row)` is zero based. Each captain authors a local 8×4 deployment with local row 0 at the back and row 3 near the center. Side A maps `(c,r)` to `(c,r)` in the encounter; side B maps to `(7-c,7-r)`. Rotate both axes, not only the row, so flanks transform consistently. World positions use the measured 200 cm tile convention; visual offsets do not affect logical range.

Use Chebyshev distance and eight-neighbor movement. Diagonal movement is forbidden if **either** of the two intervening orthogonal cells is occupied/reserved; this is deliberately stricter than the ambiguous earlier wording. There is no terrain obstruction in the first arena. Every unit occupies one cell, independent of model size, star level or race.

Ordinary movement chooses a shortest route to an unoccupied cell within basic attack range of a living enemy. Stable target preference: preserve a valid current enemy when reachable; otherwise nearest reachable enemy, then seeded per-combat initiative index, then stable identity. If no route exists, wait and retry at bounded cadence. Do not keep recalculating every render frame. Do not select a physically nearest but permanently unreachable target forever.

A movement step reserves destination while the origin remains occupied. It completes after the quantized step interval; on completion origin is freed and destination occupied. Two units cannot exchange cells in the same step. Stun or defeat cancels an unfinished movement and releases the reservation; presentation returns/interpolates to the still-occupied origin without changing authoritative state. Process already completed steps before impacts on that tick.

## 3. Numerical units and time

Health, damage, shield and healing use integer centipoints (100 = one displayed point). Percentage modifiers use basis points (1000 = 10%). Attack/movement rates use milli-rates (800 = 0.8 per second). Durations use integer milliseconds aligned to 50 ms. Simulation is 20 Hz; rendering is independent.

`attackIntervalTicks = ceil(1,000,000 / (attackRateMilli * tickMs))`. Apply additive rate modifiers to the base milli-rate with half-up rounding, clamp to 250–2500 milli-attacks/sec, then quantize. Show nominal and effective rates in advanced inspection. Windup must leave at least one recovery tick at maximum permitted attack rate; author attack intervals from the common evaluator, not an unrelated timer in each animation.

Health/basic damage star multipliers are 1.00, 1.80, 3.24. Skills use explicit `magnitude_by_star`, not automatic multiplication. Range, duration, cooldown, footprint, attack speed and stun duration do not grow unless data explicitly changes under a reviewed profile. Status-only skills may remain identical between stars while the owner grows stronger.

Use signed 64-bit intermediates within validated bounds, or explicitly wider arithmetic when needed. For nonnegative `n/d`, round half up once at the designated boundary. Do not use floating-point accumulation for centipoint damage. The Python reference is an arithmetic oracle, not runtime Python embedded into the game.

## 4. Damage, healing and effect order

Physical: `raw * (1 + sourceBonus) * 100/(100+physicalArmor)`.
Magic: same formula with magic resistance.
True: same source-bonus stage, but no defense divisor. It still encounters shields.

Source basic bonuses affect basics only; ability bonuses affect active damage only; all-damage bonuses affect both once. Add applicable source bonuses before mitigation. There are no critical hits, evasion, armor penetration, negative defenses, invulnerability, lifesteal, reflection or randomized accuracy. Round the resolved packet to centipoints, absorb through shield, then reduce health, clamping both at zero. Record requested, resolved, absorbed, health-loss and overkill separately.

A target reaching zero health is immediately ineligible for subsequent heal packets; no revival exists. A released packet can still resolve after its source is defeated. No resurrection is implied by a dissolve animation taking longer than the logical defeat.

Healing caps at maximum health; the effective amount excludes overheal. Lowest-health ally compares fractions exactly, then greater missing centipoints, then initiative/ID. Healing selectors require an injured eligible target; shielding selectors need not. Self-targeting follows the authored flag. A shield cast should reject/no-commit when no recipient would receive a stronger shield or an equal shield with a later expiry; do not waste a ready skill on a guaranteed no-op.

### Shields

Store remaining amount, expiry, original source and effect key. Expire before impacts at that tick. A stronger incoming amount replaces the remaining shield and its expiry. Equal amount takes the later expiry. A weaker shield changes neither amount nor expiry. Replacing remaining shield is not adding pools. Attribute absorption to the currently surviving shield record. Zero-value or already expired effects do nothing.

### Stuns

Stop movement/new actions and interrupt unreleased windups; cooldowns continue. Expiry is `max(existingExpiry,newExpiry)`, not a sum. Stun cannot retroactively recall an already released projectile or a release materialized earlier on the same tick. Refreshing stuns can still create excessive control uptime; measure it rather than claim non-additive behavior prevents chains.

### Temporary attack-rate effects

Use a key composed of ability definition, recipient and stat; duplicate casters of the same ability do not stack. For positive effects keep the strongest magnitude, equal refreshes expiry, weaker is ignored. For negative effects keep the strongest reduction. Distinct keys add to race/class modifiers against the original base; never repeatedly multiply an already buffed value. Recompute on expiry from canonical stats and active records. Changes apply to the next action interval, not an in-progress attack or active cooldown.

Priest support potency scales the **magnitude** of its active healing, shielding and positive attack-rate effects once at release. Example: Elin’s 20% buff with Priest 2 becomes 23%, not 35%; it does not extend duration. The race/class bonuses themselves are not amplified. Negative debuffs receive no Priest amplification. This expands the earlier “heal/shield only” diagnostic fixture intentionally.

## 5. Action and event sequencing

States: Idle, Seeking, Moving, AttackWindup, AttackRecovery, CastWindup, CastRecovery, Stunned, Defeated. Every committed action has an action ID, captured source values and a release tick. Selection and presentation do not create gameplay actions.

Per tick:
1. Expire timed records, update cooldown readiness, cancel invalid reservations.
2. Complete movement that was already due; establish a living-unit snapshot.
3. Materialize releases due now from valid windups into packets. Validate target/destination, capture source values and areas. Zero-travel packets are due this tick. This occurs before impacts, so a same-tick stun does not retroactively cancel that release.
4. Resolve due packets in `(dueTick, seededSourceInitiative, actionSequence, effectIndex, targetInitiative)` order. Mark target defeats immediately and release their reservations. Packets already released survive source defeat.
5. Living idle/recovered units choose an available valid active first, then a basic attack, then movement. Commit only future releases (positive windup); no zero-time recast loops.
6. Assess terminal state. If one side is empty but a released hostile damage packet can still hit a survivor, drain only already released packets before finalizing; survivors stop starting new actions. If both sides are empty, draw. At the hard timeout resolve current-tick impacts, discard later effects and adjudicate immediately.

Seeded stable initiative provides reproducibility, not a guarantee of fairness. Mirror-swap formations and seeds to quantify ordering bias. Never iterate an unordered map as an implicit combat priority. Store build/data versions and RNG stream states; scope replay guarantees to tested build/platform/compiler combinations.

## 6. Skill selectors

- `self`: caster only, no invented target.
- `current_enemy`: current living enemy within skill reach; keep identity for a projectile, expire on invalid target.
- `adjacent_enemies` / `adjacent_allies`: eight neighbors at release; include self only when flagged. Snapshot recipients, not a continuously following aura.
- `lowest_health_ally`: as above, within authored reach, using health fraction and valid-effect eligibility.
- `current_enemy_area`: capture current target’s cell at release, resolve occupants within radius around that **fixed cell** at impact. If the original target leaves or is defeated, the ground burst still occurs. Do not turn it into a homing area.
- `retreat_from_current_enemy`: empty landing within max dash distance, strictly farther from current target and still inside basic range. Prefer greatest separation, shortest dash, then stable cell order.
- `current_enemy_adjacent`: empty cell adjacent to the current target within max dash; require strictly reduced target distance. Prefer shortest dash then stable cell order.
- `farthest_enemy_adjacent`: select farthest living enemy at commitment, tie by initiative; choose a free neighboring cell within maximum dash. If selected target has no valid landing, skill remains ready rather than silently selecting a different target category.

Dash reserves before commitment, crosses intervening units on the unobstructed board and has no implied damage, immunity or invisibility. At release, cancel movement if the landing is illegal or the target disappeared; committed cooldown remains. Endpoint must remain empty; do not displace another unit. Dash ignores ordinary step/corner pathfinding because it is a separately specified magical movement primitive. Interruption releases its reservation. Only the arrival has authoritative occupancy; visual trail is cosmetic.

## 7. Traits

Count distinct deployed definition IDs, not instances, stars or bench units. Snapshot at combat start and retain despite deaths. Every unit has exactly one race and one class. A bonus affects matching units, unless a later reviewed definition explicitly says otherwise.

The adopted 24-hero profile activates the highest eligible tier at two/four distinct deployed definitions; four replaces two. Two-member values: Human +10% health, Elf +10% attack rate, Dwarf +10 armor, Orc +10% direct damage, Halfling +10% ordinary movement, Dragonkin +15 magic resistance. Guardian +15 armor, Warrior/Ranger +15% basic damage, Rogue +15% attack rate, Mage +20% active damage, Priest +15% support magnitude. Four-member values are twice these amounts, applied once to matching recipients. Movement bonuses change ordinary quantized steps only. These are uncalibrated numeric starting values.

Example Rok with Orc and Warrior has 25% combined basic damage bonus, not 26.5%; his positive tempo buff is not direct damage and receives neither. Example a Dwarf Guardian gets +25 physical armor from two distinct additive sources. Maximum-health bonuses apply before initializing battle health. No trait emits hidden attacks or grants extra skills.

## 8. Test fixtures and pacing

120 physical versus 50 armor → 80 damage. With 30 shield, health loses 50. 120 magic versus 20 resistance → 100. 90 true with 40 shield → 50 health loss. Heal 100 at 950/1000 → 50 effective. 0.8 attacks/sec with +10% and +15% → 1.0 nominal and effective at 20 Hz. 100 base attack with +25% versus 25 armor → 100. 1000 base health, two stars and +25% health → 2250.

The desired session experience is roughly 15–25 minutes, but the maximum phase durations do not promise that target. Measure actual match length including readiness, elimination and timeout prevalence. Candidate health loss per defeat is stage base 2/4/6 plus enemy survivors; draws lose two. No star contribution. Detailed ranking and settlement live in `TOURNAMENT_AND_BOTS.md`.

## Authoring and scaling safeguard

Ability magnitude arrays already contain the exact one-, two- and three-star values. Select the appropriate array element and then apply eligible source/trait modifiers once; do **not** multiply that element by the health/basic-attack star multiplier again. The `[1.0, 1.8, 3.24]` multiplier governs base health and basic attack damage only. Buff/control durations, ranges, areas and cooldowns remain the explicit authored values. Each hero has one active ability with a bounded ordered list of explicitly authored effects. Neris Starbind applies its declared magic damage then 1250 ms stun to a surviving target; Mage scales only the damage. Dash-only skills have no hidden damage. Null neutral abilities represent ordinary attacks only. Finn targets the highest current basic-attack-rate eligible enemy with distance/stable-ID ties; Oren skips shields rejected by the stronger-shield policy. See the adopted individual hero briefs and canonical effects arrays.

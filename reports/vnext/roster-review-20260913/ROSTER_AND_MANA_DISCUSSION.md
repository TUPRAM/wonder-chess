# Wonder Chess roster and mana discussion

Derived source snapshot: 13 September 2026. Discussion only: no combat, roster, balance or milestone acceptance change is authorized by this document. Proposed activation types and mana values below are not implemented or accepted tuning.

Current development profile: `wonder_vnext`, balance `wonder_vnext_solo_0.1.0`. Fourteen authored heroes: six executable laboratory candidates and eight designs without combat stats. Nine race and nine class traits remain inactive. The preserved 24-hero `alpha_24` catalogue is included separately; it is not the successor shop roster.

- Successor source: `data/vnext/catalog.json`; SHA-256 `6e80932173071ef05e58d90a44db3490cfcfde86d48edf33f4a940ff1748efa0`.
- Legacy source: `data/units.json`; SHA-256 `9a6820950d17b10ae870f4b61c4a28cebce58d9dcc1d9bead0121cb278943f11`.
- Runtime semantics checked in `game/Source/WonderChessRuntime/Private/Simulation/WonderSimulation.cpp`.

## Reading the stats

HP, basic damage, damage skills and healing are shown in ordinary points (100 stored centipoints = 1 point). Attack rate is nominal attacks/second; movement is nominal cells/second. Actual scheduling uses 50 ms ticks. Range is in cells. Armor and magic resistance are flat ratings, not percentages. Positive defense applies the factor 100/(100 + defense) to its matching damage type. Baseline stats exclude relics. Successor HP and basic damage scale by 1 / 1.8 / 3.24 across stars; ability values use their explicit star arrays.

## Six executable successor heroes

| Hero | Race | Class | Cost | HP | Basic damage | Attacks/s | Range | Armor | Magic resistance | Move/s |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Bellback | Beast | Guardian | 1 | 950 | 55 | 0.7 | 1 | 35 | 15 | 1 |
| Cragstoat | Beast | Warrior | 1 | 650 | 70 | 1 | 1 | 15 | 15 | 1.3 |
| Grandmother Root | Plant | Healer | 2 | 700 | 42 | 0.65 | 3 | 10 | 15 | 0.8 |
| Snapvine | Plant | Assassin | 3 | 700 | 75 | 0.85 | 2 | 15 | 15 | 1.1 |
| Prism Organ | Construct | Mage | 4 | 800 | 60 | 0.7 | 4 | 20 | 15 | 0.85 |
| Reefglass | Tidekin | Controller | 5 | 1000 | 65 | 0.8 | 3 | 25 | 15 | 1 |

All six have physical basic attacks and a 0.15 s basic-attack windup. Bellback and Cragstoat have zero basic projectile travel; the other four use 0.20 s. These are playable mechanics with prototype presentation, not final art or accepted balance.

### Bellback — Sheltering Bell

True passive: reduces damage to one eligible ally behind Bellback by 30% when the incoming origin is in the guarded forward sector. Base protection radius 1. It does not protect itself; strongest applicable guard wins rather than stacking. Stun/defeat disables the guard. The generic source effect label is shield, but this mechanic is directional mitigation, not a temporary shield pool. Generic cast/cooldown fields are bypassed for this passive.

HP by star: 950 / 1710 / 3078. Basic damage by star: 55 / 99 / 178.2.

Suggested direction (unimplemented): **Passive**. Keep directional protection available immediately.

### Cragstoat — Stonebound Lunge

Physical charge dealing 130 / 210 / 330 base damage across stars, with a clear straight path and a legal landing beside the target, up to 3 dash cells. Damage gains 15% per momentum/charge-distance step, capped at 4 steps (+60%). Ordinary completed movement stores momentum. A charge against an already adjacent target requires stored momentum; a nonadjacent legal dash can contribute its own charge distance. Stored momentum is consumed on release. Screens and occupied landing cells can deny it.

HP by star: 650 / 1170 / 2106. Basic damage by star: 70 / 126 / 226.8.

Current readiness: earliest timer 1.5 s, cooldown 6 s from commitment, cast 0.35 s, recovery 0.3 s. Target, positioning and other conditions can delay or prevent commitment; this is not a guaranteed first-cast timestamp.

Suggested direction (unimplemented): **Conditional charge**. Keep movement/path requirements; avoid a second mana readiness gate.

### Grandmother Root — Stay and Blossom

After remaining stationary for 1.5 s and finding an injured eligible ally, establishes a finite healing grove of radius 2, including herself. Heals 35 / 55 / 90 per eligible ally per pulse. Four pulses occur at release, +1 s, +2 s and +3 s, for up to 140 / 220 / 360 before overhealing or interruption. Moving, displacement, stun or defeat breaks establishment/tethered future pulses. Maximum 10 recipients per pulse.

HP by star: 700 / 1260 / 2268. Basic damage by star: 42 / 75.6 / 136.08.

Current readiness: earliest timer 1.5 s, cooldown 6 s from commitment, cast 0.35 s, recovery 0.3 s. Target, positioning and other conditions can delay or prevent commitment; this is not a guaranteed first-cast timestamp.

Suggested direction (unimplemented): **Stationary conditional cast; keep current cooldown initially**. A later mana-funded grove is possible, but isolate the initial mana experiment from healing feedback.

### Snapvine — Thornline

Aims toward the farthest in-range enemy, then strikes the first enemy intercepting its committed line for 200 / 320 / 500 physical damage. Ability range 6; maximum one victim. It does not teleport or guarantee a hit on the backline when a screen intercepts.

HP by star: 700 / 1260 / 2268. Basic damage by star: 75 / 135 / 243.

Current readiness: earliest timer 1.5 s, cooldown 6 s from commitment, cast 0.35 s, recovery 0.3 s. Target, positioning and other conditions can delay or prevent commitment; this is not a guaranteed first-cast timestamp.

Suggested direction (unimplemented): **100-mana automatic cast**. Preserve the screenable committed strike.

### Prism Organ — Crossing Hymn

Locks a target point, releases a row beam and then a column beam 0.4 s later. Each beam deals 170 / 270 / 420 magic damage; a surviving enemy remaining at the intersection can take both. Aim range 6; beam arms extend 3 cells from the locked center. Cast commitment lasts 1 s. Spreading and interrupting the marked setup provide counterplay.

HP by star: 800 / 1440 / 2592. Basic damage by star: 60 / 108 / 194.4.

Current readiness: earliest timer 1.5 s, cooldown 6 s from commitment, cast 1 s, recovery 0.3 s. Target, positioning and other conditions can delay or prevent commitment; this is not a guaranteed first-cast timestamp.

Suggested direction (unimplemented): **100-mana automatic cast**. Preserve the telegraph and sequential crossing beams.

### Reefglass — Leading Tide

Strikes an oriented cardinal lane up to 6 cells for 180 / 290 / 460 magic damage per eligible enemy, pushing the first enemy up to 2 available legal cells. Maximum 8 targets. It waits while no enemy occupies its facing lane; blocking the push destination limits displacement.

HP by star: 1000 / 1800 / 3240. Basic damage by star: 65 / 117 / 210.6.

Current readiness: earliest timer 1.5 s, cooldown 6 s from commitment, cast 0.35 s, recovery 0.3 s. Target, positioning and other conditions can delay or prevent commitment; this is not a guaranteed first-cast timestamp.

Suggested direction (unimplemented): **100-mana automatic cast**. Still require the facing lane and legal displacement rules.

## Eight authored successor designs

These have no numeric HP, attacks, defenses, movement, skill magnitudes or skill timings. Their costs, race/class memberships and ability concepts are authored. Proposed activation is a discussion recommendation.

| Hero | Race / class | Cost | Authored skill | Authored behavior | Suggested activation |
| --- | --- | --- | --- | --- | --- |
| Silkmother | Insect / Engineer | 2 | Twin Lantern Line | Set a finite trip line between two destructible anchors. | Finite opening construction |
| Manyfoot | Insect / Warrior | 2 | Pour and Re-form | Flow around a defender and re-form behind it as one logical unit. | 100-mana automatic cast plus legal destination |
| Kilnback | Construct / Guardian | 3 | Furnace Count | Capture a bounded number of frontal projectiles and vent steam afterward. | Reactive passive counter |
| Coilwyrm | Dragon / Controller | 5 | Pearl Constriction | Create a delayed constricting ring with a safe center. | 100-mana automatic cast |
| Dawnkite | Dragon / Ranger | 4 | Dawn Fan | Commit to a sweeping fan attack across a chosen sector. | 100-mana automatic cast |
| Thimblewake | Fae / Duelist | 3 | Petal Challenge | Challenge an isolated opponent with a short parry and riposte. | Conditional parry/riposte |
| Wren | Human / Engineer | 1 | Wayside Workshop | Deploy a limited repair station for nearby allies. | Finite opening construction |
| Hushlantern | Spirit / Healer | 4 | Remembered Health | Restore a capped part of recent lost health after a delay; never revive. | 100-mana automatic rescue plus eligible lost HP |

**Silkmother** — Eight-legged silk architect carrying a warm lantern abdomen. Positioning: Place anchors where an approach is likely without exposing both to one attack. Counterplay: Use another route or destroy an anchor with ranged attacks. Proposed activation boundary: One bounded anchor pair initially; replacement rules need a separate decision.

**Manyfoot** — A single coordinated colony of iridescent beetles sharing one banner-shaped shell. Positioning: Seek a target with a free rear cell and avoid crowded clusters. Counterplay: Occupy rear cells; concentrated area damage pressures the single shared health pool. Proposed activation boundary: One logical unit and one HP pool; hold full mana while the destination is blocked.

**Kilnback** — A squat glazed furnace-tortoise with hinged shield plates and steam valves. Positioning: Face ranged lanes and put allies outside the vent recovery opening. Counterplay: Melee attacks and side lanes bypass its collection arc. Proposed activation boundary: Frontal projectile capture and a bounded vent already form its charge mechanic.

**Coilwyrm** — A long branch-antlered dragon coiling around a suspended pearl. Positioning: Aim to divide formations at the edge rather than cover every enemy. Counterplay: Spread, occupy the safe center, or interrupt the setup. Proposed activation boundary: Keep the delayed ring and safe center.

**Dawnkite** — A broad-winged dragon with layered dawn-colored membranes and a forked tail. Positioning: Protect its back and aim a long diagonal across several threats. Counterplay: Close flanks and rear pressure exploit its directional commitment. Proposed activation boundary: Keep the committed sector and flank exposure.

**Thimblewake** — A flower-mantis noble with petal armor and needlelike forearms. Positioning: Find a side fight away from nearby enemy support. Counterplay: Keep support nearby and apply ranged pressure outside the parry window. Proposed activation boundary: Isolation, a bounded parry window and recovery should govern it.

**Wren** — A practical itinerant tinkerer accompanying a little walking repair cart. Positioning: Choose a station site that supports the front without feeding free demolition. Counterplay: Destroy the station or move the fight outside its service radius. Proposed activation boundary: One repair station initially; no unlimited station accumulation.

**Hushlantern** — An empty rain-cloak with a lantern where a head might be and trailing firefly echoes. Positioning: Stay close enough to a threatened ally while avoiding simultaneous area interruption. Counterplay: Burst through the delay or interrupt the rescue before release. Proposed activation boundary: Keep the delay, capped rescue to a living target and interruption.

## Race and class design inventory

All 18 bonuses below are authored and disabled in the successor runtime. Thresholds count distinct deployed recruited types; the higher tier replaces the lower tier. Several thresholds are unreachable with the currently authored membership, so these are ecosystem designs awaiting further development. Membership alone does not currently grant a bonus.

### Class traits

| Class | Thresholds | Members | Design name | Authored behavior |
| --- | --- | --- | --- | --- |
| Guardian | 2/4 | Bellback, Kilnback | Held line | Guard matching allies in adjacent rear cells using visible directed links. |
| Warrior | 3/6 | Cragstoat, Manyfoot | Sustained pressure | Matching units build capped pressure while remaining in close engagement; resets after disengagement. |
| Duelist | 2/4 | Thimblewake | Single challenge | Matching units obtain a bounded defensive window against an isolated opponent. |
| Ranger | 2/4/6 | Dawnkite | Clear firing lanes | Matching units benefit from protected straight firing lanes, losing the benefit when threatened nearby. |
| Mage | 3/5 | Prism Organ | Prepared magic | Matching units build cast stability while allies screen nearby approaches. |
| Healer | 2/3 | Grandmother Root, Hushlantern | Care network | Matching healers split a bounded fraction of effective rescue to another injured ally. |
| Controller | 2/4 | Reefglass, Coilwyrm | Follow through | Matching control effects expose a short displacement follow-up window, once per target. |
| Engineer | 2/3 | Silkmother, Wren | Service radius | Matching constructions exchange a bounded service charge inside overlapping radii. |
| Assassin | 2/4 | Snapvine | Open approach | Matching units gain one commitment benefit when reaching an unscreened target. |

### Race traits

| Race | Thresholds | Members | Design name | Authored behavior |
| --- | --- | --- | --- | --- |
| Beast | 2/4/6 | Bellback, Cragstoat | Pack momentum | Matching creatures gain a brief movement burst when an ally finishes a charge; no recursive triggers. |
| Plant | 2/3/5 | Grandmother Root, Snapvine | Established ground | Matching creatures grow a bounded protective layer while stationary; displacement clears growth. |
| Insect | 2/4 | Silkmother, Manyfoot | Colony routes | Matching units gain a brief route bonus near friendly constructions, with one refresh per crossing. |
| Construct | 2/3/5 | Prism Organ, Kilnback | Stored energy | Matching units store a bounded intercepted or absorbed hit count to shorten the next recovery. |
| Human | 2/3 | Wren | Ingenuity | The first distinct allied station interaction each combat grants a bounded utility charge. |
| Tidekin | 2/4 | Reefglass | Changing currents | Successful displacements leave short directional currents supporting following allies. |
| Fae | 2/3 | Thimblewake | Unshared attention | Matching units receive a short timing advantage in isolated engagements. |
| Spirit | 2/4 | Hushlantern | Echo memory | Matching rescuers retain a bounded recent-damage window; no revival or recursive rescue. |
| Dragon | 2/3 | Coilwyrm, Dawnkite | Committed majesty | Matching dragons extend telegraph commitment in exchange for a stronger spatial effect. |

## Seven successor neutral creatures

All currently use basic attacks only, with no active or passive special skill and no authored race/class membership. Their special encounter teaching mechanics remain future work. All have 0.8 nominal attacks/s, armor 10, magic resistance 10, movement 0.9 cells/s and a 0.15 s attack windup. Basic attacks are physical; melee projectile travel is zero and ranged travel is 0.2 s.

| Neutral | HP | Basic damage | Range |
| --- | --- | --- | --- |
| Skittering Seedpod | 210 | 21 | 1 |
| Reed Archer | 180 | 28 | 4 |
| Lantern Bulb | 280 | 18 | 2 |
| Slate Ram | 800 | 55 | 1 |
| Glass Moth | 450 | 60 | 4 |
| Root Sentinel | 1350 | 80 | 1 |
| Hollow Bellkeeper | 2200 | 100 | 3 |

## Proposed mana contract — discussion, not implementation

Keep three readable activation families: passive, conditional/reaction, and automatic mana cast. The battle remains automatic; the player influences it through recruitment, placement, facing, scouting and relics.

1. Use a 100-mana maximum. An initial test can start at 0 each encounter; per-hero starting mana is a tuning option after first-cast measurements.
2. Illustrative gain: 10 mana for a landed basic attack, once per attack rather than per area victim; plus 10 mana per 10% maximum HP actually lost to enemy damage after mitigation. Choose explicit per-event and per-time caps before implementation. These are experiment values, not accepted balance.
3. Abilities, healing, reflected damage and owned construction/summon damage do not award additional outgoing mana. No mana from applying a heal or shield, and no self/friendly-damage farming. Healing conversion must be reviewed for feedback loops.
4. At 100, cast automatically when all target/space/hero conditions are legal. Retain 100 while blocked. Spend at commitment; no refund after an interrupted committed cast. Initially pause mana gain during cast and recovery. Stun blocks commitment. Reset between encounters.
5. Mana replaces the routine cooldown gate for migrated heroes; preserve their visible windup and short recovery. Do not silently require both a full old cooldown and a full mana bar.
6. Revise cooldown-sensitive relic contracts before enabling migrated heroes with those relics. Quick Wick, Patient Lantern, Far Hourglass, Wide Hourglass, Narrow Metronome and Urgent Shard currently have non-neutral cooldown modifiers; each benefit and drawback must continue to function.
7. Show mana only for heroes that use it. Distinguish charging, ready but blocked, and casting. Show the blocking condition clearly, and use appropriate passive/condition indicators for other heroes.

At 0.7 attacks/s, earning 100 solely from ten attacks takes on the order of 13–15 seconds once attacking begins, depending on the first attack and scheduling. Current active timers permit commitment from 1.5 seconds. Consequently 100 maximum, 0 starting and 10 per hit can be a major cadence change; mana is not inherently a pacing improvement. Incoming damage and different starting mana alter this example.

## Recommended bounded development sequence after discussion

1. Define activation/resource state and the mana-event rules. Keep canonical data explicit; do not infer casting mode solely from class.
2. Compare an isolated mana candidate for Snapvine, Prism Organ and Reefglass with the current control. Keep prices, targeting, damage, captain-loss rules, Bellback, Cragstoat and Root unchanged. Resolve relic compatibility as an explicit part of the comparison.
3. Verify deterministic event order, attack versus spell gain, post-mitigation incoming gain, caps, full-mana blocked targets, interruption spending, death/reset, cast recovery and relic effects in native and packaged combat.
4. Measure first-cast time, casts per fight, death before casting, death with unspent mana, full-mana blocked time, encounter timeouts and tournament caps. Include protected and exposed formations and all star levels.
5. Human playtests must establish whether people can predict and explain activation, recognize meaningful counters and prefer the resulting decisions. Stop broad conversion if protection routinely prevents signature casts, sustain/caps regress, passive identities become obscure, or the gain rules are not understandable.
6. Revisit full ability swaps after the activation comparison. Candidate design questions: Snapvine as a ranged backline hunter versus a relocating assassin; Root as sustained area healing versus limited rescue; Wren repair versus Kilnback protection versus Silkmother route control. These are decisions to discuss, not adopted replacements.

## Appendix — preserved legacy 24-hero catalogue

This is the separate `alpha_24` comparison profile, balance `alpha_24_v0.4.1`. Values below are read from its authored canonical catalogue, not an assertion of fresh runtime/visual acceptance. They are not additional successor shop entries and no mana conversion is proposed here.

| Hero | Race / class | Cost | HP | Basic damage | Attacks/s | Range | Armor | Magic resistance | Move/s | Skill |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Ada Brightshield | Human / Guardian | 1 | 1050 | 48 | 0.7 | 1 | 35 | 15 | 1 | Sun Guard |
| Mira Dawnwell | Human / Priest | 1 | 650 | 34 | 0.75 | 3 | 10 | 20 | 1.05 | Mend |
| Rowan Emberwick | Human / Mage | 2 | 620 | 45 | 0.7 | 3 | 8 | 20 | 1 | Ember Burst |
| Liora Leafstep | Elf / Ranger | 1 | 670 | 60 | 0.85 | 4 | 10 | 10 | 1.15 | Leafstep |
| Elin Moonsong | Elf / Priest | 2 | 700 | 35 | 0.8 | 3 | 10 | 25 | 1.05 | Quick Song |
| Sylas Duskrun | Elf / Rogue | 3 | 790 | 74 | 1.05 | 1 | 18 | 12 | 1.25 | Backline Leap |
| Borin Stonebell | Dwarf / Guardian | 1 | 1100 | 44 | 0.65 | 1 | 40 | 10 | 0.9 | Bell Stomp |
| Tessa Brassbolt | Dwarf / Ranger | 2 | 760 | 68 | 0.8 | 4 | 20 | 10 | 0.95 | Heavy Bolt |
| Dagna Anvilheart | Dwarf / Warrior | 2 | 1000 | 70 | 0.8 | 1 | 25 | 15 | 1 | Hammer Sweep |
| Rok Sunward | Orc / Warrior | 1 | 950 | 64 | 0.85 | 1 | 20 | 15 | 1.1 | Battle Rhythm |
| Zura Stormcall | Orc / Mage | 3 | 750 | 50 | 0.75 | 3 | 12 | 25 | 1 | Storm Ring |
| Kesh Quickwind | Orc / Rogue | 2 | 820 | 67 | 1 | 1 | 15 | 10 | 1.25 | Quickstep |
| Cass Vale | Human / Warrior | 2 | 980 | 72 | 0.8 | 1 | 25 | 15 | 1.05 | Firm Strike |
| Neris Starbloom | Elf / Mage | 3 | 690 | 48 | 0.75 | 4 | 8 | 30 | 1.05 | Starbind |
| Orla Hearthglow | Dwarf / Priest | 2 | 820 | 36 | 0.7 | 2 | 20 | 25 | 0.95 | Hearth Glow |
| Tala Ironroot | Orc / Guardian | 2 | 1120 | 45 | 0.65 | 1 | 30 | 20 | 0.9 | Shared Guard |
| Pippa Oakstride | Halfling / Warrior | 1 | 760 | 54 | 0.95 | 1 | 20 | 10 | 1.2 | Stout Heart |
| Finn Thistlearrow | Halfling / Ranger | 1 | 590 | 49 | 1 | 4 | 8 | 10 | 1.25 | Dulling Shot |
| Nella Quickpocket | Halfling / Rogue | 2 | 660 | 58 | 1.1 | 1 | 12 | 12 | 1.3 | Quick Feint |
| Milo Mistwhistle | Halfling / Mage | 2 | 570 | 42 | 0.8 | 3 | 8 | 20 | 1.15 | Mist Pop |
| Sora Dawnscale | Dragonkin / Guardian | 3 | 1180 | 48 | 0.65 | 1 | 30 | 30 | 0.95 | Beacon Shield |
| Varek Prismshot | Dragonkin / Ranger | 2 | 720 | 56 | 0.85 | 4 | 12 | 25 | 1.05 | Prism Shot |
| Iri Cinderstep | Dragonkin / Rogue | 3 | 730 | 65 | 1.05 | 1 | 15 | 20 | 1.25 | Prism Cut |
| Oren Skyward | Dragonkin / Priest | 2 | 800 | 38 | 0.75 | 3 | 15 | 30 | 1 | Sky Ward |

### Ada Brightshield — Sun Guard

Gains a shield for three seconds.

Basic attack: physical, melee; windup 0.25 s, projectile travel 0 s.

Skill: first timer 2 s; cooldown 8 s; cast 0.3 s; recovery 0.3 s; travel 0 s; range 0; radius 0; maximum dash 0; maximum targets 12; selector `self`; allow self true.

- shield: 200 / 360 / 648 points (1/2/3 stars); duration 3 s.

### Mira Dawnwell — Mend

Heals the ally with the lowest health percentage.

Basic attack: magic, ranged; windup 0.3 s, projectile travel 0.15 s.

Skill: first timer 3 s; cooldown 7 s; cast 0.35 s; recovery 0.3 s; travel 0 s; range 8; radius 0; maximum dash 0; maximum targets 12; selector `lowest_health_ally`; allow self true.

- heal: 180 / 324 / 583 points (1/2/3 stars); duration 0 s.

### Rowan Emberwick — Ember Burst

Damages enemies around the target’s captured location.

Basic attack: magic, ranged; windup 0.3 s, projectile travel 0.15 s.

Skill: first timer 3.5 s; cooldown 8 s; cast 0.45 s; recovery 0.3 s; travel 0.25 s; range 4; radius 1; maximum dash 0; maximum targets 12; selector `current_enemy_area`; allow self false.

- damage (magic): 150 / 270 / 486 points (1/2/3 stars); duration 0 s.

### Liora Leafstep — Leafstep

Dashes away from her target while keeping it in range.

Basic attack: physical, ranged; windup 0.3 s, projectile travel 0.15 s.

Skill: first timer 2 s; cooldown 7.5 s; cast 0.2 s; recovery 0.15 s; travel 0 s; range 4; radius 0; maximum dash 2; maximum targets 12; selector `retreat_from_current_enemy`; allow self false.

- dash: no numeric magnitude; movement/duration supplies the effect; duration 0 s.

### Elin Moonsong — Quick Song

Temporarily increases nearby allies’ attack speed.

Basic attack: magic, ranged; windup 0.3 s, projectile travel 0.15 s.

Skill: first timer 2.5 s; cooldown 9 s; cast 0.35 s; recovery 0.3 s; travel 0 s; range 1; radius 1; maximum dash 0; maximum targets 12; selector `adjacent_allies`; allow self true.

- stat modifier: 20% / 25% / 30% (1/2/3 stars); stat attack_rate; duration 3 s.

### Sylas Duskrun — Backline Leap

Dashes beside the farthest enemy when a landing tile is free.

Basic attack: physical, melee; windup 0.25 s, projectile travel 0 s.

Skill: first timer 1 s; cooldown 8.5 s; cast 0.2 s; recovery 0.15 s; travel 0 s; range 8; radius 0; maximum dash 7; maximum targets 12; selector `farthest_enemy_adjacent`; allow self false.

- dash: no numeric magnitude; movement/duration supplies the effect; duration 0 s.

### Borin Stonebell — Bell Stomp

Stuns adjacent enemies for one second.

Basic attack: physical, melee; windup 0.25 s, projectile travel 0 s.

Skill: first timer 3 s; cooldown 8.5 s; cast 0.4 s; recovery 0.3 s; travel 0 s; range 1; radius 1; maximum dash 0; maximum targets 12; selector `adjacent_enemies`; allow self false.

- stun: no numeric magnitude; movement/duration supplies the effect; duration 1 s.

### Tessa Brassbolt — Heavy Bolt

Fires a stronger physical shot at her current target.

Basic attack: physical, ranged; windup 0.3 s, projectile travel 0.15 s.

Skill: first timer 2.5 s; cooldown 6.5 s; cast 0.35 s; recovery 0.3 s; travel 0.15 s; range 4; radius 0; maximum dash 0; maximum targets 12; selector `current_enemy`; allow self false.

- damage (physical): 170 / 306 / 551 points (1/2/3 stars); duration 0 s.

### Dagna Anvilheart — Hammer Sweep

Damages all adjacent enemies.

Basic attack: physical, melee; windup 0.35 s, projectile travel 0 s.

Skill: first timer 3.5 s; cooldown 8 s; cast 0.4 s; recovery 0.3 s; travel 0 s; range 1; radius 1; maximum dash 0; maximum targets 12; selector `adjacent_enemies`; allow self false.

- damage (physical): 140 / 252 / 454 points (1/2/3 stars); duration 0 s.

### Rok Sunward — Battle Rhythm

Temporarily increases his attack speed.

Basic attack: physical, melee; windup 0.35 s, projectile travel 0 s.

Skill: first timer 2.5 s; cooldown 8.5 s; cast 0.25 s; recovery 0.3 s; travel 0 s; range 0; radius 0; maximum dash 0; maximum targets 12; selector `self`; allow self true.

- stat modifier: 30% / 35% / 40% (1/2/3 stars); stat attack_rate; duration 3 s.

### Zura Stormcall — Storm Ring

Strikes enemies around a captured enemy location with magic.

Basic attack: magic, ranged; windup 0.3 s, projectile travel 0.15 s.

Skill: first timer 4 s; cooldown 10 s; cast 0.6 s; recovery 0.3 s; travel 0.3 s; range 4; radius 2; maximum dash 0; maximum targets 12; selector `current_enemy_area`; allow self false.

- damage (magic): 190 / 342 / 616 points (1/2/3 stars); duration 0 s.

### Kesh Quickwind — Quickstep

Dashes beside the current target within three tiles.

Basic attack: physical, melee; windup 0.25 s, projectile travel 0 s.

Skill: first timer 1.5 s; cooldown 6.5 s; cast 0.2 s; recovery 0.15 s; travel 0 s; range 4; radius 0; maximum dash 3; maximum targets 12; selector `current_enemy_adjacent`; allow self false.

- dash: no numeric magnitude; movement/duration supplies the effect; duration 0 s.

### Cass Vale — Firm Strike

Delivers a stronger physical hit to the current target.

Basic attack: physical, melee; windup 0.35 s, projectile travel 0 s.

Skill: first timer 3 s; cooldown 7.5 s; cast 0.35 s; recovery 0.3 s; travel 0 s; range 1; radius 0; maximum dash 0; maximum targets 12; selector `current_enemy`; allow self false.

- damage (physical): 180 / 324 / 583 points (1/2/3 stars); duration 0 s.

### Neris Starbloom — Starbind

Deal 60 / 108 / 194.4 magic damage to the current enemy, then stun it for 1.25 seconds if it survives. Mage bonuses affect damage only.

Basic attack: magic, ranged; windup 0.3 s, projectile travel 0.15 s.

Skill: first timer 3.5 s; cooldown 9.5 s; cast 0.4 s; recovery 0.3 s; travel 0.2 s; range 4; radius 0; maximum dash 0; maximum targets 12; selector `current_enemy`; allow self false.

- damage (magic): 60 / 108 / 194.4 points (1/2/3 stars); duration 0 s.
- stun: no numeric magnitude; movement/duration supplies the effect; duration 1.25 s.

### Orla Hearthglow — Hearth Glow

Heals herself and adjacent allies.

Basic attack: magic, ranged; windup 0.3 s, projectile travel 0.15 s.

Skill: first timer 3 s; cooldown 8 s; cast 0.35 s; recovery 0.3 s; travel 0 s; range 1; radius 1; maximum dash 0; maximum targets 12; selector `adjacent_allies`; allow self true.

- heal: 125 / 225 / 405 points (1/2/3 stars); duration 0 s.

### Tala Ironroot — Shared Guard

Shields herself and adjacent allies for three seconds.

Basic attack: physical, melee; windup 0.25 s, projectile travel 0 s.

Skill: first timer 2.5 s; cooldown 9.5 s; cast 0.35 s; recovery 0.3 s; travel 0 s; range 1; radius 1; maximum dash 0; maximum targets 12; selector `adjacent_allies`; allow self true.

- shield: 140 / 252 / 454 points (1/2/3 stars); duration 3 s.

### Pippa Oakstride — Stout Heart

Gains a temporary personal shield.

Basic attack: physical, melee; windup 0.35 s, projectile travel 0 s.

Skill: first timer 2 s; cooldown 7.5 s; cast 0.25 s; recovery 0.3 s; travel 0 s; range 0; radius 0; maximum dash 0; maximum targets 12; selector `self`; allow self true.

- shield: 150 / 270 / 486 points (1/2/3 stars); duration 2.5 s.

### Finn Thistlearrow — Dulling Shot

Reduce the basic attack rate of the in-range enemy with the highest current attack rate. Ties prefer the nearer enemy, then stable identity. Movement and skill cooldowns are unchanged.

Basic attack: physical, ranged; windup 0.3 s, projectile travel 0.15 s.

Skill: first timer 2.5 s; cooldown 8 s; cast 0.3 s; recovery 0.3 s; travel 0.15 s; range 4; radius 0; maximum dash 0; maximum targets 12; selector `highest_attack_rate_enemy`; allow self false.

- stat modifier: -20% / -25% / -30% (1/2/3 stars); stat attack_rate; duration 3 s.

### Nella Quickpocket — Quick Feint

Stuns the current target for one second.

Basic attack: physical, melee; windup 0.25 s, projectile travel 0 s.

Skill: first timer 2 s; cooldown 7.5 s; cast 0.2 s; recovery 0.3 s; travel 0 s; range 1; radius 0; maximum dash 0; maximum targets 12; selector `current_enemy`; allow self false.

- stun: no numeric magnitude; movement/duration supplies the effect; duration 1 s.

### Milo Mistwhistle — Mist Pop

Bursts magic around the target’s captured location.

Basic attack: magic, ranged; windup 0.3 s, projectile travel 0.15 s.

Skill: first timer 3 s; cooldown 7 s; cast 0.35 s; recovery 0.3 s; travel 0.2 s; range 4; radius 1; maximum dash 0; maximum targets 12; selector `current_enemy_area`; allow self false.

- damage (magic): 135 / 243 / 437 points (1/2/3 stars); duration 0 s.

### Sora Dawnscale — Beacon Shield

Gains a strong shield for three seconds.

Basic attack: physical, melee; windup 0.25 s, projectile travel 0 s.

Skill: first timer 2.5 s; cooldown 9 s; cast 0.35 s; recovery 0.3 s; travel 0 s; range 0; radius 0; maximum dash 0; maximum targets 12; selector `self`; allow self true.

- shield: 240 / 432 / 778 points (1/2/3 stars); duration 3 s.

### Varek Prismshot — Prism Shot

Fires a stronger magic shot at the current target.

Basic attack: magic, ranged; windup 0.3 s, projectile travel 0.15 s.

Skill: first timer 3 s; cooldown 7.5 s; cast 0.35 s; recovery 0.3 s; travel 0.15 s; range 4; radius 0; maximum dash 0; maximum targets 12; selector `current_enemy`; allow self false.

- damage (magic): 160 / 288 / 518 points (1/2/3 stars); duration 0 s.

### Iri Cinderstep — Prism Cut

Deals a small true-damage hit to the current target.

Basic attack: physical, melee; windup 0.25 s, projectile travel 0 s.

Skill: first timer 2.5 s; cooldown 8 s; cast 0.25 s; recovery 0.3 s; travel 0 s; range 1; radius 0; maximum dash 0; maximum targets 12; selector `current_enemy`; allow self false.

- damage (true): 100 / 180 / 324 points (1/2/3 stars); duration 0 s.

### Oren Skyward — Sky Ward

Shield the lowest-health eligible ally in range, including self. Skip an ally whose existing shield would reject the ward; remain ready when no ally can benefit.

Basic attack: magic, ranged; windup 0.3 s, projectile travel 0.15 s.

Skill: first timer 2.5 s; cooldown 8 s; cast 0.35 s; recovery 0.3 s; travel 0 s; range 8; radius 0; maximum dash 0; maximum targets 12; selector `lowest_health_ally`; allow self true.

- shield: 190 / 342 / 616 points (1/2/3 stars); duration 3 s.

## Verification of this inventory

Extracted directly from the two canonical JSON sources. Verified counts: 14 successor heroes (6 enabled and 8 without numeric stat blocks), 18 inactive successor traits, 7 successor neutrals, and 24 legacy heroes. Canonical source hashes were checked unchanged after writing. No combat code/data was edited and no new gameplay test was run for this discussion. Runtime interpretation was checked against the existing simulation source; mana recommendations remain untested.

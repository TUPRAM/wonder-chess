# Wonder Chess update: systems migration proposal

**Execution note:** the user adopted this migration on 6 September 2026. The starting-point inventory below is retained history. The current C++ core, canonical data, generated catalog and meaningful fixtures implement the migration; inspect `reports/implementation_state.json` and fresh run evidence instead of treating the original constraints as current blockers. Numeric tuning and its current digest are owned by canonical data.

Status: prepared for discussion and later implementation, 6 September 2026. This file does not change live rules, generated data, assets or release acceptance. The user selected **all 24 authored heroes fully playable** and **visual equipment only**. There is no item inventory, item stat system, equipment loot or equipment purchase in this update.

When the accompanying implementation prompt is adopted, migrate the selected v3 restrictions explicitly: twelve playable heroes become 24; four active races become six; tier two becomes tiers two and four; the all-PvP schedule gains monster rounds. Preserve the original Unreal deliverable, eight persistent competitors, real off-screen combat, original world and characters, legal bot commands, information boundaries and actual packaged verification. All new numbers below are proposed starting values, not balanced results.

## 1. Verified starting point and migration sites

The canonical roster has exactly 24 definitions: six races with four heroes each and six classes with four heroes each. The races are Human, Elf, Dwarf, Orc, Halfling and Dragonkin. Halfling and Dragonkin are authored expansion peoples; do not invent replacement races. Existing stable hero, ability and trait IDs remain the identity keys when visible names are shortened.

| Existing source | Current behavior or constraint | Required migration |
|---|---|---|
| `data/rules.alpha.json` | Twelve `alpha_unit_ids`, active threshold `[2]`, 24-round cap, six deployment slots | Activate all 24 authored IDs in the existing profile; add explicit schedule and reward rules; change the proposed cap to 40 and retain six slots for the initial balance iteration. |
| `data/units.json` | Twelve `alpha` and twelve `expansion` production records; canonical `role` is already present | Promote the twelve existing expansion records when adopted; preserve original full names as lore names and stable IDs; implement approved skill revisions through canonical data. |
| `data/traits.json` | Twelve design traits; ten enabled; existing tier values for two/four | Enable Halfling and Dragonkin; select highest eligible tier, replacing the lower tier. |
| `data/schemas/*.schema.json` | Closed rule objects and fixed property expectations | Version the changed contracts and validate new fields; reject unsupported definitions instead of silently ignoring them. |
| `tools/validate_kit.py` | Asserts twelve selected IDs, four races × three, six classes × two and threshold two only | Update those assertions to 24, six × four, six × four and reachable two/four. Preserve older fixtures as explicitly labeled old-profile tests only if still needed. |
| `tools/compile_catalog.py`, `tools/build_documents.py` | Generate selected Alpha rows and all-24 design rows/dossiers; asset anthology name says twelve | Keep one selected playable catalog; regenerate derivatives and rename/document the asset anthology coherently. Do not manually copy Design24 rows into runtime. |
| `tools/unreal/sync_runtime_data.py` | Stages canonical JSON, generated Alpha rows and a hash manifest | Include neutral definitions and waves in staging/digest verification; preserve byte equality checks. |
| `game/Source/WonderChessRuntime/Public/Simulation/WonderSimulation.h` | `TraitDef` has one threshold/value; `Encounter` assumes two seat indices | Add tier-aware trait representation and explicit encounter ownership/kind. Neutral definitions must not become recruitable heroes. |
| `game/Source/WonderChessRuntime/Private/WCDefinitionRegistry.cpp` | Requires 24 designs/12 active, ten traits, only tier two; rejects the two expansion trait statistics | Load 24 playable heroes, twelve traits and both eligible tiers. Expand supported stats deliberately. Its embedded catalog tests also assert twelve/ten. |
| `game/Source/WonderChessRuntime/Private/Simulation/WonderSimulation.cpp` | `Catalog::Validate` requires twelve; combat already supports flat magic resistance but not Halfling movement bonus | Validate the new catalog and derived bounds; add effective ordinary movement speed; preserve integer fixed-tick resolution. |
| `game/Source/WonderChessRuntime/Private/Simulation/WonderTournament.cpp` | `Prepare()` always calls `Pair()`; `Lock()` clones two seat rosters; `Settle()` indexes both sides as seats | Build PvE encounters per surviving seat, preserve PvP history across them, and settle neutral results once. |
| `game/Source/WonderChessRuntime/Private/WCMatchRuntime.cpp` | Serializes seat pairings and reconstructs damage display from existing round stages | Serialize encounter kind and nullable competitor ownership; transmit the authoritative result breakdown instead of reimplementing settlement in UI. |
| `game/Source/WonderChessRuntime/Private/WCMatchHUD.cpp`, `Private/WCBoardPresenter.cpp` | HUD and presentation expect playable definitions, opponent seats and single-tier traits | Support monster labels, public encounter selection, final neutral recap and higher-tier previews without indexing an invalid seat. |
| `tests/runtime/generate_catalog_fixture.py`, `runtime_tests.cpp`, `trait_combat_tests.cpp`, `targeted_combat_tests.cpp` | Generated C++ fixture and tests retain twelve/tier-two assumptions | Generate the real new catalog and extend meaningful runtime tests, including neutral encounters, all skills and active tier four. |

The existing six-person deployment cap is separate from the recruitable roster count. Keeping it at six allows four-member commitments plus two complementary heroes. Increasing to ten would also change formations, progression, UI, simulation bounds and performance; it is not implied by selecting 24 heroes.

## 2. Round schedule and tournament semantics

Use one visible round counter starting at one. For round `r`, a neutral round is `r <= 3 || r % 5 == 0`; every other valid round is PvP. The schedule is canonical data with a deterministic resolver, not repeated conditions in widgets, bots and network code.

The proposed update cap is **40 rounds**, explicitly replacing the old 24-round cap when adopted. Its eleven neutral rounds are **1, 2, 3, 5, 10, 15, 20, 25, 30, 35 and 40**; the other 29 rounds are PvP. Preserve the old 24-round schedule as a labeled regression fixture if useful, not the update default. The resolver classifies all positive integers correctly; the match cap determines which rounds are played. Forty rounds is a testable starting cap, not a promise of a 40-minute match or of reaching round 40 before elimination.

Maintain `pvpRoundIndex` as well as the visible round. Advance it only when a PvP preparation is created. Apply the existing loss-stage base 2/4/6 to PvP indices 1–6/7–12/13 onward, with the upper range explicitly covering the chosen cap. This gives the first competitive fights the intended early damage even though they begin at visible round four. Publish both fields in logs; the player only needs the visible round and actual damage explanation.

### Encounter ownership

At a neutral round, create one independent encounter for each living competitor: their battle-copy deployment versus the same authored wave. With eight survivors this means **eight simultaneous real combats**, not the four used in an eight-seat PvP round. This is a new worst-case workload that must be profiled.

Represent each encounter with an explicit kind (`pvp`, `ghost`, `neutral`), stable encounter ID, side descriptors, and an optional seat owner for each side. A neutral side has a wave ID and no seat owner. Do not insert a ninth seat, overload the ghost flag, fabricate a bot economy or use a negative seat index that later reaches an array access.

The neutral side receives battle-only instances with IDs namespaced by match, round, encounter and side. It has no shop, gold, XP, bench, placement or player-health total. It cannot be recruited, sold, merged, possessed by a controller or counted toward hero traits. Reuse the real combat primitives and rules for attacks, movement, skills, interruption, shields and defeat. Permit an explicit absent active skill for basic-only creatures; do not simulate one with an enormous hidden cooldown or a no-op fake ability.

All seats face identical wave definitions, formation and starting values that round. Use the same authored local-board orientation for every player. Neutral battle copies are isolated: damage or death in one encounter cannot mutate another wave. Seed separate combat randomness deterministically, with mirror-swap checks to expose initiative bias. Rendering and camera selection cannot alter any combat seed or tick.

### Pairing history across monster rounds

Keep the existing even-seat matching policy and odd-seat ghost policy on PvP rounds. A neutral round creates no PvP pairings and must not update meeting counts, previous PvP pairs, ghost counts or previous ghost recipient. For example, round six compares immediate rematches against round four, not an empty history from round five. Ghost fairness is measured by PvP opportunities, not calendar-round gaps.

Reveal the neutral wave at preparation start. Reveal the next actual PvP pairing only when its preparation starts, using the then-living seats. The wave preview is public and equally available to bots. Public deployments remain scoutable; shops, reserve benches and gold retain v3 privacy. Do not copy the reference client's wider information exposure accidentally.

Each living real seat must receive exactly one health-affecting result per round. A PvP ghost donor continues to receive only its real encounter result. A neutral outcome affects its one real owner and no other seat. Build all pending outcomes before applying any eliminations.

### Clocks and scene transitions

Retain authoritative preparation, combat, settlement and finish phases. Initial preparation remains 45 seconds; later preparation 25 seconds; combat timeout 40 seconds; settlement four seconds. Entry cinematics and lobby travel belong before the first preparation clock starts. They must not consume the player's buying time, as occurred with intrusive introductory overlays in the reference.

Preparation ends early only after all eligible humans and bots are ready and accepted commands are drained. During 0H8B regression, fast-forward preparation through the same completed policy budget; do not skip monster combat. Settlement waits for every actual encounter or the timeout. A finished fight may immediately switch to another ongoing fight, including another neutral fight.

Offline pause freezes all eight seats and the authoritative clock. Network options cannot pause the server. A cosmetic camera fly-through is skippable, bounded and independent of match logic. Restart resets PvP index, neutral previews, pending rewards, command caches, seeds, encounters and presenters.

## 3. Neutral outcomes, economy and reward lifecycle

The following is a small, explicit starting proposal that introduces no items:

| Outcome | Captain health | Additional next-preparation reward | Competitive wins |
|---|---:|---:|---:|
| Neutral win, rounds 1–3 | No loss | +2 gold | No increment |
| Neutral loss/draw, rounds 1–3 | No loss | None | No increment |
| Neutral win, later rounds | No loss | +2 gold | No increment |
| Neutral loss/draw, later rounds | 2 damage | None | No increment |
| PvP win, including ghost recipient | Existing winner policy | Existing +1 victory gold | Increment once |
| PvP loss/draw | Existing PvP-index stage formula/draw rule | No victory bonus | No increment |

Every surviving seat that enters another preparation receives normal base income (5), snapshotted interest and passive XP (2), once. Neutral +2 gold replaces the PvP victory bonus for that outcome; it is not +2 and +1. There is **no extra XP bonus** in the starting proposal. Retaining passive XP on all rounds preserves existing leveling cadence while combat pacing is evaluated.

Store a pending reward entitlement inside the immutable settlement record. After outcome application, elimination and tournament-end checks, eligible survivors receive it on entering the next preparation, along with ordinary income. Then resolve XP and refresh an unlocked shop. A finished or eliminated seat receives no phantom post-match income/XP. A result screen can show an earned reward as not applied because the tournament ended; do not silently add unusable currency after finish.

Neutral rewards never alter PvP `wins`, ranking tiebreaks, ghost exposure or win-streak statistics. Track `neutralWins`, `neutralLosses` and `neutralDraws` separately for observation. A draw is resolved using the same actual combat timeout/empty-team semantics and earns no reward. Opening failure is survivable, not an automatic win: retain the failed encounter and explain the missed bonus.

Retain v3 simultaneous-elimination ranking: raw post-damage health, then cumulative **PvP** wins, shared competition placements for exact ties. Neutral fixed damage can still cause simultaneous late eliminations, including zero survivors; process that without hanging. One remaining seat ends the tournament immediately; do not require it to defeat the next scheduled wave. At the cap, preserve health/PvP-win adjudication and label it clearly. If a future cap lands on a neutral round, settle that round and then adjudicate.

Gold reward particles or brief banners are optional visual acknowledgments of a server entitlement. They do not create clickable inventory objects or depend on a courier touching them. One settlement ID grants at most one reward; repeated callbacks, delayed packets or reopening the recap cannot grant it twice. On restart all reward visuals and entitlement state belong to the old match and are discarded. No world drop becomes a sellable roster item.

## 4. Monster content contract

Add dedicated canonical neutral content, proposed as `data/neutrals.json`, with a matching schema. It contains creature definitions and complete waves. It joins the content digest and staged runtime manifest. Creature IDs use a distinct namespace; recruitable `alpha_unit_ids` remains exactly the 24 heroes.

Each creature has an original display name, model/animation/audio identifiers, combat stats in the existing numerical units, optional supported skill, and an explicit one-cell footprint. Each wave declares its ID, eligible rounds, named creature IDs, legal cells, fixed star/scale values and reward policy. Do not derive opponent strength secretly from a human roster score. Bots and humans encounter the same declared wave; all scaling is profile data.

[MONSTER_WAVES.md](MONSTER_WAVES.md) is the sole proposed authority for creature identities, initial statistics, skill selectors, wave formations and scale factors. It defines seven original archetypes and eleven waves through round 40. Do not maintain an alternative composition table in systems or UI code. Before integration, the canonical-data owner migrates these proposals into schema-backed source, validates supported capabilities and executes low-, nominal- and high-investment test formations. These remain uncalibrated inputs.

No boss uses a new damage/effect mechanic merely because its animation suggests one. Initial creature skills use the approved combat primitives. If a wave needs a new selector or composite effect, define it, test it and expose it in inspection before that wave can ship. Neutral creatures need their own finished assets and continuous animation review; a primitive labeled “monster” is an internal checkpoint only.

## 5. Synergies that the 24-hero roster can actually support

Activate tiers **2 and 4** for all six races and six classes. Four distinct members is reachable for every trait in the full authored roster. The active value is the highest reached tier and replaces the lower value; never add tier-two and tier-four values together. Count only distinct deployed hero-definition IDs, excluding bench copies, stars, neutral creatures and repeated instances. Snapshot before combat; deaths do not remove an already initialized bonus.

Retain the existing authored starting values while upgrading implementation and presentation:

| Trait | Two members | Four members | Recipients |
|---|---|---|---|
| Human | +10% maximum health | +20% maximum health | Humans |
| Elf | +10% ordinary attack rate | +20% ordinary attack rate | Elves |
| Dwarf | +10 physical armor | +20 physical armor | Dwarves |
| Orc | +10% direct damage | +20% direct damage | Orcs |
| Halfling | +10% ordinary movement rate | +20% ordinary movement rate | Halflings |
| Dragonkin | +15 magic resistance | +30 magic resistance | Dragonkin |
| Guardian | +15 physical armor | +30 physical armor | Guardians |
| Warrior | +15% basic damage | +30% basic damage | Warriors |
| Ranger | +15% basic damage | +30% basic damage | Rangers |
| Rogue | +15% ordinary attack rate | +30% ordinary attack rate | Rogues |
| Mage | +20% active damage | +40% active damage | Mages |
| Priest | +15% positive active support magnitude | +30% positive active support magnitude | Priests |

Both membership explanations and numerical recipient highlights are required. A hero can complete a trait without receiving another class's effect. In the shop and placement preview show changes such as “Human 1 → 2: Ada and Mira gain +10% health” and “Mage 3 → 4: +20% becomes +40%.” Include contributors already deployed and affordable future partners; make bench suggestions visibly inactive. The hero gallery shows all reachable tiers and exact eligible recipients.

Use one tier resolver in authoritative combat, inspection, preview and bot evaluation. Do not make a UI-only four-member tier. Add an ordinary movement bonus field to battle state. Compute effective movement milli-rate from canonical base and additive applicable bonuses with half-up rounding, then quantize step duration to ticks; validate the resulting positive rate and bounded interval. It changes neither dash distance nor attack/cast cadence. Dragonkin modifies magic resistance only, with the same defense formula; the new loader must permit and validate it.

Map canonical `role` descriptions to the player-facing vocabulary in HERO_UPGRADE_BRIEFS: Tank, Melee, Ranged, Caster, Support, Healer and Control. This improves filters, recommendations, deployment previews and bot team evaluation. Race and class remain the two bonus systems. Do not create an undocumented third “role synergy,” rename class IDs casually, or let a cosmetic stance change a class.

**Required skill/trait coherence revision:** Neris is an authored Mage with pure-stun Starbind. The existing Mage active-damage bonus does not affect her stun. The proposed hero update changes it to an explicitly authored damage-plus-control skill: migrate the single-effect schema to a bounded ordered effect list, with exact magnitudes, order and interruption behavior set by the hero plan. The Mage bonus amplifies only its declared damage; it must not scale stun duration or invent a cooldown benefit. Validate the approved hero plan and generated tooltip together. Review all 24 heroes for the same ability/trait mismatch, including support amplification, basic-versus-active distinction and dash-only skills.

## 6. Visual equipment and skill boundaries

Weapons, shields, instruments, bags, focus objects and armor are authored appearance assets tied to their hero definition. Star accents may add restrained ornament while preserving identity, footprint and hit rules. Gallery equipment descriptions explain the gear and its visual function; they are not stat modifiers, loadout slots or tradable objects.

A sword's length cannot extend canonical range, a large shield cannot expand collision, wings cannot imply flight, and a heavier star costume cannot slow movement. Idle, attack, cast, hit, defeat, victory and locomotion clips follow actual events. A gallery skill demonstration uses the same capability/evaluator in an isolated labeled preview encounter, not fake combat numbers or code that mutates a running tournament.

Keep explicit star magnitudes, integer centipoints, basis points and 50 ms timing. Never apply the health/basic star multiplier again to already authored skill magnitudes. If improving skills requires ordered multiple effects, replace the single-effect representation through a versioned migration, preserving target snapshots, action IDs, release/impact ordering, source-death handling and data-generated tooltips. Multi-effect support is not permission to add summons, transformation, inventory, revival or hidden basic-hit procs.

## 7. Persistent bots, network privacy and fairness

The seven personas retain their existing roster/economy across both round types. They use the same buy/sell/XP/move/ready commands and budgets as before. With 24 offers in the pool, retune candidate scoring and test upgrade availability; merely loading more heroes changes expected duplicate acquisition. Keep independent draws and three price tiers unless later evidence justifies another separately specified economy migration.

Extend bot formation scoring to highest eligible trait tier and to useful progress toward tier four. The current feature increments once per flat trait record; storing each tier as a separate additive record would overcount completed traits. Score the actual post-action formation, include class/role coverage and avoid sacrificing all defenses to chase a fourth member. Log feature values and accepted/rejected commands.

Before a monster round a bot may inspect the same public wave preview a human sees and use bounded formation candidates against it. It cannot see hidden rolls, future rewards or unshared player state. No outcome shortcut is permitted: scoring is only a policy heuristic, while every encounter advances real combat. Bot takeover after client disconnect preserves all holdings and current entitlement state through either round kind.

Use an explicit network protocol/profile version and content digest. Host/client must agree on the 24 stable IDs, neutral data and revised skill/trait contracts before entering the match. Refuse a mismatched old client with a clear reason. Public snapshots identify round kind, wave, allowed deployment and current combat; only the owner receives shop, bench, gold and private commands. A monster is never a human seat and never receives a replication owner.

Execution amendment: protocol **5** adds the acknowledged request ID to `ClientReply`. Only the matching pending command can resolve selection or queued command state; a rejected placement/sale retains a still-owned selection for correction. Session notices use request ID zero. This changes the wire contract from the retained protocol-4 integrated slice, so its content digest and readiness handshake must reject mixed packages. Gameplay numbers remain balance `alpha_24_v0.4.1`; protocol evidence and earlier package results retain their own identities.

Presentation amendment: protocol **6** retains the request-correlated reply contract and adds `basicAttackOrdinal` to each public combat-unit snapshot. It starts at zero in a newly constructed combat and increments exactly once when that unit commits a basic attack. Casts, recovery, damage delivery and observer changes do not increment it. The value selects a validated presentation window in the same Attack animation for authored alternating strikes, including after scouting or skipped snapshots. It never changes targeting, RNG, scheduling, effects, damage, economy or outcomes. Each committed basic still has its original single release. Both peers must use protocol 6 and the same content digest; retained protocol-5 package evidence remains attached to its original payload. Current numerical balance remains `alpha_24_v0.4.1`.

Window metadata belongs to the authored export manifest and cooked animation sync markers, not combat balance. Each named window declares start, release and end; its release offset must equal the hero's canonical basic windup. Runtime clamps playback within the selected window and preserves that selection across windup and recovery for the same action. Gallery review plays the complete asset so all authored variants can be inspected. Cold and packaged tests must verify marker persistence, per-unit alternation, interruption and unchanged actual combat results.

Continue required modes **1H7B**, **0H8B** and **2H6B**. For 2H6B, use actual separate processes and a local-network run; same-machine loopback remains a useful preliminary check with that exact label. Verify host-abort and non-host takeover during neutral preparation, neutral combat and normal PvP. Preserve no-rejoin/no-host-migration boundaries unless explicitly changed later.

## 8. Implementation checkpoints and acceptance evidence

1. **Baseline and migration tests.** Record current source revision and data digest; run `python tools/validate_kit.py`, `python -m unittest discover -s tests -v`, `python tools/build_documents.py --check` and `python tools/compile_catalog.py --check`. Preserve existing failures as baseline evidence. Assign one owner for canonical sources, schemas and generated outputs. Commit the adopted narrative/schema changes with tests before importing 24 production assets.
2. **Twenty-four definitions and traits.** Generate/stage the selected roster and all twelve traits. Update `tests/runtime/generate_catalog_fixture.py`, build and run via `tests/runtime/build_and_run.ps1`, and extend `tests/runtime/run_trait_combat.ps1`. Test 0/1/2/3/4 distinct members, duplicate/bench exclusion, tier replacement, additive cross-trait effects, recipient restrictions, ordinary movement timing and magic resistance. Inspect every hero at stars one/two/three against the canonical evaluator. New capability tests execute the actual C++ combat engine.
3. **Neutral schedule and settlement.** Test schedule boundaries 1–6, 9–11, 14–16, 19–21, 24–26, 29–31, 34–36 and 39–41, invalid zero/negative rounds, the old cap24 fixture and cap40 update profile. Run eight independent neutral combats with isolated IDs/health. Verify all seats receive one result, opening failures do not damage captain health, later failures do, and reward/XP/interest/refresh occur once in documented order. Test duplicate settlement callbacks, no next round, simultaneous elimination, zero survivors and round40 neutral settlement followed by cap adjudication.
4. **Pairing and observation continuity.** Verify round-four to round-six rematch history, preserved ghost exposure through round five, odd active counts, donor invariance, early finished fight spectating, neutral preview ownership and restart cleanup. Test an empty deployment without special-casing it into a free win.
5. **Real integration.** Compile the revised Unreal loader, native module and packaged game. Verify staged data digest, invalid-data rejection, all24 definitions, trait text matching mechanics, monster presentation, skill events and lobby-to-first-preparation clock behavior. Extend the existing Unreal catalog/network/asset tests rather than claiming generated fixtures prove editor import.
6. **Complete matches and measurements.** Run at least 100 completed actual-combat 0H8B tournaments for the new profile; then complete packaged 1H7B and actual 2H6B checks. Report seeds, revision/digest, failures, cap frequency, neutral win rate by round, health/economy curves, trait/hero use, upgrades, rejected bot actions, control uptime, encounter timeouts, match length and every visible/hidden combat's result. Name hardware and measure frame-time percentiles during eight concurrent neutral encounters as well as PvP, lobby and gallery. A high neutral win rate alone does not prove balance or enjoyment.

Protect retained evidence: several existing wrappers write fixed report directories. Inspect arguments first and supply a fresh task-scoped destination, or add a tested output-directory parameter before rerunning. Never overwrite old candidate evidence. Use existing runners and readers in `tests/runtime/` where applicable: `run_packaged_regression.ps1`, `audit_packaged_regression.py`, `run_shipping_solo.ps1`, `run_shipping_network_routed.ps1`, `run_shipping_disconnect.ps1`, `audit_shipping_network.py` and `summarize_frame_evidence.py`. Inspect their real parameters and assumptions before changing or running them; a filename is not proof that a scenario is covered.

Final evidence must include the executable path/launch instructions actually produced, source/data revision, hero and neutral asset coverage, continuous animation and gallery reviews, real human/bot mode evidence, measured hardware/performance, and passed/failed/not-run checks. Keep old candidate evidence attached to its original digest; a planning file, passing Python fixture or old packaged match cannot certify this update.

## 9. Planning validation status

This proposal was prepared by reading the existing rules, roster, trait and bot data, generator/loader code, authoritative combat/tournament code, replication/HUD integration and relevant runtime test sources. No gameplay implementation, data promotion, build, match, balancing experiment or asset import was performed as part of this file. Round rewards, pacing and wave difficulty remain explicitly proposed values for implementation and measurement.

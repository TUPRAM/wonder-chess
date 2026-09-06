# Eight-seat tournament and bot contract

## 1. Persistent competitors, independent encounters

Create eight stable seat IDs at lobby start. Each seat owns health, gold, XP, level, shop offers, roster instances, bench locations, preparation formation, round results, placement and a controller binding. Human and bot bindings submit the same command types. A bot is not an enemy-wave generator. Do not rebuild its roster from an arbitrary difficulty score every round.

At eight active seats, PvP rounds run four pairwise encounters, each with up to twelve deployed combatants. Monster rounds 1–3 and every positive multiple of five run eight isolated real encounters, one per living seat, against the same public authored wave. Neutral sides have explicit wave ownership and no tournament seat/economy. Preserve PvP pairing and ghost history through monster rounds. Each side receives a battle copy of its owned deployment with trait-derived maximum health initialized, timers reset and no inherited combat wounds. After settlement, restore the persistent roster/positions rather than copying combat movement back into the bench or preparation formation.

Simulate every encounter with the actual combat engine. Team-power evaluation may help a bot choose actions, but cannot determine off-screen wins. Render only the inspected encounter where practical. Visibility, animation and sound must not consume combat random numbers or advance state.

## 2. Pairing

Reveal pairings at preparation start and freeze them for the round. For even active counts, enumerate perfect matchings (only 105 at eight seats) and minimize a lexicographic cost: number of immediate rematches, total historical meetings, seeded tie-break. Normalize pair IDs and use a specified portable seed/hash or PRNG rather than a language-dependent hash map. The reference pairing code demonstrates the policy; port it or prove an equivalent implementation.

For odd active counts at least three, choose one ghost recipient. Minimize prior ghost assignments first, then whether the seat was the previous ghost recipient, then seeded tie-break. A lower assignment count takes priority over the consecutive-assignment preference; document that rare conflict rather than promising impossible guarantees. Choose an active donor other than recipient with low recent/history repetition, then pair remaining real seats normally.

The ghost’s identity and recipient are revealed at preparation start. Its formation is copied from the donor at the common preparation lock. It does not own gold, shop, bench, permanent items or a separate competitor. Ghost clone instance IDs are namespaced by encounter so they cannot collide with real roster IDs.

The donor participates in its real encounter and is unaffected by the ghost fight. Only recipient health, fight wins and normal recipient-side reward change. One health-affecting outcome per real seat per round is an invariant. Ghost wins count as normal fight wins for the cap tiebreak in this alpha; log ghost exposure and outcome bias. Do not claim this policy is competitively proven.

## 3. Ready and phase boundaries

In offline mode the human may ready early. Bots plan under bounded budgets; begin combat early only after every active seat is ready and accepted commands are drained. In 0H8B tests fast-forward preparation only after policies finish their turn budget. In network mode all active human seats must ready, or timer expires. Any successful preparation edit after ready clears that seat’s ready flag.

At lock: reject later preparation commands, snapshot interest balances, lock public formation and trait lists, clone battle units, capture ghost donor, and initialize encounter states. Frame ordering cannot allow a late remote buy while a local buy is rejected at the same accepted sequence position. Use authoritative phase/revision checks; client timestamps do not grant permission.

Settlement waits until all encounters finish or reach hard timeout, not until the human’s fight ends. A player whose battle finishes early can watch another live encounter. Do not double-advance the round because multiple completion delegates fire.

## 4. Results and placement

A non-draw loser takes stage base (2 in PvP indices 1–6, 4 in 7–12, 6 in 13 onward) plus the count of surviving enemy units. Ignore star in player damage. A draw gives both real participants two damage; in a ghost draw only the recipient takes it. The donor never receives a second result. Winner loses no health. Empty versus empty draws immediately; empty versus nonempty is an ordinary loss with survivors counted.

Timeout compares the exact sum of each survivor’s current/max health fraction, ignoring shields. Larger sum wins; equal score draws. The score weights living units rather than raw health. This is a provisional choice to test, not a claim of ideal competitive fairness. Use rational/integer comparison carefully; overflow must be bounded or use an audited wider representation.

Compute all health changes into one pending settlement, including negative raw health. Rank newly eliminated seats by higher raw post-damage health, then higher cumulative fight wins; ties share placement. Start their placement at surviving count plus one. Use competition ranks (for example 5,5,7), never silently use seat ID to choose a winner. Persist earlier-round placements; a later survivor outranks already eliminated seats.

If one active seat remains, it takes first. If zero remain after simultaneous settlement, the tied final group can share first under the same elimination keys; do not hang waiting for a survivor. At the adopted initial cap of round 40, settle the neutral round and all eliminations first; remaining seats rank by positive health then wins with exact ties shared. Label this result capped adjudication, not a final combat win. After finish, no income, passive XP or shop reroll occurs.

Record settlement ID and apply once. Retries or duplicate encounter callbacks return the existing settlement result. Save pre/post hashes for debugging. Restart creates fresh seat IDs or a fresh match namespace, RNG streams, command caches, subscriptions, camera state and UI selections; no lingering actors or persistent buffs.

## 5. Bot information and fairness

Each bot sees its own private economy and the same public deployment, health, level, traits, opponents and standings a human can inspect. It never reads opponent shop/bench/gold, future RNG draws, private commands, human cursor intent or unrestricted authoritative state. Public observations are sampled at 1500 ms. No newly reactionary repositioning during the last 3000 ms; finish only the already planned legal sequence. Human public displays can refresh faster; bot limitations make reactive behavior legible rather than perfect.

Difficulty varies candidate breadth, utility quality and bounded noise, not hidden stats, free gold or fabricated offers. Seven personas live in `data/bots.json`; all use one evaluator. Labels clearly include “Bot.” Runtime calls to LLMs or external AI endpoints are forbidden in this offline-capable alpha.

Bot thought logs are structured, not imagined private reasoning: observation revision, candidate feature values, scores, selected legal action, command response and balance after action. They may aid debugging but do not expose other players’ private data to clients.

## 6. Decision procedure

Every 700 ms in preparation, or in equivalent discrete fast-forward test steps:

1. Read permitted state and verify the current phase. Stop at command budget or ready. Reuse legal cached observations; do not scan hidden state.
2. Repair deployment: fill available slots from owned units, retain a sensible frontline, clear illegal cached plans after a reject.
3. Generate bounded candidates: buy each affordable offer; buy XP; reroll; sell demonstrably replaceable bench units; relocate/swap; hold. Enumerate complete merge consequences before assessing bench capacity.
4. Score post-action formations, not just individual hero cost. Consider upgrade completion, useful pair retention, attainable traits, basic damage mix, at least one frontline body and at least one damage source.
5. Subtract opportunity cost: gold spent versus next level, interest band lost, bench crowding and duplicate redundancy. A unit with higher raw DPS is not automatically better than required protection.
6. Execute the highest positive legal improvement. Hold/ready when further improvements are too small or unaffordable. Do not reroll until bankrupt merely because reroll is always legal.

### Initial feature definitions

Use normalized features in [-1,1] before persona weights. Start with: change in deployable fixed-star stat budget / expected team budget; increase in completed upgrade copies / 9; change in actual highest-tier active traits / 6; capped useful duplicate progress / 6; frontline coverage improvement (zero-to-one frontline is more valuable than third-to-fourth); ranged/spell/support balance; and match-health urgency. Keep raw stat budget separate from outcome claims.

A proposed score is `3*deployment_gain + 2*upgrade_gain + 1.5*trait_gain + 1*role_coverage + 0.6*useful_pair_gain - 1.0*gold_fraction_spent - 0.8*interest_loss - 0.6*bench_pressure`, then apply the corresponding persona weights and bounded seed noise. The exact coefficients are tunable prototype values. Normalize each term and log it; do not mix health points, percentage values and gold directly into an arbitrary sum.

At low health (15 or less), increase immediate-team weight and reduce saving weight. Savings target otherwise may be 10/20/30 according to level/health, not a mandatory permanent bank. Maximum forty commands and four paid rerolls per preparation prevent policy loops; report frequent limit hits. Bot budget caps do not grant more resources or reduce shop costs.

Formation heuristic: Guardians near the front, Warriors slightly to the side, Rangers/Mages behind protection, Priests within their real support pattern and Rogues positioned for their authored targeting. Preserve legal retreat space for Liora; do not cluster every ranged unit automatically. Evaluate a small number of swaps against the revealed opponent’s sampled public formation. No unrestricted full-tree search against future draws.

The WC-U450 purchase evaluator also accounts for authored active skills. It estimates potential over a bounded twenty-second horizon (or the shorter combat timeout), using actual first-release delay, cooldown, explicit star effect values and cast/recovery occupation. Area recipients are capped at three and current deployment capacity, not assumed to hit an entire enemy team. Heal/shield potential receives a 0.6 usefulness factor; all potential receives a 0.75 delivery factor, then basic attacks occupied by casting are subtracted. Control/tempo potential uses the evaluated hero's basic-damage rate and authored duration; dash potential is bounded to half a second of basic damage. Disabled skills and first releases beyond the horizon add no value. These visible-data heuristics are purchase/formation preferences only; they never determine battle winners. They require measured usage and encounter outcomes before claiming improved balance. The previous health/basic-only evaluator systematically undervalued casters in the early 100-tournament run.

## 7. Network path and disconnects

Separate `SeatState` from `HumanCommandSource` and `BotCommandSource`. A server-side authority validates all requests. Public state and owner-private state must use distinct replication routes. The server owns complete combat snapshots; clients receive allowed state and presentation events.

For the 2H6B alpha test, a disconnected non-host human becomes a bot for the rest of that match. Preserve all resources and roster; show a takeover label. Rejoining that seat is not supported in the alpha and must be rejected clearly. Host disconnect aborts the match with no winner; no host migration is claimed. A later dedicated-server/rejoin design is separate.

One process running eight bot policies is not a human network test. Final 2H6B acceptance requires two physical LAN machines; two processes on one PC are explicitly preliminary evidence. Required 2H6B evidence includes distinct processes, accepted/rejected commands, phase locking, simulated latency/loss where tooling permits, owner-private information inspection and host/client disconnect paths.

## 8. Regression scenarios

Test 8,7,6,5,4,3,2 active seats; no self-pair; every real seat exactly once; donor unaffected by clone; deterministic pairing replay; repeat minimization; ghost assignment history; ties; simultaneous multiple eliminations; zero survivors; cap; empty formations; winner dies to an already released projectile; restart; early human elimination and continued bot tournament.

The supplied Python tests exercise pairing/settlement with synthetic provided outcomes. They explicitly do not satisfy the required 100 actual engine combat tournaments. During engine tests capture composition, gold curves, placement distribution, ghost exposure, timeout rate, bot rejects, action counts, battlefield idle time and match duration. Human playtests remain necessary for enjoyment and clarity.

## Adopted neutral settlement and entry

Keep absolute round and PvP-round index separate. A neutral victory does not increment competitive wins; record neutral wins/losses/draws separately. Opening neutral failures cause zero captain damage; later failures/draws cause two. After once-only outcome application, simultaneous elimination and finish/cap checks, eligible survivors entering the next preparation receive normal base income, locked interest and passive XP once, plus neutral win income of two instead of the PvP win bonus of one. Final/eliminated seats receive no next-round income. There is no item reward or manual pickup. Restart clears indices, neutral copies and pending rewards.

Graphical lobby/loading/readiness and the skippable bounded introduction precede the first preparation clock. A slow LAN client cannot begin buying early or stop the server indefinitely. Cancellation before commitment returns to setup and clears the pending session. The systems migration specification owns detailed edge cases and required tests.

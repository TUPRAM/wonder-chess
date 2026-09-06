# Auto Chess — complete reference playthrough

**Completed: 1st place of eight, round 42, 90 HP.** The final standings display **38–4 W-L**. The actual game was **standalone Auto Chess through Epic**, in **Casual (Solo)**. The user originally requested Dota Auto Chess; the opened client was identified and that difference disclosed. These are not Dota 2 workshop captures.

Observed match interval: **6 September 2026, 19:12:11–20:00:51 Singapore time**, or 11:12:11.613–12:00:51.549 UTC: approximately **48 minutes 40 seconds**. This is wall time between first observed round-one preparation and final elimination, including gaps, not the internal game timer. The game was returned to its Casual lobby after exactly one match.

The archive contains **93 original screenshots**. [Full gallery](gallery.md) · [Observation CSV](observations.csv) · [Session record](session.json) · [Image provenance index](screenshots/index.jsonl) · [Archive verification](verification.json).

This was a **shared, assisted session**, not a benchmark of independent agent skill. Auto Deploy and Auto Star Up were already enabled. User input was detected in the opening and late match. Several upgrades and equipment changes occurred outside observed agent actions. Rounds 33–36 and round 39 were not directly observed. Those gaps remain gaps.

![Verified first-place banner after the final opponent was eliminated.](screenshots/raw/SHOT-087_20260906T120058040Z_first-place-tournament-result-banner.jpg)

*SHOT-087 — Verified first-place banner after the final opponent was eliminated.*

## Match account and evidence

| Stage | What was verified | Boundary |
|---|---|---|
| Opening, rounds 1–7 | Casual Solo selection, eight-seat start, unit inspection, God of War and XP purchases, two-star Redaxe Chief, three-Warrior threshold, first captured loss from 100 to 95 HP. SHOT-003–021; OBS-002–006. | Opening purchase/deployment attribution is mixed. |
| Middle, rounds 11–20 | Board expansion, shop odds and income inspection, owned-piece discount, item choices and scouting. W replaced a duplicate with Grand Herald: Divinity one became two. Fire Spirit was later verified deployed. SHOT-026–052; OBS-007–009. | Early drags did not verify placement or equipment. |
| Composition, rounds 23–30 | Duplicate Light Spirits did not increase Mage beyond two; replacing one with The Source produced Mage three. Sold an unused reserve, completed Swordman two-star, observed eliminations and healing, bought XP toward level ten. SHOT-054–074; OBS-010–017. | No claim that this composition or economy route is optimal. |
| Gaps and final two | Last observed round 32 was followed by round 37 with more upgrades and four seats. Round38 had two; round 40 showed level 11, 93 HP versus 10 HP. SHOT-075–079; OBS-018–019. | Rounds33–36,39, level 11 acquisition and several upgrades unobserved. |
| Closing, rounds 41–42 | Bought a free Stone Spirit completing two-star; verified on board. Lost round 41, 93 to89 HP. Equipment changed after detected user input. Won round 42, final opponent eliminated, ownHP90. SHOT-080–087; OBS-020–024. | No isolated causal attribution to equipment or one upgrade. |
| Results and exit | Inspected hero showcase and all-eight-seat Deploy, Synergy and Relic tabs; returned to lobby. SHOT-088–093; OBS-025. | Gold column549 has unexplained aggregation; it is not described as remaining gold. |

The formation broadly developed into an armored frontline with magic support behind it. Distinct Spirit and Mage members were actionable decision targets because their counters visibly changed. The last opponent still won round 41 despite our large health lead: tournament HP did not guarantee winning the next encounter.

Click-then-W successfully deployed/withdrew pieces. E successfully sold a reserve. Direct shop clicks and XP purchases produced verified changes. Several attempts crossed preparation deadlines or shop refreshes. Drag calls never established successful equip or movement. A round-nine loading transition recovered into the same match; its cause is unknown.

## Heroes: shape and posture before small detail

The shop presents full-body animated models on rarity-colored bases, with traits, cost and upgrade hints nearby. Broad torsos, compact bodies, mounts, floating forms and long weapons create useful differences before reading names. Fire Spirit's warm trailing shapes contrast with rounder, cooler companions.

![Five distinct shop silhouettes with rarity colors, trait icons and odds.](screenshots/raw/SHOT-047_20260906T113043070Z_shop-five-distinct-hero-silhouettes-and-rarity-colors.jpg)

*SHOT-047 — Five distinct shop silhouettes with rarity colors, trait icons and odds.*

![A second sample emphasizes varied body mass, posture and weapon shape.](screenshots/raw/SHOT-064_20260906T114050050Z_shop-contrasting-body-masses-and-large-weapon-shapes.jpg)

*SHOT-064 — A second sample emphasizes varied body mass, posture and weapon shape.*

Swordman's close-up result pose shows an intentional face, asymmetric equipment and stance. At board distance the weapon and torso remain more readable than small costume details. There is also a retained failure case: tall/flying shop models are clipped at the top in SHOT-030. Shop framing should be reviewed through animation extremes.

![Featured hero close-up linked to the final eight-seat ranking.](screenshots/raw/SHOT-089_20260906T120212800Z_results-swordman-hero-showcase-and-eight-ranks.jpg)

*SHOT-089 — Featured hero close-up linked to the final eight-seat ranking.*

For Wonder Chess this supports the existing dossier-driven silhouettes and calibrated camera requirement. It does not relax Ada's costume, rig, animation, shield or source round-trip requirements. V3 requires restrained star accents and a stable footprint; the reference game's stronger visual transformations do not override that rule.

## Arena: rich perimeter, quiet playable surface

Four environments preserve the recognizable board structure while changing dressing. The beach uses pale slabs, shells and colorful vegetation. The courtyard uses cobbles and crates. Verdant ruins add greenery and leaf shadows. Dry ruins use warm stone and peripheral props.

| Sample | Visible strength | Question to test |
|---|---|---|
| Beach, SHOT-056/080 | Open, bright board; courier outside formation | Do pale effects lose contrast against the floor? |
| Stone courtyard, SHOT-041 | Strong boundary and material identity | Do cobble seams compete with feet and cell edges? |
| Verdant ruins, SHOT-044 | Rich foliage and directional shadows | Do high-contrast shadows compete with combat cues? |
| Dry ruins, SHOT-063 | Warm stone and props near edges | Are legal cells still the clearest spatial guide? |

![Stone courtyard with environmental props around a recognizable board.](screenshots/raw/SHOT-041_20260906T112823756Z_stone-courtyard-arena-crates-cobblestone-and-shadows.jpg)

*SHOT-041 — Stone courtyard with environmental props around a recognizable board.*

![Verdant ruins: leaf shadows also cross the playable surface.](screenshots/raw/SHOT-044_20260906T112939173Z_verdant-ruins-arena-leaf-shadows-and-stone-borders.jpg)

*SHOT-044 — Verdant ruins: leaf shadows also cross the playable surface.*

![Dry ruins offer another material and lighting reference.](screenshots/raw/SHOT-063_20260906T114037080Z_desert-ruins-arena-and-third-mage-battle-entry.jpg)

*SHOT-063 — Dry ruins offer another material and lighting reference.*

Wonder Chess needs **one coherent original courtyard**, not four new cosmetic arenas. Concentrate storytelling at its perimeter and test its floor under the actual authored hero palettes, rings, shields and attacks.

## Shop, bench and traits: show the consequence beside the choice

The most useful purchase cue was **Star up** on the exact completing offer. The owned-piece discount visibly produced zero-gold offers. Level-dependent rarity odds explained a consequence of buying XP. An offer prompt alone is not proof of a completed merge: the archive retains both prompts and verified results.

![Level-ten odds and a highlighted free completing offer.](screenshots/raw/SHOT-074_20260906T114557631Z_level-ten-odds-and-free-completing-upgrade.jpg)

*SHOT-074 — Level-ten odds and a highlighted free completing offer.*

![Verified Stone Spirit two-star result in round 41, after the reserve copy was consumed.](screenshots/raw/SHOT-080_20260906T115844298Z_verified-stone-spirit-two-stars-before-final-duel.jpg)

*SHOT-080 — Verified Stone Spirit two-star result in round 41, after the reserve copy was consumed.*

Trait summaries combine names, icons, thresholds and member counts. Some tooltip highlights include bench members, which is not the same as showing active bonus recipients. Two Light Spirits did not raise the Mage count above two; The Source replacement later activated three. Distinct-member counting needs an explanation at the decision point.

![Spirit membership highlights include reserves; membership and active recipients must be distinguished.](screenshots/raw/SHOT-053_20260906T113349884Z_four-spirit-tooltip-highlights-members-including-bench.jpg)

*SHOT-053 — Spirit membership highlights include reserves; membership and active recipients must be distinguished.*

Item choices contrast short numerical effects with long transformation descriptions. Text extended beyond the visible panel in some choices. NEW markers and recommendation thumbs helped locate items and suggested carriers. Late Swordman inspection showed five then six occupied slots and changed displayed stats, but the agent did not perform those changes.

![Six equipped slots, current stats, recommendations and inventory in one inspection view.](screenshots/raw/SHOT-084_20260906T120016607Z_swordman-six-equipped-items-and-inventory-comparison.jpg)

*SHOT-084 — Six equipped slots, current stats, recommendations and inventory in one inspection view.*

Talents, relics, item drafts and storefront systems are observations, not proposed Wonder Chess alpha additions. Its authored costs, race/class thresholds, roster and rules remain authoritative.

## Combat: spectacle needs readable priorities

Sampled fights show directional attacks, beams, rings, ink trails, walls, shields, health bars, stars and control-state words. Different shapes help distinguish line and area attacks. When several equally bright effects overlap, smaller bodies disappear and the spatial relationship becomes harder to read.

![Circular electricity and a bright beam overlap bodies and indicators.](screenshots/raw/SHOT-070_20260906T114324708Z_overlapping-lightning-ring-and-fire-beam.jpg)

*SHOT-070 — Circular electricity and a bright beam overlap bodies and indicators.*

![Walls, ice, lightning, beam, stun text and shields share one late-combat frame.](screenshots/raw/SHOT-079_20260906T115805629Z_round-forty-ice-wall-lightning-and-beam-overlap.jpg)

*SHOT-079 — Walls, ice, lightning, beam, stun text and shields share one late-combat frame.*

![Explicit Stun labels explain control effects while competing with units and numbers.](screenshots/raw/SHOT-085_20260906T120030533Z_simultaneous-stun-labels-and-impact-contrast.jpg)

*SHOT-085 — Explicit Stun labels explain control effects while competing with units and numbers.*

Team-colored health bars often remain the strongest locator. Stars and status icons occupy nearby space, making ordering and spacing important. Right-side statistics are useful only when their category is clear: green healing bars seen in some frames must not be described as damage.

Wonder Chess should test its actual twelve heroes while their dossier-defined skills overlap. Effects must not imply unsupported mechanics; the UI/audio contract specifically distinguishes an effect's appearance from whether the rules cause stun, damage over time or invulnerability. These stills do not establish animation smoothness, audio quality or performance.

## Scouting, elimination and results

A standings click opened another board; a Return control restored home. Cloud/camera transitions and persistent player identity helped retain context. This reference client showed the inspected bench. **Wonder Chess's contract is different:** scouting reveals public deployments, traits, level, health and pairing, never private benches or shops.

![Scouting changes the inspected board and provides a route home.](screenshots/raw/SHOT-043_20260906T112908369Z_scouting-opponent-board-bench-and-disabled-demon-trait.jpg)

*SHOT-043 — Scouting changes the inspected board and provides a route home.*

Eliminated seats remained labeled Defeated. Elimination produced visible reward drops and a healing cue. The final first-place banner made the endpoint clear. The following sequence included XP/promotional screens before a hero showcase and detailed standings. Deploy, Synergy and Relic tabs preserve context for all eight placements.

![Final deployment comparison with eight placements and the displayed 38–4 record.](screenshots/raw/SHOT-090_20260906T120220159Z_final-eight-seat-standings-deployments-and-win-loss.jpg)

*SHOT-090 — Final deployment comparison with eight placements and the displayed 38–4 record.*

![Final trait comparison attached to each placement.](screenshots/raw/SHOT-091_20260906T120227820Z_final-standings-synergy-comparison.jpg)

*SHOT-091 — Final trait comparison attached to each placement.*

Retain the less successful moments too: onboarding and long descriptions competed with preparation timers; the post-match path inserted progression and promotional UI before the useful comparison. Wonder Chess can prioritize result, explanation and restart without importing the marketing flow.

## Five prioritized Wonder Chess experiments

These are later-work proposals grounded in this match and the [v3 contract](../../../../docs/MASTER_IMPLEMENTATION_v3.md) and [UI/audio contract](../../../../docs/UI_AUDIO_AND_ONBOARDING.md). This research changed no canonical balance, game code or production assets.

| Priority | Evidence and problem | Original experiment within v3 | Observable check, not a claimed pass |
|---|---|---|---|
| 1. Action and trait feedback | SHOT-035/036/074/080: refreshing offers, deadlines and automation made outcomes ambiguous. | Review authoritative buy/merge/move feedback: consumed copies, survivor location, cost and exact rejection reason; preserve click-place alternatives and preview existing trait-count changes. | Exercise ordinary buy, full-bench merge, stale offer, combat lock and duplicate replacement in a packaged fixture. Accepted actions match visible state; rejections preserve economy and explain why. |
| 2. Hero readability | SHOT-030/047/064/089: shapes survive distance; tall shop models can clip. | Review all twelve original heroes at the calibrated gameplay camera and shop framing through required clips, using dossier-specific posture, gear and material groups. | Recognizable silhouettes, visible ownership/selection and no shop-frame clipping at 1080p and720p. Retain genuine captures. |
| 3. Concurrent effects | SHOT-070/079/085: bright areas obscure bodies and crowd indicators. | Establish visual priority for health, shield, control states and bodies; reduce decorative overlap while preserving declared mechanics and reduced-motion behavior. | In a dense encounter, reviewers can locate living units, teams, health and actual control states. Compare before/after captures with event logs. |
| 4. Courtyard and scouting orientation | SHOT-041/043/044/063: shadows and changing board context compete with tactical reading. | Refine original courtyard floor/perimeter contrast and the scouting banner/Return control. | Legal cells stay readable; scout-return preserves local selection, reveals no opponent bench/shop and cannot mutate another seat. |
| 5. Explanatory results | SHOT-071/086/090/091: placements become meaningful alongside final compositions. | Review event-derived recap and final standings with composition, health loss, ghost/timeout distinctions, spectate and restart. | Bots continue after human elimination; placements agree with logs; restart resets state and panels; damage/healing/shield metrics match actual events. |

## Limits and the next requested run

- **Audio/motion:** no recorded audio or continuous video. Still frames cannot certify sound mix, anticipation/recovery timing or smoothness.
- **Performance:** no frame-time instrumentation or hardware benchmark for this reference game. Visible network latency is not FPS. Wonder Chess performance acceptance is unchanged.
- **Balance:** one assisted Casual match cannot establish best composition, typical duration, opponent human/bot identity or item causation. The game's four-loss tally is not four fully observed experiments.
- **Coverage:** rounds 33–36 and39 are unobserved. Other capture intervals are event-driven, not a full replay.
- **Spectating after our elimination:** not encountered because our seat won; scouting was exercised.
- **Identity:** game version was not observed. Results show ID U3bFxQ, but its kind is unverified, so match_id remains null.

For a later requested run, create a fresh dated folder, establish a single active input operator and reliable controls before queueing, and focus on one design question. Keep optional inventory exploration away from the preparation deadline. Confirm the Dota 2 workshop client explicitly if that run must be Dota Auto Chess. Preserve this completed archive.

Screenshots remain private local reference material. No models, portraits, sound, code, exact layouts or proprietary asset files were transferred into Wonder Chess. These findings are reviewable questions for its existing original Unreal game, not release verification.

# Acceptance and evidence contract

## Scope of the included report

`reports/KIT_VALIDATION.md` reports checks performed on this specification/data/tooling package. It is not evidence that Blender assets, Unreal code, complete bot battles or networking already work. `reports/implementation_state.json` records actual prior execution and open gates; new update gates need fresh evidence for their own revision. Do not replace those states with green flags based on Python tests alone.

## Required test matrix

| ID | Scenario | Required result |
|---|---|---|
| DATA-01 | Full roster and alpha subset | 24 unique records; six races/classes each represented four times; playable selection is exactly 24 with 6×4 race and 6×4 class coverage; seven separate neutrals and complete reachable waves |
| DATA-02 | Authoring completeness | Art, biography, tactics, effect/timing/scaling, outputs and animation contract for every hero |
| DATA-03 | Profile validation | Valid IDs/timings, shop weights sum to 100%, enabled tiers nonempty, alpha excludes expansion |
| DATA-04 | Derivative parity | Dossiers, Unreal rows and content hashes match source |
| RULE-01 | Numeric fixtures | Exact centipoint and rate results; same outputs in Unreal |
| RULE-02 | Trait effects | Unique deployed types only; matching recipients; highest eligible threshold two/four replaces lower; no duplicate bonus application |
| RULE-03 | Shield/heal/stun | Correct replacement, expiry tick, overflow, caps and interrupt/release ordering |
| RULE-04 | Movement/dash | No duplicate occupation, leaked reservation, invalid corner step or secret dash damage |
| ECON-01 | Full bench purchase | Valid merge succeeds atomically; invalid purchase preserves gold/offers/roster |
| ECON-02 | Command replay | Same ID/payload returns prior result; changed payload rejected; no second spend |
| ECON-03 | Level/interest/sale | Exact XP progression, locked interest, preserved copy value and no capped-level charge |
| MATCH-01 | 8..2 active seats | Disjoint health-affecting opponents, no self-pair, deterministic policy |
| MATCH-02 | Odd count | Ghost donor unchanged; recipient settled once; history and displayed identity agree |
| MATCH-03 | Results | Whole-round atomic settlement, simultaneous elimination, zero survivors and capped ranks |
| MATCH-04 | Real battle coverage | Every bot-versus-bot fight uses same combat runner; visibility does not affect trace |
| MATCH-05 | Restart/spectate | Early human elimination never stalls the remaining tournament; new match resets state |
| BOT-01 | Legal economy | Same command authority, real gold/XP and no privileged mutation |
| BOT-02 | Privacy | Cannot read opponent shops/benches, future draws or human private actions |
| BOT-03 | Policy budget | Bounded actions/rerolls, diverse preferences, sensible holds; frequent rejected/no-op actions flagged |
| ART-01 | Calibration | Meter/cell/forward/root/feet measured in actual Unreal |
| ART-02 | Reference hero | Ada complete and readable, seven clips, portrait, shield and reimport evidence |
| ART-03 | Alpha roster | 24 distinct silhouettes, 168 continuously reviewed hero/clip combinations, correct effects and no missing maps |
| ART-04 | Reimport | Changed source asset preserves material, skeleton, animation and placed actor references |
| UI-01 | Full journey | Menu→lobby→tournament→results→restart, drag and click alternatives |
| UI-02 | Information | Actual stats/traits, private-state separation, correct recap and ghost labels |
| UI-03 | Language/access | en/id key parity, overflow check, focus, reduced motion and 720p layout |
| NET-01 | Two processes 2H6B | Consistent phase/economy/board/outcomes with authenticated commands |
| NET-02 | Invalid inputs | Out-of-order/replayed IDs, wrong owner, stale revision and combat buys rejected |
| NET-03 | Disconnects | Non-host bot takeover; host abort; rejoin rejected clearly; no extra gold |
| PKG-01 | Actual package | Launch outside editor/source directory, all cooked content present |
| PKG-02 | Whole matches | Complete 1H7B runs, results and restart from executable |
| PERF-01 | Named machine | 1080p target tested; CPU/GPU percentiles, memory, busy effects and stalls recorded |

## Engine regression batch

Run at least 100 seeded full eight-bot tournaments with real hero combat after integration. Seed list and failures must be reproducible. Save engine/toolchain version, commit (when one exists), profile and catalog hashes, start/end timestamps, trial count, failure seeds, fight/match lengths, timeout rate, illegal states, command rejects, ghost distribution, per-hero use and placements. Do not silently drop failed trials. A synthetic-outcome scheduler test does not count as a combat tournament.

Run equal-investment, equal-star and mirror-swapped formation fixtures separately. Interpret them as bug/balance evidence, not a solved metagame. Compare shield-heavy, sustain, spread ranged, paired Mage and Rogue-pressure formations. Include empty-versus-empty, pending projectile after source defeat, frame-hitch and observed/unobserved replay checks.

## Visual/audio review

Capture actual editor/game images or video, not illustrations presented as screenshots. For each hero include front/side/back, grayscale 96-pixel silhouette, seven clips, gameplay camera, busy-fight overlap and source revision. Log who/what performed visual review and concrete defects. A mesh-stat pass cannot verify deformation or attractive art.

Required review questions: Can a new player identify team ownership, frontline versus support, current selection, attack type, shield versus health, stun and dash direction? Does the active animation release agree with the effect time? Can the player understand the shop and their loss without reading lore? Is the camera stable and the audio nonintrusive?

## Performance and packaging

Name CPU/GPU/RAM, display resolution, engine build, graphics settings, driver where relevant and tested scene. Measure frame-time percentiles and hitches with twelve visible combatants, all four PvP simulations, all eight neutral simulations, lobby and gallery. No assumed 60 FPS from a polygon count. Test a cold package launch, settings persistence and at least one full tournament outside the source directory. No physical mobile claim from desktop emulation.

## Severity and release rule

P0: data loss/security/privacy defect or unusable package. P1: crash, stuck match, incorrect authority/settlement, broken required skill, missing required hero or unreadable basic interaction. P2: visible deformation, wrong effect/range, major readability or performance failure. P3: minor cosmetic/editorial issue. P0/P1 block release. P2 art/gameplay acceptance failures block a “presentable alpha” claim unless the scope is explicitly changed; do not label them trivial polish.

Each evidence record stores test ID, actual command/environment, inputs/seed, expected and observed result, exit code when applicable, paths/hashes, PASS/FAIL/NOT_RUN and issue link. Missing tools are NOT_RUN/BLOCKED, not passed-by-skip.

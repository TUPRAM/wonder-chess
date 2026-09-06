# Wonder Chess — Master Implementation v3
## A playable-first eight-seat auto-battler

**Adopted update, 2026-09-06:** the user authorized the 24-hero implementation package in `updates/2026-09-auto-chess-inspired/README.md`. Execute WC-U400–460. This document incorporates its explicit amendments; unchanged v3 rules and prior evidence remain in force.

**Authority:** Active project specification, replacing website-first v2 sequencing and the proposed decision brief. The user requested an enhanced implementation handoff after selecting Wonder Chess and one human plus seven bots. New character names, art, values and precise engineering choices in this kit are original proposed implementation inputs—not claims that prior sources already contained them or that gameplay is balanced.

## 1. The deliverable

Continue the existing original Windows Unreal project. One human competes with seven persistent bots through simultaneous pairwise team battles and isolated neutral encounters. All 24 authored heroes can be recruited, upgraded, positioned and inspected. A complete tournament reaches standings, elimination, spectating, final results and a clean restart. It launches without Unreal Editor, Blender, Codex, a web server or an AI service.

“First implementation” means one coherent assignment pursued through internal build/test/fix checkpoints. It does not mean one blind generation, and it does not justify pretending missing tools ran. Do not stop at a plan or a single static battle while permitted integration work remains.

All 24 production heroes are now required. Preserve and refine the existing twelve before completing the additional twelve in the adopted batch order. A website is not a deliverable; old diagnostic subsets remain fixtures rather than acceptance of the full roster.

## 2. Identity and world

Name: **Wonder Chess**. Working tagline: **A world of magic. A board of possibilities.** New repository: `wonder-chess`; Unreal project: `game/WonderChess.uproject`; runtime namespace/prefix: `WC`. The title is the selected working brand, with no trademark or domain-clearance claim.

High fantasy is hopeful, magical, heroic and adventurous. Aurelune contains warm taverns, ancient elven woodland, dwarven halls, caravan highlands, riverside markets and Dragonkin beacons. The Hollow Court threatens an old ward network; the coalition’s competitive trials train captains to combine different peoples effectively. Battles are stylized non-graphic manifestations. No gore or sexualized costumes.

Keep the lore optional. Players learn “shield,” “stun,” “heal” and “dash,” not a glossary of invented resources. Race and class affect composition; region and faction do not create a third trait system.

## 3. Locked alpha scope

| System | Required |
|---|---|
| Modes | 1H7B play, 0H8B automated combat, 2H6B actual network validation |
| Tournament | Eight seats, live pairing, odd-count ghost policy, round settlement, elimination and rank ties |
| Battlefield | One 8×8 board per encounter; four PvP simulations or eight isolated neutral simulations at eight active seats |
| Content | Twenty-four heroes, six active races, six classes, one active skill each; seven separate neutral archetypes |
| Traits | Highest eligible tier at two/four distinct deployed types; matching recipients; combat-start snapshot |
| Economy | Independent shops, three costs, reroll, lock, buy XP, interest, merge, sale |
| Presentation | One polished courtyard, 24 intentional silhouettes, seven clips per hero, model-matched portraits, VFX/SFX |
| Interface | Graphical lobby, truthful session setup/readiness/transition, full hero gallery, preparation/combat HUD, shop, bench, tooltips, scout, standings, recap, spectate, results, restart |
| Language | Data-driven English and Indonesian core UI, draft translation review |
| Distribution | Windows package and real launch evidence |

No open world, account backend, ranked service, paid random rewards, shared-pool draft, equipment inventory, summons, transformations, automated live balance updates, cinematic story campaign, or marketing site in the alpha. Eight-human hosting, mobile and monetization are separate later decisions. Do not conflate bots with proven human multiplayer support.

## 4. Source of truth and precedence

`data/units.json` is editable character/numeric source. `data/rules.alpha.json` is the active numeric profile. `data/traits.json` carries the active two-/four-member tiers. `data/neutrals.json` carries the seven original creatures and eleven waves through the adopted starting cap of 40. `data/world.json` and `data/bots.json` carry world and bot authoring inputs. Dossiers and Unreal rows are generated derivatives.

Narrative rules live in `GAME_RULES.md` and `TOURNAMENT_AND_BOTS.md`. A discrepancy between narrative and data is a defect: record and resolve it with tests, not an excuse to silently choose whichever is convenient. Required product behavior in this master outranks task convenience. Actual higher-priority workspace/security instructions still apply.

`tools/build_documents.py` generates all dossiers and both anthologies. `tools/compile_catalog.py` generates Unreal-shaped row files and a content digest. Do not hand-edit generated rows. Compile the supplied `FTableRowBase` candidates before importing corresponding rows, then compare values. Import compatibility is not established until tested in the installed editor.

## 5. Hero production and quality

Ada Brightshield is the reference character. Complete her silhouette, model, surfaces, rig, animation, shield, portrait, selection ring and in-engine presentation. Change one source costume detail and reimport without breaking references. Then construct the other alpha heroes using approved rig families and modular parts.

No delivered hero may be only a recolored mannequin, primitive pile, static statue or unreviewed generated mesh. Temporary blocks are permitted inside development checkpoints and must be visibly labeled as such. Use the individual dossiers for head shape, clothing, gear, back view, palette, body motion and effect cues.

Every hero must read at the locked gameplay camera in a twelve-unit encounter. Small gear details that vanish at distance are subordinate to silhouette, posture, timing and material grouping. Out-of-range props must not imply attacks hit farther than the data. Star upgrades change stats and restrained presentation accents, not footprint or a completely new character body.

## 6. What “good gameplay” must demonstrate

The 24-hero roster supports several viable formation hypotheses. It does not prove balance. Test protection against flank pressure, grouping against area magic, burst against shields, sustain against sustained attacks, and leveling versus duplicate hunting. Elin’s positive buff is included in Priest support potency so her class bonus has a defined effect; this is an explicit v3 refinement.

No one composition should be selected as “best” by assertion. Log battles and compare equal investment as well as equal stars. Show why an action failed, what an upgrade consumed, which trait activated and how health was lost. Players must be able to scout and make a meaningful change before the next round.

In combat, simulation—not animations, frame rate, actor visibility or arbitrary physics—owns occupancy, effects and defeat. Off-screen fights must remain real fights. Network clients submit intentions and never declare final gold, purchases, damage or winners.

## 7. Production order and ownership

| Task | Deliverable | Owner lane |
|---|---|---|
| WC-300 | Toolchain audit, safe new project, baseline validation, minimal package | Integration |
| WC-310 | Numeric/command/board contracts and real combat loop | Runtime |
| WC-320 | Eight-seat tournament, economy and persistent legal bots | Runtime + QA |
| WC-330 | Reference hero, calibrated board and reliable source round-trip | Art |
| WC-340 | Eleven remaining alpha heroes, shared materials, clips and effects | Art, serialized per binary |
| WC-350 | Content adapter, HUD, scouting, onboarding, audio and full match | Integration |
| WC-360 | Package, 100 real all-bot combat matches, two-client test and performance evidence | QA |

The runtime graybox and reference-art lane can overlap after contracts stabilize. Art-ready does not equal integrated; integrated does not equal packaged; packaged does not equal visually acceptable. Maintain these states separately. Every task has its own focused brief in `docs/tasks/`.

Only one owner edits a canonical data file, Unreal map, shared blueprint or `.blend` at a time. Different heroes can be handled independently after the base-rig contract is frozen. Do not treat binary conflicts as mergeable text.

## 8. Tool and helper policy

Use the actually installed Blender, Unreal, compiler/SDK, Python and Git. Inspect versions and paths. Codex operates files and permitted local processes; it does not automatically own an editor bridge. Optional bridges require capability/permission checks and a useful reason. Do not install random plugins to evade missing automation.

Use Blender Python for repeatable authoring/preflight/export. Use Unreal C++ for rules and editor-supported tools for content operations. Unreal Python is editor-only; do not use it as packaged gameplay. See technical references in `SOURCE_AND_CHANGE_LOG.md`.

The supplied Python fixtures are reference contracts. They do not simulate complete fights. The Blender scripts and Unreal row header have explicit unverified-editor status. Do not promote their status merely because Python can parse them.

Tools require scoped input/output paths and nonzero errors. Never clear an unrelated Blender scene, delete another repository, suppress compiler errors, or bypass permissions. Do not expose paths containing personal data in public reports.

## 9. Acceptance and honest handoff

The delivered game must complete full 1H7B tournaments, allow early elimination and spectating, and restart without stale state. All 24 heroes must be accessible under normal progression, have their defined behavior and required presentation, and be represented accurately in UI.

At least 100 actual eight-bot **combat** matches must run in the eventual engine build. Record seeds, build/data hashes, failures, unresolved combats, durations and results. Reference pairing tests supplied in this kit are not those matches. Also run 2H6B with two real network instances, private-state checks, invalid-command tests and documented disconnect behavior.

Target 1080p/60 FPS on a named test PC with a defined preset. Measure CPU/GPU frame times, memory and busy-fight behavior; do not infer performance from triangle counts. Mobile is not certified by a desktop test.

Final report: executable and launch instructions if actually produced; source/assets; implemented versus deferred content; evidence of complete matches and reimport; actual test commands/results; known defects with severity; and the next unblocked task. Failed mandatory art or gameplay acceptance means incomplete, not “production ready with minor issues.”

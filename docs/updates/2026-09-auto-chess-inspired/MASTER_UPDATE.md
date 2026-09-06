# Wonder Chess — 24-hero update design

**Adopted for execution on 6 September 2026.** The user's implementation request authorizes these explicit v3 amendments. The following preparation status is historical; it does not negate current implementation. Consult `reports/implementation_state.json` for completed checkpoints and open gates. Canonical schema 3.1.0 / profile `alpha_24` implements the data migration; a source or early-package pass is not final playable/art acceptance.

Status: **IMPLEMENTATION PLAN PREPARED; GAME CHANGES NOT IMPLEMENTED BY THIS TASK.** Date: 6 September 2026. Scope decisions explicitly confirmed by the user: all 24 authored heroes become fully playable; weapons/armor improve visually; no combat-item inventory. The user also requested clearer names, better race/class synergies, skills and character presentation, monster rounds, a graphical lobby, matchmaking transition and full hero gallery.

## Authority and adoption

This package prepares the requested update. The existing v3 contract and runtime remain unchanged during preparation. When the user sends [INITIAL_IMPLEMENTATION_PROMPT.md](INITIAL_IMPLEMENTATION_PROMPT.md), that instruction adopts the specific changes below for the next implementation. Update the affected narrative, schema, numeric profile, generators and tests together at WC-U400; do not leave contradictory active contracts or merely edit a generated dossier.

| Topic | Existing v3 | Adopted update target |
|---|---|---|
| Playable roster | 12 alpha heroes; 12 future designs | All 24 existing stable identities, normally recruitable and fully presented |
| Traits | Four races, six classes; threshold 2 | Six races and six classes; thresholds 2 and 4, highest tier replaces lower |
| Neutral encounters | Pairwise PvP throughout | Monsters on rounds 1, 2, 3 and every positive multiple of 5; PvP otherwise |
| Round cap | 24 | Proposed default 40, distinct cap adjudication retained; legacy 24-round fixtures explicitly versioned |
| Abilities | One single-effect active per hero | One active per hero remains; only individually specified, bounded multi-effect improvements may extend its schema |
| Front end | Functional menu/lobby/HUD | Original 3D Brighthaven lobby, native hero gallery/detail, honest preparation/connection flow and board transition |
| Equipment | No inventory | No inventory remains; all 24 gain dossier-specific visual weapons/armor |
| Names | Full names in many contexts | Short first names in HUD/shop; full names, titles and biography in gallery |

The existing Unreal project, original world, 8-seat tournament, independent shops, legal persistent bots, authoritative deterministic combat, privacy, 1H7B/0H8B/2H6B modes and Windows package remain required. No new website, project clone, online account backend, fake human matchmaking, real-money shop, copied game assets, item loot, extra region maps or third counted role-synergy system is introduced. VEILMARK remains untouched.

All new numerical settings here and in the supporting files are **proposed tuning inputs**, not balanced or measured claims. Scope approval is not evidence of implementation quality. A later intentional tuning change must update its version, tests and decision log; it does not require repeating permission questions for ordinary authorized implementation.

## Starting point to preserve

Preparation baseline source: `5a496a7e96162c1af15bddbbc1d83e988cc128a0`. [Existing release handoff](../../../reports/RELEASE_HANDOFF.md) records a packaged candidate, twelve authored/imported heroes and 84 animation clips, original arena/audio, native combat and network evidence. It also retains incomplete manual/continuous presentation and audio review. These are prior records, not new execution results from this planning task. Asset metadata saying `designed_not_built` must not erase newer execution evidence.

The candidate remains at `builds/WonderChess-Alpha-Candidate/Windows/WonderChess.exe`. Implementation must inspect and reuse the existing checkout, meshes, rest skeletons, importer settings, controller/network paths and authored records. Do not start a new blank project or regenerate all assets indiscriminately. Record a fresh baseline before editing; unrelated local reports and binaries are not cleanup targets.

## Product direction

Wonder Chess should feel like arranging a collection of expressive fantasy champions in a welcoming world. The art direction remains warm limestone, blue roofs, navy/ivory cloth, aged bronze, hanging gardens and restrained gold/teal beacon magic. Dark accents belong to contrast and threat cues, not an unrelated grim setting. Character faces, body masses, equipment and motion must distinguish all 24 without relying on recolors.

The three primary lobby actions are **Play**, **Heroes** and **Settings**. A selected hero animates in the center of a real 3D scene. Background motion is restrained and readable. The front end and arena share the Seven-Lantern Courtyard's vocabulary, so entering battle feels like approaching the nearby trial board rather than teleporting to an unrelated product.

Flow: graphical lobby → mode/session setup → real readiness/load progress → eight-seat introduction → round 1 monster preparation → automatic battle → recap → preparation. Rounds 1–3 teach buying, forming a team and reading enemy behavior through normal rules; optional teaching overlays remain skippable and cannot freeze only one client. The reference game's marketing panels and inventory systems are not part of this flow.

## Roster, names and trait readability

Use the existing 24 IDs and full biographies. `display_name` is a canonical first-name field; retain `name`, `title`, slug and asset IDs. Add shared localized display labels rather than per-widget substitutions. Every hero has one race and one class, with role text helping players understand use: Tank, Melee, Ranged, Caster, Support, Healer or Control. Role is informational and never adds another hidden modifier.

Race badges read Human, Elf, Dwarf, Orc, Halfling and Dragonkin. Class badges read Guardian, Warrior, Ranger, Mage, Priest and Rogue. Existing poetic synergy titles may remain secondary flavor text in expanded detail; the short labels lead.

All six races and all six classes have four authored members, so 2/4 thresholds are reachable. Count distinct deployed definition IDs, never stars, duplicate instances or the bench. Show current count, next threshold, exact effect and affected recipients. Higher tier replaces lower, race and class stack by the current common evaluator, and effects snapshot at combat start for both PvE and PvP. Preview a replacement's consequences before commitment without changing state.

The first update keeps the 8×8 board, six deployed heroes per seat, eight bench positions, five shop offers, three cost bands and existing XP table as proposed starting defaults. With six slots, a 4-member commitment plus complementary 2-member traits is a meaningful choice. The 24-hero shop changes duplicate probability and requires actual bot/combat tuning; do not claim the old economy is already balanced for it.

## Monster rounds and pace

Use the exact positive-round predicate `r <= 3 || r % 5 == 0`. Thus 1,2,3,5,10,15,20,25,30,35,40 are neutral encounters through the proposed cap; 4,6–9 and other nonmultiples are PvP. Each surviving seat fights its own real, deterministic neutral instance. Monsters are encounter participants, not a ninth tournament seat, shop offers, summons or playable hero substitutes.

Public wave information lets the human and bots prepare. Bots cannot inspect private enemy shops/benches or unseen RNG. Neutral rounds do not advance PvP pairing history or PvP wins. Use separate absolute-round and PvP-round indices so damage stages do not accidentally advance during the opening three monster rounds. Public recap distinguishes monster result, captain loss and pending next-preparation reward.

Proposed initial reward: +2 gold on neutral victory instead of the +1 PvP win bonus, credited once on the next surviving preparation. Base income, interest snapshot and passive 2 XP occur once under existing eligibility rules; no additional XP or manual pickup. Opening neutral losses cause no captain damage; later neutral losses/draws cause 2. See [SYSTEMS_MIGRATION.md](SYSTEMS_MIGRATION.md) for ordering, ties, cap and network details and [MONSTER_WAVES.md](MONSTER_WAVES.md) for wave design.

Pace is measured, not promised. Keep initial 45-second preparation, later 25-second preparation, 40-second combat ceiling and 4-second recap as starting values. A 40-round cap is a limit, not a forced duration. Log observed human-session length, combat timeouts, first elimination and capped finishes; adjust transparently if the expanded roster/neutral pacing is too long or produces frequent adjudication.

## Visual and audio completion

All 24 heroes require intentional face/hair, front/side/back silhouette, weapon grips, material separation, model-derived portraits, two lower LODs and the seven real imported clips: Idle, Move, Attack, Active, Hit, Defeat and Victory. These are the existing canonical clip identifiers; UI may label Active as Skill. New Halfling/Dragonkin proportions need validated rigs; do not scale existing bodies uniformly and call them finished.

Art work follows IMPLEMENTATION_SEQUENCE: Ada, other eleven existing heroes, four additions using existing families, then the Halfling and Dragonkin families with an accepted pilot before each family batch. Preserve accepted skeleton/rest-pose conventions and prove a source costume change survives reimport. All 24 get a normal-speed individual skill review and a crowded board review, not only still samples. See [HERO_UPGRADE_BRIEFS.md](HERO_UPGRADE_BRIEFS.md).

Weapons and armor are character design, not item pickups or gameplay stat slots. Star accents remain restrained and footprint stays one cell. Gallery animation playback cannot produce live combat damage or imply different rules. Effects preserve target/body/HP readability; no shader obscures several adjacent heroes. Required sound families extend to all new skills and neutral encounters with original/properly licensed material, sliders, voice limits and real listening review.

## Acceptance and task order

Follow [IMPLEMENTATION_SEQUENCE.md](IMPLEMENTATION_SEQUENCE.md), with one owner per canonical file and binary. Schema/rules integration and art can run independently after their shared contract is frozen. The next checkpoint always includes implement → execute → inspect → fix and a package where the change matters. An intermediate checkpoint is not a reason to stop while authorized independent work remains.

Acceptance requires all 24 accessible through normal shops and the gallery; truthful UI values at three stars; complete 1H7B tournament, elimination/spectating and restart; actual 0H8B engine combat regressions including neutrals; and an actual two-machine 2H6B LAN check when available. Two processes on one PC are useful additional coverage but do not certify the physical LAN requirement. Missing a second machine blocks that gate, not unrelated work.

Measure the package at 1080p and 720p for UI, and frame-time CPU/GPU/memory on named hardware at a stated preset. Eight concurrent neutral encounters may cost more simulation work than four paired PvP encounters; rendering only one does not allow replacing the other seven with score estimates. Game tools must actually run. Missing editor/compiler/Blender or native input access must be logged precisely; source code or a model render is not packaged-playability proof.

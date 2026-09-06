# Wonder Chess — the 24-hero update package

**Prepared for implementation, 6 September 2026.** This task discussed and prepared the update; it did not modify the running game, canonical balance, generated dossiers or production art. The user explicitly selected **24 fully playable heroes** and **visual weapons/armor only, without an item inventory**. Monster rounds, a graphical lobby and matchmaking-to-board transition, a full hero gallery, clearer names/synergies and improved character presentation are required parts of the requested update.

## Read and execute

1. [MASTER_UPDATE.md](MASTER_UPDATE.md) — adopted scope, deliberate v3 changes, product direction, baseline preservation and acceptance boundary.
2. [FRONTEND_AND_GALLERY.md](FRONTEND_AND_GALLERY.md) — original lobby design, session state flow, all-hero gallery/detail, input and stat-display contracts, four supplied reference images.
3. [SYSTEMS_MIGRATION.md](SYSTEMS_MIGRATION.md) — exact current source constraints, 24-hero/trait activation, neutral ownership, economy/settlement, bots/networking and tests.
4. [MONSTER_WAVES.md](MONSTER_WAVES.md) — seven original monster archetypes and eleven complete proposed waves, positions, numbers, skills and art direction.
5. [HERO_UPGRADE_BRIEFS.md](HERO_UPGRADE_BRIEFS.md) — individual name, skill, face/model, costume/gear, animation, VFX and review brief for all 24 existing heroes.
6. [REFERENCE_DECISIONS.md](REFERENCE_DECISIONS.md) — what we take, adapt or deliberately omit from all 93 playthrough captures and four new screenshots.
7. [IMPLEMENTATION_SEQUENCE.md](IMPLEMENTATION_SEQUENCE.md) — WC-U400–460, serialized ownership, practical execution order, evidence destinations and required verification.
8. [INITIAL_IMPLEMENTATION_PROMPT.md](INITIAL_IMPLEMENTATION_PROMPT.md) — the complete prompt to begin the implementation in this existing workspace.

## Decisions prepared

| Decision | Update direction |
|---|---|
| Brand/world | Wonder Chess, original Aurelune/Brighthaven and Seven-Lantern Courtyard |
| Names | Ada, Mira, Rowan, etc. in quick UI; full name/title/biography in Heroes |
| Roster | All 24 authored IDs, six races × four heroes, six classes × four |
| Synergies | Reachable 2/4 tiers, highest replaces lower; explicit recipients and distinct-type counting |
| Role labels | Tank, Melee, Ranged, Caster, Support, Healer, Control; descriptive only |
| Equipment | Better modeled weapons/armor and restrained star accents; no inventory or item bonuses |
| Monster schedule | Rounds 1–3 and every positive multiple of 5 |
| Initial tuning proposals | Cap 40; keep 60 HP, six deployment slots and current economy/clocks; neutral win +2 next-preparation gold, normal XP once, no opening neutral-loss damage, later loss/draw 2 |
| Lobby/session | Original 3D hero/environment, Play/Heroes/Settings, truthful Solo or LAN progress, first preparation after load/transition |
| Gallery | All 24 playable heroes, filters/grid/showcase, real model, three-star stats, Skill/Synergies/Tactics/Story |
| Delivery | Updated packaged Windows Unreal game; same rules for 1H7B, 0H8B and actual 2H6B LAN |

New numbers are testable starting proposals; no balance or completed art is claimed. Neris's bounded damage-then-stun and Finn/Oren's targeting proposals require explicit schema/runtime tests. Other skills retain their authored identity while improving their tactical clarity, presentation and individual weak points. Nothing automatically adds mana, equipment loot, summons, transformations, revival, hidden damage or a third trait system.

## Evidence and preservation

- [Preparation validation](preparation-validation.json) records actual baseline validator outcomes and final document/reference checks.
- [Reference provenance](references.json) records the four supplied PNG originals copied from temporary storage into this durable project folder, with hashes. Images remain local and Git-ignored; this index is versioned. They are references, not game assets.
- [Playthrough gallery](../../../research/playthroughs/runs/next-dota-auto-chess/gallery.md) retains 93 actual screenshots. [Findings](../../../research/playthroughs/runs/next-dota-auto-chess/findings.md) explains the shared-input/gap limits. No audio/performance inference is made from those images.
- [Existing release handoff](../../../reports/RELEASE_HANDOFF.md) and [implementation state](../../../reports/implementation_state.json) remain the record of prior game work and its incomplete gates. This update has not inherited a new playable/visual pass from them.

The known candidate path is `builds/WonderChess-Alpha-Candidate/Windows/WonderChess.exe`; this preparation did not rebuild or relaunch it. The proposed new package path is specified in the implementation sequence and becomes a deliverable only after it is produced and tested. No active v3 file is silently superseded merely by reading a proposal: sending the implementation prompt adopts this package's explicit amendments, after which the runtime owner updates the active contracts coherently.

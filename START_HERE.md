# Wonder Chess — Codex Production Kit v3

**First deliverable: a presentable, packaged Windows auto-battler with one human and seven persistent bots.**

This repository contains the original kit and subsequent authored assets, Unreal source and a packaged twelve-hero candidate. Read `reports/RELEASE_HANDOFF.md` and `reports/implementation_state.json` for actual evidence and open gates. The user adopted the 24-hero update on 2026-09-06; its implementation package is `docs/updates/2026-09-auto-chess-inspired/README.md`. Historical kit-only statements do not erase real progress.

## Use this package

1. Resume this existing Wonder Chess workspace and `game/WonderChess.uproject`. Preserve source, imported art and prior evidence; do not extract a replacement checkout or access VEILMARK.
2. Open that directory in a Codex environment that can actually execute the locally installed Blender, Unreal Editor and Windows C++ build tools. A remote Linux environment without those tools can validate data, but cannot certify the Windows game or its imported art.
3. Execute the adopted `docs/updates/2026-09-auto-chess-inspired/INITIAL_IMPLEMENTATION_PROMPT.md` and WC-U400–460 sequence. The original FIRST_MESSAGE_TO_CODEX is historical bootstrap context.
4. The active specification is `docs/MASTER_IMPLEMENTATION_v3.md` with the explicitly adopted 24-hero update package. Earlier v2 and discussion briefs are source history, not competing instructions. The old project remains untouched.
5. Run `python tools/validate_kit.py`, `python -m unittest discover -s tests -v`, `python tools/build_documents.py --check`, and `python tools/compile_catalog.py --check` as baseline checks. A successful baseline validates this handoff, not a game build.

For a clean Python environment, create a project-local virtual environment and install `requirements-tools.txt` there before validation. The reference tests themselves use the standard library; schema validation additionally uses the pinned `jsonschema` package. Do not modify global Python or editor-managed packages.

## Read order

| File | Purpose |
|---|---|
| `docs/MASTER_IMPLEMENTATION_v3.md` | Delivery target, ownership, order, completion standard |
| `docs/GAME_RULES.md` | Combat, economy, movement, upgrade and status contracts |
| `docs/TOURNAMENT_AND_BOTS.md` | Eight seats, pairing, ghosts, settlement and legal bot decisions |
| `docs/CHARACTER_BIBLE_24.md` | Complete human-readable roster, including art and all numerical skills |
| `docs/ALPHA_24_ASSET_BRIEFS.md` | All 24 playable heroes; preserve the existing twelve and complete the other twelve |
| `docs/BLENDER_PRODUCTION.md` | Art direction, rig/export/calibration/reimport process |
| `docs/UNREAL_IMPLEMENTATION.md` | Runtime architecture, content import, networking, cooking and packaging |
| `docs/UI_AUDIO_AND_ONBOARDING.md` | In-game experience; no website dependency |
| `docs/QA_ACCEPTANCE.md` | Exact evidence needed before declaring the alpha playable |
| `docs/tasks/` | Bounded tasks and ownership, still part of the full assignment |
| `reports/KIT_VALIDATION.md` | Checks actually executed while preparing this package |
| `docs/SOURCE_AND_CHANGE_LOG.md` | Retained decisions, new proposals, technical references and limitations |

## Scope that must not drift

Twenty-four playable heroes, six races, six classes and highest eligible two-/four-member trait tiers; one arena; eight-seat tournament; monsters on rounds 1–3 and every positive multiple of five; a graphical lobby and full hero gallery. No item inventory, real-money system, hidden bot advantage or runtime language-model call. Artwork and combat behavior must match canonical records. Numeric update inputs require actual play and performance measurements.

## What the provided tools establish

The reference library checks mathematics, transactions, pairing and settlement **from supplied battle outcomes**. It is not a substitute combat engine. The Blender helper scripts and Unreal import structures must be executed/compiled with the actual installed editors. Read their evidence status before assuming they work in that environment.

No font binaries, external game assets, downloaded animations, cloud credentials, engine installation, or paid content are included. No trademark/domain clearance is claimed. Core English/Indonesian strings are draft copy requiring playtest and language review.

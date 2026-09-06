# Wonder Chess — Codex Production Kit v3

**First deliverable: a presentable, packaged Windows auto-battler with one human and seven persistent bots.**

This kit supplies the active implementation specification, all 24 character designs, the twelve-hero alpha subset, numerical source data, Blender/Unreal task briefs, and executable reference checks. It is not a finished game and does not contain completed `.blend`, `.uasset`, `.umap` or playable `.exe` files.

## Use this package

1. Extract the ZIP, then open the extracted folder that directly contains `AGENTS.md` as a new `wonder-chess` workspace (rename that folder if needed). Do not place it inside VEILMARK. Keep the original folder structure, especially `data`, `docs`, `tools`, `tests`, and `.agents`.
2. Open that directory in a Codex environment that can actually execute the locally installed Blender, Unreal Editor and Windows C++ build tools. A remote Linux environment without those tools can validate data, but cannot certify the Windows game or its imported art.
3. Give Codex the contents of `FIRST_MESSAGE_TO_CODEX.md`. It directs Codex through the whole playable-alpha assignment, not a website-first bootstrap task.
4. The active specification is `docs/MASTER_IMPLEMENTATION_v3.md`. Earlier v2 and discussion briefs are source history, not competing instructions. The old project remains untouched.
5. Run `python tools/validate_kit.py`, `python -m unittest discover -s tests -v`, `python tools/build_documents.py --check`, and `python tools/compile_catalog.py --check` as baseline checks. A successful baseline validates this handoff, not a game build.

For a clean Python environment, create a project-local virtual environment and install `requirements-tools.txt` there before validation. The reference tests themselves use the standard library; schema validation additionally uses the pinned `jsonschema` package. Do not modify global Python or editor-managed packages.

## Read order

| File | Purpose |
|---|---|
| `docs/MASTER_IMPLEMENTATION_v3.md` | Delivery target, ownership, order, completion standard |
| `docs/GAME_RULES.md` | Combat, economy, movement, upgrade and status contracts |
| `docs/TOURNAMENT_AND_BOTS.md` | Eight seats, pairing, ghosts, settlement and legal bot decisions |
| `docs/CHARACTER_BIBLE_24.md` | Complete human-readable roster, including art and all numerical skills |
| `docs/ALPHA_12_ASSET_BRIEFS.md` | The twelve heroes to actually model and implement first |
| `docs/BLENDER_PRODUCTION.md` | Art direction, rig/export/calibration/reimport process |
| `docs/UNREAL_IMPLEMENTATION.md` | Runtime architecture, content import, networking, cooking and packaging |
| `docs/UI_AUDIO_AND_ONBOARDING.md` | In-game experience; no website dependency |
| `docs/QA_ACCEPTANCE.md` | Exact evidence needed before declaring the alpha playable |
| `docs/tasks/` | Bounded tasks and ownership, still part of the full assignment |
| `reports/KIT_VALIDATION.md` | Checks actually executed while preparing this package |
| `docs/SOURCE_AND_CHANGE_LOG.md` | Retained decisions, new proposals, technical references and limitations |

## Scope that must not drift

Twelve playable heroes, four active races, six active classes, two-unit trait thresholds; one arena; eight-seat tournament; no real-money system, loot boxes, website-first work, hidden bot advantages or runtime language-model calls. All 24 designs are supplied, but twelve expansion heroes are excluded from the alpha shop and asset gate. Artwork and combat behavior must match the records.

## What the provided tools establish

The reference library checks mathematics, transactions, pairing and settlement **from supplied battle outcomes**. It is not a substitute combat engine. The Blender helper scripts and Unreal import structures must be executed/compiled with the actual installed editors. Read their evidence status before assuming they work in that environment.

No font binaries, external game assets, downloaded animations, cloud credentials, engine installation, or paid content are included. No trademark/domain clearance is claimed. Core English/Indonesian strings are draft copy requiring playtest and language review.

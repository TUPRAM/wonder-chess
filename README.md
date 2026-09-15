# Wonder Chess

The current Wonder Chess successor project, its Unreal assets, source art, packaged candidates and local project support now live in this one folder. **Copy the entire folder to the new PC, including hidden `.git` and ignored `builds/` and `support/`.** A GitHub download alone will not include the complete local project.

## Start here

- **Play the current Storybook r20 solo candidate:** double-click `Play Wonder Chess.cmd`.
- **Open its combat laboratory:** double-click `Play Storybook Lab.cmd`.
- **Build/edit the game:** `game/WonderChess.uproject`.
- **Move computers:** [TRANSFER_TO_NEW_PC.md](TRANSFER_TO_NEW_PC.md).
- **Continue development:** [current milestone status](docs/vnext/milestones/MILESTONE_STATUS.md), [implementation readout](docs/vnext/milestones/IMPLEMENTATION_READOUT.md), and [successor contract](docs/vnext/README.md).
- **Inspect the consolidation:** [reorganization report](reports/REORGANIZATION_2026_09_15.md).

Storybook r20 is a six-creature development candidate. Its prior technical and art evidence remains scoped as recorded; proxy 3D creatures, pacing and acceptance work remain open.

## Folder map

| Folder | What belongs here |
|---|---|
| `game/` | Active Unreal project, C++ source, configuration and imported content |
| `data/` | Canonical gameplay data; successor source is `data/vnext/catalog.json` |
| `art-source/`, `exports/` | Authored art, isolated candidates and export assets |
| `tools/`, `tests/` | Authoring/build helpers and verification |
| `docs/`, `production/`, `.agents/` | Contracts, production workflows and project skills |
| `reports/` | Development evidence and implementation ledger |
| `generated/`, `research/` | Existing generated outputs and research records |
| `builds/` | Preserved playable candidates and package revisions; local only |
| `support/` | Consolidated external packages, tooling, archives, settings and migration evidence; [index](support/README.md) |
| `.git/` | Full existing local history, branches and repository metadata |

## Source control

This root uses `codex/milestones-b0-m7-20260912`. The milestone, Storybook r20 and consolidation checkpoint is published to [TUPRAM/wonder-chess](https://github.com/TUPRAM/wonder-chess); see the [publication report](reports/repository-sync/20260915/PUBLISHING_REPORT.md) for scope and verification. The older main checkout is archived under `support/archives/previous-checkout-20260915/`; it is not a second development location. All pre-migration local Git refs remain available.

The transfer folder is more complete than the Git commit set. Support plans, review material, original production kits, source tooling and migration records are versioned. Packaged builds, generated caches/environments, duplicate checkout archives, Git-internal recovery snapshots, machine settings and quarantined third-party acquisition packs remain local. Keep them when copying the folder.

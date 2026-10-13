# Wonder Chess

The current Wonder Chess successor project, its Unreal assets, source art, packaged candidates and local project support now live in this one folder. **Copy the entire folder to the new PC, including hidden `.git` and ignored `builds/` and `support/`.** A GitHub download alone will not include the complete local project.

## Start here

- **Development plans and goals:** [three delivery plans, ten workstreams and prioritized backlog](docs/vnext/planning/DEVELOPMENT_PLAN_2026_09_30.md).
- **Creature production pipeline:** [Meshy → Unreal handbook](production/creature-pipeline/README.md) — preserved Meshy colors, soft lighting, character rigs, animation, AI sound and packaged review. Reuse with `$wc-creature-production`.
- **Current development toolchain:** Unreal **5.8.2**, Blender **5.2.1 LTS**. See [verified setup and compatibility](docs/LOCAL_TOOLCHAIN.md).
- **Play the Unreal 5.8 candidate:** double-click `Play Wonder Chess UE58.cmd`.
- **Play the current visual r29 solo candidate:** double-click `Play Wonder Chess.cmd`. This opens the enlarged board, circular portrait bench sockets and round shop with the Bellback and Silkmother 3D preview flags; the remaining enabled creatures still use gameplay proxies.
- **Open its combat laboratory:** double-click `Play Storybook Lab.cmd`.
- **Build/edit the game:** `game/WonderChess.uproject`.
- **Move computers:** [TRANSFER_TO_NEW_PC.md](TRANSFER_TO_NEW_PC.md).
- **Continue development:** [current milestone status](docs/vnext/milestones/MILESTONE_STATUS.md), [implementation readout](docs/vnext/milestones/IMPLEMENTATION_READOUT.md), and [successor contract](docs/vnext/README.md).
- **Inspect the consolidation:** [reorganization report](reports/REORGANIZATION_2026_09_15.md).

Visual r29 is a seven-creature development candidate. Its packaged layout and selection checks are recorded in `reports/vnext/milestones/visual-20260924/`; full creature production, pacing and acceptance work remain open. Storybook r20 stays preserved under `builds/WonderChess-Storybook-r20/`.

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

This root now uses `codex/milestones-b0-m7-20260912` at base commit `d80635f615810a93c3161c6bfd6c34c758b08260`, with the existing uncommitted milestone work preserved. The older main checkout is archived under `support/archives/previous-checkout-20260915/`; it is not a second development location. All pre-migration Git refs remain available.

The transfer folder is deliberately more complete than the Git commit set. Local builds, recovery material, imported third-party acquisition packs and machine configuration stay outside normal staging. Keep them when copying the folder.

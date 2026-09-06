# Execution tasks

These checkpoints serve one complete playable-alpha assignment. A passed checkpoint is not permission to stop at scaffolding when the next task is unblocked.

| Task | Objective | Dependency |
|---|---|---|
| [WC-300](WC-300.md) | Toolchain and first package | No prerequisite; new isolated workspace. |
| [WC-310](WC-310.md) | Eight-seat game and rules | WC-300 toolchain passes; review locked alpha data before integration. |
| [WC-320](WC-320.md) | Reference hero and arena proof | WC-300 passes; WC-310 can run in parallel after interface/scale contracts are stable. |
| [WC-330](WC-330.md) | Twelve coherent playable heroes | WC-320 reference gate and stable runtime/presentation contract from WC-310. |
| [WC-340](WC-340.md) | Player experience and bot quality | WC-310 functional match; art can integrate progressively from WC-330. |
| [WC-350](WC-350.md) | Two humans plus six bots | WC-310 authority and WC-340 UI available; complete actual multi-instance test. |
| [WC-360](WC-360.md) | Packaged alpha verification and handoff | WC-300 through WC-350 pass with explicitly recorded exceptions; all twelve art gates pass. |

Critical path: WC-300 → WC-310; WC-320 can overlap runtime after scale/interfaces are stable. WC-330 follows the accepted reference hero, WC-340 completes experience, WC-350 verifies actual multiplayer authority, and WC-360 produces release evidence. Website and expansion heroes are not prerequisites.

# Local Wonder Chess support

This directory replaces the old external `Documents/Project Support/Wonder Chess` location for the owner-requested portable project. Plans, review material, original production kits, project tool sources and migration evidence are versioned. Packaged study builds, Python environments, machine preferences/state, Git-internal recovery snapshots and the duplicate historical checkout remain local. Copy the whole folder for the complete transfer; see the [publication scope](../reports/repository-sync/20260915/PUBLISHING_REPORT.md).

| Path | Contents |
|---|---|
| `external/Storybook Demo - r20/` | Current review images and Storybook readout |
| `external/2D Asset Plan - r001/` | 2D specifications and reference gallery; open `START_HERE.html` |
| `external/2D Art Slice - r001/` | Preserved earlier approved slice material |
| `external/study-builds/` | Preserved r5/r6 clean-build packages |
| `external/planning/`, `external/validation/`, `external/repository-sync-20260908/` | Original planning, test and publication records |
| `external/blender-mcp-1.9.1/`, `external/mpfb-pilot/` | Project-specific bridge/source tooling and pilot material |
| `archives/previous-checkout-20260915/` | Entire former Documents checkout payload, including its unique source, reports, caches, builds and local config |
| `archives/downloads/` | Nine original Wonder Chess ZIP packages plus the verified Blender MCP source ZIP from Downloads |
| `archives/recovered-autosaves/` | Recovered Ada Blender autosave; unreviewed recovery evidence |
| `local-state/WonderChess/` | Project-specific application settings and Python test dependencies from the virtualized AppData location |
| `local-state/native-WonderChess/` | Separate native Windows settings exposed by the app's file virtualization; preserved without overwriting the other version |
| `operations/migration-20260915/` | Original hashes, move log, Git refs/index snapshots, patches and verification |

The original support subfolder names are preserved so internal links still resolve. The `.cmd` launchers in `external/` now resolve the active repository relatively. Root launchers are the simplest entry point.

Historical logs and saved scripts can contain the paths used when they were executed. Those records are not silently rewritten. Use `operations/migration-20260915/before.jsonl` to map each original file to its destination. Do not run archived scripts as current build instructions.

The original move hashes describe the payload before the documented launcher/navigation edits and verification runs. Use the root `TRANSFER_MANIFEST.jsonl` with `tools/verify_transfer.py` to check the final snapshot on another PC.

Preserve named candidates, failed attempts, third-party rights records and unreconciled material. Consolidation does not grant any additional license or art/release acceptance. Rebuild Python virtual environments on the new PC; copied environments retain references to the original interpreter installation.

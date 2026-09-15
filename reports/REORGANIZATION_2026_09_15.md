# Wonder Chess consolidation — 15 September 2026

## Result

The current milestone working tree is now the standalone repository at `C:\Users\iputu\Documents\Wonder Chess`. Project-owned external payloads are consolidated beneath that folder. The older Documents checkout remains intact as an archive within `support/archives/previous-checkout-20260915/`.

The owner authorized consolidation for transfer to a new PC and organization for future builds. This work changes storage, navigation, launch paths and the missing Python test dependency; it does not resume a product/art milestone or change gameplay acceptance.

## Preserved payload

| Original source | Destination | Files | Bytes |
|---|---|---:|---:|
| Former Documents checkout, excluding shared `.git` | `support/archives/previous-checkout-20260915/` | 25,270 | 29,301,430,879 |
| Milestone Codex worktree payload | Repository root | 35,749 | 39,976,305,944 |
| `Documents/Project Support/Wonder Chess` | `support/external/` | 2,450 | 2,140,562,155 |
| Virtualized WonderChess AppData | `support/local-state/WonderChess/` | 239 | 2,771,526 |
| Additional native Windows settings | `support/local-state/native-WonderChess/` | 1 | 1,122 |
| Wonder Chess ZIP packages from Downloads | `support/archives/downloads/` | 9 | 26,342,040 |
| Documented Blender MCP ZIP from Downloads | `support/archives/downloads/` | 1 | 634,931 |
| Ada Blender autosave from Temp | `support/archives/recovered-autosaves/` | 1 | 739,433 |
| **Moved payload total** | | **63,720** | **71,448,788,030** |

The existing `.git` directory stayed in this folder throughout. It adds roughly 11 GB of local history/metadata to the transfer. New navigation, verification and audit files are additional to the moved payload totals.

Every moved file was SHA-256 checked. Windows app virtualization exposed a native crash-settings file and a different native game-settings file after the virtualized directory was moved. The initially missing crash-settings file was recovered into its expected location, and both game-settings versions were preserved separately. The original failed check and the successful recovery are recorded; no payload mismatch remains.

## Git preservation

- Current branch: `codex/milestones-b0-m7-20260912`.
- Base HEAD: `d80635f615810a93c3161c6bfd6c34c758b08260`.
- All preexisting Git refs are unchanged, including the historical `main` ref and local build snapshots.
- All **1,844 original dirty-status entries** remain present after promotion.
- Original main and linked-worktree indexes, HEAD/configuration, linked reflog, refs listing and binary patches are preserved in the migration evidence directory.
- The linked worktree was retired through Git only after the payload was moved and verified and its directory contained only the `.git` pointer. Its payload was not discarded.
- There is one registered worktree, at the canonical root. `core.longpaths=true` is set locally.
- Existing work remains uncommitted and unpublished. No stage/commit/push, history rewrite, remote operation or release was performed.

## Organization and portability changes

- Added root `README.md`, `TRANSFER_TO_NEW_PC.md` and `support/README.md`.
- Added root Solo/Lab launchers and converted all nine external support launchers to relative paths.
- Added a `-ValidateOnly` launcher option to check the packaged executable path without launching or writing runtime evidence.
- Updated current navigation and the implementation ledger to use this root. Historical evidence paths remain recorded; `before.jsonl` maps original paths to new destinations.
- Added `Pillow==12.3.0` to `requirements-tools.txt`: the full existing test suite imports Pillow, but the previous requirements omitted it.
- Preserved and relocated the project bridge source/environment; updated ignored local MCP paths and verified the server source imports. The project bridge process was stopped for the move; no Blender/game/editor process was stopped. A fresh environment and machine-specific config are required on the new PC.
- Added `tools/verify_transfer.py` and the final local `TRANSFER_MANIFEST.jsonl`. The manifest includes project payloads and Git objects/refs; it omits itself and mutable Git index/reflog/lock files. A completion record detects incomplete inventories.
- Kept support/build/recovery material outside normal Git staging. These ignored files remain part of the physical transfer folder.

## Verification

| Check | Result |
|---|---|
| Moved-file SHA-256 preservation | **PASS**, all 63,720 files, including the separately verified bridge ZIP |
| Git refs and original dirty-status preservation | **PASS** |
| `git fsck --full` | **PASS**, exit 0 |
| `git diff --check` | **PASS**, exit 0 |
| `python tools/validate_kit.py` | **PASS**, 400 checks |
| Full Python unittest suite | **PASS**, 230 tests |
| Generated documents | **PASS**, 28 documents |
| Legacy catalogue generation | **PASS**, 6 artifacts |
| Successor catalogue generation | **PASS**, 6 artifacts |
| Storybook r20 existing exact-package verifier at relocated roots | **PASS**, 122 source files and 49 package files |
| Relative launcher checks from a different working directory | **PASS**, 11 launchers; no game launched |
| Relocated Blender MCP source import | **PASS**, no live Blender connection attempted |
| Transfer verifier fixtures | **PASS**: valid payload, changed/missing files, unsafe paths, duplicate rows, truncated inventory |
| New Unreal compile/package, fresh game launch, new-PC runtime/performance | **NOT_RUN** |

The first suite invocation used the PATH Python without Pillow and failed on that missing import. The complete rerun used existing bundled CPython 3.12.14 with Pillow 12.3.0 and the preserved `jsonschema` 4.26.0 test dependencies. All 230 tests passed. No global or engine-managed Python package was installed or changed.

## Search coverage and remaining machine dependencies

Inspected the registered worktree, explicit Project Support root, project-specific AppData, Downloads, Desktop, Documents, managed worktree roots, Temp, D:, Pictures, Videos, OneDrive and Codex visualization names. The scoped filename searches excluded unrelated application/vendor trees and VEILMARK. Seven protected/system/legacy-junction locations could not be read; the additional optional Codex artifacts directory did not exist. This is a documented project-file inventory, not a claim to identify every unnamed file on the computer.

The former Project Support folder, both paths to the retired milestone worktree, project-specific AppData folder, moved ZIPs and recovered autosave were confirmed absent at their old locations. Installed Unreal, Blender, Visual Studio, Windows SDK, shared Codex/Python runtimes, drivers, global app preferences/add-ons, credentials and unrelated projects remain on the original PC. The project-specific bridge source and its original archive are included. Reinstall shared applications on the new PC.

Saved art binaries, Unreal import metadata and generated caches may retain original absolute paths. Their contents were preserved; no mass reimport/resave was attempted. Follow the transfer guide to verify the copy, recreate environments, regenerate build files, and relink asset sources when required.

## Evidence locations

- `support/operations/migration-20260915/before.jsonl` — original per-file paths, bytes and SHA-256 values.
- `support/operations/migration-20260915/before-summary.json` — original grouped totals and inventory digest.
- `support/operations/migration-20260915/move-verification.json` — verified move plus native/virtualized settings recovery.
- `support/operations/migration-20260915/additional-bridge-archive.json` — separately matched and verified bridge ZIP.
- `support/operations/migration-20260915/preservation-summary.json` — refs and existing changes preserved.
- `support/operations/migration-20260915/post-move-edits.json` — intentional navigation/launcher/configuration edits and the cache refresh observed after verification.
- `support/operations/migration-20260915/checks/` — authoring logs and verifier fixtures.
- `support/operations/migration-20260915/package-r20-verification.json` — existing package identity check using relocated roots.
- `TRANSFER_MANIFEST.jsonl` — final snapshot for the new-PC file-integrity check.

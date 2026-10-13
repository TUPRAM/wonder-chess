# Move Wonder Chess to the new Windows PC

## 1. Copy the complete folder

Close Wonder Chess, Blender, Unreal Editor and any builds before copying. Copy this entire `Wonder Chess` directory, including hidden `.git`, local `builds`, and `support`. Use an NTFS destination with at least 100 GB available for this snapshot, plus separate room for Unreal, development tools and future builds. A short destination such as `C:\Projects\WonderChess` helps with the deep archived art paths.

Use the complete folder copy for transfer. GitHub contains the published source/assets/evidence checkpoint, while packaged builds, generated environments/caches, duplicate historical archives and machine recovery state remain local. Keep the original until the destination passes verification.

From PowerShell on the original PC, an example copy to a mounted transfer drive is:

```powershell
robocopy 'C:\Users\iputu\Documents\Wonder Chess' 'E:\WonderChess' /E /COPY:DAT /DCOPY:DAT /R:2 /W:2 /XJ
```

Replace `E:` with your actual drive. Robocopy exit codes below 8 can indicate success; inspect its summary and then verify hashes. This command does not remove the source or mirror-delete the destination.

## 2. Verify before editing or rebuilding

Install Python 3.11 or newer and Git for Windows, open PowerShell in the copied project root, and run:

```powershell
python tools/verify_transfer.py
git fsck --full
git worktree list
git status --short --branch
```

`verify_transfer.py` checks all captured payload files against `TRANSFER_MANIFEST.jsonl`, including Git objects and refs. The mutable Git index, reflogs and temporary Git lock files are excluded. Extra files are permitted; missing or changed captured files fail. A completion record detects truncated/incomplete inventories. The manifest is an integrity comparison, not an authenticity signature.

There should be one registered checkout at the new location. The branch is `codex/milestones-b0-m7-20260912`. The consolidation originally preserved uncommitted work; the later owner-requested [GitHub publication](reports/repository-sync/20260915/PUBLISHING_REPORT.md) commits that checkpoint. Use `git status` to identify any changes made afterward. If moving only this standalone root, no external worktree repair is needed. Repo-local `core.longpaths=true` was set and travels in `.git/config`.

If you intentionally change project files before copying, keep the old manifest and capture a fresh one with a different name after closing writers:

```powershell
python tools/verify_transfer.py --create --manifest TRANSFER_MANIFEST-next.jsonl
```

Check that named inventory on the destination with `--manifest TRANSFER_MANIFEST-next.jsonl`.

## 3. Play the preserved candidate

Double-click `Play Wonder Chess.cmd` for Storybook r20 Solo, or `Play Storybook Lab.cmd` for its laboratory. Both resolve paths relative to the copied folder. They use the existing package in `builds/WonderChess-Storybook-r20/Windows/`.

For a path check without launching the game:

```powershell
powershell -NoProfile -File tools/unreal/launch_milestones.ps1 -Storybook -ValidateOnly
```

The packaged prerequisite installer is retained with the package. Install the included Unreal/Visual C++ prerequisites on the destination if needed. Check actual rendering, input, audio and performance on that PC separately; file integrity does not prove new-machine runtime acceptance.

## 4. Prepare to build

Observed original build tools: Unreal Engine **5.7.4**, Visual Studio **2022 Community** with the x64 C++ toolchain, Windows SDK **10.0.22621.0**, Blender **5.1** series, and Python **3.11.8**. Install the matching development tools on the new PC. These shared applications and GPU drivers require their own installation; they are not project files that can be moved into this folder.

Create a fresh Python environment rather than activating a copied one:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-tools.txt
.\.venv\Scripts\python.exe tools/validate_kit.py
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe tools/build_documents.py --check
.\.venv\Scripts\python.exe tools/compile_catalog.py --check
.\.venv\Scripts\python.exe tools/vnext/catalog.py --check
```

The requirements include Pillow for the image-encoder tests. Art scripts that use editor-provided modules still run in their appropriate Blender or Unreal environment. Do not change engine-managed Python packages.

Open `game/WonderChess.uproject` with Unreal 5.7 and regenerate its Visual Studio project files at the new location. The old `game/Intermediate`, `Binaries`, `Saved`, `DerivedDataCache` and solution files were preserved as requested; they can contain old absolute build paths. If a clean build is needed, archive those generated directories first and let Unreal regenerate them. Never remove `game/Content`, `game/Source`, `game/Config`, `art-source`, or `exports` as cache cleanup.

Saved Blender files and Unreal reimport metadata may also retain original source paths. Their binary contents were preserved. Check external textures and reimport source locations when opening those assets on the new PC, and relink to the matching files inside this folder where needed. Consolidation did not perform a batch resave or reimport of protected art assets.

For a fresh package, set the actual engine path and choose a new archive directory:

```powershell
$env:UE_UAT_SCRIPT = 'C:\Program Files\Epic Games\UE_5.7\Engine\Build\BatchFiles\RunUAT.bat'
.\tools\unreal\package_game.ps1 -ProjectFile .\game\WonderChess.uproject -ArchiveDirectory .\builds\NewPC-first-build -LogDirectory .\reports\new-pc-build
```

Do not overwrite the preserved r4/r6/r13/r15/r20 candidates. Review [current milestones](docs/vnext/milestones/MILESTONE_STATUS.md) before continuing product development.

## 5. Optional Blender bridge and settings

The Blender MCP source is preserved in `support/external/blender-mcp-1.9.1/blender-mcp-main`. Its copied `.venv` references the original Unreal Python interpreter and is not a portable installation. To recreate the bridge, use a new `.venv-mcp`, install that local source package into it, then create `.codex/config.toml` from `.codex/config.example.toml`. Set `command` to the new environment's absolute `python.exe` and `cwd` to the new project root. Keep the existing loopback, telemetry and safe-mode settings. The ignored config left on the old PC is machine-specific; update it before enabling the bridge on the new PC.

The bridge process was stopped to relocate its directory. Reopening the project in Codex reloads the configured bridge. No Blender scene or game process was stopped during consolidation.

Old application settings are in `support/local-state/`. Native and app-virtualized settings differed, so both versions were kept. These are optional historical preferences/crash settings, not required build inputs. Let the new game create fresh settings unless you intentionally want to restore one version.

## Evidence boundaries

The consolidation preserves the current project, old checkout, local history, builds and evidence. Historical absolute paths in saved reports remain provenance and can be resolved with `support/operations/migration-20260915/before.jsonl`. A new Unreal build, new-PC installation, human playtest and release acceptance require their own results.

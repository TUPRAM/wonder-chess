# Local development toolchain

Owner-selected versions for this PC, 17 September 2026:

| Component | Verified installation |
|---|---|
| Unreal Engine | 5.8.2, `C:\Program Files\Epic Games\UE_5.8` |
| Blender | 5.2.1 LTS, `C:\Program Files\Blender Foundation\Blender 5.2\blender.exe` |
| Visual Studio Build Tools | 2022, 17.14; MSVC 14.44.35229 (family 14.44.35207) |
| Windows SDK | 10.0.22621.0 |
| .NET Framework | 4.8 SDK and targeting pack; required by the editor build |
| Project Python | `.venv\Scripts\python.exe`, Python 3.12.14 |
| Windows PowerShell | CurrentUser `RemoteSigned`; machine and group policy unchanged |

## Build and play

Run from the repository root in PowerShell:

```powershell
& 'C:\Program Files\Epic Games\UE_5.8\Engine\Build\BatchFiles\Build.bat' WonderChessEditor Win64 Development "-Project=$PWD\game\WonderChess.uproject" -WaitMutex -NoHotReloadFromIDE -NoUBA
./tools/unreal/package_game.ps1 -ProjectFile ./game/WonderChess.uproject -ArchiveDirectory ./builds/YourNewCandidate -UatScript 'C:\Program Files\Epic Games\UE_5.8\Engine\Build\BatchFiles\RunUAT.bat'
```

Choose a fresh package directory for each candidate. `Play Wonder Chess UE58.cmd` launches the verified UE58-r1 successor package. Earlier launchers and frozen packages remain available. The editor project uses association `5.8`, V7 build settings and the 5.8 include order. JSON key access was adapted to the installed shared-string API.

For Python checks, use `.venv\Scripts\python.exe`. Native test wrappers also need that folder first on the current process PATH:

```powershell
$env:Path = "$PWD\.venv\Scripts;$env:Path"
$env:PYTHONDONTWRITEBYTECODE = '1'
.venv/Scripts/python.exe -m unittest discover -s tests -v
```

## Blender and Unreal connection

The configured local Blender MCP bridge uses `127.0.0.1:9876`, the project virtual environment and the reviewed local bridge source under `support/external/`. Start the chosen candidate with `tools/blender/Start-Mcp.ps1` using its explicit blend path. Only one session owns the port. Restart the Codex project session if its cached MCP configuration predates the repaired `.codex/config.toml`.

`start_mcp.py` resolves missing image references from the former PC to matching files inside this repository, in memory. It reports unresolved references and does not save source files. Separate relinked Dragonkin and arena copies are under `support/compatibility/blender52-20260917/relinked-sources/`; original source hashes are preserved.

Blender-to-Unreal asset transfer was verified through normalized FBX exports and Unreal's legacy FBX importer: six representative rig families, seven clips each, unit root scales, matching bone heights and 1,260 sampled poses. See `tools/blender/profiles/fbx_skeletal_cm_blender52_ue58_v1.json` for the measured scope. Existing historical profile settings remain unchanged. This is a tested export/import pipeline; it does not imply a continuously synchronized editor link.

## Evidence and rollback

Detailed results: `reports/toolchain-upgrade-20260917/REPORT.md`. Migration was first built and packaged from `support/compatibility/ue58-20260917/game/`, then its four source changes were promoted to the active `game/` project. The isolated copy is diagnostic material, not another active checkout.

Pre-migration project/target/registry files and old generated Binaries, Intermediate, Saved and DerivedDataCache are preserved in `support/archives/pre-ue58-20260917/game/`. Recover selected files from that archive if needed; do not merge old generated binaries into the 5.8 build. No original `.blend`, `.uasset`, or `.umap` was resaved by this migration. Historical packages, approvals and acceptance boundaries remain separate.

# Build tools repair — 16 September 2026

## Current result

**Prepared; installation blocked before execution.** No C++ compiler or Windows SDK was installed in this lane. Automatic approval review rejected the supported Microsoft installer command with the sole reason `blocked by policy`. No retry or alternative installation bypass was attempted. The shell also has a non-administrator Windows token.

## Prepared installer

- Official Microsoft Visual Studio **2022** Build Tools bootstrapper: `support/tools/installers/vs_buildtools-2022.exe`, downloaded from <https://aka.ms/vs/17/release/vs_buildtools.exe>.
- Authenticode status **Valid**, publisher **Microsoft Corporation**. See `installer-provenance.json` for file version and SHA-256.
- Component selection: `support/tools/installers/wonder-chess-buildtools-2022.vsconfig`.
- User launch helper: `support/tools/installers/Install Wonder Chess Build Tools.cmd`.
- Selection includes the VS2022 C++ build workload, **MSVC v143 14.44**, **Windows SDK 10.0.22621.0**, CMake, AddressSanitizer and .NET SDK. No automatic reboot is requested.

### Required Windows action

Right-click **Install Wonder Chess Build Tools.cmd** and select **Run as administrator**. Review and approve the Microsoft Windows administrator prompt yourself. The helper uses the downloaded signed Microsoft installer and the adjacent component configuration. Let installation finish; report a restart request if one appears. Codex still needs to verify compiler/SDK discovery and compile a smoke test afterward.

Microsoft documents that programmatic quiet/passive installation is unavailable to standard users. This is separate from the automatic approval review rejection.

## Unreal Engine version

Only **Unreal Engine 5.8.2**, installed at `C:\Program Files\Epic Games\UE_5.8`, is registered in the Epic Launcher inventory. The Wonder Chess project associates with **5.7**; its transfer record identifies the original engine as **5.7.4**. The project association, game source, assets and preserved binaries were not changed.

The supported binary engine installation route is the installed **Epic Games Launcher**. In the launcher:

1. Open **Unreal Engine → Library**.
2. Press **+** beside **Engine Versions** to add a version tile.
3. Use the tile's version dropdown and select **5.7.4** if it is offered.
4. Install it alongside 5.8, normally to `C:\Program Files\Epic Games\UE_5.7`.
5. Include the base engine and Windows support; select no paid content.

The available launcher dropdown was not inspected, so **5.7.4 availability is not verified**. If only another 5.7 patch is offered, record that actual version before choosing an engine migration. A launcher install is not achievable with the available browser-only computer-use APIs; native desktop automation is disabled. No unofficial downloader, credential extraction or source build was used.

About **740 GiB** of free space was observed on C: during preparation. This is sufficient headroom for the stated setup but is not an installation-size estimate.

## Compatibility evidence

- [Epic UE5.7 Visual Studio setup](https://dev.epicgames.com/documentation/en-us/unreal-engine/setting-up-visual-studio-development-environment-for-cplusplus-projects-in-unreal-engine?application_version=5.7): VS2022 17.14 recommended, MSVC14.44.35214, Windows SDK22621 or newer.
- [Microsoft Build Tools component IDs](https://learn.microsoft.com/en-us/visualstudio/install/workload-component-id-vs-build-tools?view=vs-2022): exact component IDs used by the supplied configuration.
- [Microsoft installation command reference](https://learn.microsoft.com/en-us/visualstudio/install/use-command-line-parameters-to-install-visual-studio?view=vs-2022): installer arguments and standard-user limitation.
- [Epic engine installation](https://dev.epicgames.com/documentation/unreal-engine/install-unreal-engine): supported launcher and multiple-version workflow.
- Installed UE5.8 local `Engine/Config/Windows/Windows_SDK.json` names SDK22621 as its main version and accepts/preferentially lists the 14.44 family, while banning versions through14.44.35210. This corroborates the component family selection; it does not certify Wonder Chess on5.8.

## Verification still required

Visual Studio/MSVC registration, actual compiler version, SDK headers/libraries, isolated C++ compile/run, UnrealBuildTool discovery, and a **5.7** project build remain **NOT RUN**. Unreal connection smoke results from other repair lanes are independent of build-tool installation.

Prepared verifier: `support/diagnostics/new-pc-20260916/build-tools/Verify-BuildTools.ps1`. After installation, run it from PowerShell; it locates VS2022 with `vswhere`, verifies the SDK22621 header/library, compiles a C++20 test with MSVC14.44, links `kernel32.lib`, and executes the result. Outputs stay in this report folder's `compiler-smoke/` subdirectory. Its PowerShell syntax has been checked; compilation has not run. `preflight.json` records the current absence of compiler/SDK installation.
